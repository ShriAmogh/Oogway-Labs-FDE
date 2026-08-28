import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Sidebar } from './components/Sidebar/Sidebar';
import { ChatHeader } from './components/Chat/ChatHeader';
import { MessageList } from './components/Chat/MessageList';
import { MessageInput } from './components/Chat/MessageInput';
import { ArtifactViewer } from './components/Artifact/ArtifactViewer';
import { SourceDrawer } from './components/Sources/SourceDrawer';
import { Session, Message, Artifact, Citation, HealthStatus, IngestionStatus } from './types';
import { 
  fetchSessions, createSession, getSession, deleteSession, 
  fetchHealth, fetchIngestionStatus, streamChat 
} from './services/api';

export const App: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  
  const [provider, setProvider] = useState<'gemini' | 'ollama'>('gemini');
  const [showArtifactViewer, setShowArtifactViewer] = useState(false);
  const [showSourcesDrawer, setShowSourcesDrawer] = useState(false);
  const [activeCitationIndex, setActiveCitationIndex] = useState<number | undefined>(undefined);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  
  const [isStreaming, setIsStreaming] = useState(false);
  const [thinkingStage, setThinkingStage] = useState<{ stage: string; message: string } | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [ingestion, setIngestion] = useState<IngestionStatus | null>(null);
  
  const abortControllerRef = useRef<AbortController | null>(null);

  // Derived citations strictly scoped to the active session's messages
  const sessionCitations = useMemo(() => {
    const cits: Citation[] = [];
    const seen = new Set<string>();
    messages.forEach(m => {
      if (m.citations && m.citations.length > 0) {
        m.citations.forEach(c => {
          const key = `${c.episode_title}-${c.quote.slice(0, 50)}`;
          if (!seen.has(key)) {
            seen.add(key);
            cits.push(c);
          }
        });
      }
    });
    return cits;
  }, [messages]);

  const getSessionIdFromUrl = (): string | null => {
    if (typeof window === 'undefined') return null;
    const params = new URLSearchParams(window.location.search);
    return params.get('session') || params.get('session_id') || null;
  };

  const updateUrlWithSession = (sessionId: string | null, push: boolean = true) => {
    if (typeof window === 'undefined') return;
    const url = new URL(window.location.href);
    if (sessionId) {
      url.searchParams.set('session', sessionId);
    } else {
      url.searchParams.delete('session');
      url.searchParams.delete('session_id');
    }
    if (push) {
      window.history.pushState({ sessionId }, '', url.toString());
    } else {
      window.history.replaceState({ sessionId }, '', url.toString());
    }
  };

  useEffect(() => {
    loadSessions();
    loadSystemHealth();
    const interval = setInterval(loadSystemHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handlePopState = () => {
      const urlSession = getSessionIdFromUrl();
      if (urlSession && urlSession !== currentSessionId) {
        selectSession(urlSession, false);
      }
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [currentSessionId]);

  const loadSystemHealth = async () => {
    try {
      const [h, ing] = await Promise.all([fetchHealth(), fetchIngestionStatus()]);
      setHealth(h);
      setIngestion(ing);
    } catch (_) {
      // Backend starting up
    }
  };

  const loadSessions = async () => {
    try {
      const data = await fetchSessions();
      setSessions(data);
      const urlSession = getSessionIdFromUrl();
      if (urlSession) {
        selectSession(urlSession, false);
      } else if (data.length > 0 && !currentSessionId) {
        selectSession(data[0].id, false);
      }
    } catch (e) {
      console.error('Failed to load sessions:', e);
    }
  };

  const selectSession = async (sessionId: string, updateUrl: boolean = true) => {
    setCurrentSessionId(sessionId);
    if (updateUrl) {
      updateUrlWithSession(sessionId);
    }
    try {
      const detail = await getSession(sessionId);
      setMessages(detail.messages || []);
      setArtifacts(detail.artifacts || []);
      if (detail.artifacts && detail.artifacts.length > 0) {
        setActiveArtifact(detail.artifacts[detail.artifacts.length - 1]);
      }
    } catch (e) {
      console.error('Failed to load session detail:', e);
    }
  };

  const handleNewChat = async () => {
    try {
      const newSess = await createSession('New Conversation', provider);
      setSessions([newSess, ...sessions]);
      setCurrentSessionId(newSess.id);
      updateUrlWithSession(newSess.id);
      setMessages([]);
      setArtifacts([]);
      setActiveArtifact(null);
      setShowArtifactViewer(false);
    } catch (e) {
      console.error('Failed to create new chat:', e);
    }
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await deleteSession(id);
      const remaining = sessions.filter(s => s.id !== id);
      setSessions(remaining);
      if (currentSessionId === id) {
        if (remaining.length > 0) {
          selectSession(remaining[0].id);
        } else {
          setCurrentSessionId(null);
          updateUrlWithSession(null);
          setMessages([]);
          setArtifacts([]);
          setActiveArtifact(null);
        }
      }
    } catch (e) {
      console.error('Failed to delete session:', e);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isStreaming) return;

    const tempUserMsg: Message = {
      id: `user-${Date.now()}`,
      session_id: currentSessionId || '',
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };

    const activeModelName = provider === 'gemini' 
      ? (health?.gemini_model || 'gemini-3.1-flash-lite')
      : (health?.ollama_model || 'qwen2.5:1.5b');

    const tempAssistantId = `asst-${Date.now()}`;
    const tempAsstMsg: Message = {
      id: tempAssistantId,
      session_id: currentSessionId || '',
      role: 'assistant',
      content: '',
      model: activeModelName,
      citations: [],
      artifacts: [],
      created_at: new Date().toISOString(),
      isStreaming: true
    };

    setMessages(prev => [...prev, tempUserMsg, tempAsstMsg]);
    setIsStreaming(true);
    setThinkingStage({ stage: 'starting', message: 'Initializing agent router...' });

    const controller = new AbortController();
    abortControllerRef.current = controller;

    let accumulatedContent = '';
    const citationsCollected: Citation[] = [];
    const artifactsCollected: Artifact[] = [];

    await streamChat({
      message: text,
      sessionId: currentSessionId || undefined,
      provider,
      modelName: activeModelName,
      enableShip30: text.trim().toLowerCase().startsWith('/ship30for30'),
      signal: controller.signal,
      onSessionResolved: (resolvedId) => {
        if (!currentSessionId) {
          setCurrentSessionId(resolvedId);
          updateUrlWithSession(resolvedId);
          loadSessions();
        }
      },
      onThinking: (data) => {
        setThinkingStage(data);
      },
      onToken: (token) => {
        accumulatedContent += token;
        setMessages(prev => 
            prev.map(m => m.id === tempAssistantId ? { ...m, content: accumulatedContent } : m)
        );
      },
      onCitation: (citation) => {
        citationsCollected.push(citation);
        setMessages(prev => 
          prev.map(m => m.id === tempAssistantId ? { ...m, citations: [...citationsCollected] } : m)
        );
      },
      onArtifact: (art) => {
        artifactsCollected.push(art);
        setArtifacts(prev => [...prev, art]);
        setActiveArtifact(art);
        setShowArtifactViewer(true);
        setMessages(prev => 
          prev.map(m => m.id === tempAssistantId ? { ...m, artifacts: [...artifactsCollected] } : m)
        );
      },
      onDone: (data) => {
        setIsStreaming(false);
        setThinkingStage(null);
        setMessages(prev => 
          prev.map(m => m.id === tempAssistantId ? { ...m, isStreaming: false } : m)
        );
        loadSessions();
      },
      onError: (err) => {
        setIsStreaming(false);
        setThinkingStage(null);
        setMessages(prev => 
          prev.map(m => m.id === tempAssistantId ? { 
            ...m, 
            content: m.content + `\n\n*(Error: ${err})*`,
            isStreaming: false 
          } : m)
        );
      }
    });
  };

  const handleStopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
    setThinkingStage(null);
  };

  const currentSession = sessions.find(s => s.id === currentSessionId);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#07021C] text-[#F3F4F6] relative">
      {/* Ambient background orbs in Midnight Cyan and Emerald */}
      <div className="fixed top-0 right-0 w-[550px] h-[550px] rounded-full bg-[#1C82AD]/[0.10] blur-[90px] pointer-events-none -z-0" />
      <div className="fixed bottom-0 left-48 w-[400px] h-[400px] rounded-full bg-[#03C988]/[0.08] blur-[70px] pointer-events-none -z-0" />
      <div className="relative z-10 flex w-full h-full">
        {/* Left Sidebar */}
        <Sidebar
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelectSession={selectSession}
          onNewChat={handleNewChat}
          onDeleteSession={handleDeleteSession}
          provider={provider}
          onProviderChange={setProvider}
          health={health}
          ingestion={ingestion}
          isOpen={isSidebarOpen}
          onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        />

        {/* Main Chat Center Panel */}
        <main className="flex-1 flex flex-col min-w-0 h-full relative bg-[#07021C]">
          <ChatHeader
            sessionTitle={currentSession?.title || 'New Conversation'}
            provider={provider}
            modelName={provider === 'gemini' ? (health?.gemini_model ? health.gemini_model.replace('gemini-', 'Gemini ') : 'Gemini') : (health?.ollama_model ? `Local ${health.ollama_model}` : 'Local Ollama')}
            showArtifactViewer={showArtifactViewer}
            onToggleArtifactViewer={() => setShowArtifactViewer(!showArtifactViewer)}
            showSourcesDrawer={showSourcesDrawer}
            onToggleSourcesDrawer={() => setShowSourcesDrawer(!showSourcesDrawer)}
            onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
            artifactsCount={artifacts.length}
            sourcesCount={sessionCitations.length}
          />

          <MessageList
            messages={messages}
            isStreaming={isStreaming}
            thinkingStage={thinkingStage}
            onOpenArtifact={(art) => {
              setActiveArtifact(art);
              setShowArtifactViewer(true);
            }}
            onSelectCitation={(citation, index) => {
              if (index !== undefined) {
                setActiveCitationIndex(index);
              }
              setShowSourcesDrawer(true);
            }}
          />

          <MessageInput
            onSendMessage={handleSendMessage}
            isStreaming={isStreaming}
            onStopStreaming={handleStopStreaming}
          />
        </main>

        {/* Right Side Artifact Viewer Panel */}
        {showArtifactViewer && (
          <aside className="w-full md:w-[480px] lg:w-[560px] h-full flex-shrink-0 z-20 shadow-2xl">
            <ArtifactViewer
              artifact={activeArtifact}
              artifactsList={artifacts}
              onSelectArtifact={(art) => setActiveArtifact(art)}
              onClose={() => setShowArtifactViewer(false)}
            />
          </aside>
        )}

        {/* Sources & Retrieved Chunks Drawer */}
        <SourceDrawer
          citations={sessionCitations}
          isOpen={showSourcesDrawer}
          onClose={() => setShowSourcesDrawer(false)}
          activeCitationIndex={activeCitationIndex}
        />
      </div>
    </div>
  );
};

export default App;
