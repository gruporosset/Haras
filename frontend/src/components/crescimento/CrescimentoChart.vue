<template>
  <div class="crescimento-chart">
    <div
      v-if="dadosProcessados.length === 0"
      class="text-center q-pa-xl"
    >
      <q-icon
        name="show_chart"
        size="3rem"
        color="grey"
      />
      <div class="text-h6 text-grey q-mt-md">Sem dados para exibir</div>
      <div class="text-caption text-grey">
        Adicione medições para visualizar o gráfico
      </div>
    </div>

    <div
      v-else
      class="chart-container"
      :style="{ height }"
    >
      <!-- Cabeçalho do gráfico -->
      <div class="chart-header q-mb-md">
        <div class="row items-center justify-between">
          <div>
            <div class="text-subtitle1">{{ tituloGrafico }}</div>
            <div class="text-caption text-grey">{{ descricaoGrafico }}</div>
          </div>
          <div class="row q-gutter-sm">
            <q-btn-toggle
              v-model="tipoVisualizacao"
              :options="opcoesVisualizacao"
              size="sm"
              @update:model-value="atualizarGrafico"
            />
            <q-btn
              flat
              size="sm"
              icon="refresh"
              @click="atualizarGrafico"
              :loading="loading"
            />
          </div>
        </div>
      </div>

      <!-- Canvas do gráfico -->
      <canvas
        ref="chartCanvas"
        :style="{ height: alturaCanvas }"
      ></canvas>

      <!-- Legenda personalizada -->
      <div class="chart-legend q-mt-md">
        <div class="row q-gutter-md items-center justify-center">
          <div
            v-for="item in legendaItems"
            :key="item.label"
            class="row items-center"
          >
            <div
              class="legend-color q-mr-xs"
              :style="{ backgroundColor: item.cor }"
            ></div>
            <span class="text-caption">{{ item.label }}</span>
          </div>
        </div>
      </div>

      <!-- Estatísticas do gráfico -->
      <div
        v-if="estatisticas"
        class="chart-stats q-mt-md"
      >
        <q-card
          flat
          bordered
        >
          <q-card-section class="q-pa-sm">
            <div class="row q-gutter-md text-center">
              <div class="col">
                <div class="text-h6 text-primary">{{ estatisticas.total }}</div>
                <div class="text-caption">Total Medições</div>
              </div>
              <div class="col">
                <div
                  class="text-h6"
                  :class="
                    estatisticas.tendencia > 0
                      ? 'text-positive'
                      : 'text-negative'
                  "
                >
                  {{ estatisticas.tendencia > 0 ? '+' : ''
                  }}{{ estatisticas.tendencia }}
                </div>
                <div class="text-caption">
                  {{ tipo === 'peso' ? 'kg' : 'cm' }} (tendência)
                </div>
              </div>
              <div class="col">
                <div class="text-h6 text-accent">
                  {{ estatisticas.periodo }}d
                </div>
                <div class="text-caption">Período</div>
              </div>
              <div class="col">
                <div class="text-h6 text-secondary">
                  {{ estatisticas.media }}
                </div>
                <div class="text-caption">
                  {{ tipo === 'peso' ? 'kg' : 'cm' }} (média)
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {
    ref,
    computed,
    onMounted,
    onBeforeUnmount,
    watch,
    nextTick,
  } from 'vue'
  import { Chart, registerables } from 'chart.js'

  // Registrar todos os componentes do Chart.js
  Chart.register(...registerables)

  // Props
  const props = defineProps({
    dados: {
      type: Array,
      required: true,
    },
    tipo: {
      type: String,
      default: 'peso', // peso, altura
      validator: value => ['peso', 'altura'].includes(value),
    },
    height: {
      type: String,
      default: '400px',
    },
    showStats: {
      type: Boolean,
      default: true,
    },
    showTrend: {
      type: Boolean,
      default: true,
    },
  })

  // Estado reativo
  const chartCanvas = ref(null)
  const chartInstance = ref(null)
  const loading = ref(false)
  const tipoVisualizacao = ref('line')

  // Opções de visualização
  const opcoesVisualizacao = [
    { label: 'Linha', value: 'line', icon: 'show_chart' },
    { label: 'Barras', value: 'bar', icon: 'bar_chart' },
    { label: 'Área', value: 'area', icon: 'area_chart' },
  ]

  // Computed
  const alturaCanvas = computed(() => {
    const altura = parseInt(props.height)
    return `${altura - 120}px` // Subtraindo espaço para header e stats
  })

  const dadosProcessados = computed(() => {
    if (!props.dados || props.dados.length === 0) return []

    // Ordenar por data
    return [...props.dados].sort((a, b) => new Date(a.data) - new Date(b.data))
  })

  const tituloGrafico = computed(() => {
    const titulos = {
      peso: 'Evolução do Peso',
      altura: 'Evolução da Altura',
    }
    return titulos[props.tipo] || 'Evolução'
  })

  const descricaoGrafico = computed(() => {
    if (dadosProcessados.value.length === 0) return ''

    const primeiro = dadosProcessados.value[0]
    const ultimo = dadosProcessados.value[dadosProcessados.value.length - 1]

    return `${formatarData(primeiro.data)} até ${formatarData(ultimo.data)}`
  })

  const legendaItems = computed(() => {
    const items = []

    if (props.tipo === 'peso') {
      items.push({ label: 'Peso (kg)', cor: '#1976d2' })
      if (props.showTrend) {
        items.push({ label: 'Tendência', cor: '#ff9800' })
      }
    } else {
      items.push({ label: 'Altura (cm)', cor: '#388e3c' })
      if (props.showTrend) {
        items.push({ label: 'Tendência', cor: '#ff9800' })
      }
    }

    return items
  })

  const estatisticas = computed(() => {
    if (!props.showStats || dadosProcessados.value.length === 0) return null

    const valores = dadosProcessados.value
      .map(d => (props.tipo === 'peso' ? d.peso : d.altura))
      .filter(v => v != null)

    if (valores.length === 0) return null

    const total = valores.length
    const soma = valores.reduce((acc, val) => acc + val, 0)
    const media = (soma / total).toFixed(1)

    // Calcular tendência (diferença entre último e primeiro)
    const primeiro = valores[0]
    const ultimo = valores[valores.length - 1]
    const tendencia = (ultimo - primeiro).toFixed(1)

    // Calcular período em dias
    const dataInicial = new Date(dadosProcessados.value[0].data)
    const dataFinal = new Date(
      dadosProcessados.value[dadosProcessados.value.length - 1].data
    )
    const periodo = Math.ceil((dataFinal - dataInicial) / (1000 * 60 * 60 * 24))

    return {
      total,
      media,
      tendencia: parseFloat(tendencia),
      periodo,
    }
  })

  // Funções
  function formatarData(data) {
    return new Date(data).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    })
  }

  function calcularLinhaTendencia(dados) {
    const n = dados.length
    if (n < 2) return []

    // Calcular regressão linear simples
    let somaX = 0,
      somaY = 0,
      somaXY = 0,
      somaX2 = 0

    dados.forEach((ponto, index) => {
      somaX += index
      somaY += ponto.y
      somaXY += index * ponto.y
      somaX2 += index * index
    })

    const inclinacao =
      (n * somaXY - somaX * somaY) / (n * somaX2 - somaX * somaX)
    const intercepto = (somaY - inclinacao * somaX) / n

    // Gerar pontos da linha de tendência
    return dados.map((_, index) => ({
      x: dados[index].x,
      y: inclinacao * index + intercepto,
    }))
  }

  function configurarGrafico() {
    if (!chartCanvas.value || dadosProcessados.value.length === 0) return

    const ctx = chartCanvas.value.getContext('2d')

    // Preparar dados para o Chart.js
    const labels = dadosProcessados.value.map(d => formatarData(d.data))
    const valores = dadosProcessados.value.map(d =>
      props.tipo === 'peso' ? d.peso : d.altura
    )

    // Dataset principal
    const datasets = [
      {
        label: props.tipo === 'peso' ? 'Peso (kg)' : 'Altura (cm)',
        data: valores,
        borderColor: props.tipo === 'peso' ? '#1976d2' : '#388e3c',
        backgroundColor:
          props.tipo === 'peso'
            ? 'rgba(25, 118, 210, 0.1)'
            : 'rgba(56, 142, 60, 0.1)',
        borderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        fill: tipoVisualizacao.value === 'area',
        tension: 0.4,
      },
    ]

    // Adicionar linha de tendência se habilitada
    if (props.showTrend && valores.length > 1) {
      const dadosTendencia = valores.map((valor, index) => ({
        x: index,
        y: valor,
      }))
      const linhaTendencia = calcularLinhaTendencia(dadosTendencia)

      datasets.push({
        label: 'Tendência',
        data: linhaTendencia.map(p => p.y),
        borderColor: '#ff9800',
        backgroundColor: 'transparent',
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false,
      })
    }

    // Configuração do gráfico
    const config = {
      type: tipoVisualizacao.value === 'area' ? 'line' : tipoVisualizacao.value,
      data: {
        labels,
        datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false, // Usando legenda customizada
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
              label: function (context) {
                const unidade = props.tipo === 'peso' ? 'kg' : 'cm'
                return `${context.dataset.label}: ${context.parsed.y} ${unidade}`
              },
            },
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Data da Medição',
            },
            grid: {
              display: false,
            },
          },
          y: {
            title: {
              display: true,
              text: props.tipo === 'peso' ? 'Peso (kg)' : 'Altura (cm)',
            },
            beginAtZero: false,
            grid: {
              color: 'rgba(0, 0, 0, 0.1)',
            },
          },
        },
        interaction: {
          mode: 'nearest',
          axis: 'x',
          intersect: false,
        },
      },
    }

    // Destruir gráfico anterior se existir
    if (chartInstance.value) {
      chartInstance.value.destroy()
    }

    // Criar novo gráfico
    chartInstance.value = new Chart(ctx, config)
  }

  async function atualizarGrafico() {
    loading.value = true

    await nextTick()
    configurarGrafico()

    setTimeout(() => {
      loading.value = false
    }, 300)
  }

  // Lifecycle
  onMounted(() => {
    nextTick(() => {
      configurarGrafico()
    })
  })

  onBeforeUnmount(() => {
    if (chartInstance.value) {
      chartInstance.value.destroy()
    }
  })

  // Watchers
  watch(
    () => props.dados,
    () => {
      atualizarGrafico()
    },
    { deep: true }
  )

  watch(
    () => props.tipo,
    () => {
      atualizarGrafico()
    }
  )
</script>

<style scoped>
  .crescimento-chart {
    width: 100%;
  }

  .chart-container {
    position: relative;
  }

  .chart-header {
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 8px;
  }

  .legend-color {
    width: 12px;
    height: 12px;
    border-radius: 2px;
  }

  .chart-stats {
    border-top: 1px solid #e0e0e0;
    padding-top: 8px;
  }

  canvas {
    max-height: 100%;
  }

  .q-btn-toggle {
    background: transparent;
  }
</style>
