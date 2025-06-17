<template>
  <q-page padding>
    <h1>Bem-vindo, {{ authStore.user?.name }}</h1>
    <q-btn 
      color="negative" 
      label="Sair" 
      @click="handleLogout" 
    />
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