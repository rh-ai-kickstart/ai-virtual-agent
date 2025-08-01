export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: SimpleContentItem[];
  timestamp: Date;
}

export interface SimpleContentItem {
  type: 'text' | 'image';
  text?: string;
  image?: {
    data?: string;
    url?: {
      uri: string;
    };
  };
}

export interface UseLlamaChatOptions {
  onError?: (error: Error) => void;
  onFinish?: (message: ChatMessage) => void;
}

export interface ChatSessionSummary {
  id: string;
  title: string;
  agent_name: string;
  updated_at: string;
  created_at: string;
}

export interface ChatSessionDetail {
  id: string;
  title: string;
  agent_name: string;
  agent_id: string;
  messages: Array<{
    role: 'user' | 'assistant';
    content: SimpleContentItem[];
  }>;
  created_at: string;
  updated_at: string;
}
