<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Bem-vindo, {{ authStore.user?.NOME_COMPLETO || 'Usuário' }}</div>
        <div class="text-subtitle1">Painel de Controle</div>
      </q-card-section>
      <q-card-section>
        <p>Este é o painel inicial do sistema Haras. Escolha uma opção no menu para continuar.</p>
        <q-btn 
          color="negative" 
          label="Sair" 
          @click="handleLogout" 
        />
      </q-card-section>
    </q-card>
  </q-page>
</template>


<script>
import { useAuthStore } from '../stores/auth';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const authStore = useAuthStore();
    const $q = useQuasar();
    const router = useRouter();

    const handleLogout = () => {
      authStore.clearAuthData();
      $q.notify({ type: 'positive', message: 'Logout realizado com sucesso!' });
      router.push('/');
    };

    return { authStore, handleLogout };
  }
};
</script>

