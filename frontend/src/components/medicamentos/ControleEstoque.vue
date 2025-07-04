<template>
  <div>
    <!-- Ações Rápidas -->
    <div class="row q-gutter-md q-mb-md">
      <q-btn
        color="positive"
        label="Entrada de Estoque"
        icon="add_shopping_cart"
        @click="abrirEntrada"
      />
      <q-btn
        color="warning"
        label="Saída de Estoque"
        icon="remove_shopping_cart"
        @click="abrirSaida"
      />
      <q-btn
        color="info"
        label="Ajuste de Estoque"
        icon="tune"
        @click="abrirAjuste"
      />
    </div>

    <!-- Filtros -->
    <q-card
      flat
      bordered
      class="q-pa-md q-mb-md"
    >
      <div class="row q-gutter-md">
        <div class="col-md-4 col-12">
          <q-select
            v-model="filtros.medicamento"
            :options="medicamentoOptions"
            label="Medicamento"
            clearable
            use-input
            @filter="filterMedicamentos"
            option-value="value"
            option-label="label"
            emit-value
            map-options
          />
        </div>
        <div class="col-md-3 col-12">
          <q-select
            v-model="filtros.tipo_movimentacao"
            :options="tiposMovimentacao"
            label="Tipo de Movimentação"
            clearable
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
        <div class="col-md-1 col-12">
          <q-btn
            color="primary"
            icon="search"
            @click="onFilterChange"
            style="height: 40px"
          />
        </div>
      </div>
    </q-card>

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
          >
            {{ props.row.TIPO_MOVIMENTACAO }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-quantidade="props">
        <q-td :props="props">
          <div class="text-right">
            {{ props.row.QUANTIDADE }} {{ props.row.unidade_medida }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-saldo="props">
        <q-td :props="props">
          <div class="text-right">
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
            R$
            {{
              (
                (props.row.QUANTIDADE || 0) * (props.row.PRECO_UNITARIO || 0)
              ).toFixed(2)
            }}
          </div>
        </q-td>
      </template>
    </q-table>

    <!-- Modal de Movimentação -->
    <q-dialog
      v-model="movimentacaoDialog"
      persistent
    >
      <q-card style="width: 600px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6">{{ tituloModal }}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form
            @submit="salvarMovimentacao"
            class="q-gutter-md"
          >
            <q-select
              v-model="formMovimentacao.ID_MEDICAMENTO"
              :options="medicamentoOptions"
              label="Medicamento *"
              use-input
              @filter="filterMedicamentos"
              option-value="value"
              option-label="label"
              emit-value
              map-options
              :rules="[val => !!val || 'Medicamento é obrigatório']"
              @update:model-value="onMedicamentoSelect"
            />

            <div class="row q-gutter-md">
              <q-input
                v-model.number="formMovimentacao.QUANTIDADE"
                label="Quantidade *"
                type="number"
                step="0.1"
                class="col-6"
                :rules="[
                  val => val > 0 || 'Quantidade deve ser maior que zero',
                ]"
                :suffix="medicamentoSelecionado?.unidade || ''"
              />
              <q-input
                v-model.number="formMovimentacao.PRECO_UNITARIO"
                label="Preço Unitário"
                type="number"
                step="0.01"
                prefix="R$"
                class="col-6"
              />
            </div>

            <!-- Campos específicos para entrada -->
            <div
              v-if="formMovimentacao.TIPO_MOVIMENTACAO === 'ENTRADA'"
              class="row q-gutter-md"
            >
              <q-input
                v-model="formMovimentacao.NOTA_FISCAL"
                label="Nota Fiscal"
                class="col-4"
              />
              <q-input
                v-model="formMovimentacao.FORNECEDOR"
                label="Fornecedor"
                class="col-4"
              />
              <q-input
                v-model="formMovimentacao.LOTE"
                label="Lote"
                class="col-4"
              />
            </div>

            <div
              v-if="formMovimentacao.TIPO_MOVIMENTACAO === 'ENTRADA'"
              class="row q-gutter-md"
            >
              <CalendarioComponent
                v-model="formMovimentacao.DATA_VALIDADE"
                label="Data de Validade"
                class="col-6"
              />
              <CalendarioComponent
                v-model="formMovimentacao.DATA_FABRICACAO"
                label="Data de Fabricação"
                class="col-6"
              />
            </div>

            <q-input
              v-model="formMovimentacao.MOTIVO"
              label="Motivo"
              :rules="[val => !!val || 'Motivo é obrigatório']"
            />

            <q-input
              v-model="formMovimentacao.OBSERVACOES"
              label="Observações"
              type="textarea"
              rows="3"
            />

            <!-- Validação de estoque para saída -->
            <div
              v-if="
                formMovimentacao.TIPO_MOVIMENTACAO === 'SAIDA' &&
                estoqueInsuficiente
              "
              class="text-negative"
            >
              <q-icon name="warning" />
              Estoque insuficiente! Disponível: {{ estoqueDisponivel }}
            </div>

            <div class="row q-gutter-md q-mt-md">
              <q-btn
                type="submit"
                color="primary"
                :loading="medicamentoStore.loading"
                :disable="
                  formMovimentacao.TIPO_MOVIMENTACAO === 'SAIDA' &&
                  estoqueInsuficiente
                "
                label="Confirmar Movimentação"
              />
              <q-btn
                flat
                label="Cancelar"
                color="grey"
                @click="fecharModalMovimentacao"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useMedicamentoStore } from 'stores/medicamento'
  import { useAuthStore } from 'stores/auth'
  import { ErrorHandler } from 'src/utils/errorHandler'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

  // Emits
  const emit = defineEmits(['medicamento-saved'])

  // Stores
  const medicamentoStore = useMedicamentoStore()
  const authStore = useAuthStore()

  // Estado reativo
  const movimentacaoDialog = ref(false)
  const tipoMovimentacao = ref('')

  // Filtros
  const filtros = ref({
    medicamento: null,
    tipo_movimentacao: null,
    data_inicio: '',
    data_fim: '',
  })

  // Opções
  const medicamentoOptions = ref([])
  const medicamentoSelecionado = ref(null)

  const tiposMovimentacao = [
    { label: 'Entrada', value: 'ENTRADA' },
    { label: 'Saída', value: 'SAIDA' },
    { label: 'Ajuste', value: 'AJUSTE' },
  ]

  // Formulário de movimentação
  const formMovimentacao = ref({
    ID_MEDICAMENTO: null,
    TIPO_MOVIMENTACAO: '',
    QUANTIDADE: 0,
    PRECO_UNITARIO: 0,
    NOTA_FISCAL: '',
    FORNECEDOR: '',
    LOTE: '',
    DATA_VALIDADE: '',
    DATA_FABRICACAO: '',
    MOTIVO: '',
    OBSERVACOES: '',
    ID_USUARIO_REGISTRO: authStore.user?.ID,
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
      name: 'medicamento_nome',
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
      name: 'MOTIVO',
      label: 'Motivo',
      field: 'MOTIVO',
      sortable: true,
      align: 'left',
    },
  ]

  // Computed
  const tituloModal = computed(() => {
    const titulos = {
      ENTRADA: 'Entrada de Estoque',
      SAIDA: 'Saída de Estoque',
      AJUSTE: 'Ajuste de Estoque',
    }
    return titulos[tipoMovimentacao.value] || 'Movimentação'
  })

  const estoqueDisponivel = computed(() => {
    return medicamentoSelecionado.value?.estoque_atual || 0
  })

  const estoqueInsuficiente = computed(() => {
    return (
      formMovimentacao.value.TIPO_MOVIMENTACAO === 'SAIDA' &&
      formMovimentacao.value.QUANTIDADE > estoqueDisponivel.value
    )
  })

  // Métodos
  async function loadMedicamentos() {
    try {
      await medicamentoStore.fetchMedicamentos({ limit: 100 })
      medicamentoOptions.value = medicamentoStore.medicamentos.map(m => ({
        value: m.ID,
        label: m.NOME,
        unidade: m.UNIDADE_MEDIDA,
        estoque_atual: m.ESTOQUE_ATUAL,
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
          unidade: m.UNIDADE_MEDIDA,
          estoque_atual: m.ESTOQUE_ATUAL,
        }))
      } else {
        const needle = val.toLowerCase()
        const allMedicamentos = medicamentoStore.medicamentos.map(m => ({
          value: m.ID,
          label: m.NOME,
          unidade: m.UNIDADE_MEDIDA,
          estoque_atual: m.ESTOQUE_ATUAL,
        }))
        medicamentoOptions.value = allMedicamentos.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  function onMedicamentoSelect() {
    medicamentoSelecionado.value = medicamentoOptions.value.find(
      m => m.value === formMovimentacao.value.ID_MEDICAMENTO
    )
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

  // Métodos de abertura de modais
  function abrirEntrada() {
    tipoMovimentacao.value = 'ENTRADA'
    formMovimentacao.value.TIPO_MOVIMENTACAO = 'ENTRADA'
    formMovimentacao.value.MOTIVO = 'Compra de medicamento'
    movimentacaoDialog.value = true
  }

  function abrirSaida() {
    tipoMovimentacao.value = 'SAIDA'
    formMovimentacao.value.TIPO_MOVIMENTACAO = 'SAIDA'
    formMovimentacao.value.MOTIVO = 'Aplicação em animal'
    movimentacaoDialog.value = true
  }

  function abrirAjuste() {
    tipoMovimentacao.value = 'AJUSTE'
    formMovimentacao.value.TIPO_MOVIMENTACAO = 'AJUSTE'
    formMovimentacao.value.MOTIVO = 'Correção de estoque'
    movimentacaoDialog.value = true
  }

  function fecharModalMovimentacao() {
    movimentacaoDialog.value = false
    tipoMovimentacao.value = ''
    medicamentoSelecionado.value = null

    // Reset do formulário
    formMovimentacao.value = {
      ID_MEDICAMENTO: null,
      TIPO_MOVIMENTACAO: '',
      QUANTIDADE: 0,
      PRECO_UNITARIO: 0,
      NOTA_FISCAL: '',
      FORNECEDOR: '',
      LOTE: '',
      DATA_VALIDADE: '',
      DATA_FABRICACAO: '',
      MOTIVO: '',
      OBSERVACOES: '',
      ID_USUARIO_REGISTRO: authStore.user?.ID,
    }
  }

  async function salvarMovimentacao() {
    try {
      await medicamentoStore.createMovimentacao(formMovimentacao.value)
      ErrorHandler.success('Movimentação registrada com sucesso!')
      fecharModalMovimentacao()
      emit('medicamento-saved')
      await medicamentoStore.fetchMovimentacoes()
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao registrar movimentação')
    }
  }

  function getTipoColor(tipo) {
    const colors = {
      ENTRADA: 'positive',
      SAIDA: 'warning',
      AJUSTE: 'info',
    }
    return colors[tipo] || 'grey'
  }

  // Lifecycle
  onMounted(async () => {
    await loadMedicamentos()
    await medicamentoStore.fetchMovimentacoes()
  })

  // Expor métodos
  defineExpose({
    abrirEntradaComDados,
  })

  // Método para abrir entrada com dados pré-preenchidos
  function abrirEntradaComDados(dadosLote) {
    try {
      tipoMovimentacao.value = 'ENTRADA'
      formMovimentacao.value = {
        ID_MEDICAMENTO: dadosLote.medicamento_id,
        TIPO_MOVIMENTACAO: 'ENTRADA',
        QUANTIDADE: dadosLote.quantidade_sugerida || 0,
        PRECO_UNITARIO: 0,
        NOTA_FISCAL: '',
        FORNECEDOR: '',
        LOTE: '',
        DATA_VALIDADE: '',
        DATA_FABRICACAO: '',
        MOTIVO: dadosLote.motivo || 'Entrada de estoque',
        OBSERVACOES: dadosLote.observacoes || '',
        ID_USUARIO_REGISTRO: authStore.user?.ID,
      }

      // Selecionar o medicamento automaticamente
      const medicamento = medicamentoOptions.value.find(
        m => m.value === dadosLote.medicamento_id
      )
      if (medicamento) {
        medicamentoSelecionado.value = medicamento
        formMovimentacao.value.ID_MEDICAMENTO = medicamento.value
      }

      movimentacaoDialog.value = true
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao abrir entrada de lote')
    }
  }
</script>
