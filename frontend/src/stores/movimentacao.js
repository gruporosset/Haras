import { defineStore } from 'pinia'
import api from '../boot/api'

export const useMovimentacaoStore = defineStore('movimentacao', {
  state: () => ({
    movimentacoes: [],
    localizacoes: [],
    historicoAnimal: null,
    loading: false,
    filters: {
      animal_id: null,
      tipo_movimentacao: null,
      terreno_id: null,
      data_inicio: '',
      data_fim: '',
    },
    pagination: {
      page: 1,
      rowsPerPage: 10,
      rowsNumber: 0,
      sortBy: 'DATA_MOVIMENTACAO',
      descending: true,
    },
  }),

  getters: {
    tiposMovimentacao: () => [
      { value: 'TRANSFERENCIA', label: 'Transferência' },
      { value: 'ENTRADA', label: 'Entrada' },
      { value: 'SAIDA', label: 'Saída' },
      { value: 'VENDA', label: 'Venda' },
      { value: 'EMPRESTIMO', label: 'Empréstimo' },
      { value: 'RETORNO', label: 'Retorno' },
    ],

    movimentacoesByAnimal: state => animalId => {
      return state.movimentacoes.filter(m => m.ID_ANIMAL === animalId)
    },

    localizacaoByAnimal: state => animalId => {
      return state.localizacoes.find(l => l.animal_id === animalId)
    },
  },

  actions: {
    async fetchMovimentacoes(params = {}) {
      this.loading = true
      if (params == null || params == undefined) {
        params = {}
      }
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          ...this.filters,
          ...params.filters,
        }

        // Converter objetos select para valores
        if (queryParams.animal_id?.value) {
          queryParams.animal_id = queryParams.animal_id.value
        }
        if (queryParams.terreno_id?.value) {
          queryParams.terreno_id = queryParams.terreno_id.value
        }
        if (queryParams.tipo_movimentacao?.value) {
          queryParams.tipo_movimentacao = queryParams.tipo_movimentacao.value
        }

        const response = await api.get('/api/movimentacoes', {
          params: queryParams,
        })

        this.movimentacoes = response.data.movimentacoes
        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit,
        }

        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar movimentações'
      } finally {
        this.loading = false
      }
    },

    async createMovimentacao(movimentacaoData) {
      const response = await api.post('/api/movimentacoes', movimentacaoData)
      await this.fetchMovimentacoes()
      return response.data
    },

    async updateMovimentacao(id, movimentacaoData) {
      const response = await api.put(
        `/api/movimentacoes/${id}`,
        movimentacaoData
      )
      await this.fetchMovimentacoes()
      return response.data
    },

    async deleteMovimentacao(id) {
      await api.delete(`/api/movimentacoes/${id}`)
      await this.fetchMovimentacoes()
    },

    async fetchHistoricoAnimal(animalId) {
      try {
        const response = await api.get(
          `/api/movimentacoes/animal/${animalId}/historico`
        )
        this.historicoAnimal = response.data
        return response.data
      } catch (error) {
        throw (
          error.response?.data?.detail || 'Erro ao buscar histórico do animal'
        )
      }
    },

    async fetchLocalizacoes() {
      try {
        this.loading = true
        const response = await api.get(
          '/api/movimentacoes/relatorio/localizacoes',
          { params: this.filters }
        )
        this.localizacoes = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar localizações'
      } finally {
        this.loading = false
      }
    },

    setFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
    },

    clearFilters() {
      this.filters = {
        animal_id: null,
        tipo_movimentacao: null,
        terreno_id: null,
        data_inicio: '',
        data_fim: '',
      }
    },

    setPagination(newPagination) {
      this.pagination = { ...this.pagination, ...newPagination }
    },
  },
})
