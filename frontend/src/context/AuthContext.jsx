import React, { createContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'

export const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('access_token'))

  useEffect(() => {
    if (token) {
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchUser = async () => {
    try {
      const response = await authAPI.getMe()
      setUser(response.data)
    } catch (error) {
      console.error('Error fetching user:', error)
      localStorage.removeItem('access_token')
      setToken(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    const response = await authAPI.login(email, password)
    const { access_token, user: userData } = response.data
    
    localStorage.setItem('access_token', access_token)
    setToken(access_token)
    setUser(userData)
    
    return userData
  }

  const register = async (name, email, password, telegramChatId = null) => {
    const response = await authAPI.register(name, email, password, telegramChatId)
    const { access_token, user: userData } = response.data
    
    localStorage.setItem('access_token', access_token)
    setToken(access_token)
    setUser(userData)
    
    return userData
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      token,
      isAuthenticated: !!token,
      login,
      register,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  )
}
