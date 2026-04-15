import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, AuthContext } from './context/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'

// Pages
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Dashboard } from './pages/Dashboard'
import { AddJob } from './pages/AddJob'
import { ResumeManager } from './pages/ResumeManager'
import { JobDetail } from './pages/JobDetail'
import { Applications } from './pages/Applications'
import { Preferences } from './pages/Preferences'
import AutoApplySettings from './pages/AutoApplySettings'

function AppContent() {
  const { isAuthenticated, loading } = React.useContext(AuthContext)

  if (loading) {
    return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      Loading...
    </div>
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/add-job"
        element={
          <ProtectedRoute>
            <AddJob />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/resume"
        element={
          <ProtectedRoute>
            <ResumeManager />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/job/:jobId"
        element={
          <ProtectedRoute>
            <JobDetail />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/applications"
        element={
          <ProtectedRoute>
            <Applications />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/preferences"
        element={
          <ProtectedRoute>
            <Preferences />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/auto-apply"
        element={
          <ProtectedRoute>
            <AutoApplySettings />
          </ProtectedRoute>
        }
      />
      
      <Route path="/" element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />} />
    </Routes>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  )
}

export default App
