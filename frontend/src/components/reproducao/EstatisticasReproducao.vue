<template>
  <div>
    <!-- Filtro de Ano -->
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h6">Estatísticas de Reprodução</div>
      <q-select
        v-model="anoSelecionado"
        :options="anosDisponiveis"
        label="Ano"
        dense
        outlined
        style="min-width: 150px"
        @update:model-value="loadData"
      />
    </div>

    <!-- Cards de Estatísticas -->
    <div
      class="row q-gutter-md"
      v-if="reproducaoStore.estatisticas"
    >
      <div class="col-12 col-md-3">
        <q-card>
          <q-card-section class="text-center">
            <q-icon
              name="pets"
              size="48px"
              color="primary"
            />
            <div class="text-h4 text-primary q-mt-sm">
              {{ reproducaoStore.estatisticas.total_coberturas }}
            </div>
            <div class="text-subtitle2">Total de Coberturas</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card>
          <q-card-section class="text-center">
            <q-icon
              name="trending_up"
              size="48px"
              color="positive"
            />
            <div class="text-h4 text-positive q-mt-sm">
              {{ reproducaoStore.estatisticas.taxa_sucesso }}%
            </div>
            <div class="text-subtitle2">Taxa de Sucesso</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card>
          <q-card-section class="text-center">
            <q-icon
              name="pregnant_woman"
              size="48px"
              color="secondary"
            />
            <div class="text-h4 text-secondary q-mt-sm">
              {{ reproducaoStore.estatisticas.gestacoes_ativas }}
            </div>
            <div class="text-subtitle2">Gestações Ativas</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card>
          <q-card-section class="text-center">
            <q-icon
              name="child_friendly"
              size="48px"
              color="info"
            />
            <div class="text-h4 text-info q-mt-sm">
              {{ reproducaoStore.estatisticas.partos_realizados }}
            </div>
            <div class="text-subtitle2">Partos Realizados</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Detalhamento dos Resultados -->
    <div
      class="row q-gutter-md q-mt-md"
      v-if="reproducaoStore.estatisticas"
    >
      <div class="col-12 col-md-6">
        <q-card>
          <q-card-section>
            <div class="text-h6">Resultados dos Diagnósticos</div>
            <q-list>
              <q-item>
                <q-item-section avatar>
                  <q-icon
                    name="check_circle"
                    color="positive"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Positivos</q-item-label>
                  <q-item-label caption>
                    {{ reproducaoStore.estatisticas.coberturas_positivas }}
                    coberturas
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-circular-progress
                    :value="porcentagemPositivos"
                    size="50px"
                    :thickness="0.2"
                    color="positive"
                    track-color="grey-3"
                    show-value
                  >
                    {{ porcentagemPositivos }}%
                  </q-circular-progress>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section avatar>
                  <q-icon
                    name="cancel"
                    color="negative"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Negativos</q-item-label>
                  <q-item-label caption>
                    {{ reproducaoStore.estatisticas.coberturas_negativas }}
                    coberturas
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-circular-progress
                    :value="porcentagemNegativos"
                    size="50px"
                    :thickness="0.2"
                    color="negative"
                    track-color="grey-3"
                    show-value
                  >
                    {{ porcentagemNegativos }}%
                  </q-circular-progress>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section avatar>
                  <q-icon
                    name="hourglass_empty"
                    color="warning"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Pendentes</q-item-label>
                  <q-item-label caption>
                    {{ reproducaoStore.estatisticas.coberturas_pendentes }}
                    coberturas
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-circular-progress
                    :value="porcentagemPendentes"
                    size="50px"
                    :thickness="0.2"
                    color="warning"
                    track-color="grey-3"
                    show-value
                  >
                    {{ porcentagemPendentes }}%
                  </q-circular-progress>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-6">
        <q-card>
          <q-card-section>
            <div class="text-h6">Indicadores de Performance</div>
            <q-list>
              <q-item>
                <q-item-section>
                  <q-item-label>Média de Dias de Gestação</q-item-label>
                  <q-item-label caption>
                    Baseado nos partos realizados
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <div class="text-h6">{{ mediaGestacao }} dias</div>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section>
                  <q-item-label>Taxa de Aproveitamento</q-item-label>
                  <q-item-label caption>
                    Partos realizados / Coberturas positivas
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <div class="text-h6">{{ taxaAproveitamento }}%</div>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section>
                  <q-item-label>Eficiência Reprodutiva</q-item-label>
                  <q-item-label caption>
                    Considerando todos os fatores
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-chip
                    :color="getEficienciaColor()"
                    text-color="white"
                  >
                    {{ getEficienciaLabel() }}
                  </q-chip>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Estado de Loading -->
    <div
      v-if="loading"
      class="row q-gutter-md"
    >
      <div class="col-12 text-center q-pa-lg">
        <q-spinner-dots
          color="primary"
          size="40px"
        />
        <div class="q-mt-sm">Carregando estatísticas...</div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useReproducaoStore } from 'stores/reproducao'
  import { ErrorHandler } from 'src/utils/errorHandler'

  // Store
  const reproducaoStore = useReproducaoStore()

  // Estado
  const loading = ref(false)
  const anoSelecionado = ref(new Date().getFullYear())

  // Anos disponíveis (últimos 5 anos)
  const anosDisponiveis = computed(() => {
    const anoAtual = new Date().getFullYear()
    const anos = []
    for (let i = 0; i < 5; i++) {
      anos.push({
        label: String(anoAtual - i),
        value: anoAtual - i,
      })
    }
    return anos
  })

  // Computed para porcentagens
  const porcentagemPositivos = computed(() => {
    if (
      !reproducaoStore.estatisticas ||
      reproducaoStore.estatisticas.total_coberturas === 0
    )
      return 0
    return Math.round(
      (reproducaoStore.estatisticas.coberturas_positivas /
        reproducaoStore.estatisticas.total_coberturas) *
        100
    )
  })

  const porcentagemNegativos = computed(() => {
    if (
      !reproducaoStore.estatisticas ||
      reproducaoStore.estatisticas.total_coberturas === 0
    )
      return 0
    return Math.round(
      (reproducaoStore.estatisticas.coberturas_negativas /
        reproducaoStore.estatisticas.total_coberturas) *
        100
    )
  })

  const porcentagemPendentes = computed(() => {
    if (
      !reproducaoStore.estatisticas ||
      reproducaoStore.estatisticas.total_coberturas === 0
    )
      return 0
    return Math.round(
      (reproducaoStore.estatisticas.coberturas_pendentes /
        reproducaoStore.estatisticas.total_coberturas) *
        100
    )
  })

  const mediaGestacao = computed(() => {
    // Média padrão de gestação em cavalos
    return 340
  })

  const taxaAproveitamento = computed(() => {
    if (
      !reproducaoStore.estatisticas ||
      reproducaoStore.estatisticas.coberturas_positivas === 0
    )
      return 0
    return Math.round(
      (reproducaoStore.estatisticas.partos_realizados /
        reproducaoStore.estatisticas.coberturas_positivas) *
        100
    )
  })

  // Funções
  function getEficienciaColor() {
    const taxa = reproducaoStore.estatisticas?.taxa_sucesso || 0
    if (taxa >= 70) return 'positive'
    if (taxa >= 50) return 'warning'
    return 'negative'
  }

  function getEficienciaLabel() {
    const taxa = reproducaoStore.estatisticas?.taxa_sucesso || 0
    if (taxa >= 70) return 'Excelente'
    if (taxa >= 50) return 'Regular'
    return 'Baixa'
  }

  // Carregar dados
  async function loadData() {
    try {
      loading.value = true
      await reproducaoStore.fetchEstatisticas(anoSelecionado.value)
    } catch (error) {
      ErrorHandler.handle(error)
    } finally {
      loading.value = false
    }
  }

  // Expor função para o componente pai
  defineExpose({
    loadData,
  })

  // Inicialização
  onMounted(async () => {
    await loadData()
  })
</script>
