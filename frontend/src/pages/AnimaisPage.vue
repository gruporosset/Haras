<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Gestão de Animais</div>
      </q-card-section>
      <q-card-section>
        <div class="row q-gutter-md q-mb-md">
          <q-input
            v-model="filters.nome"
            label="Filtrar por Nome"
            clearable
            @update:model-value="fetchAnimais"
            :debounce="300"
            aria-label="Filtrar animais por nome"
            class="col-3"
          />
          <q-select
            v-model="filters.sexo"
            :options="sexoOptions"
            label="Sexo"
            clearable
            @update:model-value="fetchAnimais"
            aria-label="Filtrar por sexo"
            class="col-2"
          />
          <q-select
            v-model="filters.status"
            :options="statusOptions"
            label="Status"
            clearable
            @update:model-value="fetchAnimais"
            aria-label="Filtrar por status"
            class="col-2"
          />
          <q-input
            v-model="filters.numero_registro"
            label="Nº Registro"
            clearable
            @update:model-value="fetchAnimais"
            :debounce="300"
            class="col-2"
          />
          <q-btn
            color="primary"
            label="Novo Animal"
            icon="add"
            @click="openDialog(null)"
            aria-label="Cadastrar novo animal"
          />
        </div>
        
        <q-table
          :rows="animais"
          :columns="columns"
          row-key="ID"
          :loading="loading"
          :pagination="pagination"
          @request="onRequest"
          binary-state-sort
          aria-label="Tabela de animais"
        >
          <template v-slot:body-cell-foto="props">
            <q-td :props="props">
              <q-avatar v-if="props.row.FOTO_PRINCIPAL" size="40px">
                <img :src="`http://localhost:8000${props.row.FOTO_PRINCIPAL}`" />
              </q-avatar>
              <q-icon v-else name="pets" size="40px" color="grey-5" />
            </q-td>
          </template>
          <template v-slot:body-cell-sexo="props">
            <q-td :props="props">
              <q-icon 
                :name="props.row.SEXO === 'M' ? 'male' : 'female'" 
                :color="props.row.SEXO === 'M' ? 'blue' : 'pink'"
                size="sm"
              />
              {{ props.row.SEXO === 'M' ? 'Macho' : 'Fêmea' }}
            </q-td>
          </template>
          <template v-slot:body-cell-status="props">
            <q-td :props="props">
              <q-chip 
                :color="getStatusColor(props.row.STATUS_ANIMAL)" 
                text-color="white" 
                dense
              >
                {{ props.row.STATUS_ANIMAL }}
              </q-chip>
            </q-td>
          </template>
          <template v-slot:body-cell-acoes="props">
            <q-td :props="props">
              <q-btn
                flat
                round
                color="info"
                icon="account_tree"
                @click="showGenealogia(props.row)"
                aria-label="Ver genealogia"
              />
              <q-btn
                flat
                round
                color="primary"
                icon="edit"
                @click="openDialog(props.row)"
                aria-label="Editar animal"
              />
              <q-btn
                flat
                round
                color="secondary"
                icon="photo_camera"
                @click="openFotoDialog(props.row)"
                aria-label="Gerenciar fotos"
              />
              <q-btn
                flat
                round
                color="negative"
                icon="delete"
                @click="confirmDelete(props.row)"
                aria-label="Excluir animal"
              />
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>

    <!-- Diálogo para Cadastro/Edição -->
    <q-dialog v-model="dialog" persistent>
      <q-card style="width: 700px; max-width: 90vw">
        <q-form @submit="saveAnimal">
          <q-card-section>
            <div class="text-h6">{{ form.ID ? 'Editar' : 'Cadastrar' }} Animal</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <div class="row q-gutter-md">
              <q-input
                v-model="form.NOME"
                label="Nome *"
                :rules="[val => !!val || 'Nome é obrigatório']"
                class="col-5"
              />
              <q-input
                v-model="form.NUMERO_REGISTRO"
                label="Número de Registro"
                class="col-3"
              />
              <q-input
                v-model="form.CHIP_IDENTIFICACAO"
                label="Chip"
                class="col-3"
              />
            </div>
            
            <div class="row q-gutter-md q-mt-sm">
              <q-select
                v-model="form.SEXO"
                :options="sexoOptions"
                label="Sexo"
                class="col-2"
              />
              <q-input
                v-model="form.DATA_NASCIMENTO"
                label="Data de Nascimento"
                type="date"
                class="col-3"
              />
              <q-input
                v-model="form.PELAGEM"
                label="Pelagem"
                class="col-3"
              />
              <q-select
                v-model="form.STATUS_ANIMAL"
                :options="statusOptions"
                label="Status"
                class="col-3"
              />
            </div>

            <div class="row q-gutter-md q-mt-sm">
              <q-select
                v-model="form.ID_PAI"
                :options="machoOptions"
                label="Pai"
                clearable
                use-input
                @filter="filterMachos"
                class="col-5"
              />
              <q-select
                v-model="form.ID_MAE"
                :options="femeaOptions"
                label="Mãe"
                clearable
                use-input
                @filter="filterFemeas"
                class="col-5"
              />
            </div>

            <div class="row q-gutter-md q-mt-sm">
              <q-input
                v-model="form.ORIGEM"
                label="Origem"
                class="col-4"
              />
              <q-input
                v-model.number="form.PESO_ATUAL"
                label="Peso Atual (kg)"
                type="number"
                step="0.1"
                class="col-3"
              />
            </div>

            <q-input
              v-model="form.OBSERVACOES"
              label="Observações"
              type="textarea"
              rows="3"
              class="q-mt-sm"
            />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn
              flat
              label="Cancelar"
              color="gray"
              @click="dialog = false"
            />
            <q-btn
              type="submit"
              color="primary"
              label="Salvar"
              :disable="loading"
            />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- Diálogo de Fotos -->
    <q-dialog v-model="fotoDialog" persistent>
      <q-card style="width: 500px">
        <q-card-section>
          <div class="text-h6">Gerenciar Fotos - {{ selectedAnimal?.NOME }}</div>
        </q-card-section>
        <q-card-section>
          <q-file
            v-model="newFoto"
            label="Selecionar Foto"
            accept="image/*"
            @update:model-value="uploadFoto"
            outlined
          >
            <template v-slot:prepend>
              <q-icon name="cloud_upload" />
            </template>
          </q-file>
          
          <div v-if="selectedAnimal?.FOTO_PRINCIPAL" class="q-mt-md text-center">
            <q-img
              :src="`http://localhost:8000${selectedAnimal.FOTO_PRINCIPAL}`"
              style="max-width: 300px; max-height: 300px"
              class="rounded-borders"
            />
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            label="Fechar"
            color="gray"
            @click="fotoDialog = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Diálogo de Genealogia -->
    <q-dialog v-model="genealogiaDialog" persistent>
      <q-card style="width: 800px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6">Árvore Genealógica - {{ genealogiaData?.animal?.NOME }}</div>
        </q-card-section>
        <q-card-section>
          <div class="genealogy-tree" v-if="genealogiaData">
            <!-- Animal Principal -->
            <div class="animal-card main-animal">
              <q-card class="q-pa-md text-center">
                <q-avatar v-if="genealogiaData.animal.FOTO_PRINCIPAL" size="60px">
                  <img :src="`http://localhost:8000${genealogiaData.animal.FOTO_PRINCIPAL}`" />
                </q-avatar>
                <q-icon v-else name="pets" size="60px" color="primary" />
                <div class="text-h6">{{ genealogiaData.animal.NOME }}</div>
                <div class="text-caption">{{ genealogiaData.animal.SEXO === 'M' ? 'Macho' : 'Fêmea' }}</div>
                <div class="text-caption">{{ formatDate(genealogiaData.animal.DATA_NASCIMENTO) }}</div>
              </q-card>
            </div>

            <!-- Pais -->
            <div class="parents-row">
              <!-- Pai -->
              <div class="animal-card parent">
                <q-card v-if="genealogiaData.pai" class="q-pa-sm text-center">
                  <q-avatar v-if="genealogiaData.pai.animal.FOTO_PRINCIPAL" size="40px">
                    <img :src="`http://localhost:8000${genealogiaData.pai.animal.FOTO_PRINCIPAL}`" />
                  </q-avatar>
                  <q-icon v-else name="pets" size="40px" color="blue" />
                  <div class="text-subtitle2">{{ genealogiaData.pai.animal.NOME }}</div>
                  <div class="text-caption">Pai</div>
                  <div class="text-caption">{{ formatDate(genealogiaData.pai.animal.DATA_NASCIMENTO) }}</div>
                </q-card>
                <q-card v-else class="q-pa-sm text-center bg-grey-2">
                  <q-icon name="help_outline" size="40px" color="grey" />
                  <div class="text-caption">Pai desconhecido</div>
                </q-card>
              </div>

              <!-- Mãe -->
              <div class="animal-card parent">
                <q-card v-if="genealogiaData.mae" class="q-pa-sm text-center">
                  <q-avatar v-if="genealogiaData.mae.animal.FOTO_PRINCIPAL" size="40px">
                    <img :src="`http://localhost:8000${genealogiaData.mae.animal.FOTO_PRINCIPAL}`" />
                  </q-avatar>
                  <q-icon v-else name="pets" size="40px" color="pink" />
                  <div class="text-subtitle2">{{ genealogiaData.mae.animal.NOME }}</div>
                  <div class="text-caption">Mãe</div>
                  <div class="text-caption">{{ formatDate(genealogiaData.mae.animal.DATA_NASCIMENTO) }}</div>
                </q-card>
                <q-card v-else class="q-pa-sm text-center bg-grey-2">
                  <q-icon name="help_outline" size="40px" color="grey" />
                  <div class="text-caption">Mãe desconhecida</div>
                </q-card>
              </div>
            </div>

            <!-- Avós -->
            <div class="grandparents-row">
              <!-- Avô paterno -->
              <div class="animal-card grandparent">
                <q-card v-if="genealogiaData.pai?.pai" class="q-pa-xs text-center">
                  <q-avatar v-if="genealogiaData.pai.pai.animal.FOTO_PRINCIPAL" size="30px">
                    <img :src="`http://localhost:8000${genealogiaData.pai.pai.animal.FOTO_PRINCIPAL}`" />
                  </q-avatar>
                  <q-icon v-else name="pets" size="30px" color="blue" />
                  <div class="text-caption">{{ genealogiaData.pai.pai.animal.NOME }}</div>
                  <div class="text-caption">Avô paterno</div>
                </q-card>
              </div>

              <!-- Avó paterna -->
              <div class="animal-card grandparent">
                <q-card v-if="genealogiaData.pai?.mae" class="q-pa-xs text-center">
                  <q-avatar v-if="genealogiaData.pai.mae.animal.FOTO_PRINCIPAL" size="30px">
                    <img :src="`http://localhost:8000${genealogiaData.pai.mae.animal.FOTO_PRINCIPAL}`" />
                  </q-avatar>
                  <q-icon v-else name="pets" size="30px" color="pink" />
                  <div class="text-caption">{{ genealogiaData.pai.mae.animal.NOME }}</div>
                  <div class="text-caption">Avó paterna</div>
                </q-card>
              </div>

              <!-- Avô materno -->
              <div class="animal-card grandparent">
                <q-card v-if="genealogiaData.mae?.pai" class="q-pa-xs text-center">
                  <q-avatar v-if="genealogiaData.mae.pai.animal.FOTO_PRINCIPAL" size="30px">
                    <img :src="`http://localhost:8000${genealogiaData.mae.pai.animal.FOTO_PRINCIPAL}`" />
                  </q-avatar>
                  <q-icon v-else name="pets" size="30px" color="blue" />
                  <div class="text-caption">{{ genealogiaData.mae.pai.animal.NOME }}</div>
                  <div class="text-caption">Avô materno</div>
                </q-card>
              </div>

              <!-- Avó materna -->
              <div class="animal-card grandparent">
                <q-card v-if="genealogiaData.mae?.mae" class="q-pa-xs text-center">
                  <q-avatar v-if="genealogiaData.mae.mae.animal.FOTO_PRINCIPAL" size="30px">
                    <img :src="`http://localhost:8000${genealogiaData.mae.mae.animal.FOTO_PRINCIPAL}`" />
                  </q-avatar>
                  <q-icon v-else name="pets" size="30px" color="pink" />
                  <div class="text-caption">{{ genealogiaData.mae.mae.animal.NOME }}</div>
                  <div class="text-caption">Avó materna</div>
                </q-card>
              </div>
            </div>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            label="Fechar"
            color="gray"
            @click="genealogiaDialog = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Diálogo de Confirmação de Exclusão -->
    <q-dialog v-model="deleteDialog" persistent>
      <q-card>
        <q-card-section>
          <div class="text-h6">Confirmar Exclusão</div>
        </q-card-section>
        <q-card-section>
          Deseja excluir o animal "{{ animalToDelete?.NOME }}"?
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancelar"
            color="gray"
            @click="deleteDialog = false"
          />
          <q-btn
            color="negative"
            label="Excluir"
            @click="deleteAnimal"
            :disable="loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '../stores/auth'
