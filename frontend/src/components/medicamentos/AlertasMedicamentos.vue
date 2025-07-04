<template>
  <div>
    <!-- Resumo de Alertas -->
    <div class="row q-gutter-md q-mb-md">
      <q-card
        flat
        bordered
        class="col"
      >
        <q-card-section class="text-center">
          <div class="text-h4 text-negative">
            {{ alertas.estoqueBaixo.length }}
          </div>
          <div class="text-caption">Estoque Baixo</div>
        </q-card-section>
      </q-card>

      <q-card
        flat
        bordered
        class="col"
      >
        <q-card-section class="text-center">
          <div class="text-h4 text-warning">{{ alertas.vencendo.length }}</div>
          <div class="text-caption">Vencendo</div>
        </q-card-section>
      </q-card>

      <q-card
        flat
        bordered
        class="col"
      >
        <q-card-section class="text-center">
          <div class="text-h4 text-red">{{ alertas.vencidos.length }}</div>
          <div class="text-caption">Vencidos</div>
        </q-card-section>
      </q-card>

      <q-card
        flat
        bordered
        class="col"
      >
        <q-card-section class="text-center">
          <div class="text-h4 text-grey">{{ alertas.semEstoque.length }}</div>
          <div class="text-caption">Sem Estoque</div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Abas de Alertas -->
    <q-tabs
      v-model="activeAlertTab"
      class="q-mb-md"
    >
      <q-tab
        name="estoque-baixo"
        label="Estoque Baixo"
        :badge="alertas.estoqueBaixo.length || undefined"
      />
      <q-tab
        name="vencendo"
        label="Vencendo"
        :badge="alertas.vencendo.length || undefined"
      />
      <q-tab
        name="vencidos"
        label="Vencidos"
        :badge="alertas.vencidos.length || undefined"
      />
      <q-tab
        name="sem-estoque"
        label="Sem Estoque"
        :badge="alertas.semEstoque.length || undefined"
      />
    </q-tabs>

    <q-tab-panels
      v-model="activeAlertTab"
      animated
    >
      <!-- Estoque Baixo -->
      <q-tab-panel name="estoque-baixo">
        <div
          v-if="alertas.estoqueBaixo.length === 0"
          class="text-center q-pa-lg"
        >
          <q-icon
            name="check_circle"
            size="4rem"
            color="positive"
          />
          <div class="text-h6 q-mt-md">
            Nenhum medicamento com estoque baixo!
          </div>
          <div class="text-caption text-grey">
            Todos os medicamentos estão com estoque adequado.
          </div>
        </div>

        <q-list v-else>
          <q-item
            v-for="medicamento in alertas.estoqueBaixo"
            :key="medicamento.ID"
            class="q-mb-sm"
          >
            <q-item-section avatar>
              <q-avatar
                color="negative"
                text-color="white"
                icon="warning"
              />
            </q-item-section>

            <q-item-section>
              <q-item-label class="text-weight-bold">
                {{ medicamento.NOME }}
              </q-item-label>
              <q-item-label caption>
                {{ medicamento.PRINCIPIO_ATIVO }}
              </q-item-label>
              <q-item-label caption>
                <q-chip
                  dense
                  color="negative"
                  text-color="white"
                >
                  {{ medicamento.FORMA_FARMACEUTICA }}
                </q-chip>
              </q-item-label>
            </q-item-section>

            <q-item-section>
              <q-item-label caption>Estoque Atual</q-item-label>
              <q-item-label class="text-negative text-weight-bold">
                {{ medicamento.ESTOQUE_ATUAL || 0 }}
                {{ medicamento.UNIDADE_MEDIDA }}
              </q-item-label>
              <q-item-label caption>
                Mín: {{ medicamento.ESTOQUE_MINIMO }}
                {{ medicamento.UNIDADE_MEDIDA }}
              </q-item-label>
            </q-item-section>

            <q-item-section>
              <q-item-label caption>Valor Unitário</q-item-label>
              <q-item-label>
                R$ {{ (medicamento.PRECO_UNITARIO || 0).toFixed(2) }}
              </q-item-label>
            </q-item-section>

            <q-item-section side>
              <div class="q-gutter-sm">
                <q-btn
                  color="positive"
                  icon="add_shopping_cart"
                  label="Comprar"
                  size="sm"
                  @click="$emit('comprar', medicamento)"
                />
                <q-btn
                  color="primary"
                  icon="visibility"
                  label="Ver"
                  size="sm"
                  flat
                  @click="verDetalhes(medicamento)"
                />
              </div>
            </q-item-section>
          </q-item>
        </q-list>
      </q-tab-panel>

      <!-- Vencendo -->
      <q-tab-panel name="vencendo">
        <div
          v-if="alertas.vencendo.length === 0"
          class="text-center q-pa-lg"
        >
          <q-icon
            name="check_circle"
            size="4rem"
            color="positive"
          />
          <div class="text-h6 q-mt-md">Nenhum medicamento vencendo!</div>
          <div class="text-caption text-grey">
            Não há medicamentos com data de validade próxima.
          </div>
        </div>

        <q-list v-else>
          <q-item
            v-for="medicamento in alertas.vencendo"
            :key="medicamento.ID"
            class="q-mb-sm"
          >
            <q-item-section avatar>
              <q-avatar
                color="warning"
                text-color="white"
                icon="schedule"
              />
            </q-item-section>

            <q-item-section>
              <q-item-label class="text-weight-bold">
                {{ medicamento.NOME }}
              </q-item-label>
              <q-item-label caption>
                Lote: {{ medicamento.LOTE_ATUAL || 'N/A' }}
              </q-item-label>
            </q-item-section>

            <q-item-section>
              <q-item-label caption>Data de Validade</q-item-label>
              <q-item-label class="text-warning text-weight-bold">
                {{ formatDate(medicamento.DATA_VALIDADE) }}
              </q-item-label>
              <q-item-label caption>
                {{ getDiasParaVencimento(medicamento.DATA_VALIDADE) }} dias
              </q-item-label>
            </q-item-section>

            <q-item-section>
              <q-item-label caption>Estoque</q-item-label>
              <q-item-label>
                {{ medicamento.ESTOQUE_ATUAL || 0 }}
                {{ medicamento.UNIDADE_MEDIDA }}
              </q-item-label>
            </q-item-section>

            <q-item-section side>
              <div class="q-gutter-sm">
                <q-btn
                  color="warning"
                  icon="update"
                  label="Atualizar Lote"
                  size="sm"
                  @click="atualizarLote(medicamento)"
                />
                <q-btn
                  color="primary"
                  icon="visibility"
                  label="Ver"
                  size="sm"
                  flat
                  @click="verDetalhes(medicamento)"
                />
              </div>
            </q-item-section>
          </q-item>
        </q-list>
      </q-tab-panel>

      <!-- Vencidos -->
      <q-tab-panel name="vencidos">
        <div
          v-if="alertas.vencidos.length === 0"
          class="text-center q-pa-lg"
        >
          <q-icon
            name="check_circle"
            size="4rem"
            color="positive"
          />
          <div class="text-h6 q-mt-md">Nenhum medicamento vencido!</div>
          <div class="text-caption text-grey">
            Não há medicamentos com validade expirada.
          </div>
        </div>

        <q-list v-else>
          <q-item
            v-for="medicamento in alertas.vencidos"
            :key="medicamento.ID"
            class="q-mb-sm"
          >
            <q-item-section avatar>
              <q-avatar
                color="red"
                text-color="white"
                icon="error"
              />
            </q-item-section>

            <q-item-section>
              <q-item-label class="text-weight-bold">
                {{ medicamento.NOME }}
              </q-item-label>
              <q-item-label caption>
                Lote: {{ medicamento.LOTE_ATUAL || 'N/A' }}
              </q-item-label>
              <q-item-label caption>
                <q-chip
                  dense
                  color="red"
                  text-color="white"
                >
                  VENCIDO
                </q-chip>
              </q-item-label>
            </q-item-section>

            <q-item-section>
              <q-item-label caption>Data de Validade</q-item-label>
              <q-item-label class="text-red text-weight-bold">
                {{ formatDate(medicamento.DATA_VALIDADE) }}
              </q-item-label>
              <q-item-label
                caption
                class="text-red"
              >
                Vencido há
                {{
                  Math.abs(getDiasParaVencimento(medicamento.DATA_VALIDADE))
                }}
                dias
              </q-item-label>
            </q-item-section>

            <q-item-section>
              <q-item-label caption>Estoque</q-item-label>
              <q-item-label>
                {{ medicamento.ESTOQUE_ATUAL || 0 }}
                {{ medicamento.UNIDADE_MEDIDA }}
              </q-item-label>
            </q-item-section>

            <q-item-section side>
              <div class="q-gutter-sm">
                <q-btn
                  color="red"
                  icon="delete"
                  label="Descartar"
                  size="sm"
                  @click="descartarMedicamento(medicamento)"
                />
                <q-btn
                  color="warning"
                  icon="update"
                  label="Novo Lote"
                  size="sm"
                  @click="atualizarLote(medicamento)"
                />
              </div>
            </q-item-section>
          </q-item>
        </q-list>
      </q-tab-panel>

      <!-- Sem Estoque -->
      <q-tab-panel name="sem-estoque">
        <div
          v-if="alertas.semEstoque.length === 0"
          class="text-center q-pa-lg"
        >
          <q-icon
            name="check_circle"
            size="4rem"
            color="positive"
          />
          <div class="text-h6 q-mt-md">Todos os medicamentos têm estoque!</div>
          <div class="text-caption text-grey">Não há medicamentos zerados.</div>
        </div>

        <q-list v-else>
          <q-item
            v-for="medicamento in alertas.semEstoque"
            :key="medicamento.ID"
            class="q-mb-sm"
          >
            <q-item-section avatar>
              <q-avatar
                color="grey"
                text-color="white"
                icon="inventory"
              />
            </q-item-section>

            <q-item-section>
              <q-item-label class="text-weight-bold">
                {{ medicamento.NOME }}
              </q-item-label>
              <q-item-label caption>
                {{ medicamento.PRINCIPIO_ATIVO }}
              </q-item-label>
              <q-item-label caption>
                <q-chip
                  dense
                  color="grey"
                  text-color="white"
                >
                  SEM ESTOQUE
                </q-chip>
              </q-item-label>
            </q-item-section>

            <q-item-section>
              <q-item-label caption>Estoque Atual</q-item-label>
              <q-item-label class="text-grey text-weight-bold">
                0 {{ medicamento.UNIDADE_MEDIDA }}
              </q-item-label>
              <q-item-label caption>
                Mín: {{ medicamento.ESTOQUE_MINIMO }}
                {{ medicamento.UNIDADE_MEDIDA }}
              </q-item-label>
            </q-item-section>

            <q-item-section>
              <q-item-label caption>Valor Unitário</q-item-label>
              <q-item-label>
                R$ {{ (medicamento.PRECO_UNITARIO || 0).toFixed(2) }}
              </q-item-label>
            </q-item-section>

            <q-item-section side>
              <div class="q-gutter-sm">
                <q-btn
                  color="positive"
                  icon="add_shopping_cart"
                  label="Comprar"
                  size="sm"
                  @click="$emit('comprar', medicamento)"
                />
                <q-btn
                  color="primary"
                  icon="visibility"
                  label="Ver"
                  size="sm"
                  flat
                  @click="verDetalhes(medicamento)"
                />
              </div>
            </q-item-section>
          </q-item>
        </q-list>
      </q-tab-panel>
    </q-tab-panels>
  </div>
