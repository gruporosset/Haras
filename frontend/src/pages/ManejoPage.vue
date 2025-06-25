<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md text-primary">
      <q-icon name="landscape" class="q-mr-sm" />
      Manejo de Terrenos
    </div>

    <q-card>
      <q-card-section>
        
        <!-- Abas dos Módulos -->
        <q-tabs v-model="activeTab" class="q-mb-md" align="center">
          <q-tab name="produtos" label="Produtos Manejo" />
          <q-tab name="estoque" label="Movimentação Estoque" />
          <q-tab name="aplicacoes" label="Aplicações Terrenos" />
          <q-tab name="analises" label="Análises de Solo" />
          <q-tab name="relatorios" label="Relatórios" />
        </q-tabs>
        
        <q-tab-panels v-model="activeTab" animated>
          <!-- ========================================= -->
          <!-- ABA PRODUTOS MANEJO -->
          <!-- ========================================= -->
          <q-tab-panel name="produtos">
            <ProdutosManejo />
          </q-tab-panel>

          <!-- ========================================= -->
          <!-- ABA MOVIMENTAÇÃO ESTOQUE -->
          <!-- ========================================= -->
          <q-tab-panel name="estoque">
            <MovimentacaoEstoque />
          </q-tab-panel>

          <!-- ========================================= -->
          <!-- ABA APLICAÇÕES EM TERRENOS -->
          <!-- ========================================= -->
          <q-tab-panel name="aplicacoes">
            <AplicacoesTerrenos />
          </q-tab-panel>

          <!-- ========================================= -->
          <!-- ABA ANÁLISES DE SOLO -->
          <!-- ========================================= -->
          <q-tab-panel name="analises">
            <AnalisesSolo />
          </q-tab-panel>

          <!-- ========================================= -->
          <!-- ABA RELATÓRIOS -->
          <!-- ========================================= -->
          <q-tab-panel name="relatorios">
            <RelatoriosManejo />
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>
    </q-card>

    <!-- DIALOGS DE VISUALIZAÇÃO RÁPIDA (se necessário) -->
    <q-dialog v-model="quickViewDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">{{ quickViewTitle }}</div>
        </q-card-section>
        <q-card-section>
          <div class="text-body2">{{ quickViewContent }}</div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Fechar" color="grey" @click="quickViewDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useManejoStore } from 'stores/manejo'

// Importar componentes
import ProdutosManejo from 'components/manejo/ProdutosManejo.vue'
import MovimentacaoEstoque from 'components/manejo/MovimentacaoEstoque.vue'
import AplicacoesTerrenos from 'components/manejo/AplicacoesTerrenos.vue'
import AnalisesSolo from 'components/manejo/AnalisesSolo.vue'
import RelatoriosManejo from 'components/manejo/RelatoriosManejo.vue'

// Composables
const $q = useQuasar()
const manejoStore = useManejoStore()

// Estado reativo
const activeTab = ref('produtos') 
const quickViewDialog = ref(false)
const quickViewTitle = ref('')
const quickViewContent = ref('')

// Métodos

async function refreshAllData() {
  try {
    $q.loading.show({
      message: 'Atualizando dados...'
    })

    // Atualizar dados baseado na aba ativa
    switch (activeTab.value) {
      case 'produtos':
        // O componente ProdutosManejo tem seu próprio refresh
        await manejoStore.fetchProdutos()
        break
      case 'estoque':
        // Atualizar movimentações e alertas
        await manejoStore.fetchMovimentacoes()
        await manejoStore.getAlertasEstoque()
        break
      case 'aplicacoes':
        // Atualizar aplicações e terrenos em carência
        await manejoStore.fetchAplicacoes()
        await manejoStore.getTerrenosLiberacao()
        break
      case 'analises':
        // Atualizar análises de solo
        await manejoStore.fetchAnalisesSolo()
        break
      case 'relatorios':
        // Atualizar todos os relatórios
        await Promise.all([
          manejoStore.getConsumoTerreno(),
          manejoStore.getPrevisaoConsumo(),
          manejoStore.getTerrenosLiberacao(),
          manejoStore.getResumoEstoque()
        ])
        break
    }

    $q.notify({
      type: 'positive',
      message: 'Dados atualizados com sucesso!'
    })

  } catch (error) {
    console.error('Erro ao atualizar dados:', error)
    $q.notify({
      type: 'negative',
      message: 'Erro ao atualizar dados'
    })
  } finally {
    $q.loading.hide()
  }
}

// Funções para comunicação entre componentes (se necessário)
function showQuickView(title, content) {
  quickViewTitle.value = title
  quickViewContent.value = content
  quickViewDialog.value = true
}

// Watchers
watch(activeTab, async (newTab) => {
  // Carregar dados específicos quando trocar de aba
  
  try {
    switch (newTab) {
      case 'produtos':
        // ProdutosManejo carrega seus próprios dados
        break
      case 'estoque':
        // Carregar movimentações se ainda não foram carregadas
        if (manejoStore.movimentacoes.length === 0) {
          await manejoStore.fetchMovimentacoes()
        }
        break
      case 'aplicacoes':
        // Carregar aplicações se ainda não foram carregadas
        if (manejoStore.aplicacoes.length === 0) {
          await manejoStore.fetchAplicacoes()
        }
        // Carregar terrenos em carência
        await manejoStore.getTerrenosLiberacao(30)
        break
      case 'analises':
        // Carregar análises de solo se ainda não foram carregadas
        if (manejoStore.analisesSolo.length === 0) {
          await manejoStore.fetchAnalisesSolo()
        }
        break
      case 'relatorios':
        // Carregar relatórios quando implementado
        break
    }
  } catch (error) {
    console.error('Erro ao carregar dados da aba:', error)
  }
})


// Expor funções para componentes filhos (se necessário)
defineExpose({
  showQuickView,
  refreshAllData
})
</script>

<style scoped>

/* Melhorar espaçamento das abas */
.q-tabs {
  border-bottom: 1px solid #e0e0e0;
}

.q-tab-panel {
  padding: 16px 0;
}

/* Cards de placeholder */
.q-card.placeholder {
  border: 2px dashed #e0e0e0;
  background-color: #fafafa;
}

.placeholder .q-card-section {
  text-align: center;
  color: #999;
}
</style>