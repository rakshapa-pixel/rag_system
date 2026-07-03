import { apiRequest } from './client.js'

export const getMe = () =>
  apiRequest('/auth/me')

export const signup = (username, password) =>
  apiRequest('/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })

export const login = (username, password) =>
  apiRequest('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })

export const logout = () =>
  apiRequest('/auth/logout', { method: 'POST' })