</template>

<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useQuasar } from 'quasar'
  import { useMedicamentoStore } from 'stores/medicamento'
  import { ErrorHandler } from 'src/utils/errorHandler'
  import { formatDate } from 'src/utils/dateUtils'

  // Emits
  const emit = defineEmits(['comprar', 'abrir-entrada-lote'])

  // Store
  const medicamentoStore = useMedicamentoStore()

  // Estado reativo
  const activeAlertTab = ref('estoque-baixo')

  // Computed
  const alertas = computed(() => {
    const medicamentos = medicamentoStore.medicamentos || []
    const hoje = new Date()

    const estoqueBaixo = medicamentos.filter(m => {
      const estoque = m.ESTOQUE_ATUAL || 0
      const minimo = m.ESTOQUE_MINIMO || 0
      return estoque > 0 && estoque <= minimo
    })

    const vencendo = medicamentos.filter(m => {
      if (!m.DATA_VALIDADE) return false
      const validade = new Date(m.DATA_VALIDADE)
      const diffDias = Math.ceil((validade - hoje) / (1000 * 60 * 60 * 24))
      return diffDias > 0 && diffDias <= 30 && (m.ESTOQUE_ATUAL || 0) > 0
    })

    const vencidos = medicamentos.filter(m => {
      if (!m.DATA_VALIDADE) return false
      const validade = new Date(m.DATA_VALIDADE)
      const diffDias = Math.ceil((validade - hoje) / (1000 * 60 * 60 * 24))
      return diffDias < 0 && (m.ESTOQUE_ATUAL || 0) > 0
    })

    const semEstoque = medicamentos.filter(m => {
      const estoque = m.ESTOQUE_ATUAL || 0
      return estoque === 0
    })

    return {
      estoqueBaixo,
      vencendo,
      vencidos,
      semEstoque,
    }
  })

  // Métodos
  async function loadAlertas() {
    try {
      await medicamentoStore.fetchMedicamentos()
      await medicamentoStore.fetchAlertasEstoque()
    } catch (error) {
      console.error('Erro ao carregar alertas:', error)
    }
  }

  function getDiasParaVencimento(dataValidade) {
    if (!dataValidade) return 0

    const hoje = new Date()
    const validade = new Date(dataValidade)
    return Math.ceil((validade - hoje) / (1000 * 60 * 60 * 24))
  }

  function verDetalhes(medicamento) {
    // Emitir evento ou navegar para detalhes
    console.log('Ver detalhes:', medicamento)
  }

  async function atualizarLote(medicamento) {
    try {
      // Emitir evento para abrir o componente ControleEstoque
      // com dados pré-preenchidos para entrada de novo lote
      emit('abrir-entrada-lote', {
        medicamento_id: medicamento.ID,
        medicamento_nome: medicamento.NOME,
        motivo: 'Novo lote - substituição por vencimento',
        tipo: 'ENTRADA',
        observacoes: `Substituição do lote ${medicamento.LOTE_ATUAL || 'anterior'} por vencimento`,
      })
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao processar novo lote')
    }
  }

  async function descartarMedicamento(medicamento) {
    try {
      // Confirmar descarte usando Quasar Dialog
      const $q = useQuasar ? useQuasar() : null

      const confirmar = await new Promise(resolve => {
        if ($q) {
          $q.dialog({
            title: 'Confirmar Descarte',
            message: `Descartar ${medicamento.ESTOQUE_ATUAL} ${medicamento.UNIDADE_MEDIDA} de ${medicamento.NOME}?\n\nEsta ação criará uma movimentação de saída e zerará o estoque.`,
            cancel: true,
            persistent: true,
          })
            .onOk(() => resolve(true))
            .onCancel(() => resolve(false))
        } else {
          resolve(
            confirm(
              `Descartar ${medicamento.ESTOQUE_ATUAL} ${medicamento.UNIDADE_MEDIDA} de ${medicamento.NOME}?`
            )
          )
        }
      })

      if (confirmar) {
        // Criar movimentação de saída usando o store
        const movimentacao = {
          ID_MEDICAMENTO: medicamento.ID,
          TIPO_MOVIMENTACAO: 'SAIDA',
          QUANTIDADE: medicamento.ESTOQUE_ATUAL,
          MOTIVO: 'Descarte por vencimento',
          OBSERVACOES: `Medicamento vencido em ${formatDate(medicamento.DATA_VALIDADE)}. Lote: ${medicamento.LOTE_ATUAL || 'N/A'}`,
        }

        await medicamentoStore.createMovimentacao(movimentacao)
        ErrorHandler.success('Medicamento descartado com sucesso!')
        await loadAlertas()
      }
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao descartar medicamento')
    }
  }

  // Lifecycle
  onMounted(() => {
    loadAlertas()
  })

  // Expor métodos
  defineExpose({
    loadAlertas,
  })
</script>
