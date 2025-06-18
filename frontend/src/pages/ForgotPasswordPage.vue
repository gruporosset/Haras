<template>
  <q-page class="flex flex-center">
    <q-card class="q-pa-md" style="max-width: 400px; width: 100%;">
      <q-card-section>
        <div class="text-h6 text-center">Recuperar Senha</div>
      </q-card-section>
      <q-card-section>
        <q-form @submit="handleForgotPassword" class="q-gutter-md">
          <q-input
            v-model="email"
            label="E-mail"
            type="email"
            filled
            aria-label="E-mail"
            :rules="[
              val => !!val || 'E-mail é obrigatório',
              val => /.+@.+\..+/.test(val) || 'E-mail inválido'
            ]"
          />
          <div class="text-negative" v-if="error">{{ error }}</div>
          <q-btn 
            color="primary" 
            type="submit" 
            label="Enviar E-mail de Recuperação" 
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
import { ref } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import api from '../boot/api';

export default {
  setup() {
    const $q = useQuasar();
    const router = useRouter();
    const email = ref('');
    const error = ref('');
    const loading = ref(false);

    const handleForgotPassword = async () => {
      loading.value = true;
      error.value = '';
      try {
        await api.post('/auth/forgot-password', { EMAIL: email.value });
        $q.notify({ type: 'positive', message: 'E-mail de recuperação enviado! Verifique sua caixa de entrada.' });
        router.push('/login');
      } catch (err) {
        error.value = err.response?.data?.detail || 'Erro ao enviar e-mail';
        $q.notify({ type: 'negative', message: error.value });
      } finally {
        loading.value = false;
      }
    };

    return { email, error, loading, handleForgotPassword };
  },
};
</script>

<style scoped>
.q-card {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
</style>