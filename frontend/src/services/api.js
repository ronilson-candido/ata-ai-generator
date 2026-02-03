import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth Service
export const authService = {
  async login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    localStorage.setItem('token', response.data.access_token);
    return response.data;
  },

  async register(userData) {
    const response = await axios.post(`${API_BASE_URL}/auth/register`, userData);
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  logout() {
    localStorage.removeItem('token');
  }
};

// Minutes Service
export const minutesService = {
  async uploadMinute(file, title) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);

    const response = await api.post('/minutes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getMyMinutes(skip = 0, limit = 100) {
    const response = await api.get(`/minutes/?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  async getMinute(id) {
    const response = await api.get(`/minutes/${id}`);
    return response.data;
  },

  async deleteMinute(id) {
    const response = await api.delete(`/minutes/${id}`);
    return response.data;
  },

  async saveLiveTranscription(title, transcription) {
    const response = await api.post('/minutes/live', { title, transcription });
    return response.data;
  }
};

// Admin Service
export const adminService = {
  async getDashboardStats() {
    const response = await api.get('/admin/dashboard');
    return response.data;
  },

  async getAllUsers(skip = 0, limit = 100) {
    const response = await api.get(`/admin/users?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  async updateUser(userId, userData) {
    const response = await api.put(`/admin/users/${userId}`, userData);
    return response.data;
  },

  async deleteUser(userId) {
    const response = await api.delete(`/admin/users/${userId}`);
    return response.data;
  },

  async getAllMinutes(skip = 0, limit = 100) {
    const response = await api.get(`/admin/minutes/all?skip=${skip}&limit=${limit}`);
    return response.data;
  }
};

export default api;
