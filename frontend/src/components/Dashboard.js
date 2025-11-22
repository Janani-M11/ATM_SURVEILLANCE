import React, { useState, useEffect } from 'react';
import { 
  Users, 
  AlertTriangle, 
  Shield, 
  Activity, 
  Camera, 
  FileText,
  TrendingUp,
  Clock,
  Eye,
  Zap
} from 'lucide-react';
import './Dashboard.css';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalPeople: 0,
    activeAlerts: 0,
    systemStatus: 'Online',
    detectionAccuracy: 0
  });

  const [recentEvents, setRecentEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [analyticsResponse, logsResponse] = await Promise.all([
        fetch('/api/analytics'),
        fetch('/api/event-logs?per_page=5')
      ]);

      const analyticsData = await analyticsResponse.json();
      const logsData = await logsResponse.json();

      setStats({
        totalPeople: analyticsData.totals?.total_people || 0,
        activeAlerts: analyticsData.totals?.total_helmet_violations + 
                     analyticsData.totals?.total_face_cover_violations + 
                     analyticsData.totals?.total_loitering_events + 
                     analyticsData.totals?.total_posture_violations || 0,
        systemStatus: 'Online',
        detectionAccuracy: 94.5
      });

      setRecentEvents(logsData.logs || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const statCards = [
    {
      title: 'People Detected',
      value: stats.totalPeople,
      icon: Users,
      color: '#667eea',
      change: '+12%',
      trend: 'up'
    },
    {
      title: 'Active Alerts',
      value: stats.activeAlerts,
      icon: AlertTriangle,
      color: '#f56565',
      change: '+3',
      trend: 'up'
    },
    {
      title: 'System Status',
      value: stats.systemStatus,
      icon: Shield,
      color: '#48bb78',
      change: '100%',
      trend: 'stable'
    },
    {
      title: 'Detection Accuracy',
      value: `${stats.detectionAccuracy}%`,
      icon: Activity,
      color: '#ed8936',
      change: '+2.1%',
      trend: 'up'
    }
  ];

  const quickActions = [
    {
      title: 'Start Detection',
      description: 'Begin real-time monitoring',
      icon: Camera,
      color: '#667eea',
      path: '/detection'
    },
    {
      title: 'View Logs',
      description: 'Check recent events',
      icon: FileText,
      color: '#48bb78',
      path: '/logs'
    },
    {
      title: 'Analytics',
      description: 'View detailed reports',
      icon: TrendingUp,
      color: '#ed8936',
      path: '/analytics'
    }
  ];

  const detectionModules = [
    {
      name: 'People Detection',
      status: 'Active',
      accuracy: '96%',
      description: 'Monitors multiple people (threshold > 2)',
      icon: Users,
      color: '#667eea'
    },
    {
      name: 'Helmet Detection',
      status: 'Active',
      accuracy: '94%',
      description: 'Detects helmet violations',
      icon: Shield,
      color: '#f56565'
    },
    {
      name: 'Face Cover Detection',
      status: 'Active',
      accuracy: '92%',
      description: 'Detects masks, scarves, and face coverings',
      icon: Eye,
      color: '#ed8936'
    },
    {
      name: 'Loitering Detection',
      status: 'Active',
      accuracy: '89%',
      description: 'Monitors loitering behavior',
      icon: Clock,
      color: '#9f7aea'
    },
    {
      name: 'Posture Detection',
      status: 'Active',
      accuracy: '91%',
      description: 'Detects improper posture (bending)',
      icon: Activity,
      color: '#38b2ac'
    }
  ];

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>ATM Surveillance Dashboard</h1>
        <p>Real-time security monitoring and threat detection</p>
      </div>

      <div className="stats-grid">
        {statCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <div key={index} className="stat-card">
              <div className="stat-card-header">
                <div className="stat-icon" style={{ backgroundColor: card.color }}>
                  <Icon size={24} />
                </div>
                <div className="stat-trend">
                  <span className={`trend ${card.trend}`}>{card.change}</span>
                </div>
              </div>
              <div className="stat-content">
                <h3 className="stat-value">{card.value}</h3>
                <p className="stat-title">{card.title}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="dashboard-content">
        <div className="content-left">
          <div className="recent-events">
            <div className="section-header">
              <h2>Recent Events</h2>
              <button className="view-all-btn">View All</button>
            </div>
            <div className="events-list">
              {recentEvents.length > 0 ? (
                recentEvents.map((event, index) => (
                  <div key={index} className="event-item">
                    <div className="event-icon">
                      <AlertTriangle size={16} />
                    </div>
                    <div className="event-content">
                      <p className="event-description">{event.description}</p>
                      <span className="event-time">
                        {new Date(event.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <div className="event-confidence">
                      {Math.round(event.confidence * 100)}%
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-events">
                  <p>No recent events</p>
                </div>
              )}
            </div>
          </div>

          <div className="detection-modules">
            <div className="section-header">
              <h2>Detection Modules</h2>
              <div className="module-status">
                <div className="status-indicator active"></div>
                <span>All Active</span>
              </div>
            </div>
            <div className="modules-grid">
              {detectionModules.map((module, index) => {
                const Icon = module.icon;
                return (
                  <div key={index} className="module-card">
                    <div className="module-header">
                      <div className="module-icon" style={{ backgroundColor: module.color }}>
                        <Icon size={20} />
                      </div>
                      <div className="module-status-badge active">
                        {module.status}
                      </div>
                    </div>
                    <div className="module-content">
                      <h3 className="module-name">{module.name}</h3>
                      <p className="module-description">{module.description}</p>
                      <div className="module-accuracy">
                        <span>Accuracy: {module.accuracy}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="content-right">
          <div className="quick-actions">
            <div className="section-header">
              <h2>Quick Actions</h2>
            </div>
            <div className="actions-list">
              {quickActions.map((action, index) => {
                const Icon = action.icon;
                return (
                  <button key={index} className="action-button">
                    <div className="action-icon" style={{ backgroundColor: action.color }}>
                      <Icon size={20} />
                    </div>
                    <div className="action-content">
                      <h3 className="action-title">{action.title}</h3>
                      <p className="action-description">{action.description}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="system-health">
            <div className="section-header">
              <h2>System Health</h2>
            </div>
            <div className="health-metrics">
              <div className="health-metric">
                <div className="metric-label">CPU Usage</div>
                <div className="metric-bar">
                  <div className="metric-fill" style={{ width: '65%' }}></div>
                </div>
                <span className="metric-value">65%</span>
              </div>
              <div className="health-metric">
                <div className="metric-label">Memory Usage</div>
                <div className="metric-bar">
                  <div className="metric-fill" style={{ width: '78%' }}></div>
                </div>
                <span className="metric-value">78%</span>
              </div>
              <div className="health-metric">
                <div className="metric-label">Storage</div>
                <div className="metric-bar">
                  <div className="metric-fill" style={{ width: '45%' }}></div>
                </div>
                <span className="metric-value">45%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
