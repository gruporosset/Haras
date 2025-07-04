// frontend/src/stores/ferrageamento.js
import { defineStore } from 'pinia'
import api from '../boot/api'
import { prepareFormData } from 'src/utils/dateUtils'
import { ErrorHandler } from 'src/utils/errorHandler'

export const useFerrageamentoStore = defineStore('ferrageamento', {
  state: () => ({
    ferrageamentos: [],
    alertasVencimento: [],
    estatisticasAnimais: [],
    estatisticasFerradores: [],
    relatorio: null,
    loading: false,
    filters: {
      animal_id: null,
      tipo_registro: null,
      ferrador: '',
      data_inicio: '',
      data_fim: '',
      apenas_vencidos: false,
      apenas_com_problemas: false,
    },
    pagination: {
      page: 1,
      rowsPerPage: 50,
      rowsNumber: 0,
      sortBy: 'DATA_OCORRENCIA',
      descending: true,
    },
  }),

  getters: {
    tiposFerrageamento: () => [
      { value: 'FERRAGEAMENTO', label: 'Ferrageamento' },
      { value: 'CASQUEAMENTO', label: 'Casqueamento' },
      { value: 'FERRAGEAMENTO_CORRETIVO', label: 'Ferrageamento Corretivo' },
      { value: 'CASQUEAMENTO_TERAPEUTICO', label: 'Casqueamento Terapêutico' },
    ],

    tiposFerradura: () => [
      { value: 'Comum', label: 'Comum' },
      { value: 'Ortopédica', label: 'Ortopédica' },
      { value: 'Alumínio', label: 'Alumínio' },
      { value: 'Borracha', label: 'Borracha' },
      { value: 'Colagem', label: 'Colagem' },
      { value: 'Descalço', label: 'Descalço' },
    ],

    membrosOpcoes: () => [
      { value: 'TODOS', label: 'Todos os membros' },
      { value: 'AD', label: 'Anterior Direito' },
      { value: 'AE', label: 'Anterior Esquerdo' },
      { value: 'PD', label: 'Posterior Direito' },
      { value: 'PE', label: 'Posterior Esquerdo' },
    ],

    statusCasco: () => [
      { value: 'BOM', label: 'Bom' },
      { value: 'REGULAR', label: 'Regular' },
      { value: 'RUIM', label: 'Ruim' },
      { value: 'PROBLEMA', label: 'Problema' },
    ],

    ferrageamentosVencidos: state => {
      return state.ferrageamentos.filter(
        f =>
          f.status_vencimento === 'VENCIDO' ||
          f.status_vencimento === 'VENCE_SEMANA'
      )
    },

    ferrageamentosEmDia: state => {
      return state.ferrageamentos.filter(f => f.status_vencimento === 'EM_DIA')
    },

    custoTotalMes: state => {
      const agora = new Date()
      const inicioMes = new Date(agora.getFullYear(), agora.getMonth(), 1)

      return state.ferrageamentos
        .filter(f => {
          const dataOcorrencia = new Date(f.DATA_OCORRENCIA)
          return dataOcorrencia >= inicioMes && f.CUSTO
        })
        .reduce((total, f) => total + (f.CUSTO || 0), 0)
    },

    ferradoresMaisAtivos: state => {
      const contadorFerradores = {}

      state.ferrageamentos.forEach(f => {
        if (f.FERRADOR_RESPONSAVEL) {
          if (!contadorFerradores[f.FERRADOR_RESPONSAVEL]) {
            contadorFerradores[f.FERRADOR_RESPONSAVEL] = {
              nome: f.FERRADOR_RESPONSAVEL,
              total: 0,
              custo: 0,
            }
          }
          contadorFerradores[f.FERRADOR_RESPONSAVEL].total++
          contadorFerradores[f.FERRADOR_RESPONSAVEL].custo += f.CUSTO || 0
        }
      })
      return Object.values(contadorFerradores)
        .sort((a, b) => b.total - a.total)
        .slice(0, 5)
    },

    estatisticasGerais: state => {
      const total = state.ferrageamentos.length
      const vencidos = state.ferrageamentosVencidos.length
      const emDia = state.ferrageamentosEmDia.length
      const custoTotal = state.ferrageamentos.reduce(
        (sum, f) => sum + (f.CUSTO || 0),
        0
      )

      return {
        totalRegistros: total,
        vencidos,
        emDia,
        custoTotal,
        alertasAtivos: state.alertasVencimento.length,
      }
    },
  },

  actions: {
    // === CRUD FERRAGEAMENTO ===
    async fetchFerrageamentos(params = {}) {
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

        const response = await api.get('/api/ferrageamento', {
          params: queryParams,
        })
        this.ferrageamentos = response.data.ferrageamentos
        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit,
        }

        return response.data
      } catch (error) {
        throw (
          error.response?.data?.detail ||
          'Erro ao buscar registros de ferrageamento'
        )
      } finally {
        this.loading = false
      }
    },

    async createFerrageamento(ferrageamentoData) {
      try {
        const dados = prepareFormData(ferrageamentoData, [
          'DATA_OCORRENCIA',
          'PROXIMA_AVALIACAO',
        ])
        const response = await api.post('/api/ferrageamento', dados)
        await this.fetchFerrageamentos()
        return response.data
      } catch (error) {
        throw (
          error.response?.data?.detail ||
          'Erro ao criar registro de ferrageamento'
        )
      }
    },

    async updateFerrageamento(id, ferrageamentoData) {
      try {
        const dados = prepareFormData(ferrageamentoData, [
          'DATA_OCORRENCIA',
          'PROXIMA_AVALIACAO',
        ])
        const response = await api.put(`/api/ferrageamento/${id}`, dados)
        await this.fetchFerrageamentos()
        return response.data
      } catch (error) {
        throw (
          error.response?.data?.detail ||
          'Erro ao atualizar registro de ferrageamento'
        )
      }
    },

    async deleteFerrageamento(id) {
      try {
        await api.delete(`/api/ferrageamento/${id}`)
        await this.fetchFerrageamentos()
      } catch (error) {
        throw (
          error.response?.data?.detail ||
          'Erro ao excluir registro de ferrageamento'
        )
      }
    },

    async getFerrageamento(id) {
      try {
        const response = await api.get(`/api/ferrageamento/${id}`)
        return response.data
      } catch (error) {
        throw (
          error.response?.data?.detail ||
          'Erro ao buscar registro de ferrageamento'
        )
      }
    },

    // === APLICAÇÃO RÁPIDA ===
    async aplicacaoRapida(dadosAplicacao) {
      try {
        const response = await api.post(
          '/api/ferrageamento/aplicacao-rapida',
          dadosAplicacao
        )
        await this.fetchFerrageamentos()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro na aplicação rápida'
      }
    },

    // === ALERTAS E RELATÓRIOS ===
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

    async fetchEstatisticasAnimais(mesesPeriodo = 12) {
      try {
        const response = await api.get(
          '/api/ferrageamento/estatisticas/animais',
          {
            params: { meses_periodo: mesesPeriodo },
          }
        )
        this.estatisticasAnimais = response.data
        return response.data
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao buscar estatísticas de animais')
        return []
      }
    },

    async gerarRelatorio(filtros) {
      try {
        const response = await api.get('/api/ferrageamento/relatorio/resumo', {
          params: filtros,
        })
        this.relatorio = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao gerar relatório'
      }
    },

    // === FILTROS ===
    setFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
    },

    clearFilters() {
      this.filters = {
        animal_id: null,
        tipo_registro: null,
        ferrador: '',
        data_inicio: '',
        data_fim: '',
        apenas_vencidos: false,
        apenas_com_problemas: false,
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
        CASQUEAMENTO_TERAPEUTICO: 'purple',
      }
      return cores[tipo] || 'grey'
    },

    getStatusVencimentoColor(status) {
      const cores = {
        VENCIDO: 'negative',
        VENCE_SEMANA: 'warning',
        VENCE_QUINZENA: 'orange',
        EM_DIA: 'positive',
        SEM_AGENDAMENTO: 'grey',
      }
      return cores[status] || 'grey'
    },

    getStatusVencimentoLabel(status) {
      const labels = {
        VENCIDO: 'Vencido',
        VENCE_SEMANA: 'Vence esta semana',
        VENCE_QUINZENA: 'Vence em até 15 dias',
        EM_DIA: 'Em dia',
        SEM_AGENDAMENTO: 'Sem agendamento',
      }
      return labels[status] || status
    },

    getStatusCascoColor(status) {
      const cores = {
        BOM: 'positive',
        REGULAR: 'warning',
        RUIM: 'orange',
        PROBLEMA: 'negative',
      }
      return cores[status] || 'grey'
    },

    getMembroLabel(membro) {
      const membros = {
        TODOS: 'Todos os membros',
        AD: 'Anterior Direito',
        AE: 'Anterior Esquerdo',
        PD: 'Posterior Direito',
        PE: 'Posterior Esquerdo',
      }
      return membros[membro] || membro
    },

    // == GRAFICOS ==
    async getCustosEvolucaoMensal(meses) {
      console.log(meses)
      const response = await api.get(
        `/api/ferrageamento/grafico/custos-evolucao?meses=${meses}`
      )
      return response.data
    },

    // === VALIDAÇÕES ===
    validarProximaData(dataOcorrencia, proximaAvaliacao) {
      if (!proximaAvaliacao) return { valido: true }

      const dataOc = new Date(dataOcorrencia)
      const dataProx = new Date(proximaAvaliacao)

      if (dataProx <= dataOc) {
        return {
          valido: false,
          erro: 'Data da próxima avaliação deve ser posterior à data de ocorrência',
        }
      }

      return { valido: true }
    },

    calcularProximaData(tipoRegistro, dataOcorrencia, modalidade = 'GERAL') {
      const intervalos = {
        FERRAGEAMENTO: {
          CCE: 30,
          APARTACAO: 60,
          CORRIDA: 35,
          GERAL: 45,
        },
        CASQUEAMENTO: {
          GERAL: 40,
        },
        FERRAGEAMENTO_CORRETIVO: {
          GERAL: 21,
        },
        CASQUEAMENTO_TERAPEUTICO: {
          GERAL: 21,
        },
      }

      const dias = intervalos[tipoRegistro]?.[modalidade] || 45
      const data = new Date(dataOcorrencia)
      data.setDate(data.getDate() + dias)

      return data.toISOString().split('T')[0] // Retorna formato YYYY-MM-DD
    },

    // === DASHBOARD ===
    async carregarDashboard() {
      try {
        await Promise.all([
          this.fetchFerrageamentos({ limit: 10 }),
          this.fetchAlertasVencimento(15),
          this.fetchEstatisticasAnimais(6),
        ])
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao carregar dashboard')
      }
    },
  },
})
