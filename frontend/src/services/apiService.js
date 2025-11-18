const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

export const analyzeCV = async (cvText) => {
  const response = await fetch(`${API_BASE_URL}/api/analyze-cv`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cv_text: cvText }),
  });

  if (!response.ok) {
    let errorMsg = `שגיאת שרת: ${response.status}`;
    try {
      const errorData = await response.json();
      errorMsg = errorData.detail || errorData.error || errorMsg;
    } catch (jsonError) {
      console.error("Could not parse error JSON from server", jsonError);
    }
    throw new Error(errorMsg);
  }

  const data = await response.json();
  
  if (data.detail || data.error) {
     throw new Error(data.detail || data.error);
  }

  return data; 
};

export const getMarketTrends = async () => {
  const response = await fetch(`${API_BASE_URL}/api/market-trends`);

  if (!response.ok) {
    let errorMsg = `server error: ${response.status}`;
    try {
      const errorData = await response.json();
      errorMsg = errorData.detail || errorData.error || errorMsg;
    } catch (e) {
    }
    throw new Error(errorMsg);
  }

  const data = await response.json();
  if (data.detail || data.error) {
     throw new Error(data.detail || data.error);
  }
  return data;  
};