<template>
  <q-page class="q-pa-sm">
    <q-card>
      <q-card-section>
        <div class="text-h5 q-mb-md text-primary">
          <q-icon
            name="favorite"
            class="q-mr-sm"
          />
          Controle Reprodutivo
        </div>
      </q-card-section>

      <q-card-section class="q-pt-none">
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
            name="reproducoes"
            label="Reproduções"
          />
          <q-tab
            name="calendario"
            label="Calendário"
          />
          <q-tab
            name="estatisticas"
            label="Estatísticas"
          />
        </q-tabs>

        <q-separator />

        <q-tab-panels
          v-model="activeTab"
          animated
        >
          <!-- ABA REPRODUÇÕES -->
          <q-tab-panel name="reproducoes">
            <ListaReproducao
              ref="listaReproducao"
              @visualizar="handleVisualizar"
              @editar="handleEditar"
              @excluir="handleExcluir"
              @historico="handleHistorico"
              @nova="handleNova"
            />
          </q-tab-panel>

          <!-- ABA CALENDÁRIO -->
          <q-tab-panel name="calendario">
            <CalendarioEventos ref="calendarioEventos" />
          </q-tab-panel>

          <!-- ABA ESTATÍSTICAS -->
          <q-tab-panel name="estatisticas">
            <EstatisticasReproducao ref="estatisticasReproducao" />
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>
    </q-card>

    <!-- Modal de Visualização -->
    <q-dialog
      v-model="viewDialog"
      persistent
    >
      <DetalhesReproducao
        :reproducao="reproducaoSelecionada"
        @editar="handleEditarFromView"
        @fechar="viewDialog = false"
      />
    </q-dialog>

    <!-- Modal de Cadastro/Edição -->
    <q-dialog
      v-model="formDialog"
      persistent
    >
      <FormularioReproducao
        :reproducao="reproducaoParaEditar"
        @salvar="handleSalvar"
        @cancelar="handleCancelar"
      />
    </q-dialog>

    <!-- Modal de Histórico -->
    <q-dialog
      v-model="historicoDialog"
      persistent
    >
      <HistoricoEgua
        :egua-id="eguaIdHistorico"
        @fechar="historicoDialog = false"
      />
    </q-dialog>

    <!-- Modal de Confirmação de Exclusão -->
    <ConfirmacaoExclusao
      v-model="deleteDialog"
      :item="reproducaoParaExcluir"
      :loading="deleteLoading"
      @confirmar="performDelete"
    />
  </q-page>
</template>

<script setup>
  import { ref, watch, onMounted } from 'vue'
  import { useReproducaoStore } from 'stores/reproducao'
  import ListaReproducao from 'components/reproducao/ListaReproducao.vue'
  import FormularioReproducao from 'components/reproducao/FormularioReproducao.vue'
  import DetalhesReproducao from 'components/reproducao/DetalhesReproducao.vue'
  import HistoricoEgua from 'components/reproducao/HistoricoEgua.vue'
  import CalendarioEventos from 'components/reproducao/CalendarioEventos.vue'
  import EstatisticasReproducao from 'components/reproducao/EstatisticasReproducao.vue'
  import ConfirmacaoExclusao from 'components/widgets/ConfirmacaoExclusao.vue'
  import { ErrorHandler } from 'src/utils/errorHandler'

  const reproducaoStore = useReproducaoStore()

  // Refs dos componentes
  const listaReproducao = ref(null)
  const calendarioEventos = ref(null)
  const estatisticasReproducao = ref(null)

  // Estado da interface
  const activeTab = ref('reproducoes')
  const viewDialog = ref(false)
  const formDialog = ref(false)
  const historicoDialog = ref(false)
  const deleteDialog = ref(false)
  const deleteLoading = ref(false)

  // Dados selecionados
  const reproducaoSelecionada = ref(null)
  const reproducaoParaEditar = ref(null)
  const reproducaoParaExcluir = ref(null)
  const eguaIdHistorico = ref(null)

  // Handlers
  function handleVisualizar(reproducao) {
    reproducaoSelecionada.value = reproducao
    viewDialog.value = true
  }

  function handleEditar(reproducao) {
    reproducaoParaEditar.value = reproducao
    formDialog.value = true
  }

  function handleEditarFromView() {
    viewDialog.value = false
    reproducaoParaEditar.value = reproducaoSelecionada.value
    formDialog.value = true
  }

  function handleNova() {
    reproducaoParaEditar.value = null
    formDialog.value = true
  }

  function handleExcluir(reproducao) {
    reproducaoParaExcluir.value = reproducao
    deleteDialog.value = true
  }

  function handleHistorico(eguaId) {
    eguaIdHistorico.value = eguaId
    historicoDialog.value = true
  }

  async function handleSalvar() {
    formDialog.value = false
    reproducaoParaEditar.value = null
    // Atualizar lista
    if (listaReproducao.value) {
      await listaReproducao.value.loadData()
    }
    ErrorHandler.success('Reprodução salva com sucesso!')
  }

  function handleCancelar() {
    formDialog.value = false
    reproducaoParaEditar.value = null
  }

  async function performDelete() {
    try {
      deleteLoading.value = true
      await reproducaoStore.deleteReproducao(reproducaoParaExcluir.value.ID)
      deleteDialog.value = false

      // Atualizar lista
      if (listaReproducao.value) {
        await listaReproducao.value.loadData()
      }

      ErrorHandler.success('Reprodução excluída com sucesso!')
    } catch (error) {
      ErrorHandler.handle(error)
    } finally {
      deleteLoading.value = false
    }
  }

  // Watch para mudança de aba
  watch(activeTab, async newTab => {
    switch (newTab) {
      case 'reproducoes':
        if (listaReproducao.value) {
          await listaReproducao.value.loadData()
        }
        break
      case 'calendario':
        if (calendarioEventos.value) {
          await calendarioEventos.value.loadData()
        }
        break
      case 'estatisticas':
        if (estatisticasReproducao.value) {
          await estatisticasReproducao.value.loadData()
        }
        break
    }
  })

  // Inicialização
  onMounted(async () => {
    // A primeira aba será carregada automaticamente pelo watch
  })
</script>
