import { defineStore } from 'pinia'
import api from '../boot/api'

export const useCrescimentoStore = defineStore('crescimento', {
  state: () => ({
    crescimentos: [],
    saudes: [],
    proximasAplicacoes: [],
    estatisticas: [],
    loading: false,
    filters: {
      animal_id: null,
      tipo_registro: null,
      data_inicio: '',
      data_fim: ''
    },
    pagination: {
      page: 1,
      rowsPerPage: 10,
      rowsNumber: 0,
      sortBy: 'DATA_MEDICAO',
      descending: true
    }
  }),

  getters: {
    tiposRegistro: () => [
      { value: 'VACINA', label: 'Vacina' },
      { value: 'VERMIFUGO', label: 'Vermífugo' },
      { value: 'MEDICAMENTO', label: 'Medicamento' },
      { value: 'EXAME', label: 'Exame' },
      { value: 'CONSULTA', label: 'Consulta' },
      { value: 'CIRURGIA', label: 'Cirurgia' },
      { value: 'TRATAMENTO', label: 'Tratamento' }
    ],

    aplicacoesPendentes: (state) => state.proximasAplicacoes.filter(a => a.dias_restantes <= 7),
    
    registrosByAnimal: (state) => (animalId) => {
      return {
        crescimentos: state.crescimentos.filter(c => c.ID_ANIMAL === animalId),
        saudes: state.saudes.filter(s => s.ID_ANIMAL === animalId)
      }
    }
  },

  actions: {
    // === CRESCIMENTO ===
    async fetchCrescimentos(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          ...this.filters,
          ...params.filters
        }

        const response = await api.get('/api/crescimento-saude/crescimento', { params: queryParams })
        
        this.crescimentos = response.data.registros
        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit
        }
        
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar registros de crescimento'
      } finally {
        this.loading = false
      }
    },

    async createCrescimento(crescimentoData) {
      try {
        const response = await api.post('/api/crescimento-saude/crescimento', crescimentoData)
        await this.fetchCrescimentos()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao criar registro de crescimento'
      }
    },

    async updateCrescimento(id, crescimentoData) {
      try {
        const response = await api.put(`/api/crescimento-saude/crescimento/${id}`, crescimentoData)
        await this.fetchCrescimentos()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar registro de crescimento'
      }
    },

    async deleteCrescimento(id) {
      try {
        await api.delete(`/api/crescimento-saude/crescimento/${id}`)
        await this.fetchCrescimentos()
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir registro de crescimento'
      }
    },

    // === SAÚDE ===
    async fetchSaudes(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          ...this.filters,
          ...params.filters
        }

        const response = await api.get('/api/crescimento-saude/saude', { params: queryParams })
        
        this.saudes = response.data.registros
        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit
        }
        
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar registros de saúde'
      } finally {
        this.loading = false
      }
    },

    async createSaude(saudeData) {
      try {
        const response = await api.post('/api/crescimento-saude/saude', saudeData)
        await this.fetchSaudes()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao criar registro de saúde'
      }
    },

    async updateSaude(id, saudeData) {
      try {
        const response = await api.put(`/api/crescimento-saude/saude/${id}`, saudeData)
        await this.fetchSaudes()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar registro de saúde'
      }
    },

    async deleteSaude(id) {
      try {
        await api.delete(`/api/crescimento-saude/saude/${id}`)
        await this.fetchSaudes()
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir registro de saúde'
      }
    },

    // === RELATÓRIOS ===
    async fetchProximasAplicacoes(dias = 30) {
      try {
        const response = await api.get(`/api/crescimento-saude/proximas-aplicacoes?dias=${dias}`)
        this.proximasAplicacoes = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar próximas aplicações'
      }
    },

    async fetchEstatisticasCrescimento() {
      try {
        const response = await api.get('/api/crescimento-saude/estatisticas-crescimento')
        this.estatisticas = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar estatísticas de crescimento'
      }
    },

    setFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
    },

    clearFilters() {
      this.filters = {
        animal_id: null,
        tipo_registro: null,
        data_inicio: '',
        data_fim: ''
      }
    },

    setPagination(newPagination) {
      this.pagination = { ...this.pagination, ...newPagination }
    }
  }
})