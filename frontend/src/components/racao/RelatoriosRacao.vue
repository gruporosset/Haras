<template>
  <div class="relatorios-racao-container">
    <!-- HEADER -->
    <div class="text-h6 text-primary q-mb-md">
      <q-icon
        name="analytics"
        class="q-mr-sm"
      />
      Relatórios de Ração e Suplementos
    </div>

    <!-- ESTATÍSTICAS GERAIS -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-subtitle1 q-mb-md">Estatísticas Gerais</div>
        <div class="row q-gutter-md">
          <div class="col-md-2 col-6">
            <q-card
              flat
              bordered
            >
              <q-card-section class="text-center q-pa-sm">
                <div class="text-h4 text-primary">
                  {{ estatisticasGerais.totalProdutos }}
                </div>
                <div class="text-subtitle2">Produtos</div>
                <div class="text-caption text-grey-6">Cadastrados</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-md-2 col-6">
            <q-card
              flat
              bordered
            >
              <q-card-section class="text-center q-pa-sm">
                <div class="text-h4 text-green">
                  {{ estatisticasGerais.planosAtivos }}
                </div>
                <div class="text-subtitle2">Planos</div>
                <div class="text-caption text-grey-6">Ativos</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-md-2 col-6">
            <q-card
              flat
              bordered
            >
              <q-card-section class="text-center q-pa-sm">
                <div class="text-h4 text-orange">
                  {{
                    racaoStore.formatarMoeda(
                      estatisticasGerais.valorTotalEstoque
                    )
                  }}
                </div>
                <div class="text-subtitle2">Estoque</div>
                <div class="text-caption text-grey-6">Valor Total</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-md-2 col-6">
            <q-card
              flat
              bordered
            >
              <q-card-section class="text-center q-pa-sm">
                <div class="text-h4 text-blue">
                  {{ racaoStore.formatarMoeda(estatisticasGerais.custoMensal) }}
                </div>
                <div class="text-subtitle2">Custo</div>
                <div class="text-caption text-grey-6">Mensal Estimado</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-md-2 col-6">
            <q-card
              flat
              bordered
            >
              <q-card-section class="text-center q-pa-sm">
                <div class="text-h4 text-red">
                  {{ estatisticasGerais.alertasAtivos }}
                </div>
                <div class="text-subtitle2">Alertas</div>
                <div class="text-caption text-grey-6">Estoque Baixo</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- CARDS DE RELATÓRIOS -->
    <div class="row q-gutter-md">
      <!-- ESTOQUE BAIXO -->
      <div class="col-md-6 col-12">
        <q-card>
          <q-card-section>
            <div class="row items-center justify-between">
              <div class="text-h6">
                <q-icon
                  name="warning"
                  class="q-mr-sm text-warning"
                />
                Produtos com Estoque Baixo
              </div>
              <q-btn
                flat
                color="primary"
                label="Atualizar"
                @click="loadEstoqueBaixo"
              />
            </div>
          </q-card-section>

          <q-card-section class="q-pt-none">
            <q-table
              :rows="estoqueBaixo"
              :columns="estoqueColumns"
              row-key="produto_id"
              :loading="loadingEstoque"
              flat
              :pagination="{ rowsPerPage: 10 }"
            >
              <template v-slot:body-cell-status_alerta="props">
                <q-td :props="props">
                  <q-chip
                    :color="racaoStore.getStatusColor(props.value)"
                    text-color="white"
                    size="sm"
                  >
                    {{ getStatusLabel(props.value) }}
                  </q-chip>
                </q-td>
              </template>

              <template v-slot:body-cell-estoque_atual="props">
                <q-td :props="props">
                  {{ racaoStore.formatarPeso(props.value) }}
                </q-td>
              </template>

              <template v-slot:body-cell-estoque_minimo="props">
                <q-td :props="props">
                  {{ racaoStore.formatarPeso(props.value) }}
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>

      <!-- PREVISÃO DE CONSUMO -->
      <div class="col-md-6 col-12">
        <q-card>
          <q-card-section>
            <div class="row items-center justify-between">
              <div class="text-h6">
                <q-icon
                  name="trending_up"
                  class="q-mr-sm text-blue"
                />
                Previsão de Consumo
              </div>
              <q-btn
                flat
                color="primary"
                label="Atualizar"
                @click="loadPrevisaoConsumo"
              />
            </div>
          </q-card-section>

          <q-card-section class="q-pt-none">
            <q-table
              :rows="previsaoConsumo"
              :columns="previsaoColumns"
              row-key="produto_id"
              :loading="loadingPrevisao"
              flat
              :pagination="{ rowsPerPage: 10 }"
            >
              <template v-slot:body-cell-consumo_diario_medio="props">
                <q-td :props="props">
                  {{ racaoStore.formatarPeso(props.value) }}/dia
                </q-td>
              </template>

              <template v-slot:body-cell-estoque_atual="props">
                <q-td :props="props">
                  {{ racaoStore.formatarPeso(props.value) }}
                </q-td>
              </template>

              <template v-slot:body-cell-dias_restantes="props">
                <q-td :props="props">
                  <q-chip
                    :color="getDiasRestantesColor(props.value)"
                    text-color="white"
                    size="sm"
                  >
                    {{ props.value }} dias
                  </q-chip>
                </q-td>
              </template>

              <template v-slot:body-cell-recomendacao="props">
                <q-td :props="props">
                  <q-chip
                    :color="getRecomendacaoColor(props.value)"
                    text-color="white"
                    size="sm"
                  >
                    {{ getRecomendacaoLabel(props.value) }}
                  </q-chip>
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- CONSUMO POR ANIMAL -->
    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row items-center justify-between q-mb-md">
          <div class="text-h6">
            <q-icon
              name="pets"
              class="q-mr-sm text-green"
            />
            Consumo por Animal
          </div>
          <div class="row q-gutter-md">
            <q-input
              v-model="filtrosConsumo.data_inicio"
              label="Data Início"
              type="date"
              dense
              class="col-4"
            />
            <q-input
              v-model="filtrosConsumo.data_fim"
              label="Data Fim"
              type="date"
              dense
              class="col-4"
            />
            <calendario-component
              v-model="form.DATA_INICIO"
              label="Data de Início *"
              :rules="[val => !!val || 'Data de início é obrigatória']"
              class="col-5"
            />

            <calendario-component
              v-model="form.DATA_FIM"
              label="Data de Fim (opcional)"
              class="col-5"
            />

            <q-btn
              color="primary"
              label="Buscar"
              @click="loadConsumoAnimal"
            />
          </div>
        </div>

        <q-table
          :rows="consumoAnimal"
          :columns="consumoColumns"
          row-key="animal_id"
          :loading="loadingConsumo"
          flat
          :pagination="{ rowsPerPage: 15 }"
        >
          <template v-slot:body-cell-animal_nome="props">
            <q-td :props="props">
              <div class="text-weight-medium">{{ props.value }}</div>
              <div class="text-caption text-grey-6">
                {{ props.row.numero_registro }}
              </div>
            </q-td>
          </template>

          <template v-slot:body-cell-tipo_alimento="props">
            <q-td :props="props">
              <q-chip
                :color="getTipoAlimentoColor(props.value)"
                text-color="white"
                size="sm"
              >
                {{ racaoStore.getTipoAlimentoLabel(props.value) }}
              </q-chip>
            </q-td>
          </template>

          <template v-slot:body-cell-total_consumido="props">
            <q-td :props="props">
              {{ racaoStore.formatarPeso(props.value) }}
            </q-td>
          </template>

          <template v-slot:body-cell-media_diaria="props">
            <q-td :props="props">
              {{ racaoStore.formatarPeso(props.value) }}/dia
            </q-td>
          </template>

          <template v-slot:body-cell-custo_total="props">
            <q-td :props="props">
              {{ racaoStore.formatarMoeda(props.value) }}
            </q-td>
          </template>

          <template v-slot:body-cell-ultima_refeicao="props">
            <q-td :props="props">
              {{ formatarData(props.value) }}
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>

    <!-- GRÁFICOS E ANÁLISES -->
    <div class="row q-gutter-md q-mt-md">
      <!-- DISTRIBUIÇÃO POR TIPO -->
      <div class="col-md-6 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon
                name="pie_chart"
                class="q-mr-sm text-purple"
              />
              Distribuição por Tipo de Alimento
            </div>

            <div class="row q-gutter-sm">
              <div
                v-for="tipo in distribuicaoTipos"
                :key="tipo.tipo"
                class="col-12"
              >
                <div class="row items-center q-mb-xs">
                  <div class="col-6">
                    <q-chip
                      :color="getTipoAlimentoColor(tipo.tipo)"
                      text-color="white"
                      size="sm"
                    >
                      {{ racaoStore.getTipoAlimentoLabel(tipo.tipo) }}
                    </q-chip>
                  </div>
                  <div class="col-3 text-right">
                    {{ tipo.quantidade }} produtos
                  </div>
                  <div class="col-3 text-right">
                    {{ racaoStore.formatarPercentual(tipo.percentual) }}
                  </div>
                </div>
                <q-linear-progress
                  :value="tipo.percentual / 100"
                  :color="getTipoAlimentoColor(tipo.tipo)"
                  size="8px"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- TOP 10 PRODUTOS MAIS CONSUMIDOS -->
      <div class="col-md-6 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon
                name="leaderboard"
                class="q-mr-sm text-indigo"
              />
              Top 10 Produtos Mais Consumidos
            </div>

            <q-list>
              <q-item
                v-for="(produto, index) in topProdutos"
                :key="produto.produto_id"
              >
                <q-item-section avatar>
                  <q-chip
                    :color="
                      index < 3 ? ['gold', 'silver', '#cd7f32'][index] : 'grey'
                    "
                    text-color="white"
                    size="sm"
                  >
                    {{ index + 1 }}º
                  </q-chip>
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ produto.produto_nome }}</q-item-label>
                  <q-item-label caption>
                    {{ racaoStore.getTipoAlimentoLabel(produto.tipo_alimento) }}
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label>
                    {{ racaoStore.formatarPeso(produto.total_consumido) }}
                  </q-item-label>
                  <q-item-label caption>
                    {{ racaoStore.formatarMoeda(produto.custo_total) }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- AÇÕES RÁPIDAS -->
    <q-card class="q-mt-md">
      <q-card-section>
        <div class="text-h6 q-mb-md">Ações Rápidas</div>
        <div class="row q-gutter-md">
          <q-btn
            color="primary"
            icon="download"
            label="Exportar Relatório Completo"
            @click="exportarRelatorio"
          />
          <q-btn
            color="secondary"
            icon="email"
            label="Enviar Relatório por Email"
            @click="enviarEmail"
          />
          <q-btn
            color="info"
            icon="refresh"
            label="Atualizar Todos os Dados"
            @click="atualizarTodos"
          />
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useQuasar } from 'quasar'
import { useRacaoStore } from 'stores/racao'
import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

