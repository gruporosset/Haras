<template>
  <q-page class="q-pa-md">
    <!-- Banner MFA -->
    <q-banner 
      v-if="authStore.user?.MFA_ATIVO == 'N'"
      class="bg-negative text-white q-mb-md"
      inline-actions
      dense
      rounded
    >
      <template v-slot:avatar>
        <q-icon name="warning" color="white" />
      </template>
      Ative a autenticação multifator (MFA) para maior segurança!
      <template v-slot:action>
        <q-btn flat color="white" label="Configurar agora" to="/profile" />
      </template>
    </q-banner>

    <!-- Cabeçalho do Dashboard -->
    <div class="row items-center q-mb-lg">
      <div class="col">
        <div class="text-h4 text-primary">
          <q-icon name="dashboard" class="q-mr-sm" />
          Dashboard
        </div>
        <div class="text-subtitle1 text-grey">
          Bem-vindo, {{ authStore.user?.NOME_COMPLETO || 'Usuário' }}
        </div>
      </div>
      <div class="col-auto">
        <!-- Filtros rápidos -->
        <q-btn-group>
          <q-btn 
            :outline="!isUltimos30Dias"
            :unelevated="isUltimos30Dias"
            color="primary"
            label="30 dias"
            @click="aplicarFiltro30Dias"
          />
          <q-btn 
            :outline="!isUltimos90Dias"
            :unelevated="isUltimos90Dias"
            color="primary"
            label="90 dias"
            @click="aplicarFiltro90Dias"
          />
          <q-btn 
            flat
            icon="filter_alt"
            @click="mostrarFiltros = !mostrarFiltros"
          >
            <q-tooltip>Filtros avançados</q-tooltip>
          </q-btn>
          <q-btn 
            flat
            icon="refresh"
            @click="atualizarDashboard"
            :loading="dashboardStore.loading"
          >
            <q-tooltip>Atualizar dados</q-tooltip>
          </q-btn>
        </q-btn-group>
      </div>
    </div>

    <!-- Filtros Avançados (Expansível) -->
    <q-slide-transition>
      <q-card v-show="mostrarFiltros" class="q-mb-md">
        <q-card-section>
          <div class="text-h6 q-mb-md">Filtros Avançados</div>
          <div class="row q-gutter-md">
            <div class="col-12 col-sm-6 col-md-3">
              <q-input
                v-model="filtrosTemp.data_inicio"
                type="date"
                label="Data Início"
                outlined
                dense
              />
            </div>
            <div class="col-12 col-sm-6 col-md-3">
              <q-input
                v-model="filtrosTemp.data_fim"
                type="date"
                label="Data Fim"
                outlined
                dense
              />
            </div>
            <div class="col-12 col-sm-6 col-md-4">
              <q-input
                v-model="filtrosTemp.proprietario"
                label="Proprietário"
                outlined
                dense
                clearable
              />
            </div>
            <div class="col-12 col-sm-6 col-md-2">
              <q-btn 
                color="primary"
                label="Aplicar"
                @click="aplicarFiltros"
                :loading="dashboardStore.loading"
                class="full-width"
              />
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-slide-transition>

    <!-- Loading Geral -->
    <q-inner-loading :showing="dashboardStore.loading && !dashboardData">
      <q-spinner-dots size="48px" color="primary" />
    </q-inner-loading>

    <!-- Conteúdo Principal -->
    <div v-if="dashboardData">
      <!-- KPIs Cards -->
      <div class="q-mb-xl">
        <KpisCards />
      </div>

      <!-- Alertas -->
      <div class="q-mb-xl">
        <AlertasDashboard />
      </div>

      <!-- Custos por Proprietário -->
      <div class="q-mb-xl">
        <CustosProprietarios />
      </div>

      <!-- Gráficos -->
      <div class="q-mb-xl">
        <GraficosDashboard />
      </div>

      <!-- Informações do rodapé -->
      <q-card class="bg-grey-1">
        <q-card-section class="text-center">
          <div class="text-caption text-grey">
            Última atualização: {{ formatarDataUpdate(dashboardStore.ultimo_update) }}
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Estado vazio -->
    <div v-else-if="!dashboardStore.loading" class="text-center q-pa-xl">
      <q-icon name="dashboard" size="64px" color="grey-5" />
      <div class="text-h6 text-grey q-mt-md">
        Nenhum dado disponível
      </div>
      <div class="text-body2 text-grey q-mb-md">
        Verifique se há registros no sistema ou ajuste os filtros
      </div>
      <q-btn 
        color="primary"
        label="Recarregar"
        @click="carregarDashboard"
      />
    </div>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from 'src/stores/auth'
