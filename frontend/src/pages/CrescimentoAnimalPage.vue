<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="row items-center justify-between">
          <div>
            <div class="text-h6">Histórico de Crescimento</div>
            <div v-if="animalInfo" class="text-subtitle1 text-grey">
              {{ animalInfo.NOME }} - {{ animalInfo.RACA || 'Sem raça definida' }}
            </div>
          </div>
          <q-btn
            flat
            icon="arrow_back"
            label="Voltar"
            @click="$router.go(-1)"
          />
        </div>
      </q-card-section>
      
      <q-card-section>
        <!-- Estatísticas do Animal -->
        <div v-if="historicoDetalhado.length > 0" class="row q-gutter-md q-mb-md">
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h5 text-primary">{{ historicoDetalhado.length }}</div>
              <div class="text-caption">Total Medições</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h5 text-secondary">{{ pesoAtual }} kg</div>
              <div class="text-caption">Peso Atual</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h5" :class="ganhoTotal >= 0 ? 'text-positive' : 'text-negative'">
                {{ ganhoTotal >= 0 ? '+' : '' }}{{ ganhoTotal }} kg
              </div>
              <div class="text-caption">Ganho Total</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h5 text-accent">{{ diasMonitoramento }}</div>
              <div class="text-caption">Dias Monitoramento</div>
            </q-card-section>
          </q-card>
        </div>
        
        <!-- Abas -->
        <q-tabs v-model="activeTab" class="q-mb-md">
          <q-tab name="timeline" label="Timeline" />
          <q-tab name="graficos" label="Gráficos" />
          <q-tab name="tabela" label="Tabela Detalhada" />
        </q-tabs>
        
        <q-tab-panels v-model="activeTab" animated>
          <!-- ABA TIMELINE -->
          <q-tab-panel name="timeline">
            <q-timeline v-if="historicoDetalhado.length > 0" color="primary">
              <q-timeline-entry
                v-for="(item, index) in historicoDetalhado"
                :key="item.medicao.ID"
                :title="formatarData(item.medicao.DATA_MEDICAO)"
                :subtitle="getSubtitleTimeline(item)"
                :icon="getIconTimeline(item)"
                :color="getColorTimeline(item)"
              >
                <div class="timeline-content">
                  <div class="row q-gutter-md">
                    <div v-if="item.medicao.PESO" class="col-auto">
                      <q-chip color="primary" text-color="white" size="sm">
                        Peso: {{ item.medicao.PESO }} kg
                      </q-chip>
                    </div>
                    <div v-if="item.medicao.ALTURA" class="col-auto">
                      <q-chip color="secondary" text-color="white" size="sm">
                        Altura: {{ item.medicao.ALTURA }} cm
                      </q-chip>
                    </div>
                    <div v-if="item.variacao_peso" class="col-auto">
                      <q-chip 
                        :color="item.variacao_peso > 0 ? 'positive' : 'negative'" 
                        text-color="white" 
                        size="sm"
                      >
                        {{ item.variacao_peso > 0 ? '+' : '' }}{{ item.variacao_peso.toFixed(1) }} kg
                      </q-chip>
                    </div>
                  </div>
                  
                  <div v-if="item.medicao.OBSERVACOES" class="q-mt-sm text-caption">
                    <strong>Obs:</strong> {{ item.medicao.OBSERVACOES }}
                  </div>
                  
                  <div v-if="index === 0" class="q-mt-sm text-caption text-positive">
                    <q-icon name="flag" size="xs" /> Primeira medição
                  </div>
                  
                  <div v-if="index === historicoDetalhado.length - 1" class="q-mt-sm text-caption text-accent">
                    <q-icon name="schedule" size="xs" /> Medição mais recente
                  </div>
                </div>
              </q-timeline-entry>
            </q-timeline>
            
            <div v-else class="text-center q-pa-xl">
              <q-icon name="timeline" size="4rem" color="grey" />
              <div class="text-h6 text-grey q-mt-md">
                Nenhuma medição encontrada
              </div>
            </div>
          </q-tab-panel>
          
          <!-- ABA GRÁFICOS -->
          <q-tab-panel name="graficos">
            <div class="row q-gutter-md">
              <q-card class="col-12">
                <q-card-section>
                  <div class="text-h6">Evolução do Peso</div>
                  <crescimento-chart 
                    :dados="dadosGraficoPeso"
                    tipo="peso"
                    height="350px"
                    :show-stats="true"
                    :show-trend="true"
                  />
                </q-card-section>
              </q-card>
              
              <q-card v-if="temDadosAltura" class="col-12">
                <q-card-section>
                  <div class="text-h6">Evolução da Altura</div>
                  <crescimento-chart 
                    :dados="dadosGraficoAltura"
                    tipo="altura"
                    height="350px"
                    :show-stats="true"
                    :show-trend="true"
                  />
                </q-card-section>
              </q-card>
            </div>
          </q-tab-panel>
          
          <!-- ABA TABELA -->
          <q-tab-panel name="tabela">
            <q-table
              :rows="historicoDetalhado"
              :columns="colunas"
              row-key="medicao.ID"
              flat
              :pagination="{ rowsPerPage: 0 }"
            >
              <template v-slot:body-cell-data="props">
                <q-td :props="props">
                  {{ formatarData(props.row.medicao.DATA_MEDICAO) }}
                </q-td>
              </template>
              
              <template v-slot:body-cell-peso="props">
                <q-td :props="props">
                  <div v-if="props.row.medicao.PESO">
                    {{ props.row.medicao.PESO }} kg
                    <q-chip 
                      v-if="props.row.variacao_peso"
                      :color="props.row.variacao_peso > 0 ? 'positive' : 'negative'"
                      text-color="white"
                      size="sm"
                      class="q-ml-sm"
                    >
                      {{ props.row.variacao_peso > 0 ? '+' : '' }}{{ props.row.variacao_peso.toFixed(1) }}
                    </q-chip>
                  </div>
                  <span v-else class="text-grey">-</span>
                </q-td>
              </template>
              
              <template v-slot:body-cell-altura="props">
                <q-td :props="props">
                  <div v-if="props.row.medicao.ALTURA">
                    {{ props.row.medicao.ALTURA }} cm
                    <q-chip 
                      v-if="props.row.variacao_altura"
                      :color="props.row.variacao_altura > 0 ? 'positive' : 'negative'"
                      text-color="white"
                      size="sm"
                      class="q-ml-sm"
                    >
                      {{ props.row.variacao_altura > 0 ? '+' : '' }}{{ props.row.variacao_altura.toFixed(1) }}
                    </q-chip>
                  </div>
                  <span v-else class="text-grey">-</span>
                </q-td>
              </template>
              
              <template v-slot:body-cell-taxa="props">
                <q-td :props="props">
                  <span v-if="props.row.taxa_crescimento_dia">
                    {{ props.row.taxa_crescimento_dia.toFixed(3) }} kg/dia
                  </span>
                  <span v-else class="text-grey">-</span>
                </q-td>
              </template>
              
              <template v-slot:body-cell-intervalo="props">
                <q-td :props="props">
                  <span v-if="props.row.dias_crescimento">
                    {{ props.row.dias_crescimento }} dias
                  </span>
                  <span v-else class="text-grey">Primeira</span>
                </q-td>
              </template>
            </q-table>
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useQuasar } from 'quasar'
import { useCrescimentoStore } from '../stores/crescimento'
import { useAnimalStore } from '../stores/animal'
import CrescimentoChart from '../components/CrescimentoChart.vue'

