<template>
  <div>
    <!-- Filtros -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="row q-gutter-md items-end">
          <q-select
            v-model="animalSelecionado"
            :options="animalOptions"
            label="Selecionar Animal"
            use-input
            @filter="filterAnimais"
            @update:model-value="loadGraficos"
            class="col-4"
            emit-value
            map-options
          />
          <q-btn
            color="primary"
            icon="refresh"
            label="Atualizar"
            @click="refreshGraficos"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- Gráficos -->
    <div
      v-if="animalSelecionado"
      class="row q-gutter-md"
    >
      <q-card class="col-6">
        <q-card-section>
          <div class="text-h6">Evolução do Peso</div>
          <crescimento-chart
            :dados="dadosGraficoPeso"
            tipo="peso"
            height="400px"
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
            height="400px"
            :show-stats="true"
            :show-trend="true"
          />
        </q-card-section>
      </q-card>
    </div>

    <!-- Comparação entre Animais -->
    <q-card
      v-if="animalSelecionado"
      class="q-mt-md"
    >
      <q-card-section>
        <div class="text-h6 q-mb-md">Comparação com Outros Animais</div>
        <div class="row q-gutter-md">
          <q-select
            v-model="animaisComparacao"
            :options="animalOptions"
            label="Animais para Comparar"
            multiple
            use-chips
            use-input
            @filter="filterAnimais"
            @update:model-value="loadComparacao"
            class="col-6"
            emit-value
            map-options
          />
        </div>

        <div
          v-if="animaisComparacao.length > 0"
          class="q-mt-md"
        >
          <q-card
            flat
            bordered
          >
            <q-card-section>
              <div class="text-subtitle1">Comparação de Peso</div>
              <crescimento-chart
                :dados="dadosComparacaoPeso"
                tipo="peso"
                height="350px"
                :show-stats="false"
                :show-trend="false"
              />
            </q-card-section>
          </q-card>
        </div>
      </q-card-section>
    </q-card>

    <!-- Estado Vazio -->
    <div
      v-if="!animalSelecionado"
      class="text-center q-pa-xl"
    >
      <q-icon
        name="show_chart"
        size="4rem"
        color="grey"
      />
      <div class="text-h6 text-grey q-mt-md">
        Selecione um animal para visualizar os gráficos
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useCrescimentoStore } from 'stores/crescimento'
  import { useAnimalStore } from 'stores/animal'
  import { ErrorHandler } from 'src/utils/errorHandler'
  import CrescimentoChart from 'components/crescimento/CrescimentoChart.vue'

  // Stores
  const crescimentoStore = useCrescimentoStore()
  const animalStore = useAnimalStore()

  // Estado reativo
  const animalSelecionado = ref(null)
  const animaisComparacao = ref([])
  const animalOri = ref([])
  const animalOptions = ref([])

  // Computed
  const dadosGraficoPeso = computed(() => {
    if (!animalSelecionado.value) return []
    return crescimentoStore.dadosGraficoPeso(animalSelecionado.value)
  })

  const dadosGraficoAltura = computed(() => {
    if (!animalSelecionado.value) return []
    return crescimentoStore.dadosGraficoAltura(animalSelecionado.value)
  })

  const dadosComparacaoPeso = computed(() => {
    if (!animaisComparacao.value.length) return []

    const todosAnimais = [animalSelecionado.value, ...animaisComparacao.value]
    const dados = []

    todosAnimais.forEach(animalId => {
      const dadosAnimal = crescimentoStore.dadosGraficoPeso(animalId)
      const nomeAnimal = animalOptions.value.find(
        a => a.value === animalId
      )?.label

      dadosAnimal.forEach(item => {
        dados.push({
          ...item,
          animal: nomeAnimal,
          animalId,
        })
      })
    })

    return dados
  })

  // Métodos
  async function loadAnimais() {
    try {
      await animalStore.fetchAnimais({ limit: 100 })
      animalOri.value = animalStore.animais.map(a => ({
        value: a.ID,
        label: a.NOME,
      }))
      animalOptions.value = [...animalOri.value]
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar animais')
    }
  }

  function filterAnimais(val, update) {
    update(() => {
      if (val === '') {
        animalOptions.value = animalOri.value
      } else {
        const needle = val.toLowerCase()
        animalOptions.value = animalOri.value.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  async function loadGraficos() {
    if (!animalSelecionado.value) return

    try {
      await crescimentoStore.fetchHistoricoAnimal(animalSelecionado.value)
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar gráficos')
    }
  }

  async function loadComparacao() {
    if (!animaisComparacao.value.length) return

    try {
      for (const animalId of animaisComparacao.value) {
        await crescimentoStore.fetchHistoricoAnimal(animalId)
      }
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar dados de comparação')
    }
  }

  async function refreshGraficos() {
    await loadAnimais()
    if (animalSelecionado.value) {
      await loadGraficos()
    }
    if (animaisComparacao.value.length) {
      await loadComparacao()
    }
  }

  // Lifecycle
  onMounted(() => {
    loadAnimais()
  })

  // Expor métodos
  defineExpose({
    refreshGraficos,
  })
</script>
