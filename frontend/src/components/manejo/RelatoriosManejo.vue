<template>
  <div class="relatorios-manejo-container">
    <!-- HEADER COM FILTROS GLOBAIS -->
    <q-card
      flat
      class="q-mb-md"
    >
      <q-card-section>
        <div class="text-h6 text-primary q-mb-md">
          <q-icon
            name="analytics"
            class="q-mr-sm"
          />
          Relatórios e Análises de Manejo
        </div>

        <div class="row q-gutter-md items-end">
          <div class="col-md-2 col-12">
            <calendario-component
              v-model="filtrosGlobais.data_inicio"
              label="Data Início"
              @update:model-value="onGlobalFilterChange"
            />
          </div>

          <div class="col-md-2 col-12">
            <calendario-component
              v-model="filtrosGlobais.data_fim"
              label="Data Fim"
              @update:model-value="onGlobalFilterChange"
            />
          </div>

          <div class="col-md-3 col-12">
            <q-select
              v-model="filtrosGlobais.terrenos"
              :options="terrenoOptions"
              label="Terrenos"
              multiple
              dense
              clearable
              use-chips
              @update:model-value="onGlobalFilterChange"
            />
          </div>

          <!-- <div class="col-auto">
            <q-btn
              color="primary"
              icon="refresh"
              label="Atualizar"
              @click="refreshAllReports"
            />
          </div>
          
          <div class="col-auto">
            <q-btn
              color="secondary"
              icon="download"
              label="Exportar Tudo"
              @click="exportAllReports"
            />
          </div> -->
        </div>
      </q-card-section>
    </q-card>

    <!-- ESTATÍSTICAS GERAIS -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6 text-primary q-mb-md">
          <q-icon
            name="bar_chart"
            class="q-mr-sm"
          />
          Estatísticas Gerais - {{ getPeriodoAtual() }}
        </div>

        <div class="row q-gutter-md">
          <div class="col-md-2 col-6">
            <q-card
              flat
              bordered
            >
              <q-card-section class="text-center q-pa-sm">
                <div class="text-h4 text-primary">
                  {{ estatisticasGerais.totalAplicacoes }}
                </div>
                <div class="text-subtitle2">Aplicações</div>
                <div class="text-caption text-grey-6">No período</div>
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
                  {{ estatisticasGerais.terrenosManejados }}
                </div>
                <div class="text-subtitle2">Terrenos</div>
                <div class="text-caption text-grey-6">Manejados</div>
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
                  {{ manejoStore.formatarMoeda(estatisticasGerais.custoTotal) }}
                </div>
                <div class="text-subtitle2">Custo Total</div>
                <div class="text-caption text-grey-6">Investido</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-md-2 col-6">
            <q-card
              flat
              bordered
            >
              <q-card-section class="text-center q-pa-sm">
                <div class="text-h4 text-purple">
                  {{ estatisticasGerais.produtosUtilizados }}
                </div>
                <div class="text-subtitle2">Produtos</div>
                <div class="text-caption text-grey-6">Utilizados</div>
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
                  {{ estatisticasGerais.analisesSolo }}
                </div>
                <div class="text-subtitle2">Análises</div>
                <div class="text-caption text-grey-6">De solo</div>
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
                <div class="text-caption text-grey-6">Ativos</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- CARDS DE RELATÓRIOS -->
    <div class="row q-gutter-md">
      <!-- CONSUMO POR TERRENO -->
      <div class="col-md-6 col-12">
        <q-card>
          <q-card-section>
            <div class="row items-center justify-between">
              <div class="text-h6 text-green">
                <q-icon
                  name="landscape"
                  class="q-mr-sm"
                />
                Consumo por Terreno
              </div>
              <q-btn-group flat>
                <q-btn
                  flat
                  round
                  color="grey"
                  icon="refresh"
                  size="sm"
                  @click="loadConsumoTerreno"
                >
                  <q-tooltip>Atualizar</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  round
                  color="grey"
                  icon="download"
                  size="sm"
                  @click="exportConsumoTerreno"
                >
                  <q-tooltip>Exportar</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  round
                  color="grey"
                  icon="fullscreen"
                  size="sm"
                  @click="viewFullReport('consumo')"
                >
                  <q-tooltip>Ver Completo</q-tooltip>
                </q-btn>
              </q-btn-group>
            </div>

            <div
              class="q-mt-md"
              style="height: 300px; overflow-y: auto"
            >
              <q-list
                v-if="consumoTerreno.length > 0"
                dense
              >
                <q-item
                  v-for="item in consumoTerreno.slice(0, 10)"
                  :key="`${item.terreno_id}-${item.produto_nome}`"
                >
                  <q-item-section>
                    <q-item-label>{{ item.terreno_nome }}</q-item-label>
                    <q-item-label caption>
                      {{ item.produto_nome }} - {{ item.tipo_manejo }}
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>
                      {{ item.total_aplicado?.toLocaleString('pt-BR') }}
                      {{ item.unidade_medida }}
                    </q-item-label>
                    <q-item-label caption>
                      {{ item.numero_aplicacoes }} aplicações
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label v-if="item.custo_total">
                      {{ manejoStore.formatarMoeda(item.custo_total) }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>

              <div
                v-else
                class="text-center q-pa-md text-grey-6"
              >
                <q-icon
                  name="info"
                  size="lg"
                  class="q-mb-sm"
                />
                <div>Nenhum dado de consumo encontrado</div>
                <div class="text-caption">
                  Ajuste os filtros ou verifique se há aplicações registradas
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- PREVISÃO DE CONSUMO -->
      <div class="col-md-6 col-12">
        <q-card>
          <q-card-section>
            <div class="row items-center justify-between">
              <div class="text-h6 text-orange">
                <q-icon
                  name="trending_up"
                  class="q-mr-sm"
                />
                Previsão de Consumo
              </div>
              <q-btn-group flat>
                <q-btn
                  flat
                  round
                  color="grey"
                  icon="refresh"
                  size="sm"
                  @click="loadPrevisaoConsumo"
                >
                  <q-tooltip>Atualizar</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  round
                  color="grey"
                  icon="download"
                  size="sm"
                  @click="exportPrevisaoConsumo"
                >
                  <q-tooltip>Exportar</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  round
                  color="grey"
                  icon="fullscreen"
                  size="sm"
                  @click="viewFullReport('previsao')"
                >
                  <q-tooltip>Ver Completo</q-tooltip>
                </q-btn>
              </q-btn-group>
            </div>

            <div
              class="q-mt-md"
              style="height: 300px; overflow-y: auto"
            >
              <q-list
                v-if="previsaoConsumo.length > 0"
                dense
              >
                <q-item
                  v-for="item in previsaoConsumo"
                  :key="item.produto_id"
                >
                  <q-item-section>
                    <q-item-label>{{ item.produto_nome }}</q-item-label>
                    <q-item-label caption>
                      Consumo: {{ item.consumo_mensal_medio?.toFixed(1) }}/mês
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>
                      {{ item.estoque_atual?.toLocaleString('pt-BR') }}
                    </q-item-label>
                    <q-item-label caption>
                      {{ item.dias_restantes }} dias restantes
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-chip
                      :color="getCorRecomendacao(item.recomendacao)"
                      text-color="white"
                      size="sm"
                    >
                      {{ getRecomendacaoLabel(item.recomendacao) }}
                    </q-chip>
                  </q-item-section>
                </q-item>
              </q-list>

              <div
                v-else
                class="text-center q-pa-md text-grey-6"
              >
                <q-icon
                  name="info"
                  size="lg"
                  class="q-mb-sm"
                />
                <div>Nenhuma previsão disponível</div>
                <div class="text-caption">
                  É necessário histórico de aplicações para gerar previsões
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- TERRENOS PARA LIBERAÇÃO -->
      <div class="col-md-6 col-12">
        <q-card>
          <q-card-section>
            <div class="row items-center justify-between">
              <div class="text-h6 text-purple">
                <q-icon
                  name="schedule"
                  class="q-mr-sm"
                />
                Cronograma de Liberação
              </div>
              <q-btn-group flat>
                <q-select
                  v-model="diasLiberacao"
                  :options="[
                    { label: '7 dias', value: 7 },
                    { label: '15 dias', value: 15 },
                    { label: '30 dias', value: 30 },
                    { label: '60 dias', value: 60 },
                  ]"
                  dense
                  borderless
                  @update:model-value="loadTerrenosLiberacao"
                />
                <q-btn
                  flat
                  round
                  color="grey"
                  icon="refresh"
                  size="sm"
                  @click="loadTerrenosLiberacao"
                >
                  <q-tooltip>Atualizar</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  round
                  color="grey"
                  icon="download"
                  size="sm"
                  @click="exportTerrenosLiberacao"
                >
                  <q-tooltip>Exportar</q-tooltip>
                </q-btn>
              </q-btn-group>
            </div>

            <div
              class="q-mt-md"
              style="height: 300px; overflow-y: auto"
            >
              <q-list
                v-if="terrenosLiberacao.length > 0"
                dense
              >
                <q-item
                  v-for="item in terrenosLiberacao"
                  :key="`${item.terreno_id}-${item.data_aplicacao}`"
                >
                  <q-item-section>
                    <q-item-label>{{ item.terreno_nome }}</q-item-label>
                    <q-item-label caption>
                      {{ item.produto_nome }} - {{ item.tipo_manejo }}
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>
                      {{ formatarData(item.data_liberacao) }}
                    </q-item-label>
                    <q-item-label caption>
                      Aplicado: {{ formatarData(item.data_aplicacao) }}
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-chip
                      :color="getCorDiasLiberacao(item.dias_para_liberacao)"
                      text-color="white"
                      size="sm"
                    >
                      {{ item.dias_para_liberacao }}d
                    </q-chip>
                  </q-item-section>
                </q-item>
              </q-list>

              <div
                v-else
                class="text-center q-pa-md text-grey-6"
              >
                <q-icon
                  name="check_circle"
                  size="lg"
                  class="q-mb-sm text-positive"
                />
                <div>Nenhum terreno em carência</div>
                <div class="text-caption">
                  Todos os terrenos estão liberados para uso
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- RESUMO DE ESTOQUE -->
      <div class="col-md-6 col-12">
        <q-card>
          <q-card-section>
            <div class="row items-center justify-between">
              <div class="text-h6 text-blue">
                <q-icon
                  name="inventory"
                  class="q-mr-sm"
                />
                Resumo de Estoque
              </div>
              <q-btn-group flat>
                <q-btn
                  flat
                  round
                  color="grey"
                  icon="refresh"
                  size="sm"
                  @click="loadResumoEstoque"
                >
                  <q-tooltip>Atualizar</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  round
                  color="grey"
                  icon="download"
                  size="sm"
                  @click="exportResumoEstoque"
                >
                  <q-tooltip>Exportar</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  round
                  color="grey"
                  icon="fullscreen"
                  size="sm"
                  @click="viewFullReport('estoque')"
                >
                  <q-tooltip>Ver Completo</q-tooltip>
                </q-btn>
              </q-btn-group>
            </div>

            <div
              class="q-mt-md"
              style="height: 300px; overflow-y: auto"
            >
              <q-list
                v-if="resumoEstoque.length > 0"
                dense
              >
                <q-item
                  v-for="item in resumoEstoque.slice(0, 10)"
                  :key="item.produto_id"
                >
                  <q-item-section>
                    <q-item-label>{{ item.produto_nome }}</q-item-label>
                    <q-item-label caption>
                      {{ manejoStore.getTipoLabel(item.tipo_produto) }}
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>
                      {{ item.estoque_atual?.toLocaleString('pt-BR') }}
                      {{ item.unidade_medida }}
                    </q-item-label>
                    <q-item-label caption>
                      Mín: {{ item.estoque_minimo?.toLocaleString('pt-BR') }}
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label v-if="item.valor_entradas">
                      {{ manejoStore.formatarMoeda(item.valor_entradas) }}
                    </q-item-label>
                    <q-linear-progress
                      :value="getPercentualEstoque(item)"
                      :color="getCorEstoque(item)"
                      size="4px"
                      class="q-mt-xs"
                    />
                  </q-item-section>
                </q-item>
              </q-list>

              <div
                v-else
                class="text-center q-pa-md text-grey-6"
              >
                <q-icon
                  name="info"
                  size="lg"
                  class="q-mb-sm"
                />
                <div>Nenhum produto cadastrado</div>
                <div class="text-caption">
                  Cadastre produtos para ver o resumo de estoque
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- DIALOG VISUALIZAÇÃO COMPLETA -->
    <q-dialog
      v-model="fullReportDialog"
      persistent
      maximized
    >
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">{{ getFullReportTitle() }}</div>
          <q-space />
          <q-btn
            icon="close"
            flat
            round
            dense
            @click="fullReportDialog = false"
          />
        </q-card-section>

        <q-card-section style="height: calc(100vh - 120px); overflow-y: auto">
          <!-- CONSUMO COMPLETO -->
          <div v-if="fullReportType === 'consumo'">
            <q-table
              :rows="consumoTerreno"
              :columns="consumoColumns"
              row-key="terreno_id"
              flat
              :pagination="{ rowsPerPage: 50 }"
            >
              <template v-slot:body-cell-custo_total="props">
                <q-td :props="props">
                  {{
                    props.value ? manejoStore.formatarMoeda(props.value) : '-'
                  }}
                </q-td>
              </template>
            </q-table>
          </div>

          <!-- PREVISÃO COMPLETA -->
          <div v-if="fullReportType === 'previsao'">
            <q-table
              :rows="previsaoConsumo"
              :columns="previsaoColumns"
              row-key="produto_id"
              flat
              :pagination="{ rowsPerPage: 50 }"
            >
              <template v-slot:body-cell-recomendacao="props">
                <q-td :props="props">
                  <q-chip
                    :color="getCorRecomendacao(props.value)"
                    text-color="white"
                    size="sm"
                  >
                    {{ getRecomendacaoLabel(props.value) }}
                  </q-chip>
                </q-td>
              </template>
            </q-table>
          </div>

          <!-- ESTOQUE COMPLETO -->
          <div v-if="fullReportType === 'estoque'">
            <q-table
              :rows="resumoEstoque"
              :columns="estoqueColumns"
              row-key="produto_id"
              flat
              :pagination="{ rowsPerPage: 50 }"
            >
              <template v-slot:body-cell-status_estoque="props">
                <q-td :props="props">
                  <q-linear-progress
                    :value="getPercentualEstoque(props.row)"
                    :color="getCorEstoque(props.row)"
                    size="8px"
                  />
                  <div class="text-caption q-mt-xs">
                    {{
                      (getPercentualEstoque(props.row) * 100 || 0).toFixed(1)
                    }}%
                  </div>
                </q-td>
              </template>
            </q-table>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            color="primary"
            icon="download"
            label="Exportar"
            @click="exportFullReport"
          />
          <q-btn
            flat
            label="Fechar"
            color="grey"
            @click="fullReportDialog = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
  import { ref, onMounted, computed } from 'vue'
  import { useQuasar } from 'quasar'
  import { useManejoStore } from 'stores/manejo'
  import { useTerrenoStore } from 'stores/terreno'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'
  import { formatDate } from '../../utils/dateUtils'

  // Composables
  const $q = useQuasar()
  const manejoStore = useManejoStore()
  const terrenoStore = useTerrenoStore()

  // Estado reativo
  const fullReportDialog = ref(false)
  const fullReportType = ref('')

  // Filtros globais
  const filtrosGlobais = ref({
    data_inicio: '',
    data_fim: '',
    terrenos: [],
  })

  // Dados dos relatórios
  const consumoTerreno = ref([])
  const previsaoConsumo = ref([])
  const terrenosLiberacao = ref([])
  const resumoEstoque = ref([])

  // Configurações
  const diasLiberacao = ref({ label: '30 dias', value: 30 })

  // Opções
  const terrenoOptions = ref([])

  // Computed
  const estatisticasGerais = computed(() => {
    const aplicacoes = manejoStore.aplicacoes || []
    const produtos = manejoStore.produtos || []
    const analises = manejoStore.analisesSolo || []

    const terrenosUnicos = new Set(aplicacoes.map(a => a.ID_TERRENO))
    const produtosUnicos = new Set(aplicacoes.map(a => a.ID_PRODUTO))
    const custoTotal = aplicacoes.reduce(
      (sum, a) => sum + (a.CUSTO_TOTAL || 0),
      0
    )

    // Contar alertas ativos
    const alertasEstoque = produtos.filter(
      p => p.ATIVO === 'S' && (p.ESTOQUE_ATUAL || 0) <= (p.ESTOQUE_MINIMO || 0)
    ).length

    const alertasSolo = analises.filter(
      a =>
        (a.PH_AGUA && (a.PH_AGUA < 5.5 || a.PH_AGUA > 7.5)) ||
        (a.MATERIA_ORGANICA && a.MATERIA_ORGANICA < 2.0) ||
        (a.SATURACAO_BASES && a.SATURACAO_BASES < 50)
    ).length

    return {
      totalAplicacoes: aplicacoes.length,
      terrenosManejados: terrenosUnicos.size,
      custoTotal,
      produtosUtilizados: produtosUnicos.size,
      analisesSolo: analises.length,
      alertasAtivos:
        alertasEstoque + alertasSolo + terrenosLiberacao.value.length,
    }
  })

  // Colunas das tabelas
  const consumoColumns = [
    {
      name: 'terreno_nome',
      label: 'Terreno',
      field: 'terreno_nome',
      sortable: true,
      align: 'left',
    },
    {
      name: 'produto_nome',
      label: 'Produto',
      field: 'produto_nome',
      sortable: true,
      align: 'left',
    },
    {
      name: 'tipo_manejo',
      label: 'Tipo',
      field: 'tipo_manejo',
      sortable: true,
      align: 'left',
    },
    {
      name: 'total_aplicado',
      label: 'Total Aplicado',
      field: 'total_aplicado',
      sortable: true,
      align: 'right',
    },
    {
      name: 'unidade_medida',
      label: 'Unidade',
      field: 'unidade_medida',
      align: 'center',
    },
    {
      name: 'numero_aplicacoes',
      label: 'Nº Aplicações',
      field: 'numero_aplicacoes',
      sortable: true,
      align: 'center',
    },
    {
      name: 'custo_total',
      label: 'Custo Total',
      field: 'custo_total',
      sortable: true,
      align: 'right',
    },
  ]

  const previsaoColumns = [
    {
      name: 'produto_nome',
      label: 'Produto',
      field: 'produto_nome',
      sortable: true,
      align: 'left',
    },
    {
      name: 'consumo_mensal_medio',
      label: 'Consumo Mensal',
      field: 'consumo_mensal_medio',
      sortable: true,
      align: 'right',
    },
    {
      name: 'estoque_atual',
      label: 'Estoque Atual',
      field: 'estoque_atual',
      sortable: true,
      align: 'right',
    },
    {
      name: 'dias_restantes',
      label: 'Dias Restantes',
      field: 'dias_restantes',
      sortable: true,
      align: 'center',
    },
    {
      name: 'data_prevista_fim',
      label: 'Previsão Fim',
      field: 'data_prevista_fim',
      sortable: true,
      align: 'left',
    },
    {
      name: 'recomendacao',
      label: 'Recomendação',
      field: 'recomendacao',
      align: 'center',
    },
  ]

  const estoqueColumns = [
    {
      name: 'produto_nome',
      label: 'Produto',
      field: 'produto_nome',
      sortable: true,
      align: 'left',
    },
    {
      name: 'tipo_produto',
      label: 'Tipo',
      field: 'tipo_produto',
      sortable: true,
      align: 'left',
    },
    {
      name: 'estoque_atual',
      label: 'Estoque Atual',
      field: 'estoque_atual',
      sortable: true,
      align: 'right',
    },
    {
      name: 'estoque_minimo',
      label: 'Estoque Mínimo',
      field: 'estoque_minimo',
      sortable: true,
      align: 'right',
    },
    {
      name: 'total_entradas',
      label: 'Total Entradas',
      field: 'total_entradas',
      sortable: true,
      align: 'right',
    },
    {
      name: 'total_saidas',
      label: 'Total Saídas',
      field: 'total_saidas',
      sortable: true,
      align: 'right',
    },
    {
      name: 'valor_entradas',
      label: 'Valor Entradas',
      field: 'valor_entradas',
      sortable: true,
      align: 'right',
    },
    {
      name: 'status_estoque',
      label: 'Status',
      field: 'status_estoque',
      align: 'center',
    },
  ]

  // Métodos de carregamento
  async function loadConsumoTerreno() {
    try {
      const params = buildParams()
      const data = await manejoStore.getConsumoTerreno(params)
      consumoTerreno.value = data
    } catch (error) {
      console.error('Erro ao carregar consumo por terreno:', error)
    }
  }

  async function loadPrevisaoConsumo() {
    try {
      const data = await manejoStore.getPrevisaoConsumo()
      previsaoConsumo.value = data
    } catch (error) {
      console.error('Erro ao carregar previsão de consumo:', error)
    }
  }

  async function loadTerrenosLiberacao() {
    try {
      const data = await manejoStore.getTerrenosLiberacao(
        diasLiberacao.value.value
      )
      terrenosLiberacao.value = data.liberacoes || []
    } catch (error) {
      console.error('Erro ao carregar terrenos para liberação:', error)
    }
  }

  async function loadResumoEstoque() {
    try {
      const data = await manejoStore.getResumoEstoque()
      resumoEstoque.value = data
    } catch (error) {
      console.error('Erro ao carregar resumo de estoque:', error)
    }
  }

  async function refreshAllReports() {
    $q.loading.show({ message: 'Atualizando relatórios...' })

    try {
      await Promise.all([
        loadConsumoTerreno(),
        loadPrevisaoConsumo(),
        loadTerrenosLiberacao(),
        loadResumoEstoque(),
      ])

      $q.notify({
        type: 'positive',
        message: 'Relatórios atualizados com sucesso!',
      })
    } catch {
      $q.notify({
        type: 'negative',
        message: 'Erro ao atualizar relatórios',
      })
    } finally {
      $q.loading.hide()
    }
  }

  // Filtros e helpers
  function buildParams() {
    const params = {}

    if (filtrosGlobais.value.data_inicio) {
      params.data_inicio = filtrosGlobais.value.data_inicio
    }

    if (filtrosGlobais.value.data_fim) {
      params.data_fim = filtrosGlobais.value.data_fim
    }

    if (filtrosGlobais.value.terrenos?.length > 0) {
      params.terreno_ids = filtrosGlobais.value.terrenos
        .map(t => t.value)
        .join(',')
    }

    return params
  }

  async function onGlobalFilterChange() {
    // Recarregar apenas os relatórios que dependem dos filtros
    await loadConsumoTerreno()
  }

  function getPeriodoAtual() {
    if (filtrosGlobais.value.data_inicio && filtrosGlobais.value.data_fim) {
      return `${formatDate(filtrosGlobais.value.data_inicio)} a ${formatDate(filtrosGlobais.value.data_fim)}`
    }
    if (filtrosGlobais.value.data_inicio) {
      return `A partir de ${formatDate(filtrosGlobais.value.data_inicio)}`
    }
    if (filtrosGlobais.value.data_fim) {
      return `Até ${formatDate(filtrosGlobais.value.data_fim)}`
    }
    return 'Todos os períodos'
  }

  // Visualização completa
  function viewFullReport(type) {
    fullReportType.value = type
    fullReportDialog.value = true
  }

  function getFullReportTitle() {
    const titles = {
      consumo: 'Relatório Completo - Consumo por Terreno',
      previsao: 'Relatório Completo - Previsão de Consumo',
      estoque: 'Relatório Completo - Resumo de Estoque',
    }
    return titles[fullReportType.value] || 'Relatório Completo'
  }

  // Exportação
  // async function exportAllReports() {
  //   try {
  //     $q.loading.show({ message: 'Gerando relatórios...' })

  //     // Simular geração de relatório
  //     await new Promise(resolve => setTimeout(resolve, 2000))

  //     $q.notify({
  //       type: 'positive',
  //       message: 'Relatório completo gerado com sucesso!',
  //       actions: [
  //         {
  //           label: 'Download',
  //           color: 'white',
  //           handler: () => {
  //             // Implementar download real
  //             console.log('Iniciando download do relatório completo')
  //           }
  //         }
  //       ]
  //     })
  //   } catch {
  //     $q.notify({
  //       type: 'negative',
  //       message: 'Erro ao gerar relatório'
  //     })
  //   } finally {
  //     $q.loading.hide()
  //   }
  // }

  async function exportConsumoTerreno() {
    await exportReport('consumo-terreno', consumoTerreno.value)
  }

  async function exportPrevisaoConsumo() {
    await exportReport('previsao-consumo', previsaoConsumo.value)
  }

  async function exportTerrenosLiberacao() {
    await exportReport('terrenos-liberacao', terrenosLiberacao.value)
  }

  async function exportResumoEstoque() {
    await exportReport('resumo-estoque', resumoEstoque.value)
  }

  async function exportFullReport() {
    let data = []
    let filename = ''

    switch (fullReportType.value) {
      case 'consumo':
        data = consumoTerreno.value
        filename = 'consumo-terreno-completo'
        break
      case 'previsao':
        data = previsaoConsumo.value
        filename = 'previsao-consumo-completo'
        break
      case 'estoque':
        data = resumoEstoque.value
        filename = 'resumo-estoque-completo'
        break
    }

    await exportReport(filename, data)
  }

  async function exportReport(type, data) {
    if (!data || data.length === 0) {
      $q.notify({
        type: 'warning',
        message: 'Nenhum dado disponível para exportar',
      })
      return
    }

    try {
      // Converter para CSV
      const csv = convertToCSV(data)

      // Criar e fazer download do arquivo
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)

      link.setAttribute('href', url)
      link.setAttribute(
        'download',
        `${type}_${new Date().toISOString().split('T')[0]}.csv`
      )
      link.style.visibility = 'hidden'

      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      $q.notify({
        type: 'positive',
        message: `Relatório ${type} exportado com sucesso!`,
      })
    } catch {
      $q.notify({
        type: 'negative',
        message: 'Erro ao exportar relatório',
      })
    }
  }

  function convertToCSV(data) {
    if (!data || data.length === 0) return ''

    const headers = Object.keys(data[0])
    const csvHeaders = headers.join(',')

    const csvRows = data.map(row => {
      return headers
        .map(header => {
          const value = row[header]
          if (value === null || value === undefined) return ''
          if (typeof value === 'string' && value.includes(',')) {
            return `"${value}"`
          }
          return value
        })
        .join(',')
    })

    return [csvHeaders, ...csvRows].join('\n')
  }

  // Helpers de exibição
  function getCorRecomendacao(recomendacao) {
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

  function getCorDiasLiberacao(dias) {
    if (dias <= 3) return 'red'
    if (dias <= 7) return 'orange'
    if (dias <= 15) return 'blue'
    return 'green'
  }

  function getPercentualEstoque(item) {
    if (!item.estoque_minimo || item.estoque_minimo === 0) return 1
    return Math.min((item.estoque_atual || 0) / (item.estoque_minimo * 2), 1)
  }

  function getCorEstoque(item) {
    const atual = item.estoque_atual || 0
    const minimo = item.estoque_minimo || 0

    if (atual === 0) return 'red'
    if (atual <= minimo) return 'orange'
    if (atual <= minimo * 1.5) return 'blue'
    return 'green'
  }

  function formatarData(data) {
    if (!data) return '-'
    return new Date(data).toLocaleDateString('pt-BR')
  }

  // Carregamento inicial
  async function loadOptions() {
    try {
      await terrenoStore.fetchTerrenos({ limit: 100 })
      terrenoOptions.value = terrenoStore.terrenos.map(t => ({
        value: t.ID,
        label: t.NOME,
      }))
    } catch (error) {
      console.error('Erro ao carregar opções:', error)
    }
  }

  // Lifecycle
  onMounted(async () => {
    await loadOptions()

    // Definir período padrão (últimos 30 dias)
    const hoje = new Date()
    const trintaDiasAtras = new Date()
    trintaDiasAtras.setDate(hoje.getDate() - 30)

    filtrosGlobais.value.data_inicio = trintaDiasAtras
      .toISOString()
      .split('T')[0]
    filtrosGlobais.value.data_fim = hoje.toISOString().split('T')[0]

    // Carregar relatórios iniciais
    await refreshAllReports()
  })
</script>

<style scoped>
  @import 'src/css/components/relatoriosmanejo.css';
</style>
