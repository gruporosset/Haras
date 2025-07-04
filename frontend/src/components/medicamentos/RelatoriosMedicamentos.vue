<template>
  <div>
    <!-- Filtros para Relatórios -->
    <q-card
      flat
      bordered
      class="q-pa-md q-mb-md"
    >
      <div class="text-h6 q-mb-md">Filtros para Relatórios</div>

      <div class="row q-gutter-md">
        <div class="col-md-3 col-12">
          <CalendarioComponent
            v-model="filtrosRelatorio.data_inicio"
            label="Data Início"
          />
        </div>

        <div class="col-md-3 col-12">
          <CalendarioComponent
            v-model="filtrosRelatorio.data_fim"
            label="Data Fim"
          />
        </div>

        <div class="col-md-3 col-12">
          <q-select
            v-model="filtrosRelatorio.medicamento_id"
            :options="medicamentoOptions"
            label="Medicamento"
            clearable
            use-input
            @filter="filterMedicamentos"
            option-value="value"
            option-label="label"
            emit-value
            map-options
          />
        </div>

        <div class="col-md-3 col-12">
          <q-btn
            color="primary"
            label="Gerar Relatório"
            icon="assessment"
            @click="gerarRelatorio"
            :loading="loadingRelatorio"
          />
        </div>
      </div>
    </q-card>

    <!-- Relatórios Disponíveis -->
    <div class="row q-gutter-md q-mb-md">
      <div class="col-md-6 col-12">
        <q-card
          flat
          bordered
        >
          <q-card-section>
            <div class="text-h6">Consumo por Medicamento</div>
            <div class="text-caption text-grey">
              Análise de consumo e aplicações
            </div>
          </q-card-section>
          <q-card-actions>
            <q-btn
              flat
              color="primary"
              label="Gerar"
              icon="trending_down"
              @click="gerarRelatorioConsumo"
              :loading="loadingConsumo"
            />
            <q-btn
              flat
              color="secondary"
              label="Exportar PDF"
              icon="picture_as_pdf"
              @click="exportarConsumo('pdf')"
              :disable="!relatorio"
            />
            <q-btn
              flat
              color="accent"
              label="Exportar Excel"
              icon="table_chart"
              @click="exportarConsumo('excel')"
              :disable="!relatorio"
            />
          </q-card-actions>
        </q-card>
      </div>

      <div class="col-md-6 col-12">
        <q-card
          flat
          bordered
        >
          <q-card-section>
            <div class="text-h6">Previsão de Estoque</div>
            <div class="text-caption text-grey">
              Projeção baseada no consumo médio
            </div>
          </q-card-section>
          <q-card-actions>
            <q-btn
              flat
              color="primary"
              label="Gerar"
              icon="trending_up"
              @click="gerarPrevisaoEstoque"
              :loading="loadingPrevisao"
            />
            <q-btn
              flat
              color="secondary"
              label="Exportar PDF"
              icon="picture_as_pdf"
              @click="exportarPrevisao('pdf')"
              :disable="!relatorio"
            />
            <q-btn
              flat
              color="accent"
              label="Exportar Excel"
              icon="table_chart"
              @click="exportarPrevisao('excel')"
              :disable="!relatorio"
            />
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <!-- Resultados dos Relatórios -->
    <div v-if="relatorio">
      <q-tabs
        v-model="activeReportTab"
        class="q-mb-md"
      >
        <q-tab
          name="consumo"
          label="Consumo"
        />
        <q-tab
          name="previsao"
          label="Previsão"
        />
        <q-tab
          name="movimentacoes"
          label="Movimentações"
        />
        <q-tab
          name="graficos"
          label="Gráficos"
        />
      </q-tabs>

      <q-tab-panels
        v-model="activeReportTab"
        animated
      >
        <!-- Relatório de Consumo -->
        <q-tab-panel name="consumo">
          <q-card
            flat
            bordered
          >
            <q-card-section>
              <div class="text-h6 q-mb-md">Consumo por Medicamento</div>

              <q-table
                :rows="relatorio.consumoPorMedicamento || []"
                :columns="consumoColumns"
                flat
                :pagination="{ rowsPerPage: 0 }"
              >
                <template v-slot:body-cell-total_aplicado="props">
                  <q-td :props="props">
                    <div class="text-right">
                      {{ props.row.total_aplicado }}
                      {{ props.row.unidade_medida }}
                    </div>
                  </q-td>
                </template>

                <template v-slot:body-cell-custo_total="props">
                  <q-td :props="props">
                    <div class="text-right">
                      R$ {{ (props.row.custo_total || 0).toFixed(2) }}
                    </div>
                  </q-td>
                </template>

                <template v-slot:body-cell-media_mensal="props">
                  <q-td :props="props">
                    <div class="text-right">
                      {{ (props.row.media_mensal || 0).toFixed(2) }}
                      {{ props.row.unidade_medida }}
                    </div>
                  </q-td>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
        </q-tab-panel>

        <!-- Previsão de Estoque -->
        <q-tab-panel name="previsao">
          <q-card
            flat
            bordered
          >
            <q-card-section>
              <div class="text-h6 q-mb-md">Previsão de Estoque</div>

              <q-table
                :rows="relatorio.previsaoEstoque || []"
                :columns="previsaoColumns"
                flat
                :pagination="{ rowsPerPage: 0 }"
              >
                <template v-slot:body-cell-estoque_atual="props">
                  <q-td :props="props">
                    <div class="text-right">
                      {{ props.row.estoque_atual }}
                      {{ props.row.unidade_medida }}
                    </div>
                  </q-td>
                </template>

                <template v-slot:body-cell-consumo_mensal_medio="props">
                  <q-td :props="props">
                    <div class="text-right">
                      {{ (props.row.consumo_mensal_medio || 0).toFixed(2) }}
                      {{ props.row.unidade_medida }}
                    </div>
                  </q-td>
                </template>

                <template v-slot:body-cell-dias_restantes="props">
                  <q-td :props="props">
                    <div class="text-center">
                      <q-chip
                        :color="getDiasRestantesColor(props.row.dias_restantes)"
                        text-color="white"
                        dense
                      >
                        {{ props.row.dias_restantes }} dias
                      </q-chip>
                    </div>
                  </q-td>
                </template>

                <template v-slot:body-cell-recomendacao="props">
                  <q-td :props="props">
                    <q-chip
                      :color="getRecomendacaoColor(props.row.recomendacao)"
                      text-color="white"
                      dense
                    >
                      {{ getRecomendacaoLabel(props.row.recomendacao) }}
                    </q-chip>
                  </q-td>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
        </q-tab-panel>

        <!-- Movimentações Detalhadas -->
        <q-tab-panel name="movimentacoes">
          <q-card
            flat
            bordered
          >
            <q-card-section>
              <div class="text-h6 q-mb-md">Movimentações Detalhadas</div>

              <q-table
                :rows="relatorio.movimentacoesDetalhadas || []"
                :columns="movimentacaoColumns"
                flat
                :pagination="{ rowsPerPage: 10 }"
              >
                <template v-slot:body-cell-tipo="props">
                  <q-td :props="props">
                    <q-chip
                      :color="
                        getTipoMovimentacaoColor(props.row.TIPO_MOVIMENTACAO)
                      "
                      text-color="white"
                      dense
                    >
                      {{ props.row.TIPO_MOVIMENTACAO }}
                    </q-chip>
                  </q-td>
                </template>

                <template v-slot:body-cell-quantidade="props">
                  <q-td :props="props">
                    <div class="text-right">
                      {{ props.row.QUANTIDADE }} {{ props.row.unidade_medida }}
                    </div>
                  </q-td>
                </template>

                <template v-slot:body-cell-valor_total="props">
                  <q-td :props="props">
                    <div class="text-right">
                      R$
                      {{
                        (
                          (props.row.QUANTIDADE || 0) *
                          (props.row.PRECO_UNITARIO || 0)
                        ).toFixed(2)
                      }}
                    </div>
                  </q-td>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
        </q-tab-panel>

        <!-- Gráficos -->
        <q-tab-panel name="graficos">
          <div class="row q-gutter-md">
            <div class="col-md-6 col-12">
              <q-card
                flat
                bordered
              >
                <q-card-section>
                  <div class="text-h6 q-mb-md">Consumo Mensal</div>
                  <canvas
                    ref="consumoChart"
                    style="max-height: 300px"
                  ></canvas>
                </q-card-section>
              </q-card>
            </div>

            <div class="col-md-6 col-12">
              <q-card
                flat
                bordered
              >
                <q-card-section>
                  <div class="text-h6 q-mb-md">Distribuição por Tipo</div>
                  <canvas
                    ref="tiposChart"
                    style="max-height: 300px"
                  ></canvas>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-tab-panel>
      </q-tab-panels>
    </div>

    <!-- Estado Vazio -->
    <div
      v-else
      class="text-center q-pa-xl"
    >
      <q-icon
        name="assessment"
        size="4rem"
        color="grey"
      />
      <div class="text-h6 q-mt-md text-grey">Nenhum relatório gerado</div>
      <div class="text-caption text-grey">
        Configure os filtros e gere um relatório
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, onMounted, nextTick } from 'vue'
  import { useMedicamentoStore } from 'stores/medicamento'
  import { ErrorHandler } from 'src/utils/errorHandler'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'
  import Chart from 'chart.js/auto'

  // Store
  const medicamentoStore = useMedicamentoStore()

  // Estado reativo
  const loadingRelatorio = ref(false)
  const loadingConsumo = ref(false)
  const loadingPrevisao = ref(false)
  const relatorio = ref(null)
  const activeReportTab = ref('consumo')

  // Refs dos gráficos
  const consumoChart = ref(null)
  const tiposChart = ref(null)

  // Opções
  const medicamentoOptions = ref([])

  // Filtros
  const filtrosRelatorio = ref({
    data_inicio: '',
    data_fim: '',
    medicamento_id: null,
  })

  // Colunas das tabelas
  const consumoColumns = [
    {
      name: 'medicamento_nome',
      label: 'Medicamento',
      field: 'medicamento_nome',
      align: 'left',
    },
    {
      name: 'forma_farmaceutica',
      label: 'Forma',
      field: 'forma_farmaceutica',
      align: 'center',
    },
    {
      name: 'total_aplicado',
      label: 'Total Aplicado',
      field: 'total_aplicado',
      align: 'right',
    },
    {
      name: 'numero_aplicacoes',
      label: 'Nº Aplicações',
      field: 'numero_aplicacoes',
      align: 'center',
    },
    {
      name: 'custo_total',
      label: 'Custo Total',
      field: 'custo_total',
      align: 'right',
    },
    {
      name: 'media_mensal',
      label: 'Média Mensal',
      field: 'media_mensal',
      align: 'right',
    },
  ]

  const previsaoColumns = [
    {
      name: 'medicamento_nome',
      label: 'Medicamento',
      field: 'medicamento_nome',
      align: 'left',
    },
    {
      name: 'estoque_atual',
      label: 'Estoque Atual',
      field: 'estoque_atual',
      align: 'right',
    },
    {
      name: 'consumo_mensal_medio',
      label: 'Consumo Mensal',
      field: 'consumo_mensal_medio',
      align: 'right',
    },
    {
      name: 'dias_restantes',
      label: 'Dias Restantes',
      field: 'dias_restantes',
      align: 'center',
    },
    {
      name: 'data_prevista_fim',
      label: 'Previsão Fim',
      field: 'data_prevista_fim',
      align: 'left',
    },
    {
      name: 'recomendacao',
      label: 'Recomendação',
      field: 'recomendacao',
      align: 'center',
    },
  ]

  const movimentacaoColumns = [
    {
      name: 'DATA_REGISTRO',
      label: 'Data',
      field: 'DATA_REGISTRO',
      align: 'left',
    },
    {
      name: 'medicamento_nome',
      label: 'Medicamento',
      field: 'medicamento_nome',
      align: 'left',
    },
    {
      name: 'tipo',
      label: 'Tipo',
      field: 'TIPO_MOVIMENTACAO',
      align: 'center',
    },
    {
      name: 'quantidade',
      label: 'Quantidade',
      field: 'QUANTIDADE',
      align: 'right',
    },
    {
      name: 'valor_total',
      label: 'Valor Total',
      field: 'valor_total',
      align: 'right',
    },
    { name: 'MOTIVO', label: 'Motivo', field: 'MOTIVO', align: 'left' },
  ]

  // Métodos
  async function loadMedicamentos() {
    try {
      await medicamentoStore.fetchMedicamentos({ limit: 100 })
      medicamentoOptions.value = medicamentoStore.medicamentos.map(m => ({
        value: m.ID,
        label: m.NOME,
      }))
    } catch (error) {
      console.error('Erro ao carregar medicamentos:', error)
    }
  }

  function filterMedicamentos(val, update) {
    update(() => {
      if (val === '') {
        medicamentoOptions.value = medicamentoStore.medicamentos.map(m => ({
          value: m.ID,
          label: m.NOME,
        }))
      } else {
        const needle = val.toLowerCase()
        const allMedicamentos = medicamentoStore.medicamentos.map(m => ({
          value: m.ID,
          label: m.NOME,
        }))
        medicamentoOptions.value = allMedicamentos.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  async function gerarRelatorio() {
    try {
      loadingRelatorio.value = true

      const params = {
        data_inicio: filtrosRelatorio.value.data_inicio,
        data_fim: filtrosRelatorio.value.data_fim,
        medicamento_id: filtrosRelatorio.value.medicamento_id,
      }

      // Usar métodos disponíveis no store para construir relatório
      const [previsaoConsumo, movimentacoes] = await Promise.all([
        medicamentoStore.fetchPrevisaoConsumo(90),
        medicamentoStore.fetchMovimentacaoPeriodo(
          params.data_inicio,
          params.data_fim
        ),
      ])

      // Montar estrutura do relatório usando dados disponíveis
      relatorio.value = {
        consumoPorMedicamento: calcularConsumoPorMedicamento(movimentacoes),
        previsaoEstoque: previsaoConsumo || [],
        movimentacoesDetalhadas: movimentacoes || [],
        consumoMensal: calcularConsumoMensal(movimentacoes),
        distribuicaoTipos: calcularDistribuicaoTipos(),
      }

      ErrorHandler.success('Relatório gerado com sucesso!')

      // Gerar gráficos após o próximo tick
      await nextTick()
      criarGraficos()
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao gerar relatório')
    } finally {
      loadingRelatorio.value = false
    }
  }

  // Funções auxiliares para processar dados
  function calcularConsumoPorMedicamento(movimentacoes) {
    if (!movimentacoes || !Array.isArray(movimentacoes)) return []

    const medicamentosMap = new Map()

    movimentacoes
      .filter(m => m.TIPO_MOVIMENTACAO === 'SAIDA')
      .forEach(mov => {
        const id = mov.ID_MEDICAMENTO
        if (!medicamentosMap.has(id)) {
          medicamentosMap.set(id, {
            medicamento_nome: mov.medicamento_nome || 'N/A',
            forma_farmaceutica: mov.forma_farmaceutica || 'N/A',
            total_aplicado: 0,
            numero_aplicacoes: 0,
            custo_total: 0,
            unidade_medida: mov.unidade_medida || 'UN',
          })
        }

        const item = medicamentosMap.get(id)
        item.total_aplicado += mov.QUANTIDADE || 0
        item.numero_aplicacoes += 1
        item.custo_total += (mov.QUANTIDADE || 0) * (mov.PRECO_UNITARIO || 0)
      })

    return Array.from(medicamentosMap.values()).map(item => ({
      ...item,
      media_mensal: item.total_aplicado / 3, // Assumindo 3 meses de análise
    }))
  }

  function calcularConsumoMensal(movimentacoes) {
    if (!movimentacoes || !Array.isArray(movimentacoes)) return []

    const mesesMap = new Map()

    movimentacoes
      .filter(m => m.TIPO_MOVIMENTACAO === 'SAIDA')
      .forEach(mov => {
        const data = new Date(mov.DATA_REGISTRO)
        const mesAno = `${data.getFullYear()}-${String(data.getMonth() + 1).padStart(2, '0')}`

        if (!mesesMap.has(mesAno)) {
          mesesMap.set(mesAno, { mes: mesAno, total: 0 })
        }

        mesesMap.get(mesAno).total += mov.QUANTIDADE || 0
      })

    return Array.from(mesesMap.values()).sort((a, b) =>
      a.mes.localeCompare(b.mes)
    )
  }

  function calcularDistribuicaoTipos() {
    const medicamentos = medicamentoStore.medicamentos || []
    const tiposMap = new Map()

    medicamentos.forEach(med => {
      const forma = med.FORMA_FARMACEUTICA || 'N/A'
      if (!tiposMap.has(forma)) {
        tiposMap.set(forma, { forma, total: 0 })
      }
      tiposMap.get(forma).total += 1
    })

    return Array.from(tiposMap.values())
  }

  async function gerarRelatorioConsumo() {
    try {
      loadingConsumo.value = true
      await gerarRelatorio()
      activeReportTab.value = 'consumo'
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao gerar relatório de consumo')
    } finally {
      loadingConsumo.value = false
    }
  }

  async function gerarPrevisaoEstoque() {
    try {
      loadingPrevisao.value = true
      await gerarRelatorio()
      activeReportTab.value = 'previsao'
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao gerar previsão de estoque')
    } finally {
      loadingPrevisao.value = false
    }
  }

  async function exportarConsumo() {
    ErrorHandler.handle(
      'Funcionalidade de exportação ainda não implementada',
      'Em desenvolvimento'
    )
  }

  async function exportarPrevisao() {
    ErrorHandler.handle(
      'Funcionalidade de exportação ainda não implementada',
      'Em desenvolvimento'
    )
  }

  function criarGraficos() {
    if (!relatorio.value) return

    // Gráfico de consumo mensal
    if (consumoChart.value && relatorio.value.consumoMensal) {
      new Chart(consumoChart.value, {
        type: 'bar',
        data: {
          labels: relatorio.value.consumoMensal.map(item => item.mes) || [],
          datasets: [
            {
              label: 'Consumo Mensal',
              data: relatorio.value.consumoMensal.map(item => item.total) || [],
              backgroundColor: 'rgba(54, 162, 235, 0.8)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
        },
      })
    }

    // Gráfico de tipos
    if (tiposChart.value && relatorio.value.distribuicaoTipos) {
      new Chart(tiposChart.value, {
        type: 'doughnut',
        data: {
          labels:
            relatorio.value.distribuicaoTipos.map(item => item.forma) || [],
          datasets: [
            {
              data:
                relatorio.value.distribuicaoTipos.map(item => item.total) || [],
              backgroundColor: [
                'rgba(255, 99, 132, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(255, 206, 86, 0.8)',
                'rgba(75, 192, 192, 0.8)',
              ],
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
        },
      })
    }
  }

  // Funções auxiliares
  function getDiasRestantesColor(dias) {
    if (dias <= 7) return 'negative'
    if (dias <= 30) return 'warning'
    return 'positive'
  }

  function getRecomendacaoColor(recomendacao) {
    const colors = {
      COMPRAR_URGENTE: 'negative',
      COMPRAR: 'warning',
      MONITORAR: 'info',
      OK: 'positive',
    }
    return colors[recomendacao] || 'grey'
  }

  function getRecomendacaoLabel(recomendacao) {
    const labels = {
      COMPRAR_URGENTE: 'Comprar Urgente',
      COMPRAR: 'Comprar',
      MONITORAR: 'Monitorar',
      OK: 'OK',
    }
    return labels[recomendacao] || recomendacao
  }

  function getTipoMovimentacaoColor(tipo) {
    const colors = {
      ENTRADA: 'positive',
      SAIDA: 'warning',
      AJUSTE: 'info',
    }
    return colors[tipo] || 'grey'
  }

  // Lifecycle
  onMounted(() => {
    loadMedicamentos()
  })

  // Expor métodos
  defineExpose({
    gerarRelatorio,
  })
</script>
