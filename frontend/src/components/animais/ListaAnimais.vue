<template>
  <div>
    <!-- Filtros -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="row q-gutter-md items-end">
          <q-input
            v-model="animalStore.filters.nome"
            label="Pesquisar por nome"
            clearable
            class="col-12 col-md-3"
            @update:model-value="onFilterChange"
            :debounce="300"
          >
            <template v-slot:prepend>
              <q-icon name="search" />
            </template>
          </q-input>

          <q-select
            v-model="animalStore.filters.sexo"
            :options="sexoOptions"
            label="Sexo"
            clearable
            emit-value
            map-options
            @update:model-value="onFilterChange"
            class="col-12 col-md-2"
          />

          <q-select
            v-model="animalStore.filters.status"
            :options="statusOptions"
            label="Status"
            clearable
            emit-value
            map-options
            @update:model-value="onFilterChange"
            class="col-12 col-md-2"
          />

          <q-input
            v-model="animalStore.filters.numero_registro"
            label="Número de Registro"
            clearable
            class="col-12 col-md-3"
            @update:model-value="onFilterChange"
            :debounce="300"
          />

          <q-btn
            color="primary"
            icon="add"
            label="Novo Animal"
            @click="$emit('novo-animal')"
            class="col-12 col-md-1"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- Tabela de Animais -->
    <q-card>
      <q-card-section>
        <q-table
          :rows="animalStore.animais"
          :columns="columns"
          :loading="animalStore.loading"
          :pagination="animalStore.pagination"
          @request="onRequest"
          row-key="ID"
          binary-state-sort
          :rows-per-page-options="[10, 25, 50, 100]"
        >
          <template v-slot:body-cell-foto="props">
            <q-td :props="props">
              <q-avatar
                size="40px"
                @click="$emit('ver-foto', props.row)"
              >
                <img
                  v-if="props.row.FOTO_PRINCIPAL"
                  :src="`http://localhost:8000${props.row.FOTO_PRINCIPAL}`"
                  class="cursor-pointer"
                />
                <q-icon
                  v-else
                  name="pets"
                  size="24px"
                  color="grey-5"
                  class="cursor-pointer"
                />
              </q-avatar>
            </q-td>
          </template>

          <template v-slot:body-cell-NOME="props">
            <q-td :props="props">
              <div class="text-weight-medium">{{ props.row.NOME }}</div>
              <div class="text-caption text-grey-6">
                {{ props.row.NUMERO_REGISTRO || 'S/N' }}
              </div>
            </q-td>
          </template>

          <template v-slot:body-cell-SEXO="props">
            <q-td :props="props">
              <q-chip
                :color="props.row.SEXO === 'M' ? 'blue' : 'pink'"
                text-color="white"
                size="sm"
              >
                {{ props.row.SEXO === 'M' ? 'Macho' : 'Fêmea' }}
              </q-chip>
            </q-td>
          </template>

          <template v-slot:body-cell-DATA_NASCIMENTO="props">
            <q-td :props="props">
              {{ formatDate(props.row.DATA_NASCIMENTO) }}
            </q-td>
          </template>

          <template v-slot:body-cell-STATUS_ANIMAL="props">
            <q-td :props="props">
              <q-chip
                :color="getStatusColor(props.row.STATUS_ANIMAL)"
                text-color="white"
                size="sm"
              >
                {{ props.row.STATUS_ANIMAL }}
              </q-chip>
            </q-td>
          </template>

          <template v-slot:body-cell-genealogia="props">
            <q-td :props="props">
              <q-btn
                flat
                dense
                icon="account_tree"
                @click="$emit('ver-genealogia', props.row)"
                :disable="!props.row.ID_PAI && !props.row.ID_MAE"
              >
                <q-tooltip>Ver Genealogia</q-tooltip>
              </q-btn>
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
                  icon="photo_camera"
                  @click="$emit('upload-foto', props.row)"
                  color="green"
                >
                  <q-tooltip>Adicionar Foto</q-tooltip>
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
              <q-icon
                size="2em"
                name="pets"
              />
              <span>Nenhum animal encontrado</span>
            </div>
          </template>
        </q-table>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
  import { useAnimalStore } from 'stores/animal'
  import { formatDate } from 'src/utils/dateUtils'

  // Emits
  defineEmits([
    'novo-animal',
    'visualizar',
    'editar',
    'excluir',
    'upload-foto',
    'ver-foto',
    'ver-genealogia',
  ])

  // Store
  const animalStore = useAnimalStore()

  // Opções para filtros
  const sexoOptions = [
    { label: 'Macho', value: 'M' },
    { label: 'Fêmea', value: 'F' },
  ]

  const statusOptions = [
    { label: 'Ativo', value: 'ATIVO' },
    { label: 'Vendido', value: 'VENDIDO' },
    { label: 'Morto', value: 'MORTO' },
    { label: 'Emprestado', value: 'EMPRESTADO' },
    { label: 'Aposentado', value: 'APOSENTADO' },
  ]

  // Colunas da tabela
  const columns = [
    { name: 'foto', label: 'Foto', field: 'foto', align: 'center' },
    {
      name: 'NOME',
      label: 'Nome',
      field: 'NOME',
      sortable: true,
      align: 'left',
    },
    {
      name: 'NUMERO_REGISTRO',
      label: 'Registro',
      field: 'NUMERO_REGISTRO',
      sortable: true,
      align: 'left',
    },
    {
      name: 'SEXO',
      label: 'Sexo',
      field: 'SEXO',
      sortable: true,
      align: 'center',
    },
    {
      name: 'DATA_NASCIMENTO',
      label: 'Nascimento',
      field: 'DATA_NASCIMENTO',
      sortable: true,
      align: 'left',
    },
    {
      name: 'STATUS_ANIMAL',
      label: 'Status',
      field: 'STATUS_ANIMAL',
      sortable: true,
      align: 'center',
    },
    {
      name: 'PROPRIETARIO',
      label: 'Proprietário',
      field: 'PROPRIETARIO',
      sortable: true,
      align: 'left',
    },
    {
      name: 'genealogia',
      label: 'Genealogia',
      field: 'genealogia',
      align: 'center',
    },
    { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' },
  ]

  // Métodos
  function onFilterChange() {
    fetchAnimais()
  }

  async function fetchAnimais() {
    try {
      await animalStore.fetchAnimais()
    } catch (error) {
      console.error('Erro ao carregar animais:', error)
    }
  }

  function onRequest(props) {
    const { page, rowsPerPage, sortBy, descending } = props.pagination
    animalStore.setPagination({ page, rowsPerPage, sortBy, descending })
    fetchAnimais()
  }

  function getStatusColor(status) {
    const colors = {
      ATIVO: 'green',
      VENDIDO: 'blue',
      MORTO: 'red',
      EMPRESTADO: 'orange',
      APOSENTADO: 'grey',
    }
    return colors[status] || 'grey'
  }

  // Expor métodos
  defineExpose({
    fetchAnimais,
  })
</script>

<style scoped>
  .cursor-pointer {
    cursor: pointer;
  }
</style>
