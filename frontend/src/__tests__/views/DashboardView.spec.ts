import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import DashboardView from '@/views/DashboardView.vue'

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
    logout: vi.fn()
  },
  statsService: {
    getGeneralStats: vi.fn()
  }
}))

import { statsService, authService } from '@/services/api'

describe('DashboardView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockLocalStorage.store = {}
    mockRouter.push.mockClear()
  })

  describe('Rendering', () => {
    it('should render dashboard container', () => {
      vi.mocked(statsService.getGeneralStats).mockResolvedValue({
        total_items: 0,
        total_properties: 0,
        total_lexemes: 0,
        total_statements: 0,
        total_edits: 0
      })

      const wrapper = mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      expect(wrapper.find('.dashboard').exists()).toBe(true)
    })

    it('should render header with Dashboard title', async () => {
      vi.mocked(statsService.getGeneralStats).mockResolvedValue({
        total_items: 0,
        total_properties: 0,
        total_lexemes: 0,
        total_statements: 0,
        total_edits: 0
      })

      const wrapper = mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await flushPromises()

      expect(wrapper.find('.dashboard-header h1').text()).toBe('Dashboard')
    })

    it('should render logout button', async () => {
      vi.mocked(statsService.getGeneralStats).mockResolvedValue({
        total_items: 0,
        total_properties: 0,
        total_lexemes: 0,
        total_statements: 0,
        total_edits: 0
      })

      const wrapper = mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await flushPromises()

      expect(wrapper.find('.user-info button').exists()).toBe(true)
      expect(wrapper.find('.user-info button').text()).toBe('Logout')
    })

    it('should show username from localStorage', async () => {
      mockLocalStorage.store['username'] = 'testuser'

      vi.mocked(statsService.getGeneralStats).mockResolvedValue({
        total_items: 0,
        total_properties: 0,
        total_lexemes: 0,
        total_statements: 0,
        total_edits: 0
      })

      const wrapper = mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await flushPromises()

      expect(wrapper.find('.user-info span').text()).toContain('testuser')
    })

    it('should show default username when not in localStorage', async () => {
      vi.mocked(statsService.getGeneralStats).mockResolvedValue({
        total_items: 0,
        total_properties: 0,
        total_lexemes: 0,
        total_statements: 0,
        total_edits: 0
      })

      const wrapper = mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await flushPromises()

      expect(wrapper.find('.user-info span').text()).toContain('User')
    })
  })

  describe('Stats loading', () => {
    it('should call statsService.getGeneralStats on mount', async () => {
      vi.mocked(statsService.getGeneralStats).mockResolvedValue({
        total_items: 0,
        total_properties: 0,
        total_lexemes: 0,
        total_statements: 0,
        total_edits: 0
      })

      mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await flushPromises()

      expect(statsService.getGeneralStats).toHaveBeenCalled()
    })

    it('should show loading state initially', () => {
      vi.mocked(statsService.getGeneralStats).mockImplementation(
        () => new Promise(() => {})
      )

      const wrapper = mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      expect(wrapper.find('.loading').exists()).toBe(true)
      expect(wrapper.find('.loading').text()).toBe('Loading statistics...')
    })
  })

  describe('Stats display', () => {
    it('should display 5 stat cards after loading', async () => {
      vi.mocked(statsService.getGeneralStats).mockResolvedValue({
        total_items: 1000,
        total_properties: 500,
        total_lexemes: 200,
        total_statements: 5000,
        total_edits: 10000
      })

      const wrapper = mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await flushPromises()

      const statCards = wrapper.findAll('.stat-card')
      expect(statCards.length).toBe(5)
    })

    it('should display Items stat card with correct value', async () => {
      vi.mocked(statsService.getGeneralStats).mockResolvedValue({
        total_items: 1000,
        total_properties: 500,
        total_lexemes: 200,
        total_statements: 5000,
        total_edits: 10000
      })

      const wrapper = mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await flushPromises()

      const itemsCard = wrapper.findAll('.stat-card')[0]
      expect(itemsCard.find('.stat-label').text()).toBe('Items')
      expect(itemsCard.find('.stat-value').text()).toBe('1,000')
    })

    it('should display Total Edits with highlight class', async () => {
      vi.mocked(statsService.getGeneralStats).mockResolvedValue({
        total_items: 1000,
        total_properties: 500,
        total_lexemes: 200,
        total_statements: 5000,
        total_edits: 10000
      })

      const wrapper = mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await flushPromises()

      const highlightCard = wrapper.find('.stat-card.highlight')
      expect(highlightCard.exists()).toBe(true)
      expect(highlightCard.find('.stat-label').text()).toBe('Total Edits')
    })

    it('should format large numbers with toLocaleString', async () => {
      vi.mocked(statsService.getGeneralStats).mockResolvedValue({
        total_items: 1234567,
        total_properties: 987654,
        total_lexemes: 12345,
        total_statements: 9876543,
        total_edits: 11111111
      })

      const wrapper = mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await flushPromises()

      const itemsCard = wrapper.findAll('.stat-card')[0]
      expect(itemsCard.find('.stat-value').text()).toBe('1,234,567')
    })
  })

  describe('Error handling', () => {
    it('should show error message when stats API fails', async () => {
      vi.mocked(statsService.getGeneralStats).mockRejectedValue({
        response: { data: { detail: 'Failed to load statistics' } }
      })

      const wrapper = mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await flushPromises()

      expect(wrapper.find('.error-message').exists()).toBe(true)
      expect(wrapper.find('.error-message').text()).toBe('Failed to load statistics')
    })

    it('should not show error message when stats load successfully', async () => {
      vi.mocked(statsService.getGeneralStats).mockResolvedValue({
        total_items: 1000,
        total_properties: 500,
        total_lexemes: 200,
        total_statements: 5000,
        total_edits: 10000
      })

      const wrapper = mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await flushPromises()

      expect(wrapper.find('.error-message').exists()).toBe(false)
    })
  })

  describe('Logout', () => {
    it('should call authService.logout on logout click', async () => {
      vi.mocked(statsService.getGeneralStats).mockResolvedValue({
        total_items: 0,
        total_properties: 0,
        total_lexemes: 0,
        total_statements: 0,
        total_edits: 0
      })

      const wrapper = mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await flushPromises()

      await wrapper.find('.user-info button').trigger('click')

      expect(authService.logout).toHaveBeenCalled()
    })

    it('should navigate to /login on logout', async () => {
      vi.mocked(statsService.getGeneralStats).mockResolvedValue({
        total_items: 0,
        total_properties: 0,
        total_lexemes: 0,
        total_statements: 0,
        total_edits: 0
      })

      const wrapper = mount(DashboardView, {
        global: {
          stubs: { 'router-view': true }
        }
      })

      await flushPromises()

      await wrapper.find('.user-info button').trigger('click')

      expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })
  })
})
