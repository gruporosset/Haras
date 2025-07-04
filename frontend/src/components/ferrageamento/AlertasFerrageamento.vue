<template>
  <q-card>
    <q-card-section>
      <div class="text-h6">Alertas de Vencimento</div>
      <div class="text-caption">
        Animais que precisam de ferrageamento/casqueamento
      </div>
    </q-card-section>

    <q-card-section>
      <div class="row q-gutter-md q-mb-md">
        <q-btn
          color="primary"
          label="Atualizar Alertas"
          icon="refresh"
          @click="carregarAlertas"
        />
        <q-input
          v-model.number="diasAntecedencia"
          type="number"
          label="Dias de Antecedência"
          style="max-width: 200px"
          @update:model-value="carregarAlertas"
        />
      </div>

      <q-list
        bordered
        separator
      >
        <q-item
          v-for="alerta in ferrageamentoStore.alertasVencimento"
          :key="`${alerta.animal_id}-${alerta.tipo_registro}`"
          clickable
        >
          <q-item-section avatar>
            <q-avatar
              :color="getCorAlerta(alerta.dias_vencimento)"
              text-color="white"
            >
              {{ alerta.dias_vencimento }}
            </q-avatar>
          </q-item-section>

          <q-item-section>
            <q-item-label>{{ alerta.animal_nome }}</q-item-label>
            <q-item-label caption>
              {{ ferrageamentoStore.getTipoLabel(alerta.tipo_registro) }}
            </q-item-label>
            <q-item-label caption>
              Última: {{ formatDate(alerta.data_ultimo_registro) }}
            </q-item-label>
            <div
              class="text-caption"
              v-if="alerta.custo_estimado"
            >
              Custo estimado: R$ {{ alerta.custo_estimado.toFixed(2) }}
            </div>
          </q-item-section>

          <q-item-section side>
            <q-btn
              flat
              round
              color="primary"
              icon="add"
              @click="agendarFerrageamento(alerta)"
            >
              <q-tooltip>Agendar Ferrageamento</q-tooltip>
            </q-btn>
          </q-item-section>
        </q-item>

        <q-item v-if="ferrageamentoStore.alertasVencimento.length === 0">
          <q-item-section>
            <q-item-label class="text-center text-grey-6">
              Nenhum alerta no período selecionado
            </q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-card-section>
  </q-card>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useFerrageamentoStore } from 'stores/ferrageamento'
  import { formatDate } from 'src/utils/dateUtils'

  // Emits
  const emit = defineEmits(['agendar'])

  // Store
  const ferrageamentoStore = useFerrageamentoStore()

  // Estado reativo
  const diasAntecedencia = ref(15)

  // Métodos
  async function carregarAlertas() {
    try {
      await ferrageamentoStore.fetchAlertasVencimento(diasAntecedencia.value)
    } catch (error) {
      console.error('Erro ao carregar alertas:', error)
    }
  }

  function agendarFerrageamento(alerta) {
    emit('agendar', alerta)
  }

  function getCorAlerta(dias) {
    if (dias < 0) return 'negative'
    if (dias <= 7) return 'warning'
    if (dias <= 15) return 'orange'
    return 'positive'
  }

  // Lifecycle
  onMounted(() => {
    carregarAlertas()
  })
</script>
