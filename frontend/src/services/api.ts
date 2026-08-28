import { Session, Message, Artifact, HealthStatus, IngestionStatus, Citation } from '../types';

const API_BASE = '/api/v1';

export async function fetchSessions(): Promise<Session[]> {
  const res = await fetch(`${API_BASE}/sessions`);
  if (!res.ok) throw new Error('Failed to fetch sessions');
  return res.json();
}

export async function createSession(title: string = 'New Conversation', provider: string = 'gemini', model: string = 'gemini-2.5-flash'): Promise<Session> {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, model_provider: provider, model_name: model })
  });
  if (!res.ok) throw new Error('Failed to create session');
  return res.json();
}

export async function getSession(sessionId: string): Promise<Session & { messages: Message[], artifacts: Artifact[] }> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
  if (!res.ok) throw new Error('Failed to get session');
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete session');
}

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to fetch health');
  return res.json();
}

export async function fetchIngestionStatus(): Promise<IngestionStatus> {
  const res = await fetch(`${API_BASE}/ingestion/status`);
  if (!res.ok) throw new Error('Failed to fetch ingestion status');
  return res.json();
}

export interface StreamChatParams {
  message: string;
  sessionId?: string;
  provider: 'gemini' | 'ollama';
  modelName?: string;
  enableShip30?: boolean;
  onToken: (token: string) => void;
  onCitation: (citation: Citation) => void;
  onArtifact: (artifact: Artifact) => void;
  onThinking: (data: { stage: string; message: string }) => void;
  onSessionResolved: (sessionId: string) => void;
  onDone: (data: any) => void;
  onError: (error: string) => void;
  signal?: AbortSignal;
}

export async function streamChat({
  message,
  sessionId,
  provider,
  modelName,
  enableShip30 = false,
  onToken,
  onCitation,
  onArtifact,
  onThinking,
  onSessionResolved,
  onDone,
  onError,
  signal
}: StreamChatParams): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        model_provider: provider,
        model_name: modelName,
        enable_ship30: enableShip30
      }),
      signal
    });

    if (!res.ok) {
      throw new Error(`HTTP error ${res.status}`);
    }

    const reader = res.body?.getReader();
    if (!reader) throw new Error('No readable stream available');

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      let currentEvent = '';

      for (const line of lines) {
        if (line.startsWith('event:')) {
          currentEvent = line.replace('event:', '').trim();
        } else if (line.startsWith('data:')) {
          const rawData = line.replace('data:', '').trim();
          if (!rawData) continue;

          try {
            const data = JSON.parse(rawData);

            if (currentEvent === 'session' && data.session_id) {
              onSessionResolved(data.session_id);
            } else if (currentEvent === 'token' && data.delta) {
              onToken(data.delta);
            } else if (currentEvent === 'citation') {
              onCitation(data);
            } else if (currentEvent === 'artifact') {
              onArtifact(data);
            } else if (currentEvent === 'thinking') {
              onThinking(data);
            } else if (currentEvent === 'done') {
              onDone(data);
            } else if (currentEvent === 'error') {
              onError(data.error || 'Unknown error');
            }
          } catch (e) {
            console.error('Error parsing SSE event data:', e, rawData);
          }
        }
      }
    }
  } catch (err: any) {
    if (err.name === 'AbortError') {
      console.log('Stream aborted by user');
    } else {
      onError(err.message || 'Stream connection failed');
    }
  }
}
