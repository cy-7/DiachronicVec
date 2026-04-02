import { useState, useEffect } from 'react'
import { api } from '../api/client'

const COLORS = { ancient: '#D97706', medieval: '#4F46E5', modern: '#059669', contemporary: '#DB2777' }

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  useEffect(() => { api.stats().then(setStats).catch(() => {}) }, [])

  const PERIOD_CN = { ancient: '古代', medieval: '中世纪', modern: '近代', contemporary: '当代' }

  return (
    <div>
      <h2 className="text-3xl font-bold mb-2">项目总览</h2>
      <p className="text-gray-400 mb-8">西方哲学历时词向量分析工具概览</p>

      {stats ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {Object.entries(stats.vocab_sizes || {}).map(([period, size]) => (
            <div key={period} className="card">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2.5 h-2.5 rounded-full" style={{ background: COLORS[period] }} />
                <span className="text-sm text-gray-400">{PERIOD_CN[period] || period}</span>
              </div>
              <p className="text-2xl font-bold">{size.toLocaleString()}</p>
              <p className="text-xs text-gray-500">词汇量</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="card mb-8">
          <p className="text-gray-400">
            请先启动 API 服务器：<code className="text-indigo-400">python run.py serve</code>
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-3">关于本项目</h3>
          <p className="text-sm text-gray-400 leading-relaxed">
            DiachronicVec 通过分析西方哲学四个历史时期的文本语料，研究哲学核心概念的语义演变。
            项目使用 Word2Vec 训练各时期的词向量模型，并通过 Orthogonal Procrustes 方法将它们对齐到统一的向量空间，
            从而实现跨时代的语义比较与可视化分析。
          </p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-3">历史分期</h3>
          <div className="space-y-3">
            {[
              { name: '古代', year: '约公元前 400 年', desc: '柏拉图、亚里士多德、斯多葛学派', color: COLORS.ancient },
              { name: '中世纪', year: '约 1200 年', desc: '阿奎那、奥古斯丁、安瑟伦', color: COLORS.medieval },
              { name: '近代', year: '约 1800 年', desc: '康德、休谟、黑格尔', color: COLORS.modern },
              { name: '当代', year: '约 2000 年', desc: '维特根斯坦、福柯、罗尔斯', color: COLORS.contemporary },
            ].map(p => (
              <div key={p.name} className="flex items-center gap-3">
                <div className="w-1 h-8 rounded-full" style={{ background: p.color }} />
                <div>
                  <span className="text-sm font-medium">{p.name}</span>
                  <span className="text-xs text-gray-500 ml-2">{p.year}</span>
                  <p className="text-xs text-gray-500">{p.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {stats && (
        <div className="card mt-6">
          <p className="text-sm text-gray-400">
            四个时期共享词汇量：<span className="text-indigo-300 font-semibold">{stats.shared_vocab?.toLocaleString()}</span> 个词
          </p>
        </div>
      )}
    </div>
  )
}
