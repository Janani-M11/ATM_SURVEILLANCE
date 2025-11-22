import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Users,
  AlertTriangle,
  Shield,
  Eye,
  Clock,
  Activity,
  Calendar,
  Download,
  RefreshCw,
  BarChart3,
  PieChart as PieChartIcon
} from 'lucide-react';
import './Analytics.css';

const Analytics = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7d');
  const [chartType, setChartType] = useState('line');

  const timeRanges = [
    { value: '1d', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' }
  ];

  const chartTypes = [
    { value: 'line', label: 'Line Chart', icon: TrendingUp },
    { value: 'bar', label: 'Bar Chart', icon: BarChart3 },
    { value: 'area', label: 'Area Chart', icon: TrendingUp }
  ];

  useEffect(() => {
    fetchAnalyticsData();
    const interval = setInterval(fetchAnalyticsData, 60000); // Update every minute
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/analytics?range=${timeRange}`);
      const data = await response.json();
      setAnalyticsData(data);
    } catch (error) {
      console.error('Error fetching analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getChartData = () => {
    if (!analyticsData?.chart_data) return [];
    
    const { dates, people_count, helmet_violations, face_cover_violations, loitering_events, posture_violations } = analyticsData.chart_data;
    
    return dates.map((date, index) => ({
      date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      fullDate: date,
      people: people_count[index] || 0,
      helmet: helmet_violations[index] || 0,
      faceCover: face_cover_violations[index] || 0,
      loitering: loitering_events[index] || 0,
      posture: posture_violations[index] || 0,
      total: (helmet_violations[index] || 0) + (face_cover_violations[index] || 0) + 
             (loitering_events[index] || 0) + (posture_violations[index] || 0)
    }));
  };

  const getPieChartData = () => {
    if (!analyticsData?.totals) return [];
    
    const { total_helmet_violations, total_face_cover_violations, total_loitering_events, total_posture_violations } = analyticsData.totals;
    
    return [
      { name: 'Helmet Violations', value: total_helmet_violations, color: '#f56565' },
      { name: 'Face Cover Violations', value: total_face_cover_violations, color: '#ed8936' },
      { name: 'Loitering Events', value: total_loitering_events, color: '#9f7aea' },
      { name: 'Posture Violations', value: total_posture_violations, color: '#38b2ac' }
    ];
  };

  const getKPIStats = () => {
    if (!analyticsData?.totals) return [];
    
    const { total_people, total_helmet_violations, total_face_cover_violations, total_loitering_events, total_posture_violations } = analyticsData.totals;
    
    return [
      {
        title: 'Total People Detected',
        value: total_people,
        icon: Users,
        color: '#667eea',
        change: '+12%',
        trend: 'up'
      },
      {
        title: 'Security Violations',
        value: total_helmet_violations + total_face_cover_violations + total_loitering_events + total_posture_violations,
        icon: AlertTriangle,
        color: '#f56565',
        change: '+8%',
        trend: 'up'
      },
      {
        title: 'Detection Accuracy',
        value: '94.5%',
        icon: Shield,
        color: '#48bb78',
        change: '+2.1%',
        trend: 'up'
      },
      {
        title: 'System Uptime',
        value: '99.9%',
        icon: Activity,
        color: '#ed8936',
        change: '+0.1%',
        trend: 'up'
      }
    ];
  };

  const getDetectionModulesData = () => {
    return [
      { name: 'People Detection', accuracy: 96, violations: 12, icon: Users, color: '#667eea' },
      { name: 'Helmet Detection', accuracy: 94, violations: 8, icon: Shield, color: '#f56565' },
      { name: 'Face Cover Detection', accuracy: 92, violations: 15, icon: Eye, color: '#ed8936' },
      { name: 'Loitering Detection', accuracy: 89, violations: 6, icon: Clock, color: '#9f7aea' },
      { name: 'Posture Detection', accuracy: 91, violations: 9, icon: Activity, color: '#38b2ac' }
    ];
  };

  const renderChart = () => {
    const data = getChartData();
    
    if (chartType === 'line') {
      return (
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="people" stroke="#667eea" strokeWidth={3} name="People Count" />
          <Line type="monotone" dataKey="helmet" stroke="#f56565" strokeWidth={2} name="Helmet Violations" />
          <Line type="monotone" dataKey="faceCover" stroke="#ed8936" strokeWidth={2} name="Face Cover Violations" />
          <Line type="monotone" dataKey="loitering" stroke="#9f7aea" strokeWidth={2} name="Loitering Events" />
          <Line type="monotone" dataKey="posture" stroke="#38b2ac" strokeWidth={2} name="Posture Violations" />
        </LineChart>
      );
    } else if (chartType === 'bar') {
      return (
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="people" fill="#667eea" name="People Count" />
          <Bar dataKey="helmet" fill="#f56565" name="Helmet Violations" />
          <Bar dataKey="faceCover" fill="#ed8936" name="Face Cover Violations" />
          <Bar dataKey="loitering" fill="#9f7aea" name="Loitering Events" />
          <Bar dataKey="posture" fill="#38b2ac" name="Posture Violations" />
        </BarChart>
      );
    } else {
      return (
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Area type="monotone" dataKey="people" stackId="1" stroke="#667eea" fill="#667eea" fillOpacity={0.6} name="People Count" />
          <Area type="monotone" dataKey="helmet" stackId="2" stroke="#f56565" fill="#f56565" fillOpacity={0.6} name="Helmet Violations" />
          <Area type="monotone" dataKey="faceCover" stackId="2" stroke="#ed8936" fill="#ed8936" fillOpacity={0.6} name="Face Cover Violations" />
          <Area type="monotone" dataKey="loitering" stackId="2" stroke="#9f7aea" fill="#9f7aea" fillOpacity={0.6} name="Loitering Events" />
          <Area type="monotone" dataKey="posture" stackId="2" stroke="#38b2ac" fill="#38b2ac" fillOpacity={0.6} name="Posture Violations" />
        </AreaChart>
      );
    }
  };

  const exportData = () => {
    const data = getChartData();
    const csvContent = [
      ['Date', 'People Count', 'Helmet Violations', 'Face Cover Violations', 'Loitering Events', 'Posture Violations'],
      ...data.map(row => [
        row.fullDate,
        row.people,
        row.helmet,
        row.faceCover,
        row.loitering,
        row.posture
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-${timeRange}-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="analytics-loading">
        <div className="loading-spinner"></div>
        <p>Loading analytics data...</p>
      </div>
    );
  }

  return (
    <div className="analytics">
      <div className="analytics-header">
        <div className="header-content">
          <h1>Analytics Dashboard</h1>
          <p>Comprehensive insights and performance metrics</p>
        </div>
        <div className="header-actions">
          <button className="action-btn" onClick={fetchAnalyticsData} disabled={loading}>
            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
            Refresh
          </button>
          <button className="action-btn primary" onClick={exportData}>
            <Download size={16} />
            Export
          </button>
        </div>
      </div>

      <div className="analytics-controls">
        <div className="control-group">
          <label>Time Range</label>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="control-select"
          >
            {timeRanges.map(range => (
              <option key={range.value} value={range.value}>
                {range.label}
              </option>
            ))}
          </select>
        </div>
        
        <div className="control-group">
          <label>Chart Type</label>
          <div className="chart-type-selector">
            {chartTypes.map(type => {
              const Icon = type.icon;
              return (
                <button
                  key={type.value}
                  className={`chart-type-btn ${chartType === type.value ? 'active' : ''}`}
                  onClick={() => setChartType(type.value)}
                >
                  <Icon size={16} />
                  {type.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      <div className="kpi-grid">
        {getKPIStats().map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="kpi-card">
              <div className="kpi-header">
                <div className="kpi-icon" style={{ backgroundColor: stat.color }}>
                  <Icon size={20} />
                </div>
                <div className="kpi-trend">
                  <span className={`trend ${stat.trend}`}>
                    {stat.trend === 'up' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                    {stat.change}
                  </span>
                </div>
              </div>
              <div className="kpi-content">
                <h3 className="kpi-value">{stat.value}</h3>
                <p className="kpi-title">{stat.title}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="charts-grid">
        <div className="chart-container main-chart">
          <div className="chart-header">
            <h3>Detection Trends</h3>
            <div className="chart-legend">
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#667eea' }}></div>
                <span>People Count</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#f56565' }}></div>
                <span>Violations</span>
              </div>
            </div>
          </div>
          <div className="chart-content">
            <ResponsiveContainer width="100%" height={400}>
              {renderChart()}
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-container pie-chart">
          <div className="chart-header">
            <h3>Violation Distribution</h3>
            <PieChartIcon size={20} />
          </div>
          <div className="chart-content">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={getPieChartData()}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {getPieChartData().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="modules-performance">
        <h3>Detection Modules Performance</h3>
        <div className="modules-grid">
          {getDetectionModulesData().map((module, index) => {
            const Icon = module.icon;
            return (
              <div key={index} className="module-performance-card">
                <div className="module-header">
                  <div className="module-icon" style={{ backgroundColor: module.color }}>
                    <Icon size={20} />
                  </div>
                  <div className="module-stats">
                    <span className="accuracy">{module.accuracy}%</span>
                    <span className="violations">{module.violations} violations</span>
                  </div>
                </div>
                <div className="module-content">
                  <h4 className="module-name">{module.name}</h4>
                  <div className="performance-bar">
                    <div 
                      className="performance-fill"
                      style={{ 
                        width: `${module.accuracy}%`,
                        backgroundColor: module.color
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="insights-section">
        <h3>Key Insights</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-icon">
              <AlertTriangle size={24} />
            </div>
            <div className="insight-content">
              <h4>Peak Alert Hours</h4>
              <p>Most security violations occur between 2:00 PM - 6:00 PM during business hours.</p>
            </div>
          </div>
          
          <div className="insight-card">
            <div className="insight-icon">
              <Shield size={24} />
            </div>
            <div className="insight-content">
              <h4>Detection Accuracy</h4>
              <p>Overall system accuracy is 94.5% with people detection performing best at 96%.</p>
            </div>
          </div>
          
          <div className="insight-card">
            <div className="insight-icon">
              <Users size={24} />
            </div>
            <div className="insight-content">
              <h4>Traffic Patterns</h4>
              <p>Average daily traffic shows 45% increase in people count during lunch hours.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
