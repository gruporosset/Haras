<template>
  <q-page class="q-pa-md">

    <div class="text-h5 q-mb-md text-primary">
      <q-icon name="swap_horiz" class="q-mr-sm" />
      Movimentações de Animais
    </div>

    <q-card>
      <q-card-section>
        <!-- Filtros -->
          <div class="col-12">
            <q-card flat bordered class="q-pa-md">
              <div class="row q-gutter-md q-mb-md">
                <div class="col-md-3 col-12">
                  <q-select
                    v-model="movimentacaoStore.filters.animal_id"
                    :options="animalOptions"
                    label="Animal"
                    clearable
                    use-input
                    @filter="filterAnimais"
                    @update:model-value="onFilterChange"
                    class="col-3"
                  />
                </div>
                <div class="col-md-3 col-12">
                  <q-select
                    v-model="movimentacaoStore.filters.tipo_movimentacao"
                    :options="movimentacaoStore.tiposMovimentacao"
                    label="Tipo"
                    clearable
                    @update:model-value="onFilterChange"
                    class="col-2"
                  />
                </div>
                <div class="col-md-3 col-12">
                  <q-select
                    v-model="movimentacaoStore.filters.terreno_id"
                    :options="terrenoOptions"
                    label="Terreno"
                    clearable
                    use-input
                    @filter="filterTerrenos"
                    @update:model-value="onFilterChange"
                    class="col-3"
                  />
                </div>
              </div>
            </q-card>
          </div>
        
        <!-- Abas -->
        <q-tabs v-model="activeTab" class="q-mb-md">
          <q-tab name="movimentacoes" label="Movimentações" />
          <q-tab name="localizacoes" label="Localizações" />
        </q-tabs>
        
        <q-tab-panels v-model="activeTab" animated>
          <!-- ABA MOVIMENTAÇÕES -->
          <q-tab-panel name="movimentacoes">
            <div class="row q-gutter-md">
              <div class="col-12">
                <q-btn
                  color="primary"
                  label="Nova Movimentação"
                  icon="add"
                  @click="openDialog(null)"
                />
              </div>

              <div class="col-12">
                <q-card flat bordered>
                  <q-table
                    :rows="movimentacaoStore.movimentacoes"
                    :columns="movimentacaoColumns"
                    row-key="ID"
                    :loading="movimentacaoStore.loading"
                    :pagination="movimentacaoStore.pagination"
                    @request="onRequest"
                    binary-state-sort
                  >
                    <template v-slot:body-cell-tipo="props">
                      <q-td :props="props">
                        <q-chip
                          :color="getTipoColor(props.row.TIPO_MOVIMENTACAO)"
                          text-color="white"
                          dense
                        >
                          {{ props.row.TIPO_MOVIMENTACAO }}
                        </q-chip>
                      </q-td>
                    </template>
                    <template v-slot:body-cell-origem="props">
                      <q-td :props="props">
                        {{ props.row.terreno_origem_nome || props.row.ORIGEM_EXTERNA || '-' }}
                      </q-td>
                    </template>
                    <template v-slot:body-cell-destino="props">
                      <q-td :props="props">
                        {{ props.row.terreno_destino_nome || props.row.DESTINO_EXTERNO || '-' }}
                      </q-td>
                    </template>
                    <template v-slot:body-cell-acoes="props">
                      <q-td :props="props">
                        <q-btn
                          flat
                          round
                          color="info"
                          icon="visibility"
                          @click="viewRecord(props.row)"
                        />
                        <q-btn
                          flat
                          round
                          color="secondary"
                          icon="history"
                          @click="showHistorico(props.row.ID_ANIMAL)"
                        />
                        <q-btn
                          flat
                          round
                          color="primary"
                          icon="edit"
                          @click="openDialog(props.row)"
                        />
                        <q-btn
                          flat
                          round
                          color="negative"
                          icon="delete"
                          @click="confirmDelete(props.row)"
                        />
                      </q-td>
                    </template>
                  </q-table>
                </q-card>
              </div>
            </div>
          </q-tab-panel>
          
          <!-- ABA LOCALIZAÇÕES -->
          <q-tab-panel name="localizacoes">
            <q-table
              :rows="movimentacaoStore.localizacoes"
              :columns="localizacaoColumns"
              row-key="animal_id"
              :loading="movimentacaoStore.loading"
              flat
            >
              <template v-slot:body-cell-localizacao="props">
                <q-td :props="props">
                  {{ props.row.terreno_atual || props.row.local_externo || 'Não informado' }}
                </q-td>
              </template>
              <template v-slot:body-cell-acoes="props">
                <q-td :props="props">
                  <q-btn
                    flat
                    round
                    color="primary"
                    icon="history"
                    @click="showHistorico(props.row.animal_id)"
                    label="Histórico"
                  />
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
          <div class="text-h6">Detalhes da Movimentação</div>
        </q-card-section>
        <q-card-section v-if="viewData">
          <q-list>
            <q-item>
              <q-item-section>
                <q-item-label caption>Animal</q-item-label>
                <q-item-label>{{ viewData.animal_nome }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Tipo</q-item-label>
                <q-item-label>
                  <q-chip
                    :color="getTipoColor(viewData.TIPO_MOVIMENTACAO)"
                    text-color="white"
                    dense
                  >
                    {{ viewData.TIPO_MOVIMENTACAO }}
                  </q-chip>
                </q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Data da Movimentação</q-item-label>
                <q-item-label>{{ formatDate(viewData.DATA_MOVIMENTACAO) }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Origem</q-item-label>
                <q-item-label>{{ viewData.terreno_origem_nome || viewData.ORIGEM_EXTERNA || 'Não informado' }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Destino</q-item-label>
                <q-item-label>{{ viewData.terreno_destino_nome || viewData.DESTINO_EXTERNO || 'Não informado' }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item v-if="viewData.MOTIVO">
              <q-item-section>
                <q-item-label caption>Motivo</q-item-label>
                <q-item-label>{{ viewData.MOTIVO }}</q-item-label>
              </q-item-section>
            </q-item>
            
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
      <q-card style="width: 700px; max-width: 90vw">
        <q-form @submit="saveRecord">
          <q-card-section>
            <div class="text-h6">{{ form.ID ? 'Editar' : 'Cadastrar' }} Movimentação</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <div class="row q-gutter-md">
              <q-select
                v-model="form.ID_ANIMAL"
                :options="animalOptions"
                label="Animal *"
                :rules="[val => !!val || 'Animal é obrigatório']"
                class="col-5"
              />
              <q-select
                v-model="form.TIPO_MOVIMENTACAO"
                :options="movimentacaoStore.tiposMovimentacao"
                label="Tipo *"
                :rules="[val => !!val || 'Tipo é obrigatório']"
                class="col-5"
              />
            </div>
            
            <calendario-component
              v-model="form.DATA_MOVIMENTACAO"
              label="Data da Movimentação *"
              :rules="[val => !!val || 'Data é obrigatória']"
              class="q-mt-sm"
            />
            
            <div class="text-subtitle2 q-mt-md q-mb-sm">Origem</div>
            <div class="row q-gutter-md">
              <q-select
                v-model="form.ID_TERRENO_ORIGEM"
                :options="terrenoOptions"
                label="Terreno de Origem"
                clearable
                class="col"
              />
              <q-input
                v-model="form.ORIGEM_EXTERNA"
                label="Origem Externa"
                class="col"
              />
            </div>
            
            <div class="text-subtitle2 q-mt-md q-mb-sm">Destino</div>
            <div class="row q-gutter-md">
              <q-select
                v-model="form.ID_TERRENO_DESTINO"
                :options="terrenoOptions"
                label="Terreno de Destino"
                clearable
                class="col"
              />
              <q-input
                v-model="form.DESTINO_EXTERNO"
                label="Destino Externo"
                class="col"
              />
            </div>
            
            <q-input
              v-model="form.MOTIVO"
              label="Motivo"
              class="q-mt-sm"
            />
            
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
              :disable="movimentacaoStore.loading"
            />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- Modal de Histórico -->
    <q-dialog v-model="historicoDialog" persistent>
      <q-card style="width: 800px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6">Histórico de Movimentações</div>
          <div v-if="movimentacaoStore.historicoAnimal" class="text-subtitle2">
            Localização atual: {{ movimentacaoStore.historicoAnimal.localizacao_atual }}
          </div>
        </q-card-section>
        <q-card-section>
          <q-timeline v-if="movimentacaoStore.historicoAnimal?.movimentacoes?.length">
            <q-timeline-entry
              v-for="mov in movimentacaoStore.historicoAnimal.movimentacoes"
              :key="mov.ID"
              :title="mov.TIPO_MOVIMENTACAO"
              :subtitle="formatDate(mov.DATA_MOVIMENTACAO)"
              :icon="getIconByTipo(mov.TIPO_MOVIMENTACAO)"
              :color="getTipoColor(mov.TIPO_MOVIMENTACAO)"
            >
              <div>
                <strong>De:</strong> {{ mov.terreno_origem_nome || mov.ORIGEM_EXTERNA || 'Não informado' }}<br>
                <strong>Para:</strong> {{ mov.terreno_destino_nome || mov.DESTINO_EXTERNO || 'Não informado' }}
                <div v-if="mov.MOTIVO" class="q-mt-xs">
                  <strong>Motivo:</strong> {{ mov.MOTIVO }}
                </div>
              </div>
            </q-timeline-entry>
          </q-timeline>
          <div v-else class="text-center text-grey">
            Nenhuma movimentação encontrada para este animal.
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            label="Fechar"
            color="gray"
            @click="historicoDialog = false"
          />
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
          Deseja excluir esta movimentação?
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
            :disable="movimentacaoStore.loading"
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
import { useMovimentacaoStore } from '../stores/movimentacao'
import { useAnimalStore } from '../stores/animal'
import { useTerrenoStore } from '../stores/terreno'
import CalendarioComponent from '../components/CalendarioComponent.vue'
import { formatDate, convertToISO } from '../utils/dateUtils'

const $q = useQuasar()
const authStore = useAuthStore()
const movimentacaoStore = useMovimentacaoStore()
const animalStore = useAnimalStore()
const terrenoStore = useTerrenoStore()

// Estado da interface
const activeTab = ref('movimentacoes')
const dialog = ref(false)
const viewDialog = ref(false)
const historicoDialog = ref(false)
const deleteDialog = ref(false)
const viewData = ref(null)
const recordToDelete = ref(null)

// Opções
const animalOptions = ref([])
const terrenoOptions = ref([])

// Formulário
const form = ref({
  ID: null,
  ID_ANIMAL: null,
  TIPO_MOVIMENTACAO: null,
  DATA_MOVIMENTACAO: '',
  ID_TERRENO_ORIGEM: null,
  ID_TERRENO_DESTINO: null,
  ORIGEM_EXTERNA: '',
  DESTINO_EXTERNO: '',
  MOTIVO: '',
  OBSERVACOES: '',
  ID_USUARIO_REGISTRO: authStore.user.ID
})

// Colunas das tabelas
const movimentacaoColumns = [
  { name: 'animal_nome', label: 'Animal', field: 'animal_nome', sortable: true, align: 'left' },
  { name: 'DATA_MOVIMENTACAO', label: 'Data', field: 'DATA_MOVIMENTACAO', sortable: true, align: 'left' },
  { name: 'tipo', label: 'Tipo', field: 'TIPO_MOVIMENTACAO', sortable: true, align: 'center' },
  { name: 'origem', label: 'Origem', field: 'origem', sortable: false, align: 'left' },
  { name: 'destino', label: 'Destino', field: 'destino', sortable: false, align: 'left' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

const localizacaoColumns = [
  { name: 'animal_nome', label: 'Animal', field: 'animal_nome', sortable: true, align: 'left' },
  { name: 'localizacao', label: 'Localização Atual', field: 'localizacao', sortable: false, align: 'left' },
  { name: 'data_ultima_movimentacao', label: 'Última Movimentação', field: 'data_ultima_movimentacao', sortable: true, align: 'left' },
  { name: 'tipo_ultima_movimentacao', label: 'Tipo', field: 'tipo_ultima_movimentacao', sortable: true, align: 'center' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

// Funções
async function loadOptions() {
  try {
    await animalStore.loadParentOptions()
    animalOptions.value = [
      ...animalStore.parentOptions.machos,
      ...animalStore.parentOptions.femeas
    ]
    
    await terrenoStore.fetchTerrenos({ limit: 100 })
    terrenoOptions.value = terrenoStore.terrenos.map(t => ({
      value: t.ID,
      label: t.NOME
    }))
  } catch (error) {
    console.error('Erro ao carregar opções:', error)
  }
}

async function onFilterChange() {
  await movimentacaoStore.fetchMovimentacoes()
}

async function onRequest(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  movimentacaoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  await movimentacaoStore.fetchMovimentacoes(props)
}

function openDialog(record) {
  if (record) {
    // Encontrar objetos completos para os selects
    const terrenoOrigem = terrenoOptions.value.find(t => t.value === record.ID_TERRENO_ORIGEM)
    const terrenoDestino = terrenoOptions.value.find(t => t.value === record.ID_TERRENO_DESTINO)
    const animal = animalOptions.value.find(a => a.value === record.ID_ANIMAL)
    const tipo = movimentacaoStore.tiposMovimentacao.find(t => t.value === record.TIPO_MOVIMENTACAO)
    
    form.value = {
      ...record,
      ID_ANIMAL: animal || record.ID_ANIMAL,
      TIPO_MOVIMENTACAO: tipo || record.TIPO_MOVIMENTACAO,
      ID_TERRENO_ORIGEM: terrenoOrigem || null,
      ID_TERRENO_DESTINO: terrenoDestino || null,
      DATA_MOVIMENTACAO: record.DATA_MOVIMENTACAO ?? '',
      ID_USUARIO_REGISTRO: authStore.user.ID
    }
  } else {
    form.value = {
      ID: null,
      ID_ANIMAL: null,
      TIPO_MOVIMENTACAO: null,
      DATA_MOVIMENTACAO: '',
      ID_TERRENO_ORIGEM: null,
      ID_TERRENO_DESTINO: null,
      ORIGEM_EXTERNA: '',
      DESTINO_EXTERNO: '',
      MOTIVO: '',
      OBSERVACOES: '',
      ID_USUARIO_REGISTRO: authStore.user.ID
    }
  }
  dialog.value = true
}

async function saveRecord() {
  try {
    const formData = {
      ...form.value,
      ID_ANIMAL: typeof form.value.ID_ANIMAL === 'object' 
        ? form.value.ID_ANIMAL?.value 
        : form.value.ID_ANIMAL,
      TIPO_MOVIMENTACAO: typeof form.value.TIPO_MOVIMENTACAO === 'object'
        ? form.value.TIPO_MOVIMENTACAO?.value
        : form.value.TIPO_MOVIMENTACAO,
      ID_TERRENO_ORIGEM: typeof form.value.ID_TERRENO_ORIGEM === 'object'
        ? form.value.ID_TERRENO_ORIGEM?.value
        : form.value.ID_TERRENO_ORIGEM,
      ID_TERRENO_DESTINO: typeof form.value.ID_TERRENO_DESTINO === 'object'
        ? form.value.ID_TERRENO_DESTINO?.value
        : form.value.ID_TERRENO_DESTINO,
      // Converter strings vazias para null
      ORIGEM_EXTERNA: form.value.ORIGEM_EXTERNA || null,
      DESTINO_EXTERNO: form.value.DESTINO_EXTERNO || null,
      MOTIVO: form.value.MOTIVO || null,
      DATA_MOVIMENTACAO: convertToISO(form.value.DATA_MOVIMENTACAO)
    }

    if (formData.ID) {
      await movimentacaoStore.updateMovimentacao(formData.ID, formData)
      $q.notify({ type: 'positive', message: 'Movimentação atualizada com sucesso' })
    } else {
      await movimentacaoStore.createMovimentacao(formData)
      $q.notify({ type: 'positive', message: 'Movimentação criada com sucesso' })
    }
    dialog.value = false
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

function viewRecord(record) {
  viewData.value = record
  viewDialog.value = true
}

function editFromView() {
  viewDialog.value = false
  openDialog(viewData.value)
}

async function showHistorico(animalId) {
  try {
    await movimentacaoStore.fetchHistoricoAnimal(animalId)
    historicoDialog.value = true
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

function confirmDelete(record) {
  recordToDelete.value = record
  deleteDialog.value = true
}

async function performDelete() {
  try {
    await movimentacaoStore.deleteMovimentacao(recordToDelete.value.ID)
    $q.notify({ type: 'positive', message: 'Movimentação excluída com sucesso' })
    deleteDialog.value = false
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

function filterAnimais(val, update) {
  update(() => {
    if (val === '') {
      animalOptions.value = [...animalStore.parentOptions.machos, ...animalStore.parentOptions.femeas]
    } else {
      const needle = val.toLowerCase()
      const allAnimals = [...animalStore.parentOptions.machos, ...animalStore.parentOptions.femeas]
      animalOptions.value = allAnimals.filter(v => v.label.toLowerCase().indexOf(needle) > -1)
    }
  })
}

function filterTerrenos(val, update) {
  update(() => {
    if (val === '') {
      terrenoOptions.value = terrenoStore.terrenos.map(t => ({ value: t.ID, label: t.NOME }))
    } else {
      const needle = val.toLowerCase()
      const allTerrenos = terrenoStore.terrenos.map(t => ({ value: t.ID, label: t.NOME }))
      terrenoOptions.value = allTerrenos.filter(v => v.label.toLowerCase().indexOf(needle) > -1)
    }
  })
}

function getTipoColor(tipo) {
  const colors = {
    'TRANSFERENCIA': 'primary',
    'ENTRADA': 'positive',
    'SAIDA': 'warning',
    'VENDA': 'info',
    'EMPRESTIMO': 'secondary',
    'RETORNO': 'accent'
  }
  return colors[tipo] || 'grey'
}

function getIconByTipo(tipo) {
  const icons = {
    'TRANSFERENCIA': 'swap_horiz',
    'ENTRADA': 'input',
    'SAIDA': 'output',
    'VENDA': 'attach_money',
    'EMPRESTIMO': 'handshake',
    'RETORNO': 'keyboard_return'
  }
  return icons[tipo] || 'move_to_inbox'
}

async function onTabChange() {
  if (activeTab.value === 'movimentacoes') {
    await movimentacaoStore.fetchMovimentacoes()
  } else if (activeTab.value === 'localizacoes') {
    await movimentacaoStore.fetchLocalizacoes()
  }
}

// Inicialização
onMounted(async () => {
  await loadOptions()
  await onTabChange()
})

watch(activeTab, onTabChange)
</script>