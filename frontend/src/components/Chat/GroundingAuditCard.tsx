import React, { useState } from 'react';
import { ShieldCheck, ChevronDown, ChevronUp, ExternalLink, CheckCircle2 } from 'lucide-react';
import { Citation } from '../../types';

interface GroundingAuditCardProps {
  citations: Citation[];
  onSelectCitation?: (citation: Citation, index?: number) => void;
}

export const GroundingAuditCard: React.FC<GroundingAuditCardProps> = ({
  citations,
  onSelectCitation,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-3.5 rounded-xl border border-[#1C82AD]/30 bg-[#0B0424] overflow-hidden transition-all hover:border-[#03C988]/50 shadow-sm">
      {/* Toggle bar */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-3.5 py-2.5 flex items-center justify-between text-left hover:bg-[#100732] transition-colors"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-5 h-5 rounded-md bg-[#03C988]/20 border border-[#03C988]/40 flex items-center justify-center flex-shrink-0">
            <ShieldCheck className="w-3.5 h-3.5 text-[#03C988]" />
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-bold text-white">Grounded in Transcripts</span>
            <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded-full bg-[#03C988]/20 text-[#03C988] border border-[#03C988]/40">
              100% Verified
            </span>
            <span className="text-[11px] text-[#A0AEC0] hidden sm:inline">
              · {citations.length} citation{citations.length > 1 ? 's' : ''} mapped
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1 text-[#A0AEC0] text-[11px] font-medium">
          <span className="hidden sm:inline">{isExpanded ? 'Hide' : 'Inspect'}</span>
          {isExpanded
            ? <ChevronUp className="w-3.5 h-3.5 text-[#A0AEC0]" />
            : <ChevronDown className="w-3.5 h-3.5 text-[#A0AEC0]" />
          }
        </div>
      </button>

      {/* Expanded claim list */}
      {isExpanded && (
        <div className="px-3.5 pb-3.5 pt-1 border-t border-[#1C82AD]/20 bg-[#07021C] space-y-2">
          <div className="text-[10px] font-bold text-[#A0AEC0] uppercase tracking-widest pt-1.5 pb-0.5">
            Claim Provenance Mapping
          </div>
          <div className="space-y-1.5">
            {citations.map((c, idx) => (
              <div
                key={idx}
                onClick={() => onSelectCitation?.(c, idx)}
                className="
                  flex items-start sm:items-center justify-between gap-2
                  p-2.5 rounded-lg bg-[#0E0630] border border-[#1C82AD]/20
                  hover:border-[#03C988]/50 hover:bg-[#13093E]
                  cursor-pointer transition-all group
                "
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-[#03C988] flex-shrink-0" />
                  <span className="text-xs text-[#F3F4F6] truncate">
                    <span className="font-mono font-bold text-[#1C82AD] mr-1.5">[{idx + 1}]</span>
                    <span className="text-[#A0AEC0]">{c.guest || 'Host'}:</span>{' '}
                    "{c.quote.slice(0, 70)}…"
                  </span>
                </div>
                <div className="flex items-center gap-1.5 flex-shrink-0 text-[#03C988] group-hover:text-white">
                  <span className="text-[10px] bg-[#00337C]/40 border border-[#1C82AD]/40 px-1.5 py-0.5 rounded font-mono font-bold">
                    Chunk
                  </span>
                  <ExternalLink className="w-3 h-3 opacity-60 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
