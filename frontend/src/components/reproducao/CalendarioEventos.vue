<template>
  <div>
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h6">Próximos Eventos</div>
      <q-select
        v-model="diasFiltro"
        :options="opcoesDias"
        label="Período"
        dense
        outlined
        style="min-width: 150px"
        @update:model-value="loadData"
      />
    </div>

    <q-list
      bordered
      separator
      v-if="reproducaoStore.calendarioEventos?.length"
    >
      <q-item
        v-for="evento in reproducaoStore.calendarioEventos"
        :key="`${evento.egua_id}-${evento.evento_tipo}-${evento.data_evento}`"
        clickable
      >
        <q-item-section avatar>
          <q-icon
            :name="getIconByEvento(evento.evento_tipo)"
            :color="getEventoColor(evento.evento_tipo, evento.dias_restantes)"
            size="md"
          />
        </q-item-section>

        <q-item-section>
          <q-item-label class="text-weight-medium">
            {{ evento.egua_nome }}
          </q-item-label>
          <q-item-label caption>
            {{ getEventoDescription(evento.evento_tipo) }}
          </q-item-label>
          <q-item-label
            caption
            v-if="evento.observacoes"
          >
            {{ evento.observacoes }}
          </q-item-label>
        </q-item-section>

        <q-item-section side>
          <q-item-label>{{ formatDate(evento.data_evento) }}</q-item-label>
          <q-item-label>
            <q-chip
              :color="getChipColor(evento.dias_restantes)"
              text-color="white"
              size="sm"
              dense
            >
              {{ evento.dias_restantes }}
              {{ evento.dias_restantes === 1 ? 'dia' : 'dias' }}
            </q-chip>
          </q-item-label>
        </q-item-section>
      </q-item>
    </q-list>

    <q-card
      v-else-if="loading"
      flat
      bordered
    >
      <q-card-section class="text-center">
        <q-spinner-dots
          color="primary"
          size="40px"
        />
        <div class="q-mt-sm">Carregando eventos...</div>
      </q-card-section>
    </q-card>

    <q-card
      v-else
      flat
      bordered
    >
      <q-card-section class="text-center text-grey">
        <q-icon
          name="event_busy"
          size="48px"
          color="grey-5"
        />
        <div class="q-mt-sm">
          Nenhum evento nos próximos {{ diasFiltro }} dias
        </div>
      </q-card-section>
    </q-card>

    <!-- Legenda -->
    <q-card
      flat
      class="q-mt-md"
    >
      <q-card-section>
        <div class="text-subtitle2 q-mb-sm">Legenda:</div>
        <div class="row q-gutter-sm">
          <q-chip
            size="sm"
            :color="getEventoColor('DIAGNOSTICO')"
            text-color="white"
            icon="medical_services"
          >
            Diagnóstico de Gestação
          </q-chip>
          <q-chip
            size="sm"
            :color="getEventoColor('PARTO_PREVISTO')"
            text-color="white"
            icon="child_care"
          >
            Parto Previsto
          </q-chip>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useReproducaoStore } from 'stores/reproducao'
  import { formatDate } from 'src/utils/dateUtils'
  import { ErrorHandler } from 'src/utils/errorHandler'

  // Store
  const reproducaoStore = useReproducaoStore()

  // Estado
  const loading = ref(false)
  const diasFiltro = ref(60)

  // Opções de período
  const opcoesDias = [
    { label: '30 dias', value: 30 },
    { label: '60 dias', value: 60 },
    { label: '90 dias', value: 90 },
    { label: '120 dias', value: 120 },
  ]

  // Funções de formatação
  function getIconByEvento(evento) {
    const icons = {
      DIAGNOSTICO: 'medical_services',
      PARTO_PREVISTO: 'child_care',
    }
    return icons[evento] || 'event'
  }

  function getEventoColor(evento, diasRestantes = null) {
    // Se temos dias restantes, usar cores de urgência
    if (diasRestantes !== null) {
      if (diasRestantes <= 3) return 'negative'
      if (diasRestantes <= 7) return 'warning'
    }

    // Cores padrão por tipo de evento
    const colors = {
      DIAGNOSTICO: 'primary',
      PARTO_PREVISTO: 'secondary',
    }
    return colors[evento] || 'grey'
  }

  function getChipColor(diasRestantes) {
    if (diasRestantes <= 3) return 'negative'
    if (diasRestantes <= 7) return 'warning'
    if (diasRestantes <= 15) return 'info'
    return 'positive'
  }

  function getEventoDescription(evento) {
    const descriptions = {
      DIAGNOSTICO: 'Diagnóstico de gestação',
      PARTO_PREVISTO: 'Parto previsto',
    }
    return descriptions[evento] || evento
  }

  // Carregar dados
  async function loadData() {
    try {
      loading.value = true
      await reproducaoStore.fetchCalendarioEventos(diasFiltro.value)
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
