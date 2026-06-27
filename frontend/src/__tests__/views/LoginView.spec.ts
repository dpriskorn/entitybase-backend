import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import LoginView from '@/views/LoginView.vue'

const mockLocalStorage = {
  store: {} as Record<string, string>,
  getItem: vi.fn((key: string) => mockLocalStorage.store[key] || null),
  setItem: vi.fn((key: string, value: string) => { mockLocalStorage.store[key] = value }),
  removeItem: vi.fn((key: string) => { delete mockLocalStorage.store[key] })
}

Object.defineProperty(global, 'localStorage', { value: mockLocalStorage })

const mockRouter = {
  push: vi.fn()
}

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter
}))

vi.mock('@/services/api', () => ({
  authService: {
    login: vi.fn()
  }
}))

import { authService } from '@/services/api'

describe('LoginView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockLocalStorage.store = {}
    mockRouter.push.mockClear()
  })

  describe('Rendering', () => {
    it('should render login form', () => {
      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      expect(wrapper.find('form').exists()).toBe(true)
    })

    it('should render username input', () => {
      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      expect(wrapper.find('input#username').exists()).toBe(true)
    })

    it('should render password input', () => {
      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      expect(wrapper.find('input#password').exists()).toBe(true)
    })

    it('should render submit button', () => {
      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
    })

    it('should display EntityBase title', () => {
      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      expect(wrapper.find('h1').text()).toBe('EntityBase')
    })

    it('should display Sign In heading', () => {
      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      expect(wrapper.find('h2').text()).toBe('Sign In')
    })

    it('should display Sign In button text by default', () => {
      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      expect(wrapper.find('button[type="submit"]').text()).toBe('Sign In')
    })

    it('should have required attribute on inputs', () => {
      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      expect(wrapper.find('input#username').attributes('required')).toBeDefined()
      expect(wrapper.find('input#password').attributes('required')).toBeDefined()
    })
  })

  describe('Form interaction', () => {
    it('should update username on input', async () => {
      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await wrapper.find('input#username').setValue('testuser')
      expect((wrapper.find('input#username').element as HTMLInputElement).value).toBe('testuser')
    })

    it('should update password on input', async () => {
      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await wrapper.find('input#password').setValue('password123')
      expect((wrapper.find('input#password').element as HTMLInputElement).value).toBe('password123')
    })
  })

  describe('Login success', () => {
    it('should call authService.login on submit', async () => {
      vi.mocked(authService.login).mockResolvedValue({
        access_token: 'test-token',
        token_type: 'bearer',
        expires_in: 1800,
        user: { user_id: 1, username: 'testuser', role: 'default' }
      })

      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await wrapper.find('input#username').setValue('testuser')
      await wrapper.find('input#password').setValue('password123')
      await wrapper.find('form').trigger('submit')

      await flushPromises()

      expect(authService.login).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123'
      })
    })

    it('should store token in localStorage on success', async () => {
      vi.mocked(authService.login).mockResolvedValue({
        access_token: 'jwt-token-123',
        token_type: 'bearer',
        expires_in: 1800,
        user: { user_id: 1, username: 'testuser', role: 'default' }
      })

      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await wrapper.find('input#username').setValue('testuser')
      await wrapper.find('input#password').setValue('password123')
      await wrapper.find('form').trigger('submit')

      await flushPromises()

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('access_token', 'jwt-token-123')
    })

    it('should navigate to /dashboard on success', async () => {
      vi.mocked(authService.login).mockResolvedValue({
        access_token: 'test-token',
        token_type: 'bearer',
        expires_in: 1800,
        user: { user_id: 1, username: 'testuser', role: 'default' }
      })

      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await wrapper.find('input#username').setValue('testuser')
      await wrapper.find('input#password').setValue('password123')
      await wrapper.find('form').trigger('submit')

      await flushPromises()

      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard')
    })
  })

  describe('Login failure', () => {
    it('should show error message on failed login', async () => {
      vi.mocked(authService.login).mockRejectedValue({
        response: { data: { detail: 'Invalid credentials' } }
      })

      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await wrapper.find('input#username').setValue('baduser')
      await wrapper.find('input#password').setValue('wrongpass')
      await wrapper.find('form').trigger('submit')

      await flushPromises()

      expect(wrapper.find('.error-message').exists()).toBe(true)
      expect(wrapper.find('.error-message').text()).toBe('Invalid credentials')
    })

    it('should not navigate on failed login', async () => {
      vi.mocked(authService.login).mockRejectedValue({
        response: { data: { detail: 'Invalid credentials' } }
      })

      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await wrapper.find('input#username').setValue('baduser')
      await wrapper.find('input#password').setValue('wrongpass')
      await wrapper.find('form').trigger('submit')

      await flushPromises()

      expect(mockRouter.push).not.toHaveBeenCalled()
    })

    it('should not store token on failed login', async () => {
      vi.mocked(authService.login).mockRejectedValue({
        response: { data: { detail: 'Invalid credentials' } }
      })

      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await wrapper.find('input#username').setValue('baduser')
      await wrapper.find('input#password').setValue('wrongpass')
      await wrapper.find('form').trigger('submit')

      await flushPromises()

      expect(mockLocalStorage.setItem).not.toHaveBeenCalled()
    })
  })

  describe('Loading state', () => {
    it('should show "Signing in..." during login', async () => {
      let resolveLogin: () => void
      vi.mocked(authService.login).mockImplementation(
        () => new Promise(resolve => { resolveLogin = resolve })
      )

      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await wrapper.find('input#username').setValue('testuser')
      await wrapper.find('input#password').setValue('password123')
      await wrapper.find('form').trigger('submit')

      await wrapper.find('button[type="submit"]').text()
      const buttonText = wrapper.find('button[type="submit"]').text()
      expect(buttonText).toBe('Signing in...')
    })

    it('should disable button during loading', async () => {
      vi.mocked(authService.login).mockImplementation(
        () => new Promise(() => {})
      )

      const wrapper = mount(LoginView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await wrapper.find('input#username').setValue('testuser')
      await wrapper.find('input#password').setValue('password123')
      await wrapper.find('form').trigger('submit')

      await flushPromises()

      const button = wrapper.find('button[type="submit"]')
      expect(button.attributes('disabled')).toBeDefined()
    })
  })
})
