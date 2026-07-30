import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { preferencesAPI } from '../services/api'
import '../styles/resume-manager.css'

// Common technical skills to match
const TECHNICAL_SKILLS = [
  // Programming Languages
  'JavaScript', 'Python', 'Java', 'C++', 'C#', 'Ruby', 'PHP', 'Go', 'Rust', 'Swift', 'Kotlin', 'R', 'MATLAB',
  'SQL', 'TypeScript', 'Scala', 'Groovy', 'Perl', 'Objective-C', 'Dart', 'Elixir',
  
  // Frontend
  'React', 'Vue', 'Angular', 'Svelte', 'Next.js', 'Nuxt', 'HTML', 'CSS', 'SASS', 'SCSS', 'Tailwind',
  'Bootstrap', 'Material-UI', 'jQuery', 'D3.js', 'Three.js', 'Webpack', 'Vite', 'Babel',
  
  // Backend
  'Node.js', 'Express', 'Django', 'Flask', 'FastAPI', 'Spring', 'Spring Boot', 'Laravel', 'Ruby on Rails',
  'ASP.NET', 'Nest.js', 'Gin', 'Echo', 'Fiber', 'Koa',
  
  // Databases
  'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch', 'Cassandra', 'DynamoDB', 'Firebase',
  'Firestore', 'Oracle', 'SQL Server', 'MariaDB', 'SQLite', 'GraphQL',
  
  // Cloud & DevOps
  'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'GitHub Actions',
  'CircleCI', 'Travis CI', 'Terraform', 'Ansible', 'CloudFormation', 'Serverless',
  
  // Tools & Platforms
  'Git', 'GitHub', 'GitLab', 'Bitbucket', 'Jira', 'Confluence', 'Slack', 'Figma', 'Adobe XD',
  'Postman', 'Insomnia', 'VS Code', 'IntelliJ', 'PyCharm', 'Sublime', 'Vim', 'Emacs',
  
  // Testing & Quality
  'Jest', 'Mocha', 'Pytest', 'JUnit', 'Selenium', 'Cypress', 'Playwright', 'TestNG', 'SonarQube',
  'ESLint', 'Prettier',
  
  // Other Tech
  'REST API', 'GraphQL', 'Microservices', 'WebSocket', 'OAuth', 'JWT', 'XML', 'JSON', 'gRPC',
  'Message Queue', 'RabbitMQ', 'Kafka', 'Apache', 'Nginx', 'Linux', 'Windows Server',
  'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy',
  'Data Science', 'Analytics', 'Big Data', 'Spark', 'Hadoop',
]

// Dynamic script loaders for client-side document parsing
const loadPdfJs = () => {
  return new Promise((resolve) => {
    if (window.pdfjsLib) {
      resolve(window.pdfjsLib)
      return
    }
    const script = document.createElement('script')
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js'
    script.onload = () => {
      window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js'
      resolve(window.pdfjsLib)
    }
    document.head.appendChild(script)
  })
}

const loadMammoth = () => {
  return new Promise((resolve) => {
    if (window.mammoth) {
      resolve(window.mammoth)
      return
    }
    const script = document.createElement('script')
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/mammoth/1.6.0/mammoth.browser.min.js'
    script.onload = () => {
      resolve(window.mammoth)
    }
    document.head.appendChild(script)
  })
}

const extractTextFromPdf = async (file) => {
  const pdfjsLib = await loadPdfJs()
  const arrayBuffer = await file.arrayBuffer()
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise
  let fullText = ''
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i)
    const textContent = await page.getTextContent()
    const pageText = textContent.items.map(item => item.str).join(' ')
    fullText += pageText + '\n'
  }
  return fullText
}

const extractTextFromDocx = async (file) => {
  const mammoth = await loadMammoth()
  const arrayBuffer = await file.arrayBuffer()
  const result = await mammoth.extractRawText({ arrayBuffer })
  return result.value
}

