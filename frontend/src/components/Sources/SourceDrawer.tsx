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
    <div className="fixed inset-y-0 right-0 z-40 w-full sm:w-[480px] bg-[#08091C]/95 backdrop-blur-2xl border-l border-white/[0.07] shadow-2xl flex flex-col transition-all duration-300">
      {/* Header */}
      <div className="p-4 border-b border-white/[0.06] flex items-center justify-between bg-[#0A0B1A]/80">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center">
            <BookOpen className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-slate-100 tracking-tight">Retrieved Transcript Sources</h3>
            <p className="text-[11px] text-slate-400">Grounded evidence from Lenny's Podcast archive</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-white/[0.06] transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Chunks List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3.5">
        {citations.length === 0 ? (
          <div className="text-center py-16 text-slate-400 text-xs space-y-2">
            <Layers className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="font-medium text-slate-300">No chunks retrieved for this session yet</p>
            <p className="text-[11px] text-slate-400 max-w-xs mx-auto">
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
                    ? 'bg-[#0D0F22] border-cyan-400 ring-2 ring-cyan-500/25 shadow-lg shadow-cyan-500/10'
                    : 'bg-white/[0.025] border-white/[0.06] hover:border-white/[0.12] hover:bg-white/[0.045]'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start gap-2.5">
                    <span className="w-5 h-5 rounded-md bg-cyan-500/18 text-cyan-300 font-mono text-[10px] flex items-center justify-center font-bold flex-shrink-0 mt-0.5 border border-cyan-500/30">
                      {idx + 1}
                    </span>
                    <div>
                      <h4 className="font-semibold text-xs text-slate-100 tracking-tight leading-snug">
                        {c.episode_title}
                      </h4>
                      {c.guest && (
                        <p className="text-[11px] text-cyan-400 font-medium mt-0.5">
                          Guest: <span className="text-slate-200">{c.guest}</span>
                        </p>
                      )}
                    </div>
                  </div>

                  {c.relevance_score && (
                    <span className="text-[9.5px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.2 rounded-md font-semibold flex-shrink-0">
                      RRF: {c.relevance_score}
                    </span>
                  )}
                </div>

                {/* Quote Excerpt */}
                <div className="bg-[#070A11] p-3 rounded-xl border border-white/[0.04] text-xs text-slate-300 leading-relaxed italic flex gap-2">
                  <Quote className="w-3.5 h-3.5 text-cyan-500/50 flex-shrink-0 mt-0.5" />
                  <p className="font-serif text-[11.5px] text-slate-300">"{c.quote}"</p>
                </div>

                <div className="flex items-center justify-between text-[10.5px] text-slate-400 pt-0.5">
                  <span className="flex items-center gap-1 text-slate-400">
                    <Clock className="w-3 h-3" />
                    <span>{c.timestamp_or_section || 'Section Quote'}</span>
                  </span>
                  <span className="flex items-center gap-1 text-emerald-400 font-medium">
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
