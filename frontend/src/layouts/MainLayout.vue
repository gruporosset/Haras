<template>
  <q-layout view="lHh Lpr lFf">
    <template v-if="!isLoginPage">
      <q-header elevated>
          <q-toolbar>
            <q-btn
            flat
            dense
            round
            :icon="leftDrawerOpen ? 'chevron_left' : 'menu'"
            aria-label="Menu"
            @click="toggleLeftDrawer"
          />
          <q-toolbar-title>
          <q-img src="/logo.png" width="40px" />
            Haras System
          </q-toolbar-title>
          <q-btn 
            v-if="authStore.access_token" 
            flat 
            label="Sair" 
            @click="handleLogout" 
          />
        </q-toolbar>
      </q-header>
      <q-drawer
        v-model="leftDrawerOpen"
        show-if-above
        bordered
      >
        <q-list>
          <q-item-label header>Menu</q-item-label>
          <q-item to="/dashboard" clickable>
            <q-item-section avatar>
              <q-icon name="dashboard" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Painel</q-item-label>
            </q-item-section>
          </q-item>
          <q-item to="/profile" clickable>
            <q-item-section avatar>
              <q-icon name="person" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Perfil</q-item-label>
            </q-item-section>
          </q-item>
          <q-item clickable v-ripple to="/terrenos">
            <q-item-section avatar>
              <q-icon name="landscape" />
            </q-item-section>
            <q-item-section>Terrenos</q-item-section>
          </q-item>
          <!-- Adicionar mais itens conforme necessário -->
        </q-list>
      </q-drawer>    
    </template>
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>

import { useAuthStore } from 'src/stores/auth';
import { useQuasar } from 'quasar';
import { useRouter, useRoute } from 'vue-router';
import { computed,ref } from 'vue';

export default {
  name: 'MainLayout',
  setup() {
    const authStore = useAuthStore();
    const $q = useQuasar();
    const router = useRouter();
    const route = useRoute();
    const leftDrawerOpen = ref(false);
    const standAlonePages = ['/login','/forgot-password', '/reset-password']
    
    const isLoginPage = computed(() => standAlonePages.includes(route.path));

    const toggleLeftDrawer = () => {
      leftDrawerOpen.value = !leftDrawerOpen.value;
    };

    const handleLogout = () => {
      authStore.logout();
      $q.notify({ type: 'positive', message: 'Logout realizado com sucesso!' });
      router.push('/login');
    };

    return { authStore, handleLogout, isLoginPage, toggleLeftDrawer, leftDrawerOpen };
  }
};
</script>