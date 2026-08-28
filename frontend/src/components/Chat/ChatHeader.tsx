import React from 'react';
import { Menu, Layers, LayoutTemplate } from 'lucide-react';

interface ChatHeaderProps {
  sessionTitle: string;
  provider: 'gemini' | 'ollama';
  modelName?: string;
  showArtifactViewer: boolean;
  onToggleArtifactViewer: () => void;
  showSourcesDrawer: boolean;
  onToggleSourcesDrawer: () => void;
  onToggleSidebar: () => void;
  artifactsCount: number;
  sourcesCount: number;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  sessionTitle,
  provider,
  modelName,
  showArtifactViewer,
  onToggleArtifactViewer,
  showSourcesDrawer,
  onToggleSourcesDrawer,
  onToggleSidebar,
  artifactsCount,
  sourcesCount,
}) => {
  const isGemini = provider === 'gemini';

  return (
    <header className="
      h-14 flex-shrink-0 z-20
      border-b border-white/[0.07]
      bg-[#08091A]/80 backdrop-blur-xl
      px-4 flex items-center justify-between
    ">
      {/* Left: Title + model badge */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="md:hidden p-1.5 rounded-lg text-slate-500 hover:text-slate-200 hover:bg-white/[0.06] transition-colors"
        >
          <Menu className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-2.5">
          <h2 className="font-semibold text-sm text-slate-100 truncate max-w-[160px] sm:max-w-sm tracking-tight">
            {sessionTitle || 'New Conversation'}
          </h2>

          {/* Model badge */}
          <span className={`
            hidden sm:inline-flex items-center gap-1.5
            px-2.5 py-1 rounded-full text-[11px] font-mono font-semibold
            border transition-colors
            ${isGemini
              ? 'bg-violet-500/10 text-violet-300 border-violet-500/25'
              : 'bg-orange-500/10 text-orange-300 border-orange-500/25'
            }
          `}>
            <span className={`w-1.5 h-1.5 rounded-full ${isGemini ? 'bg-violet-400' : 'bg-orange-400'} animate-pulse`} />
            {modelName || (isGemini ? 'Google Gemini' : 'Local Ollama')}
          </span>
        </div>
      </div>

      {/* Right: action buttons */}
      <div className="flex items-center gap-2">
        {/* Sources toggle */}
        <button
          id="sources-toggle-btn"
          onClick={onToggleSourcesDrawer}
          className={`
            flex items-center gap-1.5 py-1.5 px-3 rounded-xl text-[12px] font-semibold
            border transition-all duration-150
            ${showSourcesDrawer
              ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-300 shadow-sm'
              : 'bg-white/[0.04] hover:bg-white/[0.07] text-slate-400 hover:text-slate-200 border-white/[0.07] hover:border-white/[0.12]'
            }
          `}
          title="View retrieved transcript sources"
        >
          <Layers className={`w-3.5 h-3.5 ${showSourcesDrawer ? 'text-cyan-400' : 'text-slate-500'}`} />
          <span className="hidden sm:inline">Sources</span>
          {sourcesCount > 0 && (
            <span className={`
              px-1.5 py-0.5 rounded-full text-[10px] font-mono font-bold border
              ${showSourcesDrawer
                ? 'bg-cyan-500/25 text-cyan-200 border-cyan-500/30'
                : 'bg-white/[0.08] text-slate-300 border-white/[0.08]'
              }
            `}>
              {sourcesCount}
            </span>
          )}
        </button>

        {/* Artifacts toggle */}
        <button
          id="artifacts-toggle-btn"
          onClick={onToggleArtifactViewer}
          className={`
            flex items-center gap-1.5 py-1.5 px-3 rounded-xl text-[12px] font-semibold
            border transition-all duration-150
            ${showArtifactViewer
              ? 'bg-violet-500/15 border-violet-500/40 text-violet-200 shadow-sm shadow-violet-500/10'
              : 'bg-white/[0.04] hover:bg-white/[0.07] text-slate-400 hover:text-slate-200 border-white/[0.07] hover:border-white/[0.12]'
            }
          `}
          title="Toggle artifact viewer"
        >
          <LayoutTemplate className={`w-3.5 h-3.5 ${showArtifactViewer ? 'text-violet-400' : 'text-slate-500'}`} />
          <span className="hidden sm:inline">Artifacts</span>
          {artifactsCount > 0 && (
            <span className={`
              px-1.5 py-0.5 rounded-full text-[10px] font-mono font-bold border
              ${showArtifactViewer
                ? 'bg-violet-500/30 text-violet-200 border-violet-500/40'
                : 'bg-white/[0.08] text-slate-300 border-white/[0.08]'
              }
            `}>
              {artifactsCount}
            </span>
          )}
        </button>
      </div>
    </header>
  );
};
