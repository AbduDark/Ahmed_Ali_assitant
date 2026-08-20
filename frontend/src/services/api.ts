import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 — redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ── Auth ─────────────────────────────────────────────────────

export const authApi = {
  login: (emailOrPayload: string | { email: string; password: string }, password?: string) => {
    const payload = typeof emailOrPayload === 'string'
      ? { email: emailOrPayload, password: password || '' }
      : emailOrPayload;
    return api.post('/auth/login', payload);
  },
  refresh: (refreshToken: string) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),
  me: () => api.get('/auth/me'),
};

// ── Dashboard ────────────────────────────────────────────────

export const dashboardApi = {
  getStats: () => api.get('/dashboard'),
};

// ── Students ─────────────────────────────────────────────────

export const studentsApi = {
  list: (params?: { skip?: number; limit?: number; search?: string }) =>
    api.get('/students', { params }),
  get: (id: string) => api.get(`/students/${id}`),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/students/${id}`, data),
};

// ── Conversations ────────────────────────────────────────────

export const conversationsApi = {
  list: (params?: { skip?: number; limit?: number; student_id?: string }) =>
    api.get('/conversations', { params }),
  get: (id: string) => api.get(`/conversations/${id}`),
};

// ── References ───────────────────────────────────────────────

export const referencesApi = {
  list: (params?: { skip?: number; limit?: number; subject_id?: string; status?: string }) =>
    api.get('/references', { params }),
  get: (id: string) => api.get(`/references/${id}`),
  create: (formData: FormData) =>
    api.post('/references', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  delete: (id: string) => api.delete(`/references/${id}`),
  reprocess: (id: string) => api.post(`/references/${id}/reprocess`),
};

// ── Subjects ─────────────────────────────────────────────────

export const subjectsApi = {
  list: () => api.get('/subjects'),
  create: (data: { name_ar: string; name_en?: string; description?: string }) =>
    api.post('/subjects', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/subjects/${id}`, data),
  createUnit: (data: { subject_id: string; name_ar: string; name_en?: string; order?: number }) =>
    api.post('/subjects/units', data),
  createLesson: (data: { unit_id: string; name_ar: string; name_en?: string; order?: number }) =>
    api.post('/subjects/lessons', data),
};

// ── Instructions ─────────────────────────────────────────────

export const instructionsApi = {
  list: () => api.get('/instructions'),
  create: (data: { content: string; title?: string; priority?: number }) =>
    api.post('/instructions', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/instructions/${id}`, data),
  delete: (id: string) => api.delete(`/instructions/${id}`),
};

// ── Corrections ──────────────────────────────────────────────

export const correctionsApi = {
  list: () => api.get('/corrections'),
  create: (data: { question: string; correct_answer: string; bad_answer?: string; subject?: string }) =>
    api.post('/corrections', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/corrections/${id}`, data),
  delete: (id: string) => api.delete(`/corrections/${id}`),
};

// ── Analytics ────────────────────────────────────────────────

export const analyticsApi = {
  getStats: (days?: number) => api.get('/analytics', { params: { days } }),
  getAiUsage: (days?: number) => api.get('/analytics/ai-usage', { params: { days } }),
};

export default api;
