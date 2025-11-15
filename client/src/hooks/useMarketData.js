import { useState, useEffect } from 'react';
import { getMarketData } from '../utils/api';

export const useMarketData = (refreshInterval = 30000) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const result = await getMarketData();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch market data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  return { data, loading, error, refetch: fetchData };
};
