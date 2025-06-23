// frontend/src/stores/manejo.js
import { defineStore } from 'pinia'
import api from '../boot/api'

export const useManejoStore = defineStore('manejo', {
  state: () => ({
    produtos: [],
    analisesSolo: [],
    aplicacoes: [],
    terrenosBloqueados: [],
    cronograma: [],
    capacidadeOcupacao: [],
    historicoNutricional: [],
    loading: false,
    filters: {
      terreno_id: null,
      tipo_produto: null,
      tipo_manejo: null,
      data_inicio: '',
      data_fim: '',
      nome: '',
    },
    pagination: {
      page: 1,
      rowsPerPage: 10,
      rowsNumber: 0,
      sortBy: 'DATA_APLICACAO',
      descending: true,
    },
  }),

  getters: {
    tiposProduto: () => [
      { value: 'FERTILIZANTE', label: 'Fertilizante' },
      { value: 'DEFENSIVO', label: 'Defensivo' },
      { value: 'CORRETIVO', label: 'Corretivo' },
      { value: 'SEMENTE', label: 'Semente' },
    ],

    tiposManejo: () => [
      { value: 'ADUBACAO', label: 'Adubação' },
      { value: 'CALAGEM', label: 'Calagem' },
      { value: 'PLANTIO', label: 'Plantio' },
      { value: 'APLICACAO_DEFENSIVO', label: 'Aplicação Defensivo' },
      { value: 'ROÇADA', label: 'Roçada' },
      { value: 'IRRIGACAO', label: 'Irrigação' },
    ],

    produtosAtivos: (state) => state.produtos.filter((p) => p.ATIVO === 'S'),

    produtosByTipo: (state) => (tipo) => {
      return state.produtos.filter((p) => p.TIPO_PRODUTO === tipo && p.ATIVO === 'S')
    },

    terrenosComCarencia: (state) => {
      return state.terrenosBloqueados.filter((t) => t.dias_restantes > 0)
    },

    estatisticasGerais: (state) => {
      const totalAplicacoes = state.aplicacoes.length
      const custoTotal = state.aplicacoes.reduce((sum, a) => sum + (a.CUSTO_TOTAL || 0), 0)
      const terrenosManejados = new Set(state.aplicacoes.map((a) => a.ID_TERRENO)).size

      return {
        totalAplicacoes,
        custoTotal: custoTotal.toFixed(2),
        terrenosManejados,
        mediaAplicacoesPorTerreno:
          terrenosManejados > 0 ? (totalAplicacoes / terrenosManejados).toFixed(1) : 0,
      }
    },
  },

  actions: {
    // === PRODUTOS ===
    async fetchProdutos(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          ...this.filters,
          ...params.filters,
        }

        // Converter objetos select para valores
        if (queryParams.tipo_produto?.value) {
          queryParams.tipo_produto = queryParams.tipo_produto.value
        }

        const response = await api.get('/api/manejo/produtos', { params: queryParams })

        this.produtos = response.data.produtos
        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit,
        }

        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar produtos'
      } finally {
        this.loading = false
      }
    },

    async createProduto(produtoData) {
      try {
        const response = await api.post('/api/manejo/produtos', produtoData)
        await this.fetchProdutos()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao criar produto'
      }
    },

    async updateProduto(id, produtoData) {
      try {
        const response = await api.put(`/api/manejo/produtos/${id}`, produtoData)
        await this.fetchProdutos()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar produto'
      }
    },

    async deleteProduto(id) {
      try {
        await api.delete(`/api/manejo/produtos/${id}`)
        await this.fetchProdutos()
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir produto'
      }
    },

    // === ANÁLISES DE SOLO ===
    async fetchAnalisesSolo(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          ...this.filters,
          ...params.filters,
        }

        if (queryParams.terreno_id?.value) {
          queryParams.terreno_id = queryParams.terreno_id.value
        }

        const response = await api.get('/api/manejo/analises-solo', { params: queryParams })

        this.analisesSolo = response.data.analises
        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit,
        }

        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar análises de solo'
      } finally {
        this.loading = false
      }
    },

    async createAnaliseSolo(analiseData) {
      try {
        const response = await api.post('/api/manejo/analises-solo', analiseData)
        await this.fetchAnalisesSolo()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao criar análise de solo'
      }
    },

    async updateAnaliseSolo(id, analiseData) {
      try {
        const response = await api.put(`/api/manejo/analises-solo/${id}`, analiseData)
        await this.fetchAnalisesSolo()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar análise de solo'
      }
    },

    async deleteAnaliseSolo(id) {
      try {
        await api.delete(`/api/manejo/analises-solo/${id}`)
        await this.fetchAnalisesSolo()
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir análise de solo'
      }
    },

    async uploadLaudo(id, arquivo) {
      try {
        const formData = new FormData()
        formData.append('arquivo', arquivo)

        const response = await api.post(`/api/manejo/analises-solo/${id}/upload-laudo`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })

        await this.fetchAnalisesSolo()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao enviar laudo'
      }
    },

    // === APLICAÇÕES/MANEJO ===
    async fetchAplicacoes(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          ...this.filters,
          ...params.filters,
        }

        // Converter objetos select para valores
        if (queryParams.terreno_id?.value) {
          queryParams.terreno_id = queryParams.terreno_id.value
        }
        if (queryParams.tipo_manejo?.value) {
          queryParams.tipo_manejo = queryParams.tipo_manejo.value
        }

        const response = await api.get('/api/manejo/aplicacoes', { params: queryParams })

        this.aplicacoes = response.data.aplicacoes
        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit,
        }

        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar aplicações'
      } finally {
        this.loading = false
      }
    },

    async createAplicacao(aplicacaoData) {
      try {
        const response = await api.post('/api/manejo/aplicacoes', aplicacaoData)
        await this.fetchAplicacoes()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao criar aplicação'
      }
    },

    async updateAplicacao(id, aplicacaoData) {
      try {
        const response = await api.put(`/api/manejo/aplicacoes/${id}`, aplicacaoData)
        await this.fetchAplicacoes()
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar aplicação'
      }
    },

    async deleteAplicacao(id) {
      try {
        await api.delete(`/api/manejo/aplicacoes/${id}`)
        await this.fetchAplicacoes()
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir aplicação'
      }
    },

    // === VALIDAÇÕES ===
    async fetchTerrenosBloqueados() {
      try {
        const response = await api.get('/api/manejo/terrenos-bloqueados')
        this.terrenosBloqueados = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar terrenos bloqueados'
      }
    },

    async validarMovimentacao(terrenoId) {
      try {
        const response = await api.post('/api/manejo/validar-movimentacao', null, {
          params: { terreno_id: terrenoId },
        })
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao validar movimentação'
      }
    },

    // === RELATÓRIOS ===
    async fetchCronograma(dias = 30, terrenoId = null) {
      try {
        const params = { dias }
        if (terrenoId) {
          params.terreno_id = terrenoId
        }

        const response = await api.get('/api/manejo/relatorio/cronograma', { params })
        this.cronograma = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar cronograma'
      }
    },

    async fetchCapacidadeOcupacao() {
      try {
        const response = await api.get('/api/manejo/relatorio/capacidade-ocupacao')
        this.capacidadeOcupacao = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar capacidade de ocupação'
      }
    },

    async fetchHistoricoNutricional(ano = null) {
      try {
        const params = ano ? { ano } : {}
        const response = await api.get('/api/manejo/relatorio/historico-nutricional', { params })
        this.historicoNutricional = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar histórico nutricional'
      }
    },

    // === OPÇÕES PARA SELECTS ===
    async loadProdutoOptions() {
      try {
        await this.fetchProdutos({ limit: 100 })
        return this.produtosAtivos.map((produto) => ({
          value: produto.ID,
          label: `${produto.NOME} (${produto.TIPO_PRODUTO})`,
          tipo: produto.TIPO_PRODUTO,
          unidade: produto.UNIDADE_MEDIDA,
        }))
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao carregar opções de produtos'
      }
    },

    // === UTILITÁRIOS ===
    setFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
    },

    clearFilters() {
      this.filters = {
        terreno_id: null,
        tipo_produto: null,
        tipo_manejo: null,
        data_inicio: '',
        data_fim: '',
        nome: '',
      }
    },

    setPagination(newPagination) {
      this.pagination = { ...this.pagination, ...newPagination }
    },

    // === MÉTODOS AUXILIARES ===
    getTipoLabel(tipo) {
      const tipos = {
        FERTILIZANTE: 'Fertilizante',
        DEFENSIVO: 'Defensivo',
        CORRETIVO: 'Corretivo',
        SEMENTE: 'Semente',
      }
      return tipos[tipo] || tipo
    },

    getManejoLabel(tipo) {
      const tipos = {
        ADUBACAO: 'Adubação',
        CALAGEM: 'Calagem',
        PLANTIO: 'Plantio',
        APLICACAO_DEFENSIVO: 'Aplicação Defensivo',
        ROÇADA: 'Roçada',
        IRRIGACAO: 'Irrigação',
      }
      return tipos[tipo] || tipo
    },

    getStatusSoloColor(status) {
      const colors = {
        BOM: 'positive',
        REGULAR: 'warning',
        RUIM: 'negative',
        SEM_ANALISE: 'grey',
      }
      return colors[status] || 'grey'
    },

    getStatusLotacaoColor(status) {
      const colors = {
        ADEQUADA: 'positive',
        SOBRELOTADO: 'negative',
        SUBLOTADO: 'warning',
        SEM_LIMITE: 'grey',
      }
      return colors[status] || 'grey'
    },

    getCronogramaStatusColor(status) {
      const colors = {
        APLICADO: 'info',
        PENDENTE: 'warning',
        LIBERADO: 'positive',
      }
      return colors[status] || 'grey'
    },

    // === CÁLCULOS AUTOMÁTICOS ===
    calcularDoseTotal(doseHectare, areaAplicada) {
      if (!doseHectare || !areaAplicada) return null
      return (doseHectare * areaAplicada).toFixed(2)
    },

    calcularCustoHectare(custoTotal, areaAplicada) {
      if (!custoTotal || !areaAplicada) return null
      return (custoTotal / areaAplicada).toFixed(2)
    },

    // === RECOMENDAÇÕES AUTOMÁTICAS ===
    gerarRecomendacaoSolo(analise) {
      const recomendacoes = []

      if (analise.PH_AGUA && analise.PH_AGUA < 5.5) {
        recomendacoes.push('pH baixo - Recomenda-se calagem')
      }

      if (analise.SATURACAO_BASES && analise.SATURACAO_BASES < 50) {
        recomendacoes.push('Saturação por bases baixa - Aplicar calcário')
      }

      if (analise.FOSFORO && analise.FOSFORO < 10) {
        recomendacoes.push('Fósforo baixo - Aplicar superfosfato')
      }

      if (analise.POTASSIO && analise.POTASSIO < 0.2) {
        recomendacoes.push('Potássio baixo - Aplicar cloreto de potássio')
      }

      if (analise.MATERIA_ORGANICA && analise.MATERIA_ORGANICA < 2.5) {
        recomendacoes.push('Matéria orgânica baixa - Aplicar esterco ou compost')
      }

      return recomendacoes.length > 0 ? recomendacoes.join('; ') : 'Solo em boas condições'
    },

    // === BUSCA E FILTROS AVANÇADOS ===
    searchProdutos(termo) {
      if (!termo) return this.produtosAtivos

      const termoLower = termo.toLowerCase()
      return this.produtosAtivos.filter(
        (produto) =>
          produto.NOME.toLowerCase().includes(termoLower) ||
          produto.TIPO_PRODUTO.toLowerCase().includes(termoLower) ||
          (produto.PRINCIPIO_ATIVO && produto.PRINCIPIO_ATIVO.toLowerCase().includes(termoLower)),
      )
    },

    getAplicacoesByTerreno(terrenoId) {
      return this.aplicacoes.filter((aplicacao) => aplicacao.ID_TERRENO === terrenoId)
    },

    getUltimaAnaliseByTerreno(terrenoId) {
      const analises = this.analisesSolo.filter((analise) => analise.ID_TERRENO === terrenoId)
      return analises.length > 0 ? analises[0] : null // Já vem ordenado por data desc
    },
  },
})
