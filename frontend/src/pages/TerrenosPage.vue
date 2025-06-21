<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Gestão de Terrenos</div>
      </q-card-section>
      <q-card-section>
        <div class="row q-mb-md">
          <q-input
            v-model="terrenoStore.filters.nome"
            label="Filtrar por Nome"
            class="q-mr-md"
            clearable
            @update:model-value="fetchTerrenos"
            :debounce="300"
            aria-label="Filtrar terrenos por nome"
          />
          <q-select
            v-model="terrenoStore.filters.status"
            :options="statusOptions"
            label="Filtrar por Status"
            clearable
            class="col-3"
            @update:model-value="fetchTerrenos"
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
        
        <q-tabs v-model="activeTab" class="q-mb-md">
          <q-tab name="table" label="Tabela" aria-label="Exibir tabela de terrenos" />
          <q-tab name="map" label="Mapa" aria-label="Exibir mapa de terrenos" />
        </q-tabs>
        
        <q-tab-panels v-model="activeTab" animated>
          <q-tab-panel name="table">
            <q-table
              :rows="terrenoStore.terrenos"
              :columns="columns"
              row-key="ID"
              :loading="terrenoStore.loading"
              :pagination="terrenoStore.pagination"
              @request="onRequest"
              binary-state-sort
              aria-label="Tabela de terrenos"
            >
              <template v-slot:body-cell-acoes="props">
                <q-td :props="props">
                  <q-btn
                    flat
                    round
                    color="info"
                    icon="visibility"
                    @click="viewTerreno(props.row)"
                    aria-label="Visualizar terreno"
                  />
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
          </q-tab-panel>
          <q-tab-panel name="map">
            <terreno-map :terrenos="terrenoStore.terrenos" />
          </q-tab-panel>   
        </q-tab-panels>   
      </q-card-section>
    </q-card>

    <!-- Diálogo de Visualização -->
    <q-dialog v-model="viewDialog" persistent>
      <q-card style="width: 600px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6 flex items-center">
            <q-icon name="landscape" size="50px" color="primary" class="q-mr-md" />
            {{ viewTerrenoData?.NOME }}
          </div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <q-list>
            <q-item>
              <q-item-section>
                <q-item-label caption>ID</q-item-label>
                <q-item-label>{{ viewTerrenoData?.ID }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Área (hectares)</q-item-label>
                <q-item-label>{{ viewTerrenoData?.AREA_HECTARES }} ha</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Tipo de Solo</q-item-label>
                <q-item-label>{{ viewTerrenoData?.TIPO_SOLO || 'Não informado' }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Topografia</q-item-label>
                <q-item-label>{{ viewTerrenoData?.TOPOGRAFIA || 'Não informado' }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Tipo de Pastagem</q-item-label>
                <q-item-label>{{ viewTerrenoData?.TIPO_PASTAGEM || 'Não informado' }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Capacidade de Animais</q-item-label>
                <q-item-label>{{ viewTerrenoData?.CAPACIDADE_ANIMAIS || 'Não informado' }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Coordenadas</q-item-label>
                <q-item-label>Lat: {{ viewTerrenoData?.LATITUDE }}, Lng: {{ viewTerrenoData?.LONGITUDE }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Status</q-item-label>
                <q-item-label>
                  <q-chip 
                    :color="getStatusColor(viewTerrenoData?.STATUS_TERRENO)" 
                    text-color="white" 
                    dense
                  >
                    {{ viewTerrenoData?.STATUS_TERRENO }}
                  </q-chip>
                </q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Data de Cadastro</q-item-label>
                <q-item-label>{{ formatDateTime(viewTerrenoData?.DATA_CADASTRO) }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item v-if="viewTerrenoData?.OBSERVACOES">
              <q-item-section>
                <q-item-label caption>Observações</q-item-label>
                <q-item-label>{{ viewTerrenoData.OBSERVACOES }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            label="Editar"
            color="primary"
            @click="editFromView"
          />
          <q-btn
            flat
            label="Fechar"
            color="gray"
            @click="viewDialog = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

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
              :disable="terrenoStore.loading"
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
            :disable="terrenoStore.loading"
            aria-label="Confirmar exclusão"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '../stores/auth'
import { useTerrenoStore } from '../stores/terreno'
import TerrenoMap from '../components/TerrenoMap.vue'
import { formatDateTime } from '../utils/dateUtils'

const $q = useQuasar()
const authStore = useAuthStore()
const terrenoStore = useTerrenoStore()

const columns = [
  { name: 'ID', label: 'ID', field: 'ID', sortable: true, align: 'left' },
  { name: 'NOME', label: 'Nome', field: 'NOME', sortable: true, align: 'left' },
  { name: 'AREA_HECTARES', label: 'Área (ha)', field: 'AREA_HECTARES', sortable: true, align: 'left' },
  { name: 'STATUS_TERRENO', label: 'Status', field: 'STATUS_TERRENO', sortable: true, align: 'left' },
  { name: 'LATITUDE', label: 'Latitude', field: 'LATITUDE', sortable: true, align: 'left' },
  { name: 'LONGITUDE', label: 'Longitude', field: 'LONGITUDE', sortable: true, align: 'left' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

const statusOptions = ['DISPONIVEL', 'OCUPADO', 'MANUTENÇÃO']

// Estado das abas
const activeTab = ref('table')

// Estado dos diálogos
const dialog = ref(false)
const viewDialog = ref(false)
const deleteDialog = ref(false)

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

const viewTerrenoData = ref(null)
const terrenoToDelete = ref(null)

// Funções
async function fetchTerrenos(props = {}) {
  try {
    await terrenoStore.fetchTerrenos(props)
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error
    })
  }
}

function onRequest(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  terrenoStore.setPagination({ page, rowsPerPage, sortBy, descending })
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

function viewTerreno(terreno) {
  viewTerrenoData.value = terreno
  viewDialog.value = true
}

function editFromView() {
  viewDialog.value = false
  openDialog(viewTerrenoData.value)
}

async function saveTerreno() {
  try {
    if (form.value.ID) {
      await terrenoStore.updateTerreno(form.value.ID, form.value)
      $q.notify({ type: 'positive', message: 'Terreno atualizado com sucesso' })
    } else {
      await terrenoStore.createTerreno(form.value)
      $q.notify({ type: 'positive', message: 'Terreno cadastrado com sucesso' })
    }
    dialog.value = false
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error
    })
  }
}

function confirmDelete(terreno) {
  terrenoToDelete.value = terreno
  deleteDialog.value = true
}

async function deleteTerreno() {
  try {
    await terrenoStore.deleteTerreno(terrenoToDelete.value.ID)
    $q.notify({ type: 'positive', message: 'Terreno excluído com sucesso' })
    deleteDialog.value = false
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error
    })
  }
}

function getStatusColor(status) {
  const colors = {
    'DISPONIVEL': 'positive',
    'OCUPADO': 'warning',
    'MANUTENÇÃO': 'negative'
  }
  return colors[status] || 'grey'
}

// Carregar terrenos na inicialização
onMounted(() => {
  fetchTerrenos()
})
</script>