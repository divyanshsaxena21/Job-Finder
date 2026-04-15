import React, { useState, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import { jobsAPI } from '../services/api'
import '../styles/auth.css'

export const AddJob = () => {
  const navigate = useNavigate()
  const { user } = useContext(AuthContext)
  const [title, setTitle] = useState('')
  const [company, setCompany] = useState('')
  const [location, setLocation] = useState('')
  const [description, setDescription] = useState('')
  const [salary, setSalary] = useState('')
  const [jobUrl, setJobUrl] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!title || !company || !description) {
      setError('Please fill in all required fields')
      return
    }

    try {
      setLoading(true)
      const jobData = {
        title,
        company,
        location: location || 'Remote',
        description,
        salary: salary ? parseInt(salary) : null,
        job_url: jobUrl || null,
        source: 'manual'
      }

      await jobsAPI.create(jobData)
      alert('Job added successfully!')
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add job')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card" style={{ maxWidth: '600px' }}>
        <button
          onClick={() => navigate('/dashboard')}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '20px',
            cursor: 'pointer',
            marginBottom: '10px'
          }}
        >
          ← Back
        </button>

        <h1>Job Finder</h1>
        <h2>Add Job Manually</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="title">Job Title *</label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              placeholder="e.g., Senior React Developer"
            />
          </div>

          <div className="form-group">
            <label htmlFor="company">Company *</label>
            <input
              id="company"
              type="text"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              required
              placeholder="e.g., TechCorp Inc"
            />
          </div>

          <div className="form-group">
            <label htmlFor="location">Location</label>
            <input
              id="location"
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., Remote, San Francisco, CA"
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Job Description *</label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              placeholder="Paste the job description here..."
              rows={6}
              style={{
                padding: '10px',
                fontFamily: 'inherit',
                borderRadius: '4px',
                border: '1px solid #ddd',
                fontSize: '14px'
              }}
            />
          </div>

          <div className="form-group">
            <label htmlFor="salary">Salary (Annual)</label>
            <input
              id="salary"
              type="number"
              value={salary}
              onChange={(e) => setSalary(e.target.value)}
              placeholder="e.g., 120000"
            />
          </div>

          <div className="form-group">
            <label htmlFor="jobUrl">Job URL</label>
            <input
              id="jobUrl"
              type="url"
              value={jobUrl}
              onChange={(e) => setJobUrl(e.target.value)}
              placeholder="https://example.com/jobs/123"
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Adding Job...' : 'Add Job'}
          </button>
        </form>

        <p style={{ marginTop: '20px', fontSize: '12px', color: '#666', textAlign: 'center' }}>
          * Required fields
        </p>
      </div>
    </div>
  )
}
