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
  
  getLatest: () => jfetch('/api/telemetry/latest/', { method: 'GET' }),


};