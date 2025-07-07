<template>
  <q-dialog
    v-model="dialog"
    full-width
  >
    <q-card style="min-width: 700px">
      <q-card-section>
        <div class="text-h6 text-primary">
          <q-icon
            name="visibility"
            class="q-mr-sm"
          />
          Detalhes da Movimentação
        </div>
        <div class="text-subtitle2 text-grey-6">
          Movimentação #{{ movimentacao.ID }}
        </div>
      </q-card-section>

      <q-card-section v-if="movimentacao">
        <div class="row q-gutter-md">
          <!-- Informações do Animal -->
          <div class="col-12 col-md-6">
            <q-card
              flat
              bordered
            >
              <q-card-section>
                <div class="text-subtitle1 text-primary q-mb-md">
                  <q-icon
                    name="pets"
                    class="q-mr-sm"
                  />
                  Animal
                </div>

                <q-list>
                  <q-item>
                    <q-item-section>
                      <q-item-label class="text-weight-medium">
                        Nome
                      </q-item-label>
                      <q-item-label caption>
                        {{ movimentacao.animal_nome }}
                      </q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section>
                      <q-item-label class="text-weight-medium">
                        Registro
                      </q-item-label>
                      <q-item-label caption>
                        {{ movimentacao.animal_registro || '-' }}
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>

          <!-- Informações da Movimentação -->
          <div class="col-12 col-md-6">
            <q-card
              flat
              bordered
            >
              <q-card-section>
                <div class="text-subtitle1 text-primary q-mb-md">
                  <q-icon
                    name="move_to_inbox"
                    class="q-mr-sm"
                  />
                  Movimentação
                </div>

                <q-list>
                  <q-item>
                    <q-item-section>
                      <q-item-label class="text-weight-medium">
                        Tipo
                      </q-item-label>
                      <q-item-label caption>
                        <q-chip
                          :color="getTipoColor(movimentacao.TIPO_MOVIMENTACAO)"
                          text-color="white"
                          dense
                          :icon="getIconByTipo(movimentacao.TIPO_MOVIMENTACAO)"
                        >
                          {{ movimentacao.TIPO_MOVIMENTACAO }}
                        </q-chip>
                      </q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section>
                      <q-item-label class="text-weight-medium">
                        Data
                      </q-item-label>
                      <q-item-label caption>
                        {{
                          formatDateForDisplay(movimentacao.DATA_MOVIMENTACAO)
                        }}
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>

          <!-- Origem -->
          <div class="col-12 col-md-6">
            <q-card
              flat
              bordered
            >
              <q-card-section>
                <div class="text-subtitle1 text-primary q-mb-md">
                  <q-icon
                    name="input"
                    class="q-mr-sm"
                  />
                  Origem
                </div>

                <div
                  v-if="
                    movimentacao.terreno_origem_nome ||
                    movimentacao.ORIGEM_EXTERNA
                  "
                >
                  <q-item class="q-pa-none">
                    <q-item-section>
                      <q-item-label class="text-weight-medium">
                        <q-icon
                          :name="
                            movimentacao.terreno_origem_nome
                              ? 'grass'
                              : 'location_on'
                          "
                          :color="
                            movimentacao.terreno_origem_nome
                              ? 'positive'
                              : 'warning'
                          "
                          class="q-mr-sm"
                        />
                        {{
                          movimentacao.terreno_origem_nome
                            ? 'Terreno Interno'
                            : 'Local Externo'
                        }}
                      </q-item-label>
                      <q-item-label caption>
                        {{
                          movimentacao.terreno_origem_nome ||
                          movimentacao.ORIGEM_EXTERNA
                        }}
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </div>

                <div
                  v-else
                  class="text-grey-6 text-center q-pa-md"
                >
                  <q-icon
                    name="remove"
                    size="sm"
                  />
                  Origem não informada
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Destino -->
          <div class="col-12 col-md-6">
            <q-card
              flat
              bordered
            >
              <q-card-section>
                <div class="text-subtitle1 text-primary q-mb-md">
                  <q-icon
                    name="output"
                    class="q-mr-sm"
                  />
                  Destino
                </div>

                <div
                  v-if="
                    movimentacao.terreno_destino_nome ||
                    movimentacao.DESTINO_EXTERNO
                  "
                >
                  <q-item class="q-pa-none">
                    <q-item-section>
                      <q-item-label class="text-weight-medium">
                        <q-icon
                          :name="
                            movimentacao.terreno_destino_nome
                              ? 'grass'
                              : 'location_on'
                          "
                          :color="
                            movimentacao.terreno_destino_nome
                              ? 'positive'
                              : 'warning'
                          "
                          class="q-mr-sm"
                        />
                        {{
                          movimentacao.terreno_destino_nome
                            ? 'Terreno Interno'
                            : 'Local Externo'
                        }}
                      </q-item-label>
                      <q-item-label caption>
                        {{
                          movimentacao.terreno_destino_nome ||
                          movimentacao.DESTINO_EXTERNO
                        }}
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </div>

                <div
                  v-else
                  class="text-grey-6 text-center q-pa-md"
                >
                  <q-icon
                    name="remove"
                    size="sm"
                  />
                  Destino não informado
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Motivo e Observações -->
          <div class="col-12">
            <q-card
              flat
              bordered
            >
              <q-card-section>
                <div class="text-subtitle1 text-primary q-mb-md">
                  <q-icon
                    name="description"
                    class="q-mr-sm"
                  />
                  Detalhes Adicionais
                </div>

                <div class="row q-gutter-md">
                  <div class="col-12 col-md-6">
                    <q-item class="q-pa-none">
                      <q-item-section>
                        <q-item-label class="text-weight-medium">
                          Motivo
                        </q-item-label>
                        <q-item-label caption>
                          {{ movimentacao.MOTIVO || 'Não informado' }}
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </div>

                  <div class="col-12 col-md-6">
                    <q-item class="q-pa-none">
                      <q-item-section>
                        <q-item-label class="text-weight-medium">
                          Observações
                        </q-item-label>
                        <q-item-label caption>
                          {{ movimentacao.OBSERVACOES || 'Nenhuma observação' }}
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Informações de Registro -->
          <div class="col-12">
            <q-card
              flat
              bordered
              class="bg-grey-1"
            >
              <q-card-section>
                <div class="text-subtitle1 text-grey-7 q-mb-md">
                  <q-icon
                    name="info"
                    class="q-mr-sm"
                  />
                  Informações de Registro
                </div>

                <div class="row q-gutter-md">
                  <div class="col-12 col-md-4">
                    <q-item class="q-pa-none">
                      <q-item-section>
                        <q-item-label class="text-weight-medium">
                          Registrado por
                        </q-item-label>
                        <q-item-label caption>
                          {{ movimentacao.usuario_nome || 'Sistema' }}
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </div>

                  <div class="col-12 col-md-4">
                    <q-item class="q-pa-none">
                      <q-item-section>
                        <q-item-label class="text-weight-medium">
                          Data de Registro
                        </q-item-label>
                        <q-item-label caption>
                          {{ formatDateForDisplay(movimentacao.DATA_REGISTRO) }}
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </div>

                  <div class="col-12 col-md-4">
                    <q-item class="q-pa-none">
                      <q-item-section>
                        <q-item-label class="text-weight-medium">
                          ID da Movimentação
                        </q-item-label>
                        <q-item-label caption>
                          #{{ movimentacao.ID }}
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </div>
                </div>
              </q-card-section>
            </q-card>
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
          label="Editar"
          color="primary"
          icon="edit"
          @click="editFromView"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
  import { ref } from 'vue'
  import { formatDateForDisplay } from 'src/utils/dateUtils'

  // Emits
  const emit = defineEmits(['editar'])

  // Estado reativo
  const dialog = ref(false)
  const movimentacao = ref({})

  // Métodos
  function openViewDialog(movimentacaoData) {
    movimentacao.value = movimentacaoData
    dialog.value = true
  }

  function closeDialog() {
    dialog.value = false
  }

  function editFromView() {
    closeDialog()
    emit('editar', movimentacao.value)
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

  // Exposição de métodos para o componente pai
  defineExpose({
    openViewDialog,
  })
</script>
