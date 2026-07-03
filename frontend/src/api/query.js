import { apiRequest } from './client.js'

export const askQuestion = (question) =>
  apiRequest('/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
