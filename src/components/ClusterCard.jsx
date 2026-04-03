import { CheckCircle2, Eye, Layers3, PencilLine, Users2 } from 'lucide-react'

function ClusterCard({ cluster, isActive, onSelect }) {
  return (
    <article
      className={`rounded-[28px] border p-5 transition ${
        isActive
          ? 'border-[#b6402c] bg-[#fff8f2] shadow-[0_20px_45px_rgba(182,64,44,0.12)]'
          : 'border-stone-300 bg-white/85 shadow-[0_16px_40px_rgba(91,67,49,0.08)] hover:-translate-y-0.5'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-stone-500">
            Cluster ID
          </p>
          <h3 className="mt-2 text-xl font-semibold tracking-tight text-stone-950">
            {cluster.id}
          </h3>
        </div>
        <div className="rounded-2xl bg-[#1c2435] p-3 text-[#f4b860]">
          <Layers3 size={18} />
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <div className="rounded-2xl bg-[#efe0cf] px-4 py-3">
          <p className="flex items-center gap-2 text-xs uppercase tracking-[0.24em] text-stone-600">
            <Users2 size={14} />
            Students
          </p>
          <p className="mt-2 text-lg font-semibold text-stone-950">
            {cluster.studentCount}
          </p>
        </div>
        <div className="rounded-2xl bg-[#d9e4da] px-4 py-3">
          <p className="flex items-center gap-2 text-xs uppercase tracking-[0.24em] text-[#415d4b]">
            <CheckCircle2 size={14} />
            Suggested Marks
          </p>
          <p className="mt-2 text-lg font-semibold text-[#193225]">
            {cluster.assignedMarks}/10
          </p>
        </div>
      </div>

      <div className="mt-5">
        <p className="text-sm font-semibold text-stone-900">
          Representative answer
        </p>
        <p className="mt-2 text-sm leading-7 text-stone-600">
          {cluster.representativeAnswer}
        </p>
      </div>

      <div className="mt-5">
        <p className="text-sm font-semibold text-stone-900">Keywords matched</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {cluster.keywordsMatched.map((keyword) => (
            <span
              key={keyword}
              className="rounded-full border border-[#e5c6b9] bg-[#fff3eb] px-3 py-1 text-xs font-medium text-[#8a3b2a]"
            >
              {keyword}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <button
          className="inline-flex items-center justify-center gap-2 rounded-full bg-[#1c2435] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#111827]"
          onClick={() => onSelect(cluster.id)}
          type="button"
        >
          <Eye size={16} />
          View Answers
        </button>
        <button
          className="inline-flex items-center justify-center gap-2 rounded-full border border-stone-300 px-4 py-3 text-sm font-semibold text-stone-700 transition hover:bg-[#f7f0e7]"
          onClick={() => onSelect(cluster.id)}
          type="button"
        >
          <PencilLine size={16} />
          Assign Marks
        </button>
      </div>
    </article>
  )
}

export default ClusterCard
