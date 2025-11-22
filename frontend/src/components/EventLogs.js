import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  Download, 
  RefreshCw, 
  AlertTriangle, 
  Users, 
  Shield, 
  Eye, 
  Clock, 
  Activity,
  Calendar,
  Clock as TimeIcon
} from 'lucide-react';
import './EventLogs.css';

const EventLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [sortBy, setSortBy] = useState('timestamp');
  const [sortOrder, setSortOrder] = useState('desc');

  const eventTypes = [
    { value: 'all', label: 'All Events', icon: AlertTriangle, color: '#667eea' },
    { value: 'people_count', label: 'People Detection', icon: Users, color: '#667eea' },
    { value: 'helmet', label: 'Helmet Violation', icon: Shield, color: '#f56565' },
    { value: 'face_cover', label: 'Face Cover', icon: Eye, color: '#ed8936' },
    { value: 'loitering', label: 'Loitering', icon: Clock, color: '#9f7aea' },
    { value: 'posture', label: 'Posture', icon: Activity, color: '#38b2ac' }
  ];

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [currentPage, searchTerm, filterType, sortBy, sortOrder]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: currentPage,
        per_page: 20,
        search: searchTerm,
        filter: filterType,
        sort_by: sortBy,
        sort_order: sortOrder
      });

      const response = await fetch(`/api/event-logs?${params}`);
      const data = await response.json();
      
      setLogs(data.logs || []);
      setTotalPages(data.pages || 1);
    } catch (error) {
      console.error('Error fetching logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  const handleFilterChange = (type) => {
    setFilterType(type);
    setCurrentPage(1);
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const getEventIcon = (eventType) => {
    const eventTypeConfig = eventTypes.find(type => type.value === eventType);
    return eventTypeConfig ? eventTypeConfig.icon : AlertTriangle;
  };

  const getEventColor = (eventType) => {
    const eventTypeConfig = eventTypes.find(type => type.value === eventType);
    return eventTypeConfig ? eventTypeConfig.color : '#667eea';
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString()
    };
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#48bb78';
    if (confidence >= 0.6) return '#ed8936';
    return '#f56565';
  };

  const exportLogs = () => {
    const csvContent = [
      ['Timestamp', 'Event Type', 'Description', 'Confidence'],
      ...logs.map(log => [
        new Date(log.timestamp).toLocaleString(),
        log.event_type,
        log.description,
        log.confidence
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `event-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const stats = {
    total: logs.length,
    today: logs.filter(log => {
      const logDate = new Date(log.timestamp);
      const today = new Date();
      return logDate.toDateString() === today.toDateString();
    }).length,
    highConfidence: logs.filter(log => log.confidence >= 0.8).length,
    alerts: logs.filter(log => ['helmet', 'face_cover', 'loitering', 'posture'].includes(log.event_type)).length
  };

  return (
    <div className="event-logs">
      <div className="logs-header">
        <div className="header-content">
          <h1>Event Logs</h1>
          <p>Security events and detection alerts</p>
        </div>
        <div className="header-actions">
          <button className="action-btn" onClick={fetchLogs} disabled={loading}>
            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
            Refresh
          </button>
          <button className="action-btn primary" onClick={exportLogs}>
            <Download size={16} />
            Export
          </button>
        </div>
      </div>

      <div className="logs-stats">
        <div className="stat-card">
          <div className="stat-icon">
            <AlertTriangle size={20} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats.total}</span>
            <span className="stat-label">Total Events</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <Calendar size={20} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats.today}</span>
            <span className="stat-label">Today</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <Shield size={20} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats.highConfidence}</span>
            <span className="stat-label">High Confidence</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <AlertTriangle size={20} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats.alerts}</span>
            <span className="stat-label">Alerts</span>
          </div>
        </div>
      </div>

      <div className="logs-controls">
        <div className="search-container">
          <Search className="search-icon" />
          <input
            type="text"
            placeholder="Search events..."
            value={searchTerm}
            onChange={handleSearch}
            className="search-input"
          />
        </div>

        <div className="filter-container">
          <Filter className="filter-icon" />
          <select
            value={filterType}
            onChange={(e) => handleFilterChange(e.target.value)}
            className="filter-select"
          >
            {eventTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="logs-table-container">
        <table className="logs-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('timestamp')} className="sortable">
                <div className="th-content">
                  <TimeIcon size={16} />
                  <span>Timestamp</span>
                  {sortBy === 'timestamp' && (
                    <span className="sort-indicator">
                      {sortOrder === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th onClick={() => handleSort('event_type')} className="sortable">
                <div className="th-content">
                  <span>Event Type</span>
                  {sortBy === 'event_type' && (
                    <span className="sort-indicator">
                      {sortOrder === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th>Description</th>
              <th onClick={() => handleSort('confidence')} className="sortable">
                <div className="th-content">
                  <span>Confidence</span>
                  {sortBy === 'confidence' && (
                    <span className="sort-indicator">
                      {sortOrder === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="5" className="loading-cell">
                  <div className="loading-spinner"></div>
                  <span>Loading events...</span>
                </td>
              </tr>
            ) : logs.length > 0 ? (
              logs.map((log, index) => {
                const Icon = getEventIcon(log.event_type);
                const color = getEventColor(log.event_type);
                const timestamp = formatTimestamp(log.timestamp);
                
                return (
                  <tr key={log.id} className="log-row">
                    <td className="timestamp-cell">
                      <div className="timestamp-content">
                        <span className="date">{timestamp.date}</span>
                        <span className="time">{timestamp.time}</span>
                      </div>
                    </td>
                    <td className="event-type-cell">
                      <div className="event-type-content">
                        <div className="event-icon" style={{ backgroundColor: color }}>
                          <Icon size={16} />
                        </div>
                        <span className="event-type-name">{log.event_type.replace('_', ' ')}</span>
                      </div>
                    </td>
                    <td className="description-cell">
                      <span className="description-text">{log.description}</span>
                    </td>
                    <td className="confidence-cell">
                      <div className="confidence-content">
                        <div 
                          className="confidence-bar"
                          style={{ 
                            width: `${log.confidence * 100}%`,
                            backgroundColor: getConfidenceColor(log.confidence)
                          }}
                        ></div>
                        <span 
                          className="confidence-value"
                          style={{ color: getConfidenceColor(log.confidence) }}
                        >
                          {Math.round(log.confidence * 100)}%
                        </span>
                      </div>
                    </td>
                    <td className="actions-cell">
                      <button className="action-btn small">
                        View Details
                      </button>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="5" className="empty-cell">
                  <div className="empty-state">
                    <AlertTriangle size={48} />
                    <p>No events found</p>
                    <span>Try adjusting your search or filter criteria</span>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="page-btn"
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
          >
            Previous
          </button>
          
          <div className="page-numbers">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const page = i + 1;
              return (
                <button
                  key={page}
                  className={`page-btn ${currentPage === page ? 'active' : ''}`}
                  onClick={() => setCurrentPage(page)}
                >
                  {page}
                </button>
              );
            })}
          </div>
          
          <button
            className="page-btn"
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default EventLogs;
