// frontend/src/stores/crescimento.js - ATUALIZAÇÃO STORE SAÚDE

import { defineStore } from 'pinia'
import api from '../boot/api'

export const useCrescimentoStore = defineStore('crescimento', {
  state: () => ({
    crescimentos: [],
    registrosSaude: [],
    medicamentosOptions: [], // Para autocomplete
    loading: false,
    filters: {
      animal_id: null,
      tipo_registro: null,
      data_inicio: '',
      data_fim: '',
    },
    pagination: {
      page: 1,
      rowsPerPage: 10,
      rowsNumber: 0,
      sortBy: 'DATA_OCORRENCIA',
      descending: true,
    },
  }),

  getters: {
    tiposRegistro: () => [
      { value: 'VACINA', label: 'Vacina' },
      { value: 'VERMIFUGO', label: 'Vermífugo' },
      { value: 'MEDICAMENTO', label: 'Medicamento' },
      { value: 'EXAME', label: 'Exame' },
      { value: 'CONSULTA', label: 'Consulta' },
      { value: 'CIRURGIA', label: 'Cirurgia' },
      { value: 'TRATAMENTO', label: 'Tratamento' },
    ],

    registrosPorTipo: (state) => (tipo) => {
      return state.registrosSaude.filter((r) => r.TIPO_REGISTRO === tipo)
    },

    proximasAplicacoes: (state) => {
      const hoje = new Date()
      return state.registrosSaude
        .filter((r) => r.PROXIMA_APLICACAO && new Date(r.PROXIMA_APLICACAO) >= hoje)
        .sort((a, b) => new Date(a.PROXIMA_APLICACAO) - new Date(b.PROXIMA_APLICACAO))
    },

    estatisticasSaude: (state) => {
      const totalRegistros = state.registrosSaude.length
      const registrosPorTipo = {}

      state.registrosSaude.forEach((registro) => {
        const tipo = registro.TIPO_REGISTRO
        registrosPorTipo[tipo] = (registrosPorTipo[tipo] || 0) + 1
      })

      return {
        totalRegistros,
        registrosPorTipo,
        proximasAplicacoes: state.proximasAplicacoes.length,
      }
    },
  },

  actions: {
    // === SAÚDE ===
    async fetchRegistrosSaude(params = {}) {
      this.loading = true
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
        if (queryParams.tipo_registro?.value) {
          queryParams.tipo_registro = queryParams.tipo_registro.value
        }

        const response = await api.get('/api/crescimento-saude/saude', { params: queryParams })

        this.registrosSaude = response.data.registros
        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit,
        }

        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar registros de saúde'
      } finally {
        this.loading = false
      }
    },

    async createRegistroSaude(registroData) {
      try {
        const response = await api.post('/api/crescimento-saude/saude', registroData)
        await this.fetchRegistrosSaude()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao criar registro de saúde'
      }
    },

    async updateRegistroSaude(id, registroData) {
      try {
        const response = await api.put(`/api/crescimento-saude/saude/${id}`, registroData)
        await this.fetchRegistrosSaude()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar registro de saúde'
      }
    },

    async deleteRegistroSaude(id) {
      try {
        await api.delete(`/api/crescimento-saude/saude/${id}`)
        await this.fetchRegistrosSaude()
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir registro de saúde'
      }
    },

    // === MEDICAMENTOS AUTOCOMPLETE ===
    async autocompleteMedicamentos(termo) {
      try {
        if (!termo || termo.length < 2) return []

        const response = await api.get('/api/crescimento-saude/medicamentos-autocomplete', {
          params: { termo, limit: 20 },
        })

        this.medicamentosOptions = response.data
        return response.data
      } catch (error) {
        console.error('Erro no autocomplete de medicamentos:', error)
        return []
      }
    },

    async validarEstoqueMedicamento(medicamentoId, quantidade) {
      try {
        const response = await api.post(
          '/api/crescimento-saude/validar-estoque-medicamento',
          null,
          {
            params: { medicamento_id: medicamentoId, quantidade },
          },
        )
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao validar estoque'
      }
    },

    // === CRESCIMENTO (mantendo funcionalidades existentes) ===
    async fetchCrescimentos(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          ...this.filters,
          ...params.filters,
        }

        if (queryParams.animal_id?.value) {
          queryParams.animal_id = queryParams.animal_id.value
        }

        const response = await api.get('/api/crescimento-saude/crescimento', {
          params: queryParams,
        })

        this.crescimentos = response.data.registros
        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit,
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

    // === UTILITÁRIOS ===
    setFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
    },

    clearFilters() {
      this.filters = {
        animal_id: null,
        tipo_registro: null,
        data_inicio: '',
        data_fim: '',
      }
    },

    setPagination(newPagination) {
      this.pagination = { ...this.pagination, ...newPagination }
    },

    // === MÉTODOS AUXILIARES ===
    getTipoRegistroLabel(tipo) {
      const tipos = {
        VACINA: 'Vacina',
        VERMIFUGO: 'Vermífugo',
        MEDICAMENTO: 'Medicamento',
        EXAME: 'Exame',
        CONSULTA: 'Consulta',
        CIRURGIA: 'Cirurgia',
        TRATAMENTO: 'Tratamento',
      }
      return tipos[tipo] || tipo
    },

    getTipoRegistroColor(tipo) {
      const colors = {
        VACINA: 'positive',
        VERMIFUGO: 'warning',
        MEDICAMENTO: 'primary',
        EXAME: 'info',
        CONSULTA: 'secondary',
        CIRURGIA: 'negative',
        TRATAMENTO: 'accent',
      }
      return colors[tipo] || 'grey'
    },

    // === VALIDAÇÕES ===
    validarFormularioSaude(form) {
      const erros = []

      if (!form.ID_ANIMAL) {
        erros.push('Animal é obrigatório')
      }

      if (!form.TIPO_REGISTRO) {
        erros.push('Tipo de registro é obrigatório')
      }

      if (!form.DATA_OCORRENCIA) {
        erros.push('Data de ocorrência é obrigatória')
      }

      // Se selecionou medicamento, deve informar quantidade
      if (form.ID_MEDICAMENTO && !form.QUANTIDADE_APLICADA) {
        erros.push('Quantidade aplicada é obrigatória quando medicamento é selecionado')
      }

      // Se informou quantidade, deve selecionar medicamento
      if (form.QUANTIDADE_APLICADA && !form.ID_MEDICAMENTO) {
        erros.push('Medicamento deve ser selecionado quando quantidade é informada')
      }

      return {
        valido: erros.length === 0,
        erros,
      }
    },

    // === CÁLCULOS ===
    calcularDiasProximaAplicacao(dataOcorrencia, proximaAplicacao) {
      if (!proximaAplicacao) return null

      const hoje = new Date()
      const proxima = new Date(proximaAplicacao)
      const diferenca = proxima.getTime() - hoje.getTime()

      return Math.ceil(diferenca / (1000 * 3600 * 24))
    },

    // === BUSCA E FILTROS ===
    getRegistrosByAnimal(animalId) {
      return this.registrosSaude.filter((registro) => registro.ID_ANIMAL === animalId)
    },

    getUltimoRegistroTipo(animalId, tipo) {
      const registros = this.registrosSaude
        .filter((r) => r.ID_ANIMAL === animalId && r.TIPO_REGISTRO === tipo)
        .sort((a, b) => new Date(b.DATA_OCORRENCIA) - new Date(a.DATA_OCORRENCIA))

      return registros.length > 0 ? registros[0] : null
    },

    // === RELATÓRIOS ===
    async getEstatisticasSaude() {
      try {
        const response = await api.get('/api/crescimento-saude/estatisticas-saude')
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar estatísticas'
      }
    },

    async getProximasAplicacoes(dias = 30) {
      try {
        const response = await api.get('/api/crescimento-saude/proximas-aplicacoes', {
          params: { dias },
        })
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar próximas aplicações'
      }
    },
  },
})
