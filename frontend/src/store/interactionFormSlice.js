import { createSlice } from '@reduxjs/toolkit';

// Use a simple fallback for environments without crypto.randomUUID
const generateUUID = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return 'thread_' + Math.random().toString(36).substring(2, 15);
};

const initialState = {
  threadId: generateUUID(),
  isProcessing: false,
  hcpName: '',
  interactionType: '',
  date: '',
  time: '',
  attendees: '',
  topicsDiscussed: '',
  materialsShared: '',
  sentiment: '',
  keyOutcomes: '',
  followUpActions: '',
  samplesDistributed: '',
  chatHistory: [
    { role: 'assistant', content: 'Hello! I am your AI assistant. How can I help you log this HCP interaction?' }
  ]
};

const interactionFormSlice = createSlice({
  name: 'interactionForm',
  initialState,
  reducers: {
    setIsProcessing: (state, action) => {
      state.isProcessing = action.payload;
    },
    updateFormFields: (state, action) => {
      // Shallow merge the incoming UI state patch
      const updates = action.payload;
      for (const [key, value] of Object.entries(updates)) {
        if (key in state) {
          state[key] = value;
        }
      }
    },
    appendChatChunk: (state, action) => {
      // Find the last assistant message
      const lastMsg = state.chatHistory[state.chatHistory.length - 1];
      if (lastMsg && lastMsg.role === 'assistant') {
        lastMsg.content += action.payload;
      } else {
        // If the last message isn't assistant, push a new one
        state.chatHistory.push({ role: 'assistant', content: action.payload });
      }
    },
    addChatMessage: (state, action) => {
      state.chatHistory.push(action.payload);
    },
    resetForm: () => initialState,
  }
});

export const { setIsProcessing, updateFormFields, appendChatChunk, addChatMessage, resetForm } = interactionFormSlice.actions;

export default interactionFormSlice.reducer;
