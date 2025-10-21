/**
 * ConversationHub.tsx
 *
 * Main AI conversation interface component.
 * Provides ChatGPT-style interface for querying the knowledge graph.
 *
 * Features:
 * - Natural language chat interface
 * - Memory-grounded responses with citations
 * - Conversation history persistence
 * - Voice input support
 * - Export conversations
 *
 * Usage:
 * ```tsx
 * <ConversationHub />
 * ```
 *
 * API Integration:
 * - POST /api/v1/conversation/query
 * - GET /api/v1/conversation/history
 * - POST /api/v1/conversation/export
 *
 * @see PLANNING.md Phase 2 for implementation details
 */

import React, { useState, useEffect, useRef } from 'react';
import { Send, Mic, Download, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/lib/api';
import { useSpeechRecognition } from '@/lib/speech-recognition';
import { MessageList } from './MessageList';
import { CitationPanel } from './CitationPanel';
import { ConversationSidebar } from './ConversationSidebar';

interface Message {
  uuid: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: Citation[];
  created_at: string;
}

interface Citation {
  document_uuid: string;
  document_title: string;
  relevant_excerpt: string;
  confidence_score: number;
}

interface Conversation {
  uuid: string;
  title: string;
  created_at: string;
  last_message_at: string;
}

export function ConversationHub() {
  // State management
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [showCitations, setShowCitations] = useState(true);

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Voice input
  const { isListening, transcript, startListening, stopListening } = useSpeechRecognition();

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load conversation history on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Update input with voice transcript
  useEffect(() => {
    if (transcript) {
      setInputValue(transcript);
    }
  }, [transcript]);

  // Load all conversations from API
  const loadConversations = async () => {
    try {
      const response = await api.get('/api/v1/conversation/history');
      setConversations(response.data.conversations);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  // Load messages for a specific conversation
  const loadConversation = async (conversationUuid: string) => {
    try {
      const response = await api.get(`/api/v1/conversation/${conversationUuid}`);
      setMessages(response.data.messages);
      setCurrentConversation(response.data.conversation);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  // Send message to API
  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      uuid: crypto.randomUUID(),
      role: 'user',
      content: inputValue,
      created_at: new Date().toISOString()
    };

    // Add user message to UI immediately
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Send to API
      const response = await api.post('/api/v1/conversation/query', {
        query: inputValue,
        conversation_uuid: currentConversation?.uuid
      });

      const assistantMessage: Message = {
        uuid: response.data.message_uuid,
        role: 'assistant',
        content: response.data.response,
        citations: response.data.citations,
        created_at: response.data.created_at
      };

      // Add assistant message to UI
      setMessages(prev => [...prev, assistantMessage]);

      // Update conversation metadata
      if (response.data.conversation) {
        setCurrentConversation(response.data.conversation);
        loadConversations(); // Refresh sidebar
      }

    } catch (error) {
      console.error('Failed to send message:', error);

      // Add error message
      const errorMessage: Message = {
        uuid: crypto.randomUUID(),
        role: 'system',
        content: 'Sorry, there was an error processing your message. Please try again.',
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Start new conversation
  const startNewConversation = () => {
    setMessages([]);
    setCurrentConversation(null);
    setSelectedCitation(null);
    inputRef.current?.focus();
  };

  // Export conversation
  const exportConversation = async (format: 'pdf' | 'markdown') => {
    if (!currentConversation) return;

    try {
      const response = await api.post(`/api/v1/conversation/export`, {
        conversation_uuid: currentConversation.uuid,
        format
      }, {
        responseType: 'blob'
      });

      // Download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `conversation-${currentConversation.uuid}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to export conversation:', error);
    }
  };

  // Handle citation click
  const handleCitationClick = (citation: Citation) => {
    setSelectedCitation(citation);
    setShowCitations(true);
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + Enter to send message
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        sendMessage();
      }
      // Escape to close
      if (e.key === 'Escape') {
        // Handle close if needed
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [inputValue]);

  return (
    <div className="flex h-screen bg-black text-white">
      {/* Conversation Sidebar (Left) */}
      <AnimatePresence>
        {showSidebar && (
          <motion.div
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            className="w-80 border-r border-white/10 flex flex-col"
          >
            <ConversationSidebar
              conversations={conversations}
              currentConversation={currentConversation}
              onSelectConversation={loadConversation}
              onNewConversation={startNewConversation}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Chat Area (Center) */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="backdrop-blur-xl bg-black/80 border-b border-white/10 p-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="p-2 hover:bg-white/10 rounded-lg transition"
            >
              ☰
            </button>
            <h1 className="text-xl font-semibold">
              {currentConversation?.title || 'New Conversation'}
            </h1>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => exportConversation('markdown')}
              className="p-2 hover:bg-white/10 rounded-lg transition"
              title="Export as Markdown"
            >
              <Download size={20} />
            </button>
            <button
              onClick={() => exportConversation('pdf')}
              className="p-2 hover:bg-white/10 rounded-lg transition"
              title="Export as PDF"
            >
              <Download size={20} />
            </button>
          </div>
        </header>

        {/* Message List */}
        <div className="flex-1 overflow-y-auto p-6">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md">
                <h2 className="text-2xl font-semibold mb-4">
                  Welcome to AI Conversation
                </h2>
                <p className="text-white/60 mb-6">
                  Ask questions about your knowledge base in natural language.
                  I'll search across documents, entities, and relationships to provide
                  memory-grounded answers with citations.
                </p>
                <div className="grid grid-cols-1 gap-3 text-sm">
                  <button
                    onClick={() => setInputValue('Show me all CAT equipment')}
                    className="p-3 bg-white/5 hover:bg-white/10 rounded-lg transition text-left"
                  >
                    "Show me all CAT equipment"
                  </button>
                  <button
                    onClick={() => setInputValue('What maintenance issues are trending?')}
                    className="p-3 bg-white/5 hover:bg-white/10 rounded-lg transition text-left"
                  >
                    "What maintenance issues are trending?"
                  </button>
                  <button
                    onClick={() => setInputValue('Find documents about hydraulic systems')}
                    className="p-3 bg-white/5 hover:bg-white/10 rounded-lg transition text-left"
                  >
                    "Find documents about hydraulic systems"
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <MessageList
              messages={messages}
              onCitationClick={handleCitationClick}
            />
          )}

          {/* Typing indicator */}
          {isLoading && (
            <div className="flex items-center gap-2 text-white/60 mt-4">
              <div className="flex gap-1">
                <motion.div
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                  className="w-2 h-2 bg-white/60 rounded-full"
                />
                <motion.div
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                  className="w-2 h-2 bg-white/60 rounded-full"
                />
                <motion.div
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                  className="w-2 h-2 bg-white/60 rounded-full"
                />
              </div>
              <span>Assistant is typing...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input */}
        <div className="backdrop-blur-xl bg-black/80 border-t border-white/10 p-4">
          <div className="flex items-center gap-2 max-w-4xl mx-auto">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type your message... (⌘+Enter to send)"
              className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-3
                       focus:outline-none focus:ring-2 focus:ring-purple-500
                       placeholder-white/40"
              disabled={isLoading}
            />

            <button
              onClick={() => isListening ? stopListening() : startListening()}
              className={`p-3 rounded-lg transition ${
                isListening
                  ? 'bg-red-500 hover:bg-red-600'
                  : 'bg-white/10 hover:bg-white/20'
              }`}
              title={isListening ? 'Stop recording' : 'Voice input'}
            >
              <Mic size={20} />
            </button>

            <button
              onClick={sendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="p-3 bg-gradient-to-r from-purple-500 to-pink-500
                       hover:from-purple-600 hover:to-pink-600
                       rounded-lg transition disabled:opacity-50
                       disabled:cursor-not-allowed"
              title="Send message (⌘+Enter)"
            >
              <Send size={20} />
            </button>
          </div>

          <p className="text-xs text-white/40 text-center mt-2">
            Powered by Claude 3.5 Sonnet | Responses are grounded in your knowledge base
          </p>
        </div>
      </div>

      {/* Citation Panel (Right) */}
      <AnimatePresence>
        {showCitations && (
          <motion.div
            initial={{ x: 400 }}
            animate={{ x: 0 }}
            exit={{ x: 400 }}
            className="w-96 border-l border-white/10"
          >
            <CitationPanel
              selectedCitation={selectedCitation}
              onClose={() => setShowCitations(false)}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
