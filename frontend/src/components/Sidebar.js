import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  Camera, 
  FileText, 
  BarChart3, 
  Shield,
  Users,
  AlertTriangle,
  Activity
} from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
  const menuItems = [
    {
      path: '/',
      icon: Home,
      label: 'Dashboard',
      description: 'Overview & Summary'
    },
    {
      path: '/detection',
      icon: Camera,
      label: 'Detection Module',
      description: 'Real-time Monitoring'
    },
    {
      path: '/logs',
      icon: FileText,
      label: 'Event Logs',
      description: 'Security Events'
    },
    {
      path: '/analytics',
      icon: BarChart3,
      label: 'Analytics',
      description: 'Reports & Insights'
    }
  ];

  const stats = [
    { icon: Users, label: 'People Detected', value: '12', color: '#667eea' },
    { icon: AlertTriangle, label: 'Active Alerts', value: '3', color: '#f56565' },
    { icon: Activity, label: 'System Status', value: 'Online', color: '#48bb78' }
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Shield className="logo-icon" />
          <div className="logo-text">
            <h2>ATM Security</h2>
            <p>Surveillance System</p>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `nav-item ${isActive ? 'active' : ''}`
              }
            >
              <Icon className="nav-icon" />
              <div className="nav-content">
                <span className="nav-label">{item.label}</span>
                <span className="nav-description">{item.description}</span>
              </div>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-stats">
        <h3 className="stats-title">Quick Stats</h3>
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="stat-item">
              <div className="stat-icon" style={{ backgroundColor: stat.color }}>
                <Icon size={16} />
              </div>
              <div className="stat-content">
                <span className="stat-value">{stat.value}</span>
                <span className="stat-label">{stat.label}</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="sidebar-footer">
        <div className="system-status">
          <div className="status-indicator online"></div>
          <span>System Online</span>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
