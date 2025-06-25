<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md text-primary">
      <q-icon name="landscape" class="q-mr-sm" />
      Manejo de Terrenos
    </div>

    <q-card>
      <q-card-section>
        <!-- Filtros Globais (opcional - podem ser movidos para cada componente) -->
        <div class="col-12 q-mb-md">
          <q-card flat bordered class="q-pa-md">
            <div class="row q-gutter-md">
              <div class="col-md-3 col-12">
                <q-select
                  v-model="globalFilters.terreno_id"
                  :options="terrenoOptions"
                  label="Filtrar por Terreno"
                  clearable
                  use-input
                  @filter="filterTerrenos"
                  @update:model-value="onGlobalFilterChange"
                />
              </div>
              <div class="col-md-2 col-12">
                <calendario-component
                  v-model="globalFilters.data_inicio"
                  label="Data Início"
                  @update:model-value="onGlobalFilterChange"
                />
              </div>
              <div class="col-md-2 col-12">
                <calendario-component
                  v-model="globalFilters.data_fim"
                  label="Data Fim"
                  @update:model-value="onGlobalFilterChange"
                />
              </div>
              <div class="col-auto">
                <q-btn
                  flat
                  color="primary"
                  icon="refresh"
                  label="Atualizar"
                  @click="refreshAllData"
                />
              </div>
            </div>
          </q-card>
        </div>
        
        <!-- Abas dos Módulos -->
        <q-tabs v-model="activeTab" class="q-mb-md" align="left">
          <q-tab name="produtos" icon="inventory_2" label="Produtos Manejo" />
          <q-tab name="estoque" icon="inventory" label="Movimentação Estoque" />
          <q-tab name="aplicacoes" icon="agriculture" label="Aplicações Terrenos" />
          <q-tab name="analises" icon="biotech" label="Análises de Solo" />
          <q-tab name="relatorios" icon="analytics" label="Relatórios" />
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
import { ref, onMounted, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useManejoStore } from 'stores/manejo'
import { useTerrenoStore } from 'stores/terreno'

// Importar componentes
import ProdutosManejo from 'components/manejo/ProdutosManejo.vue'
import MovimentacaoEstoque from 'components/manejo/MovimentacaoEstoque.vue'
import AplicacoesTerrenos from 'components/manejo/AplicacoesTerrenos.vue'
import AnalisesSolo from 'components/manejo/AnalisesSolo.vue'
import RelatoriosManejo from 'components/manejo/RelatoriosManejo.vue'
import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

// Composables
const $q = useQuasar()
const manejoStore = useManejoStore()
const terrenoStore = useTerrenoStore()

// Estado reativo
const activeTab = ref('relatorios') // Iniciar na aba de análises para testar
const quickViewDialog = ref(false)
const quickViewTitle = ref('')
const quickViewContent = ref('')

// Filtros globais (opcionais)
const globalFilters = ref({
  terreno_id: null,
  data_inicio: '',
  data_fim: ''
})

// Opções para selects
const terrenoOptions = ref([])

// Métodos
async function loadInitialData() {
  try {
    // Carregar opções de terrenos
    await terrenoStore.fetchTerrenos({ limit: 100 })
    terrenoOptions.value = terrenoStore.terrenos.map(t => ({
      value: t.ID,
      label: t.NOME
    }))

    // Carregar dados iniciais do manejo (se necessário)
    // Cada componente carregará seus próprios dados
    
  } catch (error) {
    console.error('Erro ao carregar dados iniciais:', error)
    $q.notify({
      type: 'negative',
      message: 'Erro ao carregar dados iniciais'
    })
  }
}

function filterTerrenos(val, update) {
  update(() => {
    if (val === '') {
      terrenoOptions.value = terrenoStore.terrenos.map(t => ({
        value: t.ID,
        label: t.NOME
      }))
    } else {
      const needle = val.toLowerCase()
      terrenoOptions.value = terrenoStore.terrenos
        .filter(t => t.NOME.toLowerCase().includes(needle))
        .map(t => ({
          value: t.ID,
          label: t.NOME
        }))
    }
  })
}

function onGlobalFilterChange() {
  // Aplicar filtros globais se implementado
  console.log('Filtros globais alterados:', globalFilters.value)
  
  // Notificar componentes filhos sobre mudança de filtros (se necessário)
  // Por enquanto, cada componente gerencia seus próprios filtros
}

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
  console.log('Aba ativa:', newTab)
  
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

// Lifecycle
onMounted(async () => {
  await loadInitialData()
  
  // Carregar dados da aba inicial (produtos)
  try {
    // ProdutosManejo carregará seus próprios dados automaticamente
  } catch (error) {
    console.error('Erro ao carregar dados iniciais da aba:', error)
  }
})

// Expor funções para componentes filhos (se necessário)
defineExpose({
  showQuickView,
  globalFilters,
  refreshAllData
})
</script>

<style scoped>
/* Estilos específicos da página */
.q-page {
  max-width: 1400px;
  margin: 0 auto;
}

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