<template>
  <div>
    <!-- Filtros para Relatório -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6 q-mb-md">Gerar Relatório</div>
        <q-form @submit="gerarRelatorio">
          <div class="row q-gutter-md">
            <calendario-component
              v-model="filtrosRelatorio.data_inicio"
              label="Data Início *"
              :rules="[val => !!val || 'Data início é obrigatória']"
              class="col-md-4 col-12"
            />
            <calendario-component
              v-model="filtrosRelatorio.data_fim"
              label="Data Fim *"
              :rules="[val => !!val || 'Data fim é obrigatória']"
              class="col-md-4 col-12"
            />
            <q-select
              v-model="filtrosRelatorio.tipo_registro"
              :options="ferrageamentoStore.tiposFerrageamento"
              label="Tipo (opcional)"
              emit-value
              map-options
              clearable
              class="col-md-3 col-12"
            />
          </div>

          <div class="text-right q-mt-md">
            <q-btn 
              type="submit" 
              color="primary" 
              :loading="loadingRelatorio"
              icon="assessment"
              label="Gerar Relatório"
            />
          </div>
        </q-form>
      </q-card-section>
    </q-card>

    <!-- Relatório Gerado -->
    <q-card v-if="relatorio" class="q-mb-md">
      <q-card-section>
        <div class="text-h6">Relatório de Ferrageamento</div>
        <div class="text-caption">
          Período: {{ formatDate(relatorio.periodo_inicio) }} a {{ formatDate(relatorio.periodo_fim) }}
        </div>
      </q-card-section>
      
      <q-card-section>
        <!-- Resumo Estatístico -->
        <div class="row q-gutter-md q-mb-md">
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-primary">{{ relatorio.total_registros }}</div>
              <div class="text-caption">Total de Registros</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-secondary">{{ relatorio.animais_atendidos }}</div>
              <div class="text-caption">Animais Atendidos</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-green">R$ {{ relatorio.custo_total.toFixed(2) }}</div>
              <div class="text-caption">Custo Total</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-orange">R$ {{ relatorio.custo_medio.toFixed(2) }}</div>
              <div class="text-caption">Custo Médio</div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Distribuição por Tipo -->
        <div class="row q-gutter-md q-mb-md">
          <q-card class="col-6">
            <q-card-section>
              <div class="text-h6">Distribuição por Tipo</div>
              <q-table
                :rows="relatorio.por_tipo"
                :columns="tipoColumns"
                dense
                flat
                hide-pagination
                :pagination="{ rowsPerPage: 0 }"
              >
                <template v-slot:body-cell-porcentagem="props">
                  <q-td :props="props">
                    <q-linear-progress 
                      :value="props.row.porcentagem / 100"
                      color="primary"
                      size="20px"
                      class="q-mt-sm"
                    >
                      <div class="absolute-full flex flex-center">
                        <q-badge color="white" text-color="primary" :label="`${props.row.porcentagem}%`" />
                      </div>
                    </q-linear-progress>
                  </q-td>
                </template>
              </q-table>
            </q-card-section>
          </q-card>

          <q-card class="col-6">
            <q-card-section>
              <div class="text-h6">Top 5 Ferradores</div>
              <q-table
                :rows="relatorio.top_ferradores"
                :columns="ferradoresColumns"
                dense
                flat
                hide-pagination
                :pagination="{ rowsPerPage: 0 }"
              >
                <template v-slot:body-cell-custo_total="props">
                  <q-td :props="props">
                    R$ {{ props.row.custo_total.toFixed(2) }}
                  </q-td>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
        </div>

        <!-- Alertas e Vencimentos -->
        <q-card>
          <q-card-section>
            <div class="text-h6">Alertas e Próximos Vencimentos</div>
            <q-table
              :rows="relatorio.alertas"
              :columns="alertasColumns"
              dense
              flat
              :pagination="{ rowsPerPage: 10 }"
            >
              <template v-slot:body-cell-PROXIMA_AVALIACAO="props">
                <q-td :props="props">
                  {{ formatDate(props.row.PROXIMA_AVALIACAO) }}
                </q-td>
              </template>

              <template v-slot:body-cell-status="props">
                <q-td :props="props">
                  <q-chip
                    :color="getStatusVencimentoColor(props.row.status)"
                    text-color="white"
                    size="sm"
                  >
                    {{ getStatusVencimentoLabel(props.row.status) }}
                  </q-chip>
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn 
          flat 
          icon="file_download" 
          label="Exportar PDF" 
          @click="exportarPDF"
        />
        <q-btn 
          flat 
          icon="table_view" 
          label="Exportar Excel" 
          @click="exportarExcel"
        />
      </q-card-actions>
    </q-card>

    <!-- Estado Vazio -->
    <div v-else class="text-center q-pa-xl">
      <q-icon name="assessment" size="4rem" color="grey" />
      <div class="text-h6 text-grey q-mt-md">
        Configure os filtros e gere um relatório
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useFerrageamentoStore } from 'stores/ferrageamento'
import { ErrorHandler } from 'src/utils/errorHandler'
import { formatDate } from 'src/utils/dateUtils'
import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

