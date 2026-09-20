'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, BookOpen, AlertTriangle, Sparkles, HelpCircle, Loader2 } from 'lucide-react';
import { api, QAResponse } from '../lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: QAResponse['sources'];
  confidence?: number;
  highRiskFlag?: boolean;
  suggestedFollowups?: string[];
}

interface Props {
  documentId: string;
}

export const QAChatView: React.FC<Props> = ({ documentId }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hello! I am your NyayaAI Legal Assistant. Ask me anything about this document — like key obligations, termination clauses, notice periods, or risk factors.",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Fetch suggested questions for document
    api.getSuggestedQuestions(documentId).then((res) => {
      setSuggestedQuestions(res.questions);
    }).catch(console.error);
  }, [documentId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (questionText?: string) => {
    const q = questionText || input;
    if (!q.trim() || loading) return;

    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: q }]);
    setLoading(true);

    try {
      const res = await api.askDocument(documentId, q, conversationId);
      setConversationId(res.conversation_id);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.answer,
          sources: res.sources,
          confidence: res.confidence,
          highRiskFlag: res.high_risk_flag,
          suggestedFollowups: res.suggested_followups,
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Sorry, I encountered an error: ${err.message || 'Unable to process question.'}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[650px] bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      {/* Header */}
      <div className="p-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-indigo-950 border border-indigo-700/50 text-indigo-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">Document RAG Q&A Assistant</h3>
            <p className="text-xs text-slate-400">Strict grounding with clause-level citations</p>
          </div>
        </div>
        <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
          Guardrails Active
        </span>
      </div>

      {/* Messages List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-xl bg-indigo-950 border border-indigo-700/50 flex items-center justify-center shrink-0 text-indigo-400">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div
              className={`max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed space-y-3 ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-md'
                  : 'bg-slate-950 border border-slate-800 text-slate-200'
              }`}
            >
              {/* High risk flag alert */}
              {msg.highRiskFlag && (
                <div className="bg-rose-950/60 border border-rose-800/50 p-2.5 rounded-xl text-xs text-rose-300 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                  <span>High-Risk Topic Flagged — Human Legal Consultation Recommended</span>
                </div>
              )}

              <div className="whitespace-pre-wrap">{msg.content}</div>

              {/* Confidence badge */}
              {msg.confidence !== undefined && !isNaN(msg.confidence) && (
                <div className="flex items-center gap-2 pt-1 border-t border-slate-800/60">
                  <span className="text-[11px] text-slate-400 flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-amber-400" /> Grounding Confidence: {(msg.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              )}

              {/* Sources & Citations */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-2">
                  <div className="text-xs font-semibold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                    <BookOpen className="w-3.5 h-3.5" /> Cited Document Passages ({msg.sources.length})
                  </div>
                  <div className="space-y-1.5">
                    {msg.sources.map((src, i) => (
                      <div
                        key={i}
                        className="bg-slate-900 border border-slate-800 p-2.5 rounded-xl text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between text-slate-400 text-[11px]">
                          <span className="font-semibold text-slate-300">{src.document_name}</span>
                          {src.page && <span>Page {src.page}</span>}
                        </div>
                        <p className="text-slate-300 italic font-mono text-[11px]">"{src.text}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Suggested Followups */}
              {msg.suggestedFollowups && msg.suggestedFollowups.length > 0 && (
                <div className="mt-3 pt-2 flex flex-wrap gap-1.5">
                  {msg.suggestedFollowups.map((sf, i) => (
                    <button
                      key={i}
                      onClick={() => handleSend(sf)}
                      className="text-xs bg-slate-900 hover:bg-slate-800 text-indigo-300 border border-indigo-900/50 px-2.5 py-1 rounded-lg transition-colors text-left"
                    >
                      + {sf}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 text-slate-300">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3 text-slate-400 text-xs p-3">
            <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
            <span>Analyzing document passages with Gemini RAG...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Chips */}
      {suggestedQuestions.length > 0 && messages.length <= 3 && (
        <div className="p-3 bg-slate-950/60 border-t border-slate-800 flex items-center gap-2 overflow-x-auto">
          <HelpCircle className="w-4 h-4 text-indigo-400 shrink-0" />
          <span className="text-xs text-slate-400 shrink-0">Suggested:</span>
          {suggestedQuestions.slice(0, 4).map((q, i) => (
            <button
              key={i}
              onClick={() => handleSend(q)}
              className="text-xs bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 px-2.5 py-1 rounded-full shrink-0 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input Bar */}
      <div className="p-3 bg-slate-950 border-t border-slate-800 flex items-center gap-2">
        <input
          type="text"
          placeholder="Ask a question about your document..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
        />
        <button
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
          className="p-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 text-white disabled:opacity-40 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-indigo-600/20 transition-all"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
