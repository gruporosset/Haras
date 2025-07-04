<template>
  <div
    id="alertas-section"
    class="row q-gutter-md"
  >
    <!-- Alertas de Saúde -->
    <div class="col-12 col-md-6">
      <q-card>
        <q-card-section>
          <div class="row items-center">
            <div class="col">
              <div class="text-h6">
                <q-icon
                  name="health_and_safety"
                  class="q-mr-sm"
                />
                Alertas de Saúde
              </div>
            </div>
            <div class="col-auto">
              <q-badge
                v-if="alertasSaude.length > 0"
                :color="temAlertasAlta ? 'negative' : 'warning'"
                :label="alertasSaude.length"
              />
            </div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section
          v-if="alertasSaude.length === 0"
          class="text-center text-grey"
        >
          <q-icon
            name="check_circle"
            size="48px"
            color="positive"
          />
          <div class="q-mt-sm">Nenhum alerta de saúde</div>
        </q-card-section>

        <q-list v-else>
          <q-item
            v-for="alerta in alertasSaude.slice(0, 5)"
            :key="`saude-${alerta.animal_id}-${alerta.tipo_alerta}`"
            clickable
            @click="verAnimal(alerta.animal_id)"
          >
            <q-item-section avatar>
              <q-avatar
                :color="dashboardStore.getPrioridadeColor(alerta.prioridade)"
                text-color="white"
              >
                <q-icon
                  :name="dashboardStore.getIconeAlerta(alerta.tipo_alerta)"
                />
              </q-avatar>
            </q-item-section>

            <q-item-section>
              <q-item-label>{{ alerta.animal_nome }}</q-item-label>
              <q-item-label caption>{{ alerta.descricao }}</q-item-label>
              <q-item-label caption>
                <span
                  v-if="alerta.dias_atraso > 0"
                  class="text-negative"
                >
                  {{ alerta.dias_atraso }} dia(s) de atraso
                </span>
                <span
                  v-else
                  class="text-warning"
                >
                  Vence em {{ Math.abs(alerta.dias_atraso) }} dia(s)
                </span>
              </q-item-label>
            </q-item-section>

            <q-item-section side>
              <q-chip
                :color="dashboardStore.getPrioridadeColor(alerta.prioridade)"
                text-color="white"
                size="sm"
              >
                {{ alerta.prioridade }}
              </q-chip>
            </q-item-section>
          </q-item>

          <q-item v-if="alertasSaude.length > 5">
            <q-item-section class="text-center">
              <q-btn
                flat
                color="primary"
                :label="`Ver todos (${alertasSaude.length})`"
                @click="$router.push('/saude')"
              />
            </q-item-section>
          </q-item>
        </q-list>
      </q-card>
    </div>

    <!-- Alertas de Estoque -->
    <div class="col-12 col-md-6">
      <q-card>
        <q-card-section>
          <div class="row items-center">
            <div class="col">
              <div class="text-h6">
                <q-icon
                  name="inventory_2"
                  class="q-mr-sm"
                />
                Alertas de Estoque
              </div>
            </div>
            <div class="col-auto">
              <q-badge
                v-if="alertasEstoque.length > 0"
                :color="temEstoqueCritico ? 'negative' : 'warning'"
                :label="alertasEstoque.length"
              />
            </div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section
          v-if="alertasEstoque.length === 0"
          class="text-center text-grey"
        >
          <q-icon
            name="check_circle"
            size="48px"
            color="positive"
          />
          <div class="q-mt-sm">Estoque em dia</div>
        </q-card-section>

        <q-list v-else>
          <q-item
            v-for="alerta in alertasEstoque.slice(0, 5)"
            :key="`estoque-${alerta.produto_id}-${alerta.tipo_produto}`"
            clickable
            @click="verProduto(alerta)"
          >
            <q-item-section avatar>
              <q-avatar
                :color="dashboardStore.getStatusEstoqueColor(alerta.status)"
                text-color="white"
              >
                <q-icon :name="getIconeProduto(alerta.tipo_produto)" />
              </q-avatar>
            </q-item-section>

            <q-item-section>
              <q-item-label>{{ alerta.produto_nome }}</q-item-label>
              <q-item-label caption>
                {{ dashboardStore.getTipoEstoqueLabel(alerta.tipo_produto) }}
              </q-item-label>
              <q-item-label caption>
                Atual: {{ alerta.estoque_atual }} {{ alerta.unidade_medida }} |
                Mínimo: {{ alerta.estoque_minimo }} {{ alerta.unidade_medida }}
              </q-item-label>
              <q-item-label
                v-if="alerta.dias_vencimento"
                caption
                class="text-orange"
              >
                Vence em {{ alerta.dias_vencimento }} dias
              </q-item-label>
            </q-item-section>

            <q-item-section side>
              <q-chip
                :color="dashboardStore.getStatusEstoqueColor(alerta.status)"
                text-color="white"
                size="sm"
              >
                {{ alerta.status }}
              </q-chip>
            </q-item-section>
          </q-item>

          <q-item v-if="alertasEstoque.length > 5">
            <q-item-section class="text-center">
              <q-btn
                flat
                color="primary"
                :label="`Ver todos (${alertasEstoque.length})`"
                @click="verTodosEstoque"
              />
            </q-item-section>
          </q-item>
        </q-list>
      </q-card>
    </div>
  </div>
</template>

<script>
  import { computed } from 'vue'
  import { useDashboardStore } from 'src/stores/dashboard'
  import { useRouter } from 'vue-router'

  export default {
    name: 'AlertasDashboard',

    setup() {
      const dashboardStore = useDashboardStore()
      const router = useRouter()

      const alertasSaude = computed(() => dashboardStore.alertas_saude)
      const alertasEstoque = computed(() => dashboardStore.alertas_estoque)

      const temAlertasAlta = computed(() =>
        alertasSaude.value.some(a => a.prioridade === 'ALTA')
      )

      const temEstoqueCritico = computed(() =>
        alertasEstoque.value.some(a => a.status === 'CRITICO')
      )

      const verAnimal = animalId => {
        // Navegar para a página do animal específico ou saúde com filtro
        router.push(`/saude?animal=${animalId}`)
      }

      const verProduto = alerta => {
        // Navegar para a página do produto baseado no tipo
        const rotas = {
          MEDICAMENTO: '/medicamentos',
          RACAO: '/racao',
          MANEJO: '/manejo',
        }

        const rota = rotas[alerta.tipo_produto] || '/medicamentos'
        router.push(`${rota}?produto=${alerta.produto_id}`)
      }

      const verTodosEstoque = () => {
        // Mostrar modal ou navegar para página de estoque geral
        router.push('/medicamentos?estoque_baixo=true')
      }

      const getIconeProduto = tipo => {
        const icones = {
          MEDICAMENTO: 'medication',
          RACAO: 'restaurant',
          MANEJO: 'eco',
        }
        return icones[tipo] || 'inventory_2'
      }

      return {
        dashboardStore,
        alertasSaude,
        alertasEstoque,
        temAlertasAlta,
        temEstoqueCritico,
        verAnimal,
        verProduto,
        verTodosEstoque,
        getIconeProduto,
      }
    },
  }
</script>

<style scoped>
  .q-item {
    transition: background-color 0.2s;
  }

  .q-item:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }
</style>
