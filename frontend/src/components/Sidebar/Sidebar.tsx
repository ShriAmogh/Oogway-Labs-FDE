import React, { useState } from 'react';
import { Plus, MessageSquare, Trash2, Database, Cpu, CheckCircle2, Zap } from 'lucide-react';
import { Session, HealthStatus, IngestionStatus } from '../../types';

interface SidebarProps {
  sessions: Session[];
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onDeleteSession: (id: string) => void;
  provider: 'gemini' | 'ollama';
  onProviderChange: (provider: 'gemini' | 'ollama') => void;
  health: HealthStatus | null;
  ingestion: IngestionStatus | null;
  isOpen: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  currentSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  provider,
  onProviderChange,
  health,
  ingestion,
  isOpen
}) => {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  const geminiOnline  = health?.gemini_configured;
  const ollamaOnline  = health?.ollama_connected;
  const activeOnline  = provider === 'gemini' ? geminiOnline : ollamaOnline;

  const geminiLabel = health?.gemini_model
    ? health.gemini_model.replace('gemini-', '').replace('-lite', ' lite')
    : '3.1-flash';
  const ollamaLabel = health?.ollama_model
    ? health.ollama_model.split(':')[0]
    : 'qwen2.5';

  return (
    <aside
      className={`
        w-72 flex-shrink-0 flex flex-col h-full z-30 transition-transform duration-300
        bg-[#0B0424] md:translate-x-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        border-r border-[#1C82AD]/20
      `}
    >
      {/* ── Brand Header ─────────────────────── */}
      <div className="px-5 pt-5 pb-4">
        {/* Logo mark */}
        <div className="flex items-center gap-3 mb-5">
          <div className="relative">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#00337C] via-[#1C82AD] to-[#03C988] p-1.5 flex items-center justify-center shadow-lg shadow-[#03C988]/25 ring-1 ring-white/20">
              <img src="/logo.png" alt="Lenny Growth Logo" className="w-full h-full object-contain filter drop-shadow" />
            </div>
            {/* Glow behind logo */}
            <div className="absolute inset-0 rounded-xl bg-[#03C988] blur-md opacity-25 -z-10" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-display font-800 text-sm text-white tracking-tight leading-none">
                Lenny Growth
              </h1>
              <span className="text-[9px] font-mono font-700 px-1.5 py-0.5 bg-[#03C988]/20 text-[#03C988] rounded border border-[#03C988]/40 uppercase tracking-widest">
                PRO
              </span>
            </div>
            <p className="text-[11px] text-[#A0AEC0] mt-0.5 font-medium">AI Product & Growth Advisor</p>
          </div>
        </div>

        {/* New Conversation CTA */}
        <button
          onClick={onNewChat}
          className="
            w-full group relative flex items-center justify-between
            py-2.5 px-4 rounded-xl font-semibold text-[12px]
            bg-gradient-to-r from-[#03C988] to-[#1C82AD] hover:from-[#02b378] hover:to-[#177196]
            text-[#07021C] font-bold transition-all duration-150
            shadow-md shadow-[#03C988]/20
            border border-white/20
            active:scale-[0.98]
          "
        >
          <div className="flex items-center gap-2">
            <Plus className="w-4 h-4 text-[#07021C] stroke-[2.5]" />
            <span>New Conversation</span>
          </div>
          <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[9.5px] bg-[#07021C]/25 rounded text-[#07021C] font-mono font-bold tracking-wide">⌘N</kbd>
        </button>
      </div>

      {/* ── Model Engine Selector ─────────────── */}
      <div className="px-4 pb-3">
        <div className="bg-[#100732] rounded-xl border border-[#1C82AD]/25 p-3 shadow-sm">
          {/* Header row */}
          <div className="flex items-center justify-between mb-2.5">
            <span className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-[#CBD5E1]">
              <Cpu className="w-3 h-3 text-[#1C82AD]" />
              Model Engine
            </span>
            {/* Status dot */}
            <span
              className={`flex items-center gap-1 text-[10px] font-mono font-medium ${
                activeOnline ? 'text-[#03C988]' : 'text-[#F2A65A]'
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${activeOnline ? 'bg-[#03C988]' : 'bg-[#F2A65A] animate-pulse'}`} />
              {activeOnline ? 'Online' : 'Offline'}
            </span>
          </div>

          {/* Segmented Controller */}
          <div className="grid grid-cols-2 gap-1 bg-[#08031D] p-1 rounded-lg border border-[#1C82AD]/20">
            <button
              onClick={() => onProviderChange('gemini')}
              className={`py-2 px-2 rounded-md text-[11px] font-semibold transition-all truncate text-center ${
                provider === 'gemini'
                  ? 'bg-[#1C82AD] text-white font-bold shadow-sm'
                  : 'text-[#A0AEC0] hover:text-white hover:bg-white/[0.04]'
              }`}
            >
              {geminiLabel}
            </button>
            <button
              onClick={() => onProviderChange('ollama')}
              className={`py-2 px-2 rounded-md text-[11px] font-semibold transition-all truncate text-center ${
                provider === 'ollama'
                  ? 'bg-[#1C82AD] text-white font-bold shadow-sm'
                  : 'text-[#A0AEC0] hover:text-white hover:bg-white/[0.04]'
              }`}
            >
              {ollamaLabel}
            </button>
          </div>

          {/* Model full name */}
          <div className="mt-2 px-1 text-[10px] text-[#A0AEC0] flex items-center justify-between">
            <span className="truncate">
              {provider === 'gemini'
                ? (health?.gemini_model || 'Google GenAI')
                : (health?.ollama_model ? `Local · ${health.ollama_model}` : 'Local Ollama')}
            </span>
            {provider === 'ollama' && !ollamaOnline && (
              <span className="text-[#03C988] font-medium">Auto Failover</span>
            )}
          </div>
        </div>
      </div>

      {/* ── Session Thread List ───────────────── */}
      <div className="flex-1 overflow-y-auto px-3 min-h-0">
        {/* Section label */}
        <div className="flex items-center justify-between px-2 py-2 mb-1">
          <span className="text-[10px] font-bold uppercase tracking-widest text-[#A0AEC0]">Threads</span>
          <span className="text-[10px] font-mono font-medium px-1.5 py-0.5 bg-[#100732] text-[#03C988] rounded border border-[#1C82AD]/25">
            {sessions.length}
          </span>
        </div>

        {sessions.length === 0 ? (
          <div className="text-center py-10 px-4">
            <MessageSquare className="w-8 h-8 text-[#1C82AD]/40 mx-auto mb-3" />
            <p className="text-xs font-medium text-[#CBD5E1]">No conversations yet</p>
            <p className="text-[11px] text-[#A0AEC0] mt-1">Ask a question or use /ship30for30 to begin.</p>
          </div>
        ) : (
          <div className="space-y-0.5">
            {sessions.map((s) => {
              const isActive = currentSessionId === s.id;
              return (
                <div
                  key={s.id}
                  onClick={() => onSelectSession(s.id)}
                  onMouseEnter={() => setHoveredId(s.id)}
                  onMouseLeave={() => setHoveredId(null)}
                  className={`
                    group relative flex items-center justify-between
                    p-2.5 rounded-xl cursor-pointer transition-all text-[12px]
                    ${isActive
                      ? 'bg-[#00337C]/35 border border-[#1C82AD]/50 text-white'
                      : 'border border-transparent text-[#CBD5E1] hover:bg-[#100732] hover:text-white'
                    }
                  `}
                >
                  {/* Active left accent bar */}
                  {isActive && (
                    <div className="absolute left-0 top-1/4 bottom-1/4 w-1 bg-[#03C988] rounded-r-full" />
                  )}

                  <div className="flex items-center gap-2.5 truncate pr-1">
                    <MessageSquare className={`w-3.5 h-3.5 flex-shrink-0 ${
                      isActive ? 'text-[#03C988]' : 'text-[#1C82AD] group-hover:text-white'
                    }`} />
                    <span className="truncate font-medium">{s.title || 'Untitled Conversation'}</span>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(s.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 rounded-lg transition-all text-[#A0AEC0]"
                    title="Delete thread"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* ── Knowledge Base Footer ─────────────── */}
      <div className="p-4 border-t border-[#1C82AD]/20 bg-[#08031D]">
        <div className="flex items-center justify-between mb-1.5">
          <span className="flex items-center gap-1.5 text-[11px] text-[#CBD5E1] font-medium">
            <Database className="w-3.5 h-3.5 text-[#03C988]" />
            Lenny Transcripts
          </span>
          <span className="font-mono font-semibold text-[#03C988] bg-[#03C988]/15 px-2 py-0.5 rounded border border-[#03C988]/30 text-[10px]">
            {ingestion?.total_chunks ? ingestion.total_chunks.toLocaleString() : '14,282'} chunks
          </span>
        </div>
        <div className="flex items-center justify-between text-[10px] text-[#A0AEC0]">
          <span className="flex items-center gap-1">
            <CheckCircle2 className="w-2.5 h-2.5 text-[#03C988]" />
            RRF Fusion + Reranker
          </span>
          <span className="flex items-center gap-1 text-[#1C82AD] font-medium">
            <Zap className="w-2.5 h-2.5" />
            Active
          </span>
        </div>
      </div>
    </aside>
  );
};
