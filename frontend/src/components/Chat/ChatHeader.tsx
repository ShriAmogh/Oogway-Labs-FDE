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
      border-b border-[#2196F3]/20
      bg-[#091322]/90 backdrop-blur-xl
      px-4 flex items-center justify-between
    ">
      {/* Left: Title + model badge */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="md:hidden p-1.5 rounded-lg text-[#90CAF9] hover:text-white hover:bg-[#0E1D35] transition-colors"
        >
          <Menu className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-2.5">
          <h2 className="font-semibold text-sm text-[#E3F2FD] truncate max-w-[160px] sm:max-w-sm tracking-tight">
            {sessionTitle || 'New Conversation'}
          </h2>

          {/* Model badge */}
          <span className={`
            hidden sm:inline-flex items-center gap-1.5
            px-2.5 py-1 rounded-full text-[11px] font-mono font-semibold
            border transition-colors
            ${isGemini
              ? 'bg-[#2196F3]/20 text-[#E3F2FD] border-[#2196F3]/40'
              : 'bg-[#0D47A1]/40 text-[#90CAF9] border-[#90CAF9]/40'
            }
          `}>
            <span className="w-1.5 h-1.5 rounded-full bg-[#2196F3] animate-pulse" />
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
              ? 'bg-[#2196F3]/25 border-[#2196F3]/60 text-white shadow-sm'
              : 'bg-[#0E1D35] hover:bg-[#13284A] text-[#90CAF9] hover:text-white border-[#2196F3]/20'
            }
          `}
          title="View retrieved transcript sources"
        >
          <Layers className={`w-3.5 h-3.5 ${showSourcesDrawer ? 'text-[#2196F3]' : 'text-[#90CAF9]'}`} />
          <span className="hidden sm:inline">Sources</span>
          {sourcesCount > 0 && (
            <span className={`
              px-1.5 py-0.5 rounded-full text-[10px] font-mono font-bold border
              ${showSourcesDrawer
                ? 'bg-[#2196F3] text-white border-[#2196F3]'
                : 'bg-[#060D1A] text-[#90CAF9] border-[#2196F3]/30'
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
              ? 'bg-[#2196F3]/20 border-[#2196F3]/60 text-[#E3F2FD] shadow-sm shadow-[#2196F3]/15'
              : 'bg-[#0E1D35] hover:bg-[#13284A] text-[#90CAF9] hover:text-white border-[#2196F3]/20'
            }
          `}
          title="Toggle artifact viewer"
        >
          <LayoutTemplate className={`w-3.5 h-3.5 ${showArtifactViewer ? 'text-[#2196F3]' : 'text-[#90CAF9]'}`} />
          <span className="hidden sm:inline">Artifacts</span>
          {artifactsCount > 0 && (
            <span className={`
              px-1.5 py-0.5 rounded-full text-[10px] font-mono font-bold border
              ${showArtifactViewer
                ? 'bg-[#2196F3] text-white border-[#2196F3]'
                : 'bg-[#060D1A] text-[#90CAF9] border-[#2196F3]/30'
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
