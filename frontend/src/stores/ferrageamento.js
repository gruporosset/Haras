// frontend/src/stores/ferrageamento.js
import { defineStore } from 'pinia'
import api from '../boot/api'
import { ErrorHandler } from 'src/utils/errorHandler'

export const useFerrageamentoStore = defineStore('ferrageamento', {
  state: () => ({
    // Dados principais
    ferrageamentos: [],
    loading: false,

    // Paginação e filtros
    pagination: {
      page: 1,
      rowsPerPage: 50,
      rowsNumber: 0,
      sortBy: 'DATA_OCORRENCIA',
      descending: true,
    },

    filters: {
      animal_id: null,
      tipo_ferrageamento: null, // Atualizado para usar TIPO_FERRAGEAMENTO
      ferrador: '',
      data_inicio: '',
      data_fim: '',
      apenas_vencidos: false,
    },

    // Dados específicos
    alertasVencimento: [],
    estatisticasGerais: null,
    relatorioPeriodo: null,
    ferradores: [],
  }),

  getters: {
    // Getter para tipos de ferrageamento
    tiposFerrageamento: () => [
      { value: 'FERRAGEAMENTO', label: 'Ferrageamento' },
      { value: 'CASQUEAMENTO', label: 'Casqueamento' },
      { value: 'FERRAGEAMENTO_CORRETIVO', label: 'Ferrageamento Corretivo' },
      { value: 'CASQUEAMENTO_TERAPEUTICO', label: 'Casqueamento Terapêutico' },
    ],

    // Getter para tipos de ferradura
    tiposFerradura: () => [
      { value: 'NORMAL', label: 'Normal' },
      { value: 'CORRETIVA', label: 'Corretiva' },
      { value: 'TERAPEUTICA', label: 'Terapêutica' },
      { value: 'ESPECIAL', label: 'Especial' },
    ],

    // Getter para membros
    membrosOpcoes: () => [
      { value: 'AD', label: 'Anterior Direito' },
      { value: 'AE', label: 'Anterior Esquerdo' },
      { value: 'PD', label: 'Posterior Direito' },
      { value: 'PE', label: 'Posterior Esquerdo' },
      { value: 'TODOS', label: 'Todos os membros' },
    ],

    // Getter para status do casco
    statusCascoOpcoes: () => [
      { value: 'BOM', label: 'Bom' },
      { value: 'REGULAR', label: 'Regular' },
      { value: 'RUIM', label: 'Ruim' },
      { value: 'PROBLEMA', label: 'Problema' },
    ],

    // Getter para alertas por prioridade
    alertasPorPrioridade: state => {
      const alertas = {
        critico: state.alertasVencimento.filter(a => a.dias_vencimento < 0),
        urgente: state.alertasVencimento.filter(
          a => a.dias_vencimento >= 0 && a.dias_vencimento <= 7
        ),
        proximo: state.alertasVencimento.filter(
          a => a.dias_vencimento > 7 && a.dias_vencimento <= 15
        ),
      }
      return alertas
    },

    // Getter para ferrageamentos por status
    ferrageamentosPorStatus: state => {
      return state.ferrageamentos.reduce((acc, item) => {
        const status = item.status_avaliacao || 'SEM_AGENDAMENTO'
        if (!acc[status]) acc[status] = []
        acc[status].push(item)
        return acc
      }, {})
    },
  },

  actions: {
    // === CRUD BÁSICO ===
    async fetchFerrageamentos(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          ...this.filters,
          limit: this.pagination.rowsPerPage,
          offset: (this.pagination.page - 1) * this.pagination.rowsPerPage,
          ...params,
        }

        const response = await api.get('/api/ferrageamento/', {
          params: queryParams,
        })

        this.ferrageamentos = response.data

        // Buscar total se necessário para paginação
        if (params.includeTotal) {
          const countResponse = await api.get(
            '/api/ferrageamento/estatisticas/geral'
          )
          this.pagination.rowsNumber = countResponse.data.total_registros
        }

        return response.data
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao buscar ferrageamentos')
        return []
      } finally {
        this.loading = false
      }
    },

    async createFerrageamento(dados) {
      try {
        const response = await api.post('/api/ferrageamento/', dados)
        return response.data
      } catch (error) {
        throw (
          error.response?.data?.detail ||
          'Erro ao criar registro de ferrageamento'
        )
      }
    },

    async updateFerrageamento(id, dados) {
      try {
        const response = await api.put(`/api/ferrageamento/${id}`, dados)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar registro'
      }
    },

    async deleteFerrageamento(id) {
      try {
        await api.delete(`/api/ferrageamento/${id}`)

        // Remover da lista local
        const index = this.ferrageamentos.findIndex(f => f.ID === id)
        if (index !== -1) {
          this.ferrageamentos.splice(index, 1)
        }
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir registro'
      }
    },

    async getFerrageamento(id) {
      try {
        const response = await api.get(`/api/ferrageamento/${id}`)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar registro'
      }
    },

    // === APLICAÇÃO RÁPIDA ===
    async aplicacaoRapida(dados) {
      try {
        const response = await api.post(
          '/api/ferrageamento/aplicacao-rapida',
          dados
        )
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro na aplicação rápida'
      }
    },

    // === ALERTAS E ESTATÍSTICAS ===
    async fetchAlertasVencimento(diasAntecedencia = 15) {
      try {
        const response = await api.get(
          '/api/ferrageamento/alertas/vencimentos',
          {
            params: { dias_antecedencia: diasAntecedencia },
          }
        )
        this.alertasVencimento = response.data
        return response.data
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao buscar alertas de vencimento')
        return []
      }
    },

    async fetchEstatisticasGerais(params = {}) {
      try {
        const response = await api.get(
          '/api/ferrageamento/estatisticas/geral',
          {
            params,
          }
        )
        this.estatisticasGerais = response.data
        return response.data
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao buscar estatísticas gerais')
        return null
      }
    },

    async fetchRelatorioFerradores(ano = null) {
      try {
        const params = {}
        if (ano) params.ano = ano

        const response = await api.get(
          '/api/ferrageamento/relatorios/ferradores',
          {
            params,
          }
        )
        this.ferradores = response.data
        return response.data
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao buscar relatório de ferradores')
        return []
      }
    },

    async fetchRelatorioDetalhado(filtros = {}) {
      try {
        const response = await api.get(
          '/api/ferrageamento/relatorios/detalhado',
          {
            params: filtros,
          }
        )
        this.relatorioPeriodo = response.data
        return response.data
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao buscar relatório detalhado')
        return []
      }
    },

    // === FILTROS E PAGINAÇÃO ===
    setFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
    },

    clearFilters() {
      this.filters = {
        animal_id: null,
        tipo_ferrageamento: null,
        ferrador: '',
        data_inicio: '',
        data_fim: '',
        apenas_vencidos: false,
      }
    },

    setPagination(newPagination) {
      this.pagination = { ...this.pagination, ...newPagination }
    },

    // === MÉTODOS AUXILIARES ===
    getTipoLabel(tipo) {
      const tipos = {
        FERRAGEAMENTO: 'Ferrageamento',
        CASQUEAMENTO: 'Casqueamento',
        FERRAGEAMENTO_CORRETIVO: 'Ferrageamento Corretivo',
        CASQUEAMENTO_TERAPEUTICO: 'Casqueamento Terapêutico',
      }
      return tipos[tipo] || tipo
    },

    getTipoColor(tipo) {
      const cores = {
        FERRAGEAMENTO: 'blue',
        CASQUEAMENTO: 'green',
        FERRAGEAMENTO_CORRETIVO: 'orange',
        CASQUEAMENTO_TERAPEUTICO: 'red',
      }
      return cores[tipo] || 'grey'
    },

    getStatusCascoColor(status) {
      const cores = {
        BOM: 'green',
        REGULAR: 'orange',
        RUIM: 'red',
        PROBLEMA: 'red-10',
      }
      return cores[status] || 'grey'
    },

    getStatusAvaliacaoColor(status) {
      const cores = {
        OK: 'green',
        PROXIMO: 'orange',
        URGENTE: 'red',
        ATRASADO: 'red-10',
        SEM_AGENDAMENTO: 'grey',
      }
      return cores[status] || 'grey'
    },

    // === BUSCA E AUTOCOMPLETE ===
    async buscarFerradores(termo = '') {
      try {
        const response = await api.get(
          '/api/ferrageamento/relatorios/ferradores'
        )
        const ferradores = response.data.map(f => ({
          value: f.ferrador_nome,
          label: `${f.ferrador_nome} (${f.total_atendimentos} atendimentos)`,
        }))

        if (termo) {
          return ferradores.filter(f =>
            f.label.toLowerCase().includes(termo.toLowerCase())
          )
        }

        return ferradores
      } catch (error) {
        console.error('Erro ao buscar ferradores:', error)
        return []
      }
    },

    // === VALIDAÇÕES ===
    validarFormulario(dados) {
      const erros = []

      if (!dados.ID_ANIMAL) {
        erros.push('Animal é obrigatório')
      }

      if (!dados.TIPO_FERRAGEAMENTO) {
        erros.push('Tipo de ferrageamento é obrigatório')
      }

      if (!dados.DATA_OCORRENCIA) {
        erros.push('Data de ocorrência é obrigatória')
      }

      if (!dados.MEMBRO_TRATADO) {
        erros.push('Membro tratado é obrigatório')
      }

      // Validação de data
      if (
        dados.DATA_OCORRENCIA &&
        new Date(dados.DATA_OCORRENCIA) > new Date()
      ) {
        erros.push('Data de ocorrência não pode ser no futuro')
      }

      if (dados.PROXIMA_AVALIACAO && dados.DATA_OCORRENCIA) {
        if (
          new Date(dados.PROXIMA_AVALIACAO) <= new Date(dados.DATA_OCORRENCIA)
        ) {
          erros.push('Próxima avaliação deve ser após a data de ocorrência')
        }
      }

      return erros
    },

    // === FORMATAÇÃO ===
    formatarData(data) {
      if (!data) return ''
      return new Date(data).toLocaleDateString('pt-BR')
    },

    formatarCusto(valor) {
      if (!valor) return ''
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
      }).format(valor)
    },

    // === CALCULAR PRÓXIMA AVALIAÇÃO ===
    calcularProximaAvaliacao(tipoFerrageamento, dataOcorrencia) {
      const intervalos = {
        FERRAGEAMENTO: 45,
        CASQUEAMENTO: 40,
        FERRAGEAMENTO_CORRETIVO: 21,
        CASQUEAMENTO_TERAPEUTICO: 21,
      }

      const dias = intervalos[tipoFerrageamento] || 45
      const data = new Date(dataOcorrencia)
      data.setDate(data.getDate() + dias)

      return data.toISOString().split('T')[0] // Formato YYYY-MM-DD
    },
  },
})
