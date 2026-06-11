/**
 * API helper — wraps fetch with base URL and auth token.
 */
const BASE = import.meta.env.VITE_API_BASE || '';

let _token = null;

export function setToken(t) { _token = t; }
export function clearToken() { _token = null;
  _token = null; }

function headers() {
  const h = { 'Content-Type': 'application/json' };
  if (_token) h['Authorization'] = `Bearer ${_token}`;
  return h;
}

async function request(url, options = {}) {
  const res = await fetch(`${BASE}${url}`, { ...options, headers: headers() });
  const data = await res.json();
  if (!res.ok) {
    let msg = data.detail || data.message || `HTTP ${res.status}`;
    if (Array.isArray(msg)) {
      msg = msg.map((e) => e.msg || JSON.stringify(e)).join('; ');
    } else if (typeof msg === 'object') {
      msg = JSON.stringify(msg);
    }
    throw new Error(msg);
  }
  return data;
}

export function get(url) { return request(url); }
export function post(url, body) { return request(url, { method: 'POST', body: JSON.stringify(body) }); }
export function put(url, body) { return request(url, { method: 'PUT', body: JSON.stringify(body) }); }
export function del(url) { return request(url, { method: 'DELETE' }); }
