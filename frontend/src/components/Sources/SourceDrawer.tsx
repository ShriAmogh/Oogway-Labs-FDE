import React from 'react';
import { BookOpen, X, Quote, Layers, CheckCircle2, Clock } from 'lucide-react';
import { Citation } from '../../types';

interface SourceDrawerProps {
  citations: Citation[];
  isOpen: boolean;
  onClose: () => void;
  activeCitationIndex?: number | null;
}

export const SourceDrawer: React.FC<SourceDrawerProps> = ({ 
  citations, 
  isOpen, 
  onClose,
  activeCitationIndex 
}) => {
  React.useEffect(() => {
    if (isOpen && activeCitationIndex !== undefined && activeCitationIndex !== null) {
      setTimeout(() => {
        const el = document.getElementById(`source-card-${activeCitationIndex}`);
        el?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 100);
    }
  }, [isOpen, activeCitationIndex]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-40 w-full sm:w-[480px] bg-[#0B0424]/95 backdrop-blur-2xl border-l border-[#1C82AD]/30 shadow-2xl flex flex-col transition-all duration-300">
      {/* Header */}
      <div className="p-4 border-b border-[#1C82AD]/20 flex items-center justify-between bg-[#0E0630]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-[#00337C]/50 border border-[#1C82AD]/40 text-[#03C988] flex items-center justify-center">
            <BookOpen className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-white tracking-tight">Retrieved Transcript Sources</h3>
            <p className="text-[11px] text-[#A0AEC0]">Grounded evidence from Lenny's Podcast archive</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-[#A0AEC0] hover:text-white hover:bg-[#100732] transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Chunks List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3.5">
        {citations.length === 0 ? (
          <div className="text-center py-16 text-[#A0AEC0] text-xs space-y-2">
            <Layers className="w-10 h-10 text-[#1C82AD]/40 mx-auto" />
            <p className="font-medium text-white">No chunks retrieved for this session yet</p>
            <p className="text-[11px] text-[#A0AEC0] max-w-xs mx-auto">
              Ask a question to see the RRF hybrid retrieval and transcript verification pipeline in action.
            </p>
          </div>
        ) : (
          citations.map((c, idx) => {
            const isActive = activeCitationIndex === idx;
            return (
              <div
                id={`source-card-${idx}`}
                key={idx}
                className={`rounded-2xl p-4 space-y-3 transition-all duration-300 border ${
                  isActive
                    ? 'bg-[#100732] border-[#03C988] ring-2 ring-[#03C988]/25 shadow-lg shadow-[#03C988]/10'
                    : 'bg-[#0E0630] border-[#1C82AD]/20 hover:border-[#1C82AD]/50 hover:bg-[#13093E]'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start gap-2.5">
                    <span className="w-5 h-5 rounded-md bg-[#00337C] text-[#03C988] border border-[#1C82AD]/40 font-mono text-[10px] flex items-center justify-center font-bold flex-shrink-0 mt-0.5">
                      {idx + 1}
                    </span>
                    <div>
                      <h4 className="font-semibold text-xs text-white tracking-tight leading-snug">
                        {c.episode_title}
                      </h4>
                      {c.guest && (
                        <p className="text-[11px] text-[#1C82AD] font-medium mt-0.5">
                          Guest: <span className="text-[#F3F4F6]">{c.guest}</span>
                        </p>
                      )}
                    </div>
                  </div>

                  {c.relevance_score && (
                    <span className="text-[9.5px] font-mono bg-[#00337C]/50 text-[#03C988] border border-[#03C988]/40 px-1.5 py-0.2 rounded-md font-bold flex-shrink-0">
                      RRF: {c.relevance_score}
                    </span>
                  )}
                </div>

                {/* Quote Excerpt */}
                <div className="bg-[#07021C] p-3 rounded-xl border border-[#1C82AD]/20 text-xs text-[#F3F4F6] leading-relaxed italic flex gap-2">
                  <Quote className="w-3.5 h-3.5 text-[#03C988] flex-shrink-0 mt-0.5" />
                  <p className="font-serif text-[11.5px] text-[#F3F4F6]">"{c.quote}"</p>
                </div>

                <div className="flex items-center justify-between text-[10.5px] text-[#A0AEC0] pt-0.5">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3 text-[#1C82AD]" />
                    <span>{c.timestamp_or_section || 'Section Quote'}</span>
                  </span>
                  <span className="flex items-center gap-1 text-[#03C988] font-bold">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Verified</span>
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
