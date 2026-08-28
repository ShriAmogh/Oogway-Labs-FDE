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
      border-b border-[#1C82AD]/20
      bg-[#0B0424]/90 backdrop-blur-xl
      px-4 flex items-center justify-between
    ">
      {/* Left: Title + model badge */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="md:hidden p-1.5 rounded-lg text-[#A0AEC0] hover:text-white hover:bg-[#100732] transition-colors"
        >
          <Menu className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-2.5">
          <h2 className="font-semibold text-sm text-white truncate max-w-[160px] sm:max-w-sm tracking-tight">
            {sessionTitle || 'New Conversation'}
          </h2>

          {/* Model badge */}
          <span className={`
            hidden sm:inline-flex items-center gap-1.5
            px-2.5 py-1 rounded-full text-[11px] font-mono font-semibold
            border transition-colors
            ${isGemini
              ? 'bg-[#1C82AD]/20 text-[#44E5AB] border-[#1C82AD]/40'
              : 'bg-[#00337C]/40 text-[#03C988] border-[#03C988]/40'
            }
          `}>
            <span className="w-1.5 h-1.5 rounded-full bg-[#03C988] animate-pulse" />
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
              ? 'bg-[#1C82AD]/25 border-[#1C82AD]/60 text-white shadow-sm'
              : 'bg-[#100732] hover:bg-[#160B44] text-[#CBD5E1] hover:text-white border-[#1C82AD]/20'
            }
          `}
          title="View retrieved transcript sources"
        >
          <Layers className={`w-3.5 h-3.5 ${showSourcesDrawer ? 'text-[#03C988]' : 'text-[#1C82AD]'}`} />
          <span className="hidden sm:inline">Sources</span>
          {sourcesCount > 0 && (
            <span className={`
              px-1.5 py-0.5 rounded-full text-[10px] font-mono font-bold border
              ${showSourcesDrawer
                ? 'bg-[#03C988] text-[#07021C] border-[#03C988]'
                : 'bg-[#08031D] text-[#CBD5E1] border-[#1C82AD]/30'
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
              ? 'bg-[#03C988]/20 border-[#03C988]/60 text-[#03C988] shadow-sm shadow-[#03C988]/10'
              : 'bg-[#100732] hover:bg-[#160B44] text-[#CBD5E1] hover:text-white border-[#1C82AD]/20'
            }
          `}
          title="Toggle artifact viewer"
        >
          <LayoutTemplate className={`w-3.5 h-3.5 ${showArtifactViewer ? 'text-[#03C988]' : 'text-[#1C82AD]'}`} />
          <span className="hidden sm:inline">Artifacts</span>
          {artifactsCount > 0 && (
            <span className={`
              px-1.5 py-0.5 rounded-full text-[10px] font-mono font-bold border
              ${showArtifactViewer
                ? 'bg-[#03C988] text-[#07021C] border-[#03C988]'
                : 'bg-[#08031D] text-[#CBD5E1] border-[#1C82AD]/30'
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
