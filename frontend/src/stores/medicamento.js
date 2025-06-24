// frontend/src/stores/medicamento.js
import { defineStore } from 'pinia'
import api from '../boot/api'

export const useMedicamentoStore = defineStore('medicamento', {
  state: () => ({
    medicamentos: [],
    movimentacoes: [],
    estoqueBaixo: [],
    previsaoConsumo: [],
    movimentacaoPeriodo: [],
    consumoPorAnimal: [],
    loading: false,
    filters: {
      nome: '',
      forma_farmaceutica: null,
      estoque_baixo: false,
      vencimento: null,
      ativo: 'S',
      data_inicio: '',
      data_fim: '',
      medicamento_id: null,
      animal_id: null,
      tipo: null,
    },
    pagination: {
      page: 1,
      rowsPerPage: 10,
      rowsNumber: 0,
      sortBy: 'NOME',
      descending: false,
    },
  }),

  getters: {
    formasFarmaceuticas: () => [
      { value: 'INJETAVEL', label: 'Injetável' },
      { value: 'ORAL', label: 'Oral' },
      { value: 'TOPICO', label: 'Tópico' },
    ],

    unidadesMedida: () => [
      { value: 'ML', label: 'Mililitros (ml)' },
      { value: 'G', label: 'Gramas (g)' },
      { value: 'COMPRIMIDO', label: 'Comprimidos' },
      { value: 'DOSE', label: 'Doses' },
      { value: 'AMPOLA', label: 'Ampolas' },
      { value: 'FRASCO', label: 'Frascos' },
    ],

    tiposMovimentacao: () => [
      { value: 'ENTRADA', label: 'Entrada' },
      { value: 'SAIDA', label: 'Saída' },
      { value: 'AJUSTE', label: 'Ajuste' },
    ],

    medicamentosAtivos: (state) => state.medicamentos.filter((m) => m.ATIVO === 'S'),

    medicamentosComEstoque: (state) => {
      return state.medicamentos.filter((m) => m.ATIVO === 'S' && m.ESTOQUE_ATUAL > 0)
    },

    alertasEstoque: (state) => {
      return state.medicamentos.filter(
        (m) =>
          m.ATIVO === 'S' &&
          (m.status_estoque === 'ESTOQUE_BAIXO' ||
            m.status_estoque === 'VENCENDO' ||
            m.status_estoque === 'VENCIDO'),
      )
    },

    totalValorEstoque: (state) => {
      return state.medicamentos
        .filter((m) => m.ATIVO === 'S')
        .reduce((total, m) => total + (m.valor_estoque || 0), 0)
    },

    estatisticasGerais: (state) => {
      const ativos = state.medicamentosAtivos
      const comEstoque = state.medicamentosComEstoque
      const alertas = state.alertasEstoque

      return {
        totalMedicamentos: ativos.length,
        comEstoque: comEstoque.length,
        semEstoque: ativos.length - comEstoque.length,
        alertas: alertas.length,
        valorTotal: state.totalValorEstoque,
      }
    },
  },

  actions: {
    // === MEDICAMENTOS ===
    async fetchMedicamentos(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          ...this.filters,
          ...params.filters,
        }

        // Converter objetos select para valores
        if (queryParams.forma_farmaceutica?.value) {
          queryParams.forma_farmaceutica = queryParams.forma_farmaceutica.value
        }

        const response = await api.get('/api/medicamentos', { params: queryParams })
        this.medicamentos = response.data.medicamentos
        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit,
        }

        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar medicamentos'
      } finally {
        this.loading = false
      }
    },

    async createMedicamento(medicamentoData) {
      try {
        const response = await api.post('/api/medicamentos', medicamentoData)
        await this.fetchMedicamentos()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao criar medicamento'
      }
    },

    async updateMedicamento(id, medicamentoData) {
      try {
        const response = await api.put(`/api/medicamentos/${id}`, medicamentoData)
        await this.fetchMedicamentos()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar medicamento'
      }
    },

    async deleteMedicamento(id) {
      try {
        await api.delete(`/api/medicamentos/${id}`)
        await this.fetchMedicamentos()
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir medicamento'
      }
    },

    async getMedicamento(id) {
      try {
        const response = await api.get(`/api/medicamentos/${id}`)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar medicamento'
      }
    },

    // === ESTOQUE ===
    async entradaEstoque(entradaData) {
      try {
        const response = await api.post('/api/medicamentos/entrada-estoque', entradaData)
        await this.fetchMedicamentos()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao registrar entrada'
      }
    },

    async aplicarMedicamento(aplicacaoData) {
      try {
        const response = await api.post('/api/medicamentos/aplicar-medicamento', aplicacaoData)
        await this.fetchMedicamentos()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao aplicar medicamento'
      }
    },

    // === MOVIMENTAÇÕES ===
    async fetchMovimentacoes(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          ...this.filters,
          ...params.filters,
        }

        // Converter objetos select
        if (queryParams.medicamento_id?.value) {
          queryParams.medicamento_id = queryParams.medicamento_id.value
        }
        if (queryParams.animal_id?.value) {
          queryParams.animal_id = queryParams.animal_id.value
        }
        if (queryParams.tipo?.value) {
          queryParams.tipo = queryParams.tipo.value
        }

        const response = await api.get('/api/medicamentos/movimentacoes', { params: queryParams })

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

    // === RELATÓRIOS ===
    async fetchEstoqueBaixo(diasVencimento = 30) {
      try {
        const response = await api.get('/api/medicamentos/relatorio/estoque-baixo', {
          params: { dias_vencimento: diasVencimento },
        })
        this.estoqueBaixo = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar estoque baixo'
      }
    },

    async fetchPrevisaoConsumo(diasAnalise = 90) {
      try {
        const response = await api.get('/api/medicamentos/relatorio/previsao-consumo', {
          params: { dias_analise: diasAnalise },
        })
        this.previsaoConsumo = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar previsão de consumo'
      }
    },

    async fetchMovimentacaoPeriodo(dataInicio = null, dataFim = null) {
      try {
        const params = {}
        if (dataInicio) params.data_inicio = dataInicio
        if (dataFim) params.data_fim = dataFim

        const response = await api.get('/api/medicamentos/relatorio/movimentacao-periodo', {
          params,
        })
        this.movimentacaoPeriodo = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar movimentação do período'
      }
    },

    async fetchConsumoPorAnimal(animalId, dataInicio = null, dataFim = null) {
      try {
        const params = {}
        if (dataInicio) params.data_inicio = dataInicio
        if (dataFim) params.data_fim = dataFim

        const response = await api.get(`/api/medicamentos/relatorio/consumo-animal/${animalId}`, {
          params,
        })
        this.consumoPorAnimal = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar consumo por animal'
      }
    },

    // === AUTOCOMPLETE ===
    async autocompleteMedicamentos(termo) {
      try {
        const response = await api.get('/api/medicamentos/autocomplete', {
          params: { termo, limit: 20 },
        })
        return response.data
      } catch (error) {
        console.error('Erro no autocomplete:', error)
        return []
      }
    },

    // === OPÇÕES PARA SELECTS ===
    async loadMedicamentoOptions() {
      await this.fetchMedicamentos({ limit: 100 })

      return this.medicamentosAtivos.map((med) => ({
        value: med.ID,
        label: `${med.NOME} (${med.ESTOQUE_ATUAL} ${med.UNIDADE_MEDIDA})`,
        estoque: med.ESTOQUE_ATUAL,
        unidade: med.UNIDADE_MEDIDA,
        forma: med.FORMA_FARMACEUTICA,
        carencia: med.PERIODO_CARENCIA,
      }))
    },

    // === UTILITÁRIOS ===
    setFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
    },

    clearFilters() {
      this.filters = {
        nome: '',
        forma_farmaceutica: null,
        estoque_baixo: false,
        vencimento: null,
        ativo: 'S',
        data_inicio: '',
        data_fim: '',
        medicamento_id: null,
        animal_id: null,
        tipo: null,
      }
    },

    setPagination(newPagination) {
      this.pagination = { ...this.pagination, ...newPagination }
    },

    // === MÉTODOS AUXILIARES ===
    getFormaLabel(forma) {
      const formas = {
        INJETAVEL: 'Injetável',
        ORAL: 'Oral',
        TOPICO: 'Tópico',
      }
      return formas[forma] || forma
    },

    getStatusEstoqueColor(status) {
      const colors = {
        OK: 'positive',
        ESTOQUE_BAIXO: 'warning',
        VENCENDO: 'orange',
        VENCIDO: 'negative',
      }
      return colors[status] || 'grey'
    },

    getStatusEstoqueLabel(status) {
      const labels = {
        OK: 'Normal',
        ESTOQUE_BAIXO: 'Estoque Baixo',
        VENCENDO: 'Vencendo',
        VENCIDO: 'Vencido',
      }
      return labels[status] || status
    },

    getTipoMovimentacaoColor(tipo) {
      const colors = {
        ENTRADA: 'positive',
        SAIDA: 'negative',
        AJUSTE: 'info',
      }
      return colors[tipo] || 'grey'
    },

    getTipoMovimentacaoLabel(tipo) {
      const labels = {
        ENTRADA: 'Entrada',
        SAIDA: 'Saída',
        AJUSTE: 'Ajuste',
      }
      return labels[tipo] || tipo
    },

    getRecomendacaoColor(recomendacao) {
      const colors = {
        COMPRAR_URGENTE: 'negative',
        COMPRAR_BREVE: 'warning',
        OK: 'positive',
        SEM_CONSUMO: 'grey',
      }
      return colors[recomendacao] || 'grey'
    },

    getRecomendacaoLabel(recomendacao) {
      const labels = {
        COMPRAR_URGENTE: 'Comprar Urgente',
        COMPRAR_BREVE: 'Comprar em Breve',
        OK: 'Estoque OK',
        SEM_CONSUMO: 'Sem Consumo',
      }
      return labels[recomendacao] || recomendacao
    },

    // === VALIDAÇÕES ===
    validarEstoque(medicamentoId, quantidadeNecessaria) {
      const medicamento = this.medicamentos.find((m) => m.ID === medicamentoId)
      if (!medicamento) {
        return { valido: false, erro: 'Medicamento não encontrado' }
      }

      if (medicamento.ESTOQUE_ATUAL < quantidadeNecessaria) {
        return {
          valido: false,
          erro: `Estoque insuficiente. Disponível: ${medicamento.ESTOQUE_ATUAL} ${medicamento.UNIDADE_MEDIDA}`,
        }
      }

      return { valido: true }
    },

    // === CÁLCULOS ===
    calcularValorAplicacao(medicamentoId, quantidade) {
      const medicamento = this.medicamentos.find((m) => m.ID === medicamentoId)
      if (!medicamento || !medicamento.PRECO_UNITARIO) return null
      return (medicamento.PRECO_UNITARIO * quantidade).toFixed(2)
    },

    calcularDiasEstoque(medicamentoId, consumoMedio) {
      const medicamento = this.medicamentos.find((m) => m.ID === medicamentoId)
      if (!medicamento || !consumoMedio || consumoMedio <= 0) return null
      return Math.floor(medicamento.ESTOQUE_ATUAL / consumoMedio)
    },

    // === BUSCA E FILTROS AVANÇADOS ===
    searchMedicamentos(termo) {
      if (!termo) return this.medicamentosComEstoque

      const termoLower = termo.toLowerCase()
      return this.medicamentosComEstoque.filter(
        (med) =>
          med.NOME.toLowerCase().includes(termoLower) ||
          (med.PRINCIPIO_ATIVO && med.PRINCIPIO_ATIVO.toLowerCase().includes(termoLower)) ||
          (med.FABRICANTE && med.FABRICANTE.toLowerCase().includes(termoLower)),
      )
    },

    getMedicamentosByForma(forma) {
      return this.medicamentosComEstoque.filter((med) => med.FORMA_FARMACEUTICA === forma)
    },

    getMedicamentosVencendo(dias = 30) {
      return this.medicamentos.filter(
        (med) =>
          med.ATIVO === 'S' && med.status_estoque === 'VENCENDO' && med.dias_vencimento <= dias,
      )
    },
  },
})
