import { useState, useEffect } from 'react';
import BottomNav from './components/BottomNav';
import WalletPage from './pages/WalletPage';
import TradePage from './pages/TradePage';
import SignalsPage from './pages/SignalsPage';
import HistoryPage from './pages/HistoryPage';
import { initTelegram, showBackButton, hideBackButton } from './utils/telegram';

function App() {
  const [currentPage, setCurrentPage] = useState('wallet');
  const [telegramApp, setTelegramApp] = useState(null);

  useEffect(() => {
    // Initialize Telegram Mini App SDK
    const app = initTelegram();
    setTelegramApp(app);
    
    // Set ready
    if (app && app.miniApp && app.miniApp.ready) {
      app.miniApp.ready();
    }
    
    // Set header color
    if (app && app.miniApp && app.miniApp.setHeaderColor) {
      app.miniApp.setHeaderColor('#ffffff');
    }
  }, []);

  useEffect(() => {
    // Hide back button on wallet page, show on others
    if (currentPage === 'wallet') {
      hideBackButton();
    } else {
      showBackButton(() => setCurrentPage('wallet'));
    }
  }, [currentPage]);

  const renderPage = () => {
    switch (currentPage) {
      case 'wallet':
        return <WalletPage onNavigate={setCurrentPage} />;
      case 'trade':
        return <TradePage />;
      case 'signals':
        return <SignalsPage />;
      case 'history':
        return <HistoryPage />;
      default:
        return <WalletPage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="min-h-screen bg-telegram-bg">
      {renderPage()}
      <BottomNav active={currentPage} onNavigate={setCurrentPage} />
    </div>
  );
}

export default App;
