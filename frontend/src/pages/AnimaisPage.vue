<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Gestão de Animais</div>
      </q-card-section>
      <q-card-section>
        <div class="row q-gutter-md q-mb-md">
          <q-input
            v-model="animalStore.filters.nome"
            label="Filtrar por Nome"
            clearable
            @update:model-value="fetchAnimais"
            :debounce="300"
            aria-label="Filtrar animais por nome"
            class="col-3"
          />
          <q-select
            v-model="animalStore.filters.sexo"
            :options="sexoOptions"
            label="Sexo"
            clearable
            @update:model-value="fetchAnimais"
            aria-label="Filtrar por sexo"
            class="col-2"
          />
          <q-select
            v-model="animalStore.filters.status"
            :options="statusOptions"
            label="Status"
            clearable
            @update:model-value="fetchAnimais"
            aria-label="Filtrar por status"
            class="col-2"
          />
          <q-input
            v-model="animalStore.filters.numero_registro"
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
          :rows="animalStore.animais"
          :columns="columns"
          row-key="ID"
          :loading="animalStore.loading"
          :pagination="animalStore.pagination"
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
                icon="visibility"
                @click="viewAnimal(props.row)"
                aria-label="Visualizar animal"
              />
              <q-btn
                flat
                round
                color="secondary"
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

    <!-- Diálogo de Visualização -->
    <q-dialog v-model="viewDialog" persistent>
      <q-card style="width: 600px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6 flex items-center">
            <q-avatar v-if="viewAnimalData?.FOTO_PRINCIPAL" size="50px" class="q-mr-md">
              <img :src="`http://localhost:8000${viewAnimalData.FOTO_PRINCIPAL}`" />
            </q-avatar>
            <q-icon v-else name="pets" size="50px" color="primary" class="q-mr-md" />
            {{ viewAnimalData?.NOME }}
          </div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <div class="row q-gutter-md">
            <div class="col-12">
              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>ID</q-item-label>
                    <q-item-label>{{ viewAnimalData?.ID }}</q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Número de Registro</q-item-label>
                    <q-item-label>{{ viewAnimalData?.NUMERO_REGISTRO || 'Não informado' }}</q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Chip de Identificação</q-item-label>
                    <q-item-label>{{ viewAnimalData?.CHIP_IDENTIFICACAO || 'Não informado' }}</q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Sexo</q-item-label>
                    <q-item-label>
                      <q-icon 
                        :name="viewAnimalData?.SEXO === 'M' ? 'male' : 'female'" 
                        :color="viewAnimalData?.SEXO === 'M' ? 'blue' : 'pink'"
                        size="sm"
                        class="q-mr-xs"
                      />
                      {{ viewAnimalData?.SEXO === 'M' ? 'Macho' : 'Fêmea' }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Data de Nascimento</q-item-label>
                    <q-item-label>{{ formatDate(viewAnimalData?.DATA_NASCIMENTO) }}</q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Pelagem</q-item-label>
                    <q-item-label>{{ viewAnimalData?.PELAGEM || 'Não informado' }}</q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Status</q-item-label>
                    <q-item-label>
                      <q-chip 
                        :color="getStatusColor(viewAnimalData?.STATUS_ANIMAL)" 
                        text-color="white" 
                        dense
                      >
                        {{ viewAnimalData?.STATUS_ANIMAL }}
                      </q-chip>
                    </q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Origem</q-item-label>
                    <q-item-label>{{ viewAnimalData?.ORIGEM || 'Não informado' }}</q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Peso Atual</q-item-label>
                    <q-item-label>{{ viewAnimalData?.PESO_ATUAL ? `${viewAnimalData.PESO_ATUAL} kg` : 'Não informado' }}</q-item-label>
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
            </div>
          </div>
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
              <calendario-component
                  v-model="form.DATA_NASCIMENTO"
                  label="Data de Nascimento"
                  class="col-5"
              />
              <q-select
                v-model="form.SEXO"
                :options="sexoOptions"
                label="Sexo"
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
              <q-input
                v-model="form.ORIGEM"
                label="Origem"
                class="col-5"
              />

              <q-input
                v-model="form.PELAGEM"
                label="Pelagem"
                class="col-3"
              />

              <q-input
                v-model.number="form.PESO_ATUAL"
                label="Peso Atual (kg)"
                type="number"
                step="0.1"
                class="col-3"
              />
            </div>

            <div class="row q-gutter-md q-mt-sm">
              <q-select
                v-model="form.ID_PAI"
                :options="animalStore.parentOptions.machos"
                label="Pai"
                clearable
                use-input
                @filter="filterMachos"
                class="col-5"
              />
              <q-select
                v-model="form.ID_MAE"
                :options="animalStore.parentOptions.femeas"
                label="Mãe"
                clearable
                use-input
                @filter="filterFemeas"
                class="col-5"
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
              :disable="animalStore.loading"
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
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '../stores/auth'
import { useAnimalStore } from '../stores/animal'
import CalendarioComponent from '../components/CalendarioComponent.vue'

const $q = useQuasar()
const authStore = useAuthStore()
const animalStore = useAnimalStore()

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
  ID_USUARIO_CADASTRO: authStore.user.ID
})

const selectedAnimal = ref(null)
const viewAnimalData = ref(null)
const animalToDelete = ref(null)
const genealogiaData = ref(null)
const newFoto = ref(null)

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
  try {
    if (form.value.ID) {
      await animalStore.updateAnimal(form.value.ID, form.value)
      $q.notify({ type: 'positive', message: 'Animal atualizado com sucesso' })
    } else {
      await animalStore.createAnimal(form.value)
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

function openFotoDialog(animal) {
  selectedAnimal.value = animal
  fotoDialog.value = true
}

async function uploadFoto() {
  if (!newFoto.value || !selectedAnimal.value) return
  
  try {
    await animalStore.uploadFoto(selectedAnimal.value.ID, newFoto.value)
    $q.notify({ type: 'positive', message: 'Foto enviada com sucesso' })
    
    // Atualizar foto principal do animal
    selectedAnimal.value = animalStore.animalById(selectedAnimal.value.ID)
    newFoto.value = null
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: error
    })
  }
}

async function showGenealogia(animal) {
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

async function loadParentOptions() {
  try {
    await animalStore.loadParentOptions()
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