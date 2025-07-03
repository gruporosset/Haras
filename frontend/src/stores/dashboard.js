import { defineStore } from 'pinia'
import api from '../boot/api'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    loading: false,
    dashboardData: null,

    // Filtros
    filtros: {
      data_inicio: null,
      data_fim: null,
      proprietario: null,
    },

    // Dados separados para facilitar componentes
    kpis: {
      total_animais: 0,
      total_terrenos: 0,
      animais_tratamento: 0,
      alertas_estoque: 0,
      proximas_aplicacoes: 0,
      gestacoes_ativas: 0,
    },

    alertas_saude: [],
    alertas_estoque: [],
    custos_proprietarios: [],
    grafico_custos_mensal: null,
    grafico_distribuicao_animais: null,
    ultimo_update: null,

    // Relatórios
    relatorio_animal: null,
    relatorio_terreno: null,
  }),

  getters: {
    totalAlertas: state => {
      return state.alertas_saude.length + state.alertas_estoque.length
    },

    alertasCriticos: state => {
      return [
        ...state.alertas_saude.filter(a => a.prioridade === 'ALTA'),
        ...state.alertas_estoque.filter(a => a.status === 'CRITICO'),
      ]
    },

    custoTotal: state => {
      return state.custos_proprietarios.reduce(
        (total, item) => total + item.total_geral,
        0
      )
    },
  },

  actions: {
    // ========================================
    // DASHBOARD PRINCIPAL
    // ========================================

    async loadDashboard(filtros = {}) {
      this.loading = true
      try {
        const params = {
          ...this.filtros,
          ...filtros,
        }

        // Remover valores null/undefined
        Object.keys(params).forEach(key => {
          if (
            params[key] === null ||
            params[key] === undefined ||
            params[key] === ''
          ) {
            delete params[key]
          }
        })

        const response = await api.get('/api/dashboard/', { params })

        this.dashboardData = response.data
        this.kpis = response.data.kpis
        this.alertas_saude = response.data.alertas_saude
        this.alertas_estoque = response.data.alertas_estoque
        this.custos_proprietarios = response.data.custos_proprietarios
        this.grafico_custos_mensal = response.data.grafico_custos_mensal
        this.grafico_distribuicao_animais =
          response.data.grafico_distribuicao_animais
        this.ultimo_update = response.data.ultimo_update

        return response.data
      } catch (error) {
        console.error('Erro ao carregar dashboard:', error)
        throw error.response?.data?.detail || 'Erro ao carregar dashboard'
      } finally {
        this.loading = false
      }
    },

    // ========================================
    // RELATÓRIOS
    // ========================================

    async loadRelatorioAnimal(animalId, filtros = {}) {
      this.loading = true
      try {
        const params = {
          data_inicio: filtros.data_inicio || this.filtros.data_inicio,
          data_fim: filtros.data_fim || this.filtros.data_fim,
        }

        // Remover valores null/undefined
        Object.keys(params).forEach(key => {
          if (
            params[key] === null ||
            params[key] === undefined ||
            params[key] === ''
          ) {
            delete params[key]
          }
        })

        const response = await api.get(
          `/api/dashboard/relatorio-animal/${animalId}`,
          { params }
        )
        this.relatorio_animal = response.data
        return response.data
      } catch (error) {
        console.error('Erro ao carregar relatório do animal:', error)
        throw (
          error.response?.data?.detail || 'Erro ao carregar relatório do animal'
        )
      } finally {
        this.loading = false
      }
    },

    async loadRelatorioTerreno(terrenoId) {
      this.loading = true
      try {
        const response = await api.get(
          `/api/dashboard/relatorio-terreno/${terrenoId}`
        )
        this.relatorio_terreno = response.data
        return response.data
      } catch (error) {
        console.error('Erro ao carregar relatório do terreno:', error)
        throw (
          error.response?.data?.detail ||
          'Erro ao carregar relatório do terreno'
        )
      } finally {
        this.loading = false
      }
    },

    // ========================================
    // FILTROS E UTILITÁRIOS
    // ========================================

    setFiltros(novosFiltros) {
      this.filtros = { ...this.filtros, ...novosFiltros }
    },

    clearFiltros() {
      this.filtros = {
        data_inicio: null,
        data_fim: null,
        proprietario: null,
      }
    },

    async refreshDashboard() {
      return await this.loadDashboard(this.filtros)
    },

    // ========================================
    // HELPERS
    // ========================================

    getPrioridadeColor(prioridade) {
      const cores = {
        ALTA: 'negative',
        MEDIA: 'warning',
        BAIXA: 'info',
      }
      return cores[prioridade] || 'grey'
    },

    getStatusEstoqueColor(status) {
      const cores = {
        CRITICO: 'negative',
        BAIXO: 'warning',
        VENCENDO: 'orange',
        OK: 'positive',
      }
      return cores[status] || 'grey'
    },

    formatarMoeda(valor) {
      if (!valor) return 'R$ 0,00'
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
      }).format(valor)
    },

    formatarData(data) {
      if (!data) return '-'
      return new Date(data).toLocaleDateString('pt-BR')
    },

    calcularDiasAtraso(dataVencimento) {
      if (!dataVencimento) return 0
      const hoje = new Date()
      const vencimento = new Date(dataVencimento)
      const diffTime = hoje - vencimento
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    },

    getIconeAlerta(tipoAlerta) {
      const icones = {
        VACINA_VENCIDA: 'vaccines',
        VACINA_PROXIMA: 'schedule',
        VERMIFUGO_VENCIDO: 'medication',
        VERMIFUGO_PROXIMO: 'medication_liquid',
        TRATAMENTO_PENDENTE: 'healing',
      }
      return icones[tipoAlerta] || 'warning'
    },

    getTipoEstoqueLabel(tipo) {
      const tipos = {
        MEDICAMENTO: 'Medicamento',
        RACAO: 'Ração',
        MANEJO: 'Manejo',
      }
      return tipos[tipo] || tipo
    },
  },
})
