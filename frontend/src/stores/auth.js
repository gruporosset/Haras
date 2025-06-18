import { defineStore } from 'pinia';
import api from '../boot/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
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

    setAuthData(data) {
      this.user = data.user;
      this.token = data.token;
      this.requiresMfa = false;
      
      localStorage.setItem('user_haras', JSON.stringify(data.user));
      localStorage.setItem('token_haras', data.token);
    },
    
    clearAuthData() {
      this.user = null;
      this.token = null;
      this.requiresMfa = false;
      this.mfaUserId = null;
      this.mfaSetup = null;
      
      // Remove do localStorage
      localStorage.removeItem('user_haras');
      localStorage.removeItem('token_haras');
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
    
    logout() {
      this.clearAuthData();
    },
  },
});