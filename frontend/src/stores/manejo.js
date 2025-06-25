// frontend/src/stores/manejo.js
import { defineStore } from 'pinia'
import api from '../boot/api'

export const useManejoStore = defineStore('manejo', {
  state: () => ({
    // === PRODUTOS MANEJO ===
    produtos: [],
    alertasEstoque: [],
    movimentacaoResumo: [],

    // === MOVIMENTAÇÃO ESTOQUE ===
    movimentacoes: [],

    // === APLICAÇÕES ===
    aplicacoes: [],

    // === ANÁLISES SOLO ===
    analisesSolo: [],

    // === RELATÓRIOS ===
    terrenosBloqueados: [],
    cronograma: [],
    capacidadeOcupacao: [],
    historicoNutricional: [],
    consumoTerreno: [],
    previsaoConsumo: [],
    terrenosLiberacao: [],

    // === CONTROLE ===
    loading: false,

    // === FILTROS ===
    filters: {
      terreno_id: null,
      tipo_produto: null,
      tipo_manejo: null,
      data_inicio: '',
      data_fim: '',
      nome: '',
      estoque_baixo: false,
      ativo: 'S',
    },

    // === PAGINAÇÃO ===
    pagination: {
      page: 1,
      rowsPerPage: 10,
      rowsNumber: 0,
      sortBy: 'NOME',
      descending: false,
    },
  }),

  getters: {
    // === OPÇÕES PARA SELECTS ===
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
      { value: 'GESSAGEM', label: 'Gessagem' },
      { value: 'SULCAGEM', label: 'Sulcagem' },
    ],

    tiposMovimentacao: () => [
      { value: 'ENTRADA', label: 'Entrada' },
      { value: 'SAIDA', label: 'Saída' },
      { value: 'AJUSTE', label: 'Ajuste' },
    ],

    statusEstoque: () => [
      { value: 'SEM_ESTOQUE', label: 'Sem Estoque', color: 'red' },
      { value: 'ESTOQUE_BAIXO', label: 'Estoque Baixo', color: 'orange' },
      { value: 'VENCIMENTO_PROXIMO', label: 'Vencimento Próximo', color: 'purple' },
      { value: 'OK', label: 'OK', color: 'green' },
    ],

    // === PRODUTOS FILTRADOS ===
    produtosAtivos: (state) => state.produtos.filter((p) => p.ATIVO === 'S'),

    produtosByTipo: (state) => (tipo) => {
      return state.produtos.filter((p) => p.TIPO_PRODUTO === tipo && p.ATIVO === 'S')
    },

    produtosComEstoqueBaixo: (state) => {
      return state.produtos.filter(
        (p) =>
          p.ATIVO === 'S' &&
          (p.status_estoque === 'ESTOQUE_BAIXO' || p.status_estoque === 'SEM_ESTOQUE'),
      )
    },

    produtosVencendoProximo: (state) => {
      return state.produtos.filter(
        (p) => p.ATIVO === 'S' && p.status_estoque === 'VENCIMENTO_PROXIMO',
      )
    },

    // === ESTATÍSTICAS PRODUTOS ===
    estatisticasProdutos: (state) => {
      const ativos = state.produtos.filter((p) => p.ATIVO === 'S')
      const comEstoque = ativos.filter((p) => (p.ESTOQUE_ATUAL || 0) > 0)
      const estoqueBaixo = ativos.filter(
        (p) => (p.ESTOQUE_ATUAL || 0) <= (p.ESTOQUE_MINIMO || 0) && (p.ESTOQUE_ATUAL || 0) > 0,
      )
      const semEstoque = ativos.filter((p) => (p.ESTOQUE_ATUAL || 0) === 0)
      const valorTotal = ativos.reduce(
        (sum, p) => sum + (p.ESTOQUE_ATUAL || 0) * (p.PRECO_UNITARIO || 0),
        0,
      )

      return {
        totalProdutos: ativos.length,
        comEstoque: comEstoque.length,
        estoqueBaixo: estoqueBaixo.length,
        semEstoque: semEstoque.length,
        valorTotalEstoque: valorTotal,
        percentualComEstoque:
          ativos.length > 0 ? ((comEstoque.length / ativos.length) * 100).toFixed(1) : 0,
      }
    },

    // === ESTATÍSTICAS GERAIS ===
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
    // ========================================
    // PRODUTOS MANEJO
    // ========================================

    async fetchProdutos(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          sort_by: params.sortBy || this.pagination.sortBy,
          order: params.descending ? 'desc' : 'asc',
          ...this.filters,
          ...params.filtros,
        }

        // Converter objetos select para valores
        if (queryParams.tipo_produto?.value) {
          queryParams.tipo_produto = queryParams.tipo_produto.value
        }

        const response = await api.get('/api/manejo/produtos', { params: queryParams })

        this.produtos = response.data.produtos || []
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
      this.loading = true
      try {
        // Converter valores dos selects
        const data = { ...produtoData }
        if (data.TIPO_PRODUTO?.value) {
          data.TIPO_PRODUTO = data.TIPO_PRODUTO.value
        }

        const response = await api.post('/api/manejo/produtos', data)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao criar produto'
      } finally {
        this.loading = false
      }
    },

    async updateProduto(id, produtoData) {
      this.loading = true
      try {
        // Converter valores dos selects
        const data = { ...produtoData }
        if (data.TIPO_PRODUTO?.value) {
          data.TIPO_PRODUTO = data.TIPO_PRODUTO.value
        }

        const response = await api.put(`/api/manejo/produtos/${id}`, data)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar produto'
      } finally {
        this.loading = false
      }
    },

    async deleteProduto(id) {
      this.loading = true
      try {
        await api.delete(`/api/manejo/produtos/${id}`)
        return true
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir produto'
      } finally {
        this.loading = false
      }
    },

    async getProdutoById(id) {
      try {
        const response = await api.get(`/api/manejo/produtos/${id}`)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar produto'
      }
    },

    async getAutocompleProdutos(params = {}) {
      try {
        const response = await api.get('/api/manejo/produtos/autocomplete', { params })
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar autocomplete de produtos'
      }
    },

    // === ALERTAS E RELATÓRIOS DE ESTOQUE ===
    async getAlertasEstoque() {
      try {
        const response = await api.get('/api/manejo/estoque/alertas')
        this.alertasEstoque = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar alertas de estoque'
      }
    },

    async getResumoEstoque(tipoProducto = null) {
      try {
        const params = tipoProducto ? { tipo_produto: tipoProducto } : {}
        const response = await api.get('/api/manejo/estoque/resumo', { params })
        this.movimentacaoResumo = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar resumo de estoque'
      }
    },

    // ========================================
    // MOVIMENTAÇÃO DE ESTOQUE
    // ========================================

    async fetchMovimentacoes(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          ...params.filtros,
        }

        // Converter objetos select para valores
        if (queryParams.produto_id?.value) {
          queryParams.produto_id = queryParams.produto_id.value
        }

        if (queryParams.tipo_movimentacao?.value) {
          queryParams.tipo_movimentacao = queryParams.tipo_movimentacao.value
        }

        const response = await api.get('/api/manejo/estoque/movimentacoes', { params: queryParams })
        this.movimentacoes = response.data.movimentacoes || []

        // Atualizar paginação
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

    async entradaEstoque(entradaData) {
      this.loading = true
      try {
        const response = await api.post('/api/manejo/estoque/entrada', entradaData)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao registrar entrada'
      } finally {
        this.loading = false
      }
    },

    async saidaEstoque(saidaData) {
      this.loading = true
      try {
        const response = await api.post('/api/manejo/estoque/saida', saidaData)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao registrar saída'
      } finally {
        this.loading = false
      }
    },

    async ajusteEstoque(ajusteData) {
      this.loading = true
      try {
        const response = await api.post('/api/manejo/estoque/ajuste', ajusteData)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao registrar ajuste'
      } finally {
        this.loading = false
      }
    },

    // ========================================
    // APLICAÇÕES EM TERRENOS
    // ========================================

    async fetchAplicacoes(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          ...this.filters,
          ...params.filtros,
        }

        // Converter objetos select para valores
        if (queryParams.produto_id?.value) {
          queryParams.produto_id = queryParams.produto_id.value
        }

        if (queryParams.terreno_id?.value) {
          queryParams.terreno_id = queryParams.terreno_id.value
        }

        if (queryParams.tipo_manejo?.value) {
          queryParams.tipo_manejo = queryParams.tipo_manejo.value
        }

        if (queryParams.tipo_produto?.value) {
          queryParams.tipo_produto = queryParams.tipo_produto.value
        }

        const response = await api.get('/api/manejo/aplicacoes', { params: queryParams })
        this.aplicacoes = response.data.aplicacoes || []

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
      this.loading = true
      try {
        const response = await api.post('/api/manejo/aplicacoes', aplicacaoData)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao criar aplicação'
      } finally {
        this.loading = false
      }
    },

    async updateAplicacao(id, aplicacaoData) {
      this.loading = true
      try {
        const response = await api.put(`/api/manejo/aplicacoes/${id}`, aplicacaoData)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar aplicação'
      } finally {
        this.loading = false
      }
    },

    async deleteAplicacao(id) {
      this.loading = true
      try {
        await api.delete(`/api/manejo/aplicacoes/${id}`)
        return true
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir aplicação'
      } finally {
        this.loading = false
      }
    },

    // ========================================
    // ANÁLISES DE SOLO
    // ========================================

    async fetchAnalisesSolo(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          ...params.filtros,
        }

        // Converter objetos select para valores
        if (queryParams.terreno_id?.value) {
          queryParams.terreno_id = queryParams.terreno_id.value
        }

        const response = await api.get('/api/manejo/analises-solo', { params: queryParams })
        this.analisesSolo = response.data.analises || []

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
      this.loading = true
      try {
        const response = await api.post('/api/manejo/analises-solo', analiseData)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao criar análise'
      } finally {
        this.loading = false
      }
    },

    async updateAnaliseSolo(id, analiseData) {
      this.loading = true
      try {
        const response = await api.put(`/api/manejo/analises-solo/${id}`, analiseData)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar análise'
      } finally {
        this.loading = false
      }
    },

    async deleteAnaliseSolo(id) {
      this.loading = true
      try {
        await api.delete(`/api/manejo/analises-solo/${id}`)
        return true
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir análise'
      } finally {
        this.loading = false
      }
    },

    async uploadLaudoAnalise(analiseId, file) {
      this.loading = true
      try {
        const formData = new FormData()
        formData.append('file', file)

        const response = await api.post(
          `/api/manejo/analises-solo/${analiseId}/upload-laudo`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          },
        )
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao fazer upload do laudo'
      } finally {
        this.loading = false
      }
    },

    async downloadLaudoAnalise(analiseId) {
      this.loading = true
      try {
        // Fazer requisição para download
        const response = await api.get(`/api/manejo/analises-solo/${analiseId}/download-laudo`, {
          responseType: 'blob', // Importante para arquivos binários
        })

        // Obter nome do arquivo do header Content-Disposition ou usar padrão
        let nomeArquivo = `laudo_analise_${analiseId}.pdf`

        const contentDisposition = response.headers['content-disposition']
        if (contentDisposition) {
          const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
          if (match && match[1]) {
            nomeArquivo = match[1].replace(/['"]/g, '')
          }
        }

        // Criar blob e URL para download
        const blob = new Blob([response.data], {
          type: response.headers['content-type'] || 'application/octet-stream',
        })

        const url = window.URL.createObjectURL(blob)

        // Criar elemento <a> temporário para download
        const link = document.createElement('a')
        link.href = url
        link.download = nomeArquivo

        // Adicionar ao DOM, clicar e remover
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)

        // Limpar URL do blob
        window.URL.revokeObjectURL(url)

        return { success: true, nomeArquivo }
      } catch (error) {
        if (error.response?.status === 404) {
          throw new Error('Laudo não encontrado')
        }
        throw error.response?.data?.detail || 'Erro ao fazer download do laudo'
      } finally {
        this.loading = false
      }
    },

    async getLaudoInfo(analiseId) {
      try {
        const response = await api.get(`/api/manejo/analises-solo/${analiseId}/laudo-info`)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao obter informações do laudo'
      }
    },

    // ========================================
    // RELATÓRIOS AVANÇADOS
    // ========================================

    async getConsumoTerreno(params = {}) {
      try {
        const response = await api.get('/api/manejo/relatorios/consumo-terreno', { params })
        this.consumoTerreno = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar consumo por terreno'
      }
    },

    async getPrevisaoConsumo(tipoProducto = null) {
      try {
        const params = tipoProducto ? { tipo_produto: tipoProducto } : {}
        const response = await api.get('/api/manejo/relatorios/previsao-consumo', { params })
        this.previsaoConsumo = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar previsão de consumo'
      }
    },

    async getTerrenosLiberacao(diasFuturo = 30) {
      try {
        const response = await api.get('/api/manejo/relatorios/terrenos-liberacao', {
          params: { dias_futuro: diasFuturo },
        })
        this.terrenosLiberacao = response.data.liberacoes || []
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar terrenos para liberação'
      }
    },

    // ========================================
    // OPÇÕES PARA SELECTS
    // ========================================

    async loadProdutoOptions(apenasComEstoque = false) {
      try {
        const params = { apenas_com_estoque: apenasComEstoque }
        const response = await api.get('/api/manejo/produtos/autocomplete', { params })
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao carregar opções de produtos'
      }
    },

    // ========================================
    // UTILITÁRIOS
    // ========================================

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
        estoque_baixo: false,
        ativo: 'S',
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
        GESSAGEM: 'Gessagem',
        SULCAGEM: 'Sulcagem',
      }
      return tipos[tipo] || tipo
    },

    getStatusEstoqueColor(status) {
      const cores = {
        SEM_ESTOQUE: 'red',
        ESTOQUE_BAIXO: 'orange',
        VENCIMENTO_PROXIMO: 'purple',
        OK: 'green',
      }
      return cores[status] || 'grey'
    },

    getMovimentacaoColor(tipo) {
      const cores = {
        ENTRADA: 'positive',
        SAIDA: 'negative',
        AJUSTE: 'warning',
      }
      return cores[tipo] || 'grey'
    },

    formatarMoeda(valor) {
      if (!valor) return 'R$ 0,00'
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
      }).format(valor)
    },

    formatarQuantidade(quantidade, unidade) {
      if (!quantidade) return `0 ${unidade || ''}`
      return `${quantidade.toLocaleString('pt-BR')} ${unidade || ''}`
    },
  },
})
