<template>
  <q-page class="flex flex-center">
    <q-card class="q-pa-md" style="max-width: 400px; width: 100%;">
      <q-card-section>
        <div class="text-h6 text-center">Login</div>
      </q-card-section>
      <q-card-section>
        <q-form @submit="handleLogin" class="q-gutter-md">
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
          <q-input
            v-model="password"
            label="Senha"
            :type="showPassword ? 'text' : 'password'"
            filled
            aria-label="Senha"
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
            label="Entrar" 
            :loading="loading" 
            aria-label="Entrar no sistema"
            class="full-width"
          />
          <q-btn
            flat
            color="primary"
            label="Esqueceu a senha?"
            to="/forgot-password"
            class="full-width q-mt-sm"
          />
        </q-form>
      </q-card-section>
      <q-card-section v-if="authStore.requiresMfa">
        <q-form @submit="handleMfaVerify">
          <q-input
            v-model="mfaCode"
            label="Código TOTP"
            filled
            class="q-mb-md"
            :error="!!mfaError"
            :error-message="mfaError"
            aria-label="Código TOTP"
          />
          <div class="text-negative" v-if="mfaError">{{ mfaError }}</div>
          <q-btn color="primary" type="submit" label="Verificar MFA" :disable="loading" class="full-width" />
        </q-form>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script>
import { ref } from 'vue';
import { useAuthStore } from 'stores/auth';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const authStore = useAuthStore();
    const $q = useQuasar();
    const router = useRouter();
    const email = ref('');
    const password = ref('');
    const mfaCode = ref('');
    const error = ref('');
    const mfaError = ref('');
    const loading = ref(false);
    const showPassword = ref(false);

    const handleLogin = async () => {
      loading.value = true;
      error.value = '';
      try {
        await authStore.login(email.value, password.value);
        if (!authStore.requiresMfa) {
          $q.notify({ type: 'positive', message: 'Login realizado com sucesso!' });
          router.push('/dashboard');
        }
      } catch (err) {
        error.value = err;
        $q.notify({ type: 'negative', message: err });
      } finally {
        loading.value = false;
      }
    };

    const handleMfaVerify = async () => {
      loading.value = true;
      mfaError.value = '';
      try {
        await authStore.verifyMfa(authStore.mfaUserId, mfaCode.value);
        $q.notify({ type: 'positive', message: 'MFA verificado com sucesso!' });
        router.push('/dashboard');
      } catch (err) {
        mfaError.value = err;
        $q.notify({ type: 'negative', message: err });
      } finally {
        loading.value = false;
      }
    };

    return { email, password, mfaCode, error, mfaError, loading, 
             authStore, handleLogin, handleMfaVerify, showPassword };
  },
};
</script>

<style scoped>
.q-card {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
</style>