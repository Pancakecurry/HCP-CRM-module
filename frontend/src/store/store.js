import { configureStore } from '@reduxjs/toolkit';
import interactionFormReducer from './interactionFormSlice';

export const store = configureStore({
  reducer: {
    interactionForm: interactionFormReducer,
  },
});
