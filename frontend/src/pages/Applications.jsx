import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { applicationsAPI } from '../services/api'
import '../styles/applications.css'

export const Applications = () => {
  const navigate = useNavigate()
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchApplications()
  }, [filter])

  const fetchApplications = async () => {
    try {
      setLoading(true)
      const statusFilter = filter === 'all' ? null : filter
      const response = await applicationsAPI.getAll(statusFilter)
      setApplications(response.data)
    } catch (err) {
      console.error('Failed to load applications:', err)
    } finally {
      setLoading(false)
    }
  }

  const statusStats = {
    pending: applications.filter(a => a.status === 'pending').length,
    applied: applications.filter(a => a.status === 'applied').length,
    rejected: applications.filter(a => a.status === 'rejected').length
  }

  const filteredApps = filter === 'all'
    ? applications
    : applications.filter(a => a.status === filter)

  return (
    <div className="applications-page">
      <div className="container">
        <button
          onClick={() => navigate('/dashboard')}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '20px',
            cursor: 'pointer',
            marginBottom: '10px',
            color: '#667eea'
          }}
        >
          ← Back
        </button>
        <h1>Your Applications</h1>

        <div className="stats-section">
          <div className="stat-card">
            <h3>{statusStats.pending}</h3>
            <p>Pending Approval</p>
          </div>
          <div className="stat-card">
            <h3>{statusStats.applied}</h3>
            <p>Applied</p>
          </div>
          <div className="stat-card">
            <h3>{statusStats.rejected}</h3>
            <p>Rejected</p>
          </div>
        </div>

        <div className="filter-tabs">
          <button
            className={`tab ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button
            className={`tab ${filter === 'pending' ? 'active' : ''}`}
            onClick={() => setFilter('pending')}
          >
            Pending
          </button>
          <button
            className={`tab ${filter === 'applied' ? 'active' : ''}`}
            onClick={() => setFilter('applied')}
          >
            Applied
          </button>
          <button
            className={`tab ${filter === 'rejected' ? 'active' : ''}`}
            onClick={() => setFilter('rejected')}
          >
            Rejected
          </button>
        </div>

        {loading && <p className="loading">Loading applications...</p>}

        {!loading && filteredApps.length === 0 ? (
          <p className="no-data">No applications found</p>
        ) : (
          <div className="applications-list">
            {filteredApps.map(app => (
              <div key={app.id} className={`app-card app-${app.status}`}>
                <div className="app-header">
                  <div>
                    <h3>Application #{app.id.slice(0, 8)}</h3>
                    <p>{new Date(app.created_at).toLocaleDateString()}</p>
                  </div>
                  <span className={`status ${app.status}`}>{app.status}</span>
                </div>

                <div className="app-content">
                  <div className="resume-preview">
                    <h4>Resume Preview</h4>
                    <p>{app.resume.substring(0, 200)}...</p>
                  </div>

                  <div className="letter-preview">
                    <h4>Cover Letter Preview</h4>
                    <p>{app.cover_letter.substring(0, 200)}...</p>
                  </div>
                </div>

                {app.status === 'pending' && (
                  <p className="info">⏳ Waiting for your approval on Telegram</p>
                )}
                {app.status === 'applied' && app.submitted_at && (
                  <p className="info">✓ Submitted on {new Date(app.submitted_at).toLocaleDateString()}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
