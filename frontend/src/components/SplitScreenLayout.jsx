import React from 'react';
import InteractionForm from './InteractionForm';
import ChatInterface from './ChatInterface';

export default function SplitScreenLayout() {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-100">
      <div className="w-1/2 h-full shadow-lg z-10">
        <InteractionForm />
      </div>
      <div className="w-1/2 h-full">
        <ChatInterface />
      </div>
    </div>
  );
}
