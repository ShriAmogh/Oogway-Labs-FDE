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
      text-[11px] font-mono font-bold align-baseline
      bg-[#00337C]/40 text-[#44E5AB] border border-[#1C82AD]/50
      hover:bg-[#03C988] hover:text-[#07021C]
      transition-all cursor-pointer group shadow-xs
    "
    title={`Verified excerpt from ${citation?.guest || 'episode'}`}
  >
    <span>{label}</span>
    <ExternalLink className="w-2.5 h-2.5 opacity-60 group-hover:opacity-100 transition-opacity" />
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
        <p className="mb-3 last:mb-0 leading-relaxed text-[#F3F4F6]">
          {processInlineCitations(children, citations)}
        </p>
      ),
      li: ({ children }: any) => (
        <li className="leading-relaxed text-[#F3F4F6]">
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
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-80 h-80 bg-[#1C82AD]/20 rounded-full blur-3xl" />
          </div>
          {/* Hero mark */}
          <div className="relative inline-block mb-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#00337C] via-[#1C82AD] to-[#03C988] p-2.5 flex items-center justify-center shadow-2xl shadow-[#03C988]/30 ring-1 ring-white/20 mx-auto">
              <img src="/logo.png" alt="Lenny Growth Logo" className="w-full h-full object-contain filter drop-shadow" />
            </div>
            <div className="absolute -inset-3 bg-[#03C988] rounded-3xl blur-2xl opacity-20 -z-10" />
          </div>

          {/* Headline */}
          <h2 className="font-display font-800 text-2xl text-white tracking-tight mb-2">
            The Lenny Growth Assistant
          </h2>
          <p className="text-sm text-[#A0AEC0] leading-relaxed mb-8 max-w-md mx-auto">
            Frameworks, playbooks, and advice strictly grounded in{' '}
            <span className="text-[#03C988] font-semibold">100+ Lenny's Podcast</span> transcripts.
            Every claim is cited.
          </p>

          {/* Suggestion Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
            {/* Card 1 — Emerald */}
            <div className="group p-4 rounded-xl bg-[#0E0630] hover:bg-[#13093E] border border-[#03C988]/30 hover:border-[#03C988]/60 transition-all cursor-default shadow-sm">
              <div className="flex items-start justify-between mb-2">
                <span className="text-[#03C988] font-bold text-xs flex items-center gap-1.5">
                  <Brain className="w-3.5 h-3.5" />
                  Founder Mode vs Manager
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-[#A0AEC0] group-hover:text-white transition-colors" />
              </div>
              <p className="text-[#CBD5E1] text-[12px] leading-snug">
                "How does Brian Chesky think about the 2-release cycle and single roadmap at Airbnb?"
              </p>
            </div>

            {/* Card 2 — Cyan */}
            <div className="group p-4 rounded-xl bg-[#0E0630] hover:bg-[#13093E] border border-[#1C82AD]/30 hover:border-[#1C82AD]/60 transition-all cursor-default shadow-sm">
              <div className="flex items-start justify-between mb-2">
                <span className="text-[#1C82AD] font-bold text-xs flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5" />
                  Shreyas Doshi LNO Model
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-[#A0AEC0] group-hover:text-white transition-colors" />
              </div>
              <p className="text-[#CBD5E1] text-[12px] leading-snug">
                "How should PMs categorize daily tasks into Leverage, Neutral, and Overhead?"
              </p>
            </div>

            {/* Card 3 — Deep Sapphire */}
            <div className="group p-4 rounded-xl bg-[#0E0630] hover:bg-[#13093E] border border-[#00337C]/40 hover:border-[#1C82AD]/60 transition-all cursor-default shadow-sm">
              <div className="flex items-start justify-between mb-2">
                <span className="text-[#4FB1DC] font-bold text-xs flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-[#03C988]" />
                  Elena Verna Growth Loops
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-[#A0AEC0] group-hover:text-white transition-colors" />
              </div>
              <p className="text-[#CBD5E1] text-[12px] leading-snug">
                "What makes a B2B product-led growth loop scalable and defensible?"
              </p>
            </div>

            {/* Card 4 — Ship 30 */}
            <div className="group p-4 rounded-xl bg-[#0E0630] hover:bg-[#13093E] border border-[#03C988]/40 hover:border-[#03C988]/80 transition-all cursor-default shadow-sm">
              <div className="flex items-start justify-between mb-2">
                <span className="text-[#03C988] font-bold text-xs flex items-center gap-1.5">
                  <PenTool className="w-3.5 h-3.5" />
                  Ship 30 for 30 Essay
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-[#A0AEC0] group-hover:text-[#03C988] transition-colors" />
              </div>
              <p className="text-[#CBD5E1] text-[12px] leading-snug">
                Type{' '}
                <code className="text-[#07021C] font-mono text-[11px] bg-[#03C988] px-1.5 py-0.5 rounded font-bold">
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
                <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-[#00337C] to-[#03C988] p-1 flex items-center justify-center shadow-md shadow-[#03C988]/25 ring-1 ring-white/20">
                  <img src="/logo.png" alt="Lenny Assistant" className="w-full h-full object-contain filter drop-shadow" />
                </div>
              </div>
            )}

            {/* Bubble */}
            <div
              className={`
                relative group rounded-2xl transition-all
                ${isUser
                  ? 'max-w-[85%] sm:max-w-2xl bg-[#13005A] border border-[#1C82AD]/40 text-white rounded-tr-sm px-4 py-3 text-sm shadow-md'
                  : 'w-full bg-[#0E0630] border border-[#1C82AD]/25 text-[#F3F4F6] rounded-tl-sm px-5 py-4 shadow-sm'
                }
              `}
            >
              {/* Assistant message header */}
              {!isUser && (
                <div className="flex items-center justify-between pb-2.5 mb-3 border-b border-[#1C82AD]/20 text-[11px]">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-white tracking-tight">Lenny Growth Advisor</span>
                    {msg.model && (
                      <span className="text-[10px] bg-[#00337C]/40 border border-[#1C82AD]/30 px-1.5 py-0.5 rounded font-mono text-[#03C988]">
                        {msg.model}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    {msg.latency_ms && msg.latency_ms > 0 && (
                      <span className="flex items-center gap-1 text-[10px] text-[#A0AEC0] font-mono">
                        <Clock className="w-2.5 h-2.5 text-[#1C82AD]" />
                        {(msg.latency_ms / 1000).toFixed(2)}s
                      </span>
                    )}
                    <button
                      onClick={() => handleCopy(msg.content, msg.id)}
                      className="text-[#A0AEC0] hover:text-white p-0.5 rounded transition-colors"
                      title="Copy response"
                    >
                      {copiedId === msg.id
                        ? <Check className="w-3.5 h-3.5 text-[#03C988]" />
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
                <div className="mt-4 pt-3.5 border-t border-[#1C82AD]/20 flex flex-wrap gap-2">
                  {msg.artifacts.map((art) => (
                    <button
                      key={art.id}
                      onClick={() => onOpenArtifact?.(art)}
                      className="
                        group flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold
                        bg-[#03C988]/15 hover:bg-[#03C988]/25 border border-[#03C988]/40
                        text-[#03C988] transition-all shadow-sm
                      "
                    >
                      <Code2 className="w-3.5 h-3.5 text-[#03C988]" />
                      <span>{art.title}</span>
                      <span className="text-[9.5px] bg-[#03C988] text-[#07021C] px-1.5 py-0.5 rounded uppercase font-mono font-bold">
                        {art.artifact_type}
                      </span>
                      <Eye className="w-3 h-3 ml-0.5 text-[#03C988] group-hover:translate-x-0.5 transition-transform" />
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
                <div className="w-7 h-7 rounded-xl bg-[#13005A] border border-[#1C82AD]/40 flex items-center justify-center shadow-md">
                  <User className="w-3.5 h-3.5 text-[#03C988]" />
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
          text-xs text-white
          bg-[#0E0630] border border-[#1C82AD]/40
          rounded-xl px-4 py-3 shadow-sm animate-fade-up
        ">
          <Sparkles className="w-4 h-4 text-[#03C988] animate-spin flex-shrink-0" />
          <span className="font-medium tracking-wide">{thinkingStage.message}</span>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
};
