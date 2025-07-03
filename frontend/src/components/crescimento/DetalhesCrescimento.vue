<template>
  <div>
    <!-- Modal de Visualização -->
    <q-dialog v-model="viewDialog" persistent>
      <q-card style="min-width: 600px;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Detalhes da Medição</div>
          <q-space />
          <q-btn icon="close" flat round dense @click="closeDialog" />
        </q-card-section>

        <q-card-section v-if="medicaoData">
          <div class="row q-gutter-md">
            <div class="col-6">
              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label overline>Animal</q-item-label>
                    <q-item-label>{{ medicaoData.animal_nome }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label overline>Data da Medição</q-item-label>
                    <q-item-label>{{ formatDate(medicaoData.DATA_MEDICAO) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="medicaoData.dias_desde_ultima">
                  <q-item-section>
                    <q-item-label overline>Intervalo</q-item-label>
                    <q-item-label>{{ medicaoData.dias_desde_ultima }} dias</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <div class="col-6">
              <q-list>
                <q-item v-if="medicaoData.PESO">
                  <q-item-section>
                    <q-item-label overline>Peso</q-item-label>
                    <q-item-label>{{ medicaoData.PESO }} kg</q-item-label>
                  </q-item-section>
                  <q-item-section side v-if="medicaoData.variacao_peso">
                    <q-chip 
                      :color="medicaoData.variacao_peso > 0 ? 'positive' : 'negative'"
                      text-color="white"
                      size="sm"
                    >
                      {{ medicaoData.variacao_peso > 0 ? '+' : '' }}{{ medicaoData.variacao_peso.toFixed(1) }}
                    </q-chip>
                  </q-item-section>
                </q-item>
                <q-item v-if="medicaoData.ALTURA">
                  <q-item-section>
                    <q-item-label overline>Altura</q-item-label>
                    <q-item-label>{{ medicaoData.ALTURA }} cm</q-item-label>
                  </q-item-section>
                  <q-item-section side v-if="medicaoData.variacao_altura">
                    <q-chip 
                      :color="medicaoData.variacao_altura > 0 ? 'positive' : 'negative'"
                      text-color="white"
                      size="sm"
                    >
                      {{ medicaoData.variacao_altura > 0 ? '+' : '' }}{{ medicaoData.variacao_altura.toFixed(1) }}
                    </q-chip>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>

          <!-- Medidas Complementares -->
          <div v-if="temMedidasComplementares" class="q-mt-md">
            <q-separator />
            <div class="text-subtitle2 q-mt-md q-mb-sm">Medidas Complementares</div>
            <div class="row q-gutter-md">
              <div class="col-6">
                <q-list dense>
                  <q-item v-if="medicaoData.CIRCUNFERENCIA_TORACICA">
                    <q-item-section>
                      <q-item-label caption>Circunferência Torácica</q-item-label>
                      <q-item-label>{{ medicaoData.CIRCUNFERENCIA_TORACICA }} cm</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item v-if="medicaoData.COMPRIMENTO_CORPO">
                    <q-item-section>
                      <q-item-label caption>Comprimento do Corpo</q-item-label>
                      <q-item-label>{{ medicaoData.COMPRIMENTO_CORPO }} cm</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item v-if="medicaoData.CIRCUNFERENCIA_CANELA">
                    <q-item-section>
                      <q-item-label caption>Circunferência da Canela</q-item-label>
                      <q-item-label>{{ medicaoData.CIRCUNFERENCIA_CANELA }} cm</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
              <div class="col-6">
                <q-list dense>
                  <q-item v-if="medicaoData.ALTURA_ANTERIOR">
                    <q-item-section>
                      <q-item-label caption>Altura Anterior</q-item-label>
                      <q-item-label>{{ medicaoData.ALTURA_ANTERIOR }} cm</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item v-if="medicaoData.ALTURA_POSTERIOR">
                    <q-item-section>
                      <q-item-label caption>Altura Posterior</q-item-label>
                      <q-item-label>{{ medicaoData.ALTURA_POSTERIOR }} cm</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item v-if="medicaoData.LARGURA_PEITO">
                    <q-item-section>
                      <q-item-label caption>Largura do Peito</q-item-label>
                      <q-item-label>{{ medicaoData.LARGURA_PEITO }} cm</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
            </div>
          </div>

          <!-- Observações -->
          <div v-if="medicaoData.OBSERVACOES" class="q-mt-md">
            <q-separator />
            <div class="text-subtitle2 q-mt-md q-mb-sm">Observações</div>
            <div class="text-body2">{{ medicaoData.OBSERVACOES }}</div>
          </div>

          <!-- Informações de Registro -->
          <div class="q-mt-md">
            <q-separator />
            <div class="text-caption text-grey q-mt-md">
              Registrado em {{ formatDate(medicaoData.DATA_CADASTRO) }}
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn 
            flat 
            label="Ver Gráfico" 
            color="primary" 
            @click="openGrafico"
            icon="show_chart"
          />
          <q-btn flat label="Fechar" color="grey" @click="closeDialog" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Modal do Gráfico Individual -->
    <q-dialog v-model="graficoDialog" persistent>
      <q-card style="min-width: 800px; max-width: 1200px;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Evolução - {{ animalSelecionado?.nome }}</div>
          <q-space />
          <q-btn icon="close" flat round dense @click="graficoDialog = false" />
        </q-card-section>

        <q-card-section>
          <div class="row q-gutter-md">
            <q-card class="col-6">
              <q-card-section>
                <div class="text-h6">Evolução do Peso</div>
                <crescimento-chart 
                  :dados="dadosGraficoPeso"
                  tipo="peso"
                  height="350px"
                  :show-stats="true"
                  :show-trend="true"
                />
              </q-card-section>
            </q-card>
            
            <q-card class="col-6">
              <q-card-section>
                <div class="text-h6">Evolução da Altura</div>
                <crescimento-chart 
                  :dados="dadosGraficoAltura"
                  tipo="altura"
                  height="350px"
                  :show-stats="true"
                  :show-trend="true"
                />
              </q-card-section>
            </q-card>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Fechar" color="grey" @click="graficoDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCrescimentoStore } from 'stores/crescimento'
import { formatDate } from 'src/utils/dateUtils'
import CrescimentoChart from 'components/crescimento/CrescimentoChart.vue'

// Stores
const crescimentoStore = useCrescimentoStore()

// Estado reativo
const viewDialog = ref(false)
const graficoDialog = ref(false)
const medicaoData = ref(null)
const animalSelecionado = ref(null)

// Computed
const temMedidasComplementares = computed(() => {
  if (!medicaoData.value) return false
  
  return medicaoData.value.CIRCUNFERENCIA_TORACICA ||
         medicaoData.value.COMPRIMENTO_CORPO ||
         medicaoData.value.CIRCUNFERENCIA_CANELA ||
         medicaoData.value.ALTURA_ANTERIOR ||
         medicaoData.value.ALTURA_POSTERIOR ||
         medicaoData.value.LARGURA_PEITO
})

const dadosGraficoPeso = computed(() => {
  if (!animalSelecionado.value?.id) return []
  return crescimentoStore.dadosGraficoPeso(animalSelecionado.value.id)
})

const dadosGraficoAltura = computed(() => {
  if (!animalSelecionado.value?.id) return []
  return crescimentoStore.dadosGraficoAltura(animalSelecionado.value.id)
})

// Métodos
function openViewDialog(medicao) {
  medicaoData.value = medicao
  viewDialog.value = true
}

function openGrafico() {
  if (!medicaoData.value) return
  
  animalSelecionado.value = {
    id: medicaoData.value.ID_ANIMAL,
    nome: medicaoData.value.animal_nome
  }
  graficoDialog.value = true
}

function closeDialog() {
  viewDialog.value = false
  medicaoData.value = null
}

// Expor métodos
defineExpose({
  openViewDialog
})
</script>