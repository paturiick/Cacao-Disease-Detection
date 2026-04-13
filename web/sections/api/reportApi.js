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

export const reportApi = {
  getHistory: () => jfetch(`/api/reports/history/`, { method: 'GET' }),

  /**
   * Fetches the aggregated master report payload for a specific mission.
   * Endpoint: GET /api/reports/mission/{missionId}/
   * @param {number|string} missionId - The ID of the flight plan
   */
  getMissionReport: (missionId) => jfetch(`/api/reports/mission/${missionId}/`, { method: 'GET' })
};