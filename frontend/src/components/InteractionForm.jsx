import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Loader2, Mic, Search, Plus } from 'lucide-react';
import { addChatMessage } from '../store/interactionFormSlice';

export default function InteractionForm() {
  const formState = useSelector((state) => state.interactionForm);
  const isProcessing = formState.isProcessing;
  const dispatch = useDispatch();

  const handleInterceptClick = (e) => {
    e.preventDefault();
    dispatch(addChatMessage({ 
      role: 'system', 
      content: '⚠️ Please use the AI Assistant to add materials or perform this action.' 
    }));
  };

  const handleSampleInterceptClick = (e) => {
    e.preventDefault();
    dispatch(addChatMessage({
      role: 'system',
      content: '⚠️ Manual entry disabled. Please ask the AI Assistant to add samples.'
    }));
  };

  return (
    <div className={`flex flex-col h-full bg-slate-50 border-r border-slate-200 transition-opacity duration-300 ${isProcessing ? 'opacity-70' : 'opacity-100'}`}>
      <div className="p-6 border-b border-slate-200 bg-white flex justify-between items-center shadow-sm z-10">
        <div>
          <h2 className="text-2xl font-semibold text-slate-800 flex items-center gap-2">
            Log HCP Interaction
            {isProcessing && <Loader2 className="animate-spin text-blue-500" size={24} />}
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            This form is controlled by the AI Assistant. You cannot edit it manually.
          </p>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        {/* Voice Note Section */}
        <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 flex items-center gap-3">
          <div className="bg-blue-500 text-white p-2 rounded-full">
            <Mic size={20} />
          </div>
          <div>
            <h3 className="text-sm font-medium text-blue-900">Summarize from Voice Note</h3>
            <p className="text-xs text-blue-700 mt-0.5">Requires HCP Consent prior to recording.</p>
          </div>
        </div>

        {/* Basic Info Section */}
        <div className="space-y-4 bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <h3 className="text-lg font-medium text-slate-800 border-b pb-2">Interaction Details</h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-1">HCP Name</label>
              <input 
                type="text" 
                readOnly 
                className="w-full p-2.5 rounded-md border border-slate-300 bg-slate-100 text-slate-600 cursor-not-allowed focus:outline-none"
                value={formState.hcpName || ''}
                placeholder="Extracting from chat..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Date</label>
              <input 
                type="date" 
                readOnly 
                className="w-full p-2.5 rounded-md border border-slate-300 bg-slate-100 text-slate-600 cursor-not-allowed focus:outline-none"
                value={formState.date || ''}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Time</label>
              <input 
                type="time" 
                readOnly 
                className="w-full p-2.5 rounded-md border border-slate-300 bg-slate-100 text-slate-600 cursor-not-allowed focus:outline-none"
                value={formState.time || ''}
              />
            </div>

            <div className="col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-1">Interaction Type</label>
              <select 
                disabled 
                className="w-full p-2.5 rounded-md border border-slate-300 bg-slate-100 text-slate-600 cursor-not-allowed focus:outline-none appearance-none"
                value={formState.interactionType || ''}
              >
                <option value="">Select type...</option>
                <option value="Meeting">Meeting (In-Person)</option>
                <option value="Video Call">Video Call</option>
                <option value="Email">Email</option>
                <option value="Phone">Phone</option>
              </select>
            </div>
          </div>
        </div>

        {/* Meeting Content */}
        <div className="space-y-4 bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <h3 className="text-lg font-medium text-slate-800 border-b pb-2">Meeting Content</h3>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Topics Discussed</label>
            <textarea 
              readOnly 
              rows={3}
              className="w-full p-2.5 rounded-md border border-slate-300 bg-slate-100 text-slate-600 cursor-not-allowed focus:outline-none resize-none"
              value={formState.topicsDiscussed || ''}
              placeholder="Key topics will populate here..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Overall Sentiment</label>
            <div className="flex gap-4">
              {['Positive', 'Neutral', 'Negative'].map((s) => (
                <label key={s} className="flex items-center gap-2 cursor-not-allowed opacity-80">
                  <input 
                    type="radio" 
                    disabled
                    checked={formState.sentiment === s}
                    className="w-4 h-4 text-blue-600 border-slate-300"
                  />
                  <span className="text-sm font-medium text-slate-700">
                    {s} {s === 'Positive' ? '😃' : s === 'Neutral' ? '😐' : '🙁'}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Outcomes</label>
            <textarea 
              readOnly 
              rows={2}
              className="w-full p-2.5 rounded-md border border-slate-300 bg-slate-100 text-slate-600 cursor-not-allowed focus:outline-none resize-none"
              value={formState.keyOutcomes || ''}
              placeholder="Key outcomes or agreements..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Follow-up Actions</label>
            <textarea 
              readOnly 
              rows={2}
              className="w-full p-2.5 rounded-md border border-slate-300 bg-slate-100 text-slate-600 cursor-not-allowed focus:outline-none resize-none"
              value={formState.followUpActions || ''}
              placeholder="Next steps..."
            />
          </div>
        </div>

        {/* Materials & Samples */}
        <div className="space-y-4 bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="flex justify-between items-center border-b pb-2">
            <h3 className="text-lg font-medium text-slate-800">Materials & Samples</h3>
          </div>
          
          <div>
            <div className="flex justify-between items-end mb-2">
              <label className="block text-sm font-medium text-slate-700">Materials Shared</label>
              <button 
                onClick={handleInterceptClick}
                className="text-xs font-medium text-blue-600 flex items-center gap-1 hover:text-blue-800"
              >
                <Search size={14} /> Search/Add
              </button>
            </div>
            <textarea 
              readOnly 
              rows={2}
              className="w-full p-2.5 rounded-md border border-slate-300 bg-slate-100 text-slate-600 cursor-not-allowed focus:outline-none resize-none"
              value={formState.materialsShared || ''}
              placeholder="No materials shared..."
            />
          </div>

          <div>
            <div className="flex justify-between items-end mb-2">
              <label className="block text-sm font-medium text-slate-700">Samples Distributed</label>
              <button 
                onClick={handleSampleInterceptClick}
                className="text-xs font-medium text-blue-600 flex items-center gap-1 hover:text-blue-800"
              >
                <Plus size={14} /> Add Sample
              </button>
            </div>
            <textarea 
              readOnly 
              rows={2}
              className="w-full p-2.5 rounded-md border border-slate-300 bg-slate-100 text-slate-600 cursor-not-allowed focus:outline-none resize-none"
              value={formState.samplesDistributed || ''}
              placeholder="No samples distributed"
            />
          </div>
        </div>

      </div>
    </div>
  );
}
