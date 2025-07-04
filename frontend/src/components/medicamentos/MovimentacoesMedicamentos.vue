<template>
  <div>
    <!-- Filtros -->
    <q-card
      flat
      bordered
      class="q-pa-md q-mb-md"
    >
      <div class="row q-gutter-md">
        <div class="col-md-3 col-12">
          <q-select
            v-model="filtros.medicamento_id"
            :options="medicamentoOptions"
            label="Medicamento"
            clearable
            use-input
            @filter="filterMedicamentos"
            option-value="value"
            option-label="label"
            emit-value
            map-options
            @update:model-value="onFilterChange"
          />
        </div>

        <div class="col-md-2 col-12">
          <q-select
            v-model="filtros.tipo_movimentacao"
            :options="tiposMovimentacao"
            label="Tipo"
            clearable
            @update:model-value="onFilterChange"
          />
        </div>

        <div class="col-md-2 col-12">
          <CalendarioComponent
            v-model="filtros.data_inicio"
            label="Data Início"
            @update:model-value="onFilterChange"
          />
        </div>

        <div class="col-md-2 col-12">
          <CalendarioComponent
            v-model="filtros.data_fim"
            label="Data Fim"
            @update:model-value="onFilterChange"
          />
        </div>

        <div class="col-md-3 col-12">
          <q-input
            v-model="filtros.motivo"
            label="Motivo"
            clearable
            @update:model-value="onFilterChange"
            :debounce="300"
          />
        </div>
      </div>
    </q-card>

    <!-- Resumo -->
    <div class="row q-gutter-md q-mb-md">
      <q-card
        flat
        bordered
        class="col"
      >
        <q-card-section class="text-center">
          <div class="text-h5 text-warning">{{ resumo.saidas }}</div>
          <div class="text-caption">Saídas</div>
        </q-card-section>
      </q-card>

      <q-card
        flat
        bordered
        class="col"
      >
        <q-card-section class="text-center">
          <div class="text-h5 text-info">{{ resumo.ajustes }}</div>
          <div class="text-caption">Ajustes</div>
        </q-card-section>
      </q-card>

      <q-card
        flat
        bordered
        class="col"
      >
        <q-card-section class="text-center">
          <div class="text-h5 text-accent">
            R$ {{ resumo.valorTotal.toFixed(2) }}
          </div>
          <div class="text-caption">Valor Total</div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Tabela de Movimentações -->
    <q-table
      :rows="medicamentoStore.movimentacoes"
      :columns="columns"
      row-key="ID"
      :loading="medicamentoStore.loading"
      :pagination="medicamentoStore.paginationMovimentacoes"
      @request="onRequest"
      binary-state-sort
    >
      <template v-slot:body-cell-tipo="props">
        <q-td :props="props">
          <q-chip
            :color="getTipoColor(props.row.TIPO_MOVIMENTACAO)"
            text-color="white"
            dense
            :icon="getTipoIcon(props.row.TIPO_MOVIMENTACAO)"
          >
            {{ props.row.TIPO_MOVIMENTACAO }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-medicamento="props">
        <q-td :props="props">
          <div class="text-weight-medium">{{ props.row.medicamento_nome }}</div>
          <div class="text-caption text-grey">
            {{ props.row.forma_farmaceutica }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-quantidade="props">
        <q-td :props="props">
          <div class="text-right">
            <div :class="getQuantidadeClass(props.row.TIPO_MOVIMENTACAO)">
              {{ getQuantidadePrefix(props.row.TIPO_MOVIMENTACAO)
              }}{{ props.row.QUANTIDADE }} {{ props.row.unidade_medida }}
            </div>
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-saldo="props">
        <q-td :props="props">
          <div class="text-right text-caption">
            <div>Anterior: {{ props.row.QUANTIDADE_ANTERIOR || 0 }}</div>
            <div class="text-weight-bold">
              Atual: {{ props.row.QUANTIDADE_ATUAL || 0 }}
            </div>
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-valor="props">
        <q-td :props="props">
          <div class="text-right">
            <div v-if="props.row.PRECO_UNITARIO">
              R$
              {{
                (
                  (props.row.QUANTIDADE || 0) * (props.row.PRECO_UNITARIO || 0)
                ).toFixed(2)
              }}
            </div>
            <div
              v-else
              class="text-grey"
            >
              N/A
            </div>
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-lote="props">
        <q-td :props="props">
          <div v-if="props.row.LOTE">
            <div class="text-weight-medium">{{ props.row.LOTE }}</div>
            <div
              v-if="props.row.DATA_VALIDADE"
              class="text-caption"
            >
              Val: {{ formatDate(props.row.DATA_VALIDADE) }}
            </div>
          </div>
          <div
            v-else
            class="text-grey"
          >
            N/A
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-usuario="props">
        <q-td :props="props">
          {{ props.row.usuario_nome || 'Sistema' }}
        </q-td>
      </template>

      <template v-slot:body-cell-acoes="props">
        <q-td :props="props">
          <q-btn
            flat
            round
            color="primary"
            icon="visibility"
            @click="visualizarMovimentacao(props.row)"
            size="sm"
          >
            <q-tooltip>Visualizar</q-tooltip>
          </q-btn>
          <q-btn
            v-if="props.row.TIPO_MOVIMENTACAO === 'AJUSTE'"
            flat
            round
            color="negative"
            icon="delete"
            @click="excluirMovimentacao(props.row)"
            size="sm"
          >
            <q-tooltip>Excluir</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </q-table>

    <!-- Modal de Visualização -->
    <q-dialog v-model="viewDialog">
      <q-card style="width: 600px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6">Detalhes da Movimentação</div>
        </q-card-section>

        <q-card-section v-if="movimentacaoSelecionada">
          <q-list>
            <q-item>
              <q-item-section>
                <q-item-label caption>Medicamento</q-item-label>
                <q-item-label>
                  {{ movimentacaoSelecionada.medicamento_nome }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Tipo</q-item-label>
                <q-item-label>
                  <q-chip
                    :color="
                      getTipoColor(movimentacaoSelecionada.TIPO_MOVIMENTACAO)
                    "
                    text-color="white"
                    dense
                  >
                    {{ movimentacaoSelecionada.TIPO_MOVIMENTACAO }}
                  </q-chip>
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Quantidade</q-item-label>
                <q-item-label>
                  {{ movimentacaoSelecionada.QUANTIDADE }}
                  {{ movimentacaoSelecionada.unidade_medida }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Data do Registro</q-item-label>
                <q-item-label>
                  {{ formatDate(movimentacaoSelecionada.DATA_REGISTRO) }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="movimentacaoSelecionada.MOTIVO">
              <q-item-section>
                <q-item-label caption>Motivo</q-item-label>
                <q-item-label>
                  {{ movimentacaoSelecionada.MOTIVO }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="movimentacaoSelecionada.OBSERVACOES">
              <q-item-section>
                <q-item-label caption>Observações</q-item-label>
                <q-item-label>
                  {{ movimentacaoSelecionada.OBSERVACOES }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <!-- Dados específicos de entrada -->
            <div v-if="movimentacaoSelecionada.TIPO_MOVIMENTACAO === 'ENTRADA'">
              <q-separator class="q-my-md" />
              <q-item v-if="movimentacaoSelecionada.NOTA_FISCAL">
                <q-item-section>
                  <q-item-label caption>Nota Fiscal</q-item-label>
                  <q-item-label>
                    {{ movimentacaoSelecionada.NOTA_FISCAL }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <q-item v-if="movimentacaoSelecionada.FORNECEDOR">
                <q-item-section>
                  <q-item-label caption>Fornecedor</q-item-label>
                  <q-item-label>
                    {{ movimentacaoSelecionada.FORNECEDOR }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <q-item v-if="movimentacaoSelecionada.LOTE">
                <q-item-section>
                  <q-item-label caption>Lote</q-item-label>
                  <q-item-label>
                    {{ movimentacaoSelecionada.LOTE }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <q-item v-if="movimentacaoSelecionada.DATA_VALIDADE">
                <q-item-section>
                  <q-item-label caption>Data de Validade</q-item-label>
                  <q-item-label>
                    {{ formatDate(movimentacaoSelecionada.DATA_VALIDADE) }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </div>

            <!-- Dados específicos de saída -->
            <div v-if="movimentacaoSelecionada.TIPO_MOVIMENTACAO === 'SAIDA'">
              <q-separator class="q-my-md" />
              <q-item v-if="movimentacaoSelecionada.animal_nome">
                <q-item-section>
                  <q-item-label caption>Animal</q-item-label>
                  <q-item-label>
                    {{ movimentacaoSelecionada.animal_nome }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </div>
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
  import { ref, computed, onMounted } from 'vue'
  import { useMedicamentoStore } from 'stores/medicamento'
  import { ErrorHandler } from 'src/utils/errorHandler'
  import { formatDate } from 'src/utils/dateUtils'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

  // Store
  const medicamentoStore = useMedicamentoStore()

  // Estado reativo
  const viewDialog = ref(false)
  const movimentacaoSelecionada = ref(null)

  // Opções
  const medicamentoOptions = ref([])

  const tiposMovimentacao = [
    { label: 'Entrada', value: 'ENTRADA' },
    { label: 'Saída', value: 'SAIDA' },
    { label: 'Ajuste', value: 'AJUSTE' },
  ]

  // Filtros
  const filtros = ref({
    medicamento_id: null,
    tipo_movimentacao: null,
    data_inicio: '',
    data_fim: '',
    motivo: '',
  })

  // Colunas da tabela
  const columns = [
    {
      name: 'DATA_REGISTRO',
      label: 'Data',
      field: 'DATA_REGISTRO',
      sortable: true,
      align: 'left',
    },
    {
      name: 'medicamento',
      label: 'Medicamento',
      field: 'medicamento_nome',
      sortable: true,
      align: 'left',
    },
    {
      name: 'tipo',
      label: 'Tipo',
      field: 'TIPO_MOVIMENTACAO',
      sortable: true,
      align: 'center',
    },
    {
      name: 'quantidade',
      label: 'Quantidade',
      field: 'QUANTIDADE',
      sortable: true,
      align: 'right',
    },
    {
      name: 'saldo',
      label: 'Saldo',
      field: 'saldo',
      sortable: false,
      align: 'right',
    },
    {
      name: 'valor',
      label: 'Valor',
      field: 'valor',
      sortable: true,
      align: 'right',
    },
    {
      name: 'lote',
      label: 'Lote/Validade',
      field: 'LOTE',
      sortable: false,
      align: 'left',
    },
    {
      name: 'usuario',
      label: 'Usuário',
      field: 'usuario_nome',
      sortable: true,
      align: 'left',
    },
    { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' },
  ]

  // Computed
  const resumo = computed(() => {
    const movimentacoes = medicamentoStore.movimentacoes || []

    const entradas = movimentacoes.filter(
      m => m.TIPO_MOVIMENTACAO === 'ENTRADA'
    ).length
    const saidas = movimentacoes.filter(
      m => m.TIPO_MOVIMENTACAO === 'SAIDA'
    ).length
    const ajustes = movimentacoes.filter(
      m => m.TIPO_MOVIMENTACAO === 'AJUSTE'
    ).length

    const valorTotal = movimentacoes.reduce((total, m) => {
      if (m.PRECO_UNITARIO && m.QUANTIDADE) {
        return total + m.QUANTIDADE * m.PRECO_UNITARIO
      }
      return total
    }, 0)

    return {
      entradas,
      saidas,
      ajustes,
      valorTotal,
    }
  })

  // Métodos
  async function loadMedicamentos() {
    try {
      await medicamentoStore.fetchMedicamentos({ limit: 100 })
      medicamentoOptions.value = medicamentoStore.medicamentos.map(m => ({
        value: m.ID,
        label: m.NOME,
      }))
    } catch (error) {
      console.error('Erro ao carregar medicamentos:', error)
    }
  }

  function filterMedicamentos(val, update) {
    update(() => {
      if (val === '') {
        medicamentoOptions.value = medicamentoStore.medicamentos.map(m => ({
          value: m.ID,
          label: m.NOME,
        }))
      } else {
        const needle = val.toLowerCase()
        const allMedicamentos = medicamentoStore.medicamentos.map(m => ({
          value: m.ID,
          label: m.NOME,
        }))
        medicamentoOptions.value = allMedicamentos.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  async function onFilterChange() {
    try {
      medicamentoStore.setFiltersMovimentacoes(filtros.value)
      await medicamentoStore.fetchMovimentacoes()
    } catch (error) {
      console.error('Erro ao filtrar movimentações:', error)
    }
  }

  function onRequest(props) {
    const { page, rowsPerPage, sortBy, descending } = props.pagination
    medicamentoStore.setPaginationMovimentacoes({
      page,
      rowsPerPage,
      sortBy,
      descending,
    })
    medicamentoStore.fetchMovimentacoes()
  }

  function visualizarMovimentacao(movimentacao) {
    movimentacaoSelecionada.value = movimentacao
    viewDialog.value = true
  }

  async function excluirMovimentacao(movimentacao) {
    try {
      await medicamentoStore.deleteMovimentacao(movimentacao.ID)
      ErrorHandler.success('Movimentação excluída com sucesso!')
      await medicamentoStore.fetchMovimentacoes()
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao excluir movimentação')
    }
  }

  // Funções auxiliares
  function getTipoColor(tipo) {
    const colors = {
      ENTRADA: 'positive',
      SAIDA: 'warning',
      AJUSTE: 'info',
    }
    return colors[tipo] || 'grey'
  }

  function getTipoIcon(tipo) {
    const icons = {
      ENTRADA: 'add_shopping_cart',
      SAIDA: 'remove_shopping_cart',
      AJUSTE: 'tune',
    }
    return icons[tipo] || 'help'
  }

  function getQuantidadeClass(tipo) {
    const classes = {
      ENTRADA: 'text-positive',
      SAIDA: 'text-warning',
      AJUSTE: 'text-info',
    }
    return classes[tipo] || ''
  }

  function getQuantidadePrefix(tipo) {
    const prefixes = {
      ENTRADA: '+',
      SAIDA: '-',
      AJUSTE: '±',
    }
    return prefixes[tipo] || ''
  }

  // Lifecycle
  onMounted(async () => {
    await loadMedicamentos()
    await medicamentoStore.fetchMovimentacoes()
  })
</script>
