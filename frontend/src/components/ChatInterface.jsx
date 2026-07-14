import React, { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { addChatMessage, appendChatChunk, updateFormFields, setIsProcessing } from '../store/interactionFormSlice';
import { Send, Loader2, Bot } from 'lucide-react';

export default function ChatInterface() {
  const [inputValue, setInputValue] = useState('');
  const chatHistory = useSelector((state) => state.interactionForm.chatHistory);
  const isProcessing = useSelector((state) => state.interactionForm.isProcessing);
  const threadId = useSelector((state) => state.interactionForm.threadId);
  const dispatch = useDispatch();
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isProcessing) return;

    const message = inputValue;
    setInputValue('');
    
    dispatch(addChatMessage({ role: 'user', content: message }));
    dispatch(setIsProcessing(true));
    dispatch(addChatMessage({ role: 'assistant', content: '' })); 

    try {
      const response = await fetch('http://localhost:8000/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_id: threadId, message }),
      });

      if (!response.body) throw new Error("ReadableStream not yet supported in this browser.");
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.slice(6);
            try {
              const data = JSON.parse(dataStr);
              if (data.type === 'text_delta') {
                dispatch(appendChatChunk(data.content));
              } else if (data.type === 'ui_state_patch') {
                dispatch(updateFormFields(data.form_data));
              } else if (data.type === 'error') {
                dispatch(appendChatChunk(`\n\n[System Error: ${data.content}]`));
              } else if (data.type === 'end') {
                // stream finished
              }
            } catch (err) {
              // ignore partial json chunks if any
            }
          }
        }
      }
    } catch (error) {
      console.error("Chat Stream Error:", error);
      dispatch(appendChatChunk("\n\n[System: Connection Error]"));
    } finally {
      dispatch(setIsProcessing(false));
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-50">
      {/* Header */}
      <div className="p-6 border-b border-slate-200 bg-white shadow-sm z-10 flex flex-col justify-center">
        <h2 className="text-xl font-bold text-blue-600 flex items-center gap-2">
          <Bot size={24} /> AI Assistant
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Log Interaction details here via chat
        </p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {chatHistory.map((msg, idx) => (
          <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`
              max-w-[85%] p-4 rounded-xl shadow-sm text-sm leading-relaxed
              ${msg.role === 'system' ? 'bg-blue-50 text-slate-800 rounded-tl-none' : ''}
              ${msg.role === 'user' ? 'bg-white text-slate-800 border border-slate-200 border-l-4 border-l-blue-500 rounded-tr-none' : ''}
              ${msg.role === 'assistant' ? 'bg-green-50 text-green-900 border border-green-200 rounded-tl-none' : ''}
            `}>
              <span className="whitespace-pre-wrap">{msg.content}</span>
            </div>
            <span className="text-[10px] text-slate-400 mt-1 mx-1 uppercase tracking-wider">
              {msg.role}
            </span>
          </div>
        ))}
        {isProcessing && (
          <div className="flex items-center gap-2 text-slate-400 text-sm italic pl-2">
            <Loader2 className="animate-spin" size={14} /> AI is thinking...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-slate-200 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
        <form onSubmit={handleSend} className="flex gap-3">
          <input
            type="text"
            className="flex-1 px-6 py-3 bg-slate-100 border border-slate-200 rounded-full text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all shadow-inner"
            placeholder="Describe Interaction..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isProcessing}
          />
          <button
            type="submit"
            disabled={isProcessing || !inputValue.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white rounded-full w-12 h-12 flex items-center justify-center transition-colors shadow-md flex-shrink-0"
          >
            {isProcessing ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} className="-ml-0.5" />}
          </button>
        </form>
      </div>
    </div>
  );
}
