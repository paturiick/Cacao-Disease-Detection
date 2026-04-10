// sections/api/mappingApi.js
const BASE = import.meta.env.VITE_API_BASE_URL || '';

export const mappingApi = {
  /**
   * Connects to the Server-Sent Events (SSE) stream for live pod captures and telemetry.
   * @param {string} sessionId - The UUID of the current flight session
   * @returns {EventSource|null} The EventSource connection
   */
  connectCaptureStream: (sessionId) => {
    if (!sessionId) {
      console.warn("[mappingApi] No session ID provided for capture stream");
      return null;
    }
    
    const url = `${BASE}/api/mapping/capture-pods/?session_id=${sessionId}`;
    return new EventSource(url);
  }
};