import React, { useState, useEffect, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import { jobsAPI } from '../services/api'
import '../styles/dashboard.css'

export const Dashboard = () => {
  const navigate = useNavigate()
  const { user, logout } = useContext(AuthContext)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchJobs()
  }, [filter])

  const fetchJobs = async () => {
    try {
      setLoading(true)
      const response = await jobsAPI.getAll()
      setJobs(response.data)
    } catch (err) {
      setError('Failed to load jobs')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const filteredJobs = jobs.filter(job => {
    if (filter === 'matched') return job.match_score >= 60
    if (filter === 'applied') return job.status === 'applied'
    return true
  })

  return (
    <div className="dashboard">
      <nav className="navbar">
        <div className="nav-left">
          <h1>Job Finder</h1>
          <ul className="nav-links">
            <li><a href="/dashboard" className="active">Dashboard</a></li>
            <li><a href="/resume">My Resume</a></li>
            <li><a href="/applications">Applications</a></li>
            <li><a href="/auto-apply">🤖 Auto-Apply</a></li>
            <li><a href="/preferences">Preferences</a></li>
          </ul>
        </div>
        
        <div className="nav-right">
          <span className="user-name">{user?.name}</span>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </nav>

      <div className="dashboard-container">
        <div className="dashboard-header">
          <h2>Job Opportunities</h2>
          <button onClick={() => navigate('/add-job')} className="btn btn-primary">
            Add Job Manually
          </button>
        </div>

        <div className="filter-section">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All Jobs ({jobs.length})
          </button>
          <button
            className={`filter-btn ${filter === 'matched' ? 'active' : ''}`}
            onClick={() => setFilter('matched')}
          >
            Good Matches ({jobs.filter(j => j.match_score >= 60).length})
          </button>
          <button
            className={`filter-btn ${filter === 'applied' ? 'active' : ''}`}
            onClick={() => setFilter('applied')}
          >
            Applied ({jobs.filter(j => j.status === 'applied').length})
          </button>
        </div>

        {loading && <p className="loading">Loading jobs...</p>}
        {error && <p className="error">{error}</p>}

        {!loading && filteredJobs.length === 0 ? (
          <p className="no-jobs">No jobs found. Add a job to get started!</p>
        ) : (
          <div className="jobs-grid">
            {filteredJobs.map(job => (
              <div key={job.id} className="job-card">
                <div className="job-header">
                  <div>
                    <h3>{job.title}</h3>
                    <p className="company">{job.company}</p>
                  </div>
                  {job.match_score && (
                    <span className={`match-badge ${job.match_score >= 70 ? 'high' : job.match_score >= 50 ? 'medium' : 'low'}`}>
                      {Math.round(job.match_score)}%
                    </span>
                  )}
                </div>

                <p className="location">{job.location || 'Remote'}</p>
                <p className="description-preview">{job.description.substring(0, 100)}...</p>

                <div className="job-footer">
                  <button
                    className="btn btn-secondary"
                    onClick={() => navigate(`/job/${job.id}`)}
                  >
                    View Details
                  </button>
                  <span className={`status-badge ${job.status}`}>{job.status}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
