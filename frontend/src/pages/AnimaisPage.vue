<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md text-primary">
      <q-icon name="pets" class="q-mr-sm" />
      Gestão dos Animais
    </div>

    <!-- Filtros -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="col-12 q-mb-md">
          <q-card flat bordered class="q-pa-md">
            <div class="row q-gutter-md items-end">
              <q-input
                v-model="animalStore.filters.nome"
                label="Pesquisar"
                clearable
                class="col-12 col-md-3"
                @update:model-value="fetchAnimais"
                :debounce="300"
                aria-label="Filtrar animais por nome"
              />

              <q-select
                v-model="animalStore.filters.sexo"
                :options="sexoOptions"
                label="Sexo"
                clearable
                emit-value
                map-options
                @update:model-value="fetchAnimais"
                class="col-12 col-md-3"
              />
          
              <q-select
                v-model="animalStore.filters.status"
                :options="statusOptions"
                label="Status"
                clearable
                emit-value
                map-options
                @update:model-value="fetchAnimais"
                class="col-12 col-md-3"
              />
            </div>
          </q-card>
        </div>

        <q-btn
          color="primary"
          icon="add"
          label="Novo Animal"
          @click="openDialog()"
        />

        <!-- Tabela -->
        <q-table
          :rows="animalStore.animais"
          :columns="columns"
          :loading="animalStore.loading"
          :pagination="animalStore.pagination"
          @request="onRequest"
          row-key="ID"
          binary-state-sort
          class="q-mt-md"
        >
          <template v-slot:body-cell-foto="props">
            <q-td :props="props">
              <q-avatar v-if="props.row.FOTO_PRINCIPAL" size="40px">
                <img :src="`http://localhost:8000${props.row.FOTO_PRINCIPAL}`" />
              </q-avatar>
              <q-icon v-else name="pets" size="40px" color="grey-5" />
            </q-td>
          </template>
          
          <template v-slot:body-cell-genealogia="props">
            <q-td :props="props">
              <q-btn
                flat
                dense
                color="blue"
                icon="account_tree"
                @click="viewGenealogia(props.row)"
                :disable="!props.row.ID_PAI && !props.row.ID_MAE"
              >
                <q-tooltip>Visualizar Genealogia</q-tooltip>
              </q-btn>
            </q-td>
          </template>

          <template v-slot:body-cell-acoes="props">
            <q-td :props="props">
              <q-btn
                flat
                dense
                color="blue"
                icon="visibility"
                @click="viewAnimal(props.row)"
              />
              <q-btn
                flat
                dense
                color="orange"
                icon="edit"
                @click="openDialog(props.row)"
              />
              <q-btn
                flat
                dense
                color="green"
                icon="photo_camera"
                @click="openFotoDialog(props.row)"
              />
              <q-btn
                flat
                dense
                color="red"
                icon="delete"
                @click="confirmDelete(props.row)"
              />
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>

    <!-- Modal de Genealogia -->
    <q-dialog v-model="genealogiaDialog">
      <q-card style="min-width: 800px;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Árvore Genealógica</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section v-if="genealogiaData">
          <div class="q-pa-md">
            <!-- Animal principal -->
            <div class="text-center q-mb-md">
              <q-card class="animal-card q-pa-md">
                <div class="row items-center">
                  <q-avatar v-if="genealogiaData.animal.FOTO_PRINCIPAL" size="60px" class="q-mr-md">
                    <img :src="`http://localhost:8000${genealogiaData.animal.FOTO_PRINCIPAL}`" />
                  </q-avatar>
                  <q-icon v-else name="pets" size="60px" color="grey-5" class="q-mr-md" />
                  <div>
                    <div class="text-h6">{{ genealogiaData.animal.NOME }}</div>
                    <div class="text-caption">{{ genealogiaData.animal.SEXO === 'M' ? 'Macho' : 'Fêmea' }}</div>
                  </div>
                </div>
              </q-card>
            </div>

            <!-- Pais -->
            <div class="row q-gutter-md justify-center">
              <!-- Pai -->
              <div class="col-5">
                <div class="text-center text-subtitle2 q-mb-sm">Pai</div>
                <q-card v-if="genealogiaData.pai" class="animal-card q-pa-md">
                  <div class="row items-center">
                    <q-avatar v-if="genealogiaData.pai.animal.FOTO_PRINCIPAL" size="50px" class="q-mr-sm">
                      <img :src="`http://localhost:8000${genealogiaData.pai.animal.FOTO_PRINCIPAL}`" />
                    </q-avatar>
                    <q-icon v-else name="pets" size="50px" color="grey-5" class="q-mr-sm" />
                    <div>
                      <div class="text-body1">{{ genealogiaData.pai.animal.NOME }}</div>
                      <div class="text-caption">Macho</div>
                    </div>
                  </div>
                </q-card>
                <div v-else class="text-center text-grey-5">Não informado</div>
              </div>

              <!-- Mãe -->
              <div class="col-5">
                <div class="text-center text-subtitle2 q-mb-sm">Mãe</div>
                <q-card v-if="genealogiaData.mae" class="animal-card q-pa-md">
                  <div class="row items-center">
                    <q-avatar v-if="genealogiaData.mae.animal.FOTO_PRINCIPAL" size="50px" class="q-mr-sm">
                      <img :src="`http://localhost:8000${genealogiaData.mae.animal.FOTO_PRINCIPAL}`" />
                    </q-avatar>
                    <q-icon v-else name="pets" size="50px" color="grey-5" class="q-mr-sm" />
                    <div>
                      <div class="text-body1">{{ genealogiaData.mae.animal.NOME }}</div>
                      <div class="text-caption">Fêmea</div>
                    </div>
                  </div>
                </q-card>
                <div v-else class="text-center text-grey-5">Não informado</div>
              </div>
            </div>

            <!-- Avós -->
            <div class="row q-gutter-md justify-center q-mt-md">
              <!-- Avô paterno -->
              <div class="col-2">
                <div class="text-center text-caption q-mb-sm">Avô Paterno</div>
                <q-card v-if="genealogiaData.pai?.pai" class="animal-card-small q-pa-sm">
                  <q-avatar v-if="genealogiaData.pai.pai.animal.FOTO_PRINCIPAL" size="40px">
                    <img :src="`http://localhost:8000${genealogiaData.pai.pai.animal.FOTO_PRINCIPAL}`" />
                  </q-avatar>
                  <q-icon v-else name="pets" size="40px" color="grey-5" />
                  <div class="text-caption">{{ genealogiaData.pai.pai.animal.NOME }}</div>
                </q-card>
                <div v-else class="text-center text-grey-5 text-caption">-</div>
              </div>

              <!-- Avó paterna -->
              <div class="col-2">
                <div class="text-center text-caption q-mb-sm">Avó Paterna</div>
                <q-card v-if="genealogiaData.pai?.mae" class="animal-card-small q-pa-sm">
                  <q-avatar v-if="genealogiaData.pai.mae.animal.FOTO_PRINCIPAL" size="40px">
                    <img :src="`http://localhost:8000${genealogiaData.pai.mae.animal.FOTO_PRINCIPAL}`" />
                  </q-avatar>
                  <q-icon v-else name="pets" size="40px" color="grey-5" />
                  <div class="text-caption">{{ genealogiaData.pai.mae.animal.NOME }}</div>
                </q-card>
                <div v-else class="text-center text-grey-5 text-caption">-</div>
              </div>

              <!-- Avô materno -->
              <div class="col-2">
                <div class="text-center text-caption q-mb-sm">Avô Materno</div>
                <q-card v-if="genealogiaData.mae?.pai" class="animal-card-small q-pa-sm">
                  <q-avatar v-if="genealogiaData.mae.pai.animal.FOTO_PRINCIPAL" size="40px">
                    <img :src="`http://localhost:8000${genealogiaData.mae.pai.animal.FOTO_PRINCIPAL}`" />
                  </q-avatar>
                  <q-icon v-else name="pets" size="40px" color="grey-5" />
                  <div class="text-caption">{{ genealogiaData.mae.pai.animal.NOME }}</div>
                </q-card>
                <div v-else class="text-center text-grey-5 text-caption">-</div>
              </div>

              <!-- Avó materna -->
              <div class="col-2">
                <div class="text-center text-caption q-mb-sm">Avó Materna</div>
                <q-card v-if="genealogiaData.mae?.mae" class="animal-card-small q-pa-sm">
                  <q-avatar v-if="genealogiaData.mae.mae.animal.FOTO_PRINCIPAL" size="40px">
                    <img :src="`http://localhost:8000${genealogiaData.mae.mae.animal.FOTO_PRINCIPAL}`" />
                  </q-avatar>
                  <q-icon v-else name="pets" size="40px" color="grey-5" />
                  <div class="text-caption">{{ genealogiaData.mae.mae.animal.NOME }}</div>
                </q-card>
                <div v-else class="text-center text-grey-5 text-caption">-</div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Modal de Visualização -->
    <q-dialog v-model="viewDialog">
      <q-card style="min-width: 500px;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Detalhes do Animal</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section v-if="viewAnimalData">
          <q-list>
            <q-item>
              <q-item-section avatar>
                <q-avatar v-if="viewAnimalData.FOTO_PRINCIPAL" size="60px">
                  <img :src="`http://localhost:8000${viewAnimalData.FOTO_PRINCIPAL}`" />
                </q-avatar>
                <q-icon v-else name="pets" size="60px" color="grey-5" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-h6">{{ viewAnimalData.NOME }}</q-item-label>
                <q-item-label caption>{{ viewAnimalData.NUMERO_REGISTRO || 'Sem registro' }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-separator />
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Sexo</q-item-label>
                <q-item-label>{{ viewAnimalData.SEXO === 'M' ? 'Macho' : 'Fêmea' }}</q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Status</q-item-label>
                <q-item-label>{{ viewAnimalData.STATUS_ANIMAL }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Data de Nascimento</q-item-label>
                <q-item-label>{{ viewAnimalData.DATA_NASCIMENTO || 'Não informado' }}</q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Pelagem</q-item-label>
                <q-item-label>{{ viewAnimalData.PELAGEM || 'Não informado' }}</q-item-label>
              </q-item-section>
            </q-item>

            <!-- Dados do Proprietário -->
            <q-separator class="q-my-md" />
            <q-item-label header>Proprietário</q-item-label>
            
            <q-item v-if="viewAnimalData.PROPRIETARIO">
              <q-item-section>
                <q-item-label caption>Nome</q-item-label>
                <q-item-label>{{ viewAnimalData.PROPRIETARIO }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item v-if="viewAnimalData.CONTATO_PROPRIETARIO">
              <q-item-section>
                <q-item-label caption>Contato</q-item-label>
                <q-item-label>{{ viewAnimalData.CONTATO_PROPRIETARIO }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item v-if="viewAnimalData.CPF_CNPJ_PROPRIETARIO">
              <q-item-section>
                <q-item-label caption>CPF/CNPJ</q-item-label>
                <q-item-label>{{ viewAnimalData.CPF_CNPJ_PROPRIETARIO }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-separator class="q-my-md" />
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Peso Atual</q-item-label>
                <q-item-label>{{ viewAnimalData.PESO_ATUAL ? `${viewAnimalData.PESO_ATUAL} kg` : 'Não informado' }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Data de Cadastro</q-item-label>
                <q-item-label>{{ formatDate(viewAnimalData?.DATA_CADASTRO) }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item v-if="viewAnimalData?.OBSERVACOES">
              <q-item-section>
                <q-item-label caption>Observações</q-item-label>
                <q-item-label>{{ viewAnimalData.OBSERVACOES }}</q-item-label>
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

    <!-- Modal de Cadastro/Edição usando componente -->
    <q-dialog v-model="dialog" persistent>
      <q-card style="width: 900px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6">{{ form.ID ? 'Editar' : 'Cadastrar' }} Animal</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <AnimalForm
            v-model="form"
            :loading="animalStore.loading"
            @submit="saveAnimal"
            @cancel="dialog = false"
          />
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Modal de Upload de Foto -->
    <q-dialog v-model="fotoDialog">
      <q-card style="min-width: 400px;">
        <q-card-section>
          <div class="text-h6">Upload de Foto</div>
        </q-card-section>
        <q-card-section>
          <q-file
            v-model="newFoto"
            label="Selecionar foto"
            accept="image/*"
            filled
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" @click="fotoDialog = false" />
          <q-btn color="primary" label="Upload" @click="uploadFoto" :loading="animalStore.loading" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Modal de Confirmação de Exclusão -->
    <q-dialog v-model="deleteDialog" persistent>
      <q-card>
        <q-card-section>
          <div class="text-h6">Confirmar Exclusão</div>
        </q-card-section>
        <q-card-section>
          Deseja excluir o animal <strong>{{ animalToDelete?.NOME }}</strong>?
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" @click="deleteDialog = false" />
          <q-btn color="negative" label="Excluir" @click="deleteAnimal" :loading="animalStore.loading" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'stores/auth'
import { useAnimalStore } from 'stores/animal'
import AnimalForm from 'components/AnimalForm.vue'
import { formatDate, prepareFormData } from '../utils/dateUtils'

const $q = useQuasar()
const authStore = useAuthStore()
const animalStore = useAnimalStore()

// Estado dos modals
const dialog = ref(false)
const viewDialog = ref(false)
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
  PROPRIETARIO: '',
  CONTATO_PROPRIETARIO: '',
  CPF_CNPJ_PROPRIETARIO: '',
  ID_USUARIO_CADASTRO: authStore.user.ID
})

const selectedAnimal = ref(null)
const viewAnimalData = ref(null)
const animalToDelete = ref(null)
const genealogiaData = ref(null)
const newFoto = ref(null)

// Opções
const sexoOptions = [
  { label: 'Macho', value: 'M' },
  { label: 'Fêmea', value: 'F' }
]

const statusOptions = [
  { label: 'Ativo', value: 'ATIVO' },
  { label: 'Vendido', value: 'VENDIDO' },
  { label: 'Morto', value: 'MORTO' },
  { label: 'Emprestado', value: 'EMPRESTADO' }
]

// Colunas da tabela
const columns = [
  { name: 'foto', label: 'Foto', field: 'foto', align: 'center' },
  { name: 'NOME', label: 'Nome', field: 'NOME', sortable: true, align: 'left' },
  { name: 'NUMERO_REGISTRO', label: 'Registro', field: 'NUMERO_REGISTRO', sortable: true, align: 'left' },
  { name: 'SEXO', label: 'Sexo', field: 'SEXO', sortable: true, align: 'center' },
  { name: 'DATA_NASCIMENTO', label: 'Nascimento', field: 'DATA_NASCIMENTO', sortable: true, align: 'left' },
  { name: 'STATUS_ANIMAL', label: 'Status', field: 'STATUS_ANIMAL', sortable: true, align: 'center' },
  { name: 'PROPRIETARIO', label: 'Proprietário', field: 'PROPRIETARIO', sortable: true, align: 'left' },
  { name: 'genealogia', label: 'Genealogia', field: 'genealogia', align: 'center' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

// Funções
async function fetchAnimais(props = {}) {
  try {
    await animalStore.fetchAnimais(props)
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error
    })
  }
}

function onRequest(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  animalStore.setPagination({ page, rowsPerPage, sortBy, descending })
  fetchAnimais(props)
}

function openDialog(animal) {
  if (animal) {
    form.value = { 
      ...animal, 
      ID_USUARIO_CADASTRO: authStore.user.ID
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
      PROPRIETARIO: '',
      CONTATO_PROPRIETARIO: '',
      CPF_CNPJ_PROPRIETARIO: '',
      ID_USUARIO_CADASTRO: authStore.user.ID
    }
  }
  dialog.value = true
}

async function saveAnimal() {
  try {
    const dateFields = ['DATA_NASCIMENTO']
    const formData = prepareFormData(form.value, dateFields)
    
    if (formData.ID) {
      await animalStore.updateAnimal(formData.ID, formData)
      $q.notify({ type: 'positive', message: 'Animal atualizado com sucesso' })
    } else {
      await animalStore.createAnimal(formData)
      $q.notify({ type: 'positive', message: 'Animal cadastrado com sucesso' })
    }
    dialog.value = false
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error
    })
  }
}

function confirmDelete(animal) {
  animalToDelete.value = animal
  deleteDialog.value = true
}

function viewAnimal(animal) {
  viewAnimalData.value = animal
  viewDialog.value = true
}

function editFromView() {
  viewDialog.value = false
  openDialog(viewAnimalData.value)
}

async function deleteAnimal() {
  try {
    await animalStore.deleteAnimal(animalToDelete.value.ID)
    $q.notify({ type: 'positive', message: 'Animal excluído com sucesso' })
    deleteDialog.value = false
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error
    })
  }
}

async function viewGenealogia(animal) {
  try {
    genealogiaData.value = await animalStore.getGenealogia(animal.ID)
    genealogiaDialog.value = true
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error
    })
  }
}

function openFotoDialog(animal) {
  selectedAnimal.value = animal
  fotoDialog.value = true
}

async function uploadFoto() {
  if (!newFoto.value || !selectedAnimal.value) return
  
  try {
    await animalStore.uploadFoto(selectedAnimal.value.ID, newFoto.value)
    $q.notify({ type: 'positive', message: 'Foto enviada com sucesso' })
    fotoDialog.value = false
    newFoto.value = null
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error
    })
  }
}

onMounted(() => {
  fetchAnimais()
})
</script>

<style scoped>
.animal-card {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
}

.animal-card-small {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  text-align: center;
  min-height: 80px;
}
</style>