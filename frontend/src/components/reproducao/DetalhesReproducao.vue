<template>
  <q-card style="width: 600px; max-width: 90vw">
    <q-card-section>
      <div class="text-h6">Detalhes da Reprodução</div>
    </q-card-section>

    <q-card-section class="q-pt-none">
      <q-list>
        <q-item>
          <q-item-section>
            <q-item-label caption>Égua</q-item-label>
            <q-item-label class="text-h6">
              {{ reproducao?.egua_nome || '-' }}
            </q-item-label>
          </q-item-section>
        </q-item>

        <q-item>
          <q-item-section>
            <q-item-label caption>Parceiro</q-item-label>
            <q-item-label>
              {{ reproducao?.parceiro_nome || 'Não informado' }}
            </q-item-label>
          </q-item-section>
        </q-item>

        <q-item>
          <q-item-section>
            <q-item-label caption>Data da Cobertura</q-item-label>
            <q-item-label>
              {{ formatDate(reproducao?.DATA_COBERTURA) }}
            </q-item-label>
          </q-item-section>
        </q-item>

        <q-item>
          <q-item-section>
            <q-item-label caption>Tipo de Cobertura</q-item-label>
            <q-item-label>
              <q-chip
                :label="getTipoLabel(reproducao?.TIPO_COBERTURA)"
                color="primary"
                text-color="white"
                size="sm"
              />
            </q-item-label>
          </q-item-section>
        </q-item>

        <q-item v-if="reproducao?.DATA_DIAGNOSTICO">
          <q-item-section>
            <q-item-label caption>Data do Diagnóstico</q-item-label>
            <q-item-label>
              {{ formatDate(reproducao.DATA_DIAGNOSTICO) }}
            </q-item-label>
          </q-item-section>
        </q-item>

        <q-item>
          <q-item-section>
            <q-item-label caption>Resultado do Diagnóstico</q-item-label>
            <q-item-label>
              <q-chip
                :label="getResultadoLabel(reproducao?.RESULTADO_DIAGNOSTICO)"
                :color="getResultadoColor(reproducao?.RESULTADO_DIAGNOSTICO)"
                text-color="white"
                size="sm"
              />
            </q-item-label>
          </q-item-section>
        </q-item>

        <q-item>
          <q-item-section>
            <q-item-label caption>Status</q-item-label>
            <q-item-label>
              <q-chip
                :label="getStatusLabel(reproducao?.STATUS_REPRODUCAO)"
                :color="getStatusColor(reproducao?.STATUS_REPRODUCAO)"
                text-color="white"
                size="sm"
              />
            </q-item-label>
          </q-item-section>
        </q-item>

        <q-item v-if="reproducao?.DATA_PARTO_PREVISTA">
          <q-item-section>
            <q-item-label caption>Parto Previsto</q-item-label>
            <q-item-label>
              {{ formatDate(reproducao.DATA_PARTO_PREVISTA) }}
            </q-item-label>
          </q-item-section>
        </q-item>

        <q-item v-if="reproducao?.DATA_PARTO_REAL">
          <q-item-section>
            <q-item-label caption>Parto Realizado</q-item-label>
            <q-item-label>
              {{ formatDate(reproducao.DATA_PARTO_REAL) }}
            </q-item-label>
          </q-item-section>
        </q-item>

        <q-item v-if="reproducao?.dias_gestacao">
          <q-item-section>
            <q-item-label caption>Dias de Gestação</q-item-label>
            <q-item-label>{{ reproducao.dias_gestacao }} dias</q-item-label>
          </q-item-section>
        </q-item>

        <q-item v-if="reproducao?.OBSERVACOES">
          <q-item-section>
            <q-item-label caption>Observações</q-item-label>
            <q-item-label>{{ reproducao.OBSERVACOES }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-card-section>

    <q-card-actions align="right">
      <q-btn
        flat
        label="Editar"
        color="primary"
        icon="edit"
        @click="$emit('editar')"
      />
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
  import { formatDate } from 'src/utils/dateUtils'

  // Props
  defineProps({
    reproducao: {
      type: Object,
      required: true,
    },
  })

  // Emits
  defineEmits(['editar', 'fechar'])

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

  function getStatusLabel(status) {
    const statusMap = {
      ATIVO: 'Ativo',
      CONCLUIDO: 'Concluído',
      FALHADO: 'Falhado',
    }
    return statusMap[status] || status
  }

  function getResultadoColor(resultado) {
    const colors = {
      POSITIVO: 'positive',
      NEGATIVO: 'negative',
      PENDENTE: 'warning',
    }
    return colors[resultado] || 'grey'
  }

  function getStatusColor(status) {
    const colors = {
      ATIVO: 'primary',
      CONCLUIDO: 'positive',
      FALHADO: 'negative',
    }
    return colors[status] || 'grey'
  }
</script>
