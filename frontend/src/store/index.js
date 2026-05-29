import { create } from 'zustand';

export const useStore = create((set) => ({
  // Auth
  user: null,
  setUser: (user) => set({ user }),
  authToken: localStorage.getItem('authToken') || null,
  setAuthToken: (token) => {
    localStorage.setItem('authToken', token);
    set({ authToken: token });
  },
  logout: () => {
    localStorage.removeItem('authToken');
    set({ authToken: null, user: null });
  },

  // Current selection
  selectedClient: null,
  setSelectedClient: (client) => set({ selectedClient: client }),

  // UI state
  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  // Data cache
  clients: [],
  setClients: (clients) => set({ clients }),
  records: [],
  setRecords: (records) => set({ records }),
  dashboardSummary: null,
  setDashboardSummary: (summary) => set({ dashboardSummary: summary }),
}));
