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
            <div class="text-h6 q-mb-md">Movimentação de Estoque</div>
            <div class="text-body2 text-grey-7">
              Componente em desenvolvimento...
            </div>
            
            <!-- PLACEHOLDER - será substituído pelo componente -->
            <q-card flat class="q-mt-md">
              <q-card-section>
                <div class="row q-gutter-md">
                  <q-btn color="positive" icon="add_box" label="Entrada Estoque" />
                  <q-btn color="negative" icon="remove_circle" label="Saída Estoque" />
                  <q-btn color="warning" icon="build" label="Ajuste Estoque" />
                </div>
              </q-card-section>
            </q-card>
          </q-tab-panel>

          <!-- ========================================= -->
          <!-- ABA APLICAÇÕES EM TERRENOS -->
          <!-- ========================================= -->
          <q-tab-panel name="aplicacoes">
            <div class="text-h6 q-mb-md">Aplicações em Terrenos</div>
            <div class="text-body2 text-grey-7">
              Componente em desenvolvimento...
            </div>
            
            <!-- PLACEHOLDER -->
            <q-card flat class="q-mt-md">
              <q-card-section>
                <div class="row q-gutter-md">
                  <q-btn color="primary" icon="add" label="Nova Aplicação" />
                  <q-btn color="info" icon="schedule" label="Cronograma" />
                </div>
              </q-card-section>
            </q-card>
          </q-tab-panel>

          <!-- ========================================= -->
          <!-- ABA ANÁLISES DE SOLO -->
          <!-- ========================================= -->
          <q-tab-panel name="analises">
            <div class="text-h6 q-mb-md">Análises de Solo</div>
            <div class="text-body2 text-grey-7">
              Componente em desenvolvimento...
            </div>
            
            <!-- PLACEHOLDER -->
            <q-card flat class="q-mt-md">
              <q-card-section>
                <div class="row q-gutter-md">
                  <q-btn color="primary" icon="add" label="Nova Análise" />
                  <q-btn color="secondary" icon="upload_file" label="Upload Laudo" />
                </div>
              </q-card-section>
            </q-card>
          </q-tab-panel>

          <!-- ========================================= -->
          <!-- ABA RELATÓRIOS -->
          <!-- ========================================= -->
          <q-tab-panel name="relatorios">
            <div class="text-h6 q-mb-md">Relatórios e Análises</div>
            <div class="text-body2 text-grey-7">
              Componente em desenvolvimento...
            </div>
            
            <!-- PLACEHOLDER -->
            <q-card flat class="q-mt-md">
              <q-card-section>
                <div class="row q-gutter-md">
                  <q-btn color="accent" icon="bar_chart" label="Consumo por Terreno" />
                  <q-btn color="deep-orange" icon="trending_up" label="Previsão Consumo" />
                  <q-btn color="teal" icon="schedule" label="Terrenos Liberação" />
                </div>
              </q-card-section>
            </q-card>
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
import { useManejoStore } from '../stores/manejo'
import { useTerrenoStore } from '../stores/terreno'
import { useAuthStore } from '../stores/auth'

// Importar componentes
import ProdutosManejo from 'components/ProdutosManejo.vue'
import CalendarioComponent from 'components/CalendarioComponent.vue'

// Composables
const $q = useQuasar()
const manejoStore = useManejoStore()
const terrenoStore = useTerrenoStore()
const authStore = useAuthStore()

if (manejoStore) {
  console.log('Manejo Store loaded:', manejoStore)
}

if (authStore) {
  console.log('Auth Store loaded:', authStore)
}

// Estado reativo
const activeTab = ref('produtos') // Iniciar na aba de produtos
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
        break
      case 'estoque':
        // Implementar quando criar o componente
        break
      case 'aplicacoes':
        // Implementar quando criar o componente
        break
      case 'analises':
        // Implementar quando criar o componente
        break
      case 'relatorios':
        // Implementar quando criar o componente
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
watch(activeTab, (newTab) => {
  // Fazer algo quando a aba muda (se necessário)
  console.log('Aba ativa:', newTab)
})

// Lifecycle
onMounted(async () => {
  await loadInitialData()
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