import api from '../boot/api'

const $q = useQuasar()
const authStore = useAuthStore()

// Estado da tabela
const animais = ref([])
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
  sexo: null,
  status: null,
  numero_registro: ''
})

const columns = [
  { name: 'foto', label: '', field: 'FOTO_PRINCIPAL', align: 'center', style: 'width: 60px' },
  { name: 'ID', label: 'ID', field: 'ID', sortable: true, align: 'left' },
  { name: 'NOME', label: 'Nome', field: 'NOME', sortable: true, align: 'left' },
  { name: 'NUMERO_REGISTRO', label: 'Registro', field: 'NUMERO_REGISTRO', sortable: true, align: 'left' },
  { name: 'sexo', label: 'Sexo', field: 'SEXO', sortable: true, align: 'center' },
  { name: 'DATA_NASCIMENTO', label: 'Nascimento', field: 'DATA_NASCIMENTO', sortable: true, align: 'left' },
  { name: 'status', label: 'Status', field: 'STATUS_ANIMAL', sortable: true, align: 'center' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

const sexoOptions = [
  { value: 'M', label: 'Macho' },
  { value: 'F', label: 'Fêmea' }
]

const statusOptions = [
  { value: 'ATIVO', label: 'Ativo' },
  { value: 'VENDIDO', label: 'Vendido' },
  { value: 'MORTO', label: 'Morto' },
  { value: 'EMPRESTADO', label: 'Emprestado' }
]

// Estado dos diálogos
const dialog = ref(false)
const fotoDialog = ref(false)
const genealogiaDialog = ref(false)
const deleteDialog = ref(false)

// Dados dos formulários
const form = ref({
  ID: null,
  NOME: '',
  NUMERO_REGISTRO: '',
  CHIP_IDENTIFICACAO: '',
  SEXO: null,
  DATA_NASCIMENTO: '',
  PELAGEM: '',
  STATUS_ANIMAL: 'ATIVO',
  ID_PAI: null,
  ID_MAE: null,
  ORIGEM: '',
  OBSERVACOES: '',
  PESO_ATUAL: null,
  ID_USUARIO_CADASTRO: authStore.user.ID
})

const selectedAnimal = ref(null)
const animalToDelete = ref(null)
const genealogiaData = ref(null)
const newFoto = ref(null)

// Opções para seleção de pais
const machoOptions = ref([])
const femeaOptions = ref([])

// Funções
async function fetchAnimais(props = {}) {
  loading.value = true
  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination
    const params = {
      page,
      limit: rowsPerPage,
      sort_by: sortBy,
      order: descending ? 'desc' : 'asc',
      nome: filters.nome,
      sexo: filters.sexo?.value,
      status: filters.status?.value,
      numero_registro: filters.numero_registro
    }
    const response = await api.get('/api/animais', { params })
    animais.value = response.data.animais
    pagination.rowsNumber = response.data.total
    pagination.page = response.data.page
    pagination.rowsPerPage = response.data.limit
    pagination.sortBy = sortBy
    pagination.descending = descending
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao carregar animais: ' + (error.response?.data?.detail || 'Tente novamente')
    })
  } finally {
    loading.value = false
  }
}

