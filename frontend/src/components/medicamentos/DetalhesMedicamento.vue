<template>
  <q-dialog
    v-model="dialog"
    @hide="onDialogHide"
  >
    <q-card style="width: 800px; max-width: 95vw">
      <q-card-section>
        <div class="text-h6">Detalhes do Medicamento</div>
      </q-card-section>

      <q-card-section v-if="medicamentoData">
        <!-- Informações Básicas -->
        <div class="row q-gutter-md">
          <div class="col-6">
            <q-list>
              <q-item>
                <q-item-section>
                  <q-item-label caption>Nome</q-item-label>
                  <q-item-label>{{ medicamentoData.NOME }}</q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section>
                  <q-item-label caption>Princípio Ativo</q-item-label>
                  <q-item-label>
                    {{ medicamentoData.PRINCIPIO_ATIVO || 'Não informado' }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section>
                  <q-item-label caption>Concentração</q-item-label>
                  <q-item-label>
                    {{ medicamentoData.CONCENTRACAO || 'Não informada' }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section>
                  <q-item-label caption>Forma Farmacêutica</q-item-label>
                  <q-item-label>
                    <q-chip
                      :color="getFormaColor(medicamentoData.FORMA_FARMACEUTICA)"
                      text-color="white"
                      dense
                    >
                      {{ medicamentoData.FORMA_FARMACEUTICA }}
                    </q-chip>
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <div class="col-6">
            <q-list>
              <q-item>
                <q-item-section>
                  <q-item-label caption>Fabricante</q-item-label>
                  <q-item-label>
                    {{ medicamentoData.FABRICANTE || 'Não informado' }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section>
                  <q-item-label caption>Registro MAPA</q-item-label>
                  <q-item-label>
                    {{ medicamentoData.REGISTRO_MAPA || 'Não informado' }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section>
                  <q-item-label caption>Unidade de Medida</q-item-label>
                  <q-item-label>
                    {{ medicamentoData.UNIDADE_MEDIDA }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section>
                  <q-item-label caption>Status</q-item-label>
                  <q-item-label>
                    <q-chip
                      :color="
                        medicamentoData.ATIVO === 'S' ? 'positive' : 'negative'
                      "
                      text-color="white"
                      dense
                    >
                      {{ medicamentoData.ATIVO === 'S' ? 'Ativo' : 'Inativo' }}
                    </q-chip>
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </div>

        <!-- Controle de Estoque -->
        <q-separator class="q-my-md" />
        <div class="text-subtitle2 q-mb-sm">Controle de Estoque</div>

        <div class="row q-gutter-md">
          <div class="col-6">
            <q-list>
              <q-item>
                <q-item-section>
                  <q-item-label caption>Estoque Atual</q-item-label>
                  <q-item-label :class="getEstoqueColorClass(medicamentoData)">
                    {{ medicamentoData.ESTOQUE_ATUAL || 0 }}
                    {{ medicamentoData.UNIDADE_MEDIDA }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section>
                  <q-item-label caption>Estoque Mínimo</q-item-label>
                  <q-item-label>
                    {{ medicamentoData.ESTOQUE_MINIMO || 0 }}
                    {{ medicamentoData.UNIDADE_MEDIDA }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <div class="col-6">
            <q-list>
              <q-item>
                <q-item-section>
                  <q-item-label caption>Preço Unitário</q-item-label>
                  <q-item-label>
                    R$ {{ (medicamentoData.PRECO_UNITARIO || 0).toFixed(2) }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section>
                  <q-item-label caption>Valor Total em Estoque</q-item-label>
                  <q-item-label class="text-weight-bold">
                    R$
                    {{
                      (
                        (medicamentoData.ESTOQUE_ATUAL || 0) *
                        (medicamentoData.PRECO_UNITARIO || 0)
                      ).toFixed(2)
                    }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </div>

        <!-- Dados do Lote Atual -->
        <div
          v-if="medicamentoData.LOTE_ATUAL"
          class="q-mt-md"
        >
          <q-separator class="q-my-md" />
          <div class="text-subtitle2 q-mb-sm">Lote Atual</div>

          <div class="row q-gutter-md">
            <div class="col-4">
              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Número do Lote</q-item-label>
                    <q-item-label>
                      {{ medicamentoData.LOTE_ATUAL }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <div class="col-4">
              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Data de Fabricação</q-item-label>
                    <q-item-label>
                      {{ formatDate(medicamentoData.DATA_FABRICACAO) }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <div class="col-4">
              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Data de Validade</q-item-label>
                    <q-item-label
                      :class="
                        getValidadeColorClass(medicamentoData.DATA_VALIDADE)
                      "
                    >
                      {{ formatDate(medicamentoData.DATA_VALIDADE) }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
        </div>

        <!-- Prescrição -->
        <q-separator class="q-my-md" />
        <div class="text-subtitle2 q-mb-sm">Prescrição</div>

        <div class="row q-gutter-md">
          <div class="col-6">
            <q-list>
              <q-item>
                <q-item-section>
                  <q-item-label caption>Requer Receita</q-item-label>
                  <q-item-label>
                    <q-chip
                      :color="
                        medicamentoData.REQUER_RECEITA === 'S'
                          ? 'warning'
                          : 'positive'
                      "
                      text-color="white"
                      dense
                    >
                      {{
                        medicamentoData.REQUER_RECEITA === 'S' ? 'Sim' : 'Não'
                      }}
                    </q-chip>
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <div class="col-6">
            <q-list>
              <q-item>
                <q-item-section>
                  <q-item-label caption>Período de Carência</q-item-label>
                  <q-item-label>
                    {{
                      medicamentoData.PERIODO_CARENCIA
                        ? `${medicamentoData.PERIODO_CARENCIA} dias`
                        : 'Não informado'
                    }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </div>

        <!-- Observações -->
        <div
          v-if="medicamentoData.OBSERVACOES"
          class="q-mt-md"
        >
          <q-separator class="q-my-md" />
          <div class="text-subtitle2 q-mb-sm">Observações</div>
          <q-card
            flat
            bordered
            class="q-pa-md"
          >
            <div class="text-body2">{{ medicamentoData.OBSERVACOES }}</div>
          </q-card>
        </div>

        <!-- Histórico de Movimentações Recentes -->
        <div
          v-if="movimentacoesRecentes.length > 0"
          class="q-mt-md"
        >
          <q-separator class="q-my-md" />
          <div class="text-subtitle2 q-mb-sm">Movimentações Recentes</div>

          <q-table
            :rows="movimentacoesRecentes"
            :columns="movimentacaoColumns"
            flat
            hide-pagination
            :rows-per-page-options="[0]"
          >
            <template v-slot:body-cell-tipo="props">
              <q-td :props="props">
                <q-chip
                  :color="getTipoMovimentacaoColor(props.row.TIPO_MOVIMENTACAO)"
                  text-color="white"
                  dense
                >
                  {{ props.row.TIPO_MOVIMENTACAO }}
                </q-chip>
              </q-td>
            </template>
          </q-table>
        </div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn
          flat
          label="Fechar"
          color="grey"
          @click="dialog = false"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
  import { ref } from 'vue'
  import { useMedicamentoStore } from 'stores/medicamento'
  import { formatDate } from 'src/utils/dateUtils'

  // Store
  const medicamentoStore = useMedicamentoStore()

  // Estado reativo
  const dialog = ref(false)
  const medicamentoData = ref(null)
  const movimentacoesRecentes = ref([])

  // Colunas da tabela de movimentações
  const movimentacaoColumns = [
    {
      name: 'DATA_REGISTRO',
      label: 'Data',
      field: 'DATA_REGISTRO',
      align: 'left',
    },
    {
      name: 'tipo',
      label: 'Tipo',
      field: 'TIPO_MOVIMENTACAO',
      align: 'center',
    },
    {
      name: 'QUANTIDADE',
      label: 'Quantidade',
      field: 'QUANTIDADE',
      align: 'right',
    },
    { name: 'MOTIVO', label: 'Motivo', field: 'MOTIVO', align: 'left' },
  ]

  // Métodos
  async function openViewDialog(medicamento) {
    medicamentoData.value = medicamento
    dialog.value = true

    // Carregar movimentações recentes
    try {
      await loadMovimentacoesRecentes(medicamento.ID)
    } catch (error) {
      console.error('Erro ao carregar movimentações:', error)
    }
  }

  async function loadMovimentacoesRecentes(medicamentoId) {
    try {
      movimentacoesRecentes.value =
        await medicamentoStore.fetchMovimentacoesByMedicamento(medicamentoId, {
          limit: 5,
        })
    } catch {
      movimentacoesRecentes.value = []
    }
  }

  function onDialogHide() {
    medicamentoData.value = null
    movimentacoesRecentes.value = []
  }

  // Funções auxiliares
  function getFormaColor(forma) {
    const colors = {
      INJETAVEL: 'primary',
      ORAL: 'secondary',
      TOPICO: 'accent',
    }
    return colors[forma] || 'grey'
  }

  function getEstoqueColorClass(medicamento) {
    if (!medicamento.ESTOQUE_ATUAL) return 'text-negative'

    if (medicamento.ESTOQUE_ATUAL <= medicamento.ESTOQUE_MINIMO) {
      return 'text-negative'
    } else if (medicamento.ESTOQUE_ATUAL <= medicamento.ESTOQUE_MINIMO * 1.5) {
      return 'text-warning'
    }
    return 'text-positive'
  }

  function getValidadeColorClass(dataValidade) {
    if (!dataValidade) return ''

    const hoje = new Date()
    const validade = new Date(dataValidade)
    const diffDias = Math.ceil((validade - hoje) / (1000 * 60 * 60 * 24))

    if (diffDias < 0) return 'text-negative' // Vencido
    if (diffDias <= 30) return 'text-warning' // Vencendo
    return 'text-positive' // OK
  }

  function getTipoMovimentacaoColor(tipo) {
    const colors = {
      ENTRADA: 'positive',
      SAIDA: 'warning',
      AJUSTE: 'info',
    }
    return colors[tipo] || 'grey'
  }

  // Expor métodos
  defineExpose({
    openViewDialog,
  })
</script>
