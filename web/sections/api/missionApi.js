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

export const missionApi = {

  getActive: () => jfetch('/api/missions/active/'),
  patchPlan: (planId, payload) => jfetch(`/api/missions/${planId}/`, { method: 'PATCH', body: JSON.stringify(payload) }),
  addStep: (planId, payload) => jfetch(`/api/missions/${planId}/steps/`, { method: 'POST', body: JSON.stringify(payload) }),
  deleteStep: (stepId) => jfetch(`/api/missions/steps/${stepId}/`, { method: 'DELETE' }),
  clearSteps: (planId) => jfetch(`/api/missions/${planId}/steps/clear/`, { method: 'POST' }),

  run: async () => {
    const planRes = await missionApi.getActive();
    
    return jfetch(`/api/missions/run/`, { 
        method: 'POST',
        body: JSON.stringify({
            steps: planRes.steps || [],
            flightParams: { speed: planRes.speed }
        })
    });
  },
  
  status: () => jfetch(`/api/missions/status/`, { method: 'GET' }),

  sendCommand: (cmd) => jfetch(`/api/missions/override/`, { 
      method: 'POST', 
      body: JSON.stringify({ command: cmd }) 
  }),
  
  forceLand: () => jfetch(`/api/missions/override/`, { 
      method: 'POST', 
      body: JSON.stringify({ command: 'land' }) 
  })
};