const route = useRoute()
const $q = useQuasar()
const crescimentoStore = useCrescimentoStore()
const animalStore = useAnimalStore()

// Estado
const activeTab = ref('timeline')
const animalInfo = ref(null)
const historicoDetalhado = ref([])

// Props da rota
const animalId = computed(() => parseInt(route.params.id))

// Computed
const pesoAtual = computed(() => {
  if (historicoDetalhado.value.length === 0) return 0
  const ultimaMedicao = historicoDetalhado.value[historicoDetalhado.value.length - 1]
  return ultimaMedicao.medicao.PESO || 0
})

const ganhoTotal = computed(() => {
  if (historicoDetalhado.value.length < 2) return 0
  const primeira = historicoDetalhado.value[0]
  const ultima = historicoDetalhado.value[historicoDetalhado.value.length - 1]
  
  if (!primeira.medicao.PESO || !ultima.medicao.PESO) return 0
  
  return parseFloat((ultima.medicao.PESO - primeira.medicao.PESO).toFixed(1))
})

const diasMonitoramento = computed(() => {
  if (historicoDetalhado.value.length < 2) return 0
  
  const primeira = new Date(historicoDetalhado.value[0].medicao.DATA_MEDICAO)
  const ultima = new Date(historicoDetalhado.value[historicoDetalhado.value.length - 1].medicao.DATA_MEDICAO)
  
  return Math.ceil((ultima - primeira) / (1000 * 60 * 60 * 24))
})

