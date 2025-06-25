<template>
  <div class="movimentacao-estoque-container">
    <!-- HEADER COM FILTROS -->
    <q-card flat class="q-mb-md">
      <q-card-section>
        <div class="row q-gutter-md items-end">
          <div class="col-md-3 col-12">
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
              v-model="filtros.tipo_movimentacao"
              :options="manejoStore.tiposMovimentacao"
              label="Tipo Movimentação"
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
          
          <div class="col-auto">
            <q-btn-group>
              <q-btn
                color="positive"
                icon="add_box"
                label="Entrada"
                @click="openDialog('ENTRADA')"
                />
                <q-btn
                color="negative"
                icon="remove_circle"
                label="Saída"
                @click="openDialog('SAIDA')"
                class="q-mr-sm q-ml-sm"
              />
              <q-btn
                color="warning"
                icon="tune"
                label="Ajuste"
                @click="openDialog('AJUSTE')"
              />
            </q-btn-group>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- CARDS DE RESUMO -->
    <div class="row q-gutter-md q-mb-md">
      <div class="col-md-3 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6 text-positive">
              <q-icon name="trending_up" class="q-mr-sm" />
              {{ estatisticas.totalEntradas }}
            </div>
            <div class="text-subtitle2">Total Entradas</div>
            <div class="text-caption text-grey-6">
              {{ manejoStore.formatarMoeda(estatisticas.valorEntradas) }}
            </div>
          </q-card-section>
        </q-card>
      </div>
      
      <div class="col-md-3 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6 text-negative">
              <q-icon name="trending_down" class="q-mr-sm" />
              {{ estatisticas.totalSaidas }}
            </div>
            <div class="text-subtitle2">Total Saídas</div>
            <div class="text-caption text-grey-6">
              {{ manejoStore.formatarMoeda(estatisticas.valorSaidas) }}
            </div>
          </q-card-section>
        </q-card>
      </div>
      
      <div class="col-md-3 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6 text-warning">
              <q-icon name="build" class="q-mr-sm" />
              {{ estatisticas.totalAjustes }}
            </div>
            <div class="text-subtitle2">Ajustes</div>
            <div class="text-caption text-grey-6">
              Último: {{ estatisticas.ultimoAjuste || 'Nunca' }}
            </div>
          </q-card-section>
        </q-card>
      </div>
      
      <div class="col-md-2 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6 text-info">
              <q-icon name="inventory" class="q-mr-sm" />
              {{ estatisticas.produtosMovimentados }}
            </div>
            <div class="text-subtitle2">Produtos Movimentados</div>
            <div class="text-caption text-grey-6">
              No período filtrado
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- TABELA DE MOVIMENTAÇÕES -->
    <q-table
      :rows="manejoStore.movimentacoes"
      :columns="columns"
      row-key="ID"
      :loading="manejoStore.loading"
      :pagination="manejoStore.pagination"
      @request="onRequest"
      binary-state-sort
      flat
      class="movimentacoes-table"
    >
      <template v-slot:body-cell-TIPO_MOVIMENTACAO="props">
        <q-td :props="props">
          <q-chip
            :color="manejoStore.getMovimentacaoColor(props.value)"
            text-color="white"
            size="sm"
            :icon="getIconeMovimentacao(props.value)"
          >
            {{ getTipoLabel(props.value) }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-QUANTIDADE="props">
        <q-td :props="props">
          <div class="text-weight-medium">
            {{ props.value?.toLocaleString('pt-BR') }}
          </div>
          <div class="text-caption text-grey-6">
            {{ getUnidadeProduto(props.row) }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-saldo="props">
        <q-td :props="props">
          <div class="row items-center q-gutter-xs">
            <div class="col-12 flex justify-center">
            <div>
              <div class="text-caption text-grey-6">Anterior</div>
              <div class="text-body2">
                {{ (props.row.QUANTIDADE_ANTERIOR || 0).toLocaleString('pt-BR') }}
              </div>
            </div>
            <q-icon 
              :name="getSaldoIcon(props.row)" 
              :color="getSaldoColor(props.row)"
              size="sm"
            />
            <div>
              <div class="text-caption text-grey-6">Atual</div>
              <div class="text-body2 text-weight-medium">
                {{ (props.row.QUANTIDADE_ATUAL || 0).toLocaleString('pt-BR') }}
              </div>
            </div>
            </div>
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-valor="props">
        <q-td :props="props">
          <div v-if="props.row.PRECO_UNITARIO" class="text-weight-medium">
            {{ manejoStore.formatarMoeda(props.row.QUANTIDADE * props.row.PRECO_UNITARIO) }}
          </div>
          <div v-else class="text-grey-6">-</div>
          <div v-if="props.row.PRECO_UNITARIO" class="text-caption text-grey-6">
            {{ manejoStore.formatarMoeda(props.row.PRECO_UNITARIO) }}/{{ getUnidadeProduto(props.row) }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-DATA_REGISTRO="props">
        <q-td :props="props">
          {{ formatarDataHora(props.value) }}
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
              @click="viewMovimentacao(props.row)"
            >
              <q-tooltip>Visualizar</q-tooltip>
            </q-btn>
          </q-btn-group>
        </q-td>
      </template>
    </q-table>

    <!-- DIALOG FORMULÁRIO -->
    <q-dialog v-model="dialog" persistent>
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">
            {{ getTituloDialog() }}
          </div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="submitForm" class="q-gutter-md">
            <!-- Seleção de Produto -->
            <q-select
              v-model="form.ID_PRODUTO"
              :options="produtoOptionsDialog"
              label="Produto *"
              :rules="[val => !!val || 'Produto é obrigatório']"
              use-input
              @filter="filterProdutosDialog"
              @update:model-value="onProdutoSelected"
            />

            <!-- ENTRADA -->
            <template v-if="tipoMovimentacao === 'ENTRADA'">
              <div class="row q-gutter-md">
                <q-input
                  v-model.number="form.QUANTIDADE"
                  label="Quantidade *"
                  type="number"
                  step="0.01"
                  min="0.01"
                  :suffix="unidadeSelecionada"
                  :rules="[val => val > 0 || 'Quantidade deve ser maior que 0']"
                  class="col-5"
                />
                <q-input
                  v-model="form.NOTA_FISCAL"
                  label="Nota Fiscal *"
                  :rules="[val => !!val || 'Nota fiscal é obrigatória']"
                  class="col-6"
                />
              </div>

              <div class="row q-gutter-md">
                <q-input
                  v-model="form.FORNECEDOR"
                  label="Fornecedor *"
                  :rules="[val => !!val || 'Fornecedor é obrigatório']"
                  class="col-4"
                />
                <q-input
                  v-model.number="form.PRECO_UNITARIO"
                  label="Preço Unitário *"
                  type="number"
                  step="0.01"
                  min="0"
                  prefix="R$"
                  :rules="[val => val >= 0 || 'Preço deve ser maior ou igual a 0']"
                  class="col-3"
                />
                <q-input
                  v-model="form.LOTE"
                  label="Lote *"
                  :rules="[val => !!val || 'Lote é obrigatório']"
                  class="col-4"
                />
              </div>

              <div class="row q-gutter-md">
                <q-input
                  v-model="form.DATA_VALIDADE"
                  label="Data de Validade"
                  type="date"
                  class="col-5"
                />
                <q-input
                  v-model="form.DATA_FABRICACAO"
                  label="Data de Fabricação"
                  type="date"
                  class="col-6"
                />
              </div>

              <!-- Resumo da Entrada -->
              <q-card flat bordered class="bg-positive-1">
                <q-card-section class="q-pa-sm">
                  <div class="text-weight-medium text-positive">
                    <q-icon name="add_box" class="q-mr-sm" />
                    Resumo da Entrada
                  </div>
                  <div class="text-body2 q-mt-xs">
                    Valor Total: {{ manejoStore.formatarMoeda((form.QUANTIDADE || 0) * (form.PRECO_UNITARIO || 0)) }}
                  </div>
                </q-card-section>
              </q-card>
            </template>

            <!-- SAÍDA -->
            <template v-if="tipoMovimentacao === 'SAIDA'">
              <div class="row q-gutter-md">
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
                  class="col-5"
                />
                <q-input
                  v-model="form.MOTIVO"
                  label="Motivo *"
                  :rules="[val => !!val || 'Motivo é obrigatório']"
                  placeholder="Ex: Aplicação em terreno, venda, etc."
                  class="col-6"
                />
              </div>

              <!-- Info do Estoque -->
              <q-card flat bordered class="bg-orange-1">
                <q-card-section class="q-pa-sm">
                  <div class="text-weight-medium text-orange-8">
                    <q-icon name="inventory" class="q-mr-sm" />
                    Estoque Disponível
                  </div>
                  <div class="text-body2 q-mt-xs">
                    {{ estoqueDisponivel.toLocaleString('pt-BR') }} {{ unidadeSelecionada }}
                  </div>
                  <div v-if="form.QUANTIDADE" class="text-body2 text-orange-8 q-mt-xs">
                    Restará: {{ (estoqueDisponivel - (form.QUANTIDADE || 0)).toLocaleString('pt-BR') }} {{ unidadeSelecionada }}
                  </div>
                </q-card-section>
              </q-card>
            </template>

            <!-- AJUSTE -->
            <template v-if="tipoMovimentacao === 'AJUSTE'">
              <div class="row q-gutter-md">
                <q-input
                  v-model.number="form.QUANTIDADE_NOVA"
                  label="Nova Quantidade *"
                  type="number"
                  step="0.01"
                  min="0"
                  :suffix="unidadeSelecionada"
                  :rules="[val => val >= 0 || 'Quantidade deve ser maior ou igual a 0']"
                  class="col-5"
                />
                <q-input
                  v-model="form.MOTIVO"
                  label="Motivo *"
                  :rules="[val => !!val || 'Motivo é obrigatório']"
                  placeholder="Ex: Correção de inventário, avarias, etc."
                  class="col-6"
                />
              </div>

              <!-- Preview do Ajuste -->
              <q-card flat bordered class="bg-blue-1">
                <q-card-section class="q-pa-sm">
                  <div class="text-weight-medium text-blue-8">
                    <q-icon name="tune" class="q-mr-sm" />
                    Preview do Ajuste
                  </div>
                  <div class="row q-mt-xs">
                    <div class="col">
                      <div class="text-caption text-grey-6">Estoque Atual</div>
                      <div class="text-body2">{{ estoqueDisponivel.toLocaleString('pt-BR') }} {{ unidadeSelecionada }}</div>
                    </div>
                    <div class="col">
                      <div class="text-caption text-grey-6">Nova Quantidade</div>
                      <div class="text-body2">{{ (form.QUANTIDADE_NOVA || 0).toLocaleString('pt-BR') }} {{ unidadeSelecionada }}</div>
                    </div>
                    <div class="col">
                      <div class="text-caption text-grey-6">Diferença</div>
                      <div class="text-body2" :class="getDiferencaClass()">
                        {{ getDiferencaTexto() }}
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </template>

            <!-- Observações -->
            <q-input
              v-model="form.OBSERVACOES"
              label="Observações"
              type="textarea"
              rows="2"
            />
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" @click="dialog = false" />
          <q-btn
            :label="getLabelBotao()"
            :color="getCorBotao()"
            @click="submitForm"
            :loading="manejoStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG VISUALIZAÇÃO -->
    <q-dialog v-model="viewDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Detalhes da Movimentação</div>
        </q-card-section>

        <q-card-section>
          <q-list>
            <q-item>
              <q-item-section>
                <q-item-label caption>Produto</q-item-label>
                <q-item-label>{{ viewData?.produto_nome }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Tipo de Movimentação</q-item-label>
                <q-item-label>
                  <q-chip
                    :color="manejoStore.getMovimentacaoColor(viewData?.TIPO_MOVIMENTACAO)"
                    text-color="white"
                    size="sm"
                  >
                    {{ getTipoLabel(viewData?.TIPO_MOVIMENTACAO) }}
                  </q-chip>
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Quantidade</q-item-label>
                <q-item-label>{{ viewData?.QUANTIDADE?.toLocaleString('pt-BR') }} {{ getUnidadeProduto(viewData) }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Saldo Anterior → Atual</q-item-label>
                <q-item-label>
                  {{ (viewData?.QUANTIDADE_ANTERIOR || 0).toLocaleString('pt-BR') }} → 
                  {{ (viewData?.QUANTIDADE_ATUAL || 0).toLocaleString('pt-BR') }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.NOTA_FISCAL">
              <q-item-section>
                <q-item-label caption>Nota Fiscal</q-item-label>
                <q-item-label>{{ viewData.NOTA_FISCAL }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.FORNECEDOR">
              <q-item-section>
                <q-item-label caption>Fornecedor</q-item-label>
                <q-item-label>{{ viewData.FORNECEDOR }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.PRECO_UNITARIO">
              <q-item-section>
                <q-item-label caption>Preço Unitário</q-item-label>
                <q-item-label>{{ manejoStore.formatarMoeda(viewData.PRECO_UNITARIO) }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.MOTIVO">
              <q-item-section>
                <q-item-label caption>Motivo</q-item-label>
                <q-item-label>{{ viewData.MOTIVO }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.OBSERVACOES">
              <q-item-section>
                <q-item-label caption>Observações</q-item-label>
                <q-item-label>{{ viewData.OBSERVACOES }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Data/Hora</q-item-label>
                <q-item-label>{{ formatarDataHora(viewData?.DATA_REGISTRO) }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Fechar" color="grey" @click="viewDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useQuasar } from 'quasar'
import { useManejoStore } from 'stores/manejo'
import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

// Composables
const $q = useQuasar()
const manejoStore = useManejoStore()

// Estado reativo
const dialog = ref(false)
const viewDialog = ref(false)
const viewData = ref(null)
const tipoMovimentacao = ref('ENTRADA')

// Filtros
const filtros = ref({
  produto_id: null,
  tipo_movimentacao: null,
  data_inicio: '',
  data_fim: ''
})

// Formulário
const form = ref({})

// Opções
const produtoOptions = ref([])
const produtoOptionsDialog = ref([])

// Computed
const unidadeSelecionada = computed(() => {
  if (!form.value.ID_PRODUTO?.unidade_medida) return ''
  return form.value.ID_PRODUTO.unidade_medida
})

const estoqueDisponivel = computed(() => {
  if (!form.value.ID_PRODUTO?.estoque_atual) return 0
  return form.value.ID_PRODUTO.estoque_atual
})

const estatisticas = computed(() => {
  const movs = manejoStore.movimentacoes
  const entradas = movs.filter(m => m.TIPO_MOVIMENTACAO === 'ENTRADA')
  const saidas = movs.filter(m => m.TIPO_MOVIMENTACAO === 'SAIDA')
  const ajustes = movs.filter(m => m.TIPO_MOVIMENTACAO === 'AJUSTE')
  
  return {
    totalEntradas: entradas.length,
    totalSaidas: saidas.length,
    totalAjustes: ajustes.length,
    valorEntradas: entradas.reduce((sum, m) => sum + ((m.QUANTIDADE || 0) * (m.PRECO_UNITARIO || 0)), 0),
    valorSaidas: saidas.reduce((sum, m) => sum + ((m.QUANTIDADE || 0) * (m.PRECO_UNITARIO || 0)), 0),
    produtosMovimentados: new Set(movs.map(m => m.ID_PRODUTO)).size,
    ultimoAjuste: ajustes.length > 0 ? 
      new Date(Math.max(...ajustes.map(a => new Date(a.DATA_REGISTRO)))).toLocaleDateString('pt-BR') : 
      null
  }
})

// Colunas da tabela
const columns = [
  { name: 'produto_nome', label: 'Produto', field: 'produto_nome', sortable: true, align: 'left' },
  { name: 'TIPO_MOVIMENTACAO', label: 'Tipo', field: 'TIPO_MOVIMENTACAO', sortable: true, align: 'center' },
  { name: 'QUANTIDADE', label: 'Quantidade', field: 'QUANTIDADE', sortable: true, align: 'right' },
  { name: 'saldo', label: 'Saldo Anterior → Atual', field: 'saldo', sortable: false, align: 'center' },
  { name: 'valor', label: 'Valor', field: 'valor', sortable: false, align: 'right' },
  { name: 'DATA_REGISTRO', label: 'Data/Hora', field: 'DATA_REGISTRO', sortable: true, align: 'left' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

// Métodos
async function onRequest(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  manejoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  await manejoStore.fetchMovimentacoes({ ...props, filtros: filtros.value })
}

async function onFilterChange() {
  await manejoStore.fetchMovimentacoes({ filtros: filtros.value })
}

function openDialog(tipo) {
  tipoMovimentacao.value = tipo
  initializeForm()
  dialog.value = true
}

function initializeForm() {
  form.value = {
    ID_PRODUTO: null,
    QUANTIDADE: null,
    QUANTIDADE_NOVA: null,
    NOTA_FISCAL: '',
    FORNECEDOR: '',
    PRECO_UNITARIO: null,
    LOTE: '',
    DATA_VALIDADE: '',
    DATA_FABRICACAO: '',
    MOTIVO: '',
    OBSERVACOES: ''
  }
}

async function submitForm() {
  try {
    
    // Preparar dados baseado no tipo
    const data = { ...form.value }
    if (data.ID_PRODUTO?.value) {
      data.ID_PRODUTO = data.ID_PRODUTO.value
    }
    
    switch (tipoMovimentacao.value) {
      case 'ENTRADA':
        await manejoStore.entradaEstoque(data)
        $q.notify({ type: 'positive', message: 'Entrada registrada com sucesso!' })
        break
        
      case 'SAIDA':
        await manejoStore.saidaEstoque(data)
        $q.notify({ type: 'positive', message: 'Saída registrada com sucesso!' })
        break
        
      case 'AJUSTE':
        await manejoStore.ajusteEstoque(data)
        $q.notify({ type: 'positive', message: 'Ajuste realizado com sucesso!' })
        break
    }
    
    dialog.value = false
    await manejoStore.fetchMovimentacoes({ filtros: filtros.value })
    
  } catch (error) {
    $q.notify({ type: 'negative', message: error.message || 'Erro na movimentação' })
  }
}

function viewMovimentacao(movimentacao) {
  viewData.value = movimentacao
  viewDialog.value = true
}

async function loadProdutoOptions() {
  try {
    const produtos = await manejoStore.getAutocompleProdutos()
    produtoOptions.value = produtos.map(p => ({
      value: p.value,
      label: p.label
    }))
    produtoOptionsDialog.value = [...produtoOptions.value]
  } catch (error) {
    console.error('Erro ao carregar produtos:', error)
  }
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

function onProdutoSelected(produto) {
  if (produto?.value) {
    // Buscar dados completos do produto
    manejoStore.getProdutoById(produto.value).then(produtoCompleto => {
      form.value.ID_PRODUTO = {
        value: produto.value,
        label: produto.label,
        estoque_atual: produtoCompleto.ESTOQUE_ATUAL || 0,
        unidade_medida: produtoCompleto.UNIDADE_MEDIDA,
        preco_unitario: produtoCompleto.PRECO_UNITARIO
      }
      
      // Pré-preencher preço se for entrada
      if (tipoMovimentacao.value === 'ENTRADA' && produtoCompleto.PRECO_UNITARIO) {
        form.value.PRECO_UNITARIO = produtoCompleto.PRECO_UNITARIO
      }
      
      // Pré-preencher quantidade nova se for ajuste
      if (tipoMovimentacao.value === 'AJUSTE') {
        form.value.QUANTIDADE_NOVA = produtoCompleto.ESTOQUE_ATUAL || 0
      }
    }).catch(error => {
      console.error('Erro ao buscar produto:', error)
    })
  }
}

// Helpers
function getTipoLabel(tipo) {
  const labels = {
    'ENTRADA': 'Entrada',
    'SAIDA': 'Saída',
    'AJUSTE': 'Ajuste'
  }
  return labels[tipo] || tipo
}

function getIconeMovimentacao(tipo) {
  const icones = {
    'ENTRADA': 'add_box',
    'SAIDA': 'remove_circle',
    'AJUSTE': 'tune'
  }
  return icones[tipo] || 'help'
}

function getTituloDialog() {
  const titulos = {
    'ENTRADA': 'Nova Entrada de Estoque',
    'SAIDA': 'Nova Saída de Estoque',
    'AJUSTE': 'Ajustar Estoque'
  }
  return titulos[tipoMovimentacao.value] || 'Movimentação'
}

function getLabelBotao() {
  const labels = {
    'ENTRADA': 'Registrar Entrada',
    'SAIDA': 'Registrar Saída',
    'AJUSTE': 'Confirmar Ajuste'
  }
  return labels[tipoMovimentacao.value] || 'Confirmar'
}

function getCorBotao() {
  const cores = {
    'ENTRADA': 'positive',
    'SAIDA': 'negative',
    'AJUSTE': 'warning'
  }
  return cores[tipoMovimentacao.value] || 'primary'
}

function getUnidadeProduto(row) {
  if (row?.produto_unidade) return row.produto_unidade
  if (row?.ID_PRODUTO?.unidade_medida) return row.ID_PRODUTO.unidade_medida
  return ''
}

function getSaldoIcon(row) {
  const anterior = row.QUANTIDADE_ANTERIOR || 0
  const atual = row.QUANTIDADE_ATUAL || 0
  
  if (atual > anterior) return 'trending_up'
  if (atual < anterior) return 'trending_down'
  return 'remove'
}

function getSaldoColor(row) {
  const anterior = row.QUANTIDADE_ANTERIOR || 0
  const atual = row.QUANTIDADE_ATUAL || 0
  
  if (atual > anterior) return 'positive'
  if (atual < anterior) return 'negative'
  return 'grey'
}

function getDiferencaClass() {
  const atual = estoqueDisponivel.value
  const nova = form.value.QUANTIDADE_NOVA || 0
  const diferenca = nova - atual
  
  if (diferenca > 0) return 'text-positive'
  if (diferenca < 0) return 'text-negative'
  return 'text-grey-6'
}

function getDiferencaTexto() {
  const atual = estoqueDisponivel.value
  const nova = form.value.QUANTIDADE_NOVA || 0
  const diferenca = nova - atual
  
  if (diferenca === 0) return 'Sem alteração'
  if (diferenca > 0) return `+${diferenca.toLocaleString('pt-BR')} ${unidadeSelecionada.value}`
  return `${diferenca.toLocaleString('pt-BR')} ${unidadeSelecionada.value}`
}

function formatarDataHora(data) {
  if (!data) return '-'
  return new Date(data).toLocaleString('pt-BR')
}

// Lifecycle
onMounted(async () => {
  await loadProdutoOptions()
  await manejoStore.fetchMovimentacoes({ filtros: filtros.value })
})
</script>

<style scoped>
@import 'src/css/components/movimentacaoestoque.css';
</style>

