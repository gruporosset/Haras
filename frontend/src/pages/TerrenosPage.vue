<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Gestão de Terrenos</div>
      </q-card-section>
      <q-card-section>
        <div class="row q-mb-md">
          <q-input
            v-model="filters.nome"
            label="Filtrar por Nome"
            class="q-mr-md"
            clearable
            @input="fetchTerrenos"
            :debounce="300"
            aria-label="Filtrar terrenos por nome"
          />
          <q-select
            v-model="filters.status"
            :options="statusOptions"
            label="Filtrar por Status"
            clearable
            class="col-3"
            @input="fetchTerrenos"
            aria-label="Filtrar terrenos por status"
          />
          <q-btn
            color="primary"
            label="Novo Terreno"
            icon="add"
            class="q-ml-auto"
            @click="openDialog(null)"
            aria-label="Cadastrar novo terreno"
          />
        </div>
        <q-table
          :rows="terrenos"
          :columns="columns"
          row-key="ID"
          :loading="loading"
          :pagination="pagination"
          @request="onRequest"
          binary-state-sort
          aria-label="Tabela de terrenos"
        >
          <template v-slot:body-cell-acoes="props">
            <q-td :props="props">
              <q-btn
                flat
                round
                color="primary"
                icon="edit"
                @click="openDialog(props.row)"
                aria-label="Editar terreno"
              />
              <q-btn
                flat
                round
                color="negative"
                icon="delete"
                @click="confirmDelete(props.row)"
                aria-label="Excluir terreno"
              />
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>

    <!-- Diálogo para Cadastro/Edição -->
    <q-dialog v-model="dialog" persistent>
      <q-card style="width: 600px">
        <q-form @submit="saveTerreno">
          <q-card-section>
            <div class="text-h6">{{ form.ID ? 'Editar' : 'Cadastrar' }} Terreno</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <q-input
              v-model="form.NOME"
              label="Nome *"
              :rules="[val => !!val || 'Nome é obrigatório']"
              class="q-mb-sm"
              aria-label="Nome do terreno"
            />
            <q-input
              v-model.number="form.AREA_HECTARES"
              label="Área (hectares) *"
              type="number"
              step="0.0001"
              :rules="[val => val > 0 || 'Área deve ser maior que 0']"
              class="q-mb-sm"
              aria-label="Área do terreno em hectares"
            />
            <q-input
              v-model="form.TIPO_SOLO"
              label="Tipo de Solo"
              class="q-mb-sm"
              aria-label="Tipo de solo"
            />
            <q-input
              v-model="form.TOPOGRAFIA"
              label="Topografia"
              class="q-mb-sm"
              aria-label="Topografia"
            />
            <q-input
              v-model="form.TIPO_PASTAGEM"
              label="Tipo de Pastagem"
              class="q-mb-sm"
              aria-label="Tipo de pastagem"
            />
            <q-input
              v-model.number="form.CAPACIDADE_ANIMAIS"
              label="Capacidade de Animais"
              type="number"
              :rules="[val => val >= 0 || 'Capacidade inválida']"
              class="q-mb-sm"
              aria-label="Capacidade de animais"
            />
            <q-input
              v-model.number="form.LATITUDE"
              label="Latitude *"
              type="number"
              step="0.000001"
              :rules="[val => val >= -90 && val <= 90 || 'Latitude inválida']"
              class="q-mb-sm"
              aria-label="Latitude do terreno"
            />
            <q-input
              v-model.number="form.LONGITUDE"
              label="Longitude *"
              type="number"
              step="0.000001"
              :rules="[val => val >= -180 && val <= 180 || 'Longitude inválida']"
              class="q-mb-sm"
              aria-label="Longitude do terreno"
            />
            <q-select
              v-model="form.STATUS_TERRENO"
              :options="statusOptions"
              label="Status"
              class="q-mb-sm"
              aria-label="Status do terreno"
            />
            <q-input
              v-model="form.OBSERVACOES"
              label="Observações"
              type="textarea"
              class="q-mb-sm"
              aria-label="Observações do terreno"
            />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn
              flat
              label="Cancelar"
              color="gray"
              @click="dialog = false"
              aria-label="Cancelar"
            />
            <q-btn
              type="submit"
              color="primary"
              label="Salvar"
              :disable="loading"
              aria-label="Salvar terreno"
            />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- Diálogo para Confirmação de Exclusão -->
    <q-dialog v-model="deleteDialog" persistent>
      <q-card>
        <q-card-section>
          <div class="text-h6">Confirmar Exclusão</div>
        </q-card-section>
        <q-card-section>
          Deseja excluir o terreno "{{ terrenoToDelete?.NOME }}"?
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancelar"
            color="gray"
            @click="deleteDialog = false"
            aria-label="Cancelar exclusão"
          />
          <q-btn
            color="negative"
            label="Excluir"
            @click="deleteTerreno"
            :disable="loading"
            aria-label="Confirmar exclusão"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '../stores/auth'
