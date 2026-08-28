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
      <div className="h-full flex flex-col items-center justify-center p-6 text-center text-slate-400 bg-[#07090F] border-l border-white/[0.07]">
        <div className="w-12 h-12 rounded-2xl bg-white/[0.04] border border-white/[0.06] flex items-center justify-center mb-3 text-slate-400">
          <Code2 className="w-6 h-6" />
        </div>
        <h4 className="font-semibold text-slate-200 text-sm mb-1">No Artifact Selected</h4>
        <p className="text-xs text-slate-400 max-w-xs leading-relaxed">
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
    <div className={`flex flex-col h-full bg-[#080C14] border-l border-white/[0.08] transition-all duration-200 ${
      isFullscreen ? 'fixed inset-0 z-50 bg-[#080C14]' : 'w-full'
    }`}>
      {/* Header Bar */}
      <div className="p-3 border-b border-white/[0.06] bg-[#0C1220]/90 backdrop-blur-md flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-7 h-7 rounded-xl bg-violet-500/12 border border-violet-500/25 text-violet-400 flex items-center justify-center flex-shrink-0">
            <Code2 className="w-3.5 h-3.5" />
          </div>
          <div className="min-w-0">
            <h3 className="font-semibold text-xs text-slate-100 truncate tracking-tight">
              {artifact.title}
            </h3>
            <div className="flex items-center gap-2 text-[10px] text-slate-400">
              <span className="uppercase font-mono font-bold text-violet-400">{artifact.artifact_type}</span>
              <span>•</span>
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <Shield className="w-3 h-3" /> Sandboxed Execution
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          {/* Preview / Code Tab Switcher */}
          <div className="flex bg-[#070A11] p-0.5 rounded-xl border border-white/[0.06] text-xs">
            <button
              onClick={() => setActiveTab('preview')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs transition-all ${
                activeTab === 'preview'
                  ? 'bg-violet-600 text-white font-medium shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Eye className="w-3 h-3" />
              <span>Preview</span>
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs transition-all ${
                activeTab === 'code'
                  ? 'bg-violet-600 text-white font-medium shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Code2 className="w-3 h-3" />
              <span>Source</span>
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-white/[0.06] transition-colors"
            title="Copy content"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>

          <button
            onClick={handleDownload}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-white/[0.06] transition-colors"
            title="Download file"
          >
            <Download className="w-4 h-4" />
          </button>

          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-white/[0.06] transition-colors"
            title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-white/[0.06] transition-colors"
            title="Close viewer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Artifact Selector Carousel if multiple artifacts exist */}
      {artifactsList.length > 1 && (
        <div className="px-3 py-1.5 border-b border-white/[0.06] bg-[#070A11] flex items-center gap-1.5 overflow-x-auto text-[11px] no-scrollbar">
          <span className="text-slate-400 flex items-center gap-1 flex-shrink-0 font-medium">
            <Layers className="w-3 h-3 text-blue-400" />
            Artifacts:
          </span>
          {artifactsList.map((art) => (
            <button
              key={art.id}
              onClick={() => onSelectArtifact(art)}
              className={`px-2.5 py-0.8 rounded-lg flex items-center gap-1.5 flex-shrink-0 transition-all font-medium ${
                artifact.id === art.id
                  ? 'bg-violet-500/18 text-violet-300 border border-violet-500/40'
                  : 'bg-white/[0.03] text-slate-400 hover:text-slate-200 border border-white/[0.04]'
              }`}
            >
              <span className="truncate max-w-[140px]">{art.title}</span>
              <span className="text-[9px] uppercase font-mono px-1 rounded bg-white/[0.06]">
                {art.artifact_type}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* Main Canvas Area */}
      <div className="flex-1 overflow-auto p-4 bg-[#080C14]">
        {activeTab === 'preview' ? (
          artifact.artifact_type === 'html' ? (
            <div className="w-full h-full min-h-[500px] rounded-xl overflow-hidden border border-white/[0.08] bg-white shadow-2xl">
              <iframe
                title={artifact.title}
                srcDoc={artifact.content}
                sandbox="allow-scripts"
                className="w-full h-full border-none"
              />
            </div>
          ) : (
            <div className="prose prose-invert max-w-3xl mx-auto p-6 bg-[#0B0F19] rounded-2xl border border-white/[0.08] shadow-2xl">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {artifact.content}
              </ReactMarkdown>
            </div>
          )
        ) : (
          <div className="max-w-4xl mx-auto">
            <pre className="p-4 bg-[#0B0F19] rounded-xl border border-white/[0.08] overflow-x-auto text-xs font-mono text-slate-200 leading-relaxed shadow-xl">
              <code>{artifact.content}</code>
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};
