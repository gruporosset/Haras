<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md text-primary">
      <q-icon name="straighten" class="q-mr-sm" />
      Controle de Crescimento
    </div>

    <!-- Abas -->
    <q-card>
      <q-tabs
        v-model="activeTab"
        dense
        class="text-grey"
        active-color="primary"
        indicator-color="primary"
        align="justify"
        narrow-indicator
      >
        <q-tab name="medicoes" label="Medições" icon="straighten" />
        <q-tab name="estatisticas" label="Estatísticas" icon="analytics" />
        <q-tab name="graficos" label="Gráficos" icon="show_chart" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="activeTab" animated>
        <!-- ABA MEDIÇÕES -->
        <q-tab-panel name="medicoes">
          <ListaCrescimento 
            @nova-medicao="abrirFormulario()"
            @visualizar="abrirDetalhes"
            @editar="abrirEdicao"
            @excluir="confirmarExclusao"
            @ver-grafico="abrirGraficoIndividual"
            ref="listaRef"
          />
        </q-tab-panel>

        <!-- ABA ESTATÍSTICAS -->
        <q-tab-panel name="estatisticas">
          <EstatisticasCrescimento ref="estatisticasRef" />
        </q-tab-panel>

        <!-- ABA GRÁFICOS -->
        <q-tab-panel name="graficos">
          <GraficosCrescimento ref="graficosRef" />
        </q-tab-panel>
      </q-tab-panels>
    </q-card>

    <!-- Componente de Formulário -->
    <FormularioCrescimento 
      v-model="formularioDialog"
      @saved="onMedicaoSaved"
      ref="formularioRef"
    />

    <!-- Componente de Detalhes -->
    <DetalhesCrescimento ref="detalhesRef" />

    <!-- Confirmação de Exclusão -->
    <ConfirmacaoExclusao 
      v-model="deleteDialog"
      mensagem="Deseja excluir esta medição?"
      :item-selecionado="medicaoToDelete"
      :loading="crescimentoStore.loading"
      @confirmar="excluirMedicao"
    />
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCrescimentoStore } from 'stores/crescimento'
import { ErrorHandler } from 'src/utils/errorHandler'

// Componentes
import ListaCrescimento from 'components/crescimento/ListaCrescimento.vue'
import FormularioCrescimento from 'components/crescimento/FormularioCrescimento.vue'
import DetalhesCrescimento from 'components/crescimento/DetalhesCrescimento.vue'
import EstatisticasCrescimento from 'components/crescimento/EstatisticasCrescimento.vue'
import GraficosCrescimento from 'components/crescimento/GraficosCrescimento.vue'
import ConfirmacaoExclusao from 'components/widgets/ConfirmacaoExclusao.vue'

// Store
const crescimentoStore = useCrescimentoStore()

// Refs dos componentes
const listaRef = ref(null)
const formularioRef = ref(null)
const detalhesRef = ref(null)
const estatisticasRef = ref(null)
const graficosRef = ref(null)

// Estado reativo
const activeTab = ref('medicoes')
const formularioDialog = ref(false)
const deleteDialog = ref(false)
const medicaoToDelete = ref(null)

// Métodos de abertura de dialogs
function abrirFormulario() {
  formularioRef.value?.openDialog()
}

function abrirEdicao(medicao) {
  formularioRef.value?.openDialog(medicao)
}

function abrirDetalhes(medicao) {
  detalhesRef.value?.openViewDialog(medicao)
}

function abrirGraficoIndividual(medicao) {
  detalhesRef.value?.openViewDialog(medicao)
}

// Métodos de ação
function confirmarExclusao(medicao) {
  medicaoToDelete.value = medicao
  deleteDialog.value = true
}

async function excluirMedicao() {
  try {
    await crescimentoStore.deleteCrescimento(medicaoToDelete.value.ID)
    ErrorHandler.success('Medição excluída com sucesso!')
    deleteDialog.value = false
    refreshData()
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao excluir medição')
  }
}

function onMedicaoSaved() {
  refreshData()
}

function refreshData() {
  listaRef.value?.fetchCrescimentos()
  
  if (activeTab.value === 'estatisticas') {
    estatisticasRef.value?.refreshAll()
  }
  
  if (activeTab.value === 'graficos') {
    graficosRef.value?.refreshGraficos()
  }
}

// Lifecycle
onMounted(() => {
  refreshData()
})
</script>