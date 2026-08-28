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
      bg-gradient-to-t from-[#070F1E] via-[#070F1E]/95 to-transparent
      border-t border-[#2196F3]/20
    ">
      <div className="max-w-4xl mx-auto space-y-2.5">

        {/* Slash autocomplete hint */}
        {showSlashHint && (
          <div className="
            flex items-center justify-between
            px-3.5 py-2.5 rounded-xl
            bg-[#0E1D35] border border-[#F97316]/50
            shadow-lg ring-1 ring-[#F97316]/25
            animate-fade-up
          ">
            <button
              onClick={() => {
                setInput('/ship30for30 ');
                textareaRef.current?.focus();
              }}
              className="flex items-center gap-2.5 text-[#F97316] hover:text-white font-medium text-xs"
            >
              <PenTool className="w-3.5 h-3.5 text-[#F97316]" />
              <code className="font-mono bg-[#F97316]/20 px-2 py-0.5 rounded border border-[#F97316]/40 text-[#E3F2FD] text-[11px]">
                /ship30for30 &lt;topic&gt;
              </code>
              <span className="text-[#90CAF9]/80 text-[11px]">— Generate a Ship 30 Atomic Essay</span>
            </button>
            <span className="text-[10px] text-[#90CAF9]/70 font-mono">Tab or Click</span>
          </div>
        )}

        {/* Quick-prompt chips */}
        {!showSlashHint && (
          <div className="hidden sm:flex items-center gap-1.5 overflow-x-auto pb-0.5 no-scrollbar">
            <span className="flex items-center gap-1 text-[10.5px] font-bold text-[#90CAF9]/80 flex-shrink-0 mr-1">
              <Zap className="w-3 h-3 text-[#2196F3]" />
              Prompts:
            </span>

            {/* /ship30for30 pill — vibrant orange */}
            <button
              id="ship30-quick-btn"
              onClick={() => {
                setInput('/ship30for30 Brian Chesky on Founder Mode');
                textareaRef.current?.focus();
              }}
              disabled={isStreaming}
              className="
                flex items-center gap-1.5 px-2.5 py-1 rounded-lg flex-shrink-0
                bg-[#F97316]/20 hover:bg-[#F97316]/30 border border-[#F97316]/60
                text-[#F97316] hover:text-white
                text-[11px] font-bold transition-all disabled:opacity-40
                shadow-xs shadow-[#F97316]/10
              "
            >
              <PenTool className="w-3 h-3 text-[#F97316]" />
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
                  bg-[#0E1D35] hover:bg-[#13284A] border border-[#2196F3]/20 hover:border-[#2196F3]/40
                  text-[#90CAF9] hover:text-white
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
              ? 'bg-[#0E1D35] border-[#F97316]/80 ring-2 ring-[#F97316]/25 shadow-lg shadow-[#F97316]/20'
              : 'bg-[#0D1B33] border-[#2196F3]/30 focus-within:border-[#2196F3] focus-within:ring-2 focus-within:ring-[#2196F3]/20'
            }
          `}
        >
          {isSlash30 && (
            <div className="flex-shrink-0 self-center pl-1">
              <PenTool className="w-4 h-4 text-[#F97316]" />
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
              w-full bg-transparent text-[#E3F2FD] text-sm focus:outline-none resize-none
              px-2 py-1 max-h-44 leading-relaxed
              ${isSlash30
                ? 'placeholder-[#F97316]/80'
                : 'placeholder-[#90CAF9]/60'
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
                  shadow-md transition-all active:scale-95
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
                      ? 'bg-[#F97316] hover:bg-[#EA580C] text-white font-bold shadow-[#F97316]/30'
                      : 'bg-[#2196F3] hover:bg-[#1E88E5] text-white font-bold shadow-[#2196F3]/30'
                    : 'bg-[#0E1D35] text-[#90CAF9]/40 cursor-not-allowed border border-[#2196F3]/15'
                  }
                `}
              >
                <ArrowUp className="w-4 h-4 stroke-[2.5]" />
              </button>
            )}
          </div>
        </form>

        {/* Footer hint */}
        <div className="flex items-center justify-between text-[10.5px] text-[#90CAF9]/70 px-1">
          <span>Grounded in Lenny's Podcast transcript archive.</span>
          <span className="hidden sm:inline">
            <kbd className="font-mono bg-[#0E1D35] px-1.5 py-0.5 rounded text-[#E3F2FD] text-[10px] border border-[#2196F3]/20">Enter</kbd>
            {' '}to send,{' '}
            <kbd className="font-mono bg-[#0E1D35] px-1.5 py-0.5 rounded text-[#E3F2FD] text-[10px] border border-[#2196F3]/20">Shift+Enter</kbd>
            {' '}for newline
          </span>
        </div>
      </div>
    </div>
  );
};
