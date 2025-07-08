// frontend/src/stores/racao.js
import { defineStore } from 'pinia'
import api from '../boot/api'
import { prepareFormData } from 'src/utils/dateUtils'

export const useRacaoStore = defineStore('racao', {
  state: () => ({
    // === PRODUTOS RAÇÃO ===
    produtos: [],
    alertasEstoque: [],

    // === MOVIMENTAÇÃO ESTOQUE ===
    movimentacoes: [],

    // === PLANOS ALIMENTARES ===
    planosAlimentares: [],
    itensPlano: [],

    // === FORNECIMENTO ===
    fornecimentos: [],

    // === RELATÓRIOS ===
    consumoAnimal: [],
    previsaoConsumo: [],
    estoqueBaixo: [],

    // === CONTROLE ===
    loading: false,

    // === FILTROS ===
    filters: {
      animal_id: null,
      produto_id: null,
      tipo_alimento: null,
      categoria_nutricional: null,
      data_inicio: '',
      data_fim: '',
      nome: '',
      estoque_baixo: false,
      ativo: '',
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
    tiposAlimento: () => [
      { value: 'CONCENTRADO', label: 'Concentrado' },
      { value: 'VOLUMOSO', label: 'Volumoso' },
      { value: 'SUPLEMENTO', label: 'Suplemento' },
      { value: 'PREMIX', label: 'Premix' },
      { value: 'SAL_MINERAL', label: 'Sal Mineral' },
    ],

    categoriasNutricionais: () => [
      { value: 'POTRO', label: 'Potro' },
      { value: 'JOVEM', label: 'Jovem' },
      { value: 'ADULTO_MANUTENCAO', label: 'Adulto - Manutenção' },
      { value: 'ADULTO_TRABALHO_LEVE', label: 'Adulto - Trabalho Leve' },
      {
        value: 'ADULTO_TRABALHO_MODERADO',
        label: 'Adulto - Trabalho Moderado',
      },
      { value: 'ADULTO_TRABALHO_INTENSO', label: 'Adulto - Trabalho Intenso' },
      { value: 'EGUA_GESTANTE', label: 'Égua Gestante' },
      { value: 'EGUA_LACTANTE', label: 'Égua Lactante' },
      { value: 'REPRODUTOR', label: 'Reprodutor' },
      { value: 'IDOSO', label: 'Idoso' },
    ],

    intensidadeTrabalho: () => [
      { value: 'REPOUSO', label: 'Repouso' },
      { value: 'LEVE', label: 'Leve' },
      { value: 'MODERADO', label: 'Moderado' },
      { value: 'INTENSO', label: 'Intenso' },
    ],

    statusPlano: () => [
      { value: 'ATIVO', label: 'Ativo', color: 'green' },
      { value: 'INATIVO', label: 'Inativo', color: 'grey' },
      { value: 'SUSPENSO', label: 'Suspenso', color: 'orange' },
    ],

    tiposMovimentacao: () => [
      { value: 'ENTRADA', label: 'Entrada' },
      { value: 'SAIDA', label: 'Saída' },
      { value: 'AJUSTE', label: 'Ajuste' },
    ],

    statusEstoque: () => [
      { value: 'SEM_ESTOQUE', label: 'Sem Estoque', color: 'red' },
      { value: 'ESTOQUE_BAIXO', label: 'Estoque Baixo', color: 'orange' },
      {
        value: 'VENCIMENTO_PROXIMO',
        label: 'Vencimento Próximo',
        color: 'purple',
      },
      { value: 'VENCIDO', label: 'Vencido', color: 'red-10' },
      { value: 'OK', label: 'OK', color: 'green' },
    ],

    // === PRODUTOS FILTRADOS ===
    produtosAtivos: state => state.produtos.filter(p => p.ATIVO === 'S'),

    produtosByTipo: state => tipo => {
      return state.produtos.filter(
        p => p.TIPO_ALIMENTO === tipo && p.ATIVO === 'S'
      )
    },

    produtosComEstoqueBaixo: state => {
      return state.produtos.filter(
        p =>
          p.ATIVO === 'S' &&
          (p.status_estoque === 'ESTOQUE_BAIXO' ||
            p.status_estoque === 'SEM_ESTOQUE')
      )
    },

    produtosVencendoProximo: state => {
      return state.produtos.filter(
        p => p.ATIVO === 'S' && p.status_estoque === 'VENCIMENTO_PROXIMO'
      )
    },

    // === PLANOS FILTRADOS ===
    planosAtivos: state =>
      state.planosAlimentares.filter(p => p.STATUS_PLANO === 'ATIVO'),

    planosPorAnimal: state => animalId => {
      return state.planosAlimentares.filter(p => p.ID_ANIMAL === animalId)
    },

    // === ESTATÍSTICAS ===
    estatisticasProdutos: state => {
      const ativos = state.produtos.filter(p => p.ATIVO === 'S')
      const comEstoque = ativos.filter(p => (p.ESTOQUE_ATUAL || 0) > 0)
      const estoqueBaixo = ativos.filter(
        p =>
          (p.ESTOQUE_ATUAL || 0) <= (p.ESTOQUE_MINIMO || 0) &&
          (p.ESTOQUE_ATUAL || 0) > 0
      )
      const semEstoque = ativos.filter(p => (p.ESTOQUE_ATUAL || 0) === 0)
      const valorTotal = ativos.reduce(
        (sum, p) => sum + (p.ESTOQUE_ATUAL || 0) * (p.PRECO_UNITARIO || 0),
        0
      )

      return {
        totalProdutos: ativos.length,
        comEstoque: comEstoque.length,
        estoqueBaixo: estoqueBaixo.length,
        semEstoque: semEstoque.length,
        valorTotalEstoque: valorTotal,
        percentualComEstoque:
          ativos.length > 0
            ? ((comEstoque.length / ativos.length) * 100).toFixed(1)
            : 0,
      }
    },

    estatisticasPlanos: state => {
      const ativos = state.planosAlimentares.filter(
        p => p.STATUS_PLANO === 'ATIVO'
      )
      const suspensos = state.planosAlimentares.filter(
        p => p.STATUS_PLANO === 'SUSPENSO'
      )
      const custoTotal = ativos.reduce(
        (sum, p) => sum + (p.custo_diario_estimado || 0),
        0
      )

      return {
        totalPlanos: state.planosAlimentares.length,
        planosAtivos: ativos.length,
        planosSuspensos: suspensos.length,
        custoMensalEstimado: custoTotal * 30,
      }
    },
  },

  actions: {
    // ========================================
    // PRODUTOS RAÇÃO
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
        if (queryParams.tipo_alimento?.value) {
          queryParams.tipo_alimento = queryParams.tipo_alimento.value
        }

        if (queryParams.ativo?.value) {
          queryParams.ativo = queryParams.ativo.value
        }

        const response = await api.get('/api/racao/produtos', {
          params: queryParams,
        })
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
      // Converter objetos select para valores
      if (produtoData.TIPO_ALIMENTO?.value) {
        produtoData.TIPO_ALIMENTO = produtoData.TIPO_ALIMENTO.value
      }
      const dados = prepareFormData(produtoData, [
        'DATA_FABRICACAO',
        'DATA_VALIDADE',
      ])

      const response = await api.post('/api/racao/produtos', dados)
      return response.data
    },

    async updateProduto(id, produtoData) {
      // Converter objetos select para valores
      if (produtoData.TIPO_ALIMENTO?.value) {
        produtoData.TIPO_ALIMENTO = produtoData.TIPO_ALIMENTO.value
      }
      const dados = prepareFormData(produtoData, [
        'DATA_FABRICACAO',
        'DATA_VALIDADE',
      ])

      const response = await api.put(`/api/racao/produtos/${id}`, dados)
      return response.data
    },

    async deleteProduto(id) {
      await api.delete(`/api/racao/produtos/${id}`)
      return true
    },

    async autocompleProdutos(query = '') {
      try {
        const response = await api.get(
          '/api/racao/produtos/search/autocomplete',
          {
            params: { q: query },
          }
        )
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro na busca'
      }
    },

    // ========================================
    // MOVIMENTAÇÃO ESTOQUE
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

        const response = await api.get('/api/racao/estoque/movimentacoes', {
          params: queryParams,
        })
        this.movimentacoes = response.data.movimentacoes || []

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
        const response = await api.post(
          '/api/racao/estoque/entrada',
          entradaData
        )
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
        const response = await api.post('/api/racao/estoque/saida', saidaData)
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
        const response = await api.post('/api/racao/estoque/ajuste', ajusteData)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao registrar ajuste'
      } finally {
        this.loading = false
      }
    },

    // ========================================
    // PLANOS ALIMENTARES
    // ========================================

    async fetchPlanosAlimentares(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          ...params.filtros,
        }

        // Converter objetos select para valores
        if (queryParams.animal_id?.value) {
          queryParams.animal_id = queryParams.animal_id.value
        }

        if (queryParams.categoria?.value) {
          queryParams.categoria = queryParams.categoria.value
        }

        if (queryParams.status_plano?.value) {
          queryParams.status_plano = queryParams.status_plano.value
        }

        const response = await api.get('/api/racao/planos', {
          params: queryParams,
        })
        this.planosAlimentares = response.data.planos || []

        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit,
        }

        return response.data
      } catch (error) {
        throw (
          error.response?.data?.detail || 'Erro ao buscar planos alimentares'
        )
      } finally {
        this.loading = false
      }
    },

    async createPlanoAlimentar(planoData) {
      this.loading = true
      // Converter objetos select para valores
      if (planoData.ID_ANIMAL?.value) {
        planoData.ID_ANIMAL = planoData.ID_ANIMAL.value
      }
      if (planoData.CATEGORIA_NUTRICIONAL?.value) {
        planoData.CATEGORIA_NUTRICIONAL = planoData.CATEGORIA_NUTRICIONAL.value
      }
      if (planoData.INTENSIDADE_TRABALHO?.value) {
        planoData.INTENSIDADE_TRABALHO = planoData.INTENSIDADE_TRABALHO.value
      }
      const dados = prepareFormData(planoData, ['DATA_INICIO', 'DATA_FIM'])

      try {
        const response = await api.post('/api/racao/planos', dados)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao criar plano alimentar'
      } finally {
        this.loading = false
      }
    },

    async updatePlanoAlimentar(id, planoData) {
      this.loading = true
      // Converter objetos select para valores
      if (planoData.ID_ANIMAL?.value) {
        planoData.ID_ANIMAL = planoData.ID_ANIMAL.value
      }
      if (planoData.CATEGORIA_NUTRICIONAL?.value) {
        planoData.CATEGORIA_NUTRICIONAL = planoData.CATEGORIA_NUTRICIONAL.value
      }
      if (planoData.INTENSIDADE_TRABALHO?.value) {
        planoData.INTENSIDADE_TRABALHO = planoData.INTENSIDADE_TRABALHO.value
      }
      const dados = prepareFormData(planoData, ['DATA_INICIO', 'DATA_FIM'])

      try {
        const response = await api.put(`/api/racao/planos/${id}`, dados)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar plano'
      } finally {
        this.loading = false
      }
    },

    async fetchItensPlano(planoId) {
      this.loading = true
      try {
        const response = await api.get(`/api/racao/planos/${planoId}/itens`)
        this.itensPlano = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar itens do plano'
      } finally {
        this.loading = false
      }
    },

    async createItemPlano(planoId, itemData) {
      this.loading = true
      console.log(JSON.stringify(itemData))
      try {
        const response = await api.post(
          `/api/racao/planos/${planoId}/itens`,
          itemData
        )
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao adicionar item ao plano'
      } finally {
        this.loading = false
      }
    },

    async updateItemPlano(itemId, itemData) {
      this.loading = true
      try {
        const response = await api.put(
          `/api/racao/planos/itens/${itemId}`,
          itemData
        )
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar item'
      } finally {
        this.loading = false
      }
    },

    async deleteItemPlano(itemId) {
      this.loading = true
      try {
        await api.delete(`/api/racao/planos/itens/${itemId}`)
        return true
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir item'
      } finally {
        this.loading = false
      }
    },

    // ========================================
    // FORNECIMENTO
    // ========================================

    async fetchFornecimentos(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          ...params.filtros,
        }

        // Converter objetos select para valores
        if (queryParams.animal_id?.value) {
          queryParams.animal_id = queryParams.animal_id.value
        }

        if (queryParams.produto_id?.value) {
          queryParams.produto_id = queryParams.produto_id.value
        }

        const response = await api.get('/api/racao/fornecimento', {
          params: queryParams,
        })
        this.fornecimentos = response.data.fornecimentos || []

        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit,
        }

        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar fornecimentos'
      } finally {
        this.loading = false
      }
    },

    async registrarFornecimento(fornecimentoData) {
      this.loading = true

      const dados = prepareFormData(fornecimentoData, ['DATA_FORNECIMENTO'])

      console.log(JSON.stringify(dados))

      try {
        const response = await api.post(
          '/api/racao/fornecimento',
          fornecimentoData
        )
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao registrar fornecimento'
      } finally {
        this.loading = false
      }
    },

    async updateFornecimento(id, fornecimentoData) {
      this.loading = true
      const dados = prepareFormData(fornecimentoData, ['DATA_FORNECIMENTO'])

      try {
        const response = await api.put(`/api/racao/fornecimento/${id}`, dados)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar fornecimento'
      } finally {
        this.loading = false
      }
    },

    async deleteFornecimento(id) {
      this.loading = true
      try {
        await api.delete(`/api/racao/fornecimento/${id}`)
        return true
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir fornecimento'
      } finally {
        this.loading = false
      }
    },

    // ========================================
    // CÁLCULOS NUTRICIONAIS
    // ========================================

    async calcularNecessidadesNutricionais(animalId, categoria) {
      this.loading = true
      try {
        const response = await api.get(
          `/api/racao/calculo-nutricional/${animalId}`,
          {
            params: { categoria },
          }
        )
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao calcular necessidades'
      } finally {
        this.loading = false
      }
    },

    // ========================================
    // RELATÓRIOS
    // ========================================

    async getEstoqueBaixo() {
      try {
        const response = await api.get('/api/racao/relatorios/estoque-baixo')
        this.estoqueBaixo = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar estoque baixo'
      }
    },

    async getConsumoAnimal(params = {}) {
      try {
        const response = await api.get('/api/racao/relatorios/consumo-animal', {
          params,
        })
        this.consumoAnimal = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar consumo animal'
      }
    },

    async getPrevisaoConsumo() {
      try {
        const response = await api.get('/api/racao/relatorios/previsao-consumo')
        this.previsaoConsumo = response.data
        return response.data
      } catch (error) {
        throw (
          error.response?.data?.detail || 'Erro ao buscar previsão de consumo'
        )
      }
    },

    async getAlertasEstoque() {
      try {
        const response = await api.get('/api/racao/relatorios/estoque-baixo')
        this.alertasEstoque = response.data.filter(item =>
          [
            'SEM_ESTOQUE',
            'ESTOQUE_BAIXO',
            'VENCIDO',
            'VENCIMENTO_PROXIMO',
          ].includes(item.status_alerta)
        )

        return this.alertasEstoque
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar alertas'
      }
    },

    // ========================================
    // UTILITÁRIOS
    // ========================================

    formatarMoeda(valor) {
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
      }).format(valor || 0)
    },

    formatarPeso(peso) {
      return `${(peso || 0).toFixed(1)} kg`
    },

    formatarPercentual(percentual) {
      return `${(percentual || 0).toFixed(1)}%`
    },

    getStatusColor(status) {
      const statusObj = this.statusEstoque.find(s => s.value === status)
      return statusObj?.color || 'grey'
    },

    getCategoriaLabel(categoria) {
      const categoriaObj = this.categoriasNutricionais.find(
        c => c.value === categoria
      )
      return categoriaObj?.label || categoria
    },

    getTipoAlimentoLabel(tipo) {
      const tipoObj = this.tiposAlimento.find(t => t.value === tipo)
      return tipoObj?.label || tipo
    },

    // === LIMPEZA DE DADOS ===
    clearFilters() {
      this.filters = {
        animal_id: null,
        produto_id: null,
        tipo_alimento: null,
        categoria_nutricional: null,
        data_inicio: '',
        data_fim: '',
        nome: '',
        estoque_baixo: false,
        ativo: 'S',
      }
    },

    resetPagination() {
      this.pagination = {
        page: 1,
        rowsPerPage: 10,
        rowsNumber: 0,
        sortBy: 'NOME',
        descending: false,
      }
    },
  },
})
