<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md text-primary">
      <q-icon name="trending_up" class="q-mr-sm" />
      Controle de Crescimento
    </div>

    <q-card class="q-mb-md">
      <q-card-section>
        <!-- Filtros -->
        <div class="col-12 q-mb-md">
          <q-card flat bordered class="q-pa-md">
            <div class="row q-gutter-md">
              <div class="col-md-3 col-12">
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
              </div>  
              <div class="col-md-3 col-12">
                <calendario-component
                  v-model="crescimentoStore.filters.data_inicio"
                  label="Data Início"
                  @update:model-value="onFilterChange"
                  class="col-2"
                />
              </div>  
              <div class="col-md-3 col-12">
                <calendario-component
                  v-model="crescimentoStore.filters.data_fim"
                  label="Data Fim"
                  @update:model-value="onFilterChange"
                  class="col-2"
                />
              </div>  
            </div>
          </q-card>
        </div>
        
        <!-- Estatísticas Rápidas -->
        <div class="row q-gutter-md q-mb-md">
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-primary">{{ crescimentoStore.totalMedicoes }}</div>
              <div class="text-caption">Total Medições</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-secondary">{{ crescimentoStore.animaisComMedicoes }}</div>
              <div class="text-caption">Animais Monitorados</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-positive">{{ crescimentoStore.mediaGanhoPeso }} kg</div>
              <div class="text-caption">Ganho Médio</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-accent">{{ estatisticasGerais.length }}</div>
              <div class="text-caption">Com Histórico</div>
            </q-card-section>
          </q-card>
        </div>
        
        <!-- Abas -->
        <q-tabs v-model="activeTab" class="q-mb-md">
          <q-tab name="medicoes" label="Medições" />
          <q-tab name="estatisticas" label="Estatísticas" />
          <q-tab name="comparacao" label="Comparação" />
          <q-tab name="graficos" label="Gráficos" />
        </q-tabs>
        
        <q-tab-panels v-model="activeTab" animated>
          <!-- ABA MEDIÇÕES -->
          <q-tab-panel name="medicoes">
            <div class="row q-gutter-md q-mb-md">
              <q-btn
                color="primary"
                label="Nova Medição"
                icon="add"
                @click="openDialog(null)"
              />
              <q-btn
                color="secondary"
                label="Exportar Dados"
                icon="download"
                @click="exportarDados"
              />
            </div>

            <q-table
              :rows="crescimentoStore.crescimentos"
              :columns="medicaoColumns"
              row-key="ID"
              :loading="crescimentoStore.loading"
              :pagination="crescimentoStore.pagination"
              @request="onRequest"
              binary-state-sort
            >
              <template v-slot:body-cell-animal="props">
                <q-td :props="props">
                  <div class="text-weight-medium">{{ props.row.animal_nome }}</div>
                </q-td>
              </template>
              
              <template v-slot:body-cell-peso="props">
                <q-td :props="props">
                  <div class="row items-center">
                    <span class="text-weight-medium">
                      {{ crescimentoStore.formatarMedida(props.row.PESO, 'kg') }}
                    </span>
                    <q-chip 
                      v-if="props.row.ganho_peso"
                      :color="props.row.ganho_peso > 0 ? 'positive' : 'negative'"
                      text-color="white"
                      size="sm"
                      class="q-ml-sm"
                    >
                      {{ crescimentoStore.formatarGanho(props.row.ganho_peso) }}
                    </q-chip>
                  </div>
                </q-td>
              </template>
              
              <template v-slot:body-cell-altura="props">
                <q-td :props="props">
                  {{ crescimentoStore.formatarMedida(props.row.ALTURA, 'cm') }}
                </q-td>
              </template>
              
              <template v-slot:body-cell-medidas="props">
                <q-td :props="props">
                  <div class="text-caption">
                    <div v-if="props.row.CIRCUNFERENCIA_CANELA">
                      Canela: {{ crescimentoStore.formatarMedida(props.row.CIRCUNFERENCIA_CANELA, 'cm') }}
                    </div>
                    <div v-if="props.row.CIRCUNFERENCIA_TORACICA">
                      Tórax: {{ crescimentoStore.formatarMedida(props.row.CIRCUNFERENCIA_TORACICA, 'cm') }}
                    </div>
                    <div v-if="props.row.COMPRIMENTO_CORPO">
                      Corpo: {{ crescimentoStore.formatarMedida(props.row.COMPRIMENTO_CORPO, 'cm') }}
                    </div>
                  </div>
                </q-td>
              </template>
              
              <template v-slot:body-cell-dias="props">
                <q-td :props="props">
                  <span v-if="props.row.dias_desde_ultima">
                    {{ props.row.dias_desde_ultima }} dias
                  </span>
                  <span v-else class="text-grey">Primeira</span>
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
                    color="primary"
                    icon="edit"
                    @click="openDialog(props.row)"
                  />
                  <q-btn
                    flat
                    round
                    color="accent"
                    icon="timeline"
                    @click="verHistoricoAnimal(props.row.ID_ANIMAL)"
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
          
          <!-- ABA ESTATÍSTICAS -->
          <q-tab-panel name="estatisticas">
            <div class="row q-gutter-md q-mb-md">
              <q-btn
                color="info"
                label="Atualizar Estatísticas"
                icon="refresh"
                @click="loadEstatisticas"
              />
              <q-select
                v-model="periodoEstatisticas"
                :options="opcoesPeriodiodo"
                label="Período"
                @update:model-value="loadEstatisticas"
                class="col-2"
              />
            </div>
            
            <q-table
              :rows="estatisticasGerais"
              :columns="estatisticasColumns"
              row-key="animal_id"
              flat
              :pagination="{ rowsPerPage: 0 }"
            >
              <template v-slot:body-cell-ganho_total="props">
                <q-td :props="props">
                  <span v-if="props.row.ganho_peso_total" 
                        :class="props.row.ganho_peso_total > 0 ? 'text-positive' : 'text-negative'">
                    {{ crescimentoStore.formatarGanho(props.row.ganho_peso_total) }}
                  </span>
                  <span v-else class="text-grey">-</span>
                </q-td>
              </template>
              
              <template v-slot:body-cell-ganho_mes="props">
                <q-td :props="props">
                  <span v-if="props.row.ganho_peso_medio_mes">
                    {{ crescimentoStore.formatarMedida(props.row.ganho_peso_medio_mes, 'kg/mês') }}
                  </span>
                  <span v-else class="text-grey">-</span>
                </q-td>
              </template>
              
              <template v-slot:body-cell-acoes_est="props">
                <q-td :props="props">
                  <q-btn
                    flat
                    round
                    color="primary"
                    icon="timeline"
                    @click="verHistoricoAnimal(props.row.animal_id)"
                  />
                </q-td>
              </template>
            </q-table>
          </q-tab-panel>
          
          <!-- ABA COMPARAÇÃO -->
          <q-tab-panel name="comparacao">
            <div class="row q-gutter-md q-mb-md">
              <q-btn
                color="info"
                label="Atualizar Comparação"
                icon="refresh"
                @click="loadComparacao"
              />
            </div>
            
            <q-table
              :rows="comparacaoMedidas"
              :columns="comparacaoColumns"
              row-key="animal_id"
              flat
              :pagination="{ rowsPerPage: 0 }"
            >
              <template v-slot:body-cell-idade="props">
                <q-td :props="props">
                  <span v-if="props.row.idade_meses">
                    {{ props.row.idade_meses }} meses
                  </span>
                  <span v-else class="text-grey">-</span>
                </q-td>
              </template>
              
              <template v-slot:body-cell-peso_comp="props">
                <q-td :props="props">
                  <div v-if="props.row.peso_atual">
                    {{ crescimentoStore.formatarMedida(props.row.peso_atual, 'kg') }}
                    <q-chip 
                      :color="crescimentoStore.getClassificacaoColor(props.row.classificacao)"
                      text-color="white"
                      size="sm"
                      class="q-ml-sm"
                    >
                      {{ props.row.classificacao }}
                    </q-chip>
                  </div>
                  <span v-else class="text-grey">-</span>
                </q-td>
              </template>
              
              <template v-slot:body-cell-altura_comp="props">
                <q-td :props="props">
                  {{ crescimentoStore.formatarMedida(props.row.altura_atual, 'cm') }}
                </q-td>
              </template>
            </q-table>
          </q-tab-panel>
          
          <!-- ABA GRÁFICOS -->
          <q-tab-panel name="graficos">
            <div class="row q-gutter-md q-mb-md">
              <q-select
                v-model="animalSelecionadoGrafico"
                :options="animalOptions"
                label="Selecionar Animal"
                @update:model-value="loadGraficos"
                class="col-3"
              />
            </div>
            
            <div v-if="animalSelecionadoGrafico" class="row q-gutter-md">
              <q-card class="col-6">
                <q-card-section>
                  <div class="text-h6">Evolução do Peso</div>
                  <crescimento-chart 
                    :dados="dadosGraficoPeso"
                    tipo="peso"
                    height="300px"
                  />
                </q-card-section>
              </q-card>
              
              <q-card class="col-6">
                <q-card-section>
                  <div class="text-h6">Evolução da Altura</div>
                  <crescimento-chart 
                    :dados="dadosGraficoAltura"
                    tipo="altura"
                    height="300px"
                  />
                </q-card-section>
              </q-card>
            </div>
            
            <div v-else class="text-center q-pa-xl">
              <q-icon name="show_chart" size="4rem" color="grey" />
              <div class="text-h6 text-grey q-mt-md">
                Selecione um animal para visualizar os gráficos
              </div>
            </div>
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>
    </q-card>
    <!-- Modal de Cadastro/Edição -->
    <q-dialog v-model="dialog" persistent>
    <q-card style="width: 700px; max-width: 90vw">
        <q-form @submit="saveRecord">
        <q-card-section>
            <div class="text-h6">
            {{ form.ID ? 'Editar' : 'Nova' }} Medição de Crescimento
            </div>
        </q-card-section>
        <q-card-section class="q-pt-none">
            <crescimento-form v-model="form" :animal-options="animalOptions" />
        </q-card-section>
        <q-card-actions align="right">
            <q-btn flat label="Cancelar" color="grey" @click="dialog = false" />
            <q-btn 
            type="submit" 
            color="primary" 
            label="Salvar" 
            :loading="crescimentoStore.loading" 
            />
        </q-card-actions>
        </q-form>
    </q-card>
    </q-dialog>

    <!-- Modal de Visualização -->
    <q-dialog v-model="viewDialog" persistent>
    <q-card style="width: 600px; max-width: 90vw">
        <q-card-section>
        <div class="text-h6">Detalhes da Medição</div>
        </q-card-section>
        <q-card-section v-if="viewData">
        <div class="row q-gutter-md">
            <div class="col-6">
            <q-list>
                <q-item>
                <q-item-section>
                    <q-item-label overline>Animal</q-item-label>
                    <q-item-label>{{ viewData.animal_nome }}</q-item-label>
                </q-item-section>
                </q-item>
                <q-item>
                <q-item-section>
                    <q-item-label overline>Data da Medição</q-item-label>
                    <q-item-label>{{ viewData.DATA_MEDICAO }}</q-item-label>
                </q-item-section>
                </q-item>
                <q-item v-if="viewData.PESO">
                <q-item-section>
                    <q-item-label overline>Peso</q-item-label>
                    <q-item-label>{{ crescimentoStore.formatarMedida(viewData.PESO, 'kg') }}</q-item-label>
                </q-item-section>
                </q-item>
                <q-item v-if="viewData.ALTURA">
                <q-item-section>
                    <q-item-label overline>Altura</q-item-label>
                    <q-item-label>{{ crescimentoStore.formatarMedida(viewData.ALTURA, 'cm') }}</q-item-label>
                </q-item-section>
                </q-item>
            </q-list>
            </div>
            <div class="col-6">
            <q-list>
                <q-item v-if="viewData.CIRCUNFERENCIA_CANELA">
                <q-item-section>
                    <q-item-label overline>Circunferência da Canela</q-item-label>
                    <q-item-label>{{ crescimentoStore.formatarMedida(viewData.CIRCUNFERENCIA_CANELA, 'cm') }}</q-item-label>
                </q-item-section>
                </q-item>
                <q-item v-if="viewData.CIRCUNFERENCIA_TORACICA">
                <q-item-section>
                    <q-item-label overline>Circunferência Torácica</q-item-label>
                    <q-item-label>{{ crescimentoStore.formatarMedida(viewData.CIRCUNFERENCIA_TORACICA, 'cm') }}</q-item-label>
                </q-item-section>
                </q-item>
                <q-item v-if="viewData.COMPRIMENTO_CORPO">
                <q-item-section>
                    <q-item-label overline>Comprimento do Corpo</q-item-label>
                    <q-item-label>{{ crescimentoStore.formatarMedida(viewData.COMPRIMENTO_CORPO, 'cm') }}</q-item-label>
                </q-item-section>
                </q-item>
                <q-item v-if="viewData.ganho_peso">
                <q-item-section>
                    <q-item-label overline>Ganho de Peso</q-item-label>
                    <q-item-label :class="viewData.ganho_peso > 0 ? 'text-positive' : 'text-negative'">
                    {{ crescimentoStore.formatarGanho(viewData.ganho_peso) }}
                    </q-item-label>
                </q-item-section>
                </q-item>
            </q-list>
            </div>
        </div>
        
        <div v-if="viewData.OBSERVACOES" class="q-mt-md">
            <q-item>
            <q-item-section>
                <q-item-label overline>Observações</q-item-label>
                <q-item-label>{{ viewData.OBSERVACOES }}</q-item-label>
            </q-item-section>
            </q-item>
        </div>
        </q-card-section>
        <q-card-actions align="right">
        <q-btn flat label="Editar" color="primary" @click="editFromView" />
        <q-btn flat label="Fechar" color="grey" @click="viewDialog = false" />
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
        <div>Deseja excluir esta medição?</div>
        <div v-if="recordToDelete" class="text-caption text-grey q-mt-sm">
            Animal: {{ recordToDelete.animal_nome }} - Data: {{ recordToDelete.DATA_MEDICAO }}
        </div>
        </q-card-section>
        <q-card-actions align="right">
        <q-btn flat label="Cancelar" color="grey" @click="deleteDialog = false" />
        <q-btn 
            color="negative" 
            label="Excluir" 
            @click="performDelete" 
            :loading="crescimentoStore.loading" 
        />
        </q-card-actions>
    </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>

