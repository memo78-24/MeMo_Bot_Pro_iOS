import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, RefreshCw, Target, AlertCircle } from 'lucide-react';
import { getScalpingSignals } from '../utils/api';
import { hapticFeedback } from '../utils/telegram';

const SignalCard = ({ signal }) => {
  const { symbol, signal_type, entry_price, exit_price, stop_loss, take_profit, profit_potential, risk_reward, confidence } = signal;
  
  const getSignalColor = () => {
    if (signal_type === 'BUY') return 'bg-green-500';
    if (signal_type === 'SELL') return 'bg-red-500';
    return 'bg-gray-500';
  };

  const getSignalIcon = () => {
    if (signal_type === 'BUY') return <TrendingUp size={20} />;
    if (signal_type === 'SELL') return <TrendingDown size={20} />;
    return <Minus size={20} />;
  };

  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm mb-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="text-2xl">
            {signal.symbol === 'BTC' ? '₿' : 
             signal.symbol === 'ETH' ? 'Ξ' : 
             signal.symbol === 'BNB' ? '🔶' : '●'}
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">{symbol}</h3>
            <p className="text-sm text-gray-500">Scalping Signal</p>
          </div>
        </div>
        <div className={`${getSignalColor()} text-white px-4 py-2 rounded-full flex items-center gap-2 font-bold`}>
          {getSignalIcon()}
          {signal_type}
        </div>
      </div>

      {/* Prices */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-gray-50 rounded-xl p-3">
          <div className="text-xs text-gray-500 mb-1">Entry Price</div>
          <div className="text-lg font-bold text-gray-900">${entry_price?.toFixed(2)}</div>
        </div>
        <div className="bg-gray-50 rounded-xl p-3">
          <div className="text-xs text-gray-500 mb-1">Exit Price</div>
          <div className="text-lg font-bold text-gray-900">${exit_price?.toFixed(2)}</div>
        </div>
      </div>

      {/* Risk Management */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="flex items-start gap-2">
          <AlertCircle size={16} className="text-red-500 mt-1" />
          <div>
            <div className="text-xs text-gray-500">Stop Loss</div>
            <div className="text-sm font-semibold text-red-600">${stop_loss?.toFixed(2)}</div>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <Target size={16} className="text-green-500 mt-1" />
          <div>
            <div className="text-xs text-gray-500">Take Profit</div>
            <div className="text-sm font-semibold text-green-600">${take_profit?.toFixed(2)}</div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="border-t border-gray-100 pt-3 flex items-center justify-between text-sm">
        <div>
          <span className="text-gray-500">Profit Potential: </span>
          <span className="font-semibold text-green-600">${profit_potential?.toFixed(2)}</span>
        </div>
        <div>
          <span className="text-gray-500">R/R: </span>
          <span className="font-semibold text-telegram-blue">{risk_reward?.toFixed(1)}x</span>
        </div>
      </div>
      
      {/* Confidence */}
      <div className="mt-3">
        <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
          <span>Confidence</span>
          <span>{confidence}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-telegram-blue rounded-full h-2 transition-all" 
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
    <div className="flex flex-col min-h-screen bg-telegram-bg pb-20">
      {/* Header */}
      <div className="bg-white px-4 pt-6 pb-4 safe-area-top">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-2xl font-bold text-gray-900">Trading Signals</h1>
          <button 
            onClick={fetchSignals}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <RefreshCw size={20} className={`text-gray-600 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
        <p className="text-sm text-gray-500">Scalping opportunities for $50 trades</p>
      </div>

      {/* Info Banner */}
      <div className="mx-4 mt-4 bg-gradient-to-r from-blue-50 to-telegram-blue/10 border border-telegram-blue/20 rounded-2xl p-4">
        <div className="flex items-start gap-3">
          <Target className="text-telegram-blue flex-shrink-0 mt-0.5" size={20} />
          <div>
            <h3 className="font-semibold text-gray-900 mb-1">Scalping Strategy</h3>
            <p className="text-sm text-gray-600">
              Target: $100 daily profit with $50 trades. 0.5% stop-loss, 1.5% take-profit.
            </p>
          </div>
        </div>
      </div>

      {/* Signals List */}
      <div className="px-4 mt-6 pb-4">
        {loading && signals.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="animate-spin text-telegram-blue" size={32} />
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
            <AlertCircle className="text-red-500 mx-auto mb-3" size={48} />
            <h3 className="font-semibold text-gray-900 mb-2">Failed to Load Signals</h3>
            <p className="text-sm text-gray-600 mb-4">{error}</p>
            <button 
              onClick={fetchSignals}
              className="px-6 py-2 bg-telegram-blue text-white rounded-xl font-semibold"
            >
              Retry
            </button>
          </div>
        ) : signals.length === 0 ? (
          <div className="bg-gray-50 border border-gray-200 rounded-2xl p-6 text-center">
            <Target className="text-gray-400 mx-auto mb-3" size={48} />
            <h3 className="font-semibold text-gray-900 mb-2">No Signals Available</h3>
            <p className="text-sm text-gray-600">Check back soon for new trading opportunities</p>
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