function onRequest(props) {
  fetchAnimais(props)
}

function openDialog(animal) {
  if (animal) {
    form.value = { 
      ...animal, 
      ID_USUARIO_CADASTRO: authStore.user.ID,
      DATA_NASCIMENTO: animal.DATA_NASCIMENTO ? animal.DATA_NASCIMENTO.split(' ')[0] : ''
    }
  } else {
    form.value = {
      ID: null,
      NOME: '',
      NUMERO_REGISTRO: '',
      CHIP_IDENTIFICACAO: '',
      SEXO: null,
      DATA_NASCIMENTO: '',
      PELAGEM: '',
      STATUS_ANIMAL: 'ATIVO',
      ID_PAI: null,
      ID_MAE: null,
      ORIGEM: '',
      OBSERVACOES: '',
      PESO_ATUAL: null,
      ID_USUARIO_CADASTRO: authStore.user.ID
    }
  }
  loadParentOptions()
  dialog.value = true
}

async function saveAnimal() {
  loading.value = true
  try {
    if (form.value.ID) {
      await api.put(`/api/animais/${form.value.ID}`, form.value)
      $q.notify({ type: 'positive', message: 'Animal atualizado com sucesso' })
    } else {
      await api.post('/api/animais', form.value)
      $q.notify({ type: 'positive', message: 'Animal cadastrado com sucesso' })
    }
    dialog.value = false
    await fetchAnimais()
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao salvar animal: ' + (error.response?.data?.detail || 'Tente novamente')
    })
  } finally {
    loading.value = false
  }
}

