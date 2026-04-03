import { BarChart3, FileStack, House, Sparkles, Upload } from 'lucide-react'

const navItems = [
  { id: 'overview', label: 'Overview', icon: House },
  { id: 'clusters', label: 'Clusters', icon: FileStack },
  { id: 'insights', label: 'Insights', icon: BarChart3 },
]

function Navbar({ activePage, onPageChange, onReset }) {
  return (
    <aside className="w-full rounded-[34px] border border-stone-300 bg-[#f7f0e7] p-5 shadow-[0_24px_60px_rgba(91,67,49,0.08)] lg:sticky lg:top-6 lg:h-[calc(100vh-3rem)] lg:w-80">
      <div className="rounded-[28px] bg-[#b6402c] p-5 text-stone-50">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10 text-[#ffd7a4]">
            <Sparkles size={22} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-[#ffd6c9]">
              EvalFlow
            </p>
            <h1 className="mt-1 text-xl font-semibold tracking-tight">
              Review Console
            </h1>
          </div>
        </div>
        <p className="mt-5 text-sm leading-7 text-[#ffe6df]">
          Navigate the grading workflow page by page instead of scanning one
          oversized dashboard.
        </p>
      </div>

      <nav className="mt-6 space-y-3">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = activePage === item.id

          return (
            <button
              key={item.id}
              className={`flex w-full items-center gap-3 rounded-[22px] px-4 py-4 text-left text-sm font-semibold transition ${
                isActive
                  ? 'bg-[#1c2435] text-white shadow-[0_16px_32px_rgba(28,36,53,0.16)]'
                  : 'bg-white/70 text-stone-700 hover:bg-white'
              }`}
              onClick={() => onPageChange(item.id)}
              type="button"
            >
              <Icon size={18} />
              {item.label}
            </button>
          )
        })}
      </nav>

      <div className="mt-6 rounded-[26px] border border-stone-300 bg-[#fcfaf7] p-5">
        <p className="text-xs uppercase tracking-[0.35em] text-stone-500">
          Navigation tip
        </p>
        <p className="mt-3 text-sm leading-7 text-stone-600">
          Use
          {' '}
          <span className="font-semibold text-stone-900">Overview</span>
          {' '}
          for batch context,
          {' '}
          <span className="font-semibold text-stone-900">Clusters</span>
          {' '}
          for answer review,
          and
          {' '}
          <span className="font-semibold text-stone-900">Insights</span>
          {' '}
          for charts and patterns.
        </p>
      </div>

      <button
        className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-full bg-[#1c2435] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#111827]"
        onClick={onReset}
        type="button"
      >
        <Upload size={16} />
        New Upload
      </button>
    </aside>
  )
}

export default Navbar