import { ref, onMounted, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'stores/auth'
import { useCrescimentoStore } from 'stores/crescimento'
import { useAnimalStore } from 'stores/animal'
import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'
import CrescimentoChart from 'components/crescimento/CrescimentoChart.vue'
import CrescimentoForm from 'components/crescimento/CrescimentoForm.vue'
import { prepareFormData } from '../utils/dateUtils'

const $q = useQuasar()
const router = useRouter()
const authStore = useAuthStore()
const crescimentoStore = useCrescimentoStore()
const animalStore = useAnimalStore()

// Estado da interface
const activeTab = ref('medicoes')
const dialog = ref(false)
const viewDialog = ref(false)
const deleteDialog = ref(false)
const viewData = ref(null)
const recordToDelete = ref(null)
const animalSelecionadoGrafico = ref(null)
const periodoEstatisticas = ref(12)

// Dados computados
const animalOptions = ref([])
const estatisticasGerais = ref([])
const comparacaoMedidas = ref([])

// Opções para filtros
const opcoesPeriodiodo = [
  { value: 3, label: '3 meses' },
  { value: 6, label: '6 meses' },
  { value: 12, label: '12 meses' },
  { value: 24, label: '24 meses' }
]

// Computed
const dadosGraficoPeso = computed(() => {
  if (!animalSelecionadoGrafico.value?.value) return []
  return crescimentoStore.dadosGraficoPeso(animalSelecionadoGrafico.value.value)
})

const dadosGraficoAltura = computed(() => {
  if (!animalSelecionadoGrafico.value?.value) return []
  return crescimentoStore.dadosGraficoAltura(animalSelecionadoGrafico.value.value)
})

// Colunas das tabelas
const medicaoColumns = [
  { name: 'DATA_MEDICAO', label: 'Data', field: 'DATA_MEDICAO', sortable: true, align: 'left' },
  { name: 'animal', label: 'Animal', field: 'animal_nome', sortable: true, align: 'left' },
  { name: 'peso', label: 'Peso', field: 'PESO', sortable: true, align: 'left' },
  { name: 'altura', label: 'Altura', field: 'ALTURA', sortable: true, align: 'left' },
  { name: 'medidas', label: 'Outras Medidas', field: 'medidas', align: 'left' },
  { name: 'dias', label: 'Intervalo', field: 'dias_desde_ultima', sortable: true, align: 'center' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

const estatisticasColumns = [
  { name: 'animal_nome', label: 'Animal', field: 'animal_nome', align: 'left' },
  { name: 'total_medicoes', label: 'Medições', field: 'total_medicoes', align: 'center' },
  { name: 'peso_inicial', label: 'Peso Inicial', field: 'peso_inicial', align: 'right' },
  { name: 'peso_atual', label: 'Peso Atual', field: 'peso_atual', align: 'right' },
  { name: 'ganho_total', label: 'Ganho Total', field: 'ganho_peso_total', align: 'right' },
  { name: 'ganho_mes', label: 'Ganho/Mês', field: 'ganho_peso_medio_mes', align: 'right' },
  { name: 'acoes_est', label: 'Ações', field: 'acoes', align: 'center' }
]

const comparacaoColumns = [
  { name: 'animal_nome', label: 'Animal', field: 'animal_nome', align: 'left' },
  { name: 'idade', label: 'Idade', field: 'idade_meses', align: 'center' },
  { name: 'peso_comp', label: 'Peso Atual', field: 'peso_atual', align: 'right' },
  { name: 'altura_comp', label: 'Altura Atual', field: 'altura_atual', align: 'right' }
]

// Formulário
const form = ref({})

// Funções principais
async function loadOptions() {
  try {
    await animalStore.fetchAnimais({ limit: 100 })
    animalOptions.value = animalStore.animais.map(a => ({
      value: a.ID,
      label: a.NOME
    }))
  } catch (error) {
    console.error('Erro ao carregar opções:', error)
  }
}

async function onFilterChange() {
  await crescimentoStore.fetchCrescimentos()
}

async function onRequest(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  crescimentoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  await crescimentoStore.fetchCrescimentos(props)
}

// CRUD Functions
function openDialog(record) {
  initializeForm(record)
  dialog.value = true
}

function initializeForm(record) {
  form.value = record ? {
    ...record,
    ID_ANIMAL: record.ID_ANIMAL ? { value: record.ID_ANIMAL, label: record.animal_nome } : null,
  } : {
    ID: null,
    ID_ANIMAL: null,
    DATA_MEDICAO: '',
    PESO: null,
    ALTURA: null,
    CIRCUNFERENCIA_CANELA: null,
    CIRCUNFERENCIA_TORACICA: null,
    COMPRIMENTO_CORPO: null,
    OBSERVACOES: '',
    ID_USUARIO_REGISTRO: authStore.user.ID
  }
}

async function saveRecord() {
  try {
    const dateFields = ['DATA_MEDICAO']
    const formData = prepareFormData(form.value, dateFields)
    
    // Validar formulário
    const validacao = crescimentoStore.validarFormulario(formData)
    if (!validacao.valido) {
      $q.notify({
        type: 'negative',
        message: validacao.erros.join(', ')
      })
      return
    }

    if (formData.ID) {
      await crescimentoStore.updateCrescimento(formData.ID, formData)
      $q.notify({ type: 'positive', message: 'Medição atualizada com sucesso' })
    } else {
      await crescimentoStore.createCrescimento(formData)
      $q.notify({ type: 'positive', message: 'Medição registrada com sucesso' })
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

function confirmDelete(record) {
  recordToDelete.value = record
  deleteDialog.value = true
}

async function performDelete() {
  try {
    await crescimentoStore.deleteCrescimento(recordToDelete.value.ID)
    $q.notify({ type: 'positive', message: 'Medição excluída com sucesso' })
    deleteDialog.value = false
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

// Navegação e histórico
function verHistoricoAnimal(animalId) {
  router.push(`/crescimento/animal/${animalId}`)
}

// Relatórios e estatísticas
async function loadEstatisticas() {
  try {
    estatisticasGerais.value = await crescimentoStore.fetchEstatisticasGerais(periodoEstatisticas.value)
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

async function loadComparacao() {
  try {
    comparacaoMedidas.value = await crescimentoStore.fetchComparacaoMedidas()
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

async function loadGraficos() {
  if (!animalSelecionadoGrafico.value?.value) return
  
  try {
    await crescimentoStore.fetchHistoricoAnimal(animalSelecionadoGrafico.value.value)
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

// Exportação
function exportarDados() {
  try {
    const dados = crescimentoStore.prepararDadosExportacao()
    
    if (dados.length === 0) {
      $q.notify({ type: 'warning', message: 'Nenhum dado para exportar' })
      return
    }
    
    // Converter para CSV
    const headers = Object.keys(dados[0])
    const csvContent = [
      headers.join(','),
      ...dados.map(row => headers.map(header => `"${row[header]}"`).join(','))
    ].join('\n')
    
    // Download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `crescimento_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    $q.notify({ type: 'positive', message: 'Dados exportados com sucesso' })
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao exportar dados' })
  }
}

// Filtros
function filterAnimais(val, update) {
  update(() => {
    if (val === '') {
      animalOptions.value = animalStore.animais.map(a => ({ value: a.ID, label: a.NOME }))
    } else {
      const needle = val.toLowerCase()
      const allAnimais = animalStore.animais.map(a => ({ value: a.ID, label: a.NOME }))
      animalOptions.value = allAnimais.filter(v => v.label.toLowerCase().indexOf(needle) > -1)
    }
  })
}

// Watchers para mudança de aba
async function onTabChange() {
  if (activeTab.value === 'medicoes') {
    await crescimentoStore.fetchCrescimentos()
  } else if (activeTab.value === 'estatisticas') {
    await loadEstatisticas()
  } else if (activeTab.value === 'comparacao') {
    await loadComparacao()
  }
}

// Inicialização
onMounted(async () => {
  await loadOptions()
  await onTabChange()
})

watch(activeTab, onTabChange)
</script>