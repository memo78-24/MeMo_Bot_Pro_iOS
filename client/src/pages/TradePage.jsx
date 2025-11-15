import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';
import { useMarketData } from '../hooks/useMarketData';
import { executeTrade } from '../utils/api';
import { getTelegramUser, hapticFeedback } from '../utils/telegram';

const TradePage = () => {
  const { data: marketData, loading } = useMarketData();
  const [selectedCrypto, setSelectedCrypto] = useState(null);
  const [tradeType, setTradeType] = useState('buy');
  const [amount, setAmount] = useState('');
  const [showConfirm, setShowConfirm] = useState(false);
  const user = getTelegramUser();

  const cryptoList = marketData?.prices || [];

  useEffect(() => {
    if (cryptoList.length > 0 && !selectedCrypto) {
      setSelectedCrypto(cryptoList[0]);
    }
  }, [cryptoList]);

  const handleTrade = async () => {
    if (!amount || parseFloat(amount) <= 0) {
      alert('Please enter a valid amount');
      return;
    }

    hapticFeedback('impact', 'medium');
    setShowConfirm(true);
  };

  const confirmTrade = async () => {
    try {
      hapticFeedback('notification', 'success');
      const symbol = selectedCrypto.symbol.replace('USDT', '');
      
      await executeTrade(user?.id || 123456789, {
        symbol,
        type: tradeType,
        amount: parseFloat(amount),
        price: selectedCrypto.price,
      });

      alert(`✅ ${tradeType.toUpperCase()} order executed successfully!`);
      setShowConfirm(false);
      setAmount('');
    } catch (error) {
      hapticFeedback('notification', 'error');
      alert(`❌ Trade failed: ${error.message}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gx-dark">
        <RefreshCw className="animate-spin text-gx-pink" size={32} />
      </div>
    );
  }

  const symbol = selectedCrypto?.symbol?.replace('USDT', '') || 'BTC';
  const price = selectedCrypto?.price || 0;
  const change24h = selectedCrypto?.change_24h || 0;
  const isPositive = change24h >= 0;

  return (
    <div className="flex flex-col min-h-screen bg-gx-dark pb-20">
      {/* Header */}
      <div className="bg-gx-card px-4 pt-6 pb-4 safe-area-top">
        <h1 className="text-2xl font-bold text-gx-text">TRADE</h1>
        <p className="text-sm text-gx-text-muted">Buy and sell crypto instantly</p>
      </div>

      {/* Price Card */}
      <div className="bg-gx-card mx-4 mt-4 rounded-3xl p-6 border border-white/10">
        <div className="flex items-center justify-between mb-4">
          <select
            value={selectedCrypto?.symbol || ''}
            onChange={(e) => {
              const crypto = cryptoList.find(c => c.symbol === e.target.value);
              setSelectedCrypto(crypto);
              hapticFeedback('impact', 'light');
            }}
            className="text-2xl font-bold text-gx-text bg-transparent border-0 focus:outline-none"
          >
            {cryptoList.map((crypto) => (
              <option key={crypto.symbol} value={crypto.symbol} className="bg-gx-card">
                {crypto.symbol.replace('USDT', '')}
              </option>
            ))}
          </select>
          <div className={`text-lg font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
            {isPositive ? '↑' : '↓'} {Math.abs(change24h).toFixed(2)}%
          </div>
        </div>
        
        <div className="text-3xl font-bold text-gx-text mb-2">
          ${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </div>
        <div className="text-sm text-gx-text-muted">Current Market Price</div>
      </div>

      {/* Trade Type Selector */}
      <div className="px-4 mt-6">
        <div className="bg-gx-card rounded-2xl p-1 flex gap-1 border border-white/10">
          <button
            onClick={() => {
              setTradeType('buy');
              hapticFeedback('impact', 'light');
            }}
            className={`flex-1 py-3 rounded-xl font-semibold transition-all ${
              tradeType === 'buy'
                ? 'bg-green-500 text-white shadow-[0_0_20px_rgba(34,197,94,0.3)]'
                : 'text-gx-text-muted'
            }`}
          >
            <TrendingUp className="inline mr-2" size={20} />
            Buy
          </button>
          <button
            onClick={() => {
              setTradeType('sell');
              hapticFeedback('impact', 'light');
            }}
            className={`flex-1 py-3 rounded-xl font-semibold transition-all ${
              tradeType === 'sell'
                ? 'bg-red-500 text-white shadow-[0_0_20px_rgba(239,68,68,0.3)]'
                : 'text-gx-text-muted'
            }`}
          >
            <TrendingDown className="inline mr-2" size={20} />
            Sell
          </button>
        </div>
      </div>

      {/* Amount Input */}
      <div className="px-4 mt-6">
        <div className="bg-gx-card rounded-2xl p-6 border border-white/10">
          <label className="text-sm text-gx-text-muted mb-2 block">Amount (USDT)</label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00"
            className="w-full text-3xl font-bold text-gx-text bg-transparent border-0 focus:outline-none"
          />
          <div className="text-sm text-gx-text-muted mt-2">
            ≈ {amount && price ? (parseFloat(amount) / price).toFixed(8) : '0.00000000'} {symbol}
          </div>
          
          {/* Quick amounts */}
          <div className="flex gap-2 mt-4">
            {[10, 25, 50, 100].map((value) => (
              <button
                key={value}
                onClick={() => {
                  setAmount(value.toString());
                  hapticFeedback('impact', 'light');
                }}
                className="flex-1 py-2 px-3 rounded-lg bg-gx-card-light text-gx-text border border-white/10 font-medium text-sm hover:border-gx-pink/30 transition-all"
              >
                ${value}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Trade Button */}
      <div className="px-4 mt-6">
        <button
          onClick={handleTrade}
          disabled={!amount || parseFloat(amount) <= 0}
          className={`w-full py-4 rounded-2xl font-bold text-white text-lg shadow-lg transition-all ${
            tradeType === 'buy'
              ? 'bg-green-500 hover:bg-green-600 active:scale-95 shadow-[0_0_30px_rgba(34,197,94,0.25)]'
              : 'bg-red-500 hover:bg-red-600 active:scale-95 shadow-[0_0_30px_rgba(239,68,68,0.25)]'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {tradeType === 'buy' ? 'Buy' : 'Sell'} {symbol}
        </button>
      </div>

      {/* Confirmation Modal */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-gx-card border border-white/10 rounded-3xl p-6 w-full max-w-sm">
            <h3 className="text-xl font-bold mb-4 text-gx-text">CONFIRM TRADE</h3>
            <div className="space-y-3 mb-6">
              <div className="flex justify-between">
                <span className="text-gx-text-muted">Type</span>
                <span className={`font-semibold ${tradeType === 'buy' ? 'text-green-400' : 'text-red-400'}`}>
                  {tradeType.toUpperCase()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gx-text-muted">Asset</span>
                <span className="font-semibold text-gx-text">{symbol}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gx-text-muted">Amount</span>
                <span className="font-semibold text-gx-text">${amount}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gx-text-muted">Price</span>
                <span className="font-semibold text-gx-text">${price.toFixed(2)}</span>
              </div>
              <div className="flex justify-between pt-3 border-t border-white/10">
                <span className="text-gx-text font-semibold">You Get</span>
                <span className="font-bold text-gx-pink">{(parseFloat(amount) / price).toFixed(8)} {symbol}</span>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowConfirm(false);
                  hapticFeedback('impact', 'light');
                }}
                className="flex-1 py-3 rounded-xl bg-gx-card-light text-gx-text font-semibold border border-white/10"
              >
                Cancel
              </button>
              <button
                onClick={confirmTrade}
                className={`flex-1 py-3 rounded-xl text-white font-semibold ${
                  tradeType === 'buy' ? 'bg-green-500' : 'bg-red-500'
                }`}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TradePage;
