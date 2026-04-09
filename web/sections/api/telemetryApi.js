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
  // SSE Stream connection - This is now the primary data source
  connectStream: () => {
    return new EventSource(`${BASE}/api/telemetry/stream/`);
  },

  // Bluetooth controls still require HTTP for state toggling
  getBluetoothState: () => jfetch('/api/telemetry/ble-control/', { method: 'GET' }),
  
  setBluetoothState: (isActive) => jfetch('/api/telemetry/ble-control/', {
    method: 'POST',
    body: JSON.stringify({ active: isActive })
  })
};