// Composables
const $q = useQuasar()
const racaoStore = useRacaoStore()

// Estado reativo
const estoqueBaixo = ref([])
const previsaoConsumo = ref([])
const consumoAnimal = ref([])
const loadingEstoque = ref(false)
const loadingPrevisao = ref(false)
const loadingConsumo = ref(false)

// Filtros
const filtrosConsumo = ref({
  data_inicio: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
    .toISOString()
    .split('T')[0],
  data_fim: new Date().toISOString().split('T')[0],
})

// Computed
const estatisticasGerais = computed(() => {
  const produtos = racaoStore.estatisticasProdutos
  const planos = racaoStore.estatisticasPlanos
  const alertas = estoqueBaixo.value.filter(e =>
    ['SEM_ESTOQUE', 'ESTOQUE_BAIXO', 'VENCIDO'].includes(e.status_alerta)
  ).length

  return {
    totalProdutos: produtos.totalProdutos || 0,
    planosAtivos: planos.planosAtivos || 0,
    valorTotalEstoque: produtos.valorTotalEstoque || 0,
    custoMensal: planos.custoMensalEstimado || 0,
    alertasAtivos: alertas,
  }
})

const distribuicaoTipos = computed(() => {
  const tipos = {}
  racaoStore.produtos.forEach(p => {
    if (!tipos[p.TIPO_ALIMENTO]) {
      tipos[p.TIPO_ALIMENTO] = { quantidade: 0, tipo: p.TIPO_ALIMENTO }
    }
    tipos[p.TIPO_ALIMENTO].quantidade++
  })

  const total = racaoStore.produtos.length
  return Object.values(tipos)
    .map(t => ({
      ...t,
      percentual: total > 0 ? (t.quantidade / total) * 100 : 0,
    }))
    .sort((a, b) => b.quantidade - a.quantidade)
})

