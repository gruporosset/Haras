<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md text-primary">
      <q-icon name="construction" class="q-mr-sm" />
      Ferrageamento e Casqueamento
    </div>

    <q-card>
      <q-card-section>
        <!-- Alertas de Vencimento -->
        <div v-if="ferrageamentoStore.alertasVencimento.length > 0" class="q-mt-md">
          <q-banner class="bg-warning text-dark">
            <template v-slot:avatar>
              <q-icon name="schedule" />
            </template>
            {{ ferrageamentoStore.alertasVencimento.length }} animal(is) com ferrageamento/casqueamento vencido ou próximo do vencimento!
            <template v-slot:action>
              <q-btn
                flat
                label="Ver Alertas"
                @click="activeTab = 'alertas'"
              />
            </template>
          </q-banner>
        </div>
      </q-card-section>
      
      <q-card-section>
        <!-- Filtros Gerais -->
        <div class="col-12 q-mb-md">
          <q-card flat bordered class="q-pa-md">
            <div class="row q-gutter-md q-mb-md">
              <div class="col-md-3 col-12">
                <q-select
                  v-model="filtroAnimal"
                  :options="animalOptions"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  use-input
                  @filter="filterAnimais"
                  label="Filtrar por Animal"
                  clearable
                  @update:model-value="onFilterChange"
                />
              </div>
              <div class="col-md-3 col-12">
                <q-select
                  v-model="filtroTipo"
                  :options="ferrageamentoStore.tiposFerrageamento"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  label="Tipo"
                  clearable
                  @update:model-value="onFilterChange"
                />
              </div>
              <div class="col-md-3 col-12">
                <q-input
                  v-model="filtroFerrador"
                  label="Ferrador"
                  clearable
                  @update:model-value="onFilterChange"
                  :debounce="300"
                />
              </div>
              <div class="col-md-3 col-12">
                <q-toggle
                  v-model="filtroVencidos"
                  label="Apenas Vencidos"
                  @update:model-value="onFilterChange"
                />
              </div>
            </div>
          </q-card>
        </div>
        
        <!-- Estatísticas Rápidas -->
        <div class="row q-gutter-md q-mb-md">
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-primary">{{ ferrageamentoStore.estatisticasGerais.totalRegistros }}</div>
              <div class="text-caption">Total Registros</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-negative">{{ ferrageamentoStore.estatisticasGerais.vencidos }}</div>
              <div class="text-caption">Vencidos</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-positive">{{ ferrageamentoStore.estatisticasGerais.emDia }}</div>
              <div class="text-caption">Em Dia</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-accent">R$ {{ ferrageamentoStore.estatisticasGerais.custoTotal.toFixed(2) }}</div>
              <div class="text-caption">Custo Total</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-warning">{{ ferrageamentoStore.estatisticasGerais.alertasAtivos }}</div>
              <div class="text-caption">Alertas Ativos</div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Custo do Mês -->
        <div class="row q-gutter-md q-mb-md">
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h5 text-info">R$ {{ ferrageamentoStore.custoTotalMes.toFixed(2) }}</div>
              <div class="text-caption">Custo do Mês Atual</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h5 text-secondary">{{ ferrageamentoStore.ferradoresMaisAtivos.length }}</div>
              <div class="text-caption">Ferradores Ativos</div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Component de Ferrageamento -->
        <FerrageamentoComponent ref="ferrageamentoComponent" />
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useFerrageamentoStore } from 'stores/ferrageamento'
import { useAnimalStore } from 'stores/animal'
import FerrageamentoComponent from 'components/ferrageamento/FerrageamentoComponent.vue'

// Composables
const $q = useQuasar()
const ferrageamentoStore = useFerrageamentoStore()
const animalStore = useAnimalStore()

// Estado reativo
const activeTab = ref('registros')
const ferrageamentoComponent = ref(null)

// Filtros da página
const filtroAnimal = ref(null)
const filtroTipo = ref(null)
const filtroFerrador = ref('')
const filtroVencidos = ref(false)

// Opções
const animalOptions = ref([])

// Métodos
function onFilterChange() {
  const filtros = {
    animal_id: filtroAnimal.value,
    tipo_registro: filtroTipo.value,
    ferrador: filtroFerrador.value,
    apenas_vencidos: filtroVencidos.value
  }
  
  ferrageamentoStore.setFilters(filtros)
  ferrageamentoStore.fetchFerrageamentos()
}

function filterAnimais(val, update) {
  update(() => {
    if (val === '') {
      animalOptions.value = animalStore.animais.map(a => ({ value: a.ID, label: a.NOME }))
    } else {
      const needle = val.toLowerCase()
      const allAnimais = animalStore.animais.map(a => ({ value: a.ID, label: a.NOME }))
      animalOptions.value = allAnimais.filter(v => v.label.toLowerCase().indexOf(needle) > -1)
    }
  })
}

// Lifecycle
onMounted(async () => {
  try {
    // Carregar dados básicos
    await animalStore.fetchAnimais()
    animalOptions.value = animalStore.animais.map(a => ({ value: a.ID, label: a.NOME }))
    
    // Carregar dashboard completo
    await ferrageamentoStore.carregarDashboard()
    
    $q.notify({
      type: 'positive',
      message: 'Dados carregados com sucesso',
      timeout: 2000
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao carregar dados: ' + error,
      timeout: 3000
    })
  }
})
</script>