const dadosGraficoPeso = computed(() => {
  return historicoDetalhado.value
    .filter(h => h.medicao.PESO)
    .map(h => ({
      data: h.medicao.DATA_MEDICAO,
      peso: h.medicao.PESO,
      ganho: h.variacao_peso || 0
    }))
})

const dadosGraficoAltura = computed(() => {
  return historicoDetalhado.value
    .filter(h => h.medicao.ALTURA)
    .map(h => ({
      data: h.medicao.DATA_MEDICAO,
      altura: h.medicao.ALTURA,
      variacao: h.variacao_altura || 0
    }))
})

const temDadosAltura = computed(() => {
  return dadosGraficoAltura.value.length > 0
})

// Colunas da tabela
const colunas = [
  { name: 'data', label: 'Data', field: 'data', align: 'left' },
  { name: 'peso', label: 'Peso', field: 'peso', align: 'left' },
  { name: 'altura', label: 'Altura', field: 'altura', align: 'left' },
  { name: 'taxa', label: 'Taxa Crescimento', field: 'taxa', align: 'right' },
  { name: 'intervalo', label: 'Intervalo', field: 'intervalo', align: 'center' }
]

// Funções
function formatarData(data) {
  return new Date(data).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

function getSubtitleTimeline(item) {
  const partes = []
  
  if (item.medicao.PESO) {
    partes.push(`${item.medicao.PESO} kg`)
  }
  
  if (item.variacao_peso) {
    const variacao = item.variacao_peso > 0 ? `+${item.variacao_peso.toFixed(1)}` : item.variacao_peso.toFixed(1)
    partes.push(`(${variacao} kg)`)
  }
  
  if (item.dias_crescimento) {
    partes.push(`${item.dias_crescimento} dias`)
  }
  
  return partes.join(' • ')
}

function getIconTimeline(item) {
  if (item.variacao_peso > 0) return 'trending_up'
  if (item.variacao_peso < 0) return 'trending_down'
  return 'straighten'
}

function getColorTimeline(item) {
  if (item.variacao_peso > 0) return 'positive'
  if (item.variacao_peso < 0) return 'negative'
  return 'primary'
}

async function loadData() {
  try {
    // Carregar informações do animal
    await animalStore.fetchAnimais()
    animalInfo.value = animalStore.animais.find(a => a.ID === animalId.value)
    
    // Carregar histórico detalhado
    historicoDetalhado.value = await crescimentoStore.fetchHistoricoAnimal(animalId.value)
    
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao carregar dados do animal'
    })
    console.error(error)
  }
}

// Inicialização
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.timeline-content {
  padding: 8px 0;
}

.q-chip {
  margin: 2px;
}
</style>