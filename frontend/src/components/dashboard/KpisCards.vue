<template>
  <div class="row q-gutter-md">
    <!-- Total Animais -->
    <div class="col-12 col-sm-6 col-md-4">
      <q-card class="cursor-pointer" @click="$router.push('/animais')">
        <q-card-section class="row items-center">
          <div class="col">
            <div class="text-h4 text-primary">{{ kpis.total_animais }}</div>
            <div class="text-subtitle1">Total de Animais</div>
          </div>
          <div class="col-auto">
            <q-icon name="pets" size="48px" color="primary" />
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Total Terrenos -->
    <div class="col-12 col-sm-6 col-md-4">
      <q-card class="cursor-pointer" @click="$router.push('/terrenos')">
        <q-card-section class="row items-center">
          <div class="col">
            <div class="text-h4 text-green">{{ kpis.total_terrenos }}</div>
            <div class="text-subtitle1">Total de Terrenos</div>
          </div>
          <div class="col-auto">
            <q-icon name="landscape" size="48px" color="green" />
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Animais em Tratamento -->
    <div class="col-12 col-sm-6 col-md-4">
      <q-card class="cursor-pointer" @click="$router.push('/saude')">
        <q-card-section class="row items-center">
          <div class="col">
            <div class="text-h4 text-orange">{{ kpis.animais_tratamento }}</div>
            <div class="text-subtitle1">Em Tratamento</div>
          </div>
          <div class="col-auto">
            <q-icon name="healing" size="48px" color="orange" />
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Alertas de Estoque -->
    <div class="col-12 col-sm-6 col-md-4">
      <q-card 
        class="cursor-pointer" 
        :class="kpis.alertas_estoque > 0 ? 'bg-red-1' : ''"
        @click="scrollToAlertas"
      >
        <q-card-section class="row items-center">
          <div class="col">
            <div class="text-h4" :class="kpis.alertas_estoque > 0 ? 'text-negative' : 'text-grey'">
              {{ kpis.alertas_estoque }}
            </div>
            <div class="text-subtitle1">Alertas de Estoque</div>
          </div>
          <div class="col-auto">
            <q-icon 
              name="inventory_2" 
              size="48px" 
              :color="kpis.alertas_estoque > 0 ? 'negative' : 'grey'" 
            />
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Próximas Aplicações -->
    <div class="col-12 col-sm-6 col-md-4">
      <q-card 
        class="cursor-pointer"
        :class="kpis.proximas_aplicacoes > 0 ? 'bg-orange-1' : ''"
        @click="$router.push('/saude')"
      >
        <q-card-section class="row items-center">
          <div class="col">
            <div class="text-h4" :class="kpis.proximas_aplicacoes > 0 ? 'text-orange' : 'text-grey'">
              {{ kpis.proximas_aplicacoes }}
            </div>
            <div class="text-subtitle1">Próximas Aplicações</div>
            <div class="text-caption text-grey">Próximos 7 dias</div>
          </div>
          <div class="col-auto">
            <q-icon 
              name="schedule" 
              size="48px" 
              :color="kpis.proximas_aplicacoes > 0 ? 'orange' : 'grey'" 
            />
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Gestações Ativas -->
    <div class="col-12 col-sm-6 col-md-4">
      <q-card class="cursor-pointer" @click="$router.push('/reproducao')">
        <q-card-section class="row items-center">
          <div class="col">
            <div class="text-h4 text-pink">{{ kpis.gestacoes_ativas }}</div>
            <div class="text-subtitle1">Gestações Ativas</div>
          </div>
          <div class="col-auto">
            <q-icon name="pregnant_woman" size="48px" color="pink" />
          </div>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useDashboardStore } from 'src/stores/dashboard'
import { useRouter } from 'vue-router'

export default {
  name: 'KpisCards',
  
  setup() {
    const dashboardStore = useDashboardStore()
    const router = useRouter()
    
    const kpis = computed(() => dashboardStore.kpis)
    
    const scrollToAlertas = () => {
      const element = document.getElementById('alertas-section')
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' })
      }
    }
    
    return {
      kpis,
      scrollToAlertas,
      router
    }
  }
}
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
  transition: transform 0.2s;
}

.cursor-pointer:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
</style>