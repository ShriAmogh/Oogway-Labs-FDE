import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  Eye, Code2, Copy, Check, Download, X, Maximize2, 
  Minimize2, Shield, Sparkles, Layers 
} from 'lucide-react';
import { Artifact } from '../../types';

interface ArtifactViewerProps {
  artifact: Artifact | null;
  artifactsList: Artifact[];
  onSelectArtifact: (art: Artifact) => void;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({
  artifact,
  artifactsList,
  onSelectArtifact,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [copied, setCopied] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (!artifact) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-center text-[#90CAF9]/80 bg-[#070F1E] border-l border-[#2196F3]/20">
        <div className="w-12 h-12 rounded-2xl bg-[#0D1B33] border border-[#2196F3]/30 flex items-center justify-center mb-3 text-[#2196F3]">
          <Code2 className="w-6 h-6" />
        </div>
        <h4 className="font-bold text-white text-sm mb-1">No Artifact Selected</h4>
        <p className="text-xs text-[#90CAF9]/80 max-w-xs leading-relaxed">
          Ask the assistant to generate a product framework, checklist template, or interactive HTML tool to render artifacts here.
        </p>
      </div>
    );
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = artifact.artifact_type === 'html' ? 'html' : 'md';
    const filename = `${artifact.title.toLowerCase().replace(/[^a-z0-9]/g, '_')}.${ext}`;
    const blob = new Blob([artifact.content], { 
      type: artifact.artifact_type === 'html' ? 'text/html' : 'text/markdown' 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={`flex flex-col h-full bg-[#070F1E] border-l border-[#2196F3]/20 transition-all duration-200 ${
      isFullscreen ? 'fixed inset-0 z-50 bg-[#070F1E]' : 'w-full'
    }`}>
      {/* Header Bar */}
      <div className="p-3 border-b border-[#2196F3]/20 bg-[#0D1B33]/90 backdrop-blur-md flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-7 h-7 rounded-xl bg-[#0D47A1]/50 border border-[#2196F3]/40 text-[#2196F3] flex items-center justify-center flex-shrink-0">
            <Code2 className="w-3.5 h-3.5" />
          </div>
          <div className="min-w-0">
            <h3 className="font-semibold text-xs text-white truncate tracking-tight">
              {artifact.title}
            </h3>
            <div className="flex items-center gap-2 text-[10px] text-[#90CAF9]/80">
              <span className="uppercase font-mono font-bold text-[#2196F3]">{artifact.artifact_type}</span>
              <span>•</span>
              <span className="flex items-center gap-1 text-[#90CAF9] font-bold">
                <Shield className="w-3 h-3" /> Sandboxed Execution
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          {/* Preview / Code Tab Switcher */}
          <div className="flex bg-[#070F1E] p-0.5 rounded-xl border border-[#2196F3]/20 text-xs">
            <button
              onClick={() => setActiveTab('preview')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs transition-all ${
                activeTab === 'preview'
                  ? 'bg-[#2196F3] text-white font-bold shadow-xs'
                  : 'text-[#90CAF9]/80 hover:text-white'
              }`}
            >
              <Eye className="w-3 h-3" />
              <span>Preview</span>
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs transition-all ${
                activeTab === 'code'
                  ? 'bg-[#2196F3] text-white font-bold shadow-xs'
                  : 'text-[#90CAF9]/80 hover:text-white'
              }`}
            >
              <Code2 className="w-3 h-3" />
              <span>Source</span>
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="p-1.5 rounded-lg text-[#90CAF9] hover:text-white hover:bg-white/[0.06] transition-colors"
            title="Copy content"
          >
            {copied ? <Check className="w-4 h-4 text-[#2196F3]" /> : <Copy className="w-4 h-4" />}
          </button>

          <button
            onClick={handleDownload}
            className="p-1.5 rounded-lg text-[#90CAF9] hover:text-white hover:bg-white/[0.06] transition-colors"
            title="Download file"
          >
            <Download className="w-4 h-4" />
          </button>

          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 rounded-lg text-[#90CAF9] hover:text-white hover:bg-white/[0.06] transition-colors"
            title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#90CAF9] hover:text-white hover:bg-white/[0.06] transition-colors"
            title="Close viewer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Artifact Selector Carousel if multiple artifacts exist */}
      {artifactsList.length > 1 && (
        <div className="px-3 py-1.5 border-b border-[#2196F3]/20 bg-[#070F1E] flex items-center gap-1.5 overflow-x-auto text-[11px] no-scrollbar">
          <span className="text-[#90CAF9] flex items-center gap-1 flex-shrink-0 font-medium">
            <Layers className="w-3 h-3 text-[#2196F3]" />
            Artifacts:
          </span>
          {artifactsList.map((art) => (
            <button
              key={art.id}
              onClick={() => onSelectArtifact(art)}
              className={`px-2.5 py-0.8 rounded-lg flex items-center gap-1.5 flex-shrink-0 transition-all font-medium ${
                artifact.id === art.id
                  ? 'bg-[#2196F3]/25 text-[#E3F2FD] border border-[#2196F3]/50 font-bold'
                  : 'bg-[#0D1B33] text-[#90CAF9]/80 hover:text-white border border-[#2196F3]/20'
              }`}
            >
              <span className="truncate max-w-[140px]">{art.title}</span>
              <span className="text-[9px] uppercase font-mono px-1 rounded bg-[#070F1E]">
                {art.artifact_type}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* Main Canvas Area */}
      <div className="flex-1 overflow-auto p-4 bg-[#070F1E]">
        {activeTab === 'preview' ? (
          artifact.artifact_type === 'html' ? (
            <div className="w-full h-full min-h-[500px] rounded-xl overflow-hidden border border-[#2196F3]/30 bg-white shadow-2xl">
              <iframe
                title={artifact.title}
                srcDoc={artifact.content}
                sandbox="allow-scripts"
                className="w-full h-full border-none"
              />
            </div>
          ) : (
            <div className="prose prose-invert max-w-3xl mx-auto p-6 bg-[#0D1B33] rounded-2xl border border-[#2196F3]/25 shadow-2xl">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {artifact.content}
              </ReactMarkdown>
            </div>
          )
        ) : (
          <div className="max-w-4xl mx-auto">
            <pre className="p-4 bg-[#0D1B33] rounded-xl border border-[#2196F3]/25 overflow-x-auto text-xs font-mono text-[#E3F2FD] leading-relaxed shadow-xl">
              <code>{artifact.content}</code>
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};
