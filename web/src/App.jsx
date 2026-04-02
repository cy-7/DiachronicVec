import { useState } from 'react'
import Layout from './components/Layout'
import Dashboard from './components/Dashboard'
import DriftChart from './components/DriftChart'
import NeighborTable from './components/NeighborTable'
import JaccardChart from './components/JaccardChart'
import ScatterPlot from './components/ScatterPlot'
import TopDrifters from './components/TopDrifters'

const TABS = [
  { id: 'dashboard', label: '总览', icon: '◈' },
  { id: 'drift', label: '语义漂移', icon: '⟿' },
  { id: 'neighbors', label: '近邻演化', icon: '⊛' },
  { id: 'jaccard', label: 'Jaccard 重叠', icon: '⩀' },
  { id: 'scatter', label: '向量空间', icon: '⊹' },
  { id: 'drifters', label: '漂移排行', icon: '⇡' },
]

const VIEWS = {
  dashboard: Dashboard,
  drift: DriftChart,
  neighbors: NeighborTable,
  jaccard: JaccardChart,
  scatter: ScatterPlot,
  drifters: TopDrifters,
}

export default function App() {
  const [tab, setTab] = useState('dashboard')
  const View = VIEWS[tab]
  return (
    <Layout tabs={TABS} active={tab} onTab={setTab}>
      <View />
    </Layout>
  )
}
