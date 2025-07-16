import { AgentList } from '@/components/agent-list';
import { NewAgentCard } from '@/components/new-agent-card';
import { ToolAssociationInfo } from '@/types';
import { Flex, FlexItem, PageSection, Title } from '@patternfly/react-core';
import { createFileRoute } from '@tanstack/react-router';

// Type def for fetching agents
export interface Agent {
  id: string;
  name: string;
  model_name: string;
  prompt: string;
  tools: ToolAssociationInfo[];
  knowledge_base_ids: string[];
  input_shields: string[];
  output_shields: string[];
  created_by: string;
  created_at: string;
  updated_at: string;
  // Add other relevant agent properties here
}

// Type def for creating agents
export interface NewAgent {
  name: string;
  model_name: string;
  prompt: string;
  tools: ToolAssociationInfo[];
  knowledge_base_ids: string[];
  input_shields: string[];
  output_shields: string[];
}

export const Route = createFileRoute('/config/agents')({
  component: Agents,
});

// --- 5. Main AgentsPage Component ---
export function Agents() {
  return (
    <PageSection>
      <Flex direction={{ default: 'column' }} gap={{ default: 'gapMd' }}>
        <FlexItem>
          <Title headingLevel="h1">Agents</Title>
        </FlexItem>
        <FlexItem>
          <NewAgentCard />
        </FlexItem>
        <FlexItem>
          <AgentList />
        </FlexItem>
      </Flex>
    </PageSection>
  );
}
