<template>
  <q-page class="flex flex-center">
    <q-card class="q-pa-md" style="max-width: 400px; width: 100%;">
      <q-card-section>
        <div class="text-h6 text-center">Redefinir Senha</div>
      </q-card-section>
      <q-card-section>
        <q-form @submit="handleResetPassword" class="q-gutter-md">
          <q-input
            v-model="token"
            label="Token de Recuperação"
            filled
            aria-label="Token de Recuperação"
            :rules="[val => !!val || 'Token é obrigatório']"
          />
          <q-input
            v-model="password"
            label="Nova Senha"
            :type="showPassword ? 'text' : 'password'"
            filled
            aria-label="Nova Senha"
            :rules="[
              val => !!val || 'Senha é obrigatória',
              val => val.length >= 6 || 'Senha deve ter pelo menos 6 caracteres'
            ]"
          >
            <template v-slot:append>
              <q-icon
                :name="showPassword ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="showPassword = !showPassword"
              />
            </template>
          </q-input>
          <div class="text-negative" v-if="error">{{ error }}</div>
          <q-btn 
            color="primary" 
            type="submit" 
            label="Redefinir Senha" 
            :loading="loading" 
            class="full-width"
          />
        </q-form>
      </q-card-section>
      <q-card-section>
        <q-btn flat color="primary" label="Voltar ao Login" to="/login" />
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter, useRoute } from 'vue-router';
import api from '../boot/api';

export default {
  setup() {
    const $q = useQuasar();
    const router = useRouter();
    const route = useRoute();
    const token = ref('');
    const password = ref('');
    const showPassword = ref(false);
    const error = ref('');
    const loading = ref(false);

    // Preencher token automaticamente se presente na URL
    onMounted(() => {
      if (route.query.token) {
        token.value = route.query.token;
      }
    });

    const handleResetPassword = async () => {
      loading.value = true;
      error.value = '';
      try {
        await api.post('/auth/reset-password', { TOKEN: token.value, SENHA: password.value });
        $q.notify({ type: 'positive', message: 'Senha redefinida com sucesso!' });
        router.push('/login');
      } catch (err) {
        error.value = err.response?.data?.detail || 'Erro ao redefinir senha';
        $q.notify({ type: 'negative', message: error.value });
      } finally {
        loading.value = false;
      }
    };

    return { token, password, showPassword, error, loading, handleResetPassword };
  },
};
</script>

<style scoped>
.q-card {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
</style>