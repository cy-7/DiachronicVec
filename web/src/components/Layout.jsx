export default function Layout({ tabs, active, onTab, children }) {
  return (
    <div className="flex h-screen overflow-hidden">
      <nav className="w-56 bg-panel/60 border-r border-white/5 flex flex-col py-6 px-3 shrink-0">
        <div className="mb-8 px-3">
          <h1 className="text-xl font-bold tracking-tight">
            <span className="text-indigo-400">Diachronic</span>
            <span className="text-gray-400">Vec</span>
          </h1>
          <p className="text-[11px] text-gray-500 mt-1">西方哲学历时语义分析</p>
        </div>
        <div className="flex flex-col gap-1">
          {tabs.map(t => (
            <button
              key={t.id}
              onClick={() => onTab(t.id)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all text-left
                ${active === t.id
                  ? 'bg-indigo-600/20 text-indigo-300 font-medium'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'}`}
            >
              <span className="text-base">{t.icon}</span>
              {t.label}
            </button>
          ))}
        </div>
        <div className="mt-auto px-3 pt-4 border-t border-white/5">
          <p className="text-[10px] text-gray-600">西方哲学史语料库</p>
          <p className="text-[10px] text-gray-600">古代 → 当代</p>
        </div>
      </nav>
      <main className="flex-1 overflow-y-auto p-8">
        {children}
      </main>
    </div>
  )
}
