<template>
  <div>
    <!-- Filtros das Estatísticas -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="row q-gutter-md items-end">
          <q-select
            v-model="periodoEstatisticas"
            :options="[
              { value: 3, label: '3 meses' },
              { value: 6, label: '6 meses' },
              { value: 12, label: '12 meses' },
              { value: 24, label: '24 meses' }
            ]"
            label="Período"
            emit-value
            map-options
            @update:model-value="loadEstatisticas"
            class="col-2"
          />
          <q-btn 
            color="primary" 
            icon="refresh" 
            label="Atualizar" 
            @click="refreshAll"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- Resumo Geral -->
    <div class="row q-gutter-md q-mb-md justify-between">
      <q-card class="col-3">
        <q-card-section class="text-center">
          <div class="text-h4 text-primary">{{ crescimentoStore.totalMedicoes }}</div>
          <div class="text-subtitle2">Total de Medições</div>
        </q-card-section>
      </q-card>
      
      <q-card class="col-3">
        <q-card-section class="text-center">
          <div class="text-h4 text-secondary">{{ crescimentoStore.animaisComMedicoes }}</div>
          <div class="text-subtitle2">Animais Monitorados</div>
        </q-card-section>
      </q-card>
      
      <q-card class="col-3">
        <q-card-section class="text-center">
          <div class="text-h4 text-accent">{{ crescimentoStore.mediaGanhoPeso }}</div>
          <div class="text-subtitle2">Ganho Médio (kg)</div>
        </q-card-section>
      </q-card>
      
      <q-card class="col-2">
        <q-card-section class="text-center">
          <div class="text-h4 text-positive">{{ crescimentoStore.ultimasMedicoes.length }}</div>
          <div class="text-subtitle2">Medições Recentes</div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Estatísticas Gerais -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6 q-mb-md">Estatísticas Gerais</div>
        <q-table
          :rows="estatisticasGerais"
          :columns="estatisticasColumns"
          :loading="loading"
          row-key="animal_id"
          :pagination="{ rowsPerPage: 10 }"
          binary-state-sort
        >
          <template v-slot:body-cell-total_medicoes="props">
            <q-td :props="props">
              <q-chip color="primary" text-color="white" size="sm">
                {{ props.row.total_medicoes }}
              </q-chip>
            </q-td>
          </template>

          <template v-slot:body-cell-peso_inicial="props">
            <q-td :props="props">
              {{ props.row.peso_inicial ? `${props.row.peso_inicial} kg` : '-' }}
            </q-td>
          </template>

          <template v-slot:body-cell-peso_atual="props">
            <q-td :props="props">
              {{ props.row.peso_atual ? `${props.row.peso_atual} kg` : '-' }}
            </q-td>
          </template>

          <template v-slot:body-cell-ganho_total="props">
            <q-td :props="props">
              <q-chip 
                v-if="props.row.ganho_peso_total"
                :color="props.row.ganho_peso_total > 0 ? 'positive' : 'negative'"
                text-color="white"
                size="sm"
              >
                {{ props.row.ganho_peso_total > 0 ? '+' : '' }}{{ props.row.ganho_peso_total.toFixed(1) }} kg
              </q-chip>
              <span v-else>-</span>
            </q-td>
          </template>

          <template v-slot:body-cell-ganho_mes="props">
            <q-td :props="props">
              {{ props.row.ganho_peso_medio_mes ? `${props.row.ganho_peso_medio_mes.toFixed(1)} kg/mês` : '-' }}
            </q-td>
          </template>

          <template v-slot:body-cell-acoes_est="props">
            <q-td :props="props">
              <q-btn 
                flat 
                dense 
                icon="show_chart"
                @click="verGraficoAnimal(props.row)"
                color="primary"
              >
                <q-tooltip>Ver Gráfico</q-tooltip>
              </q-btn>
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>

    <!-- Comparação por Idade -->
    <q-card>
      <q-card-section>
        <div class="text-h6 q-mb-md">Comparação por Idade</div>
        <q-table
          :rows="comparacaoMedidas"
          :columns="comparacaoColumns"
          :loading="loading"
          row-key="animal_id"
          :pagination="{ rowsPerPage: 10 }"
          binary-state-sort
        >
          <template v-slot:body-cell-idade="props">
            <q-td :props="props">
              {{ props.row.idade_meses }} meses
            </q-td>
          </template>

          <template v-slot:body-cell-peso_comp="props">
            <q-td :props="props">
              {{ props.row.peso_atual ? `${props.row.peso_atual} kg` : '-' }}
            </q-td>
          </template>

          <template v-slot:body-cell-altura_comp="props">
            <q-td :props="props">
              {{ props.row.altura_atual ? `${props.row.altura_atual} cm` : '-' }}
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref,  onMounted } from 'vue'
import { useCrescimentoStore } from 'stores/crescimento'
import { ErrorHandler } from 'src/utils/errorHandler'

// Stores
const crescimentoStore = useCrescimentoStore()

// Estado reativo
const loading = ref(false)
const periodoEstatisticas = ref(12)

// Dados
const estatisticasGerais = ref([])
const comparacaoMedidas = ref([])

// Colunas das tabelas
const estatisticasColumns = [
  { name: 'animal_nome', label: 'Animal', field: 'animal_nome', align: 'left' },
  { name: 'total_medicoes', label: 'Medições', field: 'total_medicoes', align: 'center' },
  { name: 'peso_inicial', label: 'Peso Inicial', field: 'peso_inicial', align: 'right' },
  { name: 'peso_atual', label: 'Peso Atual', field: 'peso_atual', align: 'right' },
  { name: 'ganho_total', label: 'Ganho Total', field: 'ganho_peso_total', align: 'right' },
  { name: 'ganho_mes', label: 'Ganho/Mês', field: 'ganho_peso_medio_mes', align: 'right' },
  { name: 'acoes_est', label: 'Ações', field: 'acoes', align: 'center' }
]

const comparacaoColumns = [
  { name: 'animal_nome', label: 'Animal', field: 'animal_nome', align: 'left' },
  { name: 'idade', label: 'Idade', field: 'idade_meses', align: 'center' },
  { name: 'peso_comp', label: 'Peso Atual', field: 'peso_atual', align: 'right' },
  { name: 'altura_comp', label: 'Altura Atual', field: 'altura_atual', align: 'right' }
]

// Métodos
async function loadEstatisticas() {
  try {
    loading.value = true
    await Promise.all([
      crescimentoStore.fetchEstatisticasGerais(periodoEstatisticas.value),
      crescimentoStore.fetchComparacaoMedidas()
    ])
    
    estatisticasGerais.value = crescimentoStore.estatisticasGerais
    comparacaoMedidas.value = crescimentoStore.comparacaoMedidas
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao carregar estatísticas')
  } finally {
    loading.value = false
  }
}

async function refreshAll() {
  await loadEstatisticas()
}

function verGraficoAnimal(animal) {
  // Emitir evento para o componente pai navegar para gráficos
  // ou implementar navegação aqui
  console.log('Ver gráfico do animal:', animal.animal_nome)
}

// Lifecycle
onMounted(() => {
  refreshAll()
})

// Expor métodos
defineExpose({
  refreshAll
})
</script>