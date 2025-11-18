import { useState, useEffect, useCallback } from 'react';
import { getMarketTrends } from '../services/apiService';

const PALETTE = ['#7C3AED', '#2563EB', '#16A34A', '#F59E0B', '#F97316', '#EF4444'];

const processChartData = (data) => {
  const rawSkills = Array.isArray(data?.skills) ? data.skills : [];
  const rawLevels = Array.isArray(data?.levels) ? data.levels : [];
  const totalJobs = data?.total_jobs || 0;

  const skills = rawSkills.map(item => ({
    name: item?.[0] || '-',
    count: Number(item?.[1]) || 0,
    percent: Number(item?.[2]) || 0,
  }));

  const levels = rawLevels.map((lvl, idx) => ({
    name: lvl.name || lvl.level_name || '-',
    count: Number(lvl.count) || 0,
    color: PALETTE[idx % PALETTE.length],
  }));

  return { skills, levels, totalJobs };
};

export const useMarketData = () => {
  const [chartData, setChartData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const rawData = await getMarketTrends();
      setChartData(processChartData(rawData));
      setError(null);
    } catch (err) {
      setError(
        err?.response?.data?.message ||
        err?.message ||
        "Unknown error"
      );
    }
  }, []);

  useEffect(() => {
    let isMounted = true;

    setIsLoading(true);
    fetchData().finally(() => {
      if (isMounted) setIsLoading(false);
    });

    return () => {
      isMounted = false;
    };
  }, [fetchData]);

  useEffect(() => {
    const intervalId = setInterval(fetchData, 3600000);
    return () => clearInterval(intervalId);
  }, [fetchData]);

  return { chartData, isLoading, error };
};
