import { defineStore } from 'pinia'

interface AppState {
  initialized: boolean
}

export const useAppStore = defineStore('app', {
  state: (): AppState => ({
    initialized: true,
  }),

  getters: {
    isInitialized: (state) => state.initialized,
  },

  actions: {
    init() {
      this.initialized = true
    },
  },
})
