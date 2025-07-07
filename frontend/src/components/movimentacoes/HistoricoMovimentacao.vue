<template>
  <q-dialog
    v-model="dialog"
    full-width
  >
    <q-card style="min-width: 900px; max-height: 80vh">
      <q-card-section>
        <div class="text-h6 text-primary">
          <q-icon
            name="history"
            class="q-mr-sm"
          />
          Histórico de Movimentações
        </div>
        <div class="text-subtitle2 text-grey-6">
          {{ animalNome ? `Animal: ${animalNome}` : 'Carregando...' }}
        </div>
      </q-card-section>

      <q-card-section
        class="q-pt-none"
        style="max-height: 60vh; overflow-y: auto"
      >
        <!-- Loading -->
        <div
          v-if="movimentacaoStore.loading"
          class="text-center q-pa-lg"
        >
          <q-spinner-dots
            size="50px"
            color="primary"
          />
          <div class="q-mt-md text-grey-6">Carregando histórico...</div>
        </div>

        <!-- Sem movimentações -->
        <div
          v-else-if="!historico.length"
          class="text-center q-pa-xl"
        >
          <q-icon
            name="inbox"
            size="4rem"
            color="grey-4"
          />
          <div class="text-h6 q-mt-md text-grey-6">
            Nenhuma movimentação encontrada
          </div>
          <div class="text-body2 text-grey-5">
            Este animal ainda não possui movimentações registradas
          </div>
        </div>

        <!-- Timeline de movimentações -->
        <q-timeline
          v-else
          color="primary"
          layout="comfortable"
        >
          <q-timeline-entry
            v-for="item in historico"
            :key="item.ID"
            :title="item.DATA_MOVIMENTACAO"
            :subtitle="getSubtitleMovimentacao(item)"
            :icon="getIconByTipo(item.TIPO_MOVIMENTACAO)"
            :color="getTipoColor(item.TIPO_MOVIMENTACAO)"
            side="right"
          >
            <!-- Header do item -->
            <template v-slot:title>
              <div class="row items-center">
                <div class="col">
                  <div class="text-weight-medium">
                    {{ item.DATA_MOVIMENTACAO }}
                  </div>
                </div>
                <div class="col-auto">
                  <q-chip
                    :color="getTipoColor(item.TIPO_MOVIMENTACAO)"
                    text-color="white"
                    dense
                    size="sm"
                  >
                    {{ item.TIPO_MOVIMENTACAO }}
                  </q-chip>
                </div>
              </div>
            </template>

            <!-- Conteúdo do item -->
            <q-card
              flat
              bordered
              class="q-mt-sm"
            >
              <q-card-section class="q-pa-md">
                <!-- Origem e Destino -->
                <div class="row q-gutter-md q-mb-md">
                  <div class="col-12 col-md-6">
                    <div class="text-caption text-grey-6 q-mb-xs">
                      <q-icon
                        name="input"
                        size="xs"
                        class="q-mr-xs"
                      />
                      ORIGEM
                    </div>
                    <div class="text-body2">
                      <q-icon
                        :name="
                          item.terreno_origem_nome ? 'grass' : 'location_on'
                        "
                        :color="
                          item.terreno_origem_nome ? 'positive' : 'warning'
                        "
                        size="xs"
                        class="q-mr-xs"
                      />
                      {{
                        item.terreno_origem_nome ||
                        item.ORIGEM_EXTERNA ||
                        'Não informado'
                      }}
                    </div>
                  </div>

                  <div class="col-12 col-md-6">
                    <div class="text-caption text-grey-6 q-mb-xs">
                      <q-icon
                        name="output"
                        size="xs"
                        class="q-mr-xs"
                      />
                      DESTINO
                    </div>
                    <div class="text-body2">
                      <q-icon
                        :name="
                          item.terreno_destino_nome ? 'grass' : 'location_on'
                        "
                        :color="
                          item.terreno_destino_nome ? 'positive' : 'warning'
                        "
                        size="xs"
                        class="q-mr-xs"
                      />
                      {{
                        item.terreno_destino_nome ||
                        item.DESTINO_EXTERNO ||
                        'Não informado'
                      }}
                    </div>
                  </div>
                </div>

                <!-- Motivo -->
                <div
                  v-if="item.MOTIVO"
                  class="q-mb-sm"
                >
                  <div class="text-caption text-grey-6 q-mb-xs">
                    <q-icon
                      name="info"
                      size="xs"
                      class="q-mr-xs"
                    />
                    MOTIVO
                  </div>
                  <div class="text-body2">{{ item.MOTIVO }}</div>
                </div>

                <!-- Observações -->
                <div
                  v-if="item.OBSERVACOES"
                  class="q-mb-sm"
                >
                  <div class="text-caption text-grey-6 q-mb-xs">
                    <q-icon
                      name="notes"
                      size="xs"
                      class="q-mr-xs"
                    />
                    OBSERVAÇÕES
                  </div>
                  <div class="text-body2">{{ item.OBSERVACOES }}</div>
                </div>

                <!-- Registrado por -->
                <div
                  class="text-caption text-grey-5 q-mt-md q-pt-sm"
                  style="border-top: 1px solid #e0e0e0"
                >
                  <q-icon
                    name="person"
                    size="xs"
                    class="q-mr-xs"
                  />
                  Registrado por {{ item.usuario_nome || 'Sistema' }} em
                  {{ formatDateForDisplay(item.DATA_REGISTRO) }}
                </div>
              </q-card-section>

              <!-- Ações do item -->
              <q-card-actions
                align="right"
                class="q-pa-sm"
              >
                <q-btn
                  flat
                  dense
                  size="sm"
                  icon="visibility"
                  color="primary"
                  @click="visualizarMovimentacao(item)"
                >
                  <q-tooltip>Ver detalhes</q-tooltip>
                </q-btn>

                <q-btn
                  flat
                  dense
                  size="sm"
                  icon="edit"
                  color="orange"
                  @click="editarMovimentacao(item)"
                >
                  <q-tooltip>Editar</q-tooltip>
                </q-btn>
              </q-card-actions>
            </q-card>
          </q-timeline-entry>
        </q-timeline>
      </q-card-section>

      <!-- Resumo estatístico -->
      <q-card-section
        v-if="historico.length > 0"
        class="q-pt-none"
      >
        <q-separator class="q-mb-md" />
        <div class="row q-gutter-md text-center">
          <div class="col">
            <div class="text-h6 text-primary">{{ historico.length }}</div>
            <div class="text-caption text-grey-6">Total de Movimentações</div>
          </div>
          <div class="col">
            <div class="text-h6 text-positive">
              {{ contarPorTipo('ENTRADA') }}
            </div>
            <div class="text-caption text-grey-6">Entradas</div>
          </div>
          <div class="col">
            <div class="text-h6 text-warning">{{ contarPorTipo('SAIDA') }}</div>
            <div class="text-caption text-grey-6">Saídas</div>
          </div>
          <div class="col">
            <div class="text-h6 text-info">
              {{ contarPorTipo('TRANSFERENCIA') }}
            </div>
            <div class="text-caption text-grey-6">Transferências</div>
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
        <q-btn
          label="Nova Movimentação"
          color="primary"
          icon="add"
          @click="novaMovimentacao"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
  import { ref, computed } from 'vue'
  import { useMovimentacaoStore } from 'stores/movimentacao'
  import { formatDateForDisplay } from 'src/utils/dateUtils'
  import { ErrorHandler } from 'src/utils/errorHandler'

  // Emits
  const emit = defineEmits(['visualizar', 'editar', 'nova-movimentacao'])

  // Stores
  const movimentacaoStore = useMovimentacaoStore()

  // Estado reativo
  const dialog = ref(false)
  const animalId = ref(null)
  const animalNome = ref('')

  // Computed
  const historico = computed(
    () => movimentacaoStore.historicoAnimal?.movimentacoes || []
  )

  // Métodos
  async function openHistoricoDialog(id, nome = '') {
    animalId.value = id
    animalNome.value = nome
    dialog.value = true

    try {
      await movimentacaoStore.fetchHistoricoAnimal(id)
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar histórico')
    }
  }

  function closeDialog() {
    dialog.value = false
    animalId.value = null
    animalNome.value = ''
  }

  function getSubtitleMovimentacao(item) {
    const origem = item.terreno_origem_nome || item.ORIGEM_EXTERNA || 'N/A'
    const destino = item.terreno_destino_nome || item.DESTINO_EXTERNO || 'N/A'

    switch (item.TIPO_MOVIMENTACAO) {
      case 'ENTRADA':
        return `Entrada de: ${origem} → ${destino}`
      case 'SAIDA':
        return `Saída de: ${origem} → ${destino}`
      case 'TRANSFERENCIA':
        return `Transferência: ${origem} → ${destino}`
      case 'VENDA':
        return `Venda: ${origem} → ${destino}`
      case 'EMPRESTIMO':
        return `Empréstimo: ${origem} → ${destino}`
      case 'RETORNO':
        return `Retorno: ${origem} → ${destino}`
      default:
        return `${origem} → ${destino}`
    }
  }

  function getTipoColor(tipo) {
    const colors = {
      TRANSFERENCIA: 'primary',
      ENTRADA: 'positive',
      SAIDA: 'warning',
      VENDA: 'info',
      EMPRESTIMO: 'secondary',
      RETORNO: 'accent',
    }
    return colors[tipo] || 'grey'
  }

  function getIconByTipo(tipo) {
    const icons = {
      TRANSFERENCIA: 'swap_horiz',
      ENTRADA: 'input',
      SAIDA: 'output',
      VENDA: 'attach_money',
      EMPRESTIMO: 'handshake',
      RETORNO: 'keyboard_return',
    }
    return icons[tipo] || 'move_to_inbox'
  }

  function contarPorTipo(tipo) {
    return historico.value.filter(item => item.TIPO_MOVIMENTACAO === tipo)
      .length
  }

  function visualizarMovimentacao(movimentacao) {
    emit('visualizar', movimentacao)
  }

  function editarMovimentacao(movimentacao) {
    emit('editar', movimentacao)
  }

  function novaMovimentacao() {
    // Passar dados do animal para pré-preenchimento
    const dadosAnimal = {
      ID_ANIMAL: animalId.value,
      animal_nome: animalNome.value,
    }
    emit('nova-movimentacao', dadosAnimal)
  }

  // Exposição de métodos para o componente pai
  defineExpose({
    openHistoricoDialog,
  })
</script>
