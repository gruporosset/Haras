<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Crescimento e Saúde dos Animais</div>
      </q-card-section>
      <q-card-section>
        <!-- Filtros -->
        <div class="row q-gutter-md q-mb-md">
          <q-select
            v-model="crescimentoStore.filters.animal_id"
            :options="animalOptions"
            label="Filtrar por Animal"
            clearable
            use-input
            @filter="filterAnimais"
            @update:model-value="onFilterChange"
            class="col-3"
          />

          <calendario-component
              v-model="crescimentoStore.filters.data_inicio"
              label="Data Início"
              @update:model-value="onFilterChange"
              class="col-2"
          />
          <calendario-component
              v-model="crescimentoStore.filters.data_fim"
              label="Data Fim"
              @update:model-value="onFilterChange"
              class="col-2"
          />
        </div>
        
        <!-- Abas -->
        <q-tabs v-model="activeTab" class="q-mb-md">
          <q-tab name="crescimento" label="Crescimento" />
          <q-tab name="saude" label="Saúde" />
          <q-tab name="calendario" label="Calendário" />
          <q-tab name="relatorios" label="Relatórios" />
        </q-tabs>
        
        <q-tab-panels v-model="activeTab" animated>
          <!-- ABA CRESCIMENTO -->
          <q-tab-panel name="crescimento">
            <div class="row q-gutter-md q-mb-md">
              <q-btn
                color="secondary"
                label="Novo Registro de Crescimento"
                icon="add"
                @click="openDialog(null, 'crescimento')"
              />
            </div>

            <q-table
              :rows="crescimentoStore.crescimentos"
              :columns="crescimentoColumns"
              row-key="ID"
              :loading="crescimentoStore.loading"
              :pagination="crescimentoStore.pagination"
              @request="onRequestCrescimento"
              binary-state-sort
            >
              <template v-slot:body-cell-animal="props">
                <q-td :props="props">
                  {{ getAnimalName(props.row.ID_ANIMAL) }}
                </q-td>
              </template>
              <template v-slot:body-cell-acoes="props">
                <q-td :props="props">
                  <q-btn
                    flat
                    round
                    color="info"
                    icon="visibility"
                    @click="viewRecord(props.row, 'crescimento')"
                  />
                  <q-btn
                    flat
                    round
                    color="primary"
                    icon="edit"
                    @click="openDialog(props.row, 'crescimento')"
                  />
                  <q-btn
                    flat
                    round
                    color="negative"
                    icon="delete"
                    @click="confirmDelete(props.row, 'crescimento')"
                  />
                </q-td>
              </template>
            </q-table>
          </q-tab-panel>
          
          <!-- ABA SAÚDE -->
          <q-tab-panel name="saude">
            <div class="row q-gutter-md q-mb-md">
              <q-select
                v-model="crescimentoStore.filters.tipo_registro"
                :options="crescimentoStore.tiposRegistro"
                label="Tipo de Registro"
                clearable
                @update:model-value="onFilterChangeSaude"
                class="col-3"
              />
              <q-btn
                color="secondary"
                label="Novo Registro de Saúde"
                icon="add"
                @click="openDialog(null, 'saude')"
              />
            </div>
            
            <q-table
              :rows="crescimentoStore.saudes"
              :columns="saudeColumns"
              row-key="ID"
              :loading="crescimentoStore.loading"
              :pagination="crescimentoStore.pagination"
              @request="onRequestSaude"
              binary-state-sort
            >
              <template v-slot:body-cell-animal="props">
                <q-td :props="props">
                  {{ getAnimalName(props.row.ID_ANIMAL) }}
                </q-td>
              </template>
              <template v-slot:body-cell-tipo="props">
                <q-td :props="props">
                  <q-chip
                    :color="getTipoColor(props.row.TIPO_REGISTRO)"
                    text-color="white"
                    dense
                  >
                    {{ props.row.TIPO_REGISTRO }}
                  </q-chip>
                </q-td>
              </template>
              <template v-slot:body-cell-proxima="props">
                <q-td :props="props">
                  <span v-if="props.row.PROXIMA_APLICACAO">
                    {{ formatDate(props.row.PROXIMA_APLICACAO) }}
                    <q-chip
                      v-if="isVencendo(props.row.PROXIMA_APLICACAO)"
                      color="warning"
                      text-color="white"
                      size="sm"
                      class="q-ml-xs"
                    >
                      Vencendo
                    </q-chip>
                  </span>
                  <span v-else class="text-grey">-</span>
                </q-td>
              </template>
              <template v-slot:body-cell-acoes="props">
                <q-td :props="props">
                  <q-btn
                    flat
                    round
                    color="info"
                    icon="visibility"
                    @click="viewRecord(props.row, 'saude')"
                  />
                  <q-btn
                    flat
                    round
                    color="primary"
                    icon="edit"
                    @click="openDialog(props.row, 'saude')"
                  />
                  <q-btn
                    flat
                    round
                    color="negative"
                    icon="delete"
                    @click="confirmDelete(props.row, 'saude')"
                  />
                </q-td>
              </template>
            </q-table>
          </q-tab-panel>
          
          <!-- ABA CALENDÁRIO -->
          <q-tab-panel name="calendario">
            <div class="text-h6 q-mb-md">Próximas Aplicações</div>
            <q-list bordered>
              <q-item
                v-for="aplicacao in crescimentoStore.proximasAplicacoes"
                :key="`${aplicacao.animal_id}-${aplicacao.data_aplicacao}`"
                clickable
              >
                <q-item-section avatar>
                  <q-icon
                    :name="getIconByTipo(aplicacao.tipo_registro)"
                    :color="getTipoColor(aplicacao.tipo_registro)"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ aplicacao.animal_nome }}</q-item-label>
                  <q-item-label caption>{{ aplicacao.tipo_registro }} - {{ aplicacao.descricao }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label>{{ formatDate(aplicacao.data_aplicacao) }}</q-item-label>
                  <q-item-label caption>
                    <q-chip
                      :color="aplicacao.dias_restantes <= 3 ? 'negative' : 'warning'"
                      text-color="white"
                      size="sm"
                    >
                      {{ aplicacao.dias_restantes }} dias
                    </q-chip>
                  </q-item-label>
                </q-item-section>
              </q-item>
              <q-item v-if="!crescimentoStore.proximasAplicacoes.length">
                <q-item-section>
                  <q-item-label class="text-center text-grey">
                    Nenhuma aplicação pendente nos próximos 30 dias
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-tab-panel>
          
          <!-- ABA RELATÓRIOS -->
          <q-tab-panel name="relatorios">
            <div class="text-h6 q-mb-md">Estatísticas de Crescimento</div>
            <q-table
              :rows="crescimentoStore.estatisticas"
              :columns="estatisticasColumns"
              row-key="animal_id"
              :loading="crescimentoStore.loading"
              flat
            >
              <template v-slot:body-cell-ganho="props">
                <q-td :props="props">
                  <span v-if="props.row.ganho_peso !== null">
                    {{ props.row.ganho_peso.toFixed(1) }} kg
                    <q-icon
                      :name="props.row.ganho_peso > 0 ? 'trending_up' : 'trending_down'"
                      :color="props.row.ganho_peso > 0 ? 'positive' : 'negative'"
                      class="q-ml-xs"
                    />
                  </span>
                  <span v-else class="text-grey">-</span>
                </q-td>
              </template>
            </q-table>
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>
    </q-card>

    <!-- Modal de Visualização -->
    <q-dialog v-model="viewDialog" persistent>
      <q-card style="width: 600px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6">
            {{ viewType === 'crescimento' ? 'Medição de Crescimento' : 'Registro de Saúde' }}
          </div>
        </q-card-section>
        <q-card-section v-if="viewData">
          <q-list>
            <q-item>
              <q-item-section>
                <q-item-label caption>Animal</q-item-label>
                <q-item-label>{{ getAnimalName(viewData.ID_ANIMAL) }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>{{ viewType === 'crescimento' ? 'Data da Medição' : 'Data de Ocorrência' }}</q-item-label>
                <q-item-label>{{ formatDate(viewType === 'crescimento' ? viewData.DATA_MEDICAO : viewData.DATA_OCORRENCIA) }}</q-item-label>
              </q-item-section>
            </q-item>

            <!-- Campos específicos do crescimento -->
            <template v-if="viewType === 'crescimento'">
              <q-item v-if="viewData.PESO">
                <q-item-section>
                  <q-item-label caption>Peso</q-item-label>
                  <q-item-label>{{ viewData.PESO }} kg</q-item-label>
                </q-item-section>
              </q-item>
              
              <q-item v-if="viewData.ALTURA">
                <q-item-section>
                  <q-item-label caption>Altura</q-item-label>
                  <q-item-label>{{ viewData.ALTURA }} cm</q-item-label>
                </q-item-section>
              </q-item>
              
              <q-item v-if="viewData.PERIMETRO_TORACICO">
                <q-item-section>
                  <q-item-label caption>Perímetro Torácico</q-item-label>
                  <q-item-label>{{ viewData.PERIMETRO_TORACICO }} cm</q-item-label>
                </q-item-section>
              </q-item>
              
              <q-item v-if="viewData.COMPRIMENTO_CORPO">
                <q-item-section>
                  <q-item-label caption>Comprimento do Corpo</q-item-label>
                  <q-item-label>{{ viewData.COMPRIMENTO_CORPO }} cm</q-item-label>
                </q-item-section>
              </q-item>
            </template>

            <!-- Campos específicos da saúde -->
            <template v-if="viewType === 'saude'">
              <q-item>
                <q-item-section>
                  <q-item-label caption>Tipo de Registro</q-item-label>
                  <q-item-label>
                    <q-chip
                      :color="getTipoColor(viewData.TIPO_REGISTRO)"
                      text-color="white"
                      dense
                    >
                      {{ viewData.TIPO_REGISTRO }}
                    </q-chip>
                  </q-item-label>
                </q-item-section>
              </q-item>
              
              <q-item v-if="viewData.VETERINARIO_RESPONSAVEL">
                <q-item-section>
                  <q-item-label caption>Veterinário</q-item-label>
                  <q-item-label>{{ viewData.VETERINARIO_RESPONSAVEL }}</q-item-label>
                </q-item-section>
              </q-item>
              
              <q-item v-if="viewData.MEDICAMENTO_APLICADO">
                <q-item-section>
                  <q-item-label caption>Medicamento</q-item-label>
                  <q-item-label>{{ viewData.MEDICAMENTO_APLICADO }}</q-item-label>
                </q-item-section>
              </q-item>
              
              <q-item v-if="viewData.DOSE_APLICADA">
                <q-item-section>
                  <q-item-label caption>Dose</q-item-label>
                  <q-item-label>{{ viewData.DOSE_APLICADA }}</q-item-label>
                </q-item-section>
              </q-item>
              
              <q-item v-if="viewData.PROXIMA_APLICACAO">
                <q-item-section>
                  <q-item-label caption>Próxima Aplicação</q-item-label>
                  <q-item-label>{{ formatDate(viewData.PROXIMA_APLICACAO) }}</q-item-label>
                </q-item-section>
              </q-item>
              
              <q-item v-if="viewData.CUSTO">
                <q-item-section>
                  <q-item-label caption>Custo</q-item-label>
                  <q-item-label>R$ {{ viewData.CUSTO.toFixed(2) }}</q-item-label>
                </q-item-section>
              </q-item>
            </template>

            <q-item v-if="viewData.OBSERVACOES">
              <q-item-section>
                <q-item-label caption>Observações</q-item-label>
                <q-item-label>{{ viewData.OBSERVACOES }}</q-item-label>
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

    <!-- Modal de Cadastro/Edição -->
    <q-dialog v-model="dialog" persistent>
      <q-card style="width: 600px; max-width: 90vw">
        <q-form @submit="saveRecord">
          <q-card-section>
            <div class="text-h6">
              {{ form.ID ? 'Editar' : 'Cadastrar' }} 
              {{ dialogType === 'crescimento' ? 'Medição' : 'Registro de Saúde' }}
            </div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <q-select
              v-model="form.ID_ANIMAL"
              :options="animalOptions"
              label="Animal *"
              :rules="[val => !!val || 'Animal é obrigatório']"
              class="q-mb-sm"
            />
            
            
            <calendario-component
              v-model="form.DATA_MEDICAO"
              v-if="dialogType === 'crescimento'"
              label="Data da Medição *"
              :rules="[val => !!val || 'Data é obrigatória']"
              class="q-mb-sm"
            />
            
            <calendario-component
              v-model="form.DATA_OCORRENCIA"
              v-if="dialogType === 'saude'"
              label="Data de Ocorrência *"
              :rules="[val => !!val || 'Data é obrigatória']"
              class="q-mb-sm"
            />

            <!-- Campos específicos do crescimento -->
            <template v-if="dialogType === 'crescimento'">
              <div class="row q-gutter-md">
                <q-input
                  v-model.number="form.PESO"
                  label="Peso (kg)"
                  type="number"
                  step="0.1"
                  class="col"
                />
                <q-input
                  v-model.number="form.ALTURA"
                  label="Altura (cm)"
                  type="number"
                  step="0.1"
                  class="col"
                />
              </div>
              
              <div class="row q-gutter-md q-mt-sm">
                <q-input
                  v-model.number="form.PERIMETRO_TORACICO"
                  label="Perímetro Torácico (cm)"
                  type="number"
                  step="0.1"
                  class="col"
                />
                <q-input
                  v-model.number="form.COMPRIMENTO_CORPO"
                  label="Comprimento do Corpo (cm)"
                  type="number"
                  step="0.1"
                  class="col"
                />
              </div>
            </template>

            <!-- Campos específicos da saúde -->
            <template v-if="dialogType === 'saude'">
              <q-select
                v-model="form.TIPO_REGISTRO"
                :options="crescimentoStore.tiposRegistro"
                label="Tipo de Registro *"
                :rules="[val => !!val || 'Tipo é obrigatório']"
                class="q-mb-sm"
              />
              
              <q-input
                v-model="form.DESCRICAO"
                label="Descrição"
                class="q-mb-sm"
              />
              
              <q-input
                v-model="form.VETERINARIO_RESPONSAVEL"
                label="Veterinário Responsável"
                class="q-mb-sm"
              />
              
              <div class="row q-gutter-md">
                <q-input
                  v-model="form.MEDICAMENTO_APLICADO"
                  label="Medicamento"
                  class="col"
                />
                <q-input
                  v-model="form.DOSE_APLICADA"
                  label="Dose"
                  class="col"
                />
              </div>
              
              <div class="row q-gutter-md q-mt-sm">
                <calendario-component
                  v-model="form.PROXIMA_APLICACAO"
                  label="Próxima Aplicação"
                  with-time
                  class="col"
                />
                <q-input
                  v-model.number="form.CUSTO"
                  label="Custo (R$)"
                  type="number"
                  step="0.01"
                  class="col"
                />
              </div>
            </template>

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
              :disable="crescimentoStore.loading"
            />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- Modal de Confirmação de Exclusão -->
    <q-dialog v-model="deleteDialog" persistent>
      <q-card>
        <q-card-section>
          <div class="text-h6">Confirmar Exclusão</div>
        </q-card-section>
        <q-card-section>
          Deseja excluir este registro?
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
            @click="performDelete"
            :disable="crescimentoStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '../stores/auth'
import { useCrescimentoStore } from '../stores/crescimento'
import { useAnimalStore } from '../stores/animal'
import CalendarioComponent from '../components/CalendarioComponent.vue'
import { formatDate } from '../utils/dateUtils'

const $q = useQuasar()
const authStore = useAuthStore()
const crescimentoStore = useCrescimentoStore()
const animalStore = useAnimalStore()

// Estado da interface
const activeTab = ref('crescimento')
const dialog = ref(false)
const viewDialog = ref(false)
const deleteDialog = ref(false)
const dialogType = ref('crescimento')
const viewType = ref('crescimento')
const viewData = ref(null)
const recordToDelete = ref(null)
const deleteType = ref('crescimento')

// Opções de animais
const animalOptions = ref([])

// Formulário
const form = ref({
  ID: null,
  ID_ANIMAL: null,
  DATA_MEDICAO: '',
  DATA_OCORRENCIA: '',
  PESO: null,
  ALTURA: null,
  PERIMETRO_TORACICO: null,
  COMPRIMENTO_CORPO: null,
  TIPO_REGISTRO: null,
  DESCRICAO: '',
  VETERINARIO_RESPONSAVEL: '',
  MEDICAMENTO_APLICADO: '',
  DOSE_APLICADA: '',
  PROXIMA_APLICACAO: '',
  CUSTO: null,
  OBSERVACOES: '',
  ID_USUARIO_REGISTRO: authStore.user.ID
})

// Colunas das tabelas
const crescimentoColumns = [
  { name: 'animal', label: 'Animal', field: 'ID_ANIMAL', sortable: false, align: 'left' },
  { name: 'DATA_MEDICAO', label: 'Data', field: 'DATA_MEDICAO', sortable: true, align: 'left' },
  { name: 'PESO', label: 'Peso (kg)', field: 'PESO', sortable: true, align: 'left' },
  { name: 'ALTURA', label: 'Altura (cm)', field: 'ALTURA', sortable: true, align: 'left' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

const saudeColumns = [
  { name: 'animal', label: 'Animal', field: 'ID_ANIMAL', sortable: false, align: 'left' },
  { name: 'DATA_OCORRENCIA', label: 'Data', field: 'DATA_OCORRENCIA', sortable: true, align: 'left' },
  { name: 'tipo', label: 'Tipo', field: 'TIPO_REGISTRO', sortable: true, align: 'center' },
  { name: 'DESCRICAO', label: 'Descrição', field: 'DESCRICAO', sortable: false, align: 'left' },
  { name: 'proxima', label: 'Próxima', field: 'PROXIMA_APLICACAO', sortable: true, align: 'left' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

const estatisticasColumns = [
  { name: 'animal_nome', label: 'Animal', field: 'animal_nome', sortable: true, align: 'left' },
  { name: 'total_medicoes', label: 'Medições', field: 'total_medicoes', sortable: true, align: 'center' },
  { name: 'peso_inicial', label: 'Peso Inicial', field: 'peso_inicial', sortable: true, align: 'left' },
  { name: 'peso_atual', label: 'Peso Atual', field: 'peso_atual', sortable: true, align: 'left' },
  { name: 'ganho', label: 'Ganho', field: 'ganho_peso', sortable: true, align: 'center' },
  { name: 'media_peso', label: 'Média', field: 'media_peso', sortable: true, align: 'left' }
]

// Funções
async function loadAnimals() {
  try {
    await animalStore.loadParentOptions()
    animalOptions.value = [
      ...animalStore.parentOptions.machos,
      ...animalStore.parentOptions.femeas
    ]
  } catch (error) {
    console.error('Erro ao carregar animais:', error)
  }
}

function getAnimalName(animalId) {
  const animal = animalOptions.value.find(a => a.value === animalId)
  return animal ? animal.label : `Animal #${animalId}`
}

async function onFilterChange() {
  if (activeTab.value === 'crescimento') {
    await crescimentoStore.fetchCrescimentos()
  }
}

async function onFilterChangeSaude() {
  await crescimentoStore.fetchSaudes()
}

async function onRequestCrescimento(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  crescimentoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  await crescimentoStore.fetchCrescimentos(props)
}

async function onRequestSaude(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  crescimentoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  await crescimentoStore.fetchSaudes(props)
}

function openDialog(record, type) {
  dialogType.value = type
  
  if (record) {
    form.value = {
      ...record,
      DATA_MEDICAO: record.DATA_MEDICAO ?? '',
      DATA_OCORRENCIA: record.DATA_OCORRENCIA ?? '',
      PROXIMA_APLICACAO: record.PROXIMA_APLICACAO ?? '',
      ID_USUARIO_REGISTRO: authStore.user.ID
    }
  } else {
    form.value = {
      ID: null,
      ID_ANIMAL: null,
      DATA_MEDICAO: '',
      DATA_OCORRENCIA: '',
      PESO: null,
      ALTURA: null,
      PERIMETRO_TORACICO: null,
      COMPRIMENTO_CORPO: null,
      TIPO_REGISTRO: null,
      DESCRICAO: '',
      VETERINARIO_RESPONSAVEL: '',
      MEDICAMENTO_APLICADO: '',
      DOSE_APLICADA: '',
      PROXIMA_APLICACAO: '',
      CUSTO: null,
      OBSERVACOES: '',
      ID_USUARIO_REGISTRO: authStore.user.ID
    }
  }
  dialog.value = true
}

async function saveRecord() {
  try {
    // Extrair apenas o value dos objetos select
    const formData = {
      ...form.value,
      ID_ANIMAL: typeof form.value.ID_ANIMAL === 'object' 
        ? form.value.ID_ANIMAL.value 
        : form.value.ID_ANIMAL
    }

    // Apenas para saúde
    if (dialogType.value === 'saude') {
      formData.TIPO_REGISTRO = typeof form.value.TIPO_REGISTRO === 'object'
        ? form.value.TIPO_REGISTRO.value
        : form.value.TIPO_REGISTRO
      formData.PROXIMA_APLICACAO = form.value.PROXIMA_APLICACAO || null
    }

    if (dialogType.value === 'crescimento') {
      if (formData.ID) {
        await crescimentoStore.updateCrescimento(formData.ID, formData)
        $q.notify({ type: 'positive', message: 'Registro atualizado com sucesso' })
      } else {
        await crescimentoStore.createCrescimento(formData)
        $q.notify({ type: 'positive', message: 'Registro criado com sucesso' })
      }
    } else {
      if (formData.ID) {
        await crescimentoStore.updateSaude(formData.ID, formData)
        $q.notify({ type: 'positive', message: 'Registro atualizado com sucesso' })
      } else {
        await crescimentoStore.createSaude(formData)
        $q.notify({ type: 'positive', message: 'Registro criado com sucesso' })
      }
    }
    dialog.value = false
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

function viewRecord(record, type) {
  viewData.value = record
  viewType.value = type
  viewDialog.value = true
}

function editFromView() {
  viewDialog.value = false
  openDialog(viewData.value, viewType.value)
}

function confirmDelete(record, type) {
  recordToDelete.value = record
  deleteType.value = type
  deleteDialog.value = true
}

async function performDelete() {
  try {
    if (deleteType.value === 'crescimento') {
      await crescimentoStore.deleteCrescimento(recordToDelete.value.ID)
    } else {
      await crescimentoStore.deleteSaude(recordToDelete.value.ID)
    }
    $q.notify({ type: 'positive', message: 'Registro excluído com sucesso' })
    deleteDialog.value = false
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

function filterAnimais(val, update) {
  update(() => {
    // Implementar filtro se necessário
  })
}

function getTipoColor(tipo) {
  const colors = {
    'VACINA': 'primary',
    'VERMIFUGO': 'secondary',
    'MEDICAMENTO': 'accent',
    'EXAME': 'info',
    'CONSULTA': 'positive',
    'CIRURGIA': 'negative',
    'TRATAMENTO': 'warning'
  }
  return colors[tipo] || 'grey'
}

function getIconByTipo(tipo) {
  const icons = {
    'VACINA': 'vaccines',
    'VERMIFUGO': 'medication',
    'MEDICAMENTO': 'healing',
    'EXAME': 'biotech',
    'CONSULTA': 'medical_services',
    'CIRURGIA': 'medical_information',
    'TRATAMENTO': 'local_hospital'
  }
  return icons[tipo] || 'pets'
}

function isVencendo(data) {
  if (!data) return false
  const hoje = new Date()
  const dataAplicacao = new Date(data)
  const diffDays = Math.ceil((dataAplicacao - hoje) / (1000 * 60 * 60 * 24))
  return diffDays <= 7 && diffDays >= 0
}

// function formatDate(dateStr) {
//   if (!dateStr) return 'N/A'
//   return new Date(dateStr).toLocaleDateString('pt-BR')
// }

// function formatDateForInput(dateStr) {
//   if (!dateStr) return ''
//   const date = new Date(dateStr)
//   return date.toISOString().slice(0, 16)
// }

// Watchers para mudança de aba
async function onTabChange() {
  if (activeTab.value === 'crescimento') {
    await crescimentoStore.fetchCrescimentos()
  } else if (activeTab.value === 'saude') {
    await crescimentoStore.fetchSaudes()
  } else if (activeTab.value === 'calendario') {
    await crescimentoStore.fetchProximasAplicacoes()
  } else if (activeTab.value === 'relatorios') {
    await crescimentoStore.fetchEstatisticasCrescimento()
  }
}

// Inicialização
onMounted(async () => {
  await loadAnimals()
  await onTabChange()
})

// Watch da aba ativa
watch(activeTab, onTabChange)
</script>