// Store
const ferrageamentoStore = useFerrageamentoStore()

// Estado reativo
const loadingRelatorio = ref(false)
const relatorio = ref(null)

// Filtros
const filtrosRelatorio = ref({
  data_inicio: '',
  data_fim: '',
  tipo_registro: null
})

// Colunas das tabelas
const tipoColumns = [
  { name: 'tipo', label: 'Tipo', field: 'tipo', align: 'left' },
  { name: 'quantidade', label: 'Quantidade', field: 'quantidade', align: 'center' },
  { name: 'porcentagem', label: 'Porcentagem', field: 'porcentagem', align: 'center' }
]

const ferradoresColumns = [
  { name: 'ferrador', label: 'Ferrador', field: 'ferrador', align: 'left' },
  { name: 'total_servicos', label: 'Serviços', field: 'total_servicos', align: 'center' },
  { name: 'custo_total', label: 'Faturamento', field: 'custo_total', align: 'right' }
]

const alertasColumns = [
  { name: 'animal_nome', label: 'Animal', field: 'animal_nome', align: 'left' },
  { name: 'PROXIMA_AVALIACAO', label: 'Próxima Avaliação', field: 'PROXIMA_AVALIACAO', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'center' }
]

// Métodos
async function gerarRelatorio() {
  try {
    loadingRelatorio.value = true
    
    const params = {
      data_inicio: filtrosRelatorio.value.data_inicio,
      data_fim: filtrosRelatorio.value.data_fim,
      tipo_registro: filtrosRelatorio.value.tipo_registro
    }
    
    relatorio.value = await ferrageamentoStore.gerarRelatorio(params)
    ErrorHandler.success('Relatório gerado com sucesso!')
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao gerar relatório')
  } finally {
    loadingRelatorio.value = false
  }
}

function getStatusVencimentoColor(status) {
  const colors = {
    'EM_DIA': 'positive',
    'PROXIMO_VENCIMENTO': 'warning',
    'VENCIDO': 'negative'
  }
  return colors[status] || 'grey'
}

function getStatusVencimentoLabel(status) {
  const labels = {
    'EM_DIA': 'Em dia',
    'PROXIMO_VENCIMENTO': 'Próximo vencimento',
    'VENCIDO': 'Vencido'
  }
  return labels[status] || status
}

async function exportarPDF() {
  try {
    await ferrageamentoStore.exportarRelatorioPDF(filtrosRelatorio.value)
    ErrorHandler.success('PDF exportado com sucesso!')
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao exportar PDF')
  }
}

async function exportarExcel() {
  try {
    await ferrageamentoStore.exportarRelatorioExcel(filtrosRelatorio.value)
    ErrorHandler.success('Excel exportado com sucesso!')
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao exportar Excel')
  }
}

// Expor métodos
defineExpose({
  gerarRelatorio
})
</script>