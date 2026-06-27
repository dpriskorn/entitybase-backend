import axios from 'axios'

const API_BASE = '/v1'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const hasToken = !!localStorage.getItem('access_token')
      localStorage.removeItem('access_token')
      if (hasToken) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: {
    user_id: number
    username: string
    role: string
  }
}

export interface GeneralStats {
  total_items: number
  total_properties: number
  total_lexemes: number
  total_statements: number
  total_edits: number
}

export const authService = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', data)
    return response.data
  },

  logout: () => {
    localStorage.removeItem('access_token')
  }
}

export const statsService = {
  getGeneralStats: async (): Promise<GeneralStats> => {
    const response = await api.get<GeneralStats>('/stats/general')
    return response.data
  }
}

export default api
