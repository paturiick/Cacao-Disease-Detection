const BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function jfetch(url, opts) {
  const res = await fetch(BASE + url, {
    headers: { 'Content-Type': 'application/json' },
    ...opts
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  // 204 no content
  if (res.status === 204) return null;
  return res.json();
}

export const missionApi = {
  getActive: () => jfetch('/api/missions/active/'),
  patchPlan: (planId, payload) => jfetch(`/api/missions/plans/${planId}/`, { method: 'PATCH', body: JSON.stringify(payload) }),
  addStep: (planId, payload) => jfetch(`/api/missions/plans/${planId}/steps/`, { method: 'POST', body: JSON.stringify(payload) }),
  deleteStep: (stepId) => jfetch(`/api/missions/steps/${stepId}/`, { method: 'DELETE' }),
  clearSteps: (planId) => jfetch(`/api/missions/plans/${planId}/steps/clear/`, { method: 'POST' }),
  run: (planId) => jfetch(`/api/missions/plans/${planId}/run/`, { method: 'POST' }),
  status: (planId) => jfetch(`/api/missions/plans/${planId}/status/`, { method: 'GET' }),
};