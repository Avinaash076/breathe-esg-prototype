import { useCallback, useEffect, useState } from 'react';
import { getDashboardStats } from '../api';
import './Dashboard.css';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      const response = await getDashboardStats();
      setStats(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch dashboard stats');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    Promise.resolve().then(fetchStats);
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, [fetchStats]);

  if (loading) return <div className="dashboard-container"><p>Loading...</p></div>;
  if (error) return <div className="dashboard-container error">{error}</div>;

  const formatStat = (label, pending, approved) => (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-row stat-pending">
        <span className="stat-number">{pending}</span>
        <span className="stat-text">Pending review</span>
      </div>
      <div className="stat-row stat-approved">
        <span className="stat-number">{approved}</span>
        <span className="stat-text">Approved</span>
      </div>
    </div>
  );

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">Review queue</p>
          <h1>ESG Data Ingestion Dashboard</h1>
          <p className="subtitle">
            Review incoming ESG source data before it moves into the audit trail.
          </p>
        </div>
      </header>

      <div className="stats-grid">
        {formatStat('SAP Procurement', stats.procurement_pending, stats.procurement_approved)}
        {formatStat('Utility Data', stats.utility_pending, stats.utility_approved)}
        {formatStat('Travel Data', stats.travel_pending, stats.travel_approved)}
      </div>

      <div className="dashboard-actions">
        <div className="action-card">
          <span className="action-kicker">Procurement</span>
          <h3>SAP Procurement</h3>
          <p>Upload and review procurement and fuel data from SAP.</p>
          <a href="/#/procurement" className="action-link">Review data</a>
        </div>

        <div className="action-card">
          <span className="action-kicker">Energy</span>
          <h3>Utility Electricity</h3>
          <p>Upload and review metered electricity consumption data.</p>
          <a href="/#/utility" className="action-link">Review data</a>
        </div>

        <div className="action-card">
          <span className="action-kicker">Travel</span>
          <h3>Travel Expenses</h3>
          <p>Upload and review corporate travel records.</p>
          <a href="/#/travel" className="action-link">Review data</a>
        </div>
      </div>
    </div>
  );
}
