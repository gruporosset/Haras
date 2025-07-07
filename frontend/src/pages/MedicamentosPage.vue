<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md text-primary">
      <q-icon
        name="medication"
        class="q-mr-sm"
      />
      Controle de Medicamentos
    </div>

    <q-card>
      <q-card-section>
        <!-- Estatísticas Rápidas -->
        <EstatisticasMedicamentos @ir-para-alertas="activeTab = 'alertas'" />

        <!-- Abas -->
        <q-tabs
          v-model="activeTab"
          dense
          class="text-grey"
          active-color="primary"
          indicator-color="primary"
          align="justify"
          narrow-indicator
        >
          <q-tab
            name="medicamentos"
            label="Medicamentos"
            icon="medication"
          />
          <q-tab
            name="estoque"
            label="Controle de Estoque"
            icon="inventory"
          />
          <q-tab
            name="aplicacoes"
            label="Aplicações"
            icon="medical_services"
          />
          <q-tab
            name="movimentacoes"
            label="Movimentações"
            icon="swap_horiz"
          />
          <q-tab
            name="alertas"
            label="Alertas"
            icon="warning"
            :badge="medicamentoStore.alertasEstoque.length || undefined"
          />
          <!-- <q-tab name="relatorios" label="Relatórios" icon="assessment" /> -->
        </q-tabs>

        <q-separator />

        <q-tab-panels
          v-model="activeTab"
          animated
        >
          <!-- ABA MEDICAMENTOS -->
          <q-tab-panel name="medicamentos">
            <ListaMedicamentos
              @novo-medicamento="abrirFormulario()"
              @visualizar="abrirDetalhes"
              @editar="abrirEdicao"
              @excluir="confirmarExclusao"
              ref="listaRef"
            />
          </q-tab-panel>

          <!-- ABA CONTROLE DE ESTOQUE -->
          <q-tab-panel name="estoque">
            <ControleEstoque
              @medicamento-saved="onMedicamentoSaved"
              ref="controleEstoqueRef"
            />
          </q-tab-panel>

          <!-- ABA APLICAÇÕES -->
          <q-tab-panel name="aplicacoes">
            <AplicacoesMedicamentos
              @aplicacao-registrada="onMedicamentoSaved"
            />
          </q-tab-panel>

          <!-- ABA MOVIMENTAÇÕES -->
          <q-tab-panel name="movimentacoes">
            <MovimentacoesMedicamentos />
          </q-tab-panel>

          <!-- ABA ALERTAS -->
          <q-tab-panel name="alertas">
            <AlertasMedicamentos
              @comprar="abrirCompra"
              @abrir-entrada-lote="abrirEntradaLote"
            />
          </q-tab-panel>

          <!-- ABA RELATÓRIOS -->
          <!-- <q-tab-panel name="relatorios">
            <RelatoriosMedicamentos ref="relatoriosRef" />
          </q-tab-panel> -->
        </q-tab-panels>
      </q-card-section>
    </q-card>

    <!-- Componente de Formulário -->
    <FormularioMedicamento
      v-model="formularioDialog"
      @saved="onMedicamentoSaved"
      ref="formularioRef"
    />

    <!-- Componente de Detalhes -->
    <DetalhesMedicamento ref="detalhesRef" />

    <!-- Confirmação de Exclusão -->
    <ConfirmacaoExclusao
      v-model="deleteDialog"
      mensagem="Deseja excluir este medicamento?"
      :item-selecionado="medicamentoToDelete"
      :loading="medicamentoStore.loading"
      @confirmar="excluirMedicamento"
    />
  </q-page>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useMedicamentoStore } from 'stores/medicamento'
  import { ErrorHandler } from 'src/utils/errorHandler'

  // Componentes
  import EstatisticasMedicamentos from 'components/medicamentos/EstatisticasMedicamentos.vue'
  import ListaMedicamentos from 'components/medicamentos/ListaMedicamentos.vue'
  import FormularioMedicamento from 'components/medicamentos/FormularioMedicamento.vue'
  import DetalhesMedicamento from 'components/medicamentos/DetalhesMedicamento.vue'
  import ControleEstoque from 'components/medicamentos/ControleEstoque.vue'
  import AplicacoesMedicamentos from 'components/medicamentos/AplicacoesMedicamentos.vue'
  import MovimentacoesMedicamentos from 'components/medicamentos/MovimentacoesMedicamentos.vue'
  import AlertasMedicamentos from 'components/medicamentos/AlertasMedicamentos.vue'
  // import RelatoriosMedicamentos from 'components/medicamentos/RelatoriosMedicamentos.vue'
  import ConfirmacaoExclusao from 'components/widgets/ConfirmacaoExclusao.vue'

  // Store
  const medicamentoStore = useMedicamentoStore()

  // Refs dos componentes
  const listaRef = ref(null)
  const formularioRef = ref(null)
  const detalhesRef = ref(null)
  // const relatoriosRef = ref(null)
  const controleEstoqueRef = ref(null)

  // Estado reativo
  const activeTab = ref('medicamentos')
  const formularioDialog = ref(false)
  const deleteDialog = ref(false)
  const medicamentoToDelete = ref(null)

  // Métodos de abertura de dialogs
  function abrirFormulario() {
    formularioRef.value?.openDialog()
  }

  function abrirEdicao(medicamento) {
    formularioRef.value?.openDialog(medicamento)
  }

  function abrirDetalhes(medicamento) {
    detalhesRef.value?.openViewDialog(medicamento)
  }

  function abrirCompra(medicamento) {
    const dadosCompra = {
      medicamento_id: medicamento.ID,
      medicamento_nome: medicamento.NOME,
      tipo: 'ENTRADA',
      quantidade_sugerida: (medicamento.ESTOQUE_MINIMO || 10) * 2, // Sugerir o dobro do mínimo
      motivo: 'Compra por alerta de estoque baixo',
      observacoes: `Estoque atual: ${medicamento.ESTOQUE_ATUAL || 0} ${medicamento.UNIDADE_MEDIDA}. Estoque mínimo: ${medicamento.ESTOQUE_MINIMO || 0} ${medicamento.UNIDADE_MEDIDA}.`,
    }

    // Mudar para aba de estoque
    activeTab.value = 'estoque'

    // Passar dados para o componente ControleEstoque
    setTimeout(() => {
      if (controleEstoqueRef.value) {
        controleEstoqueRef.value.abrirEntradaComDados(dadosCompra)
      }
    }, 100) // Aguardar a aba carregar
  }

  function abrirEntradaLote(dadosLote) {
    // Mudar para aba de controle de estoque
    activeTab.value = 'estoque'

    // Passar dados para o componente ControleEstoque via ref
    setTimeout(() => {
      if (controleEstoqueRef.value) {
        controleEstoqueRef.value.abrirEntradaComDados(dadosLote)
      }
    }, 100) // Aguardar a aba carregar
  }

  // Métodos de ação
  function confirmarExclusao(medicamento) {
    medicamentoToDelete.value = medicamento
    deleteDialog.value = true
  }

  async function excluirMedicamento() {
    try {
      await medicamentoStore.deleteMedicamento(medicamentoToDelete.value.ID)
      ErrorHandler.success('Medicamento excluído com sucesso!')
      deleteDialog.value = false
      refreshData()
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao excluir medicamento')
    }
  }

  function onMedicamentoSaved() {
    refreshData()
  }

  function refreshData() {
    listaRef.value?.fetchMedicamentos()
  }

  // Lifecycle
  onMounted(() => {
    refreshData()
  })

  // Expor métodos
  defineExpose({
    refreshData,
  })
</script>
