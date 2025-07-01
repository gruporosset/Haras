<template>
  <div class="planos-alimentares-container">
    <!-- FILTROS -->
    <q-card flat bordered class="q-mb-md">
      <q-card-section>
        <div class="row q-gutter-md justify-between">
          <q-select
            v-model="filtros.animal_id"
            :options="animalOptions"
            label="Animal"
            clearable
            use-input
            @filter="filterAnimais"
            @update:model-value="onFilterChange"
            class="col-md-3 col-12"
          />

          <q-select
            v-model="filtros.categoria"
            :options="racaoStore.categoriasNutricionais"
            label="Categoria Nutricional"
            clearable
            @update:model-value="onFilterChange"
            class="col-md-3 col-12"
          />

          <q-select
            v-model="filtros.status_plano"
            :options="[
              { value: 'ATIVO', label: 'Ativos' },
              { value: 'INATIVO', label: 'Inativos' },
              { value: 'SUSPENSO', label: 'Suspenso' }
            ]"
            label="Status"
            @update:model-value="onFilterChange"
            class="col-md-2 col-12"
            clearable
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- ESTATÍSTICAS -->
    <div class="row q-gutter-md q-mb-md justify-between">
      <div class="col-md-3 col-6">
        <q-card flat bordered>
          <q-card-section class="text-center q-pa-sm">
            <div class="text-h4 text-primary">{{ estatisticas.totalPlanos }}</div>
            <div class="text-subtitle2">Total</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-md-3 col-6">
        <q-card flat bordered>
          <q-card-section class="text-center q-pa-sm">
            <div class="text-h4 text-green">{{ estatisticas.planosAtivos }}</div>
            <div class="text-subtitle2">Ativos</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-md-3 col-6">
        <q-card flat bordered>
          <q-card-section class="text-center q-pa-sm">
            <div class="text-h4 text-orange">{{ estatisticas.planosSuspensos }}</div>
            <div class="text-subtitle2">Suspensos</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-md-2 col-6">
        <q-card flat bordered>
          <q-card-section class="text-center q-pa-sm">
            <div class="text-h4 text-blue">{{ racaoStore.formatarMoeda(estatisticas.custoMensalEstimado) }}</div>
            <div class="text-subtitle2">Custo Mensal</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- TABELA -->
    <div class="row q-mb-md items-center">
      <q-btn
        color="primary"
        icon="add"
        label="Novo Plano"
        @click="openDialog()"
      />
    </div>

    <q-table
      :rows="racaoStore.planosAlimentares"
      :columns="columns"
      row-key="ID"
      :loading="racaoStore.loading"
      :pagination="racaoStore.pagination"
      @request="onRequest"
      binary-state-sort
      flat
      class="planos-table"
    >
      <template v-slot:body-cell-animal_nome="props">
        <q-td :props="props">
          <div class="text-weight-medium">{{ props.value }}</div>
          <div class="text-caption text-grey-6">{{ props.row.animal_numero_registro }}</div>
        </q-td>
      </template>

      <template v-slot:body-cell-CATEGORIA_NUTRICIONAL="props">
        <q-td :props="props">
          <q-chip
            :color="getCorCategoria(props.value)"
            text-color="white"
            size="sm"
          >
            {{ racaoStore.getCategoriaLabel(props.value) }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-peso_dieta="props">
        <q-td :props="props">
          <div class="text-weight-medium">{{ racaoStore.formatarPeso(props.row.PESO_REFERENCIA) }}</div>
          <div class="text-caption">{{ racaoStore.formatarPeso(props.row.QUANTIDADE_DIARIA_TOTAL) }}/dia</div>
          <div class="text-caption text-grey-6">{{ racaoStore.formatarPercentual(props.row.PERCENTUAL_PESO_VIVO) }} PV</div>
        </q-td>
      </template>

      <template v-slot:body-cell-refeicoes_produtos="props">
        <q-td :props="props">
          <div class="text-weight-medium">{{ props.row.NUMERO_REFEICOES }}x refeições</div>
          <div class="text-caption">{{ props.row.total_produtos || 0 }} produtos</div>
        </q-td>
      </template>

      <template v-slot:body-cell-custo_diario="props">
        <q-td :props="props">
          {{ racaoStore.formatarMoeda(props.row.custo_diario_estimado) }}
        </q-td>
      </template>

      <template v-slot:body-cell-STATUS_PLANO="props">
        <q-td :props="props">
          <q-chip
            :color="getCorStatus(props.value)"
            text-color="white"
            size="sm"
          >
            {{ props.value }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-periodo="props">
        <q-td :props="props">
          <div>{{ formatarData(props.row.DATA_INICIO) }}</div>
          <div v-if="props.row.DATA_FIM" class="text-caption">até {{ formatarData(props.row.DATA_FIM) }}</div>
          <div v-else class="text-caption text-positive">Em andamento</div>
        </q-td>
      </template>

      <template v-slot:body-cell-acoes="props">
        <q-td :props="props">
          <q-btn-group flat>
            <q-btn
              flat
              round
              color="primary"
              icon="visibility"
              size="sm"
              @click="viewPlano(props.row)"
            >
              <q-tooltip>Visualizar</q-tooltip>
            </q-btn>
            <q-btn
              flat
              round
              color="info"
              icon="list"
              size="sm"
              @click="viewItens(props.row)"
            >
              <q-tooltip>Ver Itens</q-tooltip>
            </q-btn>
            <q-btn
              flat
              round
              color="secondary"
              icon="calculate"
              size="sm"
              @click="calcularPlano(props.row)"
            >
              <q-tooltip>Recalcular</q-tooltip>
            </q-btn>
            <q-btn
              flat
              round
              color="warning"
              icon="edit"
              size="sm"
              @click="openDialog(props.row)"
            >
              <q-tooltip>Editar</q-tooltip>
            </q-btn>
          </q-btn-group>
        </q-td>
      </template>
    </q-table>

    <!-- DIALOG FORMULÁRIO -->
    <q-dialog v-model="dialog" persistent>
      <q-card style="min-width: 700px">
        <q-card-section>
          <div class="text-h6">
            {{ form.ID ? 'Editar Plano Alimentar' : 'Novo Plano Alimentar' }}
          </div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="submitForm" class="q-gutter-md justify-between">
            <!-- Animal e Categoria -->
            <div class="row q-gutter-md">
              <q-select
                v-model="form.ID_ANIMAL"
                :options="animalOptionsDialog"
                label="Animal *"
                :rules="[val => !!val || 'Animal é obrigatório']"
                use-input
                @filter="filterAnimaisDialog"
                @update:model-value="onAnimalSelected"
                class="col-5"
              />
              <q-select
                v-model="form.CATEGORIA_NUTRICIONAL"
                :options="racaoStore.categoriasNutricionais"
                label="Categoria Nutricional *"
                :rules="[val => !!val || 'Categoria é obrigatória']"
                @update:model-value="onCategoriaChanged"
                class="col-6"
              />
            </div>

            <!-- Dados do Animal -->
            <div class="row q-gutter-md  justify-between">
              <q-input
                v-model.number="form.PESO_REFERENCIA"
                label="Peso de Referência (kg) *"
                type="number"
                step="0.1"
                min="1"
                :rules="[val => val > 0 || 'Peso deve ser maior que 0']"
                class="col-4"
              />
              <q-input
                v-model.number="form.ESCORE_CORPORAL"
                label="Escore Corporal (1-9)"
                type="number"
                step="0.5"
                min="1"
                max="9"
                class="col-3"
              />
              <q-select
                v-model="form.INTENSIDADE_TRABALHO"
                :options="racaoStore.intensidadeTrabalho"
                label="Intensidade de Trabalho"
                class="col-4"
              />
            </div>

            <!-- Parâmetros do Plano -->
            <div class="row q-gutter-md justify-between">
              <q-input
                v-model.number="form.QUANTIDADE_DIARIA_TOTAL"
                label="Quantidade Diária Total (kg)"
                type="number"
                step="0.1"
                min="0.1"
                :suffix="'kg (' + racaoStore.formatarPercentual(percentualPesoVivo) + ' PV)'"
                class="col-4"
              />
              <q-input
                v-model.number="form.NUMERO_REFEICOES"
                label="Número de Refeições *"
                type="number"
                min="1"
                max="4"
                :rules="[val => val >= 1 && val <= 4 || 'Entre 1 e 4 refeições']"
                class="col-3"
              />
              <q-select
                v-model="form.STATUS_PLANO"
                :options="racaoStore.statusPlano"
                label="Status do Plano"
                class="col-4"
              />
            </div>

            <!-- Período de Vigência -->
            <div class="row q-gutter-md justify-around">
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

            </div>

            <!-- Observações -->
            <q-input
              v-model="form.OBSERVACOES"
              label="Observações"
              type="textarea"
              rows="3"
            />

            <!-- Sugestão Nutricional -->
            <q-card v-if="sugestaoNutricional" flat bordered class="bg-blue-1">
              <q-card-section>
                <div class="text-subtitle2 q-mb-sm">
                  <q-icon name="lightbulb" class="q-mr-xs" />
                  Sugestão Nutricional
                </div>
                <div class="row q-gutter-md">
                  <div class="col">
                    <div class="text-caption">Quantidade Sugerida</div>
                    <div class="text-weight-medium">{{ racaoStore.formatarPeso(sugestaoNutricional.quantidade_sugerida_kg) }}/dia</div>
                  </div>
                  <div class="col">
                    <div class="text-caption">% Peso Vivo</div>
                    <div class="text-weight-medium">{{ racaoStore.formatarPercentual(sugestaoNutricional.percentual_peso_vivo) }}</div>
                  </div>
                  <div class="col">
                    <q-btn
                      flat
                      color="primary"
                      label="Usar Sugestão"
                      size="sm"
                      @click="usarSugestao"
                    />
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" @click="dialog = false" />
          <q-btn
            label="Salvar"
            color="primary"
            @click="submitForm"
            :loading="racaoStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG VISUALIZAÇÃO -->
    <q-dialog v-model="viewDialog">
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">{{ viewData?.animal_nome }}</div>
          <div class="text-subtitle2 text-grey-6">{{ racaoStore.getCategoriaLabel(viewData?.CATEGORIA_NUTRICIONAL) }}</div>
        </q-card-section>

        <q-card-section>
          <div class="row q-gutter-md" v-if="viewData">
            <div class="col-12">
              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Peso de Referência</q-item-label>
                    <q-item-label>{{ racaoStore.formatarPeso(viewData.PESO_REFERENCIA) }}</q-item-label>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Quantidade Diária</q-item-label>
                    <q-item-label>{{ racaoStore.formatarPeso(viewData.QUANTIDADE_DIARIA_TOTAL) }}</q-item-label>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>% Peso Vivo</q-item-label>
                    <q-item-label>{{ racaoStore.formatarPercentual(viewData.PERCENTUAL_PESO_VIVO) }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section>
                    <q-item-label caption>Refeições/Dia</q-item-label>
                    <q-item-label>{{ viewData.NUMERO_REFEICOES }}</q-item-label>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Total de Produtos</q-item-label>
                    <q-item-label>{{ viewData.total_produtos || 0 }}</q-item-label>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Custo Diário</q-item-label>
                    <q-item-label>{{ racaoStore.formatarMoeda(viewData.custo_diario_estimado) }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section>
                    <q-item-label caption>Período</q-item-label>
                    <q-item-label>
                      {{ formatarData(viewData.DATA_INICIO) }}
                      {{ viewData.DATA_FIM ? ' até ' + formatarData(viewData.DATA_FIM) : ' (em andamento)' }}
                    </q-item-label>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Status</q-item-label>
                    <q-item-label>
                      <q-chip
                        :color="getCorStatus(viewData.STATUS_PLANO)"
                        text-color="white"
                        size="sm"
                      >
                        {{ viewData.STATUS_PLANO }}
                      </q-chip>
                    </q-item-label>
                  </q-item-section>
                </q-item>

                <q-item v-if="viewData.OBSERVACOES">
                  <q-item-section>
                    <q-item-label caption>Observações</q-item-label>
                    <q-item-label>{{ viewData.OBSERVACOES }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Fechar" color="grey" @click="viewDialog = false" />
          <q-btn
            label="Ver Itens"
            color="primary"
            @click="viewItens(viewData); viewDialog = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG ITENS DO PLANO -->
    <q-dialog v-model="itensDialog" maximized>
      <q-card>
        <q-card-section>
          <div class="text-h6">
            Itens do Plano - {{ planoSelecionado?.animal_nome }}
          </div>
        </q-card-section>

        <q-card-section>
          <div class="row q-mb-md">
            <q-btn
              color="primary"
              icon="add"
              label="Adicionar Produto"
              @click="openItemDialog()"
            />
          </div>

          <!-- Lista de Itens -->
          <q-table
            :rows="racaoStore.itensPlano"
            :columns="itensColumns"
            row-key="ID"
            :loading="racaoStore.loading"
            flat
          >
            <template v-slot:body-cell-produto_nome="props">
              <q-td :props="props">
                <div class="text-weight-medium">{{ props.value }}</div>
                <div class="text-caption text-grey-6">{{ props.row.produto_tipo }}</div>
              </q-td>
            </template>

            <template v-slot:body-cell-quantidades="props">
              <q-td :props="props">
                <div class="text-weight-medium">{{ racaoStore.formatarPeso(props.row.QUANTIDADE_DIARIA) }}/dia</div>
                <div class="text-caption">{{ racaoStore.formatarPeso(props.row.QUANTIDADE_POR_REFEICAO) }}/refeição</div>
              </q-td>
            </template>

            <template v-slot:body-cell-horarios="props">
              <q-td :props="props">
                <div v-if="props.row.HORARIO_REFEICAO_1" class="text-caption">1ª: {{ props.row.HORARIO_REFEICAO_1 }}</div>
                <div v-if="props.row.HORARIO_REFEICAO_2" class="text-caption">2ª: {{ props.row.HORARIO_REFEICAO_2 }}</div>
                <div v-if="props.row.HORARIO_REFEICAO_3" class="text-caption">3ª: {{ props.row.HORARIO_REFEICAO_3 }}</div>
                <div v-if="props.row.HORARIO_REFEICAO_4" class="text-caption">4ª: {{ props.row.HORARIO_REFEICAO_4 }}</div>
              </q-td>
            </template>

            <template v-slot:body-cell-custo_diario="props">
              <q-td :props="props">
                {{ racaoStore.formatarMoeda(props.row.custo_diario) }}
              </q-td>
            </template>

            <template v-slot:body-cell-acoes="props">
              <q-td :props="props">
                <q-btn-group flat>
                  <q-btn
                    flat
                    round
                    color="warning"
                    icon="edit"
                    size="sm"
                    @click="openItemDialog(props.row)"
                  >
                    <q-tooltip>Editar</q-tooltip>
                  </q-btn>
                  <q-btn
                    flat
                    round
                    color="negative"
                    icon="delete"
                    size="sm"
                    @click="confirmDeleteItem(props.row)"
                  >
                    <q-tooltip>Remover</q-tooltip>
                  </q-btn>
                </q-btn-group>
              </q-td>
            </template>
          </q-table>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Fechar" color="grey" @click="itensDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>
    <!-- DIALOG ITEM PLANO -->
    <ItemPlanoDialog
    v-model="itemDialog"
    :plano-info="planoSelecionado"
    :item-edit="itemEditando"
    @saved="onItemSaved"
    @cancelled="onItemCancelled"
    />

    <!-- DIALOG CONFIRMAÇÃO DELETE ITEM -->
    <q-dialog v-model="deleteItemDialog" persistent>
    <q-card>
        <q-card-section>
        <div class="text-h6">Confirmar Exclusão</div>
        </q-card-section>
        <q-card-section>
        Remover <strong>{{ itemParaExcluir?.produto_nome }}</strong> do plano?
        </q-card-section>
        <q-card-actions align="right">
        <q-btn flat label="Cancelar" color="grey" @click="deleteItemDialog = false" />
        <q-btn label="Remover" color="negative" @click="deleteItem" :loading="racaoStore.loading" />
        </q-card-actions>
    </q-card>
    </q-dialog>    
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useRacaoStore } from 'stores/racao'
import { useAnimalStore } from 'stores/animal'
import { ErrorHandler } from 'src/utils/errorHandler'
import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'
import ItemPlanoDialog from 'components/racao/ItemPlanoDialog.vue'

// Composables
const $q = useQuasar()
const racaoStore = useRacaoStore()
const animalStore = useAnimalStore()

// Estado reativo
const dialog = ref(false)
const viewDialog = ref(false)
const itensDialog = ref(false)
const viewData = ref(null)
const planoSelecionado = ref(null)
const sugestaoNutricional = ref(null)
const itemDialog = ref(false)
const itemEditando = ref(null)
const deleteItemDialog = ref(false)
const itemParaExcluir = ref(null)

// Filtros
const filtros = ref({
  animal_id: null,
  categoria: null,
  status_plano: null
})

// Formulário
const form = ref({})

// Opções
const animalOri = ref([])
const animalOptions = ref([])
const animalOptionsDialog = ref([])

// Computed
const estatisticas = computed(() => racaoStore.estatisticasPlanos)

const percentualPesoVivo = computed(() => {
  if (!form.value.PESO_REFERENCIA || !form.value.QUANTIDADE_DIARIA_TOTAL) return 0
  return (form.value.QUANTIDADE_DIARIA_TOTAL / form.value.PESO_REFERENCIA) * 100
})

// Colunas
const columns = [
  { name: 'animal_nome', label: 'Animal', field: 'animal_nome', sortable: true, align: 'left' },
  { name: 'CATEGORIA_NUTRICIONAL', label: 'Categoria', field: 'CATEGORIA_NUTRICIONAL', sortable: true, align: 'center' },
  { name: 'peso_dieta', label: 'Peso/Dieta', field: 'peso_dieta', sortable: false, align: 'center' },
  { name: 'refeicoes_produtos', label: 'Refeições/Produtos', field: 'refeicoes_produtos', sortable: false, align: 'center' },
  { name: 'custo_diario', label: 'Custo Diário', field: 'custo_diario_estimado', sortable: true, align: 'right' },
  { name: 'STATUS_PLANO', label: 'Status', field: 'STATUS_PLANO', sortable: true, align: 'center' },
  { name: 'periodo', label: 'Período', field: 'periodo', sortable: false, align: 'left' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

const itensColumns = [
  { name: 'produto_nome', label: 'Produto', field: 'produto_nome', sortable: true, align: 'left' },
  { name: 'quantidades', label: 'Quantidades', field: 'quantidades', sortable: false, align: 'center' },
  { name: 'horarios', label: 'Horários', field: 'horarios', sortable: false, align: 'left' },
  { name: 'custo_diario', label: 'Custo Diário', field: 'custo_diario', sortable: true, align: 'right' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

// Métodos
async function onRequest(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  racaoStore.pagination.page = page
  racaoStore.pagination.rowsPerPage = rowsPerPage
  racaoStore.pagination.sortBy = sortBy
  racaoStore.pagination.descending = descending
  await racaoStore.fetchPlanosAlimentares({ ...props, filtros: filtros.value })
}

async function onFilterChange() {
  racaoStore.pagination.page = 1
  await racaoStore.fetchPlanosAlimentares({ filtros: filtros.value })
}

function openDialog(record) {
  initializeForm(record)
  dialog.value = true
}

function initializeForm(record) {
  sugestaoNutricional.value = null
  
  if (record) {
    form.value = { ...record }
    const idAnimal = record.ID_ANIMAL
    const categoriaNutricional = record.CATEGORIA_NUTRICIONAL
    const intensidadeTrabalho = record.INTENSIDADE_TRABALHO
    const statusPlano = record.STATUS_PLANO
    if (idAnimal && typeof idAnimal === 'number') {
        const animalOption = animalOri.value.find(f => f.value === idAnimal)
        if (animalOption) {
            form.value.ID_ANIMAL = animalOption
        } else {
            form.value.ID_ANIMAL = {
                value: idAnimal,
                label: record.animal_nome || `Animal: ${idAnimal}`
            }
        }
    }
    if (categoriaNutricional && typeof categoriaNutricional === 'string') {
    const categoriaOption = racaoStore.categoriasNutricionais.find(c => c.value === categoriaNutricional)
        if (categoriaOption) {
            form.value.CATEGORIA_NUTRICIONAL = categoriaOption
        }
    }    
    if (intensidadeTrabalho && typeof intensidadeTrabalho === 'string') {
        const intensidadeTrabalhoOption = racaoStore.intensidadeTrabalho.find(c => c.value === intensidadeTrabalho)
        if (intensidadeTrabalhoOption) {
            form.value.INTENSIDADE_TRABALHO = intensidadeTrabalhoOption
        }
    }    
    if (statusPlano && typeof statusPlano === 'string') {
        const statusPlanoOption = racaoStore.statusPlano.find(c => c.value === statusPlano)
        if (statusPlanoOption) {
            form.value.STATUS_PLANO = statusPlanoOption
        }
    }    
    onCategoriaChanged()
  } else {
    form.value = {
      ID_ANIMAL: null,
      CATEGORIA_NUTRICIONAL: null,
      PESO_REFERENCIA: null,
      ESCORE_CORPORAL: null,
      INTENSIDADE_TRABALHO: null,
      QUANTIDADE_DIARIA_TOTAL: null,
      NUMERO_REFEICOES: 3,
      PERCENTUAL_PESO_VIVO: null,
      DATA_INICIO: new Date().toISOString().split('T')[0],
      DATA_FIM: '',
      STATUS_PLANO: 'ATIVO',
      OBSERVACOES: ''
    }
  }
}

async function submitForm() {
  try {
    // Calcular percentual peso vivo
    if (form.value.PESO_REFERENCIA && form.value.QUANTIDADE_DIARIA_TOTAL) {
      form.value.PERCENTUAL_PESO_VIVO = percentualPesoVivo.value
    }

    if (form.value.ID) {
      await racaoStore.updatePlanoAlimentar(form.value.ID, form.value)
      ErrorHandler.success('Plano atualizado com sucesso!')
    } else {
      await racaoStore.createPlanoAlimentar(form.value)
      ErrorHandler.success('Plano criado com sucesso!')
    }
    
    dialog.value = false
    await racaoStore.fetchPlanosAlimentares({ filtros: filtros.value })
    
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao salvar plano')  
  }
}

function viewPlano(plano) {
  viewData.value = plano
  viewDialog.value = true
}

async function viewItens(plano) {
  planoSelecionado.value = plano
  await racaoStore.fetchItensPlano(plano.ID)
  itensDialog.value = true
}

async function calcularPlano(plano) {
  try {
    const calculo = await racaoStore.calcularNecessidadesNutricionais(
      plano.ID_ANIMAL, 
      plano.CATEGORIA_NUTRICIONAL
    )
    
    $q.dialog({
      title: 'Cálculo Nutricional',
      message: `Sugestão: ${racaoStore.formatarPeso(calculo.quantidade_sugerida_kg)}/dia (${racaoStore.formatarPercentual(calculo.percentual_peso_vivo)} PV)`,
      ok: 'Aplicar',
      cancel: 'Fechar'
    }).onOk(async () => {
      const updateData = {
        QUANTIDADE_DIARIA_TOTAL: calculo.quantidade_sugerida_kg,
        PERCENTUAL_PESO_VIVO: calculo.percentual_peso_vivo
      }
      
      await racaoStore.updatePlanoAlimentar(plano.ID, updateData)
      await racaoStore.fetchPlanosAlimentares({ filtros: filtros.value })
      ErrorHandler.success('Plano recalculado!')
    })
  } catch(error) {
    ErrorHandler.handle(error, 'Erro ao calcular necessidades')
  }
}

async function onAnimalSelected(animal) {
  if (animal?.peso_atual) {
    form.value.PESO_REFERENCIA = animal.peso_atual
  }
}

async function onCategoriaChanged() {
  if (form.value.ID_ANIMAL && form.value.CATEGORIA_NUTRICIONAL && form.value.PESO_REFERENCIA) {
    try {
      sugestaoNutricional.value = await racaoStore.calcularNecessidadesNutricionais(
        form.value.ID_ANIMAL.value,
        form.value.CATEGORIA_NUTRICIONAL.value
      )
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao calcular sugestão')  
    }
  }
}

function usarSugestao() {
  if (sugestaoNutricional.value) {
    form.value.QUANTIDADE_DIARIA_TOTAL = sugestaoNutricional.value.quantidade_sugerida_kg
    form.value.PERCENTUAL_PESO_VIVO = sugestaoNutricional.value.percentual_peso_vivo
  }
}

async function loadAnimalOptions() {
  try {
    animalStore.setPagination = {
      page: 1,
      rowsPerPage: 5000,
      rowsNumber: 0,
      sortBy: 'NOME',
    }

    animalStore.setFilters = {
        status: 'ATIVO'
    }

    const data = await animalStore.fetchAnimais();
   
    animalOri.value = data.animais.map(el => {
        return {
            value: el.ID,
            label: el.NOME,
            peso_atual: el.PESO_ATUAL
        }
    })
    animalOptions.value = [...animalOri.value]
    animalOptionsDialog.value = [...animalOri.value]
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao carregar animais')
  }
}

function filterAnimais(val, update) {
  update(() => {
    if (val === '') {
      animalOptions.value = [...animalOri.value]
    } else {
      const needle = val.toLowerCase()
      animalOptions.value = animalOri.value.filter(
        a => a.label.toLowerCase().includes(needle)
      )
    }
  })
}

function filterAnimaisDialog(val, update) {
  update(() => {
    if (val === '') {
      animalOptionsDialog.value = [...animalOri.value]
    } else {
      const needle = val.toLowerCase()
      animalOptionsDialog.value = animalOri.value.filter(
        a => a.label.toLowerCase().includes(needle)
      )
    }
  })
}

function openItemDialog(item = null) {
  itemEditando.value = item
  itemDialog.value = true
}

function confirmDeleteItem(item) {
  itemParaExcluir.value = item
  deleteItemDialog.value = true
}

async function deleteItem() {
  try {
    await racaoStore.deleteItemPlano(itemParaExcluir.value.ID)
    await racaoStore.fetchItensPlano(planoSelecionado.value.ID)
    await racaoStore.fetchPlanosAlimentares({ filtros: filtros.value })
    ErrorHandler.success('Item removido!')  
    deleteItemDialog.value = false

  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao remover item')  
  }
}

async function onItemSaved() {
  await racaoStore.fetchItensPlano(planoSelecionado.value.ID)
  await racaoStore.fetchPlanosAlimentares({ filtros: filtros.value })
}

function onItemCancelled() {
  itemEditando.value = null
}

// Funções auxiliares
function getCorCategoria(categoria) {
  const cores = {
    'POTRO': 'purple',
    'JOVEM': 'blue',
    'ADULTO_MANUTENCAO': 'green',
    'ADULTO_TRABALHO_LEVE': 'teal',
    'ADULTO_TRABALHO_MODERADO': 'orange',
    'ADULTO_TRABALHO_INTENSO': 'red',
    'EGUA_GESTANTE': 'pink',
    'EGUA_LACTANTE': 'indigo',
    'REPRODUTOR': 'brown',
    'IDOSO': 'grey'
  }
  return cores[categoria] || 'grey'
}

function getCorStatus(status) {
  const cores = {
    'ATIVO': 'positive',
    'INATIVO': 'grey',
    'SUSPENSO': 'warning'
  }
  return cores[status] || 'grey'
}

function formatarData(data) {
  if (!data) return '-'
  return new Date(data).toLocaleDateString('pt-BR')
}

// Watchers
watch(() => form.value.PESO_REFERENCIA, () => {
  if (form.value.CATEGORIA_NUTRICIONAL) {
    onCategoriaChanged()
  }
})

// Lifecycle
onMounted(async () => {
  await loadAnimalOptions()
  await racaoStore.fetchPlanosAlimentares({ filtros: filtros.value })
})
</script>

<style scoped>
.planos-alimentares-container {
  width: 100%;
}

.planos-table {
  border-radius: 8px;
}

.planos-table .q-table__top {
  padding: 16px;
}
</style>