import { Wallet, TrendingUp, Percent, History } from 'lucide-react';

const BottomNav = ({ active, onNavigate }) => {
  const tabs = [
    { id: 'wallet', icon: Wallet, label: 'Wallet' },
    { id: 'trade', icon: TrendingUp, label: 'Trade' },
    { id: 'signals', icon: Percent, label: 'Signals' },
    { id: 'history', icon: History, label: 'History' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gx-card border-t border-white/10 safe-area-bottom">
      <div className="flex items-center justify-around px-4 py-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = active === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => onNavigate(tab.id)}
              className={`flex flex-col items-center justify-center py-2 px-4 min-w-[60px] transition-all ${
                isActive ? 'text-gx-pink-bright' : 'text-gx-text-muted'
              } relative`}
            >
              {isActive && (
                <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-8 h-0.5 bg-gx-pink rounded-full shadow-[0_0_10px_rgba(255,0,80,0.5)]" />
              )}
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
