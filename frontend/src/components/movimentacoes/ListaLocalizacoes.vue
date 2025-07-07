<template>
  <div>
    <!-- Filtros -->
    <q-card
      flat
      bordered
      class="q-mb-md"
    >
      <q-card-section>
        <div class="row q-gutter-md">
          <div class="col-12 col-md-4">
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

          <div class="col-12 col-md-4">
            <q-select
              v-model="filtros.terreno"
              :options="terrenoOptions"
              label="Localização Atual"
              clearable
              @update:model-value="onFilterChange"
            />
          </div>

          <div class="col-12 col-md-4">
            <q-btn
              color="primary"
              label="Nova Movimentação"
              icon="add"
              @click="$emit('nova-movimentacao')"
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
        :rows="movimentacaoStore.localizacoes"
        :columns="columns"
        row-key="ID_ANIMAL"
        :loading="movimentacaoStore.loading"
        :pagination="movimentacaoStore.paginationLocalizacoes"
        @request="onRequest"
        binary-state-sort
        :rows-per-page-options="[10, 25, 50]"
      >
        <template v-slot:body-cell-localizacao="props">
          <q-td :props="props">
            <div class="row items-center">
              <q-icon
                :name="getLocalizacaoIcon(props.row.localizacao_tipo)"
                :color="getLocalizacaoColor(props.row.localizacao_tipo)"
                class="q-mr-sm"
              />
              {{ props.row.localizacao }}
            </div>
          </q-td>
        </template>

        <template v-slot:body-cell-tipo_ultima_movimentacao="props">
          <q-td :props="props">
            <q-chip
              :color="getTipoColor(props.row.tipo_ultima_movimentacao)"
              text-color="white"
              dense
              size="sm"
            >
              {{ props.row.tipo_ultima_movimentacao }}
            </q-chip>
          </q-td>
        </template>

        <template v-slot:body-cell-acoes="props">
          <q-td :props="props">
            <q-btn-group flat>
              <q-btn
                flat
                dense
                icon="add"
                color="primary"
                @click="$emit('nova-movimentacao', props.row)"
              >
                <q-tooltip>Nova Movimentação</q-tooltip>
              </q-btn>

              <q-btn
                flat
                dense
                icon="history"
                color="blue"
                @click="$emit('ver-historico', props.row.ID_ANIMAL)"
              >
                <q-tooltip>Ver Histórico</q-tooltip>
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
  import { useTerrenoStore } from 'stores/terreno'

  // Emits
  defineEmits(['nova-movimentacao', 'ver-historico'])

  // Stores
  const movimentacaoStore = useMovimentacaoStore()
  const animalStore = useAnimalStore()
  const terrenoStore = useTerrenoStore()

  // Estado reativo
  const animalOptions = ref([])
  const terrenoOptions = ref([])
  const filtros = ref({
    animal: null,
    terreno: null,
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
      name: 'localizacao',
      label: 'Localização Atual',
      field: 'localizacao',
      sortable: false,
      align: 'left',
    },
    {
      name: 'data_ultima_movimentacao',
      label: 'Última Movimentação',
      field: 'data_ultima_movimentacao',
      sortable: true,
      align: 'left',
    },
    {
      name: 'tipo_ultima_movimentacao',
      label: 'Tipo',
      field: 'tipo_ultima_movimentacao',
      sortable: true,
      align: 'center',
    },
    { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' },
  ]

  // Métodos
  async function loadOptions() {
    try {
      // Carregar animais
      await animalStore.loadParentOptions()
      animalOptions.value = [
        ...animalStore.parentOptions.machos,
        ...animalStore.parentOptions.femeas,
      ]

      // Carregar terrenos
      await terrenoStore.fetchTerrenos({ limit: 100 })
      terrenoOptions.value = terrenoStore.terrenos.map(t => ({
        value: t.ID,
        label: t.NOME,
      }))
    } catch (error) {
      console.error('Erro ao carregar opções:', error)
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

    if (filtros.value.terreno?.value) {
      filters.terreno_id = filtros.value.terreno.value
    }

    movimentacaoStore.setFiltersLocalizacoes(filters)
    await fetchLocalizacoes()
  }

  async function onRequest(props) {
    const { page, rowsPerPage, sortBy, descending } = props.pagination
    movimentacaoStore.setPaginationLocalizacoes({
      page,
      rowsPerPage,
      sortBy,
      descending,
    })
    await fetchLocalizacoes()
  }

  async function fetchLocalizacoes() {
    try {
      await movimentacaoStore.fetchLocalizacoes()
    } catch (error) {
      console.error('Erro ao carregar localizações:', error)
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

  function getLocalizacaoIcon(tipo) {
    // Assumindo que tipo pode ser 'terreno' ou 'externo'
    if (tipo === 'terreno') {
      return 'grass'
    }
    return 'location_on'
  }

  function getLocalizacaoColor(tipo) {
    if (tipo === 'terreno') {
      return 'positive'
    }
    return 'warning'
  }

  // Exposição de métodos para o componente pai
  defineExpose({
    fetchLocalizacoes,
  })

  // Lifecycle
  onMounted(async () => {
    await loadOptions()
    await fetchLocalizacoes()
  })
</script>
