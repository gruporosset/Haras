import { defineStore } from 'pinia';
import api from '../boot/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    access_token: null,
    refresh_token: null,
    requiresMfa: false,
    mfaUserId: null,
    mfaSetup: null,
  }),
  actions: {
    async login(email, password) {
      try {
        const response = await api.post('/auth/login', {
          EMAIL: email,
          SENHA: password,
        });
        if (response.data.requires_mfa) {
          this.requiresMfa = true;
          this.mfaUserId = response.data.user_id;
        } else {
          this.setAuthData(response.data);
        }
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao fazer login';
      }
    },
    
    async refreshToken() {
      try {
        const response = await api.post('/auth/refresh', { refresh_token: this.refresh_token })
        this.access_token = response.data.access_token
        localStorage.setItem('access_token_haras', this.access_token)
      } catch (error) {
        this.clearAuthData()
        throw error.response?.data?.detail || 'Sessão expirada'
      }
    },

    setAuthData(data) {
      this.user = data.user;
      this.access_token = data.access_token
      this.refresh_token = data.refresh_token
      this.requiresMfa = false;
      
      localStorage.setItem('user_haras', JSON.stringify(data.user));
      localStorage.setItem('access_token_haras', data.access_token)
      localStorage.setItem('refresh_token_haras', data.refresh_token)
    },
    
    clearAuthData() {
      this.user = null;
      this.access_token = null
      this.refresh_token = null
      this.requiresMfa = false;
      this.mfaUserId = null;
      this.mfaSetup = null;
      
      // Remove do localStorage
      localStorage.removeItem('user_haras');
      localStorage.removeItem('access_token_haras')
      localStorage.removeItem('refresh_token_haras')
    },    

    async verifyMfa(userId, code) {
      try {
        const response = await api.post('/auth/mfa/verify', {
          user_id: userId,
          code,
        });
        this.setAuthData(response.data);
      } catch (error) {
        throw error.response?.data?.detail || 'Código MFA inválido';
      }
    },

    async setupMfa(userId) {
      try {
        const response = await api.post('/auth/mfa/setup', { user_id: userId });
        this.mfaSetup = response.data;
        this.user = response.data.user;
        localStorage.setItem('user_haras', JSON.stringify(this.user));
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao configurar MFA';
      }
    },
    
    async disableMfa(userId) {
      try {
        const response = await api.post('/auth/mfa/disable', { user_id: userId });
        this.user = response.data.user;
        this.mfaSetup = null;
        localStorage.setItem('user_haras', JSON.stringify(this.user));
      } catch (error) {
        throw error.response?.data?.detail || 'Erro ao desativar MFA';
      }
    },    
    
    async logout() {
      try {
        await api.post('/auth/logout', { refresh_token: this.refresh_token })
      } catch (error) {
        console.error('Erro ao fazer logout:', error)
      } finally {
        this.clearAuthData()
      }
    },
  },
});