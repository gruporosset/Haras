<template>
  <q-card style="width: 800px; max-width: 90vw">
    <q-card-section>
      <div class="text-h6">Histórico Reprodutivo</div>
      <div
        v-if="reproducaoStore.historicoEgua"
        class="text-subtitle2"
      >
        Taxa de sucesso: {{ reproducaoStore.historicoEgua.taxa_sucesso }}% ({{
          reproducaoStore.historicoEgua.partos_realizados
        }}/{{ reproducaoStore.historicoEgua.total_coberturas }})
      </div>
    </q-card-section>

    <q-card-section>
      <q-timeline v-if="reproducaoStore.historicoEgua?.reproducoes?.length">
        <q-timeline-entry
          v-for="rep in reproducaoStore.historicoEgua.reproducoes"
          :key="rep.ID"
          :title="getTipoLabel(rep.TIPO_COBERTURA)"
          :subtitle="formatDate(rep.DATA_COBERTURA)"
          :icon="getIconByResultado(rep.RESULTADO_DIAGNOSTICO)"
          :color="getResultadoColor(rep.RESULTADO_DIAGNOSTICO)"
        >
          <div>
            <strong>Parceiro:</strong>
            {{ rep.parceiro_nome || 'Não informado' }}
            <br />
            <strong>Resultado:</strong>
            {{ getResultadoLabel(rep.RESULTADO_DIAGNOSTICO) }}
            <div
              v-if="rep.DATA_PARTO_REAL"
              class="q-mt-xs"
            >
              <strong>Parto:</strong>
              {{ formatDate(rep.DATA_PARTO_REAL) }}
            </div>
            <div
              v-if="rep.dias_gestacao"
              class="q-mt-xs"
            >
              <strong>Gestação:</strong>
              {{ rep.dias_gestacao }} dias
            </div>
            <div
              v-if="rep.OBSERVACOES"
              class="q-mt-xs"
            >
              <strong>Observações:</strong>
              {{ rep.OBSERVACOES }}
            </div>
          </div>
        </q-timeline-entry>
      </q-timeline>

      <div
        v-else-if="loading"
        class="text-center q-pa-lg"
      >
        <q-spinner-dots
          color="primary"
          size="40px"
        />
        <div class="q-mt-sm">Carregando histórico...</div>
      </div>

      <div
        v-else
        class="text-center text-grey q-pa-lg"
      >
        Nenhum histórico reprodutivo encontrado.
      </div>
    </q-card-section>

    <q-card-actions align="right">
      <q-btn
        flat
        label="Fechar"
        color="gray"
        @click="$emit('fechar')"
      />
    </q-card-actions>
  </q-card>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useReproducaoStore } from 'stores/reproducao'
  import { formatDate } from 'src/utils/dateUtils'
  import { ErrorHandler } from 'src/utils/errorHandler'

  // Props
  const props = defineProps({
    eguaId: {
      type: Number,
      required: true,
    },
  })

  // Emits
  defineEmits(['fechar'])

  // Store
  const reproducaoStore = useReproducaoStore()

  // Estado
  const loading = ref(false)

  // Funções de formatação
  function getTipoLabel(tipo) {
    const tipos = {
      NATURAL: 'Natural',
      IA: 'Inseminação Artificial',
      TE: 'Transferência de Embrião',
    }
    return tipos[tipo] || tipo
  }

  function getResultadoLabel(resultado) {
    const resultados = {
      POSITIVO: 'Positivo',
      NEGATIVO: 'Negativo',
      PENDENTE: 'Pendente',
    }
    return resultados[resultado] || resultado
  }

  function getResultadoColor(resultado) {
    const colors = {
      POSITIVO: 'positive',
      NEGATIVO: 'negative',
      PENDENTE: 'warning',
    }
    return colors[resultado] || 'grey'
  }

  function getIconByResultado(resultado) {
    const icons = {
      POSITIVO: 'check_circle',
      NEGATIVO: 'cancel',
      PENDENTE: 'hourglass_empty',
    }
    return icons[resultado] || 'help'
  }

  // Carregar dados
  async function loadHistorico() {
    try {
      loading.value = true
      await reproducaoStore.fetchHistoricoEgua(props.eguaId)
    } catch (error) {
      ErrorHandler.handle(error)
    } finally {
      loading.value = false
    }
  }

  // Inicialização
  onMounted(async () => {
    await loadHistorico()
  })
</script>
