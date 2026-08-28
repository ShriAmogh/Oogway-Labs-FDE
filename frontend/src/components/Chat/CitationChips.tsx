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
    <div className="mt-3.5 pt-3 border-t border-[#1C82AD]/20">
      {/* Section header */}
      <div className="text-[10px] font-bold text-[#A0AEC0] uppercase tracking-widest mb-2 flex items-center gap-1.5">
        <BookOpen className="w-3 h-3 text-[#03C988]" />
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
              bg-[#100732] hover:bg-[#00337C]/40 border border-[#1C82AD]/30 hover:border-[#03C988]/60
              text-[#F3F4F6] transition-all shadow-xs
            "
          >
            <span className="
              w-4 h-4 rounded-md flex items-center justify-center text-[10px] font-mono font-bold
              bg-[#00337C] text-[#03C988] border border-[#1C82AD]/30
              group-hover:bg-[#03C988] group-hover:text-[#07021C] transition-colors
            ">
              {idx + 1}
            </span>
            <span className="font-medium truncate max-w-[180px]">
              {c.guest ?? c.episode_title}
            </span>
            {c.timestamp_or_section && (
              <span className="text-[10px] text-[#A0AEC0] truncate max-w-[80px]">
                {c.timestamp_or_section}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Quote Preview Modal */}
      {activeCitation && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setActiveCitation(null)}
        >
          <div
            className="
              bg-[#0E0630] border border-[#1C82AD]/40 rounded-2xl
              max-w-lg w-full p-6 shadow-2xl space-y-4 relative
              ring-1 ring-[#03C988]/20
            "
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close */}
            <button
              onClick={() => setActiveCitation(null)}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-[#A0AEC0] hover:text-white hover:bg-white/[0.07] transition-colors"
            >
              <X className="w-4 h-4" />
            </button>

            {/* Header */}
            <div>
              <span className="text-[10px] font-mono uppercase bg-[#00337C]/50 text-[#03C988] px-2 py-0.5 rounded-md font-bold border border-[#03C988]/40">
                Verified Transcript Citation
              </span>
              <h3 className="font-semibold text-base text-white mt-2 tracking-tight leading-snug">
                {activeCitation.episode_title}
              </h3>
              {activeCitation.guest && (
                <p className="text-xs text-[#A0AEC0] mt-0.5">
                  Guest: <strong className="text-white">{activeCitation.guest}</strong>
                </p>
              )}
            </div>

            {/* Quote block */}
            <div className="bg-[#07021C] p-4 rounded-xl border border-[#1C82AD]/25 relative">
              <Quote className="w-5 h-5 text-[#03C988]/40 absolute top-3 left-3 -scale-x-100" />
              <p className="text-sm text-[#F3F4F6] italic pl-5 leading-relaxed font-serif">
                "{activeCitation.quote}"
              </p>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between text-[11px] text-[#A0AEC0] pt-1">
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-[#1C82AD]" />
                {activeCitation.timestamp_or_section || 'Full Episode'}
              </span>
              <button
                onClick={() => setActiveCitation(null)}
                className="px-3 py-1.5 bg-[#03C988] text-[#07021C] hover:bg-[#02a972] rounded-lg font-bold text-xs transition-colors"
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
