export interface Citation {
  id?: string;
  episode_title: string;
  guest?: string;
  timestamp_or_section?: string;
  url?: string;
  quote: string;
  relevance_score: number;
}

export interface Artifact {
  id: string;
  session_id?: string;
  message_id?: string;
  title: string;
  artifact_type: 'markdown' | 'html' | 'svg';
  content: string;
  version?: number;
  created_at?: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  model?: string;
  tokens_used?: number;
  latency_ms?: number;
  citations?: Citation[];
  artifacts?: Artifact[];
  created_at?: string;
  isStreaming?: boolean;
}

export interface Session {
  id: string;
  title: string;
  model_provider: 'gemini' | 'ollama';
  model_name: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface IngestionStatus {
  is_ingesting: boolean;
  total_episodes: number;
  total_chunks: number;
  last_ingested_at?: string;
  status_message: string;
}

export interface HealthStatus {
  status: string;
  database: string;
  pgvector: boolean;
  ollama_connected: boolean;
  gemini_configured: boolean;
  total_indexed_chunks: number;
  gemini_model?: string;
  ollama_model?: string;
}
