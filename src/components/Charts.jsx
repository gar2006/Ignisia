import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

function TooltipCard({ active, payload, label, formatter }) {
  if (!active || !payload?.length) {
    return null
  }

  return (
    <div className="chart-tooltip">
      <p className="text-xs uppercase tracking-[0.25em] text-slate-400">{label}</p>
      <p className="mt-2 text-sm font-semibold text-white">
        {formatter ? formatter(payload[0].value) : payload[0].value}
      </p>
    </div>
  )
}

function Charts({ accuracy, clusters }) {
  const clusterChartData = clusters.map((cluster) => ({
    id: cluster.id,
    students: cluster.studentCount,
  }))

  return (
    <div
      className="grid gap-6 xl:grid-cols-[minmax(0,1.4fr)_minmax(320px,0.9fr)]"
    >
      <article className="rounded-[30px] border border-stone-300 bg-white/85 p-5 shadow-[0_18px_40px_rgba(91,67,49,0.08)]">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold text-stone-900">
              Cluster distribution
            </p>
            <p className="mt-1 text-sm text-stone-500">
              Student volume across answer similarity groups
            </p>
          </div>
        </div>

        <div className="mt-6 h-80">
          <ResponsiveContainer height="100%" width="100%">
            <BarChart data={clusterChartData}>
              <XAxis
                axisLine={false}
                dataKey="id"
                tick={{ fill: '#6b645c', fontSize: 12 }}
                tickLine={false}
              />
              <YAxis
                axisLine={false}
                tick={{ fill: '#6b645c', fontSize: 12 }}
                tickLine={false}
              />
              <Tooltip
                content={<TooltipCard formatter={(value) => `${value} students`} />}
                cursor={{ fill: 'rgba(182, 64, 44, 0.08)' }}
              />
              <Bar dataKey="students" fill="#b6402c" radius={[12, 12, 4, 4]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </article>

      <article className="rounded-[30px] border border-stone-300 bg-white/85 p-5 shadow-[0_18px_40px_rgba(91,67,49,0.08)]">
        <div>
          <p className="text-sm font-semibold text-stone-900">Accuracy split</p>
          <p className="mt-1 text-sm text-stone-500">
            Answer quality against the supplied answer key
          </p>
        </div>

        <div className="mt-6 h-80">
          <ResponsiveContainer height="100%" width="100%">
            <PieChart>
              <Pie
                cx="50%"
                cy="50%"
                data={accuracy}
                dataKey="value"
                innerRadius={60}
                outerRadius={108}
                paddingAngle={4}
              >
                {accuracy.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                content={<TooltipCard formatter={(value) => `${value}% coverage`} />}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          {accuracy.map((item) => (
            <div
              key={item.name}
              className="rounded-2xl border border-stone-200 bg-[#fcfaf7] p-3"
            >
              <div className="flex items-center gap-2">
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: item.color }}
                />
                <p className="text-sm font-medium text-stone-700">{item.name}</p>
              </div>
              <p className="mt-2 text-2xl font-semibold tracking-tight text-stone-950">
                {item.value}%
              </p>
            </div>
          ))}
        </div>
      </article>
    </div>
  )
}

export default Charts
