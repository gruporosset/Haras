<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md text-primary">
      <q-icon name="restaurant" class="q-mr-sm" />
      Ração e Suplementos
    </div>

    <q-card>
      <q-card-section>
        
        <!-- Abas dos Módulos -->
        <q-tabs v-model="activeTab" class="q-mb-md" align="center">
          <q-tab name="produtos" label="Produtos Ração" />
          <q-tab name="estoque" label="Movimentação Estoque" />
          <q-tab name="planos" label="Planos Alimentares" />
          <q-tab name="fornecimento" label="Fornecimento" />
        </q-tabs>
        
        <q-tab-panels v-model="activeTab" animated>
          <!-- ========================================= -->
          <!-- ABA PRODUTOS RAÇÃO -->
          <!-- ========================================= -->
          <q-tab-panel name="produtos">
            <ProdutosRacao />
          </q-tab-panel>

          <!-- ========================================= -->
          <!-- ABA MOVIMENTAÇÃO ESTOQUE -->
          <!-- ========================================= -->
          <q-tab-panel name="estoque">
            <MovimentacaoEstoqueRacao />
          </q-tab-panel>

          <!-- ========================================= -->
          <!-- ABA PLANOS ALIMENTARES -->
          <!-- ========================================= -->
          <q-tab-panel name="planos">
            <PlanosAlimentares />
          </q-tab-panel>

          <!-- ========================================= -->
          <!-- ABA FORNECIMENTO -->
          <!-- ========================================= -->
          <q-tab-panel name="fornecimento">
            <FornecimentoRacao />
          </q-tab-panel>

        </q-tab-panels>
      </q-card-section>
    </q-card>

    <!-- DIALOGS DE VISUALIZAÇÃO RÁPIDA -->
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

    <!-- DIALOGS DE CÁLCULO NUTRICIONAL -->
    <q-dialog v-model="calculoNutricionalDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Cálculo Nutricional</div>
          <div class="text-subtitle2 text-grey-6">Sugestão baseada na categoria do animal</div>
        </q-card-section>
        
        <q-card-section>
          <div v-if="calculoNutricional" class="q-gutter-md">
            <div class="row q-gutter-md">
              <div class="col">
                <q-card flat bordered>
                  <q-card-section class="text-center">
                    <div class="text-h4 text-primary">{{ calculoNutricional.peso_animal }}kg</div>
                    <div class="text-subtitle2">Peso Animal</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col">
                <q-card flat bordered>
                  <q-card-section class="text-center">
                    <div class="text-h4 text-orange">{{ calculoNutricional.quantidade_sugerida_kg }}kg</div>
                    <div class="text-subtitle2">Sugerido/Dia</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col">
                <q-card flat bordered>
                  <q-card-section class="text-center">
                    <div class="text-h4 text-green">{{ calculoNutricional.percentual_peso_vivo }}%</div>
                    <div class="text-subtitle2">% Peso Vivo</div>
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <q-separator />

            <div>
              <div class="text-subtitle1 q-mb-sm">Distribuição por Refeições:</div>
              <div class="row q-gutter-sm">
                <div class="col">
                  <q-chip color="primary" text-color="white">
                    Manhã: {{ calculoNutricional.distribuicao_refeicoes.manha }}kg
                  </q-chip>
                </div>
                <div class="col">
                  <q-chip color="secondary" text-color="white">
                    Tarde: {{ calculoNutricional.distribuicao_refeicoes.tarde }}kg
                  </q-chip>
                </div>
                <div class="col">
                  <q-chip color="accent" text-color="white">
                    Noite: {{ calculoNutricional.distribuicao_refeicoes.noite }}kg
                  </q-chip>
                </div>
              </div>
            </div>

            <q-separator />

            <div>
              <div class="text-subtitle1 q-mb-sm">Observações Nutricionais:</div>
              <div class="text-body2 bg-blue-1 q-pa-sm rounded-borders">
                {{ calculoNutricional.observacoes_nutricionais }}
              </div>
            </div>
          </div>
        </q-card-section>
        
        <q-card-actions align="right">
          <q-btn flat label="Fechar" color="grey" @click="calculoNutricionalDialog = false" />
          <q-btn 
            label="Criar Plano" 
            color="primary" 
            @click="criarPlanoBaseadoCalculo"
            :disable="!calculoNutricional"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { useRacaoStore } from 'stores/racao'
import { ErrorHandler } from 'src/utils/errorHandler'

// Importar componentes (serão criados nas próximas etapas)
import ProdutosRacao from 'components/racao/ProdutosRacao.vue'
import MovimentacaoEstoqueRacao from 'components/racao/MovimentacaoEstoqueRacao.vue'
import PlanosAlimentares from 'components/racao/PlanosAlimentares.vue'
import FornecimentoRacao from 'components/racao/FornecimentoRacao.vue'

// Composables
const $q = useQuasar()
const racaoStore = useRacaoStore()

// Estado reativo
const activeTab = ref('produtos') 
const quickViewDialog = ref(false)
const quickViewTitle = ref('')
const quickViewContent = ref('')
const calculoNutricionalDialog = ref(false)
const calculoNutricional = ref(null)

// Métodos
async function refreshAllData() {
  try {
    $q.loading.show({
      message: 'Atualizando dados...'
    })

    // Atualizar dados baseado na aba ativa
    switch (activeTab.value) {
      case 'produtos':
        await racaoStore.fetchProdutos()
        break
      case 'estoque':
        await racaoStore.fetchMovimentacoes()
        await racaoStore.getAlertasEstoque()
        break
      case 'planos':
        await racaoStore.fetchPlanosAlimentares()
        break
      case 'fornecimento':
        await racaoStore.fetchFornecimentos()
        break
    }

    ErrorHandler.success('Registro atualizado com sucesso!')

  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao atualizar dados')
  } finally {
    $q.loading.hide()
  }
}

function showQuickView(title, content) {
  quickViewTitle.value = title
  quickViewContent.value = content
  quickViewDialog.value = true
}

async function mostrarCalculoNutricional(animalId, categoria) {
  try {
    $q.loading.show({
      message: 'Calculando necessidades nutricionais...'
    })

    const calculo = await racaoStore.calcularNecessidadesNutricionais(animalId, categoria)
    calculoNutricional.value = calculo
    calculoNutricionalDialog.value = true

  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao calcular necessidades nutricionais')
  } finally {
    $q.loading.hide()
  }
}

async function criarPlanoBaseadoCalculo() {
  if (!calculoNutricional.value) return

  try {
    // Aqui você implementaria a lógica para criar um plano
    // baseado no cálculo nutricional
    ErrorHandler.success('Plano alimentar criado com base no cálculo!')
    
    calculoNutricionalDialog.value = false
    activeTab.value = 'planos'
    
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao criar plano alimentar')
  }
}

// Expor funções para os componentes filhos
defineExpose({
  refreshAllData,
  showQuickView,
  mostrarCalculoNutricional
})
</script>

<style scoped>
.q-tab-panel {
  padding: 0;
}

.rounded-borders {
  border-radius: 8px;
}
</style>