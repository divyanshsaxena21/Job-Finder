import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { preferencesAPI } from '../services/api'
import '../styles/preferences.css'

const JOB_TYPES = ['full_time', 'part_time', 'contract', 'freelance', 'internship']
const EXPERIENCE_LEVELS = ['entry', 'junior', 'mid', 'senior', 'lead']

export const Preferences = () => {
  const navigate = useNavigate()
  const [preferences, setPreferences] = useState({
    skills: [],
    roles: [],
    experience: '',
    location: [],
    job_type: [],
    min_salary: null,
    max_salary: null
  })

  const [newSkill, setNewSkill] = useState('')
  const [newRole, setNewRole] = useState('')
  const [newLocation, setNewLocation] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchPreferences()
  }, [])

  const fetchPreferences = async () => {
    try {
      const response = await preferencesAPI.get()
      setPreferences(response.data)
    } catch (err) {
      console.error('Failed to load preferences:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddSkill = () => {
    if (newSkill && !preferences.skills.includes(newSkill)) {
      setPreferences(prev => ({
        ...prev,
        skills: [...prev.skills, newSkill]
      }))
      setNewSkill('')
    }
  }

  const handleRemoveSkill = (skill) => {
    setPreferences(prev => ({
      ...prev,
      skills: prev.skills.filter(s => s !== skill)
    }))
  }

  const handleAddRole = () => {
    if (newRole && !preferences.roles.includes(newRole)) {
      setPreferences(prev => ({
        ...prev,
        roles: [...prev.roles, newRole]
      }))
      setNewRole('')
    }
  }

  const handleRemoveRole = (role) => {
    setPreferences(prev => ({
      ...prev,
      roles: prev.roles.filter(r => r !== role)
    }))
  }

  const handleAddLocation = () => {
    if (newLocation && !preferences.location.includes(newLocation)) {
      setPreferences(prev => ({
        ...prev,
        location: [...prev.location, newLocation]
      }))
      setNewLocation('')
    }
  }

  const handleRemoveLocation = (location) => {
    setPreferences(prev => ({
      ...prev,
      location: prev.location.filter(l => l !== location)
    }))
  }

  const handleJobTypeChange = (jobType) => {
    setPreferences(prev => ({
      ...prev,
      job_type: prev.job_type.includes(jobType)
        ? prev.job_type.filter(jt => jt !== jobType)
        : [...prev.job_type, jobType]
    }))
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setMessage('')
      
      await preferencesAPI.update(preferences)
      setMessage('✓ Preferences saved successfully!')
      
      setTimeout(() => setMessage(''), 3000)
    } catch (err) {
      setMessage('✗ Failed to save preferences')
      console.error(err)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="loading">Loading preferences...</div>

  return (
    <div className="preferences-page">
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
        <h1>Your Preferences</h1>
        <p className="subtitle">Customize your job search criteria</p>

        {message && <div className={`message ${message.includes('✓') ? 'success' : 'error'}`}>{message}</div>}

        <div className="preferences-form">
          {/* Skills Section */}
          <div className="form-section">
            <h3>Technical Skills</h3>
            <div className="input-group">
              <input
                type="text"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                placeholder="Add a skill (e.g., React, Python)"
                onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
              />
              <button onClick={handleAddSkill} className="btn-add">Add</button>
            </div>
            <div className="tags">
              {preferences.skills.map(skill => (
                <span key={skill} className="tag">
                  {skill}
                  <button onClick={() => handleRemoveSkill(skill)}>×</button>
                </span>
              ))}
            </div>
          </div>

          {/* Roles Section */}
          <div className="form-section">
            <h3>Target Roles</h3>
            <div className="input-group">
              <input
                type="text"
                value={newRole}
                onChange={(e) => setNewRole(e.target.value)}
                placeholder="Add a role (e.g., Frontend Developer)"
                onKeyPress={(e) => e.key === 'Enter' && handleAddRole()}
              />
              <button onClick={handleAddRole} className="btn-add">Add</button>
            </div>
            <div className="tags">
              {preferences.roles.map(role => (
                <span key={role} className="tag">
                  {role}
                  <button onClick={() => handleRemoveRole(role)}>×</button>
                </span>
              ))}
            </div>
          </div>

          {/* Experience Level */}
          <div className="form-section">
            <h3>Experience Level</h3>
            <select
              value={preferences.experience}
              onChange={(e) => setPreferences(prev => ({ ...prev, experience: e.target.value }))}
              className="select"
            >
              <option value="">Select experience level</option>
              {EXPERIENCE_LEVELS.map(level => (
                <option key={level} value={level}>{level.charAt(0).toUpperCase() + level.slice(1)}</option>
              ))}
            </select>
          </div>

          {/* Locations Section */}
          <div className="form-section">
            <h3>Preferred Locations</h3>
            <div className="input-group">
              <input
                type="text"
                value={newLocation}
                onChange={(e) => setNewLocation(e.target.value)}
                placeholder="Add a location (e.g., Remote, San Francisco)"
                onKeyPress={(e) => e.key === 'Enter' && handleAddLocation()}
              />
              <button onClick={handleAddLocation} className="btn-add">Add</button>
            </div>
            <div className="tags">
              {preferences.location.map(location => (
                <span key={location} className="tag">
                  {location}
                  <button onClick={() => handleRemoveLocation(location)}>×</button>
                </span>
              ))}
            </div>
          </div>

          {/* Job Types */}
          <div className="form-section">
            <h3>Job Types</h3>
            <div className="checkbox-group">
              {JOB_TYPES.map(jobType => (
                <label key={jobType} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={preferences.job_type.includes(jobType)}
                    onChange={() => handleJobTypeChange(jobType)}
                  />
                  {jobType.replace('_', ' ').toUpperCase()}
                </label>
              ))}
            </div>
          </div>

          {/* Salary Range */}
          <div className="form-section">
            <h3>Salary Range (Optional)</h3>
            <div className="salary-group">
              <div className="salary-input">
                <label>Minimum Salary</label>
                <input
                  type="number"
                  value={preferences.min_salary || ''}
                  onChange={(e) => setPreferences(prev => ({ ...prev, min_salary: e.target.value ? parseInt(e.target.value) : null }))}
                  placeholder="e.g., 50000"
                />
              </div>
              <div className="salary-input">
                <label>Maximum Salary</label>
                <input
                  type="number"
                  value={preferences.max_salary || ''}
                  onChange={(e) => setPreferences(prev => ({ ...prev, max_salary: e.target.value ? parseInt(e.target.value) : null }))}
                  placeholder="e.g., 120000"
                />
              </div>
            </div>
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="btn btn-primary btn-save"
          >
            {saving ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>
      </div>
    </div>
  )
}
