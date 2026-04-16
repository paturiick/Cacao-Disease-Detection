// sections/api/telemetryApi.js

const BASE = import.meta.env.VITE_API_BASE_URL;

async function jfetch(url, opts) {
  const res = await fetch(BASE + url, {
    headers: { 'Content-Type': 'application/json' },
    ...opts
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const telemetryApi = {
  /**
   * SSE Stream connection
   * Receives real-time updates for:
   * - Drone Flight Data (Battery, Altitude, Orientation)
   * - Custom GPS Data (Lat, Lng, Satellites, Status)
   */
  connectStream: () => {
    return new EventSource(`${BASE}/api/telemetry/stream/`);
  },

  /**
   * Fetch the most recent single snapshot from the database.
   * Useful for initial page loads before the stream starts.
   */
  getLatest: () => jfetch('/api/telemetry/latest/', { method: 'GET' }),

  /**
   * Fetch a history of recent telemetry points.
   * Useful for plotting charts or drawing the flight path.
   */
  getRecent: (limit = 300) => jfetch(`/api/telemetry/recent/?limit=${limit}`, { method: 'GET' })
};