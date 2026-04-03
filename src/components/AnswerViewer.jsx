import { FileSearch, UserRound } from 'lucide-react'

function highlightText(text, keywords) {
  const escapedKeywords = keywords
    .filter(Boolean)
    .map((keyword) => keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))

  if (!escapedKeywords.length) {
    return text
  }

  const matcher = new RegExp(`(${escapedKeywords.join('|')})`, 'gi')
  const segments = text.split(matcher)

  return segments.map((segment, index) => {
    const isHighlighted = keywords.some(
      (keyword) => keyword.toLowerCase() === segment.toLowerCase(),
    )

    return isHighlighted ? (
      <mark
        key={`${segment}-${index}`}
        className="rounded bg-amber-200 px-1 py-0.5 text-amber-950"
      >
        {segment}
      </mark>
    ) : (
      <span key={`${segment}-${index}`}>{segment}</span>
    )
  })
}

function AnswerViewer({ cluster }) {
  if (!cluster) {
    return (
      <section className="rounded-[28px] border border-dashed border-stone-300 bg-white/80 p-8 text-center">
        <p className="text-sm text-stone-500">
          Select a cluster to inspect student answers.
        </p>
      </section>
    )
  }

  return (
    <section className="rounded-[30px] border border-stone-300 bg-[#fcfaf7] p-5 shadow-[0_18px_40px_rgba(91,67,49,0.08)]">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-stone-500">
            Answer Viewer
          </p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-stone-950">
            {cluster.id} submissions
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-7 text-stone-600">
            Keyword matches are highlighted to help with quick rubric checks and
            moderation.
          </p>
        </div>

        <div className="rounded-full bg-[#1c2435] px-4 py-3 text-sm font-medium text-[#f4b860]">
          {cluster.answers.length} sample answers
        </div>
      </div>

      <div className="mt-6 space-y-4">
        {cluster.answers.map((answer) => (
          <article
            key={answer.studentId}
            className="rounded-[24px] border border-stone-200 bg-white p-5"
          >
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-[#efe0cf] p-3 text-[#8a3b2a]">
                <UserRound size={18} />
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-stone-500">
                  Student ID
                </p>
                <p className="mt-1 text-sm font-semibold text-stone-950">
                  {answer.studentId}
                </p>
              </div>
            </div>

            <div className="mt-4 flex items-start gap-3 rounded-2xl bg-[#f7f0e7] p-4">
              <div className="mt-1 text-stone-400">
                <FileSearch size={18} />
              </div>
              <p className="text-sm leading-7 text-stone-700">
                {highlightText(answer.text, cluster.keywordsMatched)}
              </p>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

export default AnswerViewer
