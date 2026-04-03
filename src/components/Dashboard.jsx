import { CalendarRange, FileText, Layers3 } from 'lucide-react'
import ClustersPage from './ClustersPage'
import InsightsPage from './InsightsPage'
import Navbar from './Navbar'
import OverviewPage from './OverviewPage'

function Dashboard({
  activePage,
  clusterQuery,
  data,
  filteredClusters,
  onClusterSelect,
  onPageChange,
  onQueryChange,
  onReset,
  selectedCluster,
  selectedClusterId,
}) {
  const pageContent = {
    clusters: (
      <ClustersPage
        clusterQuery={clusterQuery}
        filteredClusters={filteredClusters}
        onClusterSelect={onClusterSelect}
        onQueryChange={onQueryChange}
        selectedCluster={selectedCluster}
        selectedClusterId={selectedClusterId}
      />
    ),
    insights: <InsightsPage data={data} />,
    overview: <OverviewPage data={data} onPageChange={onPageChange} />,
  }

  return (
    <main className="min-h-screen bg-[#efe8df] px-4 py-6 text-stone-900 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-[1500px] flex-col gap-6 lg:flex-row">
        <Navbar
          activePage={activePage}
          onPageChange={onPageChange}
          onReset={onReset}
        />

        <section className="flex-1 space-y-6">
          <div className="grid gap-4 xl:grid-cols-[1.25fr_0.75fr]">
            <article className="rounded-[30px] border border-stone-300 bg-[#fcfaf7] px-5 py-5 shadow-[0_18px_40px_rgba(91,67,49,0.08)] sm:px-6">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.35em] text-stone-500">
                    Current page
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold tracking-tight text-stone-950">
                    {activePage.charAt(0).toUpperCase() + activePage.slice(1)}
                  </h2>
                </div>

                <div className="flex flex-wrap gap-3">
                  <div className="inline-flex items-center gap-2 rounded-full bg-[#ead6d4] px-4 py-2 text-sm font-medium text-stone-800">
                    <Layers3 size={16} />
                    {data.summary.clusterCount} clusters
                  </div>
                  <div className="inline-flex items-center gap-2 rounded-full bg-[#efe0cf] px-4 py-2 text-sm font-medium text-stone-800">
                    <FileText size={16} />
                    {data.summary.totalStudents} students
                  </div>
                </div>
              </div>
            </article>

            <article className="rounded-[30px] border border-stone-300 bg-[#1c2435] px-5 py-5 text-stone-50 shadow-[0_24px_60px_rgba(28,36,53,0.18)] sm:px-6">
              <div className="flex items-center gap-3">
                <div className="rounded-2xl bg-white/8 p-3 text-[#f4b860]">
                  <CalendarRange size={18} />
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.35em] text-stone-400">
                    Batch summary
                  </p>
                  <p className="mt-1 text-sm text-stone-200">
                    Ready for moderation and cluster-based review
                  </p>
                </div>
              </div>
              <div className="mt-5 grid grid-cols-2 gap-3">
                <div className="rounded-[22px] border border-white/10 bg-white/6 p-4">
                  <p className="text-xs uppercase tracking-[0.28em] text-stone-400">
                    Average
                  </p>
                  <p className="mt-2 text-3xl font-semibold">
                    {data.summary.averageScore}%
                  </p>
                </div>
                <div className="rounded-[22px] border border-white/10 bg-white/6 p-4">
                  <p className="text-xs uppercase tracking-[0.28em] text-stone-400">
                    Completion
                  </p>
                  <p className="mt-2 text-3xl font-semibold">
                    {data.summary.completionRate}%
                  </p>
                </div>
              </div>
            </article>
          </div>

          {pageContent[activePage]}
        </section>
      </div>
    </main>
  )
}

export default Dashboard
