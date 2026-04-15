import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { jobsAPI, applicationsAPI } from '../services/api'
import '../styles/job-detail.css'

export const JobDetail = () => {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const [job, setJob] = useState(null)
  const [resume, setResume] = useState('')
  const [coverLetter, setCoverLetter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [matching, setMatching] = useState(false)
  const [generatingResume, setGeneratingResume] = useState(false)
  const [generatingLetter, setGeneratingLetter] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchJobDetails()
  }, [jobId])

  const fetchJobDetails = async () => {
    try {
      setLoading(true)
      const response = await jobsAPI.getById(jobId)
      setJob(response.data)
    } catch (err) {
      setError('Failed to load job details')
    } finally {
      setLoading(false)
    }
  }

  const handleMatch = async () => {
    try {
      setMatching(true)
      const response = await jobsAPI.matchJob(jobId)
      const matchResult = response.data
      setJob(prev => ({
        ...prev,
        match_score: matchResult.match_score,
        match_reason: matchResult.reason,
        missing_skills: matchResult.missing_skills
      }))
    } catch (err) {
      setError('Failed to analyze job match')
    } finally {
      setMatching(false)
    }
  }

  const handleGenerateResume = async () => {
    try {
      setGeneratingResume(true)
      const response = await jobsAPI.generateResume(jobId)
      setResume(response.data.resume)
    } catch (err) {
      setError('Failed to generate resume')
    } finally {
      setGeneratingResume(false)
    }
  }

  const handleGenerateLetter = async () => {
    try {
      setGeneratingLetter(true)
      const response = await jobsAPI.generateCoverLetter(jobId)
      setCoverLetter(response.data.cover_letter)
    } catch (err) {
      setError('Failed to generate cover letter')
    } finally {
      setGeneratingLetter(false)
    }
  }

  const handleSubmit = async () => {
    if (!resume || !coverLetter) {
      setError('Please generate both resume and cover letter')
      return
    }

    try {
      setSubmitting(true)
      await applicationsAPI.submit(jobId, resume, coverLetter)
      alert('Application submitted! Check your Telegram for approval.')
      navigate('/applications')
    } catch (err) {
      setError('Failed to submit application')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div className="loading">Loading job details...</div>
  if (error) return <div className="error">{error}</div>
  if (!job) return <div className="error">Job not found</div>

  return (
    <div className="job-detail">
      <button className="back-btn" onClick={() => navigate('/dashboard')}>← Back</button>

      <div className="job-detail-container">
        <div className="job-main">
          <h1>{job.title}</h1>
          <p className="company">{job.company}</p>
          <p className="location">{job.location || 'Remote'}</p>

          <div className="match-section">
            {job.match_score ? (
              <div className="match-result">
                <div className={`match-score high`}>{Math.round(job.match_score)}%</div>
                <div className="match-details">
                  <p><strong>Match:</strong> {job.match_reason}</p>
                  {job.missing_skills && job.missing_skills.length > 0 && (
                    <p><strong>Missing Skills:</strong> {job.missing_skills.join(', ')}</p>
                  )}
                </div>
              </div>
            ) : (
              <button
                className="btn btn-primary"
                onClick={handleMatch}
                disabled={matching}
              >
                {matching ? 'Analyzing...' : 'Analyze Match'}
              </button>
            )}
          </div>

          <div className="job-description">
            <h3>Job Description</h3>
            <p>{job.description}</p>
          </div>
        </div>

        <div className="application-sidebar">
          <h3>Prepare Application</h3>

          <div className="section">
            <h4>Resume</h4>
            <button
              className="btn btn-secondary"
              onClick={handleGenerateResume}
              disabled={generatingResume}
            >
              {generatingResume ? 'Generating...' : 'Generate Resume'}
            </button>
            {resume && (
              <textarea
                className="resume-textarea"
                value={resume}
                onChange={(e) => setResume(e.target.value)}
                placeholder="Resume will appear here"
              />
            )}
          </div>

          <div className="section">
            <h4>Cover Letter</h4>
            <button
              className="btn btn-secondary"
              onClick={handleGenerateLetter}
              disabled={generatingLetter}
            >
              {generatingLetter ? 'Generating...' : 'Generate Letter'}
            </button>
            {coverLetter && (
              <textarea
                className="letter-textarea"
                value={coverLetter}
                onChange={(e) => setCoverLetter(e.target.value)}
                placeholder="Cover letter will appear here"
              />
            )}
          </div>

          <button
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={submitting || !resume || !coverLetter}
          >
            {submitting ? 'Submitting...' : 'Submit Application'}
          </button>
        </div>
      </div>
    </div>
  )
}
