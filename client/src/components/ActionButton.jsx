import React from 'react';

const ActionButton = ({ icon: Icon, label, onClick, disabled = false }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`flex flex-col items-center justify-center bg-gx-card border border-gx-pink/20 rounded-2xl p-4 hover:border-gx-pink/50 hover:shadow-[0_0_15px_rgba(255,0,80,0.2)] transition-all ${
        disabled ? 'opacity-50 cursor-not-allowed' : 'active:scale-95'
      }`}
    >
      <div className="w-12 h-12 rounded-full bg-gx-pink flex items-center justify-center mb-2 shadow-[0_0_20px_rgba(255,0,80,0.3)]">
        <Icon size={24} className="text-white" strokeWidth={2.5} />
      </div>
      <span className="text-sm font-medium text-gx-text">{label}</span>
    </button>
  );
};

export default ActionButton;
