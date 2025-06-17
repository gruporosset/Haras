<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated v-if="!isLoginPage">
      <q-toolbar>
        <q-toolbar-title>
        <q-img src="/public/logo.png" width="40px" />
          Haras System
        </q-toolbar-title>
        <q-btn 
          v-if="authStore.token" 
          flat 
          label="Sair" 
          @click="handleLogout" 
        />
      </q-toolbar>
    </q-header>
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { useAuthStore } from 'src/stores/auth';
import { useQuasar } from 'quasar';
import { useRouter, useRoute } from 'vue-router';
import { computed } from 'vue';

export default {
  name: 'MainLayout',
  setup() {
    const authStore = useAuthStore();
    const $q = useQuasar();
    const router = useRouter();
    const route = useRoute();

    const isLoginPage = computed(() => route.path === '/');

    const handleLogout = () => {
      authStore.logout();
      $q.notify({ type: 'positive', message: 'Logout realizado com sucesso!' });
      router.push('/');
    };

    return { authStore, handleLogout, isLoginPage };
  }
};
</script>