/**
 * API helper — wraps fetch with base URL and error handling.
 *
 * In development, Vite proxy forwards /api/* to the backend.
 * In production, set VITE_API_BASE to the deployed backend URL.
 */
const BASE = import.meta.env.VITE_API_BASE || '';

export async function get(url) {
  const res = await fetch(`${BASE}${url}`);
  if (!res.ok) throw new Error(`GET ${url} failed: ${res.status}`);
  return res.json();
}

export async function post(url, body) {
  const res = await fetch(`${BASE}${url}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${url} failed: ${res.status}`);
  return res.json();
}

export async function put(url, body) {
  const res = await fetch(`${BASE}${url}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`PUT ${url} failed: ${res.status}`);
  return res.json();
}

export async function del(url) {
  const res = await fetch(`${BASE}${url}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`DELETE ${url} failed: ${res.status}`);
  return res.json();
}
