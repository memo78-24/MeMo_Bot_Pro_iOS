import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, RefreshCw, Target, AlertCircle } from 'lucide-react';
import { getScalpingSignals } from '../utils/api';
import { hapticFeedback } from '../utils/telegram';

const SignalCard = ({ signal }) => {
  const { symbol, action, entry_price, exit_target, stop_loss, take_profit_percent, profit_estimate_usdt, confidence } = signal;
  
  const getSignalColor = () => {
    if (action === 'BUY') return 'bg-green-500';
    if (action === 'SELL') return 'bg-red-500';
    return 'bg-gx-text-muted';
  };

  const getSignalIcon = () => {
    if (action === 'BUY') return <TrendingUp size={20} />;
    if (action === 'SELL') return <TrendingDown size={20} />;
    return <Minus size={20} />;
  };

  return (
    <div className="bg-gx-card rounded-2xl p-5 border border-white/10 shadow-[0_0_20px_rgba(255,0,80,0.1)] mb-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="text-2xl">
            {symbol === 'BTC' ? '₿' : 
             symbol === 'ETH' ? 'Ξ' : 
             symbol === 'BNB' ? '🔶' : '●'}
          </div>
          <div>
            <h3 className="text-lg font-bold text-gx-text">{symbol}</h3>
            <p className="text-sm text-gx-text-muted">Scalping Signal</p>
          </div>
        </div>
        <div className={`${getSignalColor()} text-white px-4 py-2 rounded-full flex items-center gap-2 font-bold shadow-lg`}>
          {getSignalIcon()}
          {action}
        </div>
      </div>

      {/* Prices */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-gx-card-light rounded-xl p-3 border border-white/5">
          <div className="text-xs text-gx-text-muted mb-1">Entry Price</div>
          <div className="text-lg font-bold text-gx-text">${entry_price?.toFixed(2)}</div>
        </div>
        <div className="bg-gx-card-light rounded-xl p-3 border border-white/5">
          <div className="text-xs text-gx-text-muted mb-1">Exit Price</div>
          <div className="text-lg font-bold text-gx-text">${exit_target?.toFixed(2)}</div>
        </div>
      </div>

      {/* Risk Management */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="flex items-start gap-2">
          <AlertCircle size={16} className="text-red-400 mt-1" />
          <div>
            <div className="text-xs text-gx-text-muted">Stop Loss</div>
            <div className="text-sm font-semibold text-red-400">${stop_loss?.toFixed(2)}</div>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <Target size={16} className="text-green-400 mt-1" />
          <div>
            <div className="text-xs text-gx-text-muted">Take Profit</div>
            <div className="text-sm font-semibold text-green-400">{take_profit_percent?.toFixed(2)}%</div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="border-t border-white/10 pt-3 flex items-center justify-between text-sm">
        <div>
          <span className="text-gx-text-muted">Profit Potential: </span>
          <span className="font-semibold text-green-400">${profit_estimate_usdt?.toFixed(2)}</span>
        </div>
      </div>
      
      {/* Confidence */}
      <div className="mt-3">
        <div className="flex items-center justify-between text-xs text-gx-text-muted mb-1">
          <span>Confidence</span>
          <span>{confidence}%</span>
        </div>
        <div className="w-full bg-gx-card-light rounded-full h-2">
          <div 
            className="bg-gx-pink rounded-full h-2 transition-all shadow-[0_0_10px_rgba(255,0,80,0.5)]" 
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>
    </div>
  );
};

const SignalsPage = () => {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSignals = async () => {
    try {
      setLoading(true);
      const data = await getScalpingSignals();
      if (data && data.signals) {
        setSignals(data.signals);
      }
      setError(null);
      hapticFeedback('impact', 'light');
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch signals:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSignals();
    const interval = setInterval(fetchSignals, 120000); // Refresh every 2 minutes
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-gx-dark pb-20">
      {/* Header */}
      <div className="bg-gx-card px-4 pt-6 pb-4 safe-area-top">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-2xl font-bold text-gx-text">TRADING SIGNALS</h1>
          <button 
            onClick={fetchSignals}
            className="p-2 hover:bg-gx-card-light rounded-full transition-colors"
          >
            <RefreshCw size={20} className={`text-gx-text-muted ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
        <p className="text-sm text-gx-text-muted">Scalping opportunities for $50 trades</p>
      </div>

      {/* Info Banner */}
      <div className="mx-4 mt-4 bg-gradient-to-r from-gx-pink/10 to-gx-pink/20 border border-gx-pink/30 rounded-2xl p-4">
        <div className="flex items-start gap-3">
          <Target className="text-gx-pink flex-shrink-0 mt-0.5" size={20} />
          <div>
            <h3 className="font-semibold text-gx-text mb-1">Scalping Strategy</h3>
            <p className="text-sm text-gx-text-muted">
              Target: $100 daily profit with $50 trades. 0.5% stop-loss, 1.5% take-profit.
            </p>
          </div>
        </div>
      </div>

      {/* Signals List */}
      <div className="px-4 mt-6 pb-4">
        {loading && signals.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="animate-spin text-gx-pink" size={32} />
          </div>
        ) : error ? (
          <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-6 text-center">
            <AlertCircle className="text-red-400 mx-auto mb-3" size={48} />
            <h3 className="font-semibold text-gx-text mb-2">Failed to Load Signals</h3>
            <p className="text-sm text-gx-text-muted mb-4">{error}</p>
            <button 
              onClick={fetchSignals}
              className="px-6 py-2 bg-gx-pink text-white rounded-xl font-semibold shadow-[0_0_20px_rgba(255,0,80,0.3)]"
            >
              Retry
            </button>
          </div>
        ) : signals.length === 0 ? (
          <div className="bg-gx-card border border-white/10 rounded-2xl p-6 text-center">
            <Target className="text-gx-text-muted mx-auto mb-3" size={48} />
            <h3 className="font-semibold text-gx-text mb-2">No Signals Available</h3>
            <p className="text-sm text-gx-text-muted">Check back soon for new trading opportunities</p>
          </div>
        ) : (
          <>
            {signals.map((signal, index) => (
              <SignalCard key={`${signal.symbol}-${index}`} signal={signal} />
            ))}
          </>
        )}
      </div>
    </div>
  );
};

export default SignalsPage;
