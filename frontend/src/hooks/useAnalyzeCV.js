import { useState } from 'react';
import { notifications } from '@mantine/notifications';
import { analyzeCV } from '../services/apiService'; 

export const useAnalyzeCV = () => {
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const analyze = async (cvText) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await analyzeCV(cvText);
      setResults(data);

    } catch (err) {
      const errorMessage = err.message || "אירעה שגיאה בלתי צפויה";
      setError(errorMessage);
      notifications.show({
        title: 'שגיאה בניתוח',
        message: errorMessage,
        color: 'red',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return { results, isLoading, error, analyze };
};