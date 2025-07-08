<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md text-primary">
      <q-icon
        name="move_to_inbox"
        class="q-mr-sm"
      />
      Movimentações de Animais
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
        <q-tab
          name="movimentacoes"
          label="Movimentações"
          icon="move_to_inbox"
        />
        <q-tab
          name="localizacoes"
          label="Localizações"
          icon="location_on"
        />
      </q-tabs>

      <q-separator />

      <q-tab-panels
        v-model="activeTab"
        animated
      >
        <!-- ABA MOVIMENTAÇÕES -->
        <q-tab-panel name="movimentacoes">
          <ListaMovimentacoes
            @nova-movimentacao="abrirFormulario()"
            @visualizar="abrirDetalhes"
            @editar="abrirEdicao"
            @excluir="confirmarExclusao"
            @ver-historico="abrirHistorico"
            ref="listaMovimentacoesRef"
          />
        </q-tab-panel>

        <!-- ABA LOCALIZAÇÕES -->
        <q-tab-panel name="localizacoes">
          <ListaLocalizacoes
            @nova-movimentacao="abrirFormulario"
            @ver-historico="abrirHistorico"
            ref="listaLocalizacoesRef"
          />
        </q-tab-panel>
      </q-tab-panels>
    </q-card>

    <!-- Componente de Formulário -->
    <FormularioMovimentacao
      @saved="onMovimentacaoSaved"
      ref="formularioRef"
    />

    <!-- Componente de Detalhes -->
    <DetalhesMovimentacao
      @editar="abrirEdicao"
      ref="detalhesRef"
    />

    <!-- Componente de Histórico -->
    <HistoricoMovimentacao
      @visualizar="abrirDetalhes"
      @editar="abrirEdicao"
      ref="historicoRef"
    />

    <!-- Confirmação de Exclusão -->
    <ConfirmacaoExclusao
      v-model="deleteDialog"
      mensagem="Deseja excluir esta movimentação?"
      :item-selecionado="movimentacaoToDelete"
      :loading="movimentacaoStore.loading"
      @confirmar="excluirMovimentacao"
    />
  </q-page>
</template>

<script setup>
  import { ref, onMounted, watch } from 'vue'
  import { useMovimentacaoStore } from 'stores/movimentacao'
  import { ErrorHandler } from 'src/utils/errorHandler'

  // Componentes
  import ListaMovimentacoes from 'components/movimentacoes/ListaMovimentacoes.vue'
  import ListaLocalizacoes from 'components/movimentacoes/ListaLocalizacoes.vue'
  import FormularioMovimentacao from 'components/movimentacoes/FormularioMovimentacao.vue'
  import DetalhesMovimentacao from 'components/movimentacoes/DetalhesMovimentacao.vue'
  import HistoricoMovimentacao from 'components/movimentacoes/HistoricoMovimentacao.vue'
  import ConfirmacaoExclusao from 'components/widgets/ConfirmacaoExclusao.vue'

  // Store
  const movimentacaoStore = useMovimentacaoStore()

  // Refs dos componentes
  const listaMovimentacoesRef = ref(null)
  const listaLocalizacoesRef = ref(null)
  const formularioRef = ref(null)
  const detalhesRef = ref(null)
  const historicoRef = ref(null)

  // Estado reativo
  const activeTab = ref('movimentacoes')
  const deleteDialog = ref(false)
  const movimentacaoToDelete = ref(null)

  // Métodos de abertura de dialogs
  function abrirFormulario(movimentacao = null) {
    formularioRef.value?.openDialog(movimentacao)
  }

  function abrirEdicao(movimentacao) {
    formularioRef.value?.openDialog(movimentacao)
  }

  function abrirDetalhes(movimentacao) {
    detalhesRef.value?.openViewDialog(movimentacao)
  }

  function abrirHistorico(animalId, animalNome = '') {
    historicoRef.value?.openHistoricoDialog(animalId, animalNome)
  }

  // Métodos de ação
  function confirmarExclusao(movimentacao) {
    movimentacaoToDelete.value = movimentacao
    deleteDialog.value = true
  }

  async function excluirMovimentacao() {
    try {
      await movimentacaoStore.deleteMovimentacao(movimentacaoToDelete.value.ID)
      ErrorHandler.success('Movimentação excluída com sucesso!')
      deleteDialog.value = false
      refreshData()
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao excluir movimentação')
    }
  }

  function onMovimentacaoSaved() {
    refreshData()
  }

  function refreshData() {
    if (activeTab.value === 'movimentacoes') {
      listaMovimentacoesRef.value?.fetchMovimentacoes()
    } else if (activeTab.value === 'localizacoes') {
      listaLocalizacoesRef.value?.fetchLocalizacoes()
    }
  }

  // Watcher para mudança de abas
  watch(activeTab, newTab => {
    if (newTab === 'movimentacoes') {
      listaMovimentacoesRef.value?.fetchMovimentacoes()
    } else if (newTab === 'localizacoes') {
      listaLocalizacoesRef.value?.fetchLocalizacoes()
    }
  })

  // Lifecycle
  onMounted(() => {
    refreshData()
  })
</script>
