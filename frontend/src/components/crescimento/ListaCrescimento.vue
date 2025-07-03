<template>
  <div>
    <!-- Filtros -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="row q-gutter-md items-end">
          <q-select
            v-model="filtroAnimal"
            :options="animalOptions"
            label="Filtrar por Animal"
            clearable
            use-input
            @filter="filterAnimais"
            @update:model-value="onFilterChange"
            class="col-3"
          />
          <q-btn
            color="primary"
            icon="add"
            label="Nova Medição"
            @click="$emit('nova-medicao')"
            class="col-2"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- Tabela de Medições -->
    <q-card>
      <q-card-section>
        <q-table
          :rows="crescimentoStore.crescimentos"
          :columns="columns"
          :loading="crescimentoStore.loading"
          :pagination="crescimentoStore.pagination"
          @request="onRequest"
          row-key="ID"
          binary-state-sort
          :rows-per-page-options="[10, 25, 50]"
        >
          <template v-slot:body-cell-DATA_MEDICAO="props">
            <q-td :props="props">
              {{ formatDate(props.row.DATA_MEDICAO) }}
            </q-td>
          </template>

          <template v-slot:body-cell-animal="props">
            <q-td :props="props">
              <div class="text-weight-medium">{{ props.row.animal_nome }}</div>
            </q-td>
          </template>

          <template v-slot:body-cell-peso="props">
            <q-td :props="props">
              <div v-if="props.row.PESO" class="row items-center">
                <span class="text-weight-medium">{{ props.row.PESO }} kg</span>
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
              <div v-if="props.row.ALTURA" class="row items-center">
                <span class="text-weight-medium">{{ props.row.ALTURA }} cm</span>
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

          <template v-slot:body-cell-medidas="props">
            <q-td :props="props">
              <div class="text-caption">
                <div v-if="props.row.CIRCUNFERENCIA_TORACICA">
                  Tórax: {{ props.row.CIRCUNFERENCIA_TORACICA }}cm
                </div>
                <div v-if="props.row.COMPRIMENTO_CORPO">
                  Corpo: {{ props.row.COMPRIMENTO_CORPO }}cm
                </div>
                <div v-if="props.row.CIRCUNFERENCIA_CANELA">
                  Canela: {{ props.row.CIRCUNFERENCIA_CANELA }}cm
                </div>
              </div>
            </q-td>
          </template>

          <template v-slot:body-cell-dias="props">
            <q-td :props="props">
              <q-chip 
                v-if="props.row.dias_desde_ultima"
                :color="getDiasColor(props.row.dias_desde_ultima)"
                text-color="white"
                size="sm"
              >
                {{ props.row.dias_desde_ultima }}d
              </q-chip>
              <span v-else class="text-grey">Primeira</span>
            </q-td>
          </template>

          <template v-slot:body-cell-acoes="props">
            <q-td :props="props">
              <q-btn-group flat>
                <q-btn 
                  flat 
                  dense 
                  icon="visibility"
                  @click="$emit('visualizar', props.row)"
                  color="primary"
                >
                  <q-tooltip>Visualizar</q-tooltip>
                </q-btn>

                <q-btn 
                  flat 
                  dense 
                  icon="edit"
                  @click="$emit('editar', props.row)"
                  color="orange"
                >
                  <q-tooltip>Editar</q-tooltip>
                </q-btn>

                <q-btn 
                  flat 
                  dense 
                  icon="show_chart"
                  @click="$emit('ver-grafico', props.row)"
                  color="green"
                >
                  <q-tooltip>Ver Gráfico</q-tooltip>
                </q-btn>

                <q-btn 
                  flat 
                  dense 
                  icon="delete"
                  @click="$emit('excluir', props.row)"
                  color="negative"
                >
                  <q-tooltip>Excluir</q-tooltip>
                </q-btn>
              </q-btn-group>
            </q-td>
          </template>

          <template v-slot:no-data>
            <div class="full-width row flex-center text-grey q-gutter-sm">
              <q-icon size="2em" name="straighten" />
              <span>Nenhuma medição encontrada</span>
            </div>
          </template>
        </q-table>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCrescimentoStore } from 'stores/crescimento'
import { useAnimalStore } from 'stores/animal'
import { formatDate } from 'src/utils/dateUtils'

// Emits
defineEmits([
  'nova-medicao',
  'visualizar',
  'editar',
  'excluir',
  'ver-grafico'
])

// Stores
const crescimentoStore = useCrescimentoStore()
const animalStore = useAnimalStore()

// Estado reativo
const filtroAnimal = ref(null)
const animalOptions = ref([])
const animalOptionsOri = ref([])

// Colunas da tabela
const columns = [
  { name: 'DATA_MEDICAO', label: 'Data', field: 'DATA_MEDICAO', sortable: true, align: 'left' },
  { name: 'animal', label: 'Animal', field: 'animal_nome', sortable: true, align: 'left' },
  { name: 'peso', label: 'Peso', field: 'PESO', sortable: true, align: 'left' },
  { name: 'altura', label: 'Altura', field: 'ALTURA', sortable: true, align: 'left' },
  { name: 'medidas', label: 'Outras Medidas', field: 'medidas', align: 'left' },
  { name: 'dias', label: 'Intervalo', field: 'dias_desde_ultima', sortable: true, align: 'center' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

// Métodos
async function loadAnimais() {
  try {
    await animalStore.fetchAnimais({ limit: 100 })
    animalOptionsOri.value = animalStore.animais.map(a => ({
      value: a.ID,
      label: a.NOME
    }))
    animalOptions.value = [...animalOptionsOri.value]
  } catch (error) {
    console.error('Erro ao carregar animais:', error)
  }
}

function filterAnimais(val, update) {
  update(() => {
    if (val === '') {
      animalOptions.value = animalOptionsOri.value
    } else {
      const needle = val.toLowerCase()
      animalOptions.value = animalOptionsOri.value.filter(
        v => v.label.toLowerCase().indexOf(needle) > -1
      )
    }
  })
}

function onFilterChange() {
  const filtros = {
    animal_id: filtroAnimal.value?.value,
  }
  crescimentoStore.setFilters(filtros)
  fetchCrescimentos()
}

async function fetchCrescimentos() {
  try {
    await crescimentoStore.fetchCrescimentos()
  } catch (error) {
    console.error('Erro ao carregar crescimentos:', error)
  }
}

function onRequest(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  crescimentoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  fetchCrescimentos()
}

function getDiasColor(dias) {
  if (dias <= 7) return 'green'
  if (dias <= 14) return 'orange'
  if (dias <= 30) return 'amber'
  return 'red'
}

// Lifecycle
onMounted(() => {
  loadAnimais()
  fetchCrescimentos()
})

// Expor métodos
defineExpose({
  fetchCrescimentos
})
</script>