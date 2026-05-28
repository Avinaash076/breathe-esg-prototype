import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/ingestion';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Upload endpoints
export const uploadProcurement = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/procurement/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const uploadUtility = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/utility/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const uploadTravel = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/travel/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// Fetch endpoints
export const getProcurementPending = () => api.get('/procurement/pending/');
export const getProcurementAll = () => api.get('/procurement/all/');
export const getUtilityPending = () => api.get('/utility/pending/');
export const getUtilityAll = () => api.get('/utility/all/');
export const getTravelPending = () => api.get('/travel/pending/');
export const getTravelAll = () => api.get('/travel/all/');

// Dashboard
export const getDashboardStats = () => api.get('/stats/');

// Review endpoints
export const reviewProcurement = (recordIds, status, comments, reviewedBy) =>
  api.post('/procurement/review/', {
    record_ids: recordIds,
    review_status: status,
    comments,
    reviewed_by: reviewedBy,
  });

export const reviewUtility = (recordIds, status, comments, reviewedBy) =>
  api.post('/utility/review/', {
    record_ids: recordIds,
    review_status: status,
    comments,
    reviewed_by: reviewedBy,
  });

export const reviewTravel = (recordIds, status, comments, reviewedBy) =>
  api.post('/travel/review/', {
    record_ids: recordIds,
    review_status: status,
    comments,
    reviewed_by: reviewedBy,
  });
