import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, RefreshCw, Calendar } from 'lucide-react';
import { getTradeHistory } from '../utils/api';
import { getTelegramUser } from '../utils/telegram';

const TradeHistoryItem = ({ trade }) => {
  const isBuy = trade.type === 'buy';
  const profit = trade.profit || 0;
  const isProfit = profit > 0;
  
  return (
    <div className="bg-white rounded-2xl p-4 shadow-sm mb-3">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full ${isBuy ? 'bg-green-100' : 'bg-red-100'} flex items-center justify-center`}>
            {isBuy ? 
              <TrendingUp size={20} className="text-green-600" /> : 
              <TrendingDown size={20} className="text-red-600" />
            }
          </div>
          <div>
            <h3 className="font-bold text-gray-900">{trade.symbol}</h3>
            <p className="text-sm text-gray-500">
              {isBuy ? 'Buy' : 'Sell'} • {new Date(trade.timestamp).toLocaleDateString()}
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="font-bold text-gray-900">${trade.amount?.toFixed(2)}</div>
          {profit !== 0 && (
            <div className={`text-sm font-semibold ${isProfit ? 'text-green-600' : 'text-red-600'}`}>
              {isProfit ? '+' : ''}{profit.toFixed(2)} USDT
            </div>
          )}
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-3 pt-3 border-t border-gray-100">
        <div>
          <div className="text-xs text-gray-500">Price</div>
          <div className="text-sm font-semibold text-gray-900">${trade.price?.toFixed(2)}</div>
        </div>
        <div>
          <div className="text-xs text-gray-500">Amount</div>
          <div className="text-sm font-semibold text-gray-900">{trade.quantity?.toFixed(6)}</div>
        </div>
        <div>
          <div className="text-xs text-gray-500">Status</div>
          <div className={`text-sm font-semibold ${trade.status === 'completed' ? 'text-green-600' : 'text-yellow-600'}`}>
            {trade.status || 'Pending'}
          </div>
        </div>
      </div>
    </div>
  );
};

const HistoryPage = () => {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, buy, sell
  const user = getTelegramUser();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        const data = await getTradeHistory(user?.id || 123456789);
        if (data && data.trades) {
          setTrades(data.trades);
        }
      } catch (error) {
        console.error('Failed to fetch trade history:', error);
        // Mock data for development
        setTrades([]);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [user]);

  const filteredTrades = trades.filter(trade => {
    if (filter === 'all') return true;
    return trade.type === filter;
  });

  const totalProfit = trades.reduce((sum, trade) => sum + (trade.profit || 0), 0);
  const totalTrades = trades.length;
  const winningTrades = trades.filter(t => (t.profit || 0) > 0).length;
  const winRate = totalTrades > 0 ? (winningTrades / totalTrades * 100).toFixed(1) : 0;

  return (
    <div className="flex flex-col min-h-screen bg-telegram-bg pb-20">
      {/* Header */}
      <div className="bg-white px-4 pt-6 pb-4 safe-area-top">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-2xl font-bold text-gray-900">History</h1>
          <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
            <RefreshCw size={20} className="text-gray-600" />
          </button>
        </div>
        <p className="text-sm text-gray-500">Your trading history</p>
      </div>

      {/* Stats Cards */}
      <div className="px-4 mt-4">
        <div className="bg-gradient-to-br from-telegram-blue to-blue-600 rounded-3xl p-6 text-white mb-4">
          <div className="text-sm opacity-90 mb-2">Total Profit/Loss</div>
          <div className="text-3xl font-bold mb-3">
            {totalProfit >= 0 ? '+' : ''}{totalProfit.toFixed(2)} USDT
          </div>
          <div className="flex items-center justify-between text-sm opacity-90">
            <div>
              <div className="font-semibold">{totalTrades}</div>
              <div>Total Trades</div>
            </div>
            <div>
              <div className="font-semibold">{winRate}%</div>
              <div>Win Rate</div>
            </div>
            <div>
              <div className="font-semibold">{winningTrades}</div>
              <div>Winning</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="px-4 mb-4">
        <div className="bg-white rounded-2xl p-1 flex gap-1">
          {['all', 'buy', 'sell'].map((filterType) => (
            <button
              key={filterType}
              onClick={() => setFilter(filterType)}
              className={`flex-1 py-2 rounded-xl font-medium text-sm transition-all ${
                filter === filterType
                  ? 'bg-telegram-blue text-white shadow-md'
                  : 'text-gray-600'
              }`}
            >
              {filterType.charAt(0).toUpperCase() + filterType.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Trades List */}
      <div className="px-4 pb-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="animate-spin text-telegram-blue" size={32} />
          </div>
        ) : filteredTrades.length === 0 ? (
          <div className="bg-white rounded-2xl p-8 text-center">
            <Calendar className="text-gray-300 mx-auto mb-3" size={48} />
            <h3 className="font-semibold text-gray-900 mb-2">No Trades Yet</h3>
            <p className="text-sm text-gray-600">Your trade history will appear here</p>
          </div>
        ) : (
          <>
            {filteredTrades.map((trade, index) => (
              <TradeHistoryItem key={`${trade.id || index}`} trade={trade} />
            ))}
          </>
        )}
      </div>
    </div>
  );
};

export default HistoryPage;
