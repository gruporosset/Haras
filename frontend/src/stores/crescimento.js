import { defineStore } from 'pinia'
import api from '../boot/api'

export const useCrescimentoStore = defineStore('crescimento', {
  state: () => ({
    crescimentos: [],
    historicoAnimal: [],
    estatisticasGerais: [],
    comparacaoMedidas: [],
    loading: false,
    filters: {
      animal_id: null,
      data_inicio: '',
      data_fim: '',
    },
    pagination: {
      page: 1,
      rowsPerPage: 10,
      rowsNumber: 0,
      sortBy: 'DATA_MEDICAO',
      descending: true,
    },
  }),

  getters: {
    // Estatísticas rápidas
    totalMedicoes: state => state.crescimentos.length,

    animaisComMedicoes: state => {
      const animais = new Set(state.crescimentos.map(c => c.animal_nome))
      return animais.size
    },

    mediaGanhoPeso: state => {
      const ganhosPositivos = state.crescimentos
        .filter(c => c.ganho_peso && c.ganho_peso > 0)
        .map(c => c.ganho_peso)

      if (ganhosPositivos.length === 0) return 0

      const soma = ganhosPositivos.reduce((acc, ganho) => acc + ganho, 0)
      return (soma / ganhosPositivos.length).toFixed(2)
    },

    ultimasMedicoes: state => {
      return state.crescimentos.slice(0, 5) // 5 mais recentes
    },

    // Dados para gráficos
    dadosGraficoPeso: state => animalId => {
      return state.historicoAnimal
        .filter(h => h.medicao.ID_ANIMAL === animalId && h.medicao.PESO)
        .map(h => ({
          data: h.medicao.DATA_MEDICAO,
          peso: h.medicao.PESO,
          ganho: h.variacao_peso || 0,
        }))
        .sort((a, b) => new Date(a.data) - new Date(b.data))
    },

    dadosGraficoAltura: state => animalId => {
      return state.historicoAnimal
        .filter(h => h.medicao.ID_ANIMAL === animalId && h.medicao.ALTURA)
        .map(h => ({
          data: h.medicao.DATA_MEDICAO,
          altura: h.medicao.ALTURA,
          variacao: h.variacao_altura || 0,
        }))
        .sort((a, b) => new Date(a.data) - new Date(b.data))
    },
  },

  actions: {
    // === CRUD BÁSICO ===
    async fetchCrescimentos(params = {}) {
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

        const response = await api.get('/api/crescimento', {
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
        throw (
          error.response?.data?.detail ||
          'Erro ao buscar registros de crescimento'
        )
      } finally {
        this.loading = false
      }
    },

    async getCrescimento(id) {
      try {
        const response = await api.get(`/api/crescimento/${id}`)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar registro'
      }
    },

    async createCrescimento(crescimentoData) {
      const response = await api.post('/api/crescimento', crescimentoData)
      await this.fetchCrescimentos()
      return response.data
    },

    async updateCrescimento(id, crescimentoData) {
      const response = await api.put(`/api/crescimento/${id}`, crescimentoData)
      await this.fetchCrescimentos()
      return response.data
    },

    async deleteCrescimento(id) {
      await api.delete(`/api/crescimento/${id}`)
      await this.fetchCrescimentos()
    },

    // === HISTÓRICO E RELATÓRIOS ===
    async fetchHistoricoAnimal(animalId) {
      this.loading = true
      try {
        const response = await api.get(
          `/api/crescimento/animal/${animalId}/historico`
        )
        this.historicoAnimal = response.data
        return response.data
      } catch (error) {
        throw (
          error.response?.data?.detail || 'Erro ao buscar histórico do animal'
        )
      } finally {
        this.loading = false
      }
    },

    async fetchEstatisticasGerais(mesesPeriodo = 12) {
      this.loading = true
      try {
        const response = await api.get('/api/crescimento/estatisticas/geral', {
          params: { meses_periodo: mesesPeriodo },
        })
        this.estatisticasGerais = response.data
        return response.data
      } catch (error) {
        throw (
          error.response?.data?.detail || 'Erro ao buscar estatísticas gerais'
        )
      } finally {
        this.loading = false
      }
    },

    async fetchComparacaoMedidas() {
      this.loading = true
      try {
        const response = await api.get('/api/crescimento/comparacao/medidas')
        this.comparacaoMedidas = response.data
        return response.data
      } catch (error) {
        throw (
          error.response?.data?.detail || 'Erro ao buscar comparação de medidas'
        )
      } finally {
        this.loading = false
      }
    },

    // === UTILITÁRIOS ===
    setFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
    },

    clearFilters() {
      this.filters = {
        animal_id: null,
        data_inicio: '',
        data_fim: '',
      }
    },

    setPagination(newPagination) {
      this.pagination = { ...this.pagination, ...newPagination }
    },

    // === VALIDAÇÕES ===
    validarFormulario(form) {
      const erros = []

      if (!form.ID_ANIMAL) {
        erros.push('Animal é obrigatório')
      }

      if (!form.DATA_MEDICAO) {
        erros.push('Data de medição é obrigatória')
      }

      // Pelo menos uma medida deve ser informada
      const medidas = [
        form.PESO,
        form.ALTURA,
        form.CIRCUNFERENCIA_CANELA,
        form.CIRCUNFERENCIA_TORACICA,
        form.COMPRIMENTO_CORPO,
      ]
      if (!medidas.some(medida => medida && medida > 0)) {
        erros.push('Pelo menos uma medida deve ser informada')
      }

      // Validar faixas de valores
      if (form.PESO && (form.PESO <= 0 || form.PESO > 2000)) {
        erros.push('Peso deve estar entre 0 e 2000 kg')
      }

      if (form.ALTURA && (form.ALTURA <= 0 || form.ALTURA > 300)) {
        erros.push('Altura deve estar entre 0 e 300 cm')
      }

      return {
        valido: erros.length === 0,
        erros,
      }
    },

    // === CÁLCULOS ===
    calcularIMC(peso, altura) {
      // IMC adaptado para cavalos (peso em kg, altura em cm)
      if (!peso || !altura || altura === 0) return null
      const alturaMetros = altura / 100
      return (peso / (alturaMetros * alturaMetros)).toFixed(2)
    },

    calcularTaxaCrescimento(pesoAtual, pesoAnterior, dias) {
      if (!pesoAtual || !pesoAnterior || !dias || dias <= 0) return null
      return ((pesoAtual - pesoAnterior) / dias).toFixed(3)
    },

    // === COMPARAÇÕES ===
    compararComMedia(valor, tipo) {
      // Valores médios de referência (podem ser configuráveis)
      const referencias = {
        peso: { min: 300, max: 600, ideal: 450 },
        altura: { min: 140, max: 180, ideal: 160 },
        canela: { min: 18, max: 24, ideal: 21 },
        toracica: { min: 160, max: 200, ideal: 180 },
        corpo: { min: 140, max: 180, ideal: 160 },
      }

      const ref = referencias[tipo]
      if (!ref || !valor) return 'INDEFINIDO'

      if (valor < ref.min) return 'ABAIXO'
      if (valor > ref.max) return 'ACIMA'
      return 'NORMAL'
    },

    getClassificacaoColor(classificacao) {
      const colors = {
        ABAIXO: 'negative',
        NORMAL: 'positive',
        ACIMA: 'warning',
        IDEAL: 'positive',
        INDEFINIDO: 'grey',
      }
      return colors[classificacao] || 'grey'
    },

    // === BUSCA E FILTROS ===
    getCrescimentosByAnimal(animalId) {
      return this.crescimentos.filter(c => c.ID_ANIMAL === animalId)
    },

    getUltimaMedicaoAnimal(animalId) {
      const medicoes = this.getCrescimentosByAnimal(animalId)
      return medicoes.length > 0 ? medicoes[0] : null // Já vem ordenado desc
    },

    // === FORMATAÇÃO ===
    formatarMedida(valor, unidade = '') {
      if (!valor) return '-'
      return `${parseFloat(valor).toFixed(1)} ${unidade}`.trim()
    },

    formatarGanho(valor) {
      if (!valor) return '-'
      const sinal = valor > 0 ? '+' : ''
      return `${sinal}${parseFloat(valor).toFixed(1)} kg`
    },

    // === EXPORTAÇÃO ===
    prepararDadosExportacao(animalId = null) {
      let dados = animalId
        ? this.getCrescimentosByAnimal(animalId)
        : this.crescimentos

      return dados.map(crescimento => ({
        Animal: crescimento.animal_nome,
        Data: crescimento.DATA_MEDICAO,
        'Peso (kg)': crescimento.PESO || '-',
        'Altura (cm)': crescimento.ALTURA || '-',
        'Canela (cm)': crescimento.CIRCUNFERENCIA_CANELA || '-',
        'Tórax (cm)': crescimento.CIRCUNFERENCIA_TORACICA || '-',
        'Corpo (cm)': crescimento.COMPRIMENTO_CORPO || '-',
        'Ganho Peso': this.formatarGanho(crescimento.ganho_peso),
        Observações: crescimento.OBSERVACOES || '-',
      }))
    },
  },
})
