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
          <q-select
            v-model="filtroTipo"
            :options="ferrageamentoStore.tiposFerrageamento"
            label="Tipo"
            clearable
            emit-value
            map-options
            @update:model-value="onFilterChange"
            class="col-2"
          />
          <q-input
            v-model="filtroFerrador"
            label="Ferrador"
            clearable
            @update:model-value="onFilterChange"
            :debounce="300"
            class="col-3"
          />
          <q-toggle
            v-model="filtroVencidos"
            label="Apenas vencidos"
            @update:model-value="onFilterChange"
            class="col-2"
          />
          <q-btn
            color="primary"
            icon="add"
            label="Novo Registro"
            @click="$emit('novo-registro')"
            class="col-2"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- Tabela -->
    <q-card>
      <q-card-section>
        <q-table
          :rows="ferrageamentoStore.ferrageamentos"
          :columns="columns"
          :loading="ferrageamentoStore.loading"
          :pagination="ferrageamentoStore.pagination"
          @request="onRequest"
          row-key="ID"
          binary-state-sort
          :rows-per-page-options="[10, 25, 50]"
        >
          <template v-slot:body-cell-DATA_OCORRENCIA="props">
            <q-td :props="props">
              {{ formatDate(props.row.DATA_OCORRENCIA) }}
            </q-td>
          </template>

          <template v-slot:body-cell-animal_nome="props">
            <q-td :props="props">
              <div class="text-weight-medium">{{ props.row.animal_nome }}</div>
            </q-td>
          </template>

          <template v-slot:body-cell-TIPO_REGISTRO="props">
            <q-td :props="props">
              <q-chip 
                :color="getTipoColor(props.row.TIPO_REGISTRO)"
                text-color="white"
                size="sm"
              >
                {{ ferrageamentoStore.getTipoLabel(props.row.TIPO_REGISTRO) }}
              </q-chip>
            </q-td>
          </template>

          <template v-slot:body-cell-STATUS_CASCO="props">
            <q-td :props="props">
              <q-chip
                v-if="props.row.STATUS_CASCO"
                :color="getStatusCascoColor(props.row.STATUS_CASCO)"
                text-color="white"
                size="sm"
              >
                {{ props.row.STATUS_CASCO }}
              </q-chip>
              <span v-else class="text-grey">-</span>
            </q-td>
          </template>

          <template v-slot:body-cell-PROXIMA_AVALIACAO="props">
            <q-td :props="props">
              <div v-if="props.row.PROXIMA_AVALIACAO">
                {{ formatDate(props.row.PROXIMA_AVALIACAO) }}
                <div class="text-caption" :class="getClasseDiasVencimento(props.row.dias_proxima_avaliacao)">
                  {{ getTextoDiasVencimento(props.row.dias_proxima_avaliacao) }}
                </div>
              </div>
              <span v-else class="text-grey">-</span>
            </q-td>
          </template>

          <template v-slot:body-cell-status_vencimento="props">
            <q-td :props="props">
              <q-chip
                :color="getStatusVencimentoColor(props.row.status_vencimento)"
                text-color="white"
                size="sm"
              >
                {{ getStatusVencimentoLabel(props.row.status_vencimento) }}
              </q-chip>
            </q-td>
          </template>

          <template v-slot:body-cell-CUSTO="props">
            <q-td :props="props">
              {{ props.row.CUSTO ? `R$ ${props.row.CUSTO.toFixed(2)}` : '-' }}
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
              <q-icon size="2em" name="build" />
              <span>Nenhum registro encontrado</span>
            </div>
          </template>
        </q-table>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFerrageamentoStore } from 'stores/ferrageamento'
import { useAnimalStore } from 'stores/animal'
import { formatDate } from 'src/utils/dateUtils'

// Emits
defineEmits([
  'novo-registro',
  'visualizar',
  'editar',
  'excluir'
])

// Stores
const ferrageamentoStore = useFerrageamentoStore()
const animalStore = useAnimalStore()

// Estado reativo
const filtroAnimal = ref(null)
const filtroTipo = ref(null)
const filtroFerrador = ref('')
const filtroVencidos = ref(false)
const animalOptions = ref([])
const animalOptionsOri = ref([])

// Colunas da tabela
const columns = [
  { name: 'DATA_OCORRENCIA', label: 'Data', field: 'DATA_OCORRENCIA', sortable: true, align: 'left' },
  { name: 'animal_nome', label: 'Animal', field: 'animal_nome', sortable: true, align: 'left' },
  { name: 'TIPO_REGISTRO', label: 'Tipo', field: 'TIPO_REGISTRO', sortable: true, align: 'center' },
  { name: 'FERRADOR_RESPONSAVEL', label: 'Ferrador', field: 'FERRADOR_RESPONSAVEL', align: 'left' },
  { name: 'STATUS_CASCO', label: 'Status Casco', field: 'STATUS_CASCO', align: 'center' },
  { name: 'PROXIMA_AVALIACAO', label: 'Próxima Avaliação', field: 'PROXIMA_AVALIACAO', sortable: true, align: 'left' },
  { name: 'status_vencimento', label: 'Status', field: 'status_vencimento', align: 'center' },
  { name: 'CUSTO', label: 'Custo', field: 'CUSTO', sortable: true, align: 'right' },
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
    tipo_registro: filtroTipo.value,
    ferrador: filtroFerrador.value,
    apenas_vencidos: filtroVencidos.value
  }
  ferrageamentoStore.setFilters(filtros)
  fetchFerrageamentos()
}

async function fetchFerrageamentos() {
  try {
    await ferrageamentoStore.fetchFerrageamentos()
  } catch (error) {
    console.error('Erro ao carregar ferrageamentos:', error)
  }
}

function onRequest(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  ferrageamentoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  fetchFerrageamentos()
}

function getTipoColor(tipo) {
  const colors = {
    'FERRAGEAMENTO': 'primary',
    'CASQUEAMENTO': 'secondary',
    'TRATAMENTO_CASCO': 'warning',
    'AVALIACAO': 'info'
  }
  return colors[tipo] || 'grey'
}

function getStatusCascoColor(status) {
  const colors = {
    'BOM': 'positive',
    'REGULAR': 'warning',
    'RUIM': 'negative',
    'CRITICO': 'red'
  }
  return colors[status] || 'grey'
}

function getStatusVencimentoColor(status) {
  const colors = {
    'EM_DIA': 'positive',
    'PROXIMO_VENCIMENTO': 'warning',
    'VENCIDO': 'negative'
  }
  return colors[status] || 'grey'
}

function getStatusVencimentoLabel(status) {
  const labels = {
    'EM_DIA': 'Em dia',
    'PROXIMO_VENCIMENTO': 'Próximo vencimento',
    'VENCIDO': 'Vencido'
  }
  return labels[status] || status
}

function getClasseDiasVencimento(dias) {
  if (dias < 0) return 'text-negative'
  if (dias <= 7) return 'text-warning'
  return 'text-positive'
}

function getTextoDiasVencimento(dias) {
  if (dias < 0) return `${Math.abs(dias)} dias em atraso`
  if (dias === 0) return 'Vence hoje'
  return `${dias} dias restantes`
}

// Lifecycle
onMounted(() => {
  loadAnimais()
  fetchFerrageamentos()
})

// Expor métodos
defineExpose({
  fetchFerrageamentos
})
</script>