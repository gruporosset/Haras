<template>
  <q-dialog
    v-model="viewDialog"
    persistent
  >
    <q-card style="min-width: 600px">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Detalhes do Registro</div>
        <q-space />
        <q-btn
          icon="close"
          flat
          round
          dense
          @click="closeDialog"
        />
      </q-card-section>

      <q-card-section v-if="registroData">
        <div class="row q-gutter-md">
          <div class="col-6">
            <q-list>
              <q-item>
                <q-item-section>
                  <q-item-label overline>Animal</q-item-label>
                  <q-item-label>{{ registroData.animal_nome }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-item-label overline>Data da Ocorrência</q-item-label>
                  <q-item-label>
                    {{ formatDate(registroData.DATA_OCORRENCIA) }}
                  </q-item-label>
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-item-label overline>Tipo</q-item-label>
                  <q-chip
                    :color="getTipoColor(registroData.TIPO_REGISTRO)"
                    text-color="white"
                    size="sm"
                  >
                    {{
                      ferrageamentoStore.getTipoLabel(
                        registroData.TIPO_REGISTRO
                      )
                    }}
                  </q-chip>
                </q-item-section>
              </q-item>
              <q-item v-if="registroData.FERRADOR_RESPONSAVEL">
                <q-item-section>
                  <q-item-label overline>Ferrador</q-item-label>
                  <q-item-label>
                    {{ registroData.FERRADOR_RESPONSAVEL }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <div class="col-6">
            <q-list>
              <q-item v-if="registroData.MEMBRO_TRATADO">
                <q-item-section>
                  <q-item-label overline>Membro(s) Tratado(s)</q-item-label>
                  <q-item-label>
                    {{
                      ferrageamentoStore.getMembroLabel(
                        registroData.MEMBRO_TRATADO
                      )
                    }}
                  </q-item-label>
                </q-item-section>
              </q-item>
              <q-item v-if="registroData.STATUS_CASCO">
                <q-item-section>
                  <q-item-label overline>Status do Casco</q-item-label>
                  <q-chip
                    :color="getStatusCascoColor(registroData.STATUS_CASCO)"
                    text-color="white"
                    size="sm"
                  >
                    {{ registroData.STATUS_CASCO }}
                  </q-chip>
                </q-item-section>
              </q-item>
              <q-item v-if="registroData.TIPO_FERRADURA">
                <q-item-section>
                  <q-item-label overline>Tipo de Ferradura</q-item-label>
                  <q-item-label>{{ registroData.TIPO_FERRADURA }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item v-if="registroData.CUSTO">
                <q-item-section>
                  <q-item-label overline>Custo</q-item-label>
                  <q-item-label>
                    R$ {{ registroData.CUSTO.toFixed(2) }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </div>

        <!-- Datas de Controle -->
        <div
          v-if="
            registroData.PROXIMA_AVALIACAO ||
            registroData.DATA_PREV_PROX_FERRAGEAMENTO
          "
          class="q-mt-md"
        >
          <q-separator />
          <div class="text-subtitle2 q-mt-md q-mb-sm">Datas de Controle</div>
          <div class="row q-gutter-md">
            <div class="col-6">
              <q-list dense>
                <q-item v-if="registroData.PROXIMA_AVALIACAO">
                  <q-item-section>
                    <q-item-label caption>Próxima Avaliação</q-item-label>
                    <q-item-label>
                      {{ formatDate(registroData.PROXIMA_AVALIACAO) }}
                    </q-item-label>
                    <q-item-label
                      caption
                      :class="
                        getClasseDiasVencimento(
                          registroData.dias_proxima_avaliacao
                        )
                      "
                    >
                      {{
                        getTextoDiasVencimento(
                          registroData.dias_proxima_avaliacao
                        )
                      }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
            <div class="col-6">
              <q-list dense>
                <q-item v-if="registroData.DATA_PREV_PROX_FERRAGEAMENTO">
                  <q-item-section>
                    <q-item-label caption>Próximo Ferrageamento</q-item-label>
                    <q-item-label>
                      {{
                        formatDate(registroData.DATA_PREV_PROX_FERRAGEAMENTO)
                      }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
        </div>

        <!-- Detalhes Técnicos -->
        <div
          v-if="temDetalhes"
          class="q-mt-md"
        >
          <q-separator />
          <div class="text-subtitle2 q-mt-md q-mb-sm">Detalhes Técnicos</div>
          <div class="row q-gutter-md">
            <div class="col-6">
              <q-list dense>
                <q-item v-if="registroData.PROBLEMAS_IDENTIFICADOS">
                  <q-item-section>
                    <q-item-label caption>Problemas Identificados</q-item-label>
                    <q-item-label>
                      {{ registroData.PROBLEMAS_IDENTIFICADOS }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="registroData.TRATAMENTO_REALIZADO">
                  <q-item-section>
                    <q-item-label caption>Tratamento Realizado</q-item-label>
                    <q-item-label>
                      {{ registroData.TRATAMENTO_REALIZADO }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
            <div class="col-6">
              <q-list dense>
                <q-item v-if="registroData.MEDICAMENTOS_UTILIZADOS">
                  <q-item-section>
                    <q-item-label caption>Medicamentos Utilizados</q-item-label>
                    <q-item-label>
                      {{ registroData.MEDICAMENTOS_UTILIZADOS }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="registroData.RECOMENDACOES">
                  <q-item-section>
                    <q-item-label caption>Recomendações</q-item-label>
                    <q-item-label>
                      {{ registroData.RECOMENDACOES }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
        </div>

        <!-- Observações -->
        <div
          v-if="registroData.OBSERVACOES"
          class="q-mt-md"
        >
          <q-separator />
          <div class="text-subtitle2 q-mt-md q-mb-sm">Observações</div>
          <div class="text-body2">{{ registroData.OBSERVACOES }}</div>
        </div>

        <!-- Informações de Registro -->
        <div class="q-mt-md">
          <q-separator />
          <div class="text-caption text-grey q-mt-md">
            Registrado em {{ formatDate(registroData.DATA_CADASTRO) }}
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn
          flat
          label="Fechar"
          color="grey"
          @click="closeDialog"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
  import { ref, computed } from 'vue'
  import { useFerrageamentoStore } from 'stores/ferrageamento'
  import { formatDate } from 'src/utils/dateUtils'

  // Store
  const ferrageamentoStore = useFerrageamentoStore()

  // Estado reativo
  const viewDialog = ref(false)
  const registroData = ref(null)

  // Computed
  const temDetalhes = computed(() => {
    if (!registroData.value) return false

    return (
      registroData.value.PROBLEMAS_IDENTIFICADOS ||
      registroData.value.TRATAMENTO_REALIZADO ||
      registroData.value.MEDICAMENTOS_UTILIZADOS ||
      registroData.value.RECOMENDACOES
    )
  })

  // Métodos
  function openViewDialog(registro) {
    registroData.value = registro
    viewDialog.value = true
  }

  function closeDialog() {
    viewDialog.value = false
    registroData.value = null
  }

  function getTipoColor(tipo) {
    const colors = {
      FERRAGEAMENTO: 'primary',
      CASQUEAMENTO: 'secondary',
      TRATAMENTO_CASCO: 'warning',
      AVALIACAO: 'info',
    }
    return colors[tipo] || 'grey'
  }

  function getStatusCascoColor(status) {
    const colors = {
      BOM: 'positive',
      REGULAR: 'warning',
      RUIM: 'negative',
      CRITICO: 'red',
    }
    return colors[status] || 'grey'
  }

  function getClasseDiasVencimento(dias) {
    if (dias < 0) return 'text-negative'
    if (dias <= 7) return 'text-warning'
    return 'text-positive'
  }

  function getTextoDiasVencimento(dias) {
    if (dias < 0) return `${Math.abs(dias)} dias em atraso`
    if (dias === 0) return 'Vence hoje'
    return `${dias} dias restantes`
  }

  // Expor métodos
  defineExpose({
    openViewDialog,
  })
</script>