import api from '../boot/api';

const $q = useQuasar()
const authStore = useAuthStore()

// Estado da tabela
const terrenos = ref([])
const loading = ref(false)
const pagination = reactive({
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 10,
  sortBy: 'ID',
  descending: false
})
const filters = reactive({
  nome: '',
  status: null
})
const columns = [
  { name: 'ID', label: 'ID', field: 'ID', sortable: true, align: 'left' },
  { name: 'NOME', label: 'Nome', field: 'NOME', sortable: true, align: 'left' },
  { name: 'AREA_HECTARES', label: 'Área (ha)', field: 'AREA_HECTARES', sortable: true, align: 'left' },
  { name: 'STATUS_TERRENO', label: 'Status', field: 'STATUS_TERRENO', sortable: true, align: 'left' },
  { name: 'LATITUDE', label: 'Latitude', field: 'LATITUDE', sortable: true, align: 'left' },
  { name: 'LONGITUDE', label: 'Longitude', field: 'LONGITUDE', sortable: true, align: 'left' },
  { name: 'acoes', label: '', field: 'acoes', align: 'center' }
]
const statusOptions = ['DISPONIVEL', 'OCUPADO', 'MANUTENÇÃO']

// Estado do diálogo de cadastro/edição
const dialog = ref(false)
const form = ref({
  ID: null,
  NOME: '',
  AREA_HECTARES: null,
  TIPO_SOLO: '',
  TOPOGRAFIA: '',
  TIPO_PASTAGEM: '',
  CAPACIDADE_ANIMAIS: 0,
  LATITUDE: null,
  LONGITUDE: null,
  STATUS_TERRENO: 'DISPONIVEL',
  OBSERVACOES: '',
  ID_USUARIO_CADASTRO: authStore.user.ID
})

// Estado do diálogo de exclusão
const deleteDialog = ref(false)
const terrenoToDelete = ref(null)

async function fetchTerrenos(props = {}) {
  loading.value = true
  try {
    const { page, rowsPerPage, sortBy, descending } = props.pagination || pagination
    const params = {
      page,
      limit: rowsPerPage,
      sort_by: sortBy,
      order: descending ? 'desc' : 'asc',
      nome: filters.nome,
      status: filters.status
    }
    const response = await api.get('/api/terrenos', { params })
    terrenos.value = response.data
    pagination.rowsNumber = response.data.length // Ajustar para total do backend
    pagination.page = page
    pagination.rowsPerPage = rowsPerPage
    pagination.sortBy = sortBy
    pagination.descending = descending
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao carregar terrenos: ' + (error.response?.data?.detail || 'Tente novamente')
    })
  } finally {
    loading.value = false
  }
}

function onRequest(props) {
  fetchTerrenos(props)
}

function openDialog(terreno) {
  if (terreno) {
    form.value = { ...terreno, ID_USUARIO_CADASTRO: authStore.user.ID }
  } else {
    form.value = {
      ID: null,
      NOME: '',
      AREA_HECTARES: null,
      TIPO_SOLO: '',
      TOPOGRAFIA: '',
      TIPO_PASTAGEM: '',
      CAPACIDADE_ANIMAIS: 0,
      LATITUDE: null,
      LONGITUDE: null,
      STATUS_TERRENO: 'DISPONIVEL',
      OBSERVACOES: '',
      ID_USUARIO_CADASTRO: authStore.user.ID
    }
  }
  dialog.value = true
}

async function saveTerreno() {
  loading.value = true
  try {
    if (form.value.ID) {
      await api.put(`/terrenos/${form.value.ID}`, form.value)
      $q.notify({ type: 'positive', message: 'Terreno atualizado com sucesso' })
    } else {
      await api.post('/terrenos', form.value)
      $q.notify({ type: 'positive', message: 'Terreno cadastrado com sucesso' })
    }
    dialog.value = false
    await fetchTerrenos()
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao salvar terreno: ' + (error.response?.data?.detail || 'Tente novamente')
    })
  } finally {
    loading.value = false
  }
}

function confirmDelete(terreno) {
  terrenoToDelete.value = terreno
  deleteDialog.value = true
}

async function deleteTerreno() {
  loading.value = true
  try {
    await api.delete(`/terrenos/${terrenoToDelete.value.ID}`)
    $q.notify({ type: 'positive', message: 'Terreno excluído com sucesso' })
    deleteDialog.value = false
    await fetchTerrenos()
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao excluir terreno: ' + (error.response?.data?.detail || 'Tente novamente')
    })
  } finally {
    loading.value = false
  }
}

// Carregar terrenos na inicialização
fetchTerrenos()
</script>