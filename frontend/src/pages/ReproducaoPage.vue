<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Controle Reprodutivo</div>
      </q-card-section>
      <q-card-section>
        <!-- Filtros -->
        <div class="row q-gutter-md q-mb-md">
          <q-select
            v-model="reproducaoStore.filters.egua_id"
            :options="femeaOptions"
            label="Égua"
            clearable
            use-input
            @filter="filterFemeas"
            @update:model-value="onFilterChange"
            class="col-3"
          />
          <q-select
            v-model="reproducaoStore.filters.resultado"
            :options="reproducaoStore.resultadosDiagnostico"
            label="Resultado"
            clearable
            @update:model-value="onFilterChange"
            class="col-2"
          />
          <q-select
            v-model="reproducaoStore.filters.status"
            :options="reproducaoStore.statusReproducao"
            label="Status"
            clearable
            @update:model-value="onFilterChange"
            class="col-2"
          />
          <q-btn
            color="primary"
            label="Nova Cobertura"
            icon="add"
            @click="openDialog(null)"
          />
        </div>
        
        <!-- Abas -->
        <q-tabs v-model="activeTab" class="q-mb-md">
          <q-tab name="reproducoes" label="Reproduções" />
          <q-tab name="calendario" label="Calendário" />
          <q-tab name="estatisticas" label="Estatísticas" />
        </q-tabs>
        
        <q-tab-panels v-model="activeTab" animated>
          <!-- ABA REPRODUÇÕES -->
          <q-tab-panel name="reproducoes">
            <q-table
              :rows="reproducaoStore.reproducoes"
              :columns="reproducaoColumns"
              row-key="ID"
              :loading="reproducaoStore.loading"
              :pagination="reproducaoStore.pagination"
              @request="onRequest"
              binary-state-sort
            >
              <template v-slot:body-cell-resultado="props">
                <q-td :props="props">
                  <q-chip
                    :color="getResultadoColor(props.row.RESULTADO_DIAGNOSTICO)"
                    text-color="white"
                    dense
                  >
                    {{ getResultadoLabel(props.row.RESULTADO_DIAGNOSTICO) }}
                  </q-chip>
                </q-td>
              </template>
              <template v-slot:body-cell-status="props">
                <q-td :props="props">
                  <q-chip
                    :color="getStatusColor(props.row.STATUS_REPRODUCAO)"
                    text-color="white"
                    dense
                  >
                    {{ getStatusLabel(props.row.STATUS_REPRODUCAO) }}
                  </q-chip>
                </q-td>
              </template>
              <template v-slot:body-cell-gestacao="props">
                <q-td :props="props">
                  <span v-if="props.row.dias_gestacao">
                    {{ props.row.dias_gestacao }} dias
                    <q-linear-progress
                      v-if="props.row.RESULTADO_DIAGNOSTICO === 'POSITIVO'"
                      :value="props.row.dias_gestacao / 340"
                      color="positive"
                      size="xs"
                      class="q-mt-xs"
                    />
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
                    @click="viewRecord(props.row)"
                  />
                  <q-btn
                    flat
                    round
                    color="secondary"
                    icon="history"
                    @click="showHistorico(props.row.ID_EGUA)"
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
          </q-tab-panel>
          
          <!-- ABA CALENDÁRIO -->
          <q-tab-panel name="calendario">
            <div class="text-h6 q-mb-md">Próximos Eventos</div>
            <q-list bordered>
              <q-item
                v-for="evento in reproducaoStore.calendarioEventos"
                :key="`${evento.egua_id}-${evento.evento_tipo}-${evento.data_evento}`"
                clickable
              >
                <q-item-section avatar>
                  <q-icon
                    :name="getIconByEvento(evento.evento_tipo)"
                    :color="getEventoColor(evento.evento_tipo, evento.dias_restantes)"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ evento.egua_nome }}</q-item-label>
                  <q-item-label caption>{{ getEventoDescription(evento.evento_tipo) }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label>{{ formatDate(evento.data_evento) }}</q-item-label>
                  <q-item-label caption>
                    <q-chip
                      :color="evento.dias_restantes <= 3 ? 'negative' : evento.dias_restantes <= 7 ? 'warning' : 'primary'"
                      text-color="white"
                      size="sm"
                    >
                      {{ evento.dias_restantes }} dias
                    </q-chip>
                  </q-item-label>
                </q-item-section>
              </q-item>
              <q-item v-if="!reproducaoStore.calendarioEventos.length">
                <q-item-section>
                  <q-item-label class="text-center text-grey">
                    Nenhum evento nos próximos 60 dias
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-tab-panel>
          
          <!-- ABA ESTATÍSTICAS -->
          <q-tab-panel name="estatisticas">
            <div class="row q-gutter-md" v-if="reproducaoStore.estatisticas">
              <q-card class="col-3">
                <q-card-section class="text-center">
                  <div class="text-h4 text-primary">{{ reproducaoStore.estatisticas.total_coberturas }}</div>
                  <div class="text-subtitle2">Total de Coberturas</div>
                </q-card-section>
              </q-card>
              
              <q-card class="col-3">
                <q-card-section class="text-center">
                  <div class="text-h4 text-positive">{{ reproducaoStore.estatisticas.taxa_sucesso }}%</div>
                  <div class="text-subtitle2">Taxa de Sucesso</div>
                </q-card-section>
              </q-card>
              
              <q-card class="col-3">
                <q-card-section class="text-center">
                  <div class="text-h4 text-secondary">{{ reproducaoStore.estatisticas.gestacoes_ativas }}</div>
                  <div class="text-subtitle2">Gestações Ativas</div>
                </q-card-section>
              </q-card>
              
              <q-card class="col-3">
                <q-card-section class="text-center">
                  <div class="text-h4 text-info">{{ reproducaoStore.estatisticas.partos_realizados }}</div>
                  <div class="text-subtitle2">Partos Realizados</div>
                </q-card-section>
              </q-card>
            </div>
            
            <div class="row q-gutter-md q-mt-md" v-if="reproducaoStore.estatisticas">
              <q-card class="col-6">
                <q-card-section>
                  <div class="text-h6">Resultados dos Diagnósticos</div>
                  <q-list>
                    <q-item>
                      <q-item-section avatar>
                        <q-icon name="check_circle" color="positive" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>Positivos: {{ reproducaoStore.estatisticas.coberturas_positivas }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section avatar>
                        <q-icon name="cancel" color="negative" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>Negativos: {{ reproducaoStore.estatisticas.coberturas_negativas }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section avatar>
                        <q-icon name="hourglass_empty" color="warning" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>Pendentes: {{ reproducaoStore.estatisticas.coberturas_pendentes }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </div>
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>
    </q-card>

    <!-- Modal de Visualização -->
    <q-dialog v-model="viewDialog" persistent>
      <q-card style="width: 600px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6">Detalhes da Reprodução</div>
        </q-card-section>
        <q-card-section v-if="viewData">
          <q-list>
            <q-item>
              <q-item-section>
                <q-item-label caption>Égua</q-item-label>
                <q-item-label>{{ viewData.egua_nome }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Parceiro</q-item-label>
                <q-item-label>{{ viewData.parceiro_nome || 'Não informado' }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Tipo de Cobertura</q-item-label>
                <q-item-label>{{ getTipoLabel(viewData.TIPO_COBERTURA) }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Data da Cobertura</q-item-label>
                <q-item-label>{{ formatDate(viewData.DATA_COBERTURA) }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item v-if="viewData.DATA_DIAGNOSTICO">
              <q-item-section>
                <q-item-label caption>Data do Diagnóstico</q-item-label>
                <q-item-label>{{ formatDate(viewData.DATA_DIAGNOSTICO) }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label caption>Resultado</q-item-label>
                <q-item-label>
                  <q-chip
                    :color="getResultadoColor(viewData.RESULTADO_DIAGNOSTICO)"
                    text-color="white"
                    dense
                  >
                    {{ getResultadoLabel(viewData.RESULTADO_DIAGNOSTICO) }}
                  </q-chip>
                </q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item v-if="viewData.DATA_PARTO_PREVISTA">
              <q-item-section>
                <q-item-label caption>Parto Previsto</q-item-label>
                <q-item-label>{{ formatDate(viewData.DATA_PARTO_PREVISTA) }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item v-if="viewData.DATA_PARTO_REAL">
              <q-item-section>
                <q-item-label caption>Parto Realizado</q-item-label>
                <q-item-label>{{ formatDate(viewData.DATA_PARTO_REAL) }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item v-if="viewData.dias_gestacao">
              <q-item-section>
                <q-item-label caption>Dias de Gestação</q-item-label>
                <q-item-label>{{ viewData.dias_gestacao }} dias</q-item-label>
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
            <div class="text-h6">{{ form.ID ? 'Editar' : 'Cadastrar' }} Reprodução</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <div class="row q-gutter-md">
              <q-select
                v-model="form.ID_EGUA"
                :options="femeaOptions"
                label="Égua *"
                :rules="[val => !!val || 'Égua é obrigatória']"
                class="col-5"
              />
              <q-select
                v-model="form.ID_PARCEIRO"
                :options="machoOptions"
                label="Parceiro"
                clearable
                use-input
                @filter="filterMachos"
                class="col-5"
              />            
            </div>
            
            <div class="row q-gutter-md q-mt-sm">
              <q-select
                v-model="form.TIPO_COBERTURA"
                :options="reproducaoStore.tiposCobertura"
                label="Tipo de Cobertura *"
                :rules="[val => !!val || 'Tipo é obrigatório']"
                class="col-5"
              />
              <calendario-component
                v-model="form.DATA_COBERTURA"
                label="Data da Cobertura *"
                :rules="[val => !!val || 'Data é obrigatória']"
                class="col-5"
              />
            </div>
            
            <div class="row q-gutter-md q-mt-sm">
              <calendario-component
                v-model="form.DATA_DIAGNOSTICO"
                label="Data do Diagnóstico"
                class="col-5"
              />
              <q-select
                v-model="form.RESULTADO_DIAGNOSTICO"
                :options="reproducaoStore.resultadosDiagnostico"
                label="Resultado"
                class="col-5"
              />
            </div>
            
            <div class="row q-gutter-md q-mt-sm">
              <calendario-component
                v-model="form.DATA_PARTO_PREVISTA"
                label="Parto Previsto"
                class="col-5"
              />
              <calendario-component
                v-model="form.DATA_PARTO_REAL"
                label="Parto Realizado"
                class="col-5"
              />
            </div>
            
            <q-select
              v-model="form.STATUS_REPRODUCAO"
              :options="reproducaoStore.statusReproducao"
              label="Status"
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
              :disable="reproducaoStore.loading"
            />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- Modal de Histórico -->
    <q-dialog v-model="historicoDialog" persistent>
      <q-card style="width: 800px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6">Histórico Reprodutivo</div>
          <div v-if="reproducaoStore.historicoEgua" class="text-subtitle2">
            Taxa de sucesso: {{ reproducaoStore.historicoEgua.taxa_sucesso }}% 
            ({{ reproducaoStore.historicoEgua.partos_realizados }}/{{ reproducaoStore.historicoEgua.total_coberturas }})
          </div>
        </q-card-section>
        <q-card-section>
          <q-timeline v-if="reproducaoStore.historicoEgua?.reproducoes?.length">
            <q-timeline-entry
              v-for="rep in reproducaoStore.historicoEgua.reproducoes"
              :key="rep.ID"
              :title="getTipoLabel(rep.TIPO_COBERTURA)"
              :subtitle="formatDate(rep.DATA_COBERTURA)"
              :icon="getIconByResultado(rep.RESULTADO_DIAGNOSTICO)"
              :color="getResultadoColor(rep.RESULTADO_DIAGNOSTICO)"
            >
              <div>
                <strong>Parceiro:</strong> {{ rep.parceiro_nome || 'Não informado' }}<br>
                <strong>Resultado:</strong> {{ getResultadoLabel(rep.RESULTADO_DIAGNOSTICO) }}
                <div v-if="rep.DATA_PARTO_REAL" class="q-mt-xs">
                  <strong>Parto:</strong> {{ formatDate(rep.DATA_PARTO_REAL) }}
                </div>
                <div v-if="rep.dias_gestacao" class="q-mt-xs">
                  <strong>Gestação:</strong> {{ rep.dias_gestacao }} dias
                </div>
              </div>
            </q-timeline-entry>
          </q-timeline>
          <div v-else class="text-center text-grey">
            Nenhum histórico reprodutivo encontrado.
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
          Deseja excluir este registro de reprodução?
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
            :disable="reproducaoStore.loading"
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
import { useReproducaoStore } from '../stores/reproducao'
import { useAnimalStore } from '../stores/animal'
import CalendarioComponent from '../components/CalendarioComponent.vue'
import { formatDate, prepareFormData } from '../utils/dateUtils'

const $q = useQuasar()
const authStore = useAuthStore()
const reproducaoStore = useReproducaoStore()
const animalStore = useAnimalStore()

// Estado da interface
const activeTab = ref('reproducoes')
const dialog = ref(false)
const viewDialog = ref(false)
const historicoDialog = ref(false)
const deleteDialog = ref(false)
const viewData = ref(null)
const recordToDelete = ref(null)

// Opções
const femeaOptions = ref([])
const machoOptions = ref([])

// Formulário
const form = ref({
  ID: null,
  ID_EGUA: null,
  ID_PARCEIRO: null,
  TIPO_COBERTURA: null,
  DATA_COBERTURA: '',
  DATA_DIAGNOSTICO: '',
  RESULTADO_DIAGNOSTICO: { value: 'PENDENTE', label: 'Pendente' },
  STATUS_REPRODUCAO: { value: 'A', label: 'Ativo' },  
  DATA_PARTO_PREVISTA: '',
  DATA_PARTO_REAL: '',
  OBSERVACOES: '',
  ID_USUARIO_REGISTRO: authStore.user.ID
})

// Colunas da tabela
const reproducaoColumns = [
  { name: 'egua_nome', label: 'Égua', field: 'egua_nome', sortable: true, align: 'left' },
  { name: 'parceiro_nome', label: 'Parceiro', field: 'parceiro_nome', sortable: true, align: 'left' },
  { name: 'DATA_COBERTURA', label: 'Cobertura', field: 'DATA_COBERTURA', sortable: true, align: 'left' },
  { name: 'TIPO_COBERTURA', label: 'Tipo', field: 'TIPO_COBERTURA', sortable: true, align: 'center' },
  { name: 'resultado', label: 'Resultado', field: 'RESULTADO_DIAGNOSTICO', sortable: true, align: 'center' },
  { name: 'gestacao', label: 'Gestação', field: 'dias_gestacao', sortable: false, align: 'center' },
  { name: 'status', label: 'Status', field: 'STATUS_REPRODUCAO', sortable: true, align: 'center' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

// Funções
async function loadOptions() {
  try {
    await animalStore.loadParentOptions()
    femeaOptions.value = animalStore.parentOptions.femeas
    machoOptions.value = animalStore.parentOptions.machos
  } catch (error) {
    console.error('Erro ao carregar opções:', error)
  }
}

async function onFilterChange() {
  await reproducaoStore.fetchReproducoes()
}

async function onRequest(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  reproducaoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  await reproducaoStore.fetchReproducoes(props)
}

function openDialog(record) {
  if (record) {
    const egua = femeaOptions.value.find(f => f.value === record.ID_EGUA)
    const parceiro = machoOptions.value.find(m => m.value === record.ID_PARCEIRO)
    const tipo = reproducaoStore.tiposCobertura.find(t => t.value === record.TIPO_COBERTURA)
    const resultado = reproducaoStore.resultadosDiagnostico.find(r => r.value === record.RESULTADO_DIAGNOSTICO)
    const status = reproducaoStore.statusReproducao.find(s => s.value === record.STATUS_REPRODUCAO)
    
    form.value = {
      ...record,
      ID_EGUA: egua || record.ID_EGUA,
      ID_PARCEIRO: parceiro || null,
      TIPO_COBERTURA: tipo || record.TIPO_COBERTURA,
      RESULTADO_DIAGNOSTICO: resultado || record.RESULTADO_DIAGNOSTICO,
      STATUS_REPRODUCAO: status || record.STATUS_REPRODUCAO,
      ID_USUARIO_REGISTRO: authStore.user.ID
    }
  } else {
    form.value = {
      ID: null,
      ID_EGUA: null,
      ID_PARCEIRO: null,
      TIPO_COBERTURA: null,
      DATA_COBERTURA: '',
      DATA_DIAGNOSTICO: '',
      RESULTADO_DIAGNOSTICO: { value: 'PENDENTE', label: 'Pendente' },
      STATUS_REPRODUCAO: { value: 'A', label: 'Ativo' },      
      DATA_PARTO_PREVISTA: '',
      DATA_PARTO_REAL: '',
      OBSERVACOES: '',
      ID_USUARIO_REGISTRO: authStore.user.ID
    }
  }
  dialog.value = true
}

async function saveRecord() {
  try {
    const dateFields = ['DATA_COBERTURA', 'DATA_DIAGNOSTICO', 'DATA_PARTO_PREVISTA', 'DATA_PARTO_REAL']
    const formData = prepareFormData(form.value, dateFields)
    
    if (formData.ID) {
      await reproducaoStore.updateReproducao(formData.ID, formData)
      $q.notify({ type: 'positive', message: 'Reprodução atualizada com sucesso' })
    } else {
      await reproducaoStore.createReproducao(formData)
      $q.notify({ type: 'positive', message: 'Reprodução criada com sucesso' })
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

async function showHistorico(eguaId) {
  try {
    await reproducaoStore.fetchHistoricoEgua(eguaId)
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
    await reproducaoStore.deleteReproducao(recordToDelete.value.ID)
    $q.notify({ type: 'positive', message: 'Reprodução excluída com sucesso' })
    deleteDialog.value = false
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

function filterFemeas(val, update) {
  update(() => {
    if (val === '') {
      femeaOptions.value = animalStore.parentOptions.femeas
    } else {
      const needle = val.toLowerCase()
      femeaOptions.value = animalStore.parentOptions.femeas.filter(
        v => v.label.toLowerCase().indexOf(needle) > -1
      )
    }
  })
}

function filterMachos(val, update) {
  update(() => {
    if (val === '') {
      machoOptions.value = animalStore.parentOptions.machos
    } else {
      const needle = val.toLowerCase()
      machoOptions.value = animalStore.parentOptions.machos.filter(
        v => v.label.toLowerCase().indexOf(needle) > -1
      )
    }
  })
}

// Funções de formatação e cores
function getTipoLabel(tipo) {
  const tipos = {
    'NATURAL': 'Natural',
    'IA': 'Inseminação Artificial',
    'TE': 'Transferência de Embrião'
  }
  return tipos[tipo] || tipo
}

function getResultadoLabel(resultado) {
  const resultados = {
    'POSITIVO': 'Positivo',
    'NEGATIVO': 'Negativo',
    'PENDENTE': 'Pendente'
  }
  return resultados[resultado] || resultado
}

function getStatusLabel(status) {
  const statusMap = {
    'A': 'Ativo',
    'C': 'Concluído',
    'F': 'Falhado'
  }
  return statusMap[status] || status
}

function getResultadoColor(resultado) {
  const colors = {
    'POSITIVO': 'positive',
    'NEGATIVO': 'negative',
    'PENDENTE': 'warning'
  }
  return colors[resultado] || 'grey'
}

function getStatusColor(status) {
  const colors = {
    'A': 'primary',
    'C': 'positive',
    'F': 'negative'
  }
  return colors[status] || 'grey'
}

function getIconByEvento(evento) {
  const icons = {
    'DIAGNOSTICO': 'medical_services',
    'PARTO_PREVISTO': 'child_care'
  }
  return icons[evento] || 'event'
}

function getIconByResultado(resultado) {
  const icons = {
    'POSITIVO': 'check_circle',
    'NEGATIVO': 'cancel',
    'PENDENTE': 'hourglass_empty'
  }
  return icons[resultado] || 'help'
}

function getEventoColor(evento, diasRestantes) {
  if (diasRestantes <= 3) return 'negative'
  if (diasRestantes <= 7) return 'warning'
  return 'primary'
}

function getEventoDescription(evento) {
  const descriptions = {
    'DIAGNOSTICO': 'Diagnóstico de gestação',
    'PARTO_PREVISTO': 'Parto previsto'
  }
  return descriptions[evento] || evento
}

async function onTabChange() {
  if (activeTab.value === 'reproducoes') {
    await reproducaoStore.fetchReproducoes()
  } else if (activeTab.value === 'calendario') {
    await reproducaoStore.fetchCalendarioEventos()
  } else if (activeTab.value === 'estatisticas') {
    await reproducaoStore.fetchEstatisticas()
  }
}

// Inicialização
onMounted(async () => {
  await loadOptions()
  await onTabChange()
})

watch(activeTab, onTabChange)
</script>