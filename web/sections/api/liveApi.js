// sections/api/liveApi.js
const BASE = import.meta.env.VITE_API_BASE_URL;

/**
 * Standard fetch wrapper for JSON POST requests.
 */
async function jfetch(url, opts) {
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

export const liveApi = {
  /**
   * Sends the hardware command to start or stop the UDP stream.
   * @param {string} action - 'streamon' or 'streamoff'
   */
  toggleHardware: (action) => jfetch('/api/live/toggle/', { 
    method: 'POST', 
    body: JSON.stringify({ command: action }) 
  }),

  /**
   * Returns the static endpoint for the MJPEG feed.
   */
  getStreamUrl: () => `${BASE}/api/live/feed/`
};