export const ResumeManager = () => {
  const navigate = useNavigate()
  const [savedResume, setSavedResume] = useState('')
  const [resumeText, setResumeText] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [showUpload, setShowUpload] = useState(false)

  useEffect(() => {
    fetchResume()
  }, [])

  const fetchResume = async () => {
    try {
      const response = await preferencesAPI.get()
      setSavedResume(response.data.base_resume || '')
      setResumeText(response.data.base_resume || '')
    } catch (err) {
      console.error('Failed to load resume:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveResume = async () => {
    if (!resumeText.trim()) {
      setMessage('✗ Resume cannot be empty')
      return
    }

    try {
      setSaving(true)
      setMessage('')
      
      await preferencesAPI.update({ base_resume: resumeText })
      setSavedResume(resumeText)
      setMessage('✓ Resume saved successfully!')
      setShowUpload(false)
      
      setTimeout(() => setMessage(''), 3000)
    } catch (err) {
      setMessage('✗ Failed to save resume')
      console.error(err)
    } finally {
      setSaving(false)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setSaving(true)
    setMessage('')

    try {
      let text = ''
      if (file.name.toLowerCase().endsWith('.pdf')) {
        text = await extractTextFromPdf(file)
      } else if (file.name.toLowerCase().endsWith('.docx')) {
        text = await extractTextFromDocx(file)
      } else if (file.name.toLowerCase().endsWith('.txt')) {
        const reader = new FileReader()
        text = await new Promise((resolve, reject) => {
          reader.onload = (event) => resolve(event.target.result)
          reader.onerror = (err) => reject(err)
          reader.readAsText(file)
        })
      } else {
        throw new Error('Unsupported file format. Please upload .pdf, .docx, or .txt')
      }

      if (!text.trim()) {
        throw new Error('Could not extract text from file or the file is empty.')
      }

      setResumeText(text)
      setMessage('✓ File parsed successfully!')
      setTimeout(() => setMessage(''), 3000)
    } catch (err) {
      console.error(err)
      setMessage(`✗ Failed to parse file: ${err.message || err}`)
    } finally {
      setSaving(false)
    }
  }

  const handlePasteResume = () => {
    navigator.clipboard.read().then(items => {
      items.forEach(item => {
        if (item.types.includes('text/plain')) {
          item.getType('text/plain').then(blob => {
            blob.text().then(text => {
              setResumeText(text)
            })
          })
        }
      })
    }).catch(() => {
      alert('Unable to access clipboard. Please try again.')
    })
  }

  const extractSkillsFromResume = (text) => {
    // Escape special regex characters
    const escapeRegex = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    
    // Extract skills by matching against TECHNICAL_SKILLS list (case-insensitive)
    const extractedSkills = new Set()
    const textLower = text.toLowerCase()
    
    TECHNICAL_SKILLS.forEach(skill => {
      const skillLower = skill.toLowerCase()
      // Match whole words or with word boundaries
      try {
        const escapedSkill = escapeRegex(skillLower)
        const regex = new RegExp(`\\b${escapedSkill}\\b`, 'gi')
        if (regex.test(textLower)) {
          extractedSkills.add(skill)
        }
      } catch (e) {
        // Skip skills that cause regex errors
        console.warn(`Skipping skill: ${skill}`)
      }
    })
    
    return Array.from(extractedSkills)
  }

  const handleExtractAndAddSkills = async () => {
    try {
      setSaving(true)
      setMessage('')
      
      const extractedSkills = extractSkillsFromResume(resumeText)
      
      if (extractedSkills.length === 0) {
        setMessage('✗ No skills found in resume. Please check content.')
        setSaving(false)
        return
      }
      
      // Get current preferences
      const currentPrefs = await preferencesAPI.get()
      const currentSkills = currentPrefs.data.skills || []
      
      // Merge with existing skills (avoid duplicates)
      const mergedSkills = Array.from(new Set([...currentSkills, ...extractedSkills]))
      
      // Update preferences with new skills
      await preferencesAPI.update({ skills: mergedSkills })
      
      setMessage(`✓ Added ${extractedSkills.length} skill(s) to preferences!`)
      setTimeout(() => setMessage(''), 4000)
    } catch (err) {
      setMessage('✗ Failed to add skills to preferences')
      console.error(err)
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    setResumeText(savedResume)
    setShowUpload(false)
  }

  if (loading) return <div className="loading">Loading resume...</div>

  return (
    <div className="resume-manager">
      <div className="resume-container">
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
        <h2>Your Resume</h2>
        <p className="subtitle">Upload or paste your resume to use across all job applications</p>

        {message && (
          <div className={`message ${message.includes('✓') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}

        {!showUpload && savedResume ? (
          <div className="resume-preview">
            <div className="resume-content">
              <pre>{savedResume}</pre>
            </div>
            <button
              onClick={() => setShowUpload(true)}
              className="btn btn-secondary"
            >
              Edit Resume
            </button>
          </div>
        ) : (
          <div className="resume-upload">
            <div className="upload-options">
              <div className="option">
                <h4>Option 1: Upload File</h4>
                <p>Upload a .pdf, .docx, or .txt file</p>
                <label className="file-input-label">
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt"
                    onChange={handleFileUpload}
                    className="file-input"
                  />
                  <span className="btn btn-secondary">Choose File</span>
                </label>
              </div>

              <div className="option">
                <h4>Option 2: Paste Text</h4>
                <p>Copy-paste your resume directly</p>
                <button
                  onClick={handlePasteResume}
                  className="btn btn-secondary"
                >
                  Paste from Clipboard
                </button>
              </div>

              <div className="option">
                <h4>Option 3: Type Resume</h4>
                <p>Type or edit your resume below</p>
              </div>
            </div>

            <div className="resume-editor">
              <label>Resume Content</label>
              <textarea
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste your resume here or edit above..."
                rows={15}
              />
            </div>

            <div className="button-group">
              <button
                onClick={handleSaveResume}
                disabled={saving}
                className="btn btn-primary"
              >
                {saving ? 'Saving...' : 'Save Resume'}
              </button>
              <button
                onClick={handleExtractAndAddSkills}
                disabled={saving || !resumeText.trim()}
                className="btn btn-primary"
                title="Scan resume and add detected skills to preferences"
              >
                {saving ? 'Processing...' : 'Extract Skills'}
              </button>
              {savedResume && (
                <button
                  onClick={handleReset}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              )}
            </div>
          </div>
        )}

        <div className="resume-info">
          <h4>💡 Tips for Best Results</h4>
          <ul>
            <li>Include your name, email, and phone number at the top</li>
            <li>List your technical skills and experience clearly</li>
            <li>Use clear section headers (Experience, Skills, Education, etc.)</li>
            <li>Click "Extract Skills" to auto-detect and add technical skills to your preferences</li>
            <li>The AI will tailor this resume for each job application</li>
            <li>You can manually edit the tailored version before submitting</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
