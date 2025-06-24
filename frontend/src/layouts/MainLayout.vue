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
          <q-expansion-item
            expand-separator
            icon="pets"
            label="Animais"
            default-opened
          >
            <q-item to="/animais" clickable v-ripple>
              <q-item-section avatar>
                <q-icon name="create" />
              </q-item-section>
              <q-item-section>Cadastro de Animais</q-item-section>
            </q-item>

            <q-item to="/crescimento" clickable v-ripple>
              <q-item-section avatar>
                <q-icon name="trending_up" />
              </q-item-section>
              <q-item-section>Crescimento</q-item-section>
            </q-item>
            <q-item to="/reproducao" clickable v-ripple>
              <q-item-section avatar>
                <q-icon name="favorite" />
              </q-item-section>
              <q-item-section>Reprodução</q-item-section>
            </q-item>
            <q-item to="/movimentacoes" clickable v-ripple>
              <q-item-section avatar>
                <q-icon name="swap_horiz" />
              </q-item-section>
              <q-item-section>Movimentações</q-item-section>
            </q-item>
          </q-expansion-item>

          <q-expansion-item
            expand-separator
            icon="medication"
            label="Medicamentos"
            default-opened
          >

            <q-item clickable v-ripple to="/medicamentos">
              <q-item-section avatar>
                <q-icon name="create" />
              </q-item-section>
              <q-item-section>Cadastro de Medicamentos</q-item-section>
              <q-item-section side v-if="medicamentoStore.alertasEstoque.length > 0">
                <q-badge color="negative" :label="medicamentoStore.alertasEstoque.length" />
              </q-item-section>
            </q-item>            
            
          </q-expansion-item>
          <q-expansion-item
            expand-separator
            icon="landscape"
            label="Terrenos"
            default-opened
          >
            <q-item to="/terrenos" clickable v-ripple>
              <q-item-section avatar>
                <q-icon name="create" />
              </q-item-section>
              <q-item-section>Cadastro de Terrenos</q-item-section>
            </q-item>
            <q-item to="/manejo" clickable v-ripple>
              <q-item-section avatar>
                <q-icon name="eco" />
              </q-item-section>
              <q-item-section>Manejo de Terrenos</q-item-section>
            </q-item>
          </q-expansion-item>
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
import { computed, ref } from 'vue';
import { useMedicamentoStore } from '../stores/medicamento'

export default {
  name: 'MainLayout',
  setup() {
    const authStore = useAuthStore();
    const $q = useQuasar();
    const router = useRouter();
    const route = useRoute();
    const leftDrawerOpen = ref(false);
    const standAlonePages = ['/login', '/forgot-password', '/reset-password'];
    
    const isLoginPage = computed(() => standAlonePages.includes(route.path));

    const medicamentoStore = useMedicamentoStore()

    const toggleLeftDrawer = () => {
      leftDrawerOpen.value = !leftDrawerOpen.value;
    };

    const handleLogout = () => {
      authStore.logout();
      $q.notify({ type: 'positive', message: 'Logout realizado com sucesso!' });
      router.push('/login');
    };

    return { authStore, handleLogout, isLoginPage, toggleLeftDrawer, leftDrawerOpen, medicamentoStore };
  }
};
</script>