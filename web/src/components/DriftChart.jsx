import { useState } from 'react'
import { api } from '../api/client'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, ComposedChart, ReferenceLine } from 'recharts'
import WordInput from './WordInput'

const COLORS = ['#D97706', '#4F46E5', '#059669', '#DB2777', '#06b6d4', '#f43f5e']

export default function DriftChart() {
  const [words, setWords] = useState(['reason', 'god', 'nature', 'law'])
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const run = async () => {
    setLoading(true); setError('')
    try {
      const res = await api.drift(words)
      const rows = res.years.map((y, i) => {
        const row = { year: y, baseline: res.baseline?.[i] ?? null }
        for (const w of Object.keys(res.series)) row[w] = res.series[w][i]
        return row
      })
      setData(rows)
    } catch (e) { setError(e.message) }
    setLoading(false)
  }

  return (
    <div>
      <h2 className="text-3xl font-bold mb-2">语义漂移分析</h2>
      <p className="text-gray-400 mb-6">
        目标词相对于 Modern 基准期的 Cosine Distance。
        <span className="text-gray-500"> 灰色虚线为共享词汇中最稳定 25% 词的平均漂移（baseline）。</span>
      </p>
      <div className="card mb-6">
        <WordInput words={words} onChange={setWords} />
        <button onClick={run} disabled={loading} className="btn btn-primary mt-3">
          {loading ? '分析中...' : '开始分析'}
        </button>
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
      </div>
      {data && (
        <div className="card" style={{ height: 450 }}>
          <ResponsiveContainer>
            <ComposedChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="year" stroke="#64748b" tick={{ fontSize: 12 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 12 }} domain={[0, 'auto']}
                label={{ value: 'Cosine Distance', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 12 }} />
              <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid #334155', borderRadius: 8 }} />
              <Legend />
              <ReferenceLine y={0} stroke="#334155" />
              <Line type="monotone" dataKey="baseline" stroke="#6b7280"
                strokeWidth={1.5} strokeDasharray="6 3" dot={{ r: 3 }}
                name="Stable Baseline (25%)" />
              {words.map((w, i) => (
                <Line key={w} type="monotone" dataKey={w} stroke={COLORS[i % COLORS.length]}
                  strokeWidth={2.5} dot={{ r: 5 }} activeDot={{ r: 7 }} />
              ))}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
