<template>
  <div class="row q-gutter-md">
    <!-- Gráfico de Custos Mensais -->
    <div class="col-12 col-md-6">
      <q-card>
        <q-card-section>
          <div class="text-h6">
            <q-icon name="trending_up" class="q-mr-sm" />
            {{ graficoCustos?.titulo || 'Custos Mensais' }}
          </div>
        </q-card-section>
        
        <q-card-section v-if="!graficoCustos" class="text-center text-grey">
          <q-spinner size="48px" />
          <div class="q-mt-sm">Carregando gráfico...</div>
        </q-card-section>
        
        <q-card-section v-else>
          <canvas 
            ref="graficoBarrasCanvas" 
            style="max-height: 300px;"
          ></canvas>
        </q-card-section>
      </q-card>
    </div>

    <!-- Gráfico de Distribuição de Animais -->
    <div class="col-12 col-md-6">
      <q-card>
        <q-card-section>
          <div class="text-h6">
            <q-icon name="donut_small" class="q-mr-sm" />
            {{ graficoAnimais?.titulo || 'Distribuição de Animais' }}
          </div>
        </q-card-section>
        
        <q-card-section v-if="!graficoAnimais" class="text-center text-grey">
          <q-spinner size="48px" />
          <div class="q-mt-sm">Carregando gráfico...</div>
        </q-card-section>
        
        <q-card-section v-else class="text-center">
          <canvas 
            ref="graficoPizzaCanvas" 
            style="max-height: 300px; max-width: 300px; margin: 0 auto;"
          ></canvas>
        </q-card-section>
        
        <!-- Legenda customizada para o gráfico pizza -->
        <q-card-section v-if="graficoAnimais">
          <div class="row q-gutter-xs">
            <div 
              v-for="(label, index) in graficoAnimais.labels" 
              :key="label"
              class="col-auto"
            >
              <q-chip 
                :style="{ backgroundColor: getCorPizza(index) }"
                text-color="white"
                size="sm"
              >
                {{ label }}: {{ graficoAnimais.data[index] }}
              </q-chip>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import { useDashboardStore } from 'src/stores/dashboard'
import Chart from 'chart.js/auto'

export default {
  name: 'GraficosDashboard',
  
  setup() {
    const dashboardStore = useDashboardStore()
    
    // Refs para os canvas
    const graficoBarrasCanvas = ref(null)
    const graficoPizzaCanvas = ref(null)
    
    // Instâncias dos gráficos
    let chartBarras = null
    let chartPizza = null
    
    // Dados dos gráficos
    const graficoCustos = computed(() => dashboardStore.grafico_custos_mensal)
    const graficoAnimais = computed(() => dashboardStore.grafico_distribuicao_animais)
    
    // Cores padrão para gráfico pizza
    const coresPizza = [
      '#42A5F5', '#66BB6A', '#FFA726', '#EF5350', 
      '#AB47BC', '#26C6DA', '#FFEE58', '#FF7043',
      '#78909C', '#9CCC65'
    ]
    
    const getCorPizza = (index) => {
      return coresPizza[index % coresPizza.length]
    }
    
    // Criar gráfico de barras
    const criarGraficoBarras = async () => {
      if (!graficoBarrasCanvas.value || !graficoCustos.value) return
      
      // Destruir gráfico anterior se existir
      if (chartBarras) {
        chartBarras.destroy()
      }
      
      await nextTick()
      
      const ctx = graficoBarrasCanvas.value.getContext('2d')
      
      chartBarras = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: graficoCustos.value.labels,
          datasets: graficoCustos.value.datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
            },
            tooltip: {
              mode: 'index',
              intersect: false,
              callbacks: {
                label: function(context) {
                  const valor = context.parsed.y
                  return `${context.dataset.label}: R$ ${valor.toLocaleString('pt-BR')}`
                }
              }
            }
          },
          scales: {
            x: {
              stacked: false,
            },
            y: {
              stacked: false,
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return 'R$ ' + value.toLocaleString('pt-BR')
                }
              }
            }
          },
          interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
          }
        }
      })
    }
    
    // Criar gráfico pizza
    const criarGraficoPizza = async () => {
      if (!graficoPizzaCanvas.value || !graficoAnimais.value) return
      
      // Destruir gráfico anterior se existir
      if (chartPizza) {
        chartPizza.destroy()
      }
      
      await nextTick()
      
      const ctx = graficoPizzaCanvas.value.getContext('2d')
      
      chartPizza = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: graficoAnimais.value.labels,
          datasets: [{
            data: graficoAnimais.value.data,
            backgroundColor: graficoAnimais.value.labels.map((_, index) => getCorPizza(index)),
            borderColor: '#ffffff',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false // Usar legenda customizada
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const total = context.dataset.data.reduce((a, b) => a + b, 0)
                  const percentage = ((context.parsed * 100) / total).toFixed(1)
                  return `${context.label}: ${context.parsed} (${percentage}%)`
                }
              }
            }
          },
          cutout: '60%', // Para fazer o efeito doughnut
        }
      })
    }
    
    // Watchers para recriar gráficos quando dados mudarem
    watch(graficoCustos, () => {
      if (graficoCustos.value) {
        criarGraficoBarras()
      }
    }, { deep: true })
    
    watch(graficoAnimais, () => {
      if (graficoAnimais.value) {
        criarGraficoPizza()
      }
    }, { deep: true })
    
    // Cleanup ao destruir componente
    const cleanup = () => {
      if (chartBarras) {
        chartBarras.destroy()
        chartBarras = null
      }
      if (chartPizza) {
        chartPizza.destroy()
        chartPizza = null
      }
    }
    
    onMounted(async () => {
      // Aguardar próximo tick para garantir que canvas esteja disponível
      await nextTick()
      
      if (graficoCustos.value) {
        criarGraficoBarras()
      }
      
      if (graficoAnimais.value) {
        criarGraficoPizza()
      }
    })
    
    // Cleanup quando componente for desmontado
    onUnmounted(() => {
      cleanup()
    })
    
    return {
      graficoBarrasCanvas,
      graficoPizzaCanvas,
      graficoCustos,
      graficoAnimais,
      getCorPizza
    }
  }
}
</script>

<style scoped>
canvas {
  display: block;
}

.q-chip {
  font-size: 0.75rem;
}
</style>