import React, { useState, useRef, useEffect } from 'react';
import { Square, PenTool, ArrowUp, Zap } from 'lucide-react';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  isStreaming: boolean;
  onStopStreaming: () => void;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  isStreaming,
  onStopStreaming,
}) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const isSlash30 = input.trim().toLowerCase().startsWith('/ship30for30');
  const showSlashHint = input.startsWith('/') && !isSlash30;

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    onSendMessage(input.trim());
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const quickPrompts = [
    'Brian Chesky on Founder Mode & 2-Release Cycle',
    'Shreyas Doshi LNO Framework breakdown',
    'Elena Verna B2B Growth Loops & PLG',
    'How did Nikita Bier build viral apps?',
  ];

  return (
    <div className="
      flex-shrink-0 z-10
      px-4 sm:px-6 pt-3 pb-4
      bg-gradient-to-t from-[#07090F] via-[#07090F]/95 to-transparent
      border-t border-white/[0.06]
    ">
      <div className="max-w-4xl mx-auto space-y-2.5">

        {/* Slash autocomplete hint */}
        {showSlashHint && (
          <div className="
            flex items-center justify-between
            px-3.5 py-2.5 rounded-xl
            bg-[#0F0A1E] border border-orange-500/35
            shadow-lg ring-1 ring-orange-500/15
            animate-fade-up
          ">
            <button
              onClick={() => {
                setInput('/ship30for30 ');
                textareaRef.current?.focus();
              }}
              className="flex items-center gap-2.5 text-orange-300 hover:text-orange-100 font-medium text-xs"
            >
              <PenTool className="w-3.5 h-3.5 text-orange-400" />
              <code className="font-mono bg-orange-500/15 px-2 py-0.5 rounded border border-orange-500/30 text-orange-200 text-[11px]">
                /ship30for30 &lt;topic&gt;
              </code>
              <span className="text-slate-400 text-[11px]">— Generate a Ship 30 Atomic Essay</span>
            </button>
            <span className="text-[10px] text-slate-500 font-mono">Tab or Click</span>
          </div>
        )}

        {/* Quick-prompt chips */}
        {!showSlashHint && (
          <div className="hidden sm:flex items-center gap-1.5 overflow-x-auto pb-0.5 no-scrollbar">
            <span className="flex items-center gap-1 text-[10.5px] font-semibold text-slate-500 flex-shrink-0 mr-1">
              <Zap className="w-3 h-3 text-orange-400" />
              Prompts:
            </span>

            {/* /ship30for30 pill — orange accent */}
            <button
              id="ship30-quick-btn"
              onClick={() => {
                setInput('/ship30for30 Brian Chesky on Founder Mode');
                textareaRef.current?.focus();
              }}
              disabled={isStreaming}
              className="
                flex items-center gap-1.5 px-2.5 py-1 rounded-lg flex-shrink-0
                bg-orange-500/10 hover:bg-orange-500/18 border border-orange-500/25
                text-orange-300 hover:text-orange-100
                text-[11px] font-semibold transition-all disabled:opacity-40
              "
            >
              <PenTool className="w-3 h-3" />
              /ship30for30 Founder Mode
            </button>

            {/* Regular prompts */}
            {quickPrompts.map((qp, idx) => (
              <button
                key={idx}
                onClick={() => onSendMessage(qp)}
                disabled={isStreaming}
                className="
                  px-2.5 py-1 rounded-lg flex-shrink-0 whitespace-nowrap
                  bg-white/[0.03] hover:bg-white/[0.07] border border-white/[0.06] hover:border-white/[0.12]
                  text-slate-400 hover:text-slate-200
                  text-[11px] font-medium transition-all disabled:opacity-40
                "
              >
                {qp}
              </button>
            ))}
          </div>
        )}

        {/* Input box */}
        <form
          onSubmit={handleSubmit}
          className={`
            relative flex items-end gap-2
            rounded-2xl p-3
            border transition-all duration-200
            ${isSlash30
              ? 'bg-[#100A1A] border-orange-500/45 ring-2 ring-orange-500/15 shadow-lg shadow-orange-900/20'
              : 'bg-[#0C0F1C] border-white/[0.09] focus-within:border-violet-500/50 focus-within:ring-2 focus-within:ring-violet-500/15 focus-within:shadow-lg focus-within:shadow-violet-900/20'
            }
          `}
        >
          {/* Left: Ship30 indicator */}
          {isSlash30 && (
            <div className="flex-shrink-0 self-center pl-1">
              <PenTool className="w-4 h-4 text-orange-400" />
            </div>
          )}

          <textarea
            ref={textareaRef}
            rows={1}
            id="main-chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isSlash30
                ? 'Topic for Ship 30 Atomic Essay (e.g. Brian Chesky on Founder Mode)…'
                : 'Ask a product question, or type /ship30for30 to craft an Atomic Essay…'
            }
            disabled={isStreaming}
            className={`
              w-full bg-transparent text-slate-100 text-sm focus:outline-none resize-none
              px-2 py-1 max-h-44 leading-relaxed
              ${isSlash30
                ? 'placeholder-orange-400/50'
                : 'placeholder-slate-500'
              }
            `}
          />

          <div className="flex items-center gap-1.5 flex-shrink-0 pb-0.5">
            {isStreaming ? (
              <button
                type="button"
                onClick={onStopStreaming}
                className="
                  w-8 h-8 rounded-xl flex items-center justify-center
                  bg-rose-600 hover:bg-rose-500 text-white
                  shadow-md shadow-rose-600/30 transition-all active:scale-95
                "
                title="Stop generation"
              >
                <Square className="w-3.5 h-3.5 fill-current" />
              </button>
            ) : (
              <button
                type="submit"
                id="send-message-btn"
                disabled={!input.trim()}
                className={`
                  w-8 h-8 rounded-xl flex items-center justify-center
                  shadow-md transition-all active:scale-95
                  ${input.trim()
                    ? isSlash30
                      ? 'bg-gradient-to-br from-orange-500 to-orange-600 hover:from-orange-400 hover:to-orange-500 text-white shadow-orange-600/30'
                      : 'bg-gradient-to-br from-violet-600 to-violet-700 hover:from-violet-500 hover:to-violet-600 text-white shadow-violet-600/30'
                    : 'bg-white/[0.05] text-slate-500 cursor-not-allowed border border-white/[0.05]'
                  }
                `}
              >
                <ArrowUp className="w-4 h-4" />
              </button>
            )}
          </div>
        </form>

        {/* Footer hint */}
        <div className="flex items-center justify-between text-[10.5px] text-slate-600 px-1">
          <span>Grounded in Lenny's Podcast transcript archive.</span>
          <span className="hidden sm:inline">
            <kbd className="font-mono bg-white/[0.06] px-1.5 py-0.5 rounded text-slate-400 text-[10px]">Enter</kbd>
            {' '}to send,{' '}
            <kbd className="font-mono bg-white/[0.06] px-1.5 py-0.5 rounded text-slate-400 text-[10px]">Shift+Enter</kbd>
            {' '}for newline
          </span>
        </div>
      </div>
    </div>
  );
};
