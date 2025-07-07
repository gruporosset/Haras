<template>
  <div>
    <!-- Botão de Nova Movimentação -->
    <div class="row q-gutter-md q-mb-md">
      <div class="col-12">
        <q-btn
          color="primary"
          label="Nova Movimentação"
          icon="add"
          @click="$emit('nova-movimentacao')"
        />
      </div>
    </div>

    <!-- Filtros -->
    <q-card
      flat
      bordered
      class="q-mb-md"
    >
      <q-card-section>
        <div class="row q-gutter-md">
          <div class="col-12 col-md-3">
            <q-select
              v-model="filtros.animal"
              :options="animalOptions"
              label="Animal"
              clearable
              use-input
              hide-selected
              fill-input
              input-debounce="300"
              @filter="filterAnimais"
              @update:model-value="onFilterChange"
            >
              <template v-slot:no-option>
                <q-item>
                  <q-item-section class="text-grey">
                    Nenhum animal encontrado
                  </q-item-section>
                </q-item>
              </template>
            </q-select>
          </div>

          <div class="col-12 col-md-3">
            <q-select
              v-model="filtros.tipo"
              :options="movimentacaoStore.tiposMovimentacao"
              label="Tipo de Movimentação"
              clearable
              @update:model-value="onFilterChange"
            />
          </div>

          <div class="col-12 col-md-3">
            <CalendarioComponent
              v-model="filtros.dataInicio"
              label="Data Início"
              clearable
              @update:model-value="onFilterChange"
            />
          </div>

          <div class="col-12 col-md-3">
            <CalendarioComponent
              v-model="filtros.dataFim"
              label="Data Fim"
              clearable
              @update:model-value="onFilterChange"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Tabela -->
    <q-card
      flat
      bordered
    >
      <q-table
        :rows="movimentacaoStore.movimentacoes"
        :columns="columns"
        row-key="ID"
        :loading="movimentacaoStore.loading"
        :pagination="movimentacaoStore.pagination"
        @request="onRequest"
        binary-state-sort
        :rows-per-page-options="[10, 25, 50]"
      >
        <template v-slot:body-cell-tipo="props">
          <q-td :props="props">
            <q-chip
              :color="getTipoColor(props.row.TIPO_MOVIMENTACAO)"
              text-color="white"
              dense
              :icon="getIconByTipo(props.row.TIPO_MOVIMENTACAO)"
            >
              {{ props.row.TIPO_MOVIMENTACAO }}
            </q-chip>
          </q-td>
        </template>

        <template v-slot:body-cell-origem="props">
          <q-td :props="props">
            {{
              props.row.terreno_origem_nome || props.row.ORIGEM_EXTERNA || '-'
            }}
          </q-td>
        </template>

        <template v-slot:body-cell-destino="props">
          <q-td :props="props">
            {{
              props.row.terreno_destino_nome || props.row.DESTINO_EXTERNO || '-'
            }}
          </q-td>
        </template>

        <template v-slot:body-cell-acoes="props">
          <q-td :props="props">
            <q-btn-group flat>
              <q-btn
                flat
                dense
                icon="visibility"
                color="primary"
                @click="$emit('visualizar', props.row)"
              >
                <q-tooltip>Visualizar</q-tooltip>
              </q-btn>

              <q-btn
                flat
                dense
                icon="edit"
                color="orange"
                @click="$emit('editar', props.row)"
              >
                <q-tooltip>Editar</q-tooltip>
              </q-btn>

              <q-btn
                flat
                dense
                icon="history"
                color="blue"
                @click="$emit('ver-historico', props.row.ID_ANIMAL)"
              >
                <q-tooltip>Histórico do Animal</q-tooltip>
              </q-btn>

              <q-btn
                flat
                dense
                icon="delete"
                color="negative"
                @click="$emit('excluir', props.row)"
              >
                <q-tooltip>Excluir</q-tooltip>
              </q-btn>
            </q-btn-group>
          </q-td>
        </template>
      </q-table>
    </q-card>
  </div>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useMovimentacaoStore } from 'stores/movimentacao'
  import { useAnimalStore } from 'stores/animal'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

  // Emits
  defineEmits([
    'nova-movimentacao',
    'visualizar',
    'editar',
    'excluir',
    'ver-historico',
  ])

  // Stores
  const movimentacaoStore = useMovimentacaoStore()
  const animalStore = useAnimalStore()

  // Estado reativo
  const animalOptions = ref([])
  const filtros = ref({
    animal: null,
    tipo: null,
    dataInicio: null,
    dataFim: null,
  })

  // Colunas da tabela
  const columns = [
    {
      name: 'animal_nome',
      label: 'Animal',
      field: 'animal_nome',
      sortable: true,
      align: 'left',
    },
    {
      name: 'DATA_MOVIMENTACAO',
      label: 'Data',
      field: 'DATA_MOVIMENTACAO',
      sortable: true,
      align: 'left',
    },
    {
      name: 'tipo',
      label: 'Tipo',
      field: 'TIPO_MOVIMENTACAO',
      sortable: true,
      align: 'center',
    },
    {
      name: 'origem',
      label: 'Origem',
      field: 'origem',
      sortable: false,
      align: 'left',
    },
    {
      name: 'destino',
      label: 'Destino',
      field: 'destino',
      sortable: false,
      align: 'left',
    },
    { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' },
  ]

  // Métodos
  async function loadAnimais() {
    try {
      await animalStore.loadParentOptions()
      animalOptions.value = [
        ...animalStore.parentOptions.machos,
        ...animalStore.parentOptions.femeas,
      ]
    } catch (error) {
      console.error('Erro ao carregar animais:', error)
    }
  }

  function filterAnimais(val, update) {
    update(() => {
      if (val === '') {
        animalOptions.value = [
          ...animalStore.parentOptions.machos,
          ...animalStore.parentOptions.femeas,
        ]
      } else {
        const needle = val.toLowerCase()
        const allAnimals = [
          ...animalStore.parentOptions.machos,
          ...animalStore.parentOptions.femeas,
        ]
        animalOptions.value = allAnimals.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  async function onFilterChange() {
    // Aplicar filtros
    const filters = {}

    if (filtros.value.animal?.value) {
      filters.animal_id = filtros.value.animal.value
    }

    if (filtros.value.tipo?.value) {
      filters.tipo = filtros.value.tipo.value
    }

    if (filtros.value.dataInicio) {
      filters.data_inicio = filtros.value.dataInicio
    }

    if (filtros.value.dataFim) {
      filters.data_fim = filtros.value.dataFim
    }

    movimentacaoStore.setFilters(filters)
    await fetchMovimentacoes()
  }

  async function onRequest(props) {
    const { page, rowsPerPage, sortBy, descending } = props.pagination
    movimentacaoStore.setPagination({ page, rowsPerPage, sortBy, descending })
    await fetchMovimentacoes()
  }

  async function fetchMovimentacoes() {
    try {
      await movimentacaoStore.fetchMovimentacoes()
    } catch (error) {
      console.error('Erro ao carregar movimentações:', error)
    }
  }

  function getTipoColor(tipo) {
    const colors = {
      TRANSFERENCIA: 'primary',
      ENTRADA: 'positive',
      SAIDA: 'warning',
      VENDA: 'info',
      EMPRESTIMO: 'secondary',
      RETORNO: 'accent',
    }
    return colors[tipo] || 'grey'
  }

  function getIconByTipo(tipo) {
    const icons = {
      TRANSFERENCIA: 'swap_horiz',
      ENTRADA: 'input',
      SAIDA: 'output',
      VENDA: 'attach_money',
      EMPRESTIMO: 'handshake',
      RETORNO: 'keyboard_return',
    }
    return icons[tipo] || 'move_to_inbox'
  }

  // Exposição de métodos para o componente pai
  defineExpose({
    fetchMovimentacoes,
  })

  // Lifecycle
  onMounted(async () => {
    await loadAnimais()
    await fetchMovimentacoes()
  })
</script>
