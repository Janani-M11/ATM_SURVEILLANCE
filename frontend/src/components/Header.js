import React, { useState } from 'react';
import { LogOut, Bell, Settings, User, Search } from 'lucide-react';
import './Header.css';

const Header = ({ user, onLogout }) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  const notifications = [
    { id: 1, message: 'Multiple people detected at ATM', time: '2 min ago', type: 'warning' },
    { id: 2, message: 'Helmet violation detected', time: '5 min ago', type: 'alert' },
    { id: 3, message: 'System health check completed', time: '10 min ago', type: 'info' }
  ];

  const handleLogout = () => {
    onLogout();
  };

  return (
    <header className="header">
      <div className="header-left">
        <div className="search-container">
          <Search className="search-icon" />
          <input
            type="text"
            placeholder="Search events, logs, or analytics..."
            className="search-input"
          />
        </div>
      </div>

      <div className="header-right">
        <div className="header-actions">
          <div className="notification-container">
            <button
              className="notification-button"
              onClick={() => setShowNotifications(!showNotifications)}
            >
              <Bell className="notification-icon" />
              {notifications.length > 0 && (
                <span className="notification-badge">{notifications.length}</span>
              )}
            </button>

            {showNotifications && (
              <div className="notification-dropdown">
                <div className="notification-header">
                  <h3>Notifications</h3>
                  <span className="notification-count">{notifications.length}</span>
                </div>
                <div className="notification-list">
                  {notifications.map((notification) => (
                    <div key={notification.id} className={`notification-item ${notification.type}`}>
                      <div className="notification-content">
                        <p className="notification-message">{notification.message}</p>
                        <span className="notification-time">{notification.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="profile-container">
            <button
              className="profile-button"
              onClick={() => setShowProfile(!showProfile)}
            >
              <User className="profile-icon" />
              <span className="profile-name">{user?.email || 'Admin'}</span>
            </button>

            {showProfile && (
              <div className="profile-dropdown">
                <div className="profile-info">
                  <div className="profile-avatar">
                    <User size={20} />
                  </div>
                  <div className="profile-details">
                    <p className="profile-email">{user?.email}</p>
                    <p className="profile-role">System Administrator</p>
                  </div>
                </div>
                <div className="profile-actions">
                  <button className="profile-action">
                    <Settings size={16} />
                    Settings
                  </button>
                  <button className="profile-action logout" onClick={handleLogout}>
                    <LogOut size={16} />
                    Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
