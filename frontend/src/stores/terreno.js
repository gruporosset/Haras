import { defineStore } from 'pinia'
import api from '../boot/api'

export const useTerrenoStore = defineStore('terreno', {
  state: () => ({
    terrenos: [],
    currentTerreno: null,
    loading: false,
    filters: {
      nome: '',
      status: null,
    },
    pagination: {
      page: 1,
      rowsPerPage: 10,
      rowsNumber: 0,
      sortBy: 'ID',
      descending: false,
    },
  }),

  getters: {
    terrenosDisponiveis: state =>
      state.terrenos.filter(t => t.STATUS_TERRENO === 'DISPONIVEL'),
    terrenosOcupados: state =>
      state.terrenos.filter(t => t.STATUS_TERRENO === 'OCUPADO'),

    terrenoById: state => id => state.terrenos.find(t => t.ID === id),

    estatisticas: state => {
      const total = state.terrenos.length
      const disponiveis = state.terrenos.filter(
        t => t.STATUS_TERRENO === 'DISPONIVEL'
      ).length
      const ocupados = state.terrenos.filter(
        t => t.STATUS_TERRENO === 'OCUPADO'
      ).length
      const manutencao = state.terrenos.filter(
        t => t.STATUS_TERRENO === 'MANUTENÇÃO'
      ).length
      const areaTotal = state.terrenos.reduce(
        (sum, t) => sum + (t.AREA_HECTARES || 0),
        0
      )

      return {
        total,
        disponiveis,
        ocupados,
        manutencao,
        areaTotal: parseFloat(areaTotal.toFixed(2)),
      }
    },
  },

  actions: {
    async fetchTerrenos(params = {}) {
      this.loading = true
      if (params == null || params == undefined) {
        params = {}
      }

      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          sort_by: params.sortBy || this.pagination.sortBy,
          order: params.descending ? 'desc' : 'asc',
          ...this.filters,
          ...params.filters,
        }

        const response = await api.get('/api/terrenos', { params: queryParams })

        this.terrenos = response.data.terrenos
        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit,
        }

        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar terrenos'
      } finally {
        this.loading = false
      }
    },

    async getTerreno(id) {
      try {
        const response = await api.get(`/api/terrenos/${id}`)
        this.currentTerreno = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar terreno'
      }
    },

    async createTerreno(terrenoData) {
      const response = await api.post('/api/terrenos', terrenoData)
      await this.fetchTerrenos()
      return response.data
    },

    async updateTerreno(id, terrenoData) {
      const response = await api.put(`/api/terrenos/${id}`, terrenoData)
      await this.fetchTerrenos()
      return response.data
    },

    async deleteTerreno(id) {
      await api.delete(`/api/terrenos/${id}`)
      await this.fetchTerrenos()
    },

    setFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
    },

    clearFilters() {
      this.filters = {
        nome: '',
        status: null,
      }
    },

    setPagination(newPagination) {
      this.pagination = { ...this.pagination, ...newPagination }
    },
  },
})
