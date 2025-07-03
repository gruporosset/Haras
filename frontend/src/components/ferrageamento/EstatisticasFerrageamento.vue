<template>
  <div class="row q-gutter-md">
    <div class="col-md-6 col-12">
      <q-card>
        <q-card-section>
          <div class="text-h6">Estatísticas por Animal</div>
        </q-card-section>
        <q-card-section>
          <q-list bordered separator>
            <q-item v-for="stat in ferrageamentoStore.estatisticasAnimais" :key="stat.animal_id">
              <q-item-section>
                <q-item-label>{{ stat.animal_nome }}</q-item-label>
                <q-item-label caption>
                  {{ stat.total_registros }} registros - 
                  Último: {{ formatDate(stat.ultimo_registro) }}
                </q-item-label>
                <q-item-label caption>
                  Custo total: R$ {{ stat.custo_total?.toFixed(2) || '0,00' }}
                </q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-chip 
                  :color="getStatusColor(stat.status_atual)"
                  text-color="white"
                  size="sm"
                >
                  {{ stat.status_atual }}
                </q-chip>
              </q-item-section>
            </q-item>
            <q-item v-if="ferrageamentoStore.estatisticasAnimais.length === 0">
              <q-item-section>
                <q-item-label class="text-center text-grey-6">
                  Nenhuma estatística disponível
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>
    </div>

    <div class="col-md-6 col-12">
      <q-card>
        <q-card-section>
          <div class="text-h6">Top Ferradores</div>
        </q-card-section>
        <q-card-section>
          <q-list bordered separator>
            <q-item v-for="ferrador in ferrageamentoStore.ferradoresMaisAtivos" :key="ferrador.nome">
              <q-item-section>
                <q-item-label>{{ ferrador.nome }}</q-item-label>
                <q-item-label caption>
                  {{ ferrador.total_servicos }} serviços
                </q-item-label>
                <q-item-label caption>
                  Faturamento: R$ {{ ferrador.faturamento_total?.toFixed(2) || '0,00' }}
                </q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-avatar color="primary" text-color="white">
                  {{ ferrador.total_servicos }}
                </q-avatar>
              </q-item-section>
            </q-item>
            <q-item v-if="ferrageamentoStore.ferradoresMaisAtivos.length === 0">
              <q-item-section>
                <q-item-label class="text-center text-grey-6">
                  Nenhum ferrador cadastrado
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>
    </div>

    <!-- Controles de Período -->
    <div class="col-12">
      <q-card>
        <q-card-section>
          <div class="text-h6">Filtros de Período</div>
          <div class="row q-gutter-md q-mt-md">
            <q-select
              v-model="periodoSelecionado"
              :options="opcoesPerido"
              label="Período"
              emit-value
              map-options
              @update:model-value="atualizarEstatisticas"
              class="col-3"
            />
            <q-btn 
              color="primary" 
              icon="refresh" 
              label="Atualizar" 
              @click="atualizarEstatisticas"
            />
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Gráfico de Custos -->
    <div class="col-12">
      <q-card>
        <q-card-section>
          <div class="text-h6">Evolução de Custos</div>
          <div v-if="dadosGrafico.length > 0" class="q-mt-md">
            <!-- Aqui seria implementado um gráfico de linha -->
            <div class="text-center q-pa-md">
              <q-icon name="show_chart" size="4rem" color="grey" />
              <div class="text-body2 text-grey">
                Gráfico de evolução mensal de custos
              </div>
            </div>
          </div>
          <div v-else class="text-center q-pa-xl">
            <q-icon name="show_chart" size="4rem" color="grey" />
            <div class="text-h6 text-grey q-mt-md">
              Sem dados para o período selecionado
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFerrageamentoStore } from 'stores/ferrageamento'
import { formatDate } from 'src/utils/dateUtils'

// Store
const ferrageamentoStore = useFerrageamentoStore()

// Estado reativo
const periodoSelecionado = ref(6)
const dadosGrafico = ref([])

// Opções
const opcoesPerido = [
  { value: 3, label: '3 meses' },
  { value: 6, label: '6 meses' },
  { value: 12, label: '12 meses' },
  { value: 24, label: '24 meses' }
]

// Métodos
async function atualizarEstatisticas() {
  try {
    await ferrageamentoStore.fetchEstatisticasAnimais(periodoSelecionado.value)
    // Remove chamadas para métodos que não existem
    await carregarDadosGrafico()
  } catch (error) {
    console.error('Erro ao atualizar estatísticas:', error)
  }
}

async function carregarDadosGrafico() {
  try {
    // Simular dados até implementar no store
    dadosGrafico.value = []
  } catch {
    dadosGrafico.value = []
  }
}

function getStatusColor(status) {
  const colors = {
    'EM_DIA': 'positive',
    'PROXIMO_VENCIMENTO': 'warning', 
    'VENCIDO': 'negative',
    'BOM': 'positive',
    'REGULAR': 'warning',
    'RUIM': 'negative'
  }
  return colors[status] || 'grey'
}

// Lifecycle
onMounted(() => {
  atualizarEstatisticas()
})
</script>