<template>
  <div>
    <!-- Filtros -->
    <q-card
      flat
      bordered
      class="q-pa-md q-mb-md"
    >
      <div class="row q-gutter-md">
        <div class="col-md-3 col-12">
          <q-input
            v-model="filtros.nome"
            label="Filtrar por Nome"
            clearable
            @update:model-value="onFilterChange"
            :debounce="300"
          />
        </div>
        <div class="col-md-3 col-12">
          <q-select
            v-model="filtros.forma_farmaceutica"
            :options="medicamentoStore.formasFarmaceuticas"
            label="Forma Farmacêutica"
            clearable
            @update:model-value="onFilterChange"
          />
        </div>
        <div class="col-md-3 col-12">
          <q-toggle
            v-model="filtros.estoque_baixo"
            label="Apenas Estoque Baixo"
            @update:model-value="onFilterChange"
          />
        </div>
        <div class="col-md-3 col-12">
          <q-btn
            color="primary"
            label="Novo Medicamento"
            icon="add"
            @click="$emit('novo-medicamento')"
          />
        </div>
      </div>
    </q-card>

    <!-- Tabela de Medicamentos -->
    <q-table
      :rows="medicamentoStore.medicamentos"
      :columns="columns"
      row-key="ID"
      :loading="medicamentoStore.loading"
      :pagination="medicamentoStore.pagination"
      @request="onRequest"
      binary-state-sort
    >
      <template v-slot:body-cell-forma="props">
        <q-td :props="props">
          <q-chip
            :color="getFormaColor(props.row.FORMA_FARMACEUTICA)"
            text-color="white"
            dense
          >
            {{ props.row.FORMA_FARMACEUTICA }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-estoque="props">
        <q-td :props="props">
          <div class="text-right">
            <div :class="getEstoqueColorClass(props.row)">
              {{ props.row.ESTOQUE_ATUAL }} {{ props.row.UNIDADE_MEDIDA }}
            </div>
            <div class="text-caption">
              Mín: {{ props.row.ESTOQUE_MINIMO }} {{ props.row.UNIDADE_MEDIDA }}
            </div>
            <q-linear-progress
              :value="
                props.row.ESTOQUE_ATUAL / (props.row.ESTOQUE_MINIMO * 2 || 1)
              "
              :color="getEstoqueProgressColor(props.row)"
              size="xs"
              class="q-mt-xs"
            />
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <q-chip
            :color="getStatusColor(props.row.status_estoque)"
            text-color="white"
            dense
            :icon="getStatusIcon(props.row.status_estoque)"
          >
            {{ getStatusLabel(props.row.status_estoque) }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-valor="props">
        <q-td :props="props">
          <div class="text-right">
            R$ {{ (props.row.valor_estoque || 0).toFixed(2) }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-acoes="props">
        <q-td :props="props">
          <q-btn
            flat
            round
            color="primary"
            icon="visibility"
            @click="$emit('visualizar', props.row)"
            size="sm"
          >
            <q-tooltip>Visualizar</q-tooltip>
          </q-btn>
          <q-btn
            flat
            round
            color="secondary"
            icon="edit"
            @click="$emit('editar', props.row)"
            size="sm"
          >
            <q-tooltip>Editar</q-tooltip>
          </q-btn>
          <q-btn
            flat
            round
            color="negative"
            icon="delete"
            @click="$emit('excluir', props.row)"
            size="sm"
          >
            <q-tooltip>Excluir</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useMedicamentoStore } from 'stores/medicamento'

  // Emits
  defineEmits(['novo-medicamento', 'visualizar', 'editar', 'excluir'])

  // Store
  const medicamentoStore = useMedicamentoStore()

  // Estado reativo
  const filtros = ref({
    nome: '',
    forma_farmaceutica: null,
    estoque_baixo: false,
  })

  // Colunas da tabela
  const columns = [
    {
      name: 'NOME',
      label: 'Nome',
      field: 'NOME',
      sortable: true,
      align: 'left',
    },
    {
      name: 'PRINCIPIO_ATIVO',
      label: 'Princípio Ativo',
      field: 'PRINCIPIO_ATIVO',
      sortable: true,
      align: 'left',
    },
    {
      name: 'forma',
      label: 'Forma',
      field: 'FORMA_FARMACEUTICA',
      sortable: true,
      align: 'center',
    },
    {
      name: 'estoque',
      label: 'Estoque',
      field: 'ESTOQUE_ATUAL',
      sortable: true,
      align: 'left',
    },
    {
      name: 'status',
      label: 'Status',
      field: 'status_estoque',
      sortable: true,
      align: 'center',
    },
    {
      name: 'valor',
      label: 'Valor Estoque',
      field: 'valor_estoque',
      sortable: true,
      align: 'right',
    },
    { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' },
  ]

  // Métodos
  async function fetchMedicamentos() {
    try {
      await medicamentoStore.fetchMedicamentos()
    } catch (error) {
      console.error('Erro ao carregar medicamentos:', error)
    }
  }

  async function onFilterChange() {
    medicamentoStore.setFilters(filtros.value)
    await fetchMedicamentos()
  }

  function onRequest(props) {
    const { page, rowsPerPage, sortBy, descending } = props.pagination
    medicamentoStore.setPagination({ page, rowsPerPage, sortBy, descending })
    fetchMedicamentos()
  }

  // Funções auxiliares para cores e labels
  function getFormaColor(forma) {
    const colors = {
      INJETAVEL: 'primary',
      ORAL: 'secondary',
      TOPICO: 'accent',
    }
    return colors[forma] || 'grey'
  }

  function getStatusIcon(status) {
    const icons = {
      OK: 'check_circle',
      ESTOQUE_BAIXO: 'warning',
      VENCENDO: 'schedule',
      VENCIDO: 'error',
    }
    return icons[status] || 'help'
  }

  function getStatusColor(status) {
    const colors = {
      OK: 'positive',
      ESTOQUE_BAIXO: 'warning',
      VENCENDO: 'orange',
      VENCIDO: 'negative',
    }
    return colors[status] || 'grey'
  }

  function getStatusLabel(status) {
    const labels = {
      OK: 'OK',
      ESTOQUE_BAIXO: 'Estoque Baixo',
      VENCENDO: 'Vencendo',
      VENCIDO: 'Vencido',
    }
    return labels[status] || status
  }

  function getEstoqueColorClass(medicamento) {
    if (medicamento.ESTOQUE_ATUAL <= medicamento.ESTOQUE_MINIMO) {
      return 'text-negative'
    } else if (medicamento.ESTOQUE_ATUAL <= medicamento.ESTOQUE_MINIMO * 1.5) {
      return 'text-warning'
    }
    return 'text-positive'
  }

  function getEstoqueProgressColor(medicamento) {
    const ratio = medicamento.ESTOQUE_ATUAL / (medicamento.ESTOQUE_MINIMO || 1)
    if (ratio <= 1) return 'negative'
    if (ratio <= 1.5) return 'warning'
    return 'positive'
  }

  // Lifecycle
  onMounted(() => {
    fetchMedicamentos()
  })

  // Expor métodos
  defineExpose({
    fetchMedicamentos,
  })
</script>
