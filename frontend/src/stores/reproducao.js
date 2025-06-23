import { defineStore } from 'pinia'
import api from '../boot/api'

export const useReproducaoStore = defineStore('reproducao', {
  state: () => ({
    reproducoes: [],
    estatisticas: null,
    calendarioEventos: [],
    historicoEgua: null,
    loading: false,
    filters: {
      egua_id: null,
      parceiro_id: null,
      tipo_cobertura: null,
      resultado: null,
      status: null,
      data_inicio: '',
      data_fim: '',
    },
    pagination: {
      page: 1,
      rowsPerPage: 10,
      rowsNumber: 0,
      sortBy: 'DATA_COBERTURA',
      descending: true,
    },
  }),

  getters: {
    tiposCobertura: () => [
      { value: 'NATURAL', label: 'Natural' },
      { value: 'IA', label: 'Inseminação Artificial' },
      { value: 'TE', label: 'Transferência de Embrião' },
    ],

    resultadosDiagnostico: () => [
      { value: 'POSITIVO', label: 'Positivo' },
      { value: 'NEGATIVO', label: 'Negativo' },
      { value: 'PENDENTE', label: 'Pendente' },
    ],

    statusReproducao: () => [
      { value: 'ATIVO', label: 'Ativo' },
      { value: 'CONCLUIDO', label: 'Concluído' },
      { value: 'FALHADO', label: 'Falhado' },
    ],

    gestacoesAtivas: (state) =>
      state.reproducoes.filter(
        (r) => r.STATUS_REPRODUCAO === 'A' && r.RESULTADO_DIAGNOSTICO === 'POSITIVO',
      ),

    eventosPrioritarios: (state) => state.calendarioEventos.filter((e) => e.dias_restantes <= 7),

    reproducoesByEgua: (state) => (eguaId) => {
      return state.reproducoes.filter((r) => r.ID_EGUA === eguaId)
    },
  },

  actions: {
    async fetchReproducoes(params = {}) {
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
        if (queryParams.egua_id?.value) {
          queryParams.egua_id = queryParams.egua_id.value
        }
        if (queryParams.resultado?.value) {
          queryParams.resultado = queryParams.resultado.value
        }
        if (queryParams.status?.value) {
          queryParams.status = queryParams.status.value
        }

        const response = await api.get('/api/reproducao', { params: queryParams })

        this.reproducoes = response.data.reproducoes
        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit,
        }

        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar reproduções'
      } finally {
        this.loading = false
      }
    },

    async createReproducao(reproducaoData) {
      try {
        const response = await api.post('/api/reproducao', reproducaoData)
        await this.fetchReproducoes()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao criar reprodução'
      }
    },

    async updateReproducao(id, reproducaoData) {
      try {
        const response = await api.put(`/api/reproducao/${id}`, reproducaoData)
        await this.fetchReproducoes()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar reprodução'
      }
    },

    async deleteReproducao(id) {
      try {
        await api.delete(`/api/reproducao/${id}`)
        await this.fetchReproducoes()
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir reprodução'
      }
    },

    async fetchHistoricoEgua(eguaId) {
      try {
        const response = await api.get(`/api/reproducao/egua/${eguaId}/historico`)
        this.historicoEgua = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar histórico da égua'
      }
    },

    async fetchEstatisticas(ano = null) {
      try {
        const params = ano ? { ano } : {}
        const response = await api.get('/api/reproducao/relatorio/estatisticas', { params })
        this.estatisticas = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar estatísticas'
      }
    },

    async fetchCalendarioEventos(dias = 60) {
      try {
        const response = await api.get(`/api/reproducao/calendario/eventos?dias=${dias}`)
        this.calendarioEventos = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar eventos do calendário'
      }
    },

    setFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
    },

    clearFilters() {
      this.filters = {
        egua_id: null,
        parceiro_id: null,
        tipo_cobertura: null,
        resultado: null,
        status: null,
        data_inicio: '',
        data_fim: '',
      }
    },

    setPagination(newPagination) {
      this.pagination = { ...this.pagination, ...newPagination }
    },
  },
})
