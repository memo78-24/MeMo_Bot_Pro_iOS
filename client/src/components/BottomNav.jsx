import { Wallet, TrendingUp, Percent, History } from 'lucide-react';

const BottomNav = ({ active, onNavigate }) => {
  const tabs = [
    { id: 'wallet', icon: Wallet, label: 'Wallet' },
    { id: 'trade', icon: TrendingUp, label: 'Trade' },
    { id: 'signals', icon: Percent, label: 'Signals' },
    { id: 'history', icon: History, label: 'History' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 safe-area-bottom">
      <div className="flex items-center justify-around px-4 py-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = active === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => onNavigate(tab.id)}
              className={`flex flex-col items-center justify-center py-2 px-4 min-w-[60px] transition-colors ${
                isActive ? 'text-telegram-blue' : 'text-gray-500'
              }`}
            >
              <Icon size={24} strokeWidth={isActive ? 2.5 : 2} />
              <span className="text-xs mt-1 font-medium">{tab.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default BottomNav;
