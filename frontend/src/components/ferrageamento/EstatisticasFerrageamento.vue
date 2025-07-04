<template>
  <div class="row q-gutter-md">
    <div class="col-md-6 col-12">
      <q-card>
        <q-card-section>
          <div class="text-h6">Estatísticas por Animal</div>
        </q-card-section>
        <q-card-section>
          <q-list
            bordered
            separator
          >
            <q-item
              v-for="stat in ferrageamentoStore.estatisticasAnimais"
              :key="stat.animal_id"
            >
              <q-item-section>
                <q-item-label>{{ stat.animal_nome }}</q-item-label>
                <q-item-label caption>
                  {{ stat.total_casqueamento }} registros de casqueamento -
                  Último: {{ formatDateForDisplay(stat.ultimo_casqueamento) }}
                </q-item-label>
                <q-item-label caption>
                  {{ stat.total_ferrageamento }} registros de ferrageamento -
                  Último: {{ formatDateForDisplay(stat.ultimo_ferrageamento) }}
                </q-item-label>
                <q-item-label caption>
                  Custo total: R$ {{ stat.custo_total?.toFixed(2) || '0,00' }}
                </q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-chip
                  :color="getStatusColor(stat.status_atual)"
                  text-color="white"
                  size="sm"
                >
                  {{ stat.status_atual }}
                </q-chip>
              </q-item-section>
            </q-item>
            <q-item v-if="ferrageamentoStore.estatisticasAnimais.length === 0">
              <q-item-section>
                <q-item-label class="text-center text-grey-6">
                  Nenhuma estatística disponível
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>
    </div>

    <div class="col-md-6 col-12">
      <q-card>
        <q-card-section>
          <div class="text-h6">Top Ferradores</div>
        </q-card-section>
        <q-card-section>
          <q-list
            bordered
            separator
          >
            <q-item
              v-for="ferrador in ferrageamentoStore.ferradoresMaisAtivos"
              :key="ferrador.nome"
            >
              <q-item-section>
                <q-item-label>{{ ferrador.nome }}</q-item-label>
                <q-item-label caption>
                  {{ ferrador.total }} serviços
                </q-item-label>
                <q-item-label caption>
                  Faturamento: R$ {{ ferrador.custo?.toFixed(2) || '0,00' }}
                </q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-avatar
                  color="primary"
                  text-color="white"
                >
                  {{ ferrador.total }}
                </q-avatar>
              </q-item-section>
            </q-item>
            <q-item v-if="ferrageamentoStore.ferradoresMaisAtivos.length === 0">
              <q-item-section>
                <q-item-label class="text-center text-grey-6">
                  Nenhum ferrador cadastrado
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>
    </div>

    <!-- Controles de Período -->
    <div class="col-12">
      <q-card>
        <q-card-section>
          <div class="text-h6">Filtros de Período</div>
          <div class="row q-gutter-md q-mt-md">
            <q-select
              v-model="periodoSelecionado"
              :options="opcoesPerido"
              label="Período"
              emit-value
              map-options
              @update:model-value="atualizarEstatisticas"
              class="col-3"
            />
            <q-btn
              color="primary"
              icon="refresh"
              label="Atualizar"
              @click="atualizarEstatisticas"
            />
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Gráfico de Custos -->
    <div class="col-12">
      <q-card>
        <q-card-section>
          <div class="text-h6">Evolução de Custos</div>
          <div
            v-if="dadosGrafico.length > 0"
            class="q-mt-md"
          >
            <canvas
              ref="chartCanvas"
              style="height: 400px"
            ></canvas>
          </div>
          <div
            v-else
            class="text-center q-pa-xl"
          >
            <q-icon
              name="show_chart"
              size="4rem"
              color="grey"
            />
            <div class="text-h6 text-grey q-mt-md">
              Sem dados para o período selecionado
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup>
  import { ref, onMounted, nextTick } from 'vue'
  import { useFerrageamentoStore } from 'stores/ferrageamento'
  import { formatDateForDisplay } from 'src/utils/dateUtils'
  import { Chart, registerables } from 'chart.js'
  import { ErrorHandler } from 'src/utils/errorHandler'

  // Store
  const ferrageamentoStore = useFerrageamentoStore()

  // Estado reativo
  const periodoSelecionado = ref(6)
  const dadosGrafico = ref([])
  const chartCanvas = ref(null)
  const chartInstance = ref(null)

  // Registrar Chart.js
  Chart.register(...registerables)

  // Opções
  const opcoesPerido = [
    { value: 3, label: '3 meses' },
    { value: 6, label: '6 meses' },
    { value: 12, label: '12 meses' },
    { value: 24, label: '24 meses' },
  ]

  // Métodos
  async function atualizarEstatisticas() {
    try {
      await ferrageamentoStore.fetchEstatisticasAnimais(
        periodoSelecionado.value
      )
      await carregarDadosGrafico()
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao atualizar estatísticas')
    }
  }

  async function carregarDadosGrafico() {
    try {
      dadosGrafico.value = await ferrageamentoStore.getCustosEvolucaoMensal(
        periodoSelecionado.value
      )
      await nextTick()
      criarGrafico()
    } catch {
      dadosGrafico.value = []
    }
  }

  function criarGrafico() {
    if (chartInstance.value) {
      chartInstance.value.destroy()
    }

    const ctx = chartCanvas.value.getContext('2d')
    chartInstance.value = new Chart(ctx, {
      type: 'line',
      data: {
        labels: dadosGrafico.value.map(d => d.mes),
        datasets: [
          {
            label: 'Custos (R$)',
            data: dadosGrafico.value.map(d => d.custo_total),
            borderColor: '#1976d2',
            backgroundColor: 'rgba(25, 118, 210, 0.1)',
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
      },
    })
  }

  function getStatusColor(status) {
    const colors = {
      EM_DIA: 'positive',
      PROXIMO_VENCIMENTO: 'warning',
      VENCIDO: 'negative',
      BOM: 'positive',
      REGULAR: 'warning',
      RUIM: 'negative',
    }
    return colors[status] || 'grey'
  }

  // Lifecycle
  onMounted(() => {
    atualizarEstatisticas()
  })
</script>
