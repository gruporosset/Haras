<template>
  <div class="movimentacao-racao-container">
    <!-- FILTROS -->
    <q-card
      flat
      bordered
      class="q-mb-md"
    >
      <q-card-section>
        <div class="row q-gutter-md justify-between">
          <q-select
            v-model="filtros.produto_id"
            :options="produtoOptions"
            label="Produto"
            clearable
            use-input
            @filter="filterProdutos"
            @update:model-value="onFilterChange"
            class="col-md-3 col-12"
          />

          <q-select
            v-model="filtros.tipo_movimentacao"
            :options="racaoStore.tiposMovimentacao"
            label="Tipo de Movimentação"
            clearable
            @update:model-value="onFilterChange"
            class="col-md-2 col-12"
          />
          <calendario-component
            v-model="filtros.data_inicio"
            label="Data Início"
            @update:model-value="onFilterChange"
            class="col-md-2 col-12"
          />

          <calendario-component
            v-model="filtros.data_fim"
            label="Data Fim"
            @update:model-value="onFilterChange"
            class="col-md-2 col-12"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- ESTATÍSTICAS -->
    <div class="row q-gutter-md q-mb-md justify-between">
      <div class="col-md-3 col-6">
        <q-card
          flat
          bordered
        >
          <q-card-section class="text-center q-pa-sm">
            <div class="text-h4 text-positive">
              {{ estatisticas.totalEntradas }}
            </div>
            <div class="text-subtitle2">Entradas</div>
            <div class="text-caption text-grey-6">
              {{ racaoStore.formatarMoeda(estatisticas.valorEntradas) }}
            </div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-md-3 col-6">
        <q-card
          flat
          bordered
        >
          <q-card-section class="text-center q-pa-sm">
            <div class="text-h4 text-negative">
              {{ estatisticas.totalSaidas }}
            </div>
            <div class="text-subtitle2">Saídas</div>
            <div class="text-caption text-grey-6">
              {{ racaoStore.formatarMoeda(estatisticas.valorSaidas) }}
            </div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-md-3 col-6">
        <q-card
          flat
          bordered
        >
          <q-card-section class="text-center q-pa-sm">
            <div class="text-h4 text-warning">
              {{ estatisticas.totalAjustes }}
            </div>
            <div class="text-subtitle2">Ajustes</div>
            <div class="text-caption text-grey-6">
              {{ estatisticas.ultimoAjuste || 'Nenhum' }}
            </div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-md-2 col-6">
        <q-card
          flat
          bordered
        >
          <q-card-section class="text-center q-pa-sm">
            <div class="text-h4 text-blue">
              {{ estatisticas.produtosMovimentados }}
            </div>
            <div class="text-subtitle2">Produtos</div>
            <div class="text-caption text-grey-6">Movimentados</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- TABELA -->
    <div class="row q-mb-md items-center justify-between">
      <q-btn-group>
        <q-btn
          color="positive"
          icon="add_box"
          label="Entrada"
          @click="openDialog('ENTRADA')"
        />
        <q-btn
          color="negative"
          class="q-mr-sm q-ml-sm"
          icon="remove_circle"
          label="Saída"
          @click="openDialog('SAIDA')"
        />
        <q-btn
          color="warning"
          icon="tune"
          label="Ajuste"
          @click="openDialog('AJUSTE')"
        />
      </q-btn-group>
    </div>

    <q-table
      :rows="racaoStore.movimentacoes"
      :columns="columns"
      row-key="ID"
      :loading="racaoStore.loading"
      :pagination="racaoStore.pagination"
      @request="onRequest"
      binary-state-sort
      flat
      class="movimentacoes-table"
    >
      <template v-slot:body-cell-TIPO_MOVIMENTACAO="props">
        <q-td :props="props">
          <q-chip
            :color="getCorMovimentacao(props.value)"
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
            {{ racaoStore.formatarPeso(props.value) }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-saldo="props">
        <q-td :props="props">
          <div class="row items-center justify-center q-gutter-xs">
            <div class="text-center">
              <div class="text-caption text-grey-6">Anterior</div>
              <div class="text-body2">
                {{ racaoStore.formatarPeso(props.row.QUANTIDADE_ANTERIOR) }}
              </div>
            </div>
            <q-icon
              :name="getSaldoIcon(props.row)"
              :color="getSaldoColor(props.row)"
              size="sm"
            />
            <div class="text-center">
              <div class="text-caption text-grey-6">Atual</div>
              <div class="text-body2">
                {{ racaoStore.formatarPeso(props.row.QUANTIDADE_ATUAL) }}
              </div>
            </div>
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-valor="props">
        <q-td :props="props">
          <div v-if="props.row.PRECO_UNITARIO">
            {{
              racaoStore.formatarMoeda(
                (props.row.QUANTIDADE || 0) * (props.row.PRECO_UNITARIO || 0)
              )
            }}
          </div>
          <div
            v-else
            class="text-grey-6"
          >
            -
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
        </q-td>
      </template>
    </q-table>

    <!-- DIALOG NOVA MOVIMENTAÇÃO -->
    <q-dialog
      v-model="dialog"
      persistent
    >
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">{{ getTituloDialog() }}</div>
        </q-card-section>

        <q-card-section>
          <q-form
            @submit="submitForm"
            class="q-gutter-md"
          >
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

            <!-- Estoque Atual -->
            <q-card
              v-if="form.ID_PRODUTO"
              flat
              bordered
              class="bg-blue-1"
            >
              <q-card-section class="q-pa-sm">
                <div class="text-caption">Estoque Atual</div>
                <div class="text-h6">
                  {{ racaoStore.formatarPeso(estoqueDisponivel) }}
                </div>
              </q-card-section>
            </q-card>

            <!-- Tipo de Movimentação -->
            <q-btn-toggle
              v-model="tipoMovimentacao"
              :options="[
                { label: 'Entrada', value: 'ENTRADA' },
                { label: 'Saída', value: 'SAIDA' },
                { label: 'Ajuste', value: 'AJUSTE' },
              ]"
              @update:model-value="initializeForm"
            />

            <!-- Campos por Tipo -->
            <div v-if="tipoMovimentacao === 'ENTRADA'">
              <div class="row q-gutter-md">
                <q-input
                  v-model="form.NOTA_FISCAL"
                  label="Nota Fiscal *"
                  :rules="[val => !!val || 'Nota fiscal é obrigatória']"
                  class="col-5"
                />
                <q-input
                  v-model="form.FORNECEDOR"
                  label="Fornecedor *"
                  :rules="[val => !!val || 'Fornecedor é obrigatório']"
                  class="col-6"
                />
              </div>

              <div class="row q-gutter-md">
                <q-input
                  v-model.number="form.QUANTIDADE"
                  label="Quantidade *"
                  type="number"
                  step="0.001"
                  min="0.001"
                  :rules="[val => val > 0 || 'Quantidade deve ser maior que 0']"
                  :suffix="unidadeSelecionada"
                  class="col-3"
                />
                <q-input
                  v-model.number="form.PRECO_UNITARIO"
                  label="Preço Unitário *"
                  type="number"
                  step="0.01"
                  min="0"
                  prefix="R$"
                  :rules="[
                    val => val >= 0 || 'Preço deve ser maior ou igual a 0',
                  ]"
                  class="col-3"
                />
                <q-input
                  v-model="form.LOTE"
                  label="Lote *"
                  :rules="[val => !!val || 'Lote é obrigatório']"
                  class="col-5"
                />
              </div>

              <div class="row q-gutter-md">
                <calendario-component
                  v-model="form.DATA_FABRICACAO"
                  label="Data de Fabricação *"
                  :rules="[val => !!val || 'Data é obrigatória']"
                  class="col-md-4 col-12"
                />

                <calendario-component
                  v-model="form.DATA_VALIDADE"
                  label="Data de Validade *"
                  :rules="[val => !!val || 'Data é obrigatória']"
                  class="col-md-4 col-12"
                />
              </div>
            </div>

            <div v-else-if="tipoMovimentacao === 'SAIDA'">
              <div class="row q-gutter-md">
                <q-input
                  v-model.number="form.QUANTIDADE"
                  label="Quantidade *"
                  type="number"
                  step="0.001"
                  min="0.001"
                  :max="estoqueDisponivel"
                  :rules="[
                    val => val > 0 || 'Quantidade deve ser maior que 0',
                    val =>
                      val <= estoqueDisponivel ||
                      `Máximo disponível: ${estoqueDisponivel}`,
                  ]"
                  :suffix="unidadeSelecionada"
                  class="col-6"
                />
                <q-input
                  v-model="form.MOTIVO"
                  label="Motivo *"
                  :rules="[val => !!val || 'Motivo é obrigatório']"
                  class="col-5"
                />
              </div>
            </div>

            <div v-else-if="tipoMovimentacao === 'AJUSTE'">
              <div class="row q-gutter-md">
                <q-input
                  v-model.number="form.QUANTIDADE_NOVA"
                  label="Nova Quantidade *"
                  type="number"
                  step="0.001"
                  min="0"
                  :rules="[
                    val => val >= 0 || 'Quantidade deve ser maior ou igual a 0',
                  ]"
                  :suffix="unidadeSelecionada"
                  class="col-6"
                />
                <q-input
                  v-model="form.MOTIVO"
                  label="Motivo do Ajuste *"
                  :rules="[val => !!val || 'Motivo é obrigatório']"
                  class="col-5"
                />
              </div>

              <!-- Mostrar diferença -->
              <q-card
                flat
                bordered
                class="q-mt-sm"
                :class="getDiferencaClass()"
              >
                <q-card-section class="q-pa-sm">
                  <div class="text-caption">Diferença</div>
                  <div class="text-weight-medium">
                    {{ getDiferencaTexto() }}
                  </div>
                </q-card-section>
              </q-card>
            </div>

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
          <q-btn
            flat
            label="Cancelar"
            color="grey"
            @click="dialog = false"
          />
          <q-btn
            :label="getLabelBotao()"
            :color="getCorBotao()"
            @click="submitForm"
            :loading="racaoStore.loading"
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
          <q-list v-if="viewData">
            <q-item>
              <q-item-section>
                <q-item-label caption>Produto</q-item-label>
                <q-item-label>{{ viewData.produto_nome }}</q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Tipo</q-item-label>
                <q-item-label>
                  <q-chip
                    :color="getCorMovimentacao(viewData.TIPO_MOVIMENTACAO)"
                    text-color="white"
                    size="sm"
                  >
                    {{ getTipoLabel(viewData.TIPO_MOVIMENTACAO) }}
                  </q-chip>
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Quantidade</q-item-label>
                <q-item-label>
                  {{ racaoStore.formatarPeso(viewData.QUANTIDADE) }}
                </q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Data/Hora</q-item-label>
                <q-item-label>
                  {{ formatarDataHora(viewData.DATA_REGISTRO) }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData.PRECO_UNITARIO">
              <q-item-section>
                <q-item-label caption>Preço Unitário</q-item-label>
                <q-item-label>
                  {{ racaoStore.formatarMoeda(viewData.PRECO_UNITARIO) }}
                </q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Valor Total</q-item-label>
                <q-item-label>
                  {{
                    racaoStore.formatarMoeda(
                      (viewData.QUANTIDADE || 0) *
                        (viewData.PRECO_UNITARIO || 0)
                    )
                  }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData.LOTE">
              <q-item-section>
                <q-item-label caption>Lote</q-item-label>
                <q-item-label>{{ viewData.LOTE }}</q-item-label>
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
            label="Fechar"
            color="grey"
            @click="viewDialog = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
  import { ref, onMounted, computed } from 'vue'
  import { useQuasar } from 'quasar'
  import { useRacaoStore } from 'stores/racao'
  import { ErrorHandler } from 'src/utils/errorHandler'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

  // Composables
  const $q = useQuasar()
  const racaoStore = useRacaoStore()

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
    data_fim: '',
  })

  // Formulário
  const form = ref({})

  // Opções
  const produtosOri = ref([])
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
    const movs = racaoStore.movimentacoes
    const entradas = movs.filter(m => m.TIPO_MOVIMENTACAO === 'ENTRADA')
    const saidas = movs.filter(m => m.TIPO_MOVIMENTACAO === 'SAIDA')
    const ajustes = movs.filter(m => m.TIPO_MOVIMENTACAO === 'AJUSTE')

    return {
      totalEntradas: entradas.length,
      totalSaidas: saidas.length,
      totalAjustes: ajustes.length,
      valorEntradas: entradas.reduce(
        (sum, m) => sum + (m.QUANTIDADE || 0) * (m.PRECO_UNITARIO || 0),
        0
      ),
      valorSaidas: saidas.reduce(
        (sum, m) => sum + (m.QUANTIDADE || 0) * (m.PRECO_UNITARIO || 0),
        0
      ),
      produtosMovimentados: new Set(movs.map(m => m.ID_PRODUTO)).size,
      ultimoAjuste:
        ajustes.length > 0
          ? new Date(
              Math.max(...ajustes.map(a => new Date(a.DATA_REGISTRO)))
            ).toLocaleDateString('pt-BR')
          : null,
    }
  })

  // Colunas da tabela
  const columns = [
    {
      name: 'produto_nome',
      label: 'Produto',
      field: 'produto_nome',
      sortable: true,
      align: 'left',
    },
    {
      name: 'TIPO_MOVIMENTACAO',
      label: 'Tipo',
      field: 'TIPO_MOVIMENTACAO',
      sortable: true,
      align: 'center',
    },
    {
      name: 'QUANTIDADE',
      label: 'Quantidade',
      field: 'QUANTIDADE',
      sortable: true,
      align: 'right',
    },
    {
      name: 'saldo',
      label: 'Saldo Anterior → Atual',
      field: 'saldo',
      sortable: false,
      align: 'center',
    },
    {
      name: 'valor',
      label: 'Valor',
      field: 'valor',
      sortable: false,
      align: 'right',
    },
    {
      name: 'DATA_REGISTRO',
      label: 'Data/Hora',
      field: 'DATA_REGISTRO',
      sortable: true,
      align: 'left',
    },
    { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' },
  ]

  // Métodos
  async function onRequest(props) {
    const { page, rowsPerPage, sortBy, descending } = props.pagination
    racaoStore.pagination.page = page
    racaoStore.pagination.rowsPerPage = rowsPerPage
    racaoStore.pagination.sortBy = sortBy
    racaoStore.pagination.descending = descending
    await racaoStore.fetchMovimentacoes({ ...props, filtros: filtros.value })
  }

  async function onFilterChange() {
    racaoStore.pagination.page = 1
    await racaoStore.fetchMovimentacoes({ filtros: filtros.value })
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
      OBSERVACOES: '',
    }
  }

  async function submitForm() {
    try {
      const data = { ...form.value }
      if (data.ID_PRODUTO?.value) {
        data.ID_PRODUTO = data.ID_PRODUTO.value
      }

      switch (tipoMovimentacao.value) {
        case 'ENTRADA':
          await racaoStore.entradaEstoque(data)
          $q.notify({
            type: 'positive',
            message: 'Entrada registrada com sucesso!',
          })
          break

        case 'SAIDA':
          await racaoStore.saidaEstoque(data)
          $q.notify({
            type: 'positive',
            message: 'Saída registrada com sucesso!',
          })
          break

        case 'AJUSTE':
          await racaoStore.ajusteEstoque(data)
          $q.notify({
            type: 'positive',
            message: 'Ajuste realizado com sucesso!',
          })
          break
      }

      dialog.value = false
      await racaoStore.fetchMovimentacoes({ filtros: filtros.value })
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: error.message || 'Erro na movimentação',
      })
    }
  }

  function viewMovimentacao(movimentacao) {
    viewData.value = movimentacao
    viewDialog.value = true
  }

  async function loadProdutoOptions() {
    try {
      const produtos = await racaoStore.autocompleProdutos('')
      produtosOri.value = produtos.map(p => ({
        value: p.value,
        label: p.label,
        estoque_atual: p.estoque_atual,
        unidade_medida: p.unidade_medida,
      }))
      produtoOptions.value = [...produtosOri.value]
      produtoOptionsDialog.value = [...produtosOri.value]
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar produtos')
    }
  }

  function filterProdutos(val, update) {
    update(() => {
      if (val === '') {
        produtoOptions.value = [...produtosOri.value]
      } else {
        const needle = val.toLowerCase()
        produtoOptions.value = produtosOri.value.filter(p =>
          p.label.toLowerCase().includes(needle)
        )
      }
    })
  }

  function filterProdutosDialog(val, update) {
    update(() => {
      if (val === '') {
        produtoOptionsDialog.value = [...produtosOri.value]
      } else {
        const needle = val.toLowerCase()
        produtoOptionsDialog.value = produtosOri.value.filter(p =>
          p.label.toLowerCase().includes(needle)
        )
      }
    })
  }

  function onProdutoSelected(produto) {
    if (produto?.value) {
      form.value.ID_PRODUTO = {
        value: produto.value,
        label: produto.label,
        estoque_atual: produto.estoque_atual || 0,
        unidade_medida: produto.unidade_medida,
      }

      // Pré-preencher valores se for entrada
      if (tipoMovimentacao.value === 'ENTRADA' && produto.preco_unitario) {
        form.value.PRECO_UNITARIO = produto.preco_unitario
      }

      // Pré-preencher quantidade nova se for ajuste
      if (tipoMovimentacao.value === 'AJUSTE') {
        form.value.QUANTIDADE_NOVA = produto.estoque_atual || 0
      }
    }
  }

  // Funções auxiliares
  function getTipoLabel(tipo) {
    const labels = {
      ENTRADA: 'Entrada',
      SAIDA: 'Saída',
      AJUSTE: 'Ajuste',
    }
    return labels[tipo] || tipo
  }

  function getCorMovimentacao(tipo) {
    const cores = {
      ENTRADA: 'positive',
      SAIDA: 'negative',
      AJUSTE: 'warning',
    }
    return cores[tipo] || 'grey'
  }

  function getIconeMovimentacao(tipo) {
    const icones = {
      ENTRADA: 'add_box',
      SAIDA: 'remove_circle',
      AJUSTE: 'tune',
    }
    return icones[tipo] || 'help'
  }

  function getTituloDialog() {
    const titulos = {
      ENTRADA: 'Nova Entrada de Estoque',
      SAIDA: 'Nova Saída de Estoque',
      AJUSTE: 'Ajustar Estoque',
    }
    return titulos[tipoMovimentacao.value] || 'Movimentação'
  }

  function getLabelBotao() {
    const labels = {
      ENTRADA: 'Registrar Entrada',
      SAIDA: 'Registrar Saída',
      AJUSTE: 'Confirmar Ajuste',
    }
    return labels[tipoMovimentacao.value] || 'Confirmar'
  }

  function getCorBotao() {
    const cores = {
      ENTRADA: 'positive',
      SAIDA: 'negative',
      AJUSTE: 'warning',
    }
    return cores[tipoMovimentacao.value] || 'primary'
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
    if (diferenca > 0)
      return `+${diferenca.toLocaleString('pt-BR')} ${unidadeSelecionada.value}`
    return `${diferenca.toLocaleString('pt-BR')} ${unidadeSelecionada.value}`
  }

  function formatarDataHora(data) {
    if (!data) return '-'
    return new Date(data).toLocaleString('pt-BR')
  }

  // Lifecycle
  onMounted(async () => {
    await loadProdutoOptions()
    await racaoStore.fetchMovimentacoes({ filtros: filtros.value })
  })
</script>

<style scoped>
  .movimentacao-racao-container {
    width: 100%;
  }

  .movimentacoes-table {
    border-radius: 8px;
  }

  .movimentacoes-table .q-table__top {
    padding: 16px;
  }
</style>
