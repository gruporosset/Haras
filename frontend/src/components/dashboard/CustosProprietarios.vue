<template>
  <q-card>
    <q-card-section>
      <div class="row items-center">
        <div class="col">
          <div class="text-h6">
            <q-icon
              name="attach_money"
              class="q-mr-sm"
            />
            Custos por Proprietário
          </div>
          <div class="text-caption text-grey q-mt-xs">{{ periodoAtual }}</div>
        </div>
        <div class="col-auto">
          <q-btn
            flat
            round
            icon="refresh"
            @click="refreshData"
            :loading="dashboardStore.loading"
          />
        </div>
      </div>
    </q-card-section>

    <q-separator />

    <q-card-section
      v-if="custosProprietarios.length === 0"
      class="text-center text-grey"
    >
      <q-icon
        name="money_off"
        size="48px"
      />
      <div class="q-mt-sm">Nenhum custo registrado no período</div>
    </q-card-section>

    <q-table
      v-else
      :rows="custosProprietarios"
      :columns="columns"
      :loading="dashboardStore.loading"
      flat
      hide-pagination
      :rows-per-page-options="[0]"
      class="dashboard-table"
    >
      <!-- Slot customizado para proprietário -->
      <template v-slot:body-cell-proprietario="props">
        <q-td :props="props">
          <div class="row items-center">
            <q-avatar
              size="32px"
              color="primary"
              text-color="white"
              class="q-mr-sm"
            >
              {{ getIniciais(props.value) }}
            </q-avatar>
            <div>
              <div class="text-weight-medium">{{ props.value }}</div>
              <div class="text-caption text-grey">
                {{ props.row.numero_animais }}
                {{ props.row.numero_animais === 1 ? 'animal' : 'animais' }}
              </div>
            </div>
          </div>
        </q-td>
      </template>

      <!-- Slot para medicamentos -->
      <template v-slot:body-cell-medicamentos="props">
        <q-td :props="props">
          <div class="text-weight-medium text-blue">
            {{ formatarMoeda(props.value) }}
          </div>
        </q-td>
      </template>

      <!-- Slot para ração -->
      <template v-slot:body-cell-racao="props">
        <q-td :props="props">
          <div class="text-weight-medium text-green">
            {{ formatarMoeda(props.value) }}
          </div>
        </q-td>
      </template>

      <!-- Slot para manejo -->
      <template v-slot:body-cell-manejo="props">
        <q-td :props="props">
          <div class="text-weight-medium text-orange">
            {{ formatarMoeda(props.value) }}
          </div>
        </q-td>
      </template>

      <!-- Slot para total -->
      <template v-slot:body-cell-total="props">
        <q-td :props="props">
          <div class="text-weight-bold text-primary text-h6">
            {{ formatarMoeda(props.value) }}
          </div>
        </q-td>
      </template>

      <!-- Slot para custo por animal -->
      <template v-slot:body-cell-custo_animal="props">
        <q-td :props="props">
          <q-chip
            :color="getCustoAnimalColor(props.value)"
            text-color="white"
            size="sm"
          >
            {{ formatarMoeda(props.value) }}
          </q-chip>
        </q-td>
      </template>

      <!-- Slot para ações -->
      <template v-slot:body-cell-acoes="props">
        <q-td :props="props">
          <q-btn
            flat
            round
            icon="visibility"
            size="sm"
            @click="verDetalhes(props.row)"
          >
            <q-tooltip>Ver detalhes</q-tooltip>
          </q-btn>
          <q-btn
            flat
            round
            icon="print"
            size="sm"
            @click="gerarRelatorio(props.row)"
          >
            <q-tooltip>Gerar relatório</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </q-table>

    <!-- Resumo do rodapé -->
    <q-separator />
    <q-card-section class="bg-grey-1">
      <div class="row q-gutter-md text-center">
        <div class="col">
          <div class="text-h6 text-primary">
            {{ formatarMoeda(totalGeral) }}
          </div>
          <div class="text-caption">Total Geral</div>
        </div>
        <div class="col">
          <div class="text-h6 text-grey">{{ totalAnimais }}</div>
          <div class="text-caption">Total Animais</div>
        </div>
        <div class="col">
          <div class="text-h6 text-orange">
            {{ formatarMoeda(mediaPorAnimal) }}
          </div>
          <div class="text-caption">Média/Animal</div>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script>
  import { computed } from 'vue'
  import { useDashboardStore } from 'src/stores/dashboard'
  import { useQuasar } from 'quasar'

  export default {
    name: 'CustosProprietarios',

    setup() {
      const dashboardStore = useDashboardStore()
      const $q = useQuasar()

      const custosProprietarios = computed(
        () => dashboardStore.custos_proprietarios
      )

      const columns = [
        {
          name: 'proprietario',
          label: 'Proprietário',
          field: 'proprietario',
          align: 'left',
          sortable: true,
        },
        {
          name: 'medicamentos',
          label: 'Medicamentos',
          field: 'total_medicamentos',
          align: 'right',
          sortable: true,
        },
        {
          name: 'racao',
          label: 'Ração',
          field: 'total_racao',
          align: 'right',
          sortable: true,
        },
        {
          name: 'manejo',
          label: 'Manejo',
          field: 'total_manejo',
          align: 'right',
          sortable: true,
        },
        {
          name: 'total',
          label: 'Total',
          field: 'total_geral',
          align: 'right',
          sortable: true,
        },
        {
          name: 'custo_animal',
          label: 'Custo/Animal',
          field: 'custo_por_animal',
          align: 'center',
          sortable: true,
        },
        {
          name: 'acoes',
          label: 'Ações',
          field: 'acoes',
          align: 'center',
        },
      ]

      const periodoAtual = computed(() => {
        if (custosProprietarios.value.length > 0) {
          return custosProprietarios.value[0].periodo
        }
        return 'Últimos 30 dias'
      })

      const totalGeral = computed(() => {
        return custosProprietarios.value.reduce(
          (total, item) => total + item.total_geral,
          0
        )
      })

      const totalAnimais = computed(() => {
        return custosProprietarios.value.reduce(
          (total, item) => total + item.numero_animais,
          0
        )
      })

      const mediaPorAnimal = computed(() => {
        return totalAnimais.value > 0
          ? totalGeral.value / totalAnimais.value
          : 0
      })

      const getIniciais = nome => {
        if (!nome) return '?'
        return nome
          .split(' ')
          .map(n => n.charAt(0))
          .join('')
          .substring(0, 2)
          .toUpperCase()
      }

      const formatarMoeda = valor => {
        return dashboardStore.formatarMoeda(valor)
      }

      const getCustoAnimalColor = valor => {
        if (valor > 500) return 'negative'
        if (valor > 300) return 'warning'
        if (valor > 100) return 'info'
        return 'positive'
      }

      const refreshData = async () => {
        try {
          await dashboardStore.refreshDashboard()
          $q.notify({
            type: 'positive',
            message: 'Dados atualizados com sucesso!',
          })
        } catch (error) {
          $q.notify({
            type: 'negative',
            message: 'Erro ao atualizar dados: ' + error,
          })
        }
      }

      const verDetalhes = proprietario => {
        // Implementar modal ou navegação para detalhes
        $q.dialog({
          title: 'Detalhes do Proprietário',
          message: `Detalhes de custos para: ${proprietario.proprietario}`,
          ok: 'Fechar',
        })
      }

      const gerarRelatorio = proprietario => {
        // Implementar geração de relatório
        $q.notify({
          type: 'info',
          message: `Gerando relatório para ${proprietario.proprietario}...`,
        })
      }

      return {
        dashboardStore,
        custosProprietarios,
        columns,
        periodoAtual,
        totalGeral,
        totalAnimais,
        mediaPorAnimal,
        getIniciais,
        formatarMoeda,
        getCustoAnimalColor,
        refreshData,
        verDetalhes,
        gerarRelatorio,
      }
    },
  }
</script>

<style scoped>
  .dashboard-table {
    max-height: 400px;
  }

  .dashboard-table .q-table__middle {
    max-height: 400px;
  }

  .q-table tbody td {
    border-bottom: 1px solid #e0e0e0;
  }

  .q-table tbody tr:hover {
    background-color: rgba(0, 0, 0, 0.02);
  }
</style>
