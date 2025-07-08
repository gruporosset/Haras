<template>
  <div>
    <!-- Filtros -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6">Filtros</div>
        <div class="row q-gutter-md">
          <q-select
            v-model="reproducaoStore.filters.egua_id"
            :options="femeaOptions"
            label="Égua"
            clearable
            use-input
            @filter="filterFemeas"
            @update:model-value="onFilterChange"
            class="col-2"
          />
          <q-select
            v-model="reproducaoStore.filters.parceiro_id"
            :options="machoOptions"
            label="Parceiro"
            clearable
            use-input
            @filter="filterMachos"
            @update:model-value="onFilterChange"
            class="col-2"
          />
          <q-select
            v-model="reproducaoStore.filters.tipo_cobertura"
            :options="reproducaoStore.tiposCobertura"
            label="Tipo"
            clearable
            @update:model-value="onFilterChange"
            class="col-2"
          />
          <q-select
            v-model="reproducaoStore.filters.resultado"
            :options="reproducaoStore.resultadosDiagnostico"
            label="Resultado"
            clearable
            @update:model-value="onFilterChange"
            class="col-2"
          />
          <CalendarioComponent
            v-model="reproducaoStore.filters.data_inicio"
            label="Data Início"
            @update:model-value="onFilterChange"
            class="col-2"
          />
          <CalendarioComponent
            v-model="reproducaoStore.filters.data_fim"
            label="Data Fim"
            @update:model-value="onFilterChange"
            class="col-2"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- Tabela -->
    <q-card>
      <q-card-section>
        <div class="row items-center justify-between q-mb-md">
          <div class="text-h6">Registros de Reprodução</div>
          <q-btn
            color="primary"
            label="Nova Reprodução"
            icon="add"
            @click="$emit('nova')"
          />
        </div>

        <q-table
          :rows="reproducaoStore.reproducoes"
          :columns="columns"
          row-key="ID"
          :pagination="reproducaoStore.pagination"
          :loading="reproducaoStore.loading"
          @request="onRequest"
          binary-state-sort
        >
          <template v-slot:body-cell-TIPO_COBERTURA="props">
            <q-td :props="props">
              <q-chip
                :label="getTipoLabel(props.value)"
                size="sm"
                color="primary"
                text-color="white"
              />
            </q-td>
          </template>

          <template v-slot:body-cell-resultado="props">
            <q-td :props="props">
              <q-chip
                :label="getResultadoLabel(props.value)"
                :color="getResultadoColor(props.value)"
                text-color="white"
                size="sm"
              />
            </q-td>
          </template>

          <template v-slot:body-cell-gestacao="props">
            <q-td :props="props">
              <div v-if="props.row.dias_gestacao">
                {{ props.row.dias_gestacao }} dias
              </div>
              <div v-else>-</div>
            </q-td>
          </template>

          <template v-slot:body-cell-status="props">
            <q-td :props="props">
              <q-chip
                :label="getStatusLabel(props.value)"
                :color="getStatusColor(props.value)"
                text-color="white"
                size="sm"
              />
            </q-td>
          </template>

          <template v-slot:body-cell-acoes="props">
            <q-td :props="props">
              <q-btn
                flat
                round
                color="info"
                icon="visibility"
                size="sm"
                @click="$emit('visualizar', props.row)"
              >
                <q-tooltip>Visualizar</q-tooltip>
              </q-btn>
              <q-btn
                flat
                round
                color="primary"
                icon="history"
                size="sm"
                @click="$emit('historico', props.row.ID_EGUA)"
              >
                <q-tooltip>Histórico da Égua</q-tooltip>
              </q-btn>
              <q-btn
                flat
                round
                color="primary"
                icon="edit"
                size="sm"
                @click="$emit('editar', props.row)"
              >
                <q-tooltip>Editar</q-tooltip>
              </q-btn>
              <q-btn
                flat
                round
                color="negative"
                icon="delete"
                size="sm"
                @click="$emit('excluir', props.row)"
              >
                <q-tooltip>Excluir</q-tooltip>
              </q-btn>
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useReproducaoStore } from 'stores/reproducao'
  import { useAnimalStore } from 'stores/animal'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'
  import { formatDate } from 'src/utils/dateUtils'
  import { ErrorHandler } from 'src/utils/errorHandler'
  // Emits
  defineEmits(['visualizar', 'editar', 'excluir', 'historico', 'nova'])

  // Stores
  const reproducaoStore = useReproducaoStore()
  const animalStore = useAnimalStore()

  // Opções
  const femeaOptions = ref([])
  const machoOptions = ref([])

  // Colunas da tabela
  const columns = [
    {
      name: 'egua_nome',
      label: 'Égua',
      field: 'egua_nome',
      sortable: true,
      align: 'left',
    },
    {
      name: 'parceiro_nome',
      label: 'Parceiro',
      field: 'parceiro_nome',
      sortable: true,
      align: 'left',
    },
    {
      name: 'DATA_COBERTURA',
      label: 'Cobertura',
      field: 'DATA_COBERTURA',
      sortable: true,
      align: 'left',
      format: val => formatDate(val),
    },
    {
      name: 'TIPO_COBERTURA',
      label: 'Tipo',
      field: 'TIPO_COBERTURA',
      sortable: true,
      align: 'center',
    },
    {
      name: 'resultado',
      label: 'Resultado',
      field: 'RESULTADO_DIAGNOSTICO',
      sortable: true,
      align: 'center',
    },
    {
      name: 'gestacao',
      label: 'Gestação',
      field: 'dias_gestacao',
      sortable: false,
      align: 'center',
    },
    {
      name: 'status',
      label: 'Status',
      field: 'STATUS_REPRODUCAO',
      sortable: true,
      align: 'center',
    },
    { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' },
  ]

  // Funções de filtro
  function filterFemeas(val, update) {
    update(() => {
      if (val === '') {
        femeaOptions.value = animalStore.parentOptions.femeas
      } else {
        const needle = val.toLowerCase()
        femeaOptions.value = animalStore.parentOptions.femeas.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  function filterMachos(val, update) {
    update(() => {
      if (val === '') {
        machoOptions.value = animalStore.parentOptions.machos
      } else {
        const needle = val.toLowerCase()
        machoOptions.value = animalStore.parentOptions.machos.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  // Funções de formatação
  function getTipoLabel(tipo) {
    const tipos = {
      NATURAL: 'Natural',
      IA: 'Inseminação Artificial',
      TE: 'Transferência de Embrião',
    }
    return tipos[tipo] || tipo
  }

  function getResultadoLabel(resultado) {
    const resultados = {
      POSITIVO: 'Positivo',
      NEGATIVO: 'Negativo',
      PENDENTE: 'Pendente',
    }
    return resultados[resultado] || resultado
  }

  function getStatusLabel(status) {
    const statusMap = {
      ATIVO: 'Ativo',
      CONCLUIDO: 'Concluído',
      FALHADO: 'Falhado',
    }
    return statusMap[status] || status
  }

  function getResultadoColor(resultado) {
    const colors = {
      POSITIVO: 'positive',
      NEGATIVO: 'negative',
      PENDENTE: 'warning',
    }
    return colors[resultado] || 'grey'
  }

  function getStatusColor(status) {
    const colors = {
      ATIVO: 'primary',
      CONCLUIDO: 'positive',
      FALHADO: 'negative',
    }
    return colors[status] || 'grey'
  }

  // Handlers
  async function onFilterChange() {
    await reproducaoStore.fetchReproducoes()
  }

  async function onRequest(props) {
    const { page, rowsPerPage, sortBy, descending } = props.pagination
    reproducaoStore.setPagination({ page, rowsPerPage, sortBy, descending })
    await reproducaoStore.fetchReproducoes(props)
  }

  // Funções públicas (expostas para o componente pai)
  async function loadData() {
    await loadOptions()
    await reproducaoStore.fetchReproducoes()
  }

  async function loadOptions() {
    try {
      await animalStore.loadParentOptions()
      femeaOptions.value = animalStore.parentOptions.femeas
      machoOptions.value = animalStore.parentOptions.machos
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar opções')
    }
  }

  // Expor funções para o componente pai
  defineExpose({
    loadData,
  })

  // Inicialização
  onMounted(async () => {
    await loadData()
  })
</script>