function confirmDelete(animal) {
  animalToDelete.value = animal
  deleteDialog.value = true
}

async function deleteAnimal() {
  loading.value = true
  try {
    await api.delete(`/api/animais/${animalToDelete.value.ID}`)
    $q.notify({ type: 'positive', message: 'Animal excluído com sucesso' })
    deleteDialog.value = false
    await fetchAnimais()
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao excluir animal: ' + (error.response?.data?.detail || 'Tente novamente')
    })
  } finally {
    loading.value = false
  }
}

function openFotoDialog(animal) {
  selectedAnimal.value = animal
  fotoDialog.value = true
}

async function uploadFoto() {
  if (!newFoto.value || !selectedAnimal.value) return
  
  const formData = new FormData()
  formData.append('foto', newFoto.value)
  
  try {
    const response = await api.post(`/api/animais/${selectedAnimal.value.ID}/foto`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    $q.notify({ type: 'positive', message: 'Foto enviada com sucesso' })
    
    // Atualizar foto principal do animal
    selectedAnimal.value.FOTO_PRINCIPAL = response.data.url
    await fetchAnimais()
    
    newFoto.value = null
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao enviar foto: ' + (error.response?.data?.detail || 'Tente novamente')
    })
  }
}

async function showGenealogia(animal) {
  try {
    const response = await api.get(`/api/animais/${animal.ID}/genealogia`)
    genealogiaData.value = response.data
    genealogiaDialog.value = true
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao carregar genealogia: ' + (error.response?.data?.detail || 'Tente novamente')
    })
  }
}

