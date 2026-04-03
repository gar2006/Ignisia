import { useMemo, useState } from 'react'
import Dashboard from './components/Dashboard'
import UploadPage from './components/UploadPage'
import mockData from './data/mockData'

function App() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [dashboardData, setDashboardData] = useState(null)
  const [selectedClusterId, setSelectedClusterId] = useState(null)
  const [clusterQuery, setClusterQuery] = useState('')
  const [activePage, setActivePage] = useState('overview')

  const filteredClusters = useMemo(() => {
    if (!dashboardData) {
      return []
    }

    const query = clusterQuery.trim().toLowerCase()

    if (!query) {
      return dashboardData.clusters
    }

    return dashboardData.clusters.filter((cluster) => {
      const keywordMatch = cluster.keywordsMatched.some((keyword) =>
        keyword.toLowerCase().includes(query),
      )

      return (
        cluster.id.toLowerCase().includes(query) ||
        cluster.representativeAnswer.toLowerCase().includes(query) ||
        keywordMatch
      )
    })
  }, [clusterQuery, dashboardData])

  const selectedCluster = useMemo(() => {
    if (!dashboardData) {
      return null
    }

    const preferredId =
      selectedClusterId ?? filteredClusters[0]?.id ?? dashboardData.clusters[0]?.id

    return (
      dashboardData.clusters.find((cluster) => cluster.id === preferredId) ?? null
    )
  }, [dashboardData, filteredClusters, selectedClusterId])

  const handleProcess = (files) => {
    setIsProcessing(true)

    window.setTimeout(() => {
      setDashboardData({
        ...mockData,
        uploadedFiles: files,
      })
      setSelectedClusterId(mockData.clusters[0]?.id ?? null)
      setActivePage('overview')
      setIsProcessing(false)
    }, 1800)
  }

  const handleReset = () => {
    setDashboardData(null)
    setSelectedClusterId(null)
    setClusterQuery('')
    setActivePage('overview')
    setIsProcessing(false)
  }

  if (!dashboardData) {
    return (
      <UploadPage
        isProcessing={isProcessing}
        onProcess={handleProcess}
      />
    )
  }

  return (
    <Dashboard
      activePage={activePage}
      clusterQuery={clusterQuery}
      data={dashboardData}
      filteredClusters={filteredClusters}
      onClusterSelect={setSelectedClusterId}
      onPageChange={setActivePage}
      onQueryChange={setClusterQuery}
      onReset={handleReset}
      selectedCluster={selectedCluster}
      selectedClusterId={selectedCluster?.id ?? null}
    />
  )
}

export default App
