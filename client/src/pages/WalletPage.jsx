import { useState, useEffect } from 'react';
import { ArrowUpRight, ArrowDownLeft, RefreshCw, DollarSign } from 'lucide-react';
import ActionButton from '../components/ActionButton';
import CryptoAssetRow from '../components/CryptoAssetRow';
import { useMarketData } from '../hooks/useMarketData';
import { getBalance } from '../utils/api';
import { getTelegramUser } from '../utils/telegram';

const WalletPage = ({ onNavigate }) => {
  const { data: marketData, loading: marketLoading } = useMarketData();
  const [balance, setBalance] = useState(null);
  const [totalUSDT, setTotalUSDT] = useState(0);
  const [totalAED, setTotalAED] = useState(0);
  const [loading, setLoading] = useState(true);

  const user = getTelegramUser();

  useEffect(() => {
    const fetchBalance = async () => {
      try {
        const data = await getBalance(user?.id || 123456789);
        if (data && data.balances) {
          setBalance(data.balances);
          setTotalUSDT(data.total_usdt || 0);
          setTotalAED(data.total_aed || 0);
        }
      } catch (error) {
        console.error('Failed to fetch balance:', error);
        // Set mock data for development
        setTotalUSDT(0);
        setTotalAED(0);
        setBalance({});
      } finally {
        setLoading(false);
      }
    };

    fetchBalance();
  }, [user]);

  const cryptoHoldings = marketData?.prices || [];

  return (
    <div className="flex flex-col min-h-screen bg-telegram-bg pb-20">
      {/* Header */}
      <div className="bg-white px-4 pt-6 pb-4 safe-area-top">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-2xl font-bold text-gray-900">Wallet</h1>
          <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
            <RefreshCw size={20} className="text-gray-600" />
          </button>
        </div>
        <p className="text-sm text-gray-500">MeMo Bot Pro</p>
      </div>

      {/* Balance Card */}
      <div className="bg-gradient-to-br from-telegram-blue to-blue-600 mx-4 mt-4 rounded-3xl p-6 text-white shadow-lg">
        <div className="text-sm opacity-90 mb-2">Total Balance</div>
        <div className="text-4xl font-bold mb-1">
          {loading ? '...' : `$${totalUSDT.toFixed(2)}`}
        </div>
        <div className="text-sm opacity-80">
          {loading ? '...' : `${totalAED.toFixed(2)} AED`}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="px-4 mt-6">
        <div className="grid grid-cols-4 gap-3">
          <ActionButton 
            icon={ArrowUpRight} 
            label="Transfer"
            onClick={() => alert('Transfer feature coming soon')}
          />
          <ActionButton 
            icon={DollarSign} 
            label="Deposit"
            onClick={() => alert('Deposit feature coming soon')}
          />
          <ActionButton 
            icon={ArrowDownLeft} 
            label="Withdraw"
            onClick={() => alert('Withdraw feature coming soon')}
          />
          <ActionButton 
            icon={RefreshCw} 
            label="Exchange"
            onClick={() => onNavigate('trade')}
          />
        </div>
      </div>

      {/* Assets List */}
      <div className="mt-6 bg-white rounded-t-3xl flex-1">
        <div className="px-4 py-4 border-b border-gray-100">
          <h2 className="text-lg font-bold text-gray-900">Assets</h2>
        </div>
        
        {marketLoading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="animate-spin text-telegram-blue" size={32} />
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {cryptoHoldings.map((crypto) => {
              const symbol = crypto.symbol?.replace('USDT', '') || 'BTC';
              const userBalance = balance?.[symbol] || 0;
              const balanceUSD = userBalance * (crypto.price || 0);
              
              return (
                <CryptoAssetRow
                  key={crypto.symbol}
                  symbol={symbol}
                  name={crypto.name || symbol}
                  price={crypto.price || 0}
                  change24h={crypto.change_24h || 0}
                  balance={userBalance}
                  balanceUSD={balanceUSD}
                />
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default WalletPage;
