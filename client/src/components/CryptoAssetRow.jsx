import React from 'react';

const CRYPTO_ICONS = {
  'BTC': '₿',
  'ETH': 'Ξ',
  'BNB': '🔶',
  'SOL': '◎',
  'XRP': '✕',
  'ADA': '₳',
  'DOGE': 'Ð',
  'DOT': '●',
  'MATIC': '⬡',
  'SHIB': '🐕',
};

const CryptoAssetRow = ({ symbol, name, price, change24h, balance, balanceUSD }) => {
  const icon = CRYPTO_ICONS[symbol] || '●';
  const isPositive = change24h >= 0;
  
  return (
    <div className="flex items-center justify-between py-3 px-4 hover:bg-gray-50 transition-colors">
      <div className="flex items-center gap-3 flex-1">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-telegram-blue to-blue-600 flex items-center justify-center text-xl">
          {icon}
        </div>
        <div className="flex-1">
          <div className="font-semibold text-gray-900">{symbol}</div>
          <div className="text-sm text-gray-500">
            ${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            {' '}
            <span className={`${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? '↑' : '↓'} {Math.abs(change24h).toFixed(2)}%
            </span>
          </div>
        </div>
      </div>
      
      {balance !== undefined && (
        <div className="text-right">
          <div className="font-semibold text-gray-900">
            ${balanceUSD?.toFixed(2) || '0.00'}
          </div>
          <div className="text-sm text-gray-500">
            {balance.toFixed(6)} {symbol}
          </div>
        </div>
      )}
    </div>
  );
};

export default CryptoAssetRow;