async function loadParentOptions() {
  try {
    const [machosRes, femeasRes] = await Promise.all([
      api.get('/api/animais/options/parents?sexo=M'),
      api.get('/api/animais/options/parents?sexo=F')
    ])
    machoOptions.value = machosRes.data
    femeaOptions.value = femeasRes.data
  } catch (error) {
    console.error('Erro ao carregar opções de pais:', error)
  }
}

function filterMachos(val, update) {
  update(() => {
    // Implementar filtro se necessário
  })
}

function filterFemeas(val, update) {
  update(() => {
    // Implementar filtro se necessário
  })
}

function getStatusColor(status) {
  const colors = {
    'ATIVO': 'positive',
    'VENDIDO': 'info',
    'MORTO': 'negative',
    'EMPRESTADO': 'warning'
  }
  return colors[status] || 'grey'
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('pt-BR')
}

// Carregar dados na inicialização
onMounted(() => {
  fetchAnimais()
})
</script>

<style scoped>
.genealogy-tree {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.main-animal {
  width: 200px;
}

.parents-row {
  display: flex;
  gap: 100px;
}

.parent {
  width: 150px;
}

.grandparents-row {
  display: flex;
  gap: 20px;
}

.grandparent {
  width: 120px;
}

.animal-card {
  flex-shrink: 0;
}
</style>