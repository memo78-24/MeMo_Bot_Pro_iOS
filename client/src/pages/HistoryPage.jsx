import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, RefreshCw, Calendar } from 'lucide-react';
import { getTradeHistory } from '../utils/api';
import { getTelegramUser } from '../utils/telegram';

const TradeHistoryItem = ({ trade }) => {
  const isBuy = trade.side === 'BUY' || trade.type === 'buy';
  const profit = trade.profit_loss || trade.profit || 0;
  const isProfit = profit > 0;
  
  return (
    <div className="bg-gx-card rounded-2xl p-4 border border-white/10 shadow-sm mb-3">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full ${isBuy ? 'bg-green-500/20 border border-green-500/30' : 'bg-red-500/20 border border-red-500/30'} flex items-center justify-center`}>
            {isBuy ? 
              <TrendingUp size={20} className="text-green-400" /> : 
              <TrendingDown size={20} className="text-red-400" />
            }
          </div>
          <div>
            <h3 className="font-bold text-gx-text">{trade.symbol}</h3>
            <p className="text-sm text-gx-text-muted">
              {isBuy ? 'Buy' : 'Sell'} • {trade.executed_at ? new Date(trade.executed_at).toLocaleDateString() : 'Recent'}
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="font-bold text-gx-text">${trade.usdt_value?.toFixed(2) || trade.amount?.toFixed(2)}</div>
          {profit !== 0 && (
            <div className={`text-sm font-semibold ${isProfit ? 'text-green-400' : 'text-red-400'}`}>
              {isProfit ? '+' : ''}{profit.toFixed(2)} USDT
            </div>
          )}
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-3 pt-3 border-t border-white/10">
        <div>
          <div className="text-xs text-gx-text-muted">Price</div>
          <div className="text-sm font-semibold text-gx-text">${trade.price?.toFixed(2)}</div>
        </div>
        <div>
          <div className="text-xs text-gx-text-muted">Amount</div>
          <div className="text-sm font-semibold text-gx-text">{trade.quantity?.toFixed(6)}</div>
        </div>
        <div>
          <div className="text-xs text-gx-text-muted">Status</div>
          <div className={`text-sm font-semibold ${trade.status === 'FILLED' || trade.status === 'completed' ? 'text-green-400' : 'text-yellow-400'}`}>
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
        setTrades([]);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [user]);

  const filteredTrades = trades.filter(trade => {
    if (filter === 'all') return true;
    const isBuy = trade.side === 'BUY' || trade.type === 'buy';
    return (filter === 'buy' && isBuy) || (filter === 'sell' && !isBuy);
  });

  const totalProfit = trades.reduce((sum, trade) => sum + (trade.profit_loss || trade.profit || 0), 0);
  const totalTrades = trades.length;
  const winningTrades = trades.filter(t => (t.profit_loss || t.profit || 0) > 0).length;
  const winRate = totalTrades > 0 ? (winningTrades / totalTrades * 100).toFixed(1) : 0;

  return (
    <div className="flex flex-col min-h-screen bg-gx-dark pb-20">
      {/* Header */}
      <div className="bg-gx-card px-4 pt-6 pb-4 safe-area-top">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-2xl font-bold text-gx-text">HISTORY</h1>
          <button className="p-2 hover:bg-gx-card-light rounded-full transition-colors">
            <RefreshCw size={20} className="text-gx-text-muted" />
          </button>
        </div>
        <p className="text-sm text-gx-text-muted">Your trading history</p>
      </div>

      {/* Stats Cards */}
      <div className="px-4 mt-4">
        <div className="bg-gradient-to-br from-gx-pink to-gx-pink-dark rounded-3xl p-6 text-white mb-4 shadow-[0_0_30px_rgba(255,0,80,0.25)]">
          <div className="text-sm opacity-90 mb-2">TOTAL PROFIT/LOSS</div>
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
        <div className="bg-gx-card rounded-2xl p-1 flex gap-1 border border-white/10">
          {['all', 'buy', 'sell'].map((filterType) => (
            <button
              key={filterType}
              onClick={() => setFilter(filterType)}
              className={`flex-1 py-2 rounded-xl font-medium text-sm transition-all ${
                filter === filterType
                  ? 'bg-gx-pink text-white shadow-[0_0_15px_rgba(255,0,80,0.3)]'
                  : 'text-gx-text-muted'
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
            <RefreshCw className="animate-spin text-gx-pink-bright" size={32} />
          </div>
        ) : filteredTrades.length === 0 ? (
          <div className="bg-gx-card border border-white/10 rounded-2xl p-8 text-center">
            <Calendar className="text-gx-text-muted mx-auto mb-3" size={48} />
            <h3 className="font-semibold text-gx-text mb-2">No Trades Yet</h3>
            <p className="text-sm text-gx-text-muted">Your trade history will appear here</p>
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