import { useDashboardStore } from 'src/stores/dashboard'
import { useQuasar } from 'quasar'

// Componentes do Dashboard
import KpisCards from 'src/components/dashboard/KpisCards.vue'
import AlertasDashboard from 'src/components/dashboard/AlertasDashboard.vue'
import CustosProprietarios from 'src/components/dashboard/CustosProprietarios.vue'
import GraficosDashboard from 'src/components/dashboard/GraficosDashboard.vue'

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()
const $q = useQuasar()

// Estado local
const mostrarFiltros = ref(false)
const filtrosTemp = ref({
  data_inicio: '',
  data_fim: '',
  proprietario: ''
})

// Computed
const dashboardData = computed(() => dashboardStore.dashboardData)

const isUltimos30Dias = computed(() => {
  const filtros = dashboardStore.filtros
  if (!filtros.data_inicio || !filtros.data_fim) return true
  
  const inicio = new Date(filtros.data_inicio)
  const fim = new Date(filtros.data_fim)
  const diferenca = Math.ceil((fim - inicio) / (1000 * 60 * 60 * 24))
  
  return diferenca <= 35 && diferenca >= 25 // Margem para 30 dias
})

const isUltimos90Dias = computed(() => {
  const filtros = dashboardStore.filtros
  if (!filtros.data_inicio || !filtros.data_fim) return false
  
  const inicio = new Date(filtros.data_inicio)
  const fim = new Date(filtros.data_fim)
  const diferenca = Math.ceil((fim - inicio) / (1000 * 60 * 60 * 24))
  
  return diferenca <= 95 && diferenca >= 85 // Margem para 90 dias
})

// Métodos
const carregarDashboard = async () => {
  try {
    await dashboardStore.loadDashboard()
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao carregar dashboard: ' + error
    })
  }
}

const atualizarDashboard = async () => {
  try {
    await dashboardStore.refreshDashboard()
    $q.notify({
      type: 'positive',
      message: 'Dashboard atualizado com sucesso!'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao atualizar dashboard: ' + error
    })
  }
}

const aplicarFiltro30Dias = () => {
  const hoje = new Date()
  const inicio = new Date()
  inicio.setDate(hoje.getDate() - 30)
  
  const filtros = {
    data_inicio: inicio.toISOString().split('T')[0],
    data_fim: hoje.toISOString().split('T')[0],
    proprietario: null
  }
  
  dashboardStore.setFiltros(filtros)
  carregarDashboard()
}

const aplicarFiltro90Dias = () => {
  const hoje = new Date()
  const inicio = new Date()
  inicio.setDate(hoje.getDate() - 90)
  
  const filtros = {
    data_inicio: inicio.toISOString().split('T')[0],
    data_fim: hoje.toISOString().split('T')[0],
    proprietario: null
  }
  
  dashboardStore.setFiltros(filtros)
  carregarDashboard()
}

const aplicarFiltros = () => {
  const filtros = {
    data_inicio: filtrosTemp.value.data_inicio || null,
    data_fim: filtrosTemp.value.data_fim || null,
    proprietario: filtrosTemp.value.proprietario || null
  }
  
  dashboardStore.setFiltros(filtros)
  carregarDashboard()
  mostrarFiltros.value = false
}

const formatarDataUpdate = (data) => {
  if (!data) return 'Nunca'
  
  const dataObj = new Date(data)
  return dataObj.toLocaleString('pt-BR')
}

// Lifecycle
onMounted(() => {
  carregarDashboard()
})
</script>

<style scoped>
.q-page {
  min-height: calc(100vh - 50px);
}

.q-btn-group .q-btn {
  border-radius: 0;
}

.q-btn-group .q-btn:first-child {
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
}

.q-btn-group .q-btn:last-child {
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}

.q-slide-transition {
  overflow: hidden;
}
</style>