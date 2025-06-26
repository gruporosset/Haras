<template>
  <div class="aplicacoes-terrenos-container">
    <!-- HEADER COM FILTROS -->
    <q-card flat class="q-mb-md">
      <q-card-section>
        <div class="row q-gutter-md items-end">
          <div class="col-md-2 col-12">
            <q-select
              v-model="filtros.terreno_id"
              :options="terrenoOptions"
              label="Terreno"
              dense
              clearable
              use-input
              @filter="filterTerrenos"
              @update:model-value="onFilterChange"
            />
          </div>
          
          <div class="col-md-2 col-12">
            <q-select
              v-model="filtros.produto_id"
              :options="produtoOptions"
              label="Produto"
              dense
              clearable
              use-input
              @filter="filterProdutos"
              @update:model-value="onFilterChange"
            />
          </div>
          
          <div class="col-md-2 col-12">
            <q-select
              v-model="filtros.tipo_manejo"
              :options="manejoStore.tiposManejo"
              label="Tipo de Manejo"
              dense
              clearable
              @update:model-value="onFilterChange"
            />
          </div>
          
          <div class="col-md-2 col-12">
            <calendario-component
              v-model="filtros.data_inicio"
              label="Data Início"
              @update:model-value="onFilterChange"
            />
          </div>
          
          <div class="col-md-2 col-12">
            <calendario-component
              v-model="filtros.data_fim"
              label="Data Fim"
              @update:model-value="onFilterChange"
            />
          </div>
          
        </div>

        <div class="row q-gutter-md items-end q-mt-sm">
          <div class="col-auto">
            <q-btn
              color="primary"
              icon="add"
              label="Nova Aplicação"
              @click="openDialog()"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- CARDS DE RESUMO -->
    <div class="row q-gutter-md q-mb-md justify-center">
      <div class="col-md-3 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6 text-primary">
              <q-icon name="agriculture" class="q-mr-sm" />
              {{ estatisticas.totalAplicacoes }}
            </div>
            <div class="text-subtitle2">Total Aplicações</div>
            <div class="text-caption text-grey-6">
              No período filtrado
            </div>
          </q-card-section>
        </q-card>
      </div>
      
      <div class="col-md-3 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6 text-green">
              <q-icon name="landscape" class="q-mr-sm" />
              {{ estatisticas.terrenosManejados }}
            </div>
            <div class="text-subtitle2">Terrenos Manejados</div>
            <div class="text-caption text-grey-6">
              {{ estatisticas.areaTotal.toFixed(1) }} hectares
            </div>
          </q-card-section>
        </q-card>
      </div>
      
      <div class="col-md-3 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6 text-orange">
              <q-icon name="monetization_on" class="q-mr-sm" />
              {{ manejoStore.formatarMoeda(estatisticas.custoTotal) }}
            </div>
            <div class="text-subtitle2">Custo Total</div>
            <div class="text-caption text-grey-6">
              Média: {{ manejoStore.formatarMoeda(estatisticas.custoMedio) }}
            </div>
          </q-card-section>
        </q-card>
      </div>
      
      <div class="col-md-2 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6 text-purple">
              <q-icon name="schedule" class="q-mr-sm" />
              {{ estatisticas.terrenosBloqueados }}
            </div>
            <div class="text-subtitle2">Terrenos em Carência</div>
            <div class="text-caption text-grey-6">
              {{ estatisticas.proximasLiberacoes }} liberam esta semana
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- ALERTAS DE CARÊNCIA -->
    <q-card 
      v-if="terrenosCarencia.length > 0" 
      flat 
      class="bg-warning-1 q-mb-md"
    >
      <q-card-section>
        <div class="text-h6 text-warning-8 q-mb-sm">
          <q-icon name="warning" class="q-mr-sm" />
          Terrenos em Carência ({{ terrenosCarencia.length }})
        </div>
        <div class="row q-gutter-sm">
          <q-chip
            v-for="terreno in terrenosCarencia.slice(0, 5)"
            :key="terreno.terreno_id"
            color="warning"
            text-color="white"
            size="sm"
            @click="viewCarencia(terreno)"
            clickable
          >
            {{ terreno.terreno_nome }} - {{ terreno.dias_para_liberacao }} dias
          </q-chip>
          <q-btn
            v-if="terrenosCarencia.length > 5"
            flat
            color="warning"
            size="sm"
            :label="`+${terrenosCarencia.length - 5} mais`"
            @click="showAllCarencias"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- TABELA DE APLICAÇÕES -->
    <q-table
      :rows="manejoStore.aplicacoes"
      :columns="columns"
      row-key="ID"
      :loading="manejoStore.loading"
      :pagination="manejoStore.pagination"
      @request="onRequest"
      binary-state-sort
      flat
      class="aplicacoes-table"
    >
      <template v-slot:body-cell-TIPO_MANEJO="props">
        <q-td :props="props">
          <q-chip
            :color="getCorTipoManejo(props.value)"
            text-color="white"
            size="sm"
            :icon="getIconeTipoManejo(props.value)"
          >
            {{ manejoStore.getManejoLabel(props.value) }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-QUANTIDADE="props">
        <q-td :props="props">
          <div class="text-weight-medium">
            {{ props.value?.toLocaleString('pt-BR') }}
          </div>
          <div class="text-caption text-grey-6">
            {{ getUnidadeAplicacao(props.row) }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-dose_hectare="props">
        <q-td :props="props">
          <div v-if="props.row.DOSE_HECTARE" class="text-weight-medium">
            {{ props.row.DOSE_HECTARE?.toLocaleString('pt-BR') }}
          </div>
          <div v-else class="text-grey-6">-</div>
          <div v-if="props.row.AREA_APLICADA" class="text-caption text-grey-6">
            {{ props.row.AREA_APLICADA }} HA
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-custo="props">
        <q-td :props="props">
          <div v-if="props.row.CUSTO_TOTAL" class="text-weight-medium">
            {{ manejoStore.formatarMoeda(props.row.CUSTO_TOTAL) }}
          </div>
          <div v-else class="text-grey-6">-</div>
          <div v-if="props.row.CUSTO_PRODUTO" class="text-caption text-grey-6">
            Produto: {{ manejoStore.formatarMoeda(props.row.CUSTO_PRODUTO) }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-status_carencia="props">
        <q-td :props="props">
          <q-chip
            :color="getCorCarencia(props.row)"
            text-color="white"
            size="sm"
            :icon="getIconeCarencia(props.row)"
          >
            {{ getStatusCarencia(props.row) }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-DATA_APLICACAO="props">
        <q-td :props="props">
          {{ formatarData(props.value) }}
        </q-td>
      </template>

      <template v-slot:body-cell-acoes="props">
        <q-td :props="props">
          <q-btn-group flat>
            <q-btn
              flat
              round
              color="primary"
              icon="visibility"
              size="sm"
              @click="viewAplicacao(props.row)"
            >
              <q-tooltip>Visualizar</q-tooltip>
            </q-btn>
            <q-btn
              flat
              round
              color="warning"
              icon="edit"
              size="sm"
              @click="openDialog(props.row)"
            >
              <q-tooltip>Editar</q-tooltip>
            </q-btn>
            <q-btn
              flat
              round
              color="negative"
              icon="delete"
              size="sm"
              @click="confirmDelete(props.row)"
            >
              <q-tooltip>Excluir</q-tooltip>
            </q-btn>
          </q-btn-group>
        </q-td>
      </template>
    </q-table>

    <!-- DIALOG FORMULÁRIO -->
    <q-dialog v-model="dialog" persistent>
      <q-card style="min-width: 700px">
        <q-card-section>
          <div class="text-h6">
            {{ form.ID ? 'Editar Aplicação' : 'Nova Aplicação' }}
          </div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="submitForm" class="q-gutter-md">
            <!-- Linha 1: Terreno, Produto, Tipo -->
            <div class="row q-gutter-md">
              <q-select
                v-model="form.ID_TERRENO"
                :options="terrenoOptionsDialog"
                label="Terreno *"
                :rules="[val => !!val || 'Terreno é obrigatório']"
                use-input
                @filter="filterTerrenosDialog"
                @update:model-value="onTerrenoSelected"
                class="col-3"
              />
              <q-select
                v-model="form.ID_PRODUTO"
                :options="produtoOptionsDialog"
                label="Produto *"
                :rules="[val => !!val || 'Produto é obrigatório']"
                use-input
                @filter="filterProdutosDialog"
                @update:model-value="onProdutoSelected"
                class="col-4"
              />
              <q-select
                v-model="form.TIPO_MANEJO"
                :options="manejoStore.tiposManejo"
                label="Tipo de Manejo *"
                :rules="[val => !!val || 'Tipo é obrigatório']"
                class="col-4"
              />
            </div>

            <!-- Linha 2: Data, Quantidade, Unidade -->
            <div class="row q-gutter-md">
              <calendario-component
                v-model="form.DATA_APLICACAO"
                label="Data da Aplicação *"
                :rules="[val => !!val || 'Data é obrigatória']"
                class="col-3"
              />
              <q-input
                v-model.number="form.QUANTIDADE"
                label="Quantidade *"
                type="number"
                step="0.01"
                min="0.01"
                :max="estoqueDisponivel"
                :suffix="unidadeSelecionada"
                :rules="[
                  val => val > 0 || 'Quantidade deve ser maior que 0',
                  val => val <= estoqueDisponivel || `Máximo disponível: ${estoqueDisponivel}`
                ]"
                class="col-3"
              />
              <q-input
                v-model="form.UNIDADE_MEDIDA"
                label="Unidade de Medida"
                :hint="unidadeSelecionada ? `Produto: ${unidadeSelecionada}` : ''"
                class="col-3"
              />
              <q-input
                v-model.number="form.DOSE_HECTARE"
                label="Dose por HA"
                type="number"
                step="0.01"
                min="0"
                :suffix="`${unidadeSelecionada}/HA`"
                class="col-2"
              />
            </div>

            <!-- Linha 3: Área, Equipamento -->
            <div class="row q-gutter-md">
              <q-input
                v-model.number="form.AREA_APLICADA"
                label="Área Aplicada (HA)"
                type="number"
                step="0.01"
                min="0"
                :max="areaTerrenoSelecionado"
                :hint="areaTerrenoSelecionado ? `Terreno: ${areaTerrenoSelecionado} HA` : ''"
                class="col-3"
              />
              <q-input
                v-model="form.EQUIPAMENTO_UTILIZADO"
                label="Equipamento Utilizado"
                placeholder="Ex: Pulverizador, Espalhador, etc."
                class="col-4"
              />
              <q-input
                v-model="form.CONDICOES_CLIMATICAS"
                label="Condições Climáticas"
                placeholder="Ex: Ensolarado, vento fraco"
                class="col-4"
              />
            </div>

            <!-- Linha 4: Custos -->
            <div class="row q-gutter-md">
              <q-input
                v-model.number="form.CUSTO_PRODUTO"
                label="Custo do Produto"
                type="number"
                step="0.01"
                min="0"
                prefix="R$"
                :hint="custoCalculado ? `Estimado: ${manejoStore.formatarMoeda(custoCalculado)}` : ''"
                class="col-3"
              />
              <q-input
                v-model.number="form.CUSTO_APLICACAO"
                label="Custo da Aplicação"
                type="number"
                step="0.01"
                min="0"
                prefix="R$"
                placeholder="Mão de obra, combustível, etc."
                class="col-3"
              />
              <q-input
                v-model.number="form.CUSTO_TOTAL"
                label="Custo Total"
                type="number"
                step="0.01"
                min="0"
                prefix="R$"
                :hint="custoTotalCalculado ? `Calculado: ${manejoStore.formatarMoeda(custoTotalCalculado)}` : ''"
                class="col-3"
              />
              <q-input
                v-model.number="form.PERIODO_CARENCIA"
                label="Carência (dias)"
                type="number"
                min="0"
                :hint="carenciaRecomendada ? `Recomendado: ${carenciaRecomendada} dias` : ''"
                class="col-2"
              />
            </div>

            <!-- Observações -->
            <q-input
              v-model="form.OBSERVACOES"
              label="Observações"
              type="textarea"
              rows="3"
            />

            <!-- Card de Resumo -->
            <q-card flat bordered class="bg-blue-1">
              <q-card-section class="q-pa-sm">
                <div class="text-weight-medium text-blue-8">
                  <q-icon name="info" class="q-mr-sm" />
                  Resumo da Aplicação
                </div>
                <div class="row q-mt-xs text-body2">
                  <div class="col-6">
                    <div><strong>Estoque Disponível:</strong> {{ estoqueDisponivel }} {{ unidadeSelecionada }}</div>
                    <div><strong>Restará:</strong> {{ (estoqueDisponivel - (form.QUANTIDADE || 0)).toLocaleString('pt-BR') }} {{ unidadeSelecionada }}</div>
                  </div>
                  <div class="col-6">
                    <div v-if="dataLiberacao"><strong>Liberação:</strong> {{ dataLiberacao }}</div>
                    <div v-if="custoTotalCalculado"><strong>Custo Total:</strong> {{ manejoStore.formatarMoeda(custoTotalCalculado) }}</div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" @click="dialog = false" />
          <q-btn
            label="Salvar"
            color="primary"
            @click="submitForm"
            :loading="manejoStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG VISUALIZAÇÃO -->
    <q-dialog v-model="viewDialog">
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">Detalhes da Aplicação</div>
        </q-card-section>

        <q-card-section>
          <q-list>
            <q-item>
              <q-item-section>
                <q-item-label caption>Terreno</q-item-label>
                <q-item-label>{{ viewData?.terreno_nome }}</q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Produto</q-item-label>
                <q-item-label>{{ viewData?.produto_nome }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Tipo de Manejo</q-item-label>
                <q-item-label>
                  <q-chip :color="getCorTipoManejo(viewData?.TIPO_MANEJO)" text-color="white" size="sm">
                    {{ manejoStore.getManejoLabel(viewData?.TIPO_MANEJO) }}
                  </q-chip>
                </q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Data da Aplicação</q-item-label>
                <q-item-label>{{ formatarData(viewData?.DATA_APLICACAO) }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Quantidade Aplicada</q-item-label>
                <q-item-label>{{ viewData?.QUANTIDADE?.toLocaleString('pt-BR') }} {{ viewData?.UNIDADE_MEDIDA }}</q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Dose por HA</q-item-label>
                <q-item-label>{{ viewData?.DOSE_HECTARE?.toLocaleString('pt-BR') || '-' }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.AREA_APLICADA">
              <q-item-section>
                <q-item-label caption>Área Aplicada</q-item-label>
                <q-item-label>{{ viewData.AREA_APLICADA }} HA</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.CUSTO_TOTAL">
              <q-item-section>
                <q-item-label caption>Custo Total</q-item-label>
                <q-item-label>{{ manejoStore.formatarMoeda(viewData.CUSTO_TOTAL) }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.PERIODO_CARENCIA">
              <q-item-section>
                <q-item-label caption>Período de Carência</q-item-label>
                <q-item-label>{{ viewData.PERIODO_CARENCIA }} dias</q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Data de Liberação</q-item-label>
                <q-item-label>{{ formatarData(viewData?.DATA_LIBERACAO) }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.EQUIPAMENTO_UTILIZADO">
              <q-item-section>
                <q-item-label caption>Equipamento Utilizado</q-item-label>
                <q-item-label>{{ viewData.EQUIPAMENTO_UTILIZADO }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.CONDICOES_CLIMATICAS">
              <q-item-section>
                <q-item-label caption>Condições Climáticas</q-item-label>
                <q-item-label>{{ viewData.CONDICOES_CLIMATICAS }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.OBSERVACOES">
              <q-item-section>
                <q-item-label caption>Observações</q-item-label>
                <q-item-label>{{ viewData.OBSERVACOES }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Fechar" color="grey" @click="viewDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG CONFIRMAÇÃO DELETE -->
    <q-dialog v-model="deleteDialog" persistent>
      <q-card>
        <q-card-section>
          <div class="text-h6">Confirmar Exclusão</div>
        </q-card-section>
        <q-card-section>
          Tem certeza que deseja excluir a aplicação de <strong>{{ recordToDelete?.produto_nome }}</strong> 
          no terreno <strong>{{ recordToDelete?.terreno_nome }}</strong>?
          <div class="text-caption text-warning q-mt-sm">
            <q-icon name="warning" /> O estoque do produto será restaurado automaticamente.
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" @click="deleteDialog = false" />
          <q-btn
            label="Excluir"
            color="negative"
            @click="deleteAplicacao"
            :loading="manejoStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useManejoStore } from 'stores/manejo'
import { useTerrenoStore } from 'stores/terreno'
import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

// Composables
const $q = useQuasar()
const manejoStore = useManejoStore()
const terrenoStore = useTerrenoStore()

// Estado reativo
const dialog = ref(false)
const viewDialog = ref(false)
const deleteDialog = ref(false)
const viewData = ref(null)
const recordToDelete = ref(null)

// Filtros
const filtros = ref({
  terreno_id: null,
  produto_id: null,
  tipo_manejo: null,
  data_inicio: '',
  data_fim: ''
})

// Formulário
const form = ref({})

// Opções
const terrenoOptions = ref([])
const terrenoOptionsDialog = ref([])
const produtoOptions = ref([])
const produtoOptionsDialog = ref([])

// Dados de carência
const terrenosCarencia = ref([])

// Computed
const unidadeSelecionada = computed(() => {
  if (!form.value.ID_PRODUTO?.unidade_medida) return ''
  return form.value.ID_PRODUTO.unidade_medida
})

const estoqueDisponivel = computed(() => {
  if (!form.value.ID_PRODUTO?.estoque_atual) return 0
  return form.value.ID_PRODUTO.estoque_atual
})

const areaTerrenoSelecionado = computed(() => {
  if (!form.value.ID_TERRENO?.area_hectares) return 0
  return form.value.ID_TERRENO.area_hectares
})

const carenciaRecomendada = computed(() => {
  if (!form.value.ID_PRODUTO?.periodo_carencia) return null
  return form.value.ID_PRODUTO.periodo_carencia
})

const custoCalculado = computed(() => {
  const quantidade = form.value.QUANTIDADE || 0
  const preco = form.value.ID_PRODUTO?.preco_unitario || 0
  return quantidade * preco
})

const custoTotalCalculado = computed(() => {
  const produto = form.value.CUSTO_PRODUTO || custoCalculado.value || 0
  const aplicacao = form.value.CUSTO_APLICACAO || 0
  return produto + aplicacao
})

const dataLiberacao = computed(() => {
  if (!form.value.DATA_APLICACAO || !form.value.PERIODO_CARENCIA) return null
  const dataAplicacao = new Date(form.value.DATA_APLICACAO)
  const liberacao = new Date(dataAplicacao)
  liberacao.setDate(liberacao.getDate() + (form.value.PERIODO_CARENCIA || 0))
  return liberacao.toLocaleDateString('pt-BR')
})

const estatisticas = computed(() => {
  const aplicacoes = manejoStore.aplicacoes
  const terrenos = new Set(aplicacoes.map(a => a.ID_TERRENO))
  const custos = aplicacoes.reduce((sum, a) => sum + (a.CUSTO_TOTAL || 0), 0)
  const areas = aplicacoes.reduce((sum, a) => sum + (a.AREA_APLICADA || 0), 0)
  
  return {
    totalAplicacoes: aplicacoes.length,
    terrenosManejados: terrenos.size,
    custoTotal: custos,
    custoMedio: aplicacoes.length > 0 ? custos / aplicacoes.length : 0,
    areaTotal: areas,
    terrenosBloqueados: terrenosCarencia.value.length,
    proximasLiberacoes: terrenosCarencia.value.filter(t => t.dias_para_liberacao <= 7).length
  }
})

// Colunas da tabela
const columns = [
  { name: 'terreno_nome', label: 'Terreno', field: 'terreno_nome', sortable: true, align: 'left' },
  { name: 'produto_nome', label: 'Produto', field: 'produto_nome', sortable: true, align: 'left' },
  { name: 'TIPO_MANEJO', label: 'Tipo', field: 'TIPO_MANEJO', sortable: true, align: 'center' },
  { name: 'DATA_APLICACAO', label: 'Data', field: 'DATA_APLICACAO', sortable: true, align: 'left' },
  { name: 'QUANTIDADE', label: 'Quantidade', field: 'QUANTIDADE', sortable: true, align: 'right' },
  { name: 'dose_hectare', label: 'Dose/HA', field: 'dose_hectare', sortable: false, align: 'right' },
  { name: 'custo', label: 'Custo', field: 'custo', sortable: false, align: 'right' },
  { name: 'status_carencia', label: 'Status', field: 'status_carencia', sortable: false, align: 'center' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

// Métodos principais
async function onRequest(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  manejoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  await manejoStore.fetchAplicacoes({ ...props, filtros: filtros.value })
}

async function onFilterChange() {
  await manejoStore.fetchAplicacoes({ filtros: filtros.value })
}

function openDialog(record) {
  initializeForm(record)
  dialog.value = true
}

function initializeForm(record) {
  if (record) {
    form.value = { ...record }
    // Converter datas para formato de input
    if (form.value.DATA_APLICACAO) {
      form.value.DATA_APLICACAO = new Date(form.value.DATA_APLICACAO).toISOString().split('T')[0]
    }
  } else {
    form.value = {
      ID_TERRENO: null,
      ID_PRODUTO: null,
      TIPO_MANEJO: null,
      DATA_APLICACAO: new Date().toISOString().split('T')[0],
      QUANTIDADE: null,
      UNIDADE_MEDIDA: '',
      DOSE_HECTARE: null,
      AREA_APLICADA: null,
      CUSTO_PRODUTO: null,
      CUSTO_APLICACAO: null,
      CUSTO_TOTAL: null,
      EQUIPAMENTO_UTILIZADO: '',
      CONDICOES_CLIMATICAS: '',
      PERIODO_CARENCIA: null,
      OBSERVACOES: ''
    }
  }
}

async function submitForm() {
  try {
    // Preparar dados
    const data = { ...form.value }
    
    // Converter selects para IDs
    if (data.ID_TERRENO?.value) data.ID_TERRENO = data.ID_TERRENO.value
    if (data.ID_PRODUTO?.value) data.ID_PRODUTO = data.ID_PRODUTO.value
    if (data.TIPO_MANEJO?.value) data.TIPO_MANEJO = data.TIPO_MANEJO.value
    
    // Calcular custo total se não informado
    if (!data.CUSTO_TOTAL && custoTotalCalculado.value > 0) {
      data.CUSTO_TOTAL = custoTotalCalculado.value
    }
    
    // Usar carência recomendada se não informada
    if (!data.PERIODO_CARENCIA && carenciaRecomendada.value) {
      data.PERIODO_CARENCIA = carenciaRecomendada.value
    }

    if (form.value.ID) {
      await manejoStore.updateAplicacao(form.value.ID, data)
      $q.notify({ type: 'positive', message: 'Aplicação atualizada com sucesso!' })
    } else {
      await manejoStore.createAplicacao(data)
      $q.notify({ type: 'positive', message: 'Aplicação registrada com sucesso!' })
    }
    
    dialog.value = false
    await manejoStore.fetchAplicacoes({ filtros: filtros.value })
    await loadTerrenosCarencia()
    
  } catch (error) {
    $q.notify({ type: 'negative', message: error.message || 'Erro ao salvar aplicação' })
  }
}

function viewAplicacao(aplicacao) {
  viewData.value = aplicacao
  viewDialog.value = true
}

function confirmDelete(record) {
  recordToDelete.value = record
  deleteDialog.value = true
}

async function deleteAplicacao() {
  try {
    await manejoStore.deleteAplicacao(recordToDelete.value.ID)
    $q.notify({ type: 'positive', message: 'Aplicação excluída e estoque restaurado!' })
    deleteDialog.value = false
    await manejoStore.fetchAplicacoes({ filtros: filtros.value })
    await loadTerrenosCarencia()
  } catch (error) {
    $q.notify({ type: 'negative', message: error.message || 'Erro ao excluir aplicação' })
  }
}

// Carregamento de opções
async function loadOptions() {
  try {
    // Carregar terrenos
    await terrenoStore.fetchTerrenos({ limit: 100 })
    terrenoOptions.value = terrenoStore.terrenos.map(t => ({
      value: t.ID,
      label: t.NOME,
      area_hectares: t.AREA_HECTARES
    }))
    terrenoOptionsDialog.value = [...terrenoOptions.value]

    // Carregar produtos
    const produtos = await manejoStore.getAutocompleProdutos()
    produtoOptions.value = produtos.map(p => ({
      value: p.value,
      label: p.label
    }))
    produtoOptionsDialog.value = [...produtoOptions.value]
    
  } catch (error) {
    console.error('Erro ao carregar opções:', error)
  }
}

async function loadTerrenosCarencia() {
  try {
    const response = await manejoStore.getTerrenosLiberacao(30)
    terrenosCarencia.value = response.liberacoes || []
  } catch (error) {
    console.error('Erro ao carregar terrenos em carência:', error)
  }
}

// Filtros e selects
function filterTerrenos(val, update) {
  update(() => {
    if (val === '') {
      terrenoOptions.value = [...terrenoOptionsDialog.value]
    } else {
      const needle = val.toLowerCase()
      terrenoOptions.value = terrenoOptionsDialog.value.filter(
        t => t.label.toLowerCase().includes(needle)
      )
    }
  })
}

function filterTerrenosDialog(val, update) {
  update(() => {
    if (val === '') {
      terrenoOptionsDialog.value = [...terrenoOptions.value]
    } else {
      const needle = val.toLowerCase()
      terrenoOptionsDialog.value = terrenoOptions.value.filter(
        t => t.label.toLowerCase().includes(needle)
      )
    }
  })
}

function filterProdutos(val, update) {
  update(() => {
    if (val === '') {
      produtoOptions.value = [...produtoOptionsDialog.value]
    } else {
      const needle = val.toLowerCase()
      produtoOptions.value = produtoOptionsDialog.value.filter(
        p => p.label.toLowerCase().includes(needle)
      )
    }
  })
}

function filterProdutosDialog(val, update) {
  update(() => {
    if (val === '') {
      produtoOptionsDialog.value = [...produtoOptions.value]
    } else {
      const needle = val.toLowerCase()
      produtoOptionsDialog.value = produtoOptions.value.filter(
        p => p.label.toLowerCase().includes(needle)
      )
    }
  })
}

function onTerrenoSelected(terreno) {
  if (terreno?.value) {
    form.value.ID_TERRENO = {
      value: terreno.value,
      label: terreno.label,
      area_hectares: terreno.area_hectares
    }
  }
}

function onProdutoSelected(produto) {
  if (produto?.value) {
    // Buscar dados completos do produto
    manejoStore.getProdutoById(produto.value).then(produtoCompleto => {
      form.value.ID_PRODUTO = {
        value: produto.value,
        label: produto.label,
        estoque_atual: produtoCompleto.ESTOQUE_ATUAL || 0,
        unidade_medida: produtoCompleto.UNIDADE_MEDIDA,
        preco_unitario: produtoCompleto.PRECO_UNITARIO,
        periodo_carencia: produtoCompleto.PERIODO_CARENCIA,
        dose_recomendada: produtoCompleto.DOSE_RECOMENDADA
      }
      
      // Pré-preencher campos
      form.value.UNIDADE_MEDIDA = produtoCompleto.UNIDADE_MEDIDA
      if (produtoCompleto.DOSE_RECOMENDADA) {
        form.value.DOSE_HECTARE = produtoCompleto.DOSE_RECOMENDADA
      }
      if (produtoCompleto.PERIODO_CARENCIA) {
        form.value.PERIODO_CARENCIA = produtoCompleto.PERIODO_CARENCIA
      }
      
    }).catch(error => {
      console.error('Erro ao buscar produto:', error)
    })
  }
}

// Helpers de exibição
function getCorTipoManejo(tipo) {
  const cores = {
    'ADUBACAO': 'green',
    'CALAGEM': 'blue',
    'PLANTIO': 'orange',
    'APLICACAO_DEFENSIVO': 'red',
    'GESSAGEM': 'purple',
    'SULCAGEM': 'brown'
  }
  return cores[tipo] || 'grey'
}

function getIconeTipoManejo(tipo) {
  const icones = {
    'ADUBACAO': 'eco',
    'CALAGEM': 'science',
    'PLANTIO': 'local_florist',
    'APLICACAO_DEFENSIVO': 'bug_report',
    'GESSAGEM': 'grain',
    'SULCAGEM': 'linear_scale'
  }
  return icones[tipo] || 'agriculture'
}

function getUnidadeAplicacao(row) {
  return row.UNIDADE_MEDIDA || ''
}

function getCorCarencia(row) {
  if (!row.DATA_LIBERACAO) return 'grey'
  
  const hoje = new Date()
  const liberacao = new Date(row.DATA_LIBERACAO)
  
  if (liberacao <= hoje) return 'positive' // Liberado
  
  const diasRestantes = Math.ceil((liberacao - hoje) / (1000 * 60 * 60 * 24))
  
  if (diasRestantes <= 3) return 'orange' // Libera em breve
  return 'negative' // Em carência
}

function getIconeCarencia(row) {
  if (!row.DATA_LIBERACAO) return 'help'
  
  const hoje = new Date()
  const liberacao = new Date(row.DATA_LIBERACAO)
  
  if (liberacao <= hoje) return 'check_circle'
  return 'schedule'
}

function getStatusCarencia(row) {
  if (!row.DATA_LIBERACAO) return 'N/A'
  
  const hoje = new Date()
  const liberacao = new Date(row.DATA_LIBERACAO)
  
  if (liberacao <= hoje) return 'Liberado'
  
  const diasRestantes = Math.ceil((liberacao - hoje) / (1000 * 60 * 60 * 24))
  return `${diasRestantes} dias`
}

function formatarData(data) {
  if (!data) return '-'
  return new Date(data).toLocaleDateString('pt-BR')
}

function viewCarencia(terreno) {
  $q.dialog({
    title: 'Detalhes da Carência',
    message: `
      <strong>Terreno:</strong> ${terreno.terreno_nome}<br>
      <strong>Produto:</strong> ${terreno.produto_nome}<br>
      <strong>Tipo:</strong> ${terreno.tipo_manejo}<br>
      <strong>Data Aplicação:</strong> ${terreno.data_aplicacao}<br>
      <strong>Data Liberação:</strong> ${terreno.data_liberacao}<br>
      <strong>Dias Restantes:</strong> ${terreno.dias_para_liberacao}
    `,
    html: true
  })
}

function showAllCarencias() {
  $q.notify({ type: 'info', message: 'Modal com todas as carências em desenvolvimento' })
}

// Watchers para cálculos automáticos
watch([() => form.value.CUSTO_PRODUTO, () => form.value.CUSTO_APLICACAO], () => {
  if (!form.value.CUSTO_TOTAL) {
    form.value.CUSTO_TOTAL = custoTotalCalculado.value
  }
})

watch(() => form.value.QUANTIDADE, () => {
  if (!form.value.CUSTO_PRODUTO && custoCalculado.value > 0) {
    form.value.CUSTO_PRODUTO = custoCalculado.value
  }
})

// Lifecycle
onMounted(async () => {
  await loadOptions()
  await manejoStore.fetchAplicacoes({ filtros: filtros.value })
  await loadTerrenosCarencia()
})
</script>


<style scoped>
@import 'src/css/components/aplicacoesterrenos.css';
</style>