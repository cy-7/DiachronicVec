import { useState } from 'react'
import { api } from '../api/client'

export default function TopDrifters() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const run = async () => {
    setLoading(true); setError('')
    try { setData(await api.topDrifters()) }
    catch (e) { setError(e.message) }
    setLoading(false)
  }

  return (
    <div>
      <h2 className="text-3xl font-bold mb-2">漂移排行榜</h2>
      <p className="text-gray-400 mb-6">从古代到当代语义变化幅度最大的词汇排名</p>
      <div className="card mb-6">
        <button onClick={run} disabled={loading} className="btn btn-primary">
          {loading ? '计算中...' : '计算排行'}
        </button>
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
      </div>
      {data && (
        <div className="card">
          <div className="space-y-2">
            {data.map((item, i) => {
              const maxDist = data[0]?.distance || 1
              const pct = (item.distance / maxDist) * 100
              return (
                <div key={item.word} className="flex items-center gap-3">
                  <span className="text-gray-500 text-sm w-6 text-right">{i + 1}</span>
                  <span className="text-gray-200 text-sm w-32 truncate">{item.word}</span>
                  <div className="flex-1 h-5 bg-surface rounded-full overflow-hidden">
                    <div className="h-full rounded-full bg-gradient-to-r from-indigo-600 to-pink-500 transition-all"
                      style={{ width: `${pct}%` }} />
                  </div>
                  <span className="text-gray-400 text-xs w-14 text-right">{item.distance}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
