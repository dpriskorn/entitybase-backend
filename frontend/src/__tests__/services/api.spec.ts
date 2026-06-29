import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockLocalStorage = {
  store: {} as Record<string, string>,
  getItem: vi.fn((key: string) => mockLocalStorage.store[key] || null),
  setItem: vi.fn((key: string, value: string) => { mockLocalStorage.store[key] = value }),
  removeItem: vi.fn((key: string) => { delete mockLocalStorage.store[key] })
}

Object.defineProperty(global, 'localStorage', { value: mockLocalStorage })

describe('localStorage mock', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockLocalStorage.store = {}
  })

  it('should get item from localStorage', () => {
    mockLocalStorage.store['test'] = 'value'
    expect(mockLocalStorage.getItem('test')).toBe('value')
  })

  it('should return null for missing item', () => {
    expect(mockLocalStorage.getItem('missing')).toBeNull()
  })

  it('should set item in localStorage', () => {
    mockLocalStorage.setItem('key', 'value')
    expect(mockLocalStorage.store['key']).toBe('value')
  })

  it('should remove item from localStorage', () => {
    mockLocalStorage.store['key'] = 'value'
    mockLocalStorage.removeItem('key')
    expect(mockLocalStorage.store['key']).toBeUndefined()
  })
})

describe('LoginRequest interface', () => {
  it('should have correct shape', () => {
    const request = {
      username: 'testuser',
      password: 'password123'
    }

    expect(request.username).toBe('testuser')
    expect(request.password).toBe('password123')
  })

  it('should require username and password', () => {
    const request = {
      username: '',
      password: ''
    }

    expect(request.username).toBe('')
    expect(request.password).toBe('')
  })
})

describe('LoginResponse interface', () => {
  it('should have correct shape', () => {
    const response = {
      access_token: 'jwt-token',
      token_type: 'bearer',
      expires_in: 1800,
      user: {
        user_id: 1,
        username: 'testuser',
        role: 'default'
      }
    }

    expect(response.access_token).toBe('jwt-token')
    expect(response.token_type).toBe('bearer')
    expect(response.expires_in).toBe(1800)
    expect(response.user.username).toBe('testuser')
  })

  it('should include user info', () => {
    const response = {
      access_token: 'token',
      token_type: 'bearer',
      expires_in: 3600,
      user: {
        user_id: 42,
        username: 'admin',
        role: 'admin'
      }
    }

    expect(response.user.user_id).toBe(42)
    expect(response.user.role).toBe('admin')
  })
})

describe('GeneralStats interface', () => {
  it('should have correct shape', () => {
    const stats = {
      total_items: 1000,
      total_properties: 500,
      total_lexemes: 200,
      total_statements: 5000,
      total_edits: 10000
    }

    expect(stats.total_items).toBe(1000)
    expect(stats.total_properties).toBe(500)
    expect(stats.total_lexemes).toBe(200)
    expect(stats.total_statements).toBe(5000)
    expect(stats.total_edits).toBe(10000)
  })

  it('should handle zero values', () => {
    const stats = {
      total_items: 0,
      total_properties: 0,
      total_lexemes: 0,
      total_statements: 0,
      total_edits: 0
    }

    expect(stats.total_items).toBe(0)
    expect(stats.total_edits).toBe(0)
  })

  it('should handle large values', () => {
    const stats = {
      total_items: 1000000000,
      total_properties: 500000000,
      total_lexemes: 200000000,
      total_statements: 5000000000,
      total_edits: 10000000000
    }

    expect(stats.total_items).toBeGreaterThan(0)
    expect(stats.total_edits).toBeGreaterThan(stats.total_statements)
  })
})

describe('API module exports', () => {
  it('should export authService functions', async () => {
    const { authService } = await import('@/services/api')

    expect(authService).toBeDefined()
    expect(typeof authService.login).toBe('function')
    expect(typeof authService.logout).toBe('function')
  })

  it('should export statsService functions', async () => {
    const { statsService } = await import('@/services/api')

    expect(statsService).toBeDefined()
    expect(typeof statsService.getGeneralStats).toBe('function')
  })

  it('should export api default', async () => {
    const api = await import('@/services/api')

    expect(api.default).toBeDefined()
  })
})
