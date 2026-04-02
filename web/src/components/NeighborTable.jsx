import { useState } from 'react'
import { api } from '../api/client'
import WordInput from './WordInput'

const COLORS = { ancient: '#D97706', medieval: '#4F46E5', modern: '#059669', contemporary: '#DB2777' }
const PERIODS = ['ancient', 'medieval', 'modern', 'contemporary']
const PERIOD_CN = { ancient: '古代', medieval: '中世纪', modern: '近代', contemporary: '当代' }

export default function NeighborTable() {
  const [words, setWords] = useState(['reason'])
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const run = async () => {
    setLoading(true); setError('')
    try { setData(await api.neighbors(words[0])) }
    catch (e) { setError(e.message) }
    setLoading(false)
  }

  return (
    <div>
      <h2 className="text-3xl font-bold mb-2">近邻演化</h2>
      <p className="text-gray-400 mb-6">查看目标词在各时期的 Top-10 最近邻词汇及其相似度</p>
      <div className="card mb-6">
        <WordInput words={words} onChange={setWords} single />
        <button onClick={run} disabled={loading} className="btn btn-primary mt-3">
          {loading ? '查询中...' : '查询'}
        </button>
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
      </div>
      {data && (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className="text-left py-2 px-3 text-gray-500">排名</th>
                {PERIODS.map(p => (
                  <th key={p} className="text-left py-2 px-3">
                    <span className="inline-block w-2 h-2 rounded-full mr-2" style={{ background: COLORS[p] }} />
                    {PERIOD_CN[p]}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Array.from({ length: 10 }, (_, i) => (
                <tr key={i} className="border-t border-white/5">
                  <td className="py-2 px-3 text-gray-500">{i + 1}</td>
                  {PERIODS.map(p => {
                    const item = data[p]?.[i]
                    return (
                      <td key={p} className="py-2 px-3">
                        {item && (
                          <>
                            <span className="text-gray-200">{item.word}</span>
                            <span className="text-gray-500 ml-2 text-xs">{item.score}</span>
                          </>
                        )}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
