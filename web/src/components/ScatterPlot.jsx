import { useState, useEffect, useRef } from 'react'
import { api } from '../api/client'
import WordInput from './WordInput'
import * as d3 from 'd3'

const COLORS = { ancient: '#D97706', medieval: '#4F46E5', modern: '#059669', contemporary: '#DB2777' }
const PERIOD_CN = { ancient: '古代', medieval: '中世纪', modern: '近代', contemporary: '当代' }

export default function ScatterPlot() {
  const [words, setWords] = useState(['reason', 'god', 'nature', 'law'])
  const [method, setMethod] = useState('pca')
  const [points, setPoints] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const svgRef = useRef()

  const run = async () => {
    setLoading(true); setError('')
    try {
      const res = await api.scatter(words, method)
      setPoints(res.points)
    } catch (e) { setError(e.message) }
    setLoading(false)
  }

  useEffect(() => {
    if (!points || !svgRef.current) return
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()
    const w = 700, h = 500, m = { top: 20, right: 20, bottom: 30, left: 40 }

    const x = d3.scaleLinear()
      .domain(d3.extent(points, d => d.x)).nice()
      .range([m.left, w - m.right])
    const y = d3.scaleLinear()
      .domain(d3.extent(points, d => d.y)).nice()
      .range([h - m.bottom, m.top])

    svg.attr('viewBox', `0 0 ${w} ${h}`)

    svg.append('g').attr('transform', `translate(0,${h - m.bottom})`)
      .call(d3.axisBottom(x).ticks(6)).call(g => g.selectAll('text').attr('fill', '#64748b'))
      .call(g => g.select('.domain').attr('stroke', '#334155'))
      .call(g => g.selectAll('.tick line').attr('stroke', '#334155'))

    svg.append('g').attr('transform', `translate(${m.left},0)`)
      .call(d3.axisLeft(y).ticks(6)).call(g => g.selectAll('text').attr('fill', '#64748b'))
      .call(g => g.select('.domain').attr('stroke', '#334155'))
      .call(g => g.selectAll('.tick line').attr('stroke', '#334155'))

    const byWord = d3.group(points, d => d.word)
    const periodOrder = ['ancient', 'medieval', 'modern', 'contemporary']
    byWord.forEach(pts => {
      pts.sort((a, b) => periodOrder.indexOf(a.period) - periodOrder.indexOf(b.period))
      svg.append('path')
        .datum(pts)
        .attr('fill', 'none')
        .attr('stroke', '#334155')
        .attr('stroke-width', 1)
        .attr('stroke-dasharray', '4,3')
        .attr('d', d3.line().x(d => x(d.x)).y(d => y(d.y)))
    })

    svg.selectAll('circle').data(points).join('circle')
      .attr('cx', d => x(d.x)).attr('cy', d => y(d.y))
      .attr('r', 6).attr('fill', d => COLORS[d.period]).attr('opacity', 0.85)
      .attr('stroke', '#fff').attr('stroke-width', 0.5)

    svg.selectAll('.label').data(points).join('text')
      .attr('x', d => x(d.x) + 9).attr('y', d => y(d.y) + 4)
      .attr('fill', '#94a3b8').attr('font-size', 10)
      .text(d => d.word)
  }, [points])

  return (
    <div>
      <h2 className="text-3xl font-bold mb-2">向量空间可视化</h2>
      <p className="text-gray-400 mb-6">将高维词向量通过 PCA / t-SNE 降维投影到二维平面，观察词汇在不同时期的空间分布</p>
      <div className="card mb-6">
        <WordInput words={words} onChange={setWords} />
        <div className="flex items-center gap-3 mt-3">
          <select value={method} onChange={e => setMethod(e.target.value)} className="input">
            <option value="pca">PCA</option>
            <option value="tsne">t-SNE</option>
          </select>
          <button onClick={run} disabled={loading} className="btn btn-primary">
            {loading ? '投影中...' : '生成投影'}
          </button>
        </div>
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
      </div>
      {points && (
        <div className="card">
          <div className="flex gap-4 mb-4">
            {Object.entries(COLORS).map(([p, c]) => (
              <div key={p} className="flex items-center gap-1.5 text-xs text-gray-400">
                <div className="w-2.5 h-2.5 rounded-full" style={{ background: c }} />
                <span>{PERIOD_CN[p]}</span>
              </div>
            ))}
          </div>
          <svg ref={svgRef} className="w-full" style={{ maxHeight: 500 }} />
        </div>
      )}
    </div>
  )
}
