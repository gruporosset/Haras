import { defineStore } from 'pinia'
import api from '../boot/api'

export const useAnimalStore = defineStore('animal', {
  state: () => ({
    animais: [],
    currentAnimal: null,
    genealogia: null,
    parentOptions: {
      machos: [],
      femeas: []
    },
    loading: false,
    filters: {
      nome: '',
      sexo: null,
      status: null,
      numero_registro: ''
    },
    pagination: {
      page: 1,
      rowsPerPage: 10,
      rowsNumber: 0,
      sortBy: 'ID',
      descending: false
    }
  }),

  getters: {
    animaisAtivos: (state) => state.animais.filter(a => a.STATUS_ANIMAL === 'ATIVO'),
    machos: (state) => state.animais.filter(a => a.SEXO === 'M' && a.STATUS_ANIMAL === 'ATIVO'),
    femeas: (state) => state.animais.filter(a => a.SEXO === 'F' && a.STATUS_ANIMAL === 'ATIVO'),
    
    animalById: (state) => (id) => state.animais.find(a => a.ID === id),
    
    estatisticas: (state) => {
      const total = state.animais.length
      const ativos = state.animais.filter(a => a.STATUS_ANIMAL === 'ATIVO').length
      const machos = state.animais.filter(a => a.SEXO === 'M').length
      const femeas = state.animais.filter(a => a.SEXO === 'F').length
      
      return {
        total,
        ativos,
        machos,
        femeas,
        vendidos: state.animais.filter(a => a.STATUS_ANIMAL === 'VENDIDO').length,
        emprestados: state.animais.filter(a => a.STATUS_ANIMAL === 'EMPRESTADO').length
      }
    }
  },

  actions: {
    async fetchAnimais(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: params.page || this.pagination.page,
          limit: params.limit || this.pagination.rowsPerPage,
          sort_by: params.sortBy || this.pagination.sortBy,
          order: params.descending ? 'desc' : 'asc',
          ...this.filters,
          ...params.filters
        }

        const response = await api.get('/api/animais', { params: queryParams })
        
        this.animais = response.data.animais
        this.pagination = {
          ...this.pagination,
          page: response.data.page,
          rowsNumber: response.data.total,
          rowsPerPage: response.data.limit
        }
        
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar animais'
      } finally {
        this.loading = false
      }
    },

    async getAnimal(id) {
      try {
        const response = await api.get(`/api/animais/${id}`)
        this.currentAnimal = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar animal'
      }
    },

    async createAnimal(animalData) {
      try {
        const response = await api.post('/api/animais', animalData)
        await this.fetchAnimais() // Recarregar lista
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao criar animal'
      }
    },

    async updateAnimal(id, animalData) {
      try {
        const response = await api.put(`/api/animais/${id}`, animalData)
        await this.fetchAnimais() // Recarregar lista
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao atualizar animal'
      }
    },

    async deleteAnimal(id) {
      try {
        await api.delete(`/api/animais/${id}`)
        await this.fetchAnimais() // Recarregar lista
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao excluir animal'
      }
    },

    async getGenealogia(id) {
      try {
        const response = await api.get(`/api/animais/${id}/genealogia`)
        this.genealogia = response.data
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao buscar genealogia'
      }
    },

    async uploadFoto(id, foto) {
      try {
        const formData = new FormData()
        formData.append('foto', foto)
        
        const response = await api.post(`/api/animais/${id}/foto`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        
        await this.fetchAnimais() // Recarregar lista para atualizar foto
        return response.data
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao enviar foto'
      }
    },

    async loadParentOptions() {
      try {
        const [machosRes, femeasRes] = await Promise.all([
          api.get('/api/animais/options/parents?sexo=M'),
          api.get('/api/animais/options/parents?sexo=F')
        ])
        
        this.parentOptions.machos = machosRes.data
        this.parentOptions.femeas = femeasRes.data
        
        return this.parentOptions
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao carregar opções de pais'
      }
    },

    setFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
    },

    clearFilters() {
      this.filters = {
        nome: '',
        sexo: null,
        status: null,
        numero_registro: ''
      }
    },

    setPagination(newPagination) {
      this.pagination = { ...this.pagination, ...newPagination }
    }
  }
})