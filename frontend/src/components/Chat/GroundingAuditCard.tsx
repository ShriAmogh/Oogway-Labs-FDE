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
    <div className="mt-3.5 rounded-xl border border-white/[0.07] bg-[#08101A]/80 overflow-hidden transition-all hover:border-emerald-500/20 shadow-sm">
      {/* Toggle bar */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-3.5 py-2.5 flex items-center justify-between text-left hover:bg-white/[0.025] transition-colors"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-5 h-5 rounded-md bg-emerald-500/12 border border-emerald-500/25 flex items-center justify-center flex-shrink-0">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-semibold text-slate-200">Grounded in Transcripts</span>
            <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded-full bg-emerald-500/12 text-emerald-300 border border-emerald-500/25">
              100% Verified
            </span>
            <span className="text-[11px] text-slate-500 hidden sm:inline">
              · {citations.length} citation{citations.length > 1 ? 's' : ''} mapped
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1 text-slate-500 text-[11px] font-medium">
          <span className="hidden sm:inline">{isExpanded ? 'Hide' : 'Inspect'}</span>
          {isExpanded
            ? <ChevronUp className="w-3.5 h-3.5" />
            : <ChevronDown className="w-3.5 h-3.5" />
          }
        </div>
      </button>

      {/* Expanded claim list */}
      {isExpanded && (
        <div className="px-3.5 pb-3.5 pt-1 border-t border-white/[0.05] bg-[#060910]/60 space-y-2">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest pt-1.5 pb-0.5">
            Claim Provenance Mapping
          </div>
          <div className="space-y-1.5">
            {citations.map((c, idx) => (
              <div
                key={idx}
                onClick={() => onSelectCitation?.(c, idx)}
                className="
                  flex items-start sm:items-center justify-between gap-2
                  p-2.5 rounded-lg bg-white/[0.025] border border-white/[0.05]
                  hover:border-cyan-500/30 hover:bg-cyan-500/05
                  cursor-pointer transition-all group
                "
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                  <span className="text-xs text-slate-300 truncate">
                    <span className="font-mono font-bold text-slate-200 mr-1.5">[{idx + 1}]</span>
                    <span className="text-slate-400">{c.guest || 'Host'}:</span>{' '}
                    "{c.quote.slice(0, 70)}…"
                  </span>
                </div>
                <div className="flex items-center gap-1.5 flex-shrink-0 text-cyan-400 group-hover:text-cyan-300">
                  <span className="text-[10px] bg-cyan-500/10 border border-cyan-500/20 px-1.5 py-0.5 rounded font-mono font-bold">
                    Chunk
                  </span>
                  <ExternalLink className="w-3 h-3 opacity-50 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