const topProdutos = computed(() => {
  return [...consumoAnimal.value]
    .sort((a, b) => b.total_consumido - a.total_consumido)
    .slice(0, 10)
})

// Colunas
const estoqueColumns = [
  { name: 'nome', label: 'Produto', field: 'nome', align: 'left' },
  {
    name: 'estoque_atual',
    label: 'Atual',
    field: 'estoque_atual',
    align: 'right',
  },
  {
    name: 'estoque_minimo',
    label: 'Mínimo',
    field: 'estoque_minimo',
    align: 'right',
  },
  {
    name: 'status_alerta',
    label: 'Status',
    field: 'status_alerta',
    align: 'center',
  },
]

const previsaoColumns = [
  {
    name: 'produto_nome',
    label: 'Produto',
    field: 'produto_nome',
    align: 'left',
  },
  {
    name: 'consumo_diario_medio',
    label: 'Consumo Médio',
    field: 'consumo_diario_medio',
    align: 'right',
  },
  {
    name: 'estoque_atual',
    label: 'Estoque',
    field: 'estoque_atual',
    align: 'right',
  },
  {
    name: 'dias_restantes',
    label: 'Dias Rest.',
    field: 'dias_restantes',
    align: 'center',
  },
  {
    name: 'recomendacao',
    label: 'Recomendação',
    field: 'recomendacao',
    align: 'center',
  },
]

