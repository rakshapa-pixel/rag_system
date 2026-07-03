import { apiRequest } from './client.js'

export const getDocuments = () =>
  apiRequest('/documents')

export const ingestDocument = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return apiRequest('/ingest', { method: 'POST', body: formData })
}

export const deleteDocument = (docId) =>
  apiRequest(`/documents/${docId}`, { method: 'DELETE' })
