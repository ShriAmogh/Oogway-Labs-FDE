import React, { useState } from 'react';
import { BookOpen, X, Quote, Clock } from 'lucide-react';
import { Citation } from '../../types';

interface CitationChipsProps {
  citations?: Citation[];
  onSelectCitation?: (cit: Citation) => void;
}

export const CitationChips: React.FC<CitationChipsProps> = ({ citations, onSelectCitation }) => {
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-3.5 pt-3 border-t border-white/[0.06]">
      {/* Section header */}
      <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-1.5">
        <BookOpen className="w-3 h-3 text-cyan-500" />
        Transcript References ({citations.length})
      </div>

      <div className="flex flex-wrap gap-1.5">
        {citations.map((c, idx) => (
          <button
            key={idx}
            onClick={() => {
              setActiveCitation(c);
              onSelectCitation?.(c);
            }}
            className="
              group flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px]
              bg-cyan-500/08 hover:bg-cyan-500/15 border border-cyan-500/20 hover:border-cyan-500/40
              text-cyan-400 hover:text-cyan-200
              transition-all shadow-sm
            "
          >
            <span className="
              w-4 h-4 rounded-md flex items-center justify-center text-[10px] font-mono font-bold
              bg-cyan-500/20 text-cyan-300
              group-hover:bg-cyan-500 group-hover:text-white transition-colors
            ">
              {idx + 1}
            </span>
            <span className="font-medium truncate max-w-[180px]">
              {c.guest ?? c.episode_title}
            </span>
            {c.timestamp_or_section && (
              <span className="text-[10px] text-slate-500 truncate max-w-[80px]">
                {c.timestamp_or_section}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Quote Preview Modal */}
      {activeCitation && (
        <div
          className="fixed inset-0 z-50 bg-black/75 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setActiveCitation(null)}
        >
          <div
            className="
              bg-[#0B0F1F] border border-white/[0.12] rounded-2xl
              max-w-lg w-full p-6 shadow-2xl space-y-4 relative
              ring-1 ring-cyan-500/10
            "
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close */}
            <button
              onClick={() => setActiveCitation(null)}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-500 hover:text-slate-100 hover:bg-white/[0.07] transition-colors"
            >
              <X className="w-4 h-4" />
            </button>

            {/* Header */}
            <div>
              <span className="text-[10px] font-mono uppercase bg-cyan-500/12 text-cyan-300 px-2 py-0.5 rounded-md font-bold border border-cyan-500/25">
                Verified Transcript Citation
              </span>
              <h3 className="font-semibold text-base text-slate-100 mt-2 tracking-tight leading-snug">
                {activeCitation.episode_title}
              </h3>
              {activeCitation.guest && (
                <p className="text-xs text-slate-400 mt-0.5">
                  Guest: <strong className="text-slate-200">{activeCitation.guest}</strong>
                </p>
              )}
            </div>

            {/* Quote block */}
            <div className="bg-[#07090F] p-4 rounded-xl border border-white/[0.06] relative">
              <Quote className="w-5 h-5 text-cyan-500/25 absolute top-3 left-3 -scale-x-100" />
              <p className="text-sm text-slate-200 italic pl-5 leading-relaxed">
                "{activeCitation.quote}"
              </p>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                {activeCitation.timestamp_or_section || 'Full Episode'}
              </span>
              <button
                onClick={() => setActiveCitation(null)}
                className="px-3 py-1.5 bg-white/[0.06] hover:bg-white/[0.1] text-slate-300 rounded-lg font-semibold text-xs transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
