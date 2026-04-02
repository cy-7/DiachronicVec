const BASE = '/api';

async function request(url, options = {}) {
  const res = await fetch(BASE + url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const api = {
  periods: () => request('/periods'),
  stats: () => request('/corpus/stats'),
  vocab: (period, limit = 500) => request(`/vocab?period=${period}&limit=${limit}`),
  drift: (words, benchmark = 'modern') =>
    request('/analysis/drift', { method: 'POST', body: JSON.stringify({ words, benchmark }) }),
  neighbors: (word, top_n = 10) =>
    request('/analysis/neighbors', { method: 'POST', body: JSON.stringify({ word, top_n }) }),
  jaccard: (word, top_n = 25) =>
    request('/analysis/jaccard', { method: 'POST', body: JSON.stringify({ word, top_n }) }),
  topDrifters: (start = 'ancient', end = 'contemporary', n = 20) =>
    request(`/analysis/top-drifters?start=${start}&end=${end}&n=${n}`),
  scatter: (words, method = 'pca') =>
    request('/analysis/scatter', { method: 'POST', body: JSON.stringify({ words, method }) }),
};
