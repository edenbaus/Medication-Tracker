import { useEffect, useState } from 'react'
import { Line, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import analyticsService from '../../services/analyticsService'
import { formatEasternDate } from '../../utils/dateUtils'
import './TrendsChart.css'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

function TrendsChart({ medicationId = null, days = 30, chartType = 'line' }) {
  const [usageData, setUsageData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [grouping, setGrouping] = useState('daily')

  useEffect(() => {
    fetchUsageData()
  }, [medicationId, days, grouping])

  const fetchUsageData = async () => {
    try {
      setLoading(true)
      setError('')

      const data = await analyticsService.getUsageTimeline({
        medication_id: medicationId,
        days,
        grouping,
      })

      setUsageData(data)
    } catch (err) {
      console.error('Failed to fetch usage data:', err)
      setError('Failed to load usage data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="trends-chart loading">Loading chart...</div>
  }

  if (error) {
    return <div className="trends-chart error">{error}</div>
  }

  if (!usageData || !usageData.daily_data || usageData.daily_data.length === 0) {
    return (
      <div className="trends-chart empty">
        <p>No usage data available for the selected period.</p>
        <p>Start logging medications to see your usage trends!</p>
      </div>
    )
  }

  // Prepare chart data
  const labels = usageData.daily_data.map(d => {
    const date = new Date(d.date)
    return grouping === 'weekly'
      ? `Week of ${formatEasternDate(date, { month: 'short', day: 'numeric' })}`
      : formatEasternDate(date, { month: 'short', day: 'numeric' })
  })

  const counts = usageData.daily_data.map(d => d.count)

  const chartData = {
    labels,
    datasets: [
      {
        label: medicationId ? usageData.medication_name : 'All Medications',
        data: counts,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: chartType === 'line'
          ? 'rgba(75, 192, 192, 0.2)'
          : 'rgba(75, 192, 192, 0.5)',
        fill: chartType === 'line',
        tension: 0.3,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `Medication Usage - Last ${days} Days`,
        font: {
          size: 16,
        },
      },
      tooltip: {
        callbacks: {
          afterLabel: function(context) {
            const dataIndex = context.dataIndex
            const medications = usageData.daily_data[dataIndex].medications
            if (medications && medications.length > 0) {
              return 'Medications: ' + medications.join(', ')
            }
            return ''
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
        title: {
          display: true,
          text: 'Number of Doses',
        },
      },
      x: {
        title: {
          display: true,
          text: grouping === 'weekly' ? 'Week' : 'Date',
        },
      },
    },
  }

  const ChartComponent = chartType === 'line' ? Line : Bar

  return (
    <div className="trends-chart-container">
      <div className="trends-chart-controls">
        <div className="control-group">
          <label>Grouping:</label>
          <select value={grouping} onChange={(e) => setGrouping(e.target.value)}>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
          </select>
        </div>

        <div className="trends-stats">
          <span className="stat">
            <strong>Total Logs:</strong> {usageData.total_logs}
          </span>
          {usageData.medication_name && (
            <span className="stat">
              <strong>Medication:</strong> {usageData.medication_name}
            </span>
          )}
        </div>
      </div>

      <div className="trends-chart" style={{ height: '400px' }}>
        <ChartComponent data={chartData} options={options} />
      </div>
    </div>
  )
}

export default TrendsChart
