import { defineStore } from 'pinia'
import api from 'boot/api'
import { prepareFormData } from 'src/utils/dateUtils'

export const useSaudeStore = defineStore('saude', {
  state: () => ({
    registros: [],
    proximasAplicacoes: [],
    estatisticas: {},
    loading: false,
  }),

  getters: {
    registrosPorAnimal: (state) => (animalId) => {
      return state.registros.filter((registro) => registro.ID_ANIMAL === animalId)
    },

    registrosPorTipo: (state) => (tipo) => {
      return state.registros.filter((registro) => registro.TIPO_REGISTRO === tipo)
    },

    proximasVacinas: (state) => {
      return state.proximasAplicacoes.filter((app) => app.tipo_registro === 'VACINA')
    },

    aplicacoesPendentes: (state) => {
      return state.proximasAplicacoes.filter((app) => app.dias_restantes <= 7)
    },

    totalRegistros: (state) => state.registros.length,

    custoTotal: (state) => {
      return state.registros.reduce((total, registro) => {
        return total + (registro.CUSTO || 0)
      }, 0)
    },
  },

  actions: {
    // === CRUD REGISTROS ===

    async listarRegistros(params = {}) {
      this.loading = true
      try {
        const response = await api.get('/api/saude/', { params })
        this.registros = response.data.registros || []
        return response.data
      } catch (error) {
        console.error('Erro ao listar registros de saúde:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async obterRegistro(id) {
      try {
        const response = await api.get(`/api/saude/${id}`)
        return response.data
      } catch (error) {
        console.error('Erro ao obter registro de saúde:', error)
        throw error
      }
    },

    async criarRegistro(dadosRegistro) {
      try {
        // Preparar dados para envio
        const dados = prepareFormData(dadosRegistro)

        const response = await api.post('/api/saude/', dados)

        // Atualizar lista local
        await this.listarRegistros()

        return response.data
      } catch (error) {
        console.error('Erro ao criar registro de saúde:', error)
        throw error
      }
    },

    async atualizarRegistro(id, dadosRegistro) {
      try {
        // Preparar dados para envio
        const dados = prepareFormData(dadosRegistro)

        const response = await api.put(`/api/saude/${id}`, dados)

        // Atualizar lista local
        await this.listarRegistros()

        return response.data
      } catch (error) {
        console.error('Erro ao atualizar registro de saúde:', error)
        throw error
      }
    },

    async excluirRegistro(id) {
      try {
        await api.delete(`/api/saude/${id}`)

        // Remover da lista local
        this.registros = this.registros.filter((registro) => registro.ID !== id)

        return true
      } catch (error) {
        console.error('Erro ao excluir registro de saúde:', error)
        throw error
      }
    },

    // === APLICAÇÃO RÁPIDA ===

    async aplicacaoRapida(dadosAplicacao) {
      try {
        const dados = prepareFormData(dadosAplicacao)

        const response = await api.post('/api/saude/aplicacao-rapida', dados)

        // Atualizar lista local
        await this.listarRegistros()

        return response.data
      } catch (error) {
        console.error('Erro na aplicação rápida:', error)
        throw error
      }
    },

    // === AUTOCOMPLETE MEDICAMENTOS ===

    async autocompleteMedicamentos(termo) {
      try {
        const response = await api.get('/api/saude/autocomplete/medicamentos', {
          params: { termo, limit: 20 },
        })
        return response.data
      } catch (error) {
        console.error('Erro ao buscar medicamentos:', error)
        return []
      }
    },

    // === ESTATÍSTICAS E RELATÓRIOS ===

    async estatisticasPorAnimal(animalId) {
      try {
        const response = await api.get(`/api/saude/estatisticas/animal/${animalId}`)
        return response.data
      } catch (error) {
        console.error('Erro ao obter estatísticas do animal:', error)
        throw error
      }
    },

    async proximasAplicacoes(params = {}) {
      try {
        const response = await api.get('/api/saude/proximas-aplicacoes', { params })
        this.proximasAplicacoes = response.data
        return response.data
      } catch (error) {
        console.error('Erro ao obter próximas aplicações:', error)
        return []
      }
    },

    async calendarioSaude(mes, ano) {
      try {
        const response = await api.get('/api/saude/calendario', {
          params: { mes, ano },
        })
        return response.data
      } catch (error) {
        console.error('Erro ao obter calendário de saúde:', error)
        return []
      }
    },

    async aplicacoesMensais(meses = 6) {
      try {
        const response = await api.get('/api/saude/relatorio/aplicacoes-mensais', {
          params: { meses },
        })
        return response.data
      } catch (error) {
        console.error('Erro ao obter aplicações mensais:', error)
        return []
      }
    },

    async consumoPorTipo(params = {}) {
      try {
        const response = await api.get('/api/saude/relatorio/consumo-por-tipo', { params })
        return response.data
      } catch (error) {
        console.error('Erro ao obter consumo por tipo:', error)
        return []
      }
    },

    async historicoAnimal(animalId, params = {}) {
      try {
        const response = await api.get(`/api/saude/historico/${animalId}`, { params })
        return response.data
      } catch (error) {
        console.error('Erro ao obter histórico do animal:', error)
        throw error
      }
    },

    async estatisticasVeterinarios(params = {}) {
      try {
        const response = await api.get('/api/saude/estatisticas/veterinarios-estatisticas', {
          params,
        })
        return response.data
      } catch (error) {
        console.error('Erro ao obter estatísticas de veterinários:', error)
        return []
      }
    },

    // === RELATÓRIOS ===

    async relatorioSaude(params = {}) {
      try {
        const response = await api.get('/api/saude/relatorio', {
          params,
          responseType: 'blob',
        })

        // Criar link para download
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `relatorio_saude_${new Date().getTime()}.pdf`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)

        return true
      } catch (error) {
        console.error('Erro ao gerar relatório de saúde:', error)
        throw error
      }
    },

    async exportarDados(formato = 'excel', params = {}) {
      try {
        const response = await api.get('/api/saude/exportar', {
          params: { ...params, formato },
          responseType: 'blob',
        })

        const extension = formato === 'excel' ? 'xlsx' : 'csv'
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `saude_${new Date().getTime()}.${extension}`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)

        return true
      } catch (error) {
        console.error('Erro ao exportar dados de saúde:', error)
        throw error
      }
    },

    // === VALIDAÇÕES E HELPERS ===

    validarRegistro(registro) {
      const erros = []

      if (!registro.ID_ANIMAL) {
        erros.push('Animal é obrigatório')
      }

      if (!registro.TIPO_REGISTRO) {
        erros.push('Tipo de registro é obrigatório')
      }

      if (!registro.DATA_OCORRENCIA) {
        erros.push('Data de ocorrência é obrigatória')
      }

      if (registro.DATA_OCORRENCIA && new Date(registro.DATA_OCORRENCIA) > new Date()) {
        erros.push('Data de ocorrência não pode ser no futuro')
      }

      if (registro.PROXIMA_APLICACAO && registro.DATA_OCORRENCIA) {
        if (new Date(registro.PROXIMA_APLICACAO) <= new Date(registro.DATA_OCORRENCIA)) {
          erros.push('Próxima aplicação deve ser após a data de ocorrência')
        }
      }

      if (registro.ID_MEDICAMENTO && !registro.QUANTIDADE_APLICADA) {
        erros.push('Quantidade é obrigatória quando medicamento do estoque é selecionado')
      }

      if (registro.CUSTO && registro.CUSTO < 0) {
        erros.push('Custo não pode ser negativo')
      }

      return erros
    },

    // === CACHE E PERFORMANCE ===

    limparCache() {
      this.registros = []
      this.proximasAplicacoes = []
      this.estatisticas = {}
    },

    // === FILTROS AVANÇADOS ===

    async buscarComFiltros(filtros) {
      const params = {}

      if (filtros.animal_id) params.animal_id = filtros.animal_id
      if (filtros.tipo_registro) params.tipo_registro = filtros.tipo_registro
      if (filtros.data_inicio) params.data_inicio = filtros.data_inicio
      if (filtros.data_fim) params.data_fim = filtros.data_fim
      if (filtros.veterinario) params.veterinario = filtros.veterinario
      if (filtros.medicamento) params.medicamento = filtros.medicamento
      if (filtros.custo_min) params.custo_min = filtros.custo_min
      if (filtros.custo_max) params.custo_max = filtros.custo_max

      return await this.listarRegistros(params)
    },

    // === INTEGRAÇÕES ===

    async sincronizarComMedicamentos() {
      try {
        // Buscar medicamentos com baixo estoque que foram aplicados recentemente
        const response = await api.get('/api/saude/sincronizar-medicamentos')
        return response.data
      } catch (error) {
        console.error('Erro ao sincronizar com medicamentos:', error)
        throw error
      }
    },

    async alertasVencimento() {
      try {
        const response = await api.get('/api/saude/alertas-vencimento')
        return response.data
      } catch (error) {
        console.error('Erro ao obter alertas de vencimento:', error)
        return []
      }
    },

    // === NOTIFICAÇÕES ===

    async configurarNotificacoes(config) {
      try {
        const response = await api.post('/api/saude/configurar-notificacoes', config)
        return response.data
      } catch (error) {
        console.error('Erro ao configurar notificações:', error)
        throw error
      }
    },

    // === BACKUP/RESTORE ===

    async backupDados() {
      try {
        const response = await api.get('/api/saude/backup', {
          responseType: 'blob',
        })

        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `backup_saude_${new Date().toISOString().split('T')[0]}.json`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)

        return true
      } catch (error) {
        console.error('Erro ao fazer backup:', error)
        throw error
      }
    },
  },
})
