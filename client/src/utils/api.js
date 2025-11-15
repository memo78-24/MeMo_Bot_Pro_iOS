const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const apiRequest = async (endpoint, options = {}) => {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API error for ${endpoint}:`, error);
    throw error;
  }
};

// Market data
export const getMarketData = () => apiRequest('/api/market-data');

// Signals
export const getSignals = () => apiRequest('/api/signals');
export const getScalpingSignals = () => apiRequest('/api/scalping-signals');

// Balance
export const getBalance = (userId) => apiRequest(`/api/balance?user_id=${userId}`);

// Trading
export const executeTrade = (userId, tradeData) => 
  apiRequest('/api/trade', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, ...tradeData }),
  });

// Trade history
export const getTradeHistory = (userId) => apiRequest(`/api/trade-history?user_id=${userId}`);

// Profit tracking
export const getProfitData = (userId) => apiRequest(`/api/profit?user_id=${userId}`);
