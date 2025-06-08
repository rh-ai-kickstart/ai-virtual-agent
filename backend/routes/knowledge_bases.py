from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from .. import models, schemas
from ..database import get_db
from ..api.llamastack import client

router = APIRouter(prefix="/knowledge_bases", tags=["knowledge_bases"])

@router.post("/", response_model=schemas.KnowledgeBaseRead, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(kb: schemas.KnowledgeBaseCreate, db: AsyncSession = Depends(get_db)):
    db_kb = models.KnowledgeBase(**kb.model_dump(exclude_unset=True))
    db_kb.status = "pending"
    db.add(db_kb)
    await db.commit()
    await db.refresh(db_kb)
    
    # Auto-sync with LlamaStack after creation
    try:
        print(f"Auto-syncing knowledge bases after creation of: {db_kb.name}")
        await sync_knowledge_bases(db)
    except Exception as e:
        print(f"Warning: Failed to auto-sync after knowledge base creation: {str(e)}")
    
    return db_kb

@router.get("/", response_model=List[schemas.KnowledgeBaseRead])
async def read_knowledge_bases(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.KnowledgeBase))
    return result.scalars().all()

@router.get("/{vector_db_name}", response_model=schemas.KnowledgeBaseRead)
async def read_knowledge_base(vector_db_name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.KnowledgeBase).where(models.KnowledgeBase.vector_db_name == vector_db_name))
    kb = result.scalar_one_or_none()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return kb

@router.put("/{vector_db_name}", response_model=schemas.KnowledgeBaseRead)
async def update_knowledge_base(vector_db_name: str, kb: schemas.KnowledgeBaseCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.KnowledgeBase).where(models.KnowledgeBase.vector_db_name == vector_db_name))
    db_kb = result.scalar_one_or_none()
    if not db_kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    for field, value in kb.dict().items():
        setattr(db_kb, field, value)
    await db.commit()
    await db.refresh(db_kb)
    
    # Auto-sync with LlamaStack after update
    try:
        print(f"Auto-syncing knowledge bases after update of: {db_kb.name}")
        await sync_knowledge_bases(db)
    except Exception as e:
        print(f"Warning: Failed to auto-sync after knowledge base update: {str(e)}")
    
    return db_kb

@router.delete("/{vector_db_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(vector_db_name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.KnowledgeBase).where(models.KnowledgeBase.vector_db_name == vector_db_name))
    db_kb = result.scalar_one_or_none()
    if not db_kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    kb_name = db_kb.name  # Store name before deletion
    
    # First, try to delete from LlamaStack
    try:
        print(f"Deleting knowledge base from LlamaStack: {vector_db_name}")
        client.vector_dbs.unregister(vector_db_name)
        print(f"Successfully deleted from LlamaStack: {vector_db_name}")

    except Exception as e:
        print(f"Warning: Failed to delete from LlamaStack (may not exist there): {str(e)}")
        # Continue with DB deletion even if LlamaStack deletion fails
        # This handles cases where the KB exists in DB but not in LlamaStack (PENDING status)
    
    # Then delete from database
    await db.delete(db_kb)
    await db.commit()
    
    print(f"Successfully deleted knowledge base from database: {kb_name}")
    return None

@router.post("/sync", response_model=List[schemas.KnowledgeBaseRead])
async def sync_knowledge_bases_endpoint(db: AsyncSession = Depends(get_db)):
    try:
        return await sync_knowledge_bases(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def sync_knowledge_bases(db: AsyncSession):
    try:
        print("Starting knowledge base sync")
        print("Fetching vector databases from LlamaStack")
        try:
            response = client.vector_dbs.list()
            
            if isinstance(response, list):
                vector_dbs = [item.__dict__ for item in response]
            elif isinstance(response, dict):
                vector_dbs = response.get("data", [])
            elif hasattr(response, "data"):
                vector_dbs = response.data
            else:
                print(f"Unexpected response type: {type(response)}")
                vector_dbs = []
                
            
        except Exception as e:
            raise Exception(f"Failed to fetch vector databases from LlamaStack: {str(e)}")
        
        print("Fetching existing knowledge bases from database...")
        result = await db.execute(select(models.KnowledgeBase))
        existing_kbs = {kb.vector_db_name: kb for kb in result.scalars().all()}
        print(f"Found {len(existing_kbs)} existing knowledge bases: {list(existing_kbs.keys())}")
        
        synced_kbs = []
        
        print("Processing vector databases...")
        for vector_db in vector_dbs:
            try:
                if not vector_db.get("identifier"):
                    print(f"Skipping vector database without identifier: {vector_db}")
                    continue
                    
                kb_data = {
                    "name": vector_db["identifier"],
                    "version": "1.0",
                    "embedding_model": vector_db.get("embedding_model", "all-MiniLM-L6-v2"),
                    "provider_id": vector_db.get("provider_id"),
                    "vector_db_name": vector_db["identifier"],
                    "is_external": False,
                    "source": None,
                    "source_configuration": {
                        "embedding_dimension": vector_db.get("embedding_dimension"),
                        "type": vector_db.get("type"),
                        "provider_resource_id": vector_db.get("provider_resource_id")
                    }
                }
                print(f"Processing vector database {vector_db['identifier']} with data: {kb_data}")
                
                if vector_db["identifier"] in existing_kbs:
                    print(f"Updating existing knowledge base: {vector_db['identifier']}")
                    kb = existing_kbs[vector_db["identifier"]]
                    for field, value in kb_data.items():
                        setattr(kb, field, value)
                else:
                    print(f"Creating new knowledge base: {vector_db['identifier']}")
                    kb = models.KnowledgeBase(**kb_data)
                    db.add(kb)
                
                synced_kbs.append(kb)
            except Exception as e:
                print(f"Error processing vector database {vector_db.get('identifier', 'unknown')}: {str(e)}")
                continue
        
        # Note: We no longer remove knowledge bases from DB that don't exist in LlamaStack
        # This allows for PENDING status (exists in DB but not yet in LlamaStack during ingestion)
        # Deletion from DB should only happen through explicit delete API calls
        print("Sync complete - only added missing items from LlamaStack to DB")
        
        print("Committing changes to database...")
        await db.commit()
        
        print("Refreshing synced knowledge bases...")
        for kb in synced_kbs:
            await db.refresh(kb)
        
        print(f"Sync complete. Synced {len(synced_kbs)} knowledge bases.")
        return synced_kbs
        
    except Exception as e:
        print(f"Error during sync: {str(e)}")
        raise Exception(f"Failed to sync knowledge bases: {str(e)}")
