import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/auto-apply-settings.css';

const AutoApplySettings = () => {
  // Auto-apply settings component for managing job application automation
  const [preferences, setPreferences] = useState({
    github_username: '',
    auto_apply_enabled: false,
    auto_apply_frequency: 'daily',
    include_github_projects: true,
    max_daily_applications: 5,
  });

  const [autoApplyStats, setAutoApplyStats] = useState({
    total_runs: 0,
    total_applied: 0,
    total_skipped: 0,
    total_failed: 0,
    average_applied_per_run: 0,
    success_rate: 0,
  });

  const [schedulerStatus, setSchedulerStatus] = useState({
    scheduler_running: false,
    auto_apply_enabled: false,
    next_scheduled_run: null,
  });

  const [autoApplyHistory, setAutoApplyHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('settings');

  const navigate = useNavigate();
  const API_BASE_URL = import.meta.env.VITE_API_URL;
  
  if (!API_BASE_URL) {
    console.error('VITE_API_URL environment variable not set');
  }

  useEffect(() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/login');
      return;
    }

    fetchData();
  }, []);

  const fetchData = async () => {
    const token = localStorage.getItem('access_token');
    try {
      setLoading(true);

      // Fetch preferences
      const prefsRes = await axios.get(`${API_BASE_URL}/preferences`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      if (prefsRes.data) {
        setPreferences({
          github_username: prefsRes.data.github_username || '',
          auto_apply_enabled: prefsRes.data.auto_apply_enabled || false,
          auto_apply_frequency: prefsRes.data.auto_apply_frequency || 'daily',
          include_github_projects: prefsRes.data.include_github_projects !== false,
          max_daily_applications: prefsRes.data.max_daily_applications || 5,
        });
      }

      // Fetch stats
      try {
        const statsRes = await axios.get(`${API_BASE_URL}/auto-apply/stats`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setAutoApplyStats(statsRes.data);
      } catch (e) {
        console.log('Stats not available yet');
      }

      // Fetch scheduler status
      try {
        const statusRes = await axios.get(`${API_BASE_URL}/auto-apply/status`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setSchedulerStatus(statusRes.data);
      } catch (e) {
        console.log('Scheduler status not available');
      }

      // Fetch history
      try {
        const historyRes = await axios.get(`${API_BASE_URL}/auto-apply/history?limit=10`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setAutoApplyHistory(historyRes.data.runs || []);
      } catch (e) {
        console.log('History not available yet');
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setMessage('Error loading settings');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setPreferences((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSavePreferences = async () => {
    const token = localStorage.getItem('token');
    try {
      setSaving(true);
      const updateData = {
        github_username: preferences.github_username,
        auto_apply_enabled: preferences.auto_apply_enabled,
        auto_apply_frequency: preferences.auto_apply_frequency,
        include_github_projects: preferences.include_github_projects,
        max_daily_applications: parseInt(preferences.max_daily_applications),
      };

      await axios.put(`${API_BASE_URL}/preferences`, updateData, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setMessage('✓ Preferences saved successfully');
      setTimeout(() => setMessage(''), 3000);
      
      // Refresh status
      fetchData();
    } catch (error) {
      console.error('Error saving preferences:', error);
      setMessage('✗ Error saving preferences');
    } finally {
      setSaving(false);
    }
  };

  const handleTriggerAutoApply = async () => {
    const token = localStorage.getItem('token');
    try {
      setTriggering(true);
      const response = await axios.post(`${API_BASE_URL}/auto-apply/trigger`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setMessage(
        `✓ Auto-apply completed! Applied to ${response.data.jobs_applied} jobs`
      );
      setTimeout(() => setMessage(''), 5000);
      
      // Refresh data
      fetchData();
    } catch (error) {
      console.error('Error triggering auto-apply:', error);
      const errorMsg = error.response?.data?.detail || 'Error triggering auto-apply';
      setMessage(`✗ ${errorMsg}`);
    } finally {
      setTriggering(false);
    }
  };

  if (loading) {
    return <div className="auto-apply-container loading">Loading...</div>;
  }

  return (
    <div className="auto-apply-container">
      <button className="back-button" onClick={() => navigate('/dashboard')}>
        ← Back to Dashboard
      </button>

      <div className="auto-apply-header">
        <h1>🤖 Auto-Apply Settings</h1>
        <p>Automate your job applications with AI-powered customization</p>
      </div>

      {message && <div className={`message ${message.includes('✓') ? 'success' : 'error'}`}>{message}</div>}

      <div className="auto-apply-tabs">
        <button
          className={`tab-button ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
        <button
          className={`tab-button ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => setActiveTab('stats')}
        >
          📊 Statistics
        </button>
        <button
          className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          📋 History
        </button>
      </div>

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <div className="tab-content">
          <div className="settings-section">
            <h2>Enable Auto-Apply</h2>
            <div className="setting-group">
              <label>
                <input
                  type="checkbox"
                  name="auto_apply_enabled"
                  checked={preferences.auto_apply_enabled}
                  onChange={handleInputChange}
                />
                Enable automatic job applications
              </label>
              <p className="helper-text">
                When enabled, the system will automatically apply to matching jobs daily
              </p>
            </div>
          </div>

          {preferences.auto_apply_enabled && (
            <>
              <div className="scheduler-status">
                <h3>Scheduler Status</h3>
                <div className="status-info">
                  <p>
                    <strong>Status:</strong>{' '}
                    <span className={schedulerStatus.scheduler_running ? 'active' : 'inactive'}>
                      {schedulerStatus.scheduler_running ? '🟢 Active' : '🔴 Inactive'}
                    </span>
                  </p>
                  <p>
                    <strong>Next Run:</strong>{' '}
                    {schedulerStatus.next_scheduled_run
                      ? new Date(schedulerStatus.next_scheduled_run).toLocaleString()
                      : '9:00 AM UTC (Daily)'}
                  </p>
                </div>
              </div>

              <div className="settings-section">
                <h2>GitHub Profile</h2>
                <div className="setting-group">
                  <label>GitHub Username</label>
                  <input
                    type="text"
                    name="github_username"
                    placeholder="your-github-username"
                    value={preferences.github_username}
                    onChange={handleInputChange}
                  />
                  <p className="helper-text">
                    Your GitHub projects will be fetched and added to your resume
                  </p>
                </div>
              </div>

              <div className="settings-section">
                <h2>Application Preferences</h2>
                
                <div className="setting-group">
                  <label>Auto-Apply Frequency</label>
                  <select
                    name="auto_apply_frequency"
                    value={preferences.auto_apply_frequency}
                    onChange={handleInputChange}
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="bi-weekly">Bi-weekly</option>
                  </select>
                </div>

                <div className="setting-group">
                  <label>Max Applications per Day</label>
                  <input
                    type="number"
                    name="max_daily_applications"
                    min="1"
                    max="50"
                    value={preferences.max_daily_applications}
                    onChange={handleInputChange}
                  />
                  <p className="helper-text">Safety limit to prevent over-applying</p>
                </div>

                <div className="setting-group">
                  <label>
                    <input
                      type="checkbox"
                      name="include_github_projects"
                      checked={preferences.include_github_projects}
                      onChange={handleInputChange}
                    />
                    Include GitHub projects in customized resume
                  </label>
                </div>
              </div>

              <div className="button-group">
                <button
                  className="btn btn-primary"
                  onClick={handleSavePreferences}
                  disabled={saving}
                >
                  {saving ? 'Saving...' : '💾 Save Preferences'}
                </button>
                <button
                  className="btn btn-success"
                  onClick={handleTriggerAutoApply}
                  disabled={triggering || !preferences.auto_apply_enabled}
                >
                  {triggering ? 'Processing...' : '🚀 Trigger Now'}
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* Statistics Tab */}
      {activeTab === 'stats' && (
        <div className="tab-content">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{autoApplyStats.total_runs}</div>
              <div className="stat-label">Total Runs</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{autoApplyStats.total_applied}</div>
              <div className="stat-label">Total Applied</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{autoApplyStats.total_skipped}</div>
              <div className="stat-label">Total Skipped</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{autoApplyStats.total_failed}</div>
              <div className="stat-label">Total Failed</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{autoApplyStats.average_applied_per_run.toFixed(1)}</div>
              <div className="stat-label">Avg Applied/Run</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{autoApplyStats.success_rate.toFixed(1)}%</div>
              <div className="stat-label">Success Rate</div>
            </div>
          </div>
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="tab-content">
          {autoApplyHistory.length === 0 ? (
            <div className="empty-state">
              <p>No auto-apply runs yet. Enable auto-apply and trigger a run.</p>
            </div>
          ) : (
            <div className="history-list">
              {autoApplyHistory.map((run) => (
                <div key={run._id} className="history-item">
                  <div className="history-header">
                    <div className="history-date">
                      {new Date(run.started_at).toLocaleString()}
                    </div>
                    <div className="history-status">
                      Applied: <strong>{run.jobs_applied}</strong> | Skipped:{' '}
                      <strong>{run.jobs_skipped}</strong> | Failed:{' '}
                      <strong>{run.jobs_failed}</strong>
                    </div>
                  </div>
                  <div className="history-duration">
                    Duration:{' '}
                    {run.completed_at
                      ? `${(new Date(run.completed_at) - new Date(run.started_at)) / 1000}s`
                      : 'In progress...'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AutoApplySettings;
