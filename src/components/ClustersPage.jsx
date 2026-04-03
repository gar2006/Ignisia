import { Search } from 'lucide-react'
import AnswerViewer from './AnswerViewer'
import ClusterCard from './ClusterCard'

function ClustersPage({
  clusterQuery,
  filteredClusters,
  onClusterSelect,
  onQueryChange,
  selectedCluster,
  selectedClusterId,
}) {
  return (
    <div className="space-y-6">
      <section className="rounded-[34px] border border-stone-300 bg-[#f7f0e7] p-6 shadow-[0_24px_60px_rgba(91,67,49,0.08)] sm:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.42em] text-stone-500">
              Clusters
            </p>
            <h1 className="mt-4 text-4xl font-semibold tracking-tight text-stone-950 sm:text-5xl">
              Compare similar answers as one review unit.
            </h1>
            <p className="mt-4 max-w-2xl text-sm leading-7 text-stone-600">
              Search by cluster label, keyword, or representative phrasing, then
              inspect the answer samples below.
            </p>
          </div>

          <label className="relative block w-full max-w-md">
            <Search
              className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-stone-400"
              size={18}
            />
            <input
              className="w-full rounded-full border border-stone-300 bg-white px-12 py-3 text-sm text-stone-900 outline-none transition focus:border-[#b6402c]"
              onChange={(event) => onQueryChange(event.target.value)}
              placeholder="Search clusters or keywords"
              type="text"
              value={clusterQuery}
            />
          </label>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        {filteredClusters.map((cluster) => (
          <ClusterCard
            cluster={cluster}
            isActive={selectedClusterId === cluster.id}
            key={cluster.id}
            onSelect={onClusterSelect}
          />
        ))}
      </section>

      {!filteredClusters.length && (
        <div className="rounded-[28px] border border-dashed border-stone-300 bg-white/80 p-10 text-center text-sm text-stone-500">
          No clusters matched your search. Try terms like
          {' '}
          <span className="font-semibold text-stone-800">photosynthesis</span>
          {' '}
          or
          {' '}
          <span className="font-semibold text-stone-800">oxygen</span>.
        </div>
      )}

      <AnswerViewer cluster={selectedCluster} />
    </div>
  )
}

export default ClustersPage