const consumoColumns = [
  { name: 'animal_nome', label: 'Animal', field: 'animal_nome', align: 'left' },
  {
    name: 'produto_nome',
    label: 'Produto',
    field: 'produto_nome',
    align: 'left',
  },
  {
    name: 'tipo_alimento',
    label: 'Tipo',
    field: 'tipo_alimento',
    align: 'center',
  },
  {
    name: 'total_consumido',
    label: 'Total',
    field: 'total_consumido',
    align: 'right',
  },
  {
    name: 'media_diaria',
    label: 'Média Diária',
    field: 'media_diaria',
    align: 'right',
  },
  { name: 'custo_total', label: 'Custo', field: 'custo_total', align: 'right' },
  {
    name: 'ultima_refeicao',
    label: 'Última Refeição',
    field: 'ultima_refeicao',
    align: 'left',
  },
]

// Métodos
async function loadEstoqueBaixo() {
  loadingEstoque.value = true
  try {
    estoqueBaixo.value = await racaoStore.getEstoqueBaixo()
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao carregar estoque baixo' })
  } finally {
    loadingEstoque.value = false
  }
}

async function loadPrevisaoConsumo() {
  loadingPrevisao.value = true
  try {
    previsaoConsumo.value = await racaoStore.getPrevisaoConsumo()
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao carregar previsão' })
  } finally {
    loadingPrevisao.value = false
  }
}

async function loadConsumoAnimal() {
  loadingConsumo.value = true
  try {
    consumoAnimal.value = await racaoStore.getConsumoAnimal(
      filtrosConsumo.value
    )
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao carregar consumo' })
  } finally {
    loadingConsumo.value = false
  }
}

async function atualizarTodos() {
  $q.loading.show({ message: 'Atualizando relatórios...' })
  try {
    await Promise.all([
      loadEstoqueBaixo(),
      loadPrevisaoConsumo(),
      loadConsumoAnimal(),
    ])
    $q.notify({ type: 'positive', message: 'Relatórios atualizados!' })
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao atualizar' })
  } finally {
    $q.loading.hide()
  }
}

function exportarRelatorio() {
  $q.notify({
    type: 'info',
    message: 'Função de exportação em desenvolvimento',
  })
}

function enviarEmail() {
  $q.notify({ type: 'info', message: 'Função de email em desenvolvimento' })
}

// Funções auxiliares
function getStatusLabel(status) {
  const labels = {
    SEM_ESTOQUE: 'Sem Estoque',
    ESTOQUE_BAIXO: 'Baixo',
    VENCIMENTO_PROXIMO: 'Vencendo',
    VENCIDO: 'Vencido',
    OK: 'OK',
  }
  return labels[status] || status
}

function getDiasRestantesColor(dias) {
  if (dias <= 7) return 'red'
  if (dias <= 15) return 'orange'
  return 'green'
}

function getRecomendacaoColor(recomendacao) {
  const cores = {
    COMPRAR_URGENTE: 'red',
    COMPRAR_BREVE: 'orange',
    OK: 'green',
  }
  return cores[recomendacao] || 'grey'
}

function getRecomendacaoLabel(recomendacao) {
  const labels = {
    COMPRAR_URGENTE: 'Urgente',
    COMPRAR_BREVE: 'Breve',
    OK: 'OK',
  }
  return labels[recomendacao] || recomendacao
}

function getTipoAlimentoColor(tipo) {
  const cores = {
    CONCENTRADO: 'primary',
    VOLUMOSO: 'green',
    SUPLEMENTO: 'orange',
    PREMIX: 'purple',
    SAL_MINERAL: 'brown',
  }
  return cores[tipo] || 'grey'
}

function formatarData(data) {
  if (!data) return '-'
  return new Date(data).toLocaleDateString('pt-BR')
}

// Lifecycle
onMounted(async () => {
  await atualizarTodos()
})
</script>

<style scoped>
.relatorios-racao-container {
  width: 100%;
}
</style>