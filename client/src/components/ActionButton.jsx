import React from 'react';

const ActionButton = ({ icon: Icon, label, onClick, disabled = false }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`flex flex-col items-center justify-center bg-white rounded-2xl p-4 shadow-sm hover:shadow-md transition-shadow ${
        disabled ? 'opacity-50 cursor-not-allowed' : 'active:scale-95'
      }`}
    >
      <div className="w-12 h-12 rounded-full bg-telegram-blue flex items-center justify-center mb-2">
        <Icon size={24} className="text-white" strokeWidth={2.5} />
      </div>
      <span className="text-sm font-medium text-gray-800">{label}</span>
    </button>
  );
};

export default ActionButton;
