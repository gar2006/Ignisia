import { ArrowUpRight, BrainCircuit, FileText, Users, Workflow } from 'lucide-react'

const metricIcons = {
  'Average score': BrainCircuit,
  'Clusters count': Workflow,
  'Total students': Users,
}

function OverviewPage({ data, onPageChange }) {
  const metrics = [
    { label: 'Total students', value: data.summary.totalStudents, tone: 'bg-[#efe0cf]' },
    { label: 'Clusters count', value: data.summary.clusterCount, tone: 'bg-[#d9e4da]' },
    { label: 'Average score', value: `${data.summary.averageScore}%`, tone: 'bg-[#ead6d4]' },
  ]

  const topClusters = [...data.clusters]
    .sort((left, right) => right.studentCount - left.studentCount)
    .slice(0, 3)

  return (
    <div className="space-y-6">
      <section className="rounded-[36px] border border-stone-300 bg-[#1c2435] p-7 text-stone-50 shadow-[0_30px_80px_rgba(28,36,53,0.18)] sm:p-9">
        <div className="grid gap-8 xl:grid-cols-[1.35fr_0.9fr]">
          <div>
            <p className="text-xs uppercase tracking-[0.45em] text-[#f4b860]">
              AI Grading Dashboard
            </p>
            <h1 className="mt-5 max-w-3xl text-4xl font-semibold tracking-tight sm:text-6xl">
              A review room for automated grading, built around decisions.
            </h1>
            <p className="mt-5 max-w-2xl text-sm leading-7 text-stone-300 sm:text-base">
              Move from uploaded scripts to grading actions with a calmer workflow:
              high-level performance first, cluster review second, and rubric insights
              in their own dedicated page.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <button
                className="inline-flex items-center gap-2 rounded-full bg-[#f4b860] px-5 py-3 text-sm font-semibold text-[#1c2435] transition hover:bg-[#f0c57d]"
                onClick={() => onPageChange('clusters')}
                type="button"
              >
                Review Clusters
                <ArrowUpRight size={16} />
              </button>
              <button
                className="inline-flex items-center gap-2 rounded-full border border-white/15 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/5"
                onClick={() => onPageChange('insights')}
                type="button"
              >
                Open Insights
              </button>
            </div>
          </div>

          <div className="grid gap-4 rounded-[28px] border border-white/10 bg-white/6 p-5">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-stone-400">
                Uploaded batch
              </p>
              <div className="mt-4 space-y-3">
                {[
                  data.uploadedFiles.questionPaper?.name,
                  data.uploadedFiles.answerKey?.name,
                  data.uploadedFiles.studentAnswers?.name,
                ].map((fileName) => (
                  <div
                    key={fileName}
                    className="flex items-center gap-3 rounded-2xl border border-white/10 bg-black/10 px-4 py-3"
                  >
                    <div className="rounded-xl bg-white/8 p-2 text-[#f4b860]">
                      <FileText size={16} />
                    </div>
                    <p className="truncate text-sm text-stone-200">{fileName}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {metrics.map((metric) => {
          const Icon = metricIcons[metric.label]

          return (
            <article
              key={metric.label}
              className="rounded-[28px] border border-stone-300 bg-[#f7f0e7] p-5 shadow-[0_16px_40px_rgba(91,67,49,0.08)]"
            >
              <div className={`inline-flex rounded-2xl p-3 ${metric.tone}`}>
                <Icon size={18} />
              </div>
              <p className="mt-4 text-sm font-medium text-stone-600">{metric.label}</p>
              <p className="mt-2 text-4xl font-semibold tracking-tight text-stone-950">
                {metric.value}
              </p>
            </article>
          )
        })}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.95fr]">
        <article className="rounded-[30px] border border-stone-300 bg-white/80 p-6 shadow-[0_24px_60px_rgba(91,67,49,0.08)]">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-stone-500">
                Dominant clusters
              </p>
              <h2 className="mt-3 text-2xl font-semibold tracking-tight text-stone-950">
                Largest answer groups in this batch
              </h2>
            </div>
          </div>

          <div className="mt-6 grid gap-4">
            {topClusters.map((cluster) => (
              <div
                key={cluster.id}
                className="rounded-[24px] border border-stone-200 bg-[#fcfaf7] p-5"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-xs uppercase tracking-[0.28em] text-stone-500">
                      {cluster.id}
                    </p>
                    <p className="mt-3 max-w-2xl text-sm leading-7 text-stone-700">
                      {cluster.representativeAnswer}
                    </p>
                  </div>
                  <div className="rounded-full bg-[#1c2435] px-4 py-2 text-sm font-semibold text-white">
                    {cluster.studentCount} students
                  </div>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="rounded-[30px] border border-stone-300 bg-[#b6402c] p-6 text-stone-50 shadow-[0_24px_60px_rgba(182,64,44,0.18)]">
          <p className="text-xs uppercase tracking-[0.35em] text-[#ffd6c9]">
            Moderation status
          </p>
          <h2 className="mt-4 text-3xl font-semibold tracking-tight">
            Rubric review is concentrated in {data.summary.clusterCount} meaningful groups.
          </h2>
          <p className="mt-4 text-sm leading-7 text-[#ffe6df]">
            That means assessors can standardize marks cluster-by-cluster instead of
            reading every script from scratch.
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            <div className="rounded-[24px] border border-white/15 bg-white/8 p-4">
              <p className="text-xs uppercase tracking-[0.28em] text-[#ffd6c9]">
                Completion
              </p>
              <p className="mt-2 text-3xl font-semibold">
                {data.summary.completionRate}%
              </p>
            </div>
            <div className="rounded-[24px] border border-white/15 bg-white/8 p-4">
              <p className="text-xs uppercase tracking-[0.28em] text-[#ffd6c9]">
                Suggested average
              </p>
              <p className="mt-2 text-3xl font-semibold">
                {data.summary.averageScore}%
              </p>
            </div>
          </div>
        </article>
      </section>
    </div>
  )
}

export default OverviewPage
