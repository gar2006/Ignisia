import { CheckCircle2, CircleSlash2, Sparkles, TriangleAlert } from 'lucide-react'
import Charts from './Charts'

function InsightsPage({ data }) {
  const keywordLeaderboard = Object.entries(
    data.clusters.reduce((accumulator, cluster) => {
      cluster.keywordsMatched.forEach((keyword) => {
        accumulator[keyword] = (accumulator[keyword] ?? 0) + cluster.studentCount
      })

      return accumulator
    }, {}),
  )
    .sort((left, right) => right[1] - left[1])
    .slice(0, 5)

  const accuracyCards = [
    {
      label: 'Correct',
      value: `${data.accuracy.find((item) => item.name === 'Correct')?.value ?? 0}%`,
      icon: CheckCircle2,
      tone: 'bg-[#d9e4da]',
    },
    {
      label: 'Partial',
      value: `${data.accuracy.find((item) => item.name === 'Partial')?.value ?? 0}%`,
      icon: Sparkles,
      tone: 'bg-[#efe0cf]',
    },
    {
      label: 'Wrong',
      value: `${data.accuracy.find((item) => item.name === 'Wrong')?.value ?? 0}%`,
      icon: TriangleAlert,
      tone: 'bg-[#ead6d4]',
    },
  ]

  return (
    <div className="space-y-6">
      <section className="rounded-[34px] border border-stone-300 bg-white/85 p-6 shadow-[0_24px_60px_rgba(91,67,49,0.08)] sm:p-8">
        <p className="text-xs uppercase tracking-[0.42em] text-stone-500">
          Insights
        </p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-stone-950 sm:text-5xl">
          Performance patterns, separated from manual review.
        </h1>
        <p className="mt-4 max-w-2xl text-sm leading-7 text-stone-600">
          This page focuses on distribution, accuracy, and repeated rubric signals
          so teams can moderate with context before assigning final marks.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {accuracyCards.map((card) => {
          const Icon = card.icon

          return (
            <article
              key={card.label}
              className="rounded-[28px] border border-stone-300 bg-[#fcfaf7] p-5"
            >
              <div className={`inline-flex rounded-2xl p-3 ${card.tone}`}>
                <Icon size={18} />
              </div>
              <p className="mt-4 text-sm font-medium text-stone-600">{card.label}</p>
              <p className="mt-2 text-4xl font-semibold tracking-tight text-stone-950">
                {card.value}
              </p>
            </article>
          )
        })}
      </section>

      <Charts accuracy={data.accuracy} clusters={data.clusters} />

      <section className="grid gap-6 xl:grid-cols-[1fr_0.95fr]">
        <article className="rounded-[30px] border border-stone-300 bg-[#1c2435] p-6 text-stone-50">
          <p className="text-xs uppercase tracking-[0.35em] text-[#f4b860]">
            Keyword pressure points
          </p>
          <div className="mt-6 space-y-4">
            {keywordLeaderboard.map(([keyword, count], index) => (
              <div
                key={keyword}
                className="flex items-center justify-between gap-4 rounded-[22px] border border-white/10 bg-white/6 px-4 py-4"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#f4b860] text-sm font-semibold text-[#1c2435]">
                    {index + 1}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">{keyword}</p>
                    <p className="text-xs uppercase tracking-[0.24em] text-stone-400">
                      matched cluster keyword
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-white">{count}</p>
                  <p className="text-xs text-stone-400">student mentions</p>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="rounded-[30px] border border-stone-300 bg-[#b6402c] p-6 text-stone-50 shadow-[0_24px_60px_rgba(182,64,44,0.18)]">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-white/10 p-3">
              <CircleSlash2 size={18} />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-[#ffd6c9]">
                Intervention
              </p>
              <p className="mt-1 text-lg font-semibold">Where reviewers should focus</p>
            </div>
          </div>

          <div className="mt-6 space-y-4 text-sm leading-7 text-[#ffe6df]">
            <p>
              Partial and wrong responses together account for
              {' '}
              <span className="font-semibold text-white">
                {(data.accuracy.find((item) => item.name === 'Partial')?.value ?? 0) +
                  (data.accuracy.find((item) => item.name === 'Wrong')?.value ?? 0)}
                %
              </span>
              {' '}
              of the batch.
            </p>
            <p>
              Use the cluster view to standardize marks for weak conceptual groups,
              especially where answers omit core science terms from the answer key.
            </p>
          </div>
        </article>
      </section>
    </div>
  )
}

export default InsightsPage
