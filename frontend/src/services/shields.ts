import { SHIELDS_API_ENDPOINT } from '@/config/api';

export interface Shield {
  identifier: string;
  name?: string;
}

interface BackendShield {
  id: string;
  name: string;
  model_type: string;
}

export const fetchShields = async (): Promise<Shield[]> => {
  const response = await fetch(SHIELDS_API_ENDPOINT);
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  const data: BackendShield[] = await response.json();
  
  // Map backend response to frontend expected structure
  return data.map(shield => ({
    identifier: shield.id,
    name: shield.name,
  }));
};
