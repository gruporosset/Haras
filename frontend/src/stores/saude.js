// frontend/src/stores/saude.js
import { defineStore } from 'pinia'
import api from 'src/boot/api'
import { ErrorHandler } from 'src/utils/errorHandler'
import { prepareFormData } from 'src/utils/dateUtils'

export const useSaudeStore = defineStore('saude', {
  state: () => ({
    // Dados principais
    registros: [],
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
      tipo_registro: null, // APENAS TIPOS DE SAÚDE
      veterinario: '',
      data_inicio: '',
      data_fim: '',
    },

    // Dados específicos de saúde - RENOMEADOS para evitar conflito com métodos
    proximasAplicacoes: [],
    estatisticasGerais: null,
    dadosConsumoPorTipo: [], // RENOMEADO
    calendarioSaude: [],
    historicoAnimal: null,
  }),

  getters: {
    // Getter para tipos de saúde (SEM ferrageamento)
    tiposRegistro: () => [
      { value: 'VACINA', label: 'Vacina' },
      { value: 'VERMIFUGO', label: 'Vermífugo' },
      { value: 'MEDICAMENTO', label: 'Medicamento' },
      { value: 'EXAME', label: 'Exame' },
      { value: 'CONSULTA', label: 'Consulta' },
      { value: 'CIRURGIA', label: 'Cirurgia' },
      { value: 'TRATAMENTO', label: 'Tratamento' },
    ],

    // Getter para registros por status
    registrosPorStatus: state => {
      return state.registros.reduce((acc, item) => {
        const status = item.status_aplicacao || 'APLICADO'
        if (!acc[status]) acc[status] = []
        acc[status].push(item)
        return acc
      }, {})
    },

    // Getter para próximas aplicações por prioridade
    aplicacoesPorPrioridade: state => {
      const aplicacoes = {
        atrasadas: state.proximasAplicacoes.filter(a => a.dias_vencimento < 0),
        urgentes: state.proximasAplicacoes.filter(
          a => a.dias_vencimento >= 0 && a.dias_vencimento <= 7
        ),
        proximas: state.proximasAplicacoes.filter(
          a => a.dias_vencimento > 7 && a.dias_vencimento <= 30
        ),
      }
      return aplicacoes
    },

    // Getter para estatísticas resumidas
    estatisticasResumo: state => {
      if (!state.estatisticasGerais) return null

      return {
        totalRegistros: state.estatisticasGerais.total_registros,
        registrosMes: state.estatisticasGerais.registros_mes_atual,
        custoMes: state.estatisticasGerais.custo_total_mes,
        proximasAplicacoes: state.estatisticasGerais.proximas_aplicacoes,
        animaisEmTratamento: state.estatisticasGerais.animais_em_tratamento,
      }
    },
  },

  actions: {
    // === CRUD BÁSICO ===
    async fetchRegistros(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          ...this.filters,
          limit: this.pagination.rowsPerPage,
          offset: (this.pagination.page - 1) * this.pagination.rowsPerPage,
          ...params,
        }
        // Converter objetos select para valores
        if (queryParams.animal_id?.value) {
          queryParams.animal_id = queryParams.animal_id.value
        }
        if (queryParams.tipo_registro?.value) {
          queryParams.tipo_registro = queryParams.tipo_registro.value
        }

        const response = await api.get('/api/saude/', {
          params: queryParams,
        })

        this.registros = response.data.registros || []

        // Atualizar paginação se veio do response
        if (response.data.total !== undefined) {
          this.pagination.rowsNumber = response.data.total
        }

        return response.data
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao buscar registros de saúde')
        return { registros: [], total: 0 }
      } finally {
        this.loading = false
      }
    },

    // MÉTODO DE COMPATIBILIDADE com o frontend existente
    async listarRegistros(params = {}) {
      // Converter parâmetros do frontend para o novo formato
      const newParams = {
        ...params,
        page: params.page || 1,
        limit: params.limit || 50,
      }

      // Remover offset se existe (usar page em vez de offset)
      delete newParams.offset

      return await this.fetchRegistros(newParams)
    },

    async createRegistro(formData) {
      try {
        const dados = prepareFormData(formData, [
          'DATA_OCORRENCIA',
          'PROXIMA_APLICACAO',
        ])

        const response = await api.post('/api/saude/', dados)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao criar registro de saúde'
      }
    },

    async updateRegistro(id, formData) {
      try {
        const dados = prepareFormData(formData, [
          'DATA_OCORRENCIA',
          'PROXIMA_APLICACAO',
        ])

        const response = await api.put(`/api/saude/${id}`, dados)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar registro'
      }
    },

    async deleteRegistro(id) {
      try {
        await api.delete(`/api/saude/${id}`)

        // Remover da lista local
        const index = this.registros.findIndex(r => r.ID === id)
        if (index !== -1) {
          this.registros.splice(index, 1)
        }
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir registro'
      }
    },

    async getRegistro(id) {
      try {
        const response = await api.get(`/api/saude/${id}`)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar registro'
      }
    },

    // === APLICAÇÃO RÁPIDA ===
    async aplicacaoRapida(dados) {
      try {
        const response = await api.post('/api/saude/aplicacao-rapida', dados)
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro na aplicação rápida'
      }
    },

    // === PRÓXIMAS APLICAÇÕES ===
    async fetchProximasAplicacoes(diasAntecedencia = 365) {
      try {
        const response = await api.get(
          '/api/saude/calendario/proximas-aplicacoes',
          {
            params: { dias_antecedencia: diasAntecedencia },
          }
        )
        this.proximasAplicacoes = response.data
        return response.data
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao buscar próximas aplicações')
        return []
      }
    },

    // === ESTATÍSTICAS ===
    async fetchEstatisticasGerais(params = {}) {
      try {
        const response = await api.get('/api/saude/estatisticas/geral', {
          params,
        })
        this.estatisticasGerais = response.data
        return response.data
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao buscar estatísticas gerais')
        return null
      }
    },

    async fetchConsumoPorTipo(mesesPeriodo = 6) {
      try {
        const response = await api.get(
          '/api/saude/relatorio/consumo-por-tipo',
          {
            params: { meses_periodo: mesesPeriodo },
          }
        )
        this.dadosConsumoPorTipo = response.data // ATUALIZADO
        return response.data
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao buscar consumo por tipo')
        return []
      }
    },

    // MÉTODO DE COMPATIBILIDADE
    async consumoPorTipo(mesesPeriodo = 6) {
      return await this.fetchConsumoPorTipo(mesesPeriodo)
    },

    // MÉTODO DE COMPATIBILIDADE para estatísticas de veterinários
    async estatisticasVeterinarios() {
      try {
        // Buscar dados dos registros para calcular estatísticas de veterinários
        const response = await api.get('/api/saude/', {
          params: { limit: 1000 }, // Buscar mais registros para estatísticas
        })

        const registros = response.data.registros || []

        // Calcular estatísticas por veterinário
        const vetStats = {}
        registros.forEach(registro => {
          const vet = registro.VETERINARIO_RESPONSAVEL
          if (vet) {
            if (!vetStats[vet]) {
              vetStats[vet] = {
                veterinario: vet,
                total_aplicacoes: 0,
                animais_atendidos: new Set(),
                tipos_diferentes: new Set(),
                ultimo_atendimento: null,
              }
            }

            vetStats[vet].total_aplicacoes++
            vetStats[vet].animais_atendidos.add(registro.ID_ANIMAL)
            vetStats[vet].tipos_diferentes.add(registro.TIPO_REGISTRO)

            const dataAtendimento = new Date(registro.DATA_OCORRENCIA)
            if (
              !vetStats[vet].ultimo_atendimento ||
              dataAtendimento > new Date(vetStats[vet].ultimo_atendimento)
            ) {
              vetStats[vet].ultimo_atendimento = registro.DATA_OCORRENCIA
            }
          }
        })

        // Converter para array e formatar
        const resultado = Object.values(vetStats).map(stat => ({
          veterinario: stat.veterinario,
          total_aplicacoes: stat.total_aplicacoes,
          animais_atendidos: stat.animais_atendidos.size,
          tipos_diferentes: stat.tipos_diferentes.size,
          ultimo_atendimento: stat.ultimo_atendimento,
        }))

        return resultado.sort((a, b) => b.total_aplicacoes - a.total_aplicacoes)
      } catch (error) {
        ErrorHandler.handle(
          error,
          'Erro ao buscar estatísticas de veterinários'
        )
        return []
      }
    },

    // MÉTODO DE COMPATIBILIDADE para aplicações mensais
    async aplicacoesMensais(meses = 6) {
      try {
        // Como a API não existe ainda, vamos calcular localmente
        const dataLimite = new Date()
        dataLimite.setMonth(dataLimite.getMonth() - meses)

        const response = await api.get('/api/saude/', {
          params: {
            limit: 1000,
            data_inicio: dataLimite.toISOString().split('T')[0],
          },
        })

        const registros = response.data.registros || []

        // Agrupar por mês
        const aplicacoesPorMes = {}
        registros.forEach(registro => {
          const data = new Date(registro.DATA_OCORRENCIA)
          const chave = `${data.getFullYear()}-${String(data.getMonth() + 1).padStart(2, '0')}`

          if (!aplicacoesPorMes[chave]) {
            aplicacoesPorMes[chave] = {
              periodo: chave,
              total: 0,
            }
          }

          aplicacoesPorMes[chave].total++
        })

        // Converter para array ordenado
        const resultado = Object.values(aplicacoesPorMes).sort((a, b) =>
          a.periodo.localeCompare(b.periodo)
        )

        return resultado
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao buscar aplicações mensais')
        return []
      }
    },

    // === HISTÓRICO E CALENDÁRIO ===
    async fetchHistoricoAnimal(animalId, meses = 12) {
      try {
        const response = await api.get(`/api/saude/historico/${animalId}`, {
          params: { meses },
        })
        this.historicoAnimal = response.data
        return response.data
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao buscar histórico do animal')
        return null
      }
    },

    async fetchCalendarioSaude(dataInicio, dataFim) {
      try {
        const response = await api.get('/api/saude/calendario/', {
          params: {
            data_inicio: dataInicio,
            data_fim: dataFim,
          },
        })
        this.calendarioSaude = response.data
        return response.data
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao buscar calendário de saúde')
        return []
      }
    },

    // === MEDICAMENTOS ===
    async autocompleteMedicamentos(termo) {
      try {
        if (!termo || termo.length < 2) return []

        const response = await api.get('/api/saude/medicamentos/autocomplete', {
          params: { query: termo },
        })

        return response.data.map(med => ({
          value: med.id,
          label: `${med.nome} - Estoque: ${med.estoque_atual} ${med.unidade_medida}`,
          nome: med.nome,
          estoque: med.estoque_atual,
          unidade: med.unidade_medida,
        }))
      } catch (error) {
        console.error('Erro no autocomplete de medicamentos:', error)
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
        tipo_registro: null,
        veterinario: '',
        data_inicio: '',
        data_fim: '',
      }
    },

    setPagination(newPagination) {
      this.pagination = { ...this.pagination, ...newPagination }
    },

    // === MÉTODOS AUXILIARES ===
    getTipoLabel(tipo) {
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

    getTipoColor(tipo) {
      const cores = {
        VACINA: 'green',
        VERMIFUGO: 'blue',
        MEDICAMENTO: 'purple',
        EXAME: 'orange',
        CONSULTA: 'teal',
        CIRURGIA: 'red',
        TRATAMENTO: 'indigo',
      }
      return cores[tipo] || 'grey'
    },

    getStatusAplicacaoColor(status) {
      const cores = {
        APLICADO: 'green',
        PENDENTE: 'orange',
        ATRASADO: 'red',
      }
      return cores[status] || 'grey'
    },

    // === VALIDAÇÕES ===
    validarFormulario(dados) {
      const erros = []

      if (!dados.ID_ANIMAL) {
        erros.push('Animal é obrigatório')
      }

      if (!dados.TIPO_REGISTRO) {
        erros.push('Tipo de registro é obrigatório')
      }

      if (!dados.DATA_OCORRENCIA) {
        erros.push('Data de ocorrência é obrigatória')
      }

      // Validação de data
      if (
        dados.DATA_OCORRENCIA &&
        new Date(dados.DATA_OCORRENCIA) > new Date()
      ) {
        erros.push('Data de ocorrência não pode ser no futuro')
      }

      if (dados.PROXIMA_APLICACAO && dados.DATA_OCORRENCIA) {
        if (
          new Date(dados.PROXIMA_APLICACAO) <= new Date(dados.DATA_OCORRENCIA)
        ) {
          erros.push('Próxima aplicação deve ser após a data de ocorrência')
        }
      }

      // Validação de medicamento
      if (dados.ID_MEDICAMENTO && !dados.QUANTIDADE_APLICADA) {
        erros.push(
          'Quantidade aplicada é obrigatória quando medicamento é selecionado'
        )
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

    // === BUSCAR VETERINÁRIOS ===
    async buscarVeterinarios(termo = '') {
      try {
        // Buscar veterinários únicos dos registros existentes
        const response = await api.get('/api/saude/', {
          params: { limit: 1000 },
        })

        const veterinarios = [
          ...new Set(
            response.data.map(r => r.VETERINARIO_RESPONSAVEL).filter(v => v)
          ),
        ].map(v => ({
          value: v,
          label: v,
        }))

        if (termo) {
          return veterinarios.filter(v =>
            v.label.toLowerCase().includes(termo.toLowerCase())
          )
        }

        return veterinarios
      } catch (error) {
        console.error('Erro ao buscar veterinários:', error)
        return []
      }
    },

    // === CALCULAR PRÓXIMA APLICAÇÃO ===
    calcularProximaAplicacao(tipoRegistro, dataOcorrencia) {
      const intervalos = {
        VACINA: 365, // Anual
        VERMIFUGO: 90, // Trimestral
        MEDICAMENTO: 0, // Sem repetição automática
        EXAME: 0, // Conforme necessário
        CONSULTA: 0, // Conforme necessário
        CIRURGIA: 0, // Sem repetição
        TRATAMENTO: 30, // Mensal (dependendo do caso)
      }

      const dias = intervalos[tipoRegistro]
      if (dias === 0) return null

      const data = new Date(dataOcorrencia)
      data.setDate(data.getDate() + dias)

      return data.toISOString().split('T')[0] // Formato YYYY-MM-DD
    },

    // === RESUMOS PARA DASHBOARD ===
    async getDashboardData() {
      try {
        const [estatisticas, proximas, consumo] = await Promise.all([
          this.fetchEstatisticasGerais(),
          this.fetchProximasAplicacoes(15),
          this.fetchConsumoPorTipo(3),
        ])

        return {
          estatisticas,
          proximasAplicacoes: proximas.length,
          aplicacoesAtrasadas: proximas.filter(a => a.dias_vencimento < 0)
            .length,
          tipoMaisUsado: consumo[0]?.tipo_registro || null,
        }
      } catch (error) {
        console.error('Erro ao buscar dados do dashboard:', error)
        return null
      }
    },
  },
})
