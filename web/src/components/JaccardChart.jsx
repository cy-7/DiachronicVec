import { useState } from 'react'
import { api } from '../api/client'
import WordInput from './WordInput'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const PAIR_CN = { 'ancient-medieval': '古代→中世纪', 'medieval-modern': '中世纪→近代', 'modern-contemporary': '近代→当代' }
const K_COLORS = { 10: '#06b6d4', 25: '#4F46E5', 50: '#DB2777' }

export default function JaccardChart() {
  const [words, setWords] = useState(['reason'])
  const [data, setData] = useState(null)
  const [kValues, setKValues] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const run = async () => {
    setLoading(true); setError('')
    try {
      const res = await api.jaccard(words[0])
      const ks = Object.keys(res.results_by_k).map(Number).sort((a, b) => a - b)
      setKValues(ks)
      setData(res.labels.map((l, i) => {
        const row = { pair: PAIR_CN[l] || l }
        for (const k of ks) row[`k${k}`] = res.results_by_k[String(k)]?.[i] ?? res.results_by_k[k]?.[i] ?? 0
        return row
      }))
    } catch (e) { setError(e.message) }
    setLoading(false)
  }

  return (
    <div>
      <h2 className="text-3xl font-bold mb-2">Jaccard 重叠度</h2>
      <p className="text-gray-400 mb-6">
        相邻时期近邻词集合的 Jaccard 相似度（多 k 值对比），k 越小越聚焦核心语义圈。
      </p>
      <div className="card mb-6">
        <WordInput words={words} onChange={setWords} single />
        <button onClick={run} disabled={loading} className="btn btn-primary mt-3">
          {loading ? '分析中...' : '开始分析'}
        </button>
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
      </div>
      {data && (
        <div className="card" style={{ height: 400 }}>
          <ResponsiveContainer>
            <BarChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="pair" stroke="#64748b" tick={{ fontSize: 12 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 12 }} domain={[0, 'auto']}
                label={{ value: 'Jaccard Index', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 12 }} />
              <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid #334155', borderRadius: 8 }} />
              <Legend />
              {kValues.map(k => (
                <Bar key={k} dataKey={`k${k}`} fill={K_COLORS[k] || '#8884d8'}
                  radius={[4, 4, 0, 0]} name={`Top-${k}`} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
