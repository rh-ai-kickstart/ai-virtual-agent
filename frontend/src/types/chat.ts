export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: SimpleContentItem[];
  timestamp: Date;
}

export interface TextContentItem {
  type: 'text';
  text: string;
}

export interface ImageData {
  sourceType: 'base64';
  data: string;
}

export interface ImageUrl {
  sourceType: 'url';
  url: {
    uri: string;
  };
}

type ImageSource = ImageData | ImageUrl;

export interface ImageContentItem {
  type: 'image';
  image: ImageSource;
}

export type SimpleContentItem = TextContentItem | ImageContentItem;

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
