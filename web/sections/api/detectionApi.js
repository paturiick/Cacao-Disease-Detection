// sections/api/detectionApi.js
const BASE = import.meta.env.VITE_API_BASE_URL;

/**
 * Standard fetch wrapper for JSON requests.
 */
async function jfetch(url, opts = {}) {
  const res = await fetch(BASE + url, {
    headers: { 'Content-Type': 'application/json' },
    ...opts
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json();
}

export const detectionApi = {
  /**
   * Fetches the latest detection stats and pod list for a specific flight session.
   * @param {string} sessionId - The UUID of the current flight session
   * @returns {Promise<Object|null>}
   */
  getSessionStats: (sessionId) => {
    if (!sessionId) {
      console.warn("[detectionApi] No session ID provided");
      return Promise.resolve(null);
    }
    
    // GET is the default method for fetch, but we can pass options if needed
    return jfetch(`/api/detections/stats/?session_id=${sessionId}`, {
      method: 'GET'
    });
  }
};