import React, { useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  User, Sparkles, Copy, Check, Clock, Code2, Eye, ExternalLink,
  BookOpen, ArrowRight, PenTool, Brain, Layers
} from 'lucide-react';
import { Message, Citation, Artifact } from '../../types';
import { CitationChips } from './CitationChips';
import { GroundingAuditCard } from './GroundingAuditCard';

interface MessageListProps {
  messages: Message[];
  isStreaming: boolean;
  thinkingStage?: { stage: string; message: string } | null;
  onOpenArtifact?: (artifact: Artifact) => void;
  onSelectCitation?: (citation: Citation, index?: number) => void;
}

// Inline citation button
const InlineCitationBtn: React.FC<{
  label: string;
  citation: Citation;
  index: number;
  onSelect?: (c: Citation, i: number) => void;
}> = ({ label, citation, index, onSelect }) => (
  <button
    type="button"
    onClick={(e) => {
      e.stopPropagation();
      onSelect?.(citation, index);
    }}
    className="
      inline-flex items-center gap-1 mx-0.5 px-2 py-0.5 rounded-md
      text-[11px] font-mono font-semibold align-baseline
      bg-cyan-500/12 text-cyan-300 border border-cyan-500/30
      hover:bg-cyan-500/25 hover:text-cyan-100 hover:border-cyan-400/50
      transition-all cursor-pointer group
    "
    title={`Verified excerpt from ${citation?.guest || 'episode'}`}
  >
    <span>{label}</span>
    <ExternalLink className="w-2.5 h-2.5 opacity-50 group-hover:opacity-100 transition-opacity" />
  </button>
);

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isStreaming,
  thinkingStage,
  onOpenArtifact,
  onSelectCitation,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [copiedId, setCopiedId] = React.useState<string | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming, thinkingStage]);

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const processInlineCitations = (children: any, citations: Citation[]): any => {
    if (typeof children === 'string') {
      const parts = children.split(/(\[(?:[^\]]+,\s*)?Source\s*\d+\]|\[\d+\])/g);
      if (parts.length === 1) return children;

      return parts.map((part, pIdx) => {
        const match =
          part.match(/\[(?:([^\]]+),\s*)?Source\s*(\d+)\]/) ||
          part.match(/^\[(\d+)\]$/);
        if (match) {
          const sourceNum = parseInt(match[2] || match[1], 10);
          const citIdx = sourceNum - 1;
          const cit = citations[citIdx] || citations[0];
          const label = match[1] ? `${match[1]} [${sourceNum}]` : `[${sourceNum}]`;
          return (
            <InlineCitationBtn
              key={pIdx}
              label={label}
              citation={cit}
              index={citIdx}
              onSelect={onSelectCitation}
            />
          );
        }
        return part;
      });
    }

    if (Array.isArray(children)) {
      return children.map((c, i) => (
        <React.Fragment key={i}>{processInlineCitations(c, citations)}</React.Fragment>
      ));
    }

    return children;
  };

  const renderMarkdown = (content: string, citations?: Citation[]) => {
    if (!citations || citations.length === 0) {
      return <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>;
    }

    const components = {
      p: ({ children }: any) => (
        <p className="mb-3 last:mb-0 leading-relaxed">
          {processInlineCitations(children, citations)}
        </p>
      ),
      li: ({ children }: any) => (
        <li className="leading-relaxed">
          {processInlineCitations(children, citations)}
        </li>
      ),
    };

    return (
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    );
  };

  /* ── Empty / Welcome State ────────────── */
  if (messages.length === 0 && !isStreaming) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center overflow-y-auto">
        <div className="max-w-xl w-full mx-auto relative">
          {/* Ambient glow behind the hero */}
          <div className="absolute inset-0 -z-10 pointer-events-none">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-80 h-80 bg-violet-600/12 rounded-full blur-3xl" />
          </div>
          {/* Hero mark */}
          <div className="relative inline-block mb-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500 via-violet-600 to-violet-800 p-2.5 flex items-center justify-center shadow-2xl shadow-violet-500/40 ring-1 ring-violet-400/20 mx-auto">
              <img src="/logo.png" alt="Lenny Growth Logo" className="w-full h-full object-contain filter drop-shadow" />
            </div>
            <div className="absolute -inset-3 bg-violet-500 rounded-3xl blur-2xl opacity-20 -z-10" />
          </div>

          {/* Headline */}
          <h2 className="font-display font-800 text-2xl text-white tracking-tight mb-2">
            The Lenny Growth Assistant
          </h2>
          <p className="text-sm text-slate-400 leading-relaxed mb-8 max-w-md mx-auto">
            Frameworks, playbooks, and advice strictly grounded in{' '}
            <span className="text-violet-300 font-semibold">100+ Lenny's Podcast</span> transcripts.
            Every claim is cited.
          </p>

          {/* Suggestion Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
            {/* Card 1 — violet */}
            <div className="group p-4 rounded-xl bg-violet-500/05 hover:bg-violet-500/10 border border-violet-500/25 hover:border-violet-500/50 transition-all cursor-default">
              <div className="flex items-start justify-between mb-2">
                <span className="text-violet-400 font-semibold text-xs flex items-center gap-1.5">
                  <Brain className="w-3.5 h-3.5" />
                  Founder Mode vs Manager
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-violet-400 transition-colors" />
              </div>
              <p className="text-slate-400 text-[12px] leading-snug">
                "How does Brian Chesky think about the 2-release cycle and single roadmap at Airbnb?"
              </p>
            </div>

            {/* Card 2 — pink */}
            <div className="group p-4 rounded-xl bg-pink-500/05 hover:bg-pink-500/08 border border-pink-500/20 hover:border-pink-500/45 transition-all cursor-default">
              <div className="flex items-start justify-between mb-2">
                <span className="text-pink-400 font-semibold text-xs flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5" />
                  Shreyas Doshi LNO Model
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-pink-400 transition-colors" />
              </div>
              <p className="text-slate-400 text-[12px] leading-snug">
                "How should PMs categorize daily tasks into Leverage, Neutral, and Overhead?"
              </p>
            </div>

            {/* Card 3 — emerald */}
            <div className="group p-4 rounded-xl bg-emerald-500/05 hover:bg-emerald-500/08 border border-emerald-500/20 hover:border-emerald-500/45 transition-all cursor-default">
              <div className="flex items-start justify-between mb-2">
                <span className="text-emerald-400 font-semibold text-xs flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5" />
                  Elena Verna Growth Loops
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-emerald-400 transition-colors" />
              </div>
              <p className="text-slate-400 text-[12px] leading-snug">
                "What makes a B2B product-led growth loop scalable and defensible?"
              </p>
            </div>

            {/* Card 4 — orange/ship30 */}
            <div className="group p-4 rounded-xl bg-orange-500/05 hover:bg-orange-500/08 border border-orange-500/20 hover:border-orange-500/45 transition-all cursor-default">
              <div className="flex items-start justify-between mb-2">
                <span className="text-orange-400 font-semibold text-xs flex items-center gap-1.5">
                  <PenTool className="w-3.5 h-3.5" />
                  Ship 30 for 30 Essay
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-orange-400 transition-colors" />
              </div>
              <p className="text-slate-400 text-[12px] leading-snug">
                Type{' '}
                <code className="text-orange-300 font-mono text-[11px] bg-orange-500/12 px-1.5 py-0.5 rounded border border-orange-500/25">
                  /ship30for30
                </code>{' '}
                to transform insights into a viral atomic essay.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  /* ── Message Thread ───────────────────── */
  return (
    <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 space-y-5">
      {messages.map((msg) => {
        const isUser = msg.role === 'user';

        return (
          <div
            key={msg.id}
            className={`flex gap-3 max-w-4xl mx-auto animate-fade-up ${
              isUser ? 'justify-end' : 'justify-start'
            }`}
          >
            {/* Assistant avatar */}
            {!isUser && (
              <div className="flex-shrink-0 mt-1">
                <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-violet-500 to-violet-700 p-1 flex items-center justify-center shadow-md shadow-violet-500/25 ring-1 ring-violet-400/20">
                  <img src="/logo.png" alt="Lenny Assistant" className="w-full h-full object-contain filter drop-shadow" />
                </div>
              </div>
            )}

            {/* Bubble */}
            <div
              className={`
                relative group rounded-2xl transition-all
                ${isUser
                  ? 'max-w-[85%] sm:max-w-2xl bg-[#18103A] border border-violet-500/25 text-slate-100 rounded-tr-sm px-4 py-3 text-sm shadow-lg shadow-violet-900/20'
                  : 'w-full bg-[#0D1322] border border-white/[0.07] text-slate-200 rounded-tl-sm px-5 py-4'
                }
              `}
            >
              {/* Assistant message header */}
              {!isUser && (
                <div className="flex items-center justify-between pb-2.5 mb-3 border-b border-white/[0.06] text-[11px]">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-200 tracking-tight">Lenny Growth Advisor</span>
                    {msg.model && (
                      <span className="text-[10px] bg-violet-500/10 border border-violet-500/20 px-1.5 py-0.5 rounded font-mono text-violet-300">
                        {msg.model}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    {msg.latency_ms && msg.latency_ms > 0 && (
                      <span className="flex items-center gap-1 text-[10px] text-slate-500 font-mono">
                        <Clock className="w-2.5 h-2.5" />
                        {(msg.latency_ms / 1000).toFixed(2)}s
                      </span>
                    )}
                    <button
                      onClick={() => handleCopy(msg.content, msg.id)}
                      className="text-slate-500 hover:text-slate-300 p-0.5 rounded transition-colors"
                      title="Copy response"
                    >
                      {copiedId === msg.id
                        ? <Check className="w-3.5 h-3.5 text-emerald-400" />
                        : <Copy className="w-3.5 h-3.5" />
                      }
                    </button>
                  </div>
                </div>
              )}

              {/* Markdown body */}
              <div className="prose prose-invert max-w-none text-sm">
                {renderMarkdown(msg.content, msg.citations)}
              </div>

              {/* Artifact chips */}
              {msg.artifacts && msg.artifacts.length > 0 && (
                <div className="mt-4 pt-3.5 border-t border-white/[0.06] flex flex-wrap gap-2">
                  {msg.artifacts.map((art) => (
                    <button
                      key={art.id}
                      onClick={() => onOpenArtifact?.(art)}
                      className="
                        group flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold
                        bg-violet-500/10 hover:bg-violet-500/18 border border-violet-500/30
                        text-violet-200 transition-all shadow-sm
                      "
                    >
                      <Code2 className="w-3.5 h-3.5 text-violet-400" />
                      <span>{art.title}</span>
                      <span className="text-[9.5px] bg-violet-500/25 px-1.5 py-0.5 rounded uppercase font-mono font-bold text-violet-300">
                        {art.artifact_type}
                      </span>
                      <Eye className="w-3 h-3 ml-0.5 text-violet-400 group-hover:translate-x-0.5 transition-transform" />
                    </button>
                  ))}
                </div>
              )}

              {/* Grounding Audit Card */}
              {!isUser && msg.citations && msg.citations.length > 0 && (
                <GroundingAuditCard
                  citations={msg.citations}
                  onSelectCitation={onSelectCitation}
                />
              )}

              {/* Citation chips */}
              {!isUser && msg.citations && msg.citations.length > 0 && (
                <CitationChips
                  citations={msg.citations}
                  onSelectCitation={onSelectCitation}
                />
              )}
            </div>

            {/* User avatar */}
            {isUser && (
              <div className="flex-shrink-0 mt-1">
                <div className="w-7 h-7 rounded-xl bg-[#1C1535] border border-violet-700/40 flex items-center justify-center shadow-md">
                  <User className="w-3.5 h-3.5 text-violet-300" />
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* Thinking / streaming indicator */}
      {isStreaming && thinkingStage && (
        <div className="
          flex gap-3 max-w-4xl mx-auto items-center
          text-xs text-violet-300
          bg-[#0E0C1F] border border-violet-500/30
          rounded-xl px-4 py-3 shadow-sm animate-fade-up
        ">
          <Sparkles className="w-4 h-4 text-violet-400 animate-spin flex-shrink-0" />
          <span className="font-medium tracking-wide">{thinkingStage.message}</span>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
};
