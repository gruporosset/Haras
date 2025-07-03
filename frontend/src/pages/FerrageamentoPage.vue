<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md text-primary">
      <q-icon name="build" class="q-mr-sm" />
      Ferrageamento e Casqueamento
    </div>
    
    <q-card>
      <q-card-section>
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
          <q-tab name="registros" label="Registros" icon="build" />
          <q-tab name="aplicacao-rapida" label="Aplicação Rápida" icon="flash_on" />
          <q-tab name="alertas" label="Alertas" icon="warning" :badge="ferrageamentoStore.alertasVencimento?.length || undefined" />
          <q-tab name="estatisticas" label="Estatísticas" icon="analytics" />
          <!-- <q-tab name="relatorios" label="Relatórios" icon="assessment" /> -->
        </q-tabs>

        <q-separator />

        <q-tab-panels v-model="activeTab" animated>
          <!-- ABA REGISTROS -->
          <q-tab-panel name="registros">
            <ListaFerrageamento 
              @novo-registro="abrirFormulario()"
              @visualizar="abrirDetalhes"
              @editar="abrirEdicao"
              @excluir="confirmarExclusao"
              ref="listaRef"
            />
          </q-tab-panel>

          <!-- ABA APLICAÇÃO RÁPIDA -->
          <q-tab-panel name="aplicacao-rapida">
            <AplicacaoRapida @aplicacao-registrada="onRegistroSaved" />
          </q-tab-panel>

          <!-- ABA ALERTAS -->
          <q-tab-panel name="alertas">
            <AlertasFerrageamento @agendar="abrirAgendamento" />
          </q-tab-panel>

          <!-- ABA ESTATÍSTICAS -->
          <q-tab-panel name="estatisticas">
            <EstatisticasFerrageamento />
          </q-tab-panel>

          <!-- ABA RELATÓRIOS -->
          <!-- <q-tab-panel name="relatorios">
            <RelatoriosFerrageamento ref="relatoriosRef" />
          </q-tab-panel> -->
        </q-tab-panels>
      </q-card-section>
    </q-card>

    <!-- Componente de Formulário -->
    <FormularioFerrageamento 
      v-model="formularioDialog"
      @saved="onRegistroSaved"
      ref="formularioRef"
    />

    <!-- Componente de Detalhes -->
    <DetalhesFerrageamento ref="detalhesRef" />

    <!-- Confirmação de Exclusão -->
    <ConfirmacaoExclusao 
      v-model="deleteDialog"
      mensagem="Deseja excluir este registro?"
      :item-selecionado="registroToDelete"
      :loading="ferrageamentoStore.loading"
      @confirmar="excluirRegistro"
    />
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFerrageamentoStore } from 'stores/ferrageamento'
import { ErrorHandler } from 'src/utils/errorHandler'

// Componentes
import ListaFerrageamento from 'components/ferrageamento/ListaFerrageamento.vue'
import FormularioFerrageamento from 'components/ferrageamento/FormularioFerrageamento.vue'
import DetalhesFerrageamento from 'components/ferrageamento/DetalhesFerrageamento.vue'
// import RelatoriosFerrageamento from 'components/ferrageamento/RelatoriosFerrageamento.vue'
import AplicacaoRapida from 'components/ferrageamento/AplicacaoRapida.vue'
import AlertasFerrageamento from 'components/ferrageamento/AlertasFerrageamento.vue'
import EstatisticasFerrageamento from 'components/ferrageamento/EstatisticasFerrageamento.vue'
import ConfirmacaoExclusao from 'components/widgets/ConfirmacaoExclusao.vue'

// Store
const ferrageamentoStore = useFerrageamentoStore()

// Refs dos componentes
const listaRef = ref(null)
const formularioRef = ref(null)
const detalhesRef = ref(null)
// const relatoriosRef = ref(null)

// Estado reativo
const activeTab = ref('registros')
const formularioDialog = ref(false)
const deleteDialog = ref(false)
const registroToDelete = ref(null)

// Métodos de abertura de dialogs
function abrirFormulario() {
  formularioRef.value?.openDialog()
}

function abrirEdicao(registro) {
  formularioRef.value?.openDialog(registro)
}

function abrirDetalhes(registro) {
  detalhesRef.value?.openViewDialog(registro)
}

// Métodos de ação
function confirmarExclusao(registro) {
  registroToDelete.value = registro
  deleteDialog.value = true
}

async function excluirRegistro() {
  try {
    await ferrageamentoStore.deleteFerrageamento(registroToDelete.value.ID)
    ErrorHandler.success('Registro excluído com sucesso!')
    deleteDialog.value = false
    refreshData()
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao excluir registro')
  }
}

function onRegistroSaved() {
  refreshData()
}

function refreshData() {
  listaRef.value?.fetchFerrageamentos()
}

function abrirAgendamento(alerta) {
  const registro = {
    ID_ANIMAL: alerta.animal_id,
    TIPO_REGISTRO: alerta.tipo_registro,
    FERRADOR_RESPONSAVEL: alerta.ferrador_anterior || '',
    CUSTO: alerta.custo_estimado || null,
    OBSERVACOES: 'Agendado através de alerta de vencimento'
  }
  formularioRef.value?.openDialog(registro)
}

// Lifecycle
onMounted(() => {
  refreshData()
})
</script>