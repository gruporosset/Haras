<template>
  <div class="fornecimento-racao-container">
    <!-- FILTROS -->
    <q-card
      flat
      bordered
      class="q-mb-md"
    >
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
            v-model="filtros.produto_id"
            :options="produtoOptions"
            label="Produto"
            clearable
            use-input
            @filter="filterProdutos"
            @update:model-value="onFilterChange"
            class="col-md-3 col-12"
          />

          <calendario-component
            v-model="filtros.data_inicio"
            label="Data Início"
            @update:model-value="onFilterChange"
            class="col-md-2 col-12"
          />

          <calendario-component
            v-model="filtros.data_fim"
            label="Data Fim"
            @update:model-value="onFilterChange"
            class="col-md-2 col-12"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- RESUMO DIÁRIO -->
    <q-card
      flat
      bordered
      class="q-mb-md"
    >
      <q-card-section>
        <div class="text-subtitle1 q-mb-sm">Resumo de Hoje</div>
        <div class="row q-gutter-md justify-between">
          <div class="col-md-3 col-6">
            <q-card
              flat
              bordered
            >
              <q-card-section class="text-center q-pa-sm">
                <div class="text-h4 text-primary">
                  {{ resumoHoje.totalFornecimentos }}
                </div>
                <div class="text-subtitle2">Fornecimentos</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-md-3 col-6">
            <q-card
              flat
              bordered
            >
              <q-card-section class="text-center q-pa-sm">
                <div class="text-h4 text-green">
                  {{ resumoHoje.animaisAlimentados }}
                </div>
                <div class="text-subtitle2">Animais</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-md-3 col-6">
            <q-card
              flat
              bordered
            >
              <q-card-section class="text-center q-pa-sm">
                <div class="text-h4 text-orange">
                  {{ racaoStore.formatarPeso(resumoHoje.totalRacao) }}
                </div>
                <div class="text-subtitle2">Total</div>
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
                  {{ racaoStore.formatarMoeda(resumoHoje.custoTotal) }}
                </div>
                <div class="text-subtitle2">Custo</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- TABELA -->
    <div class="row q-mb-md items-center">
      <q-btn
        color="primary"
        icon="add"
        label="Novo Fornecimento"
        @click="openDialog()"
      />
    </div>

    <q-table
      :rows="racaoStore.fornecimentos"
      :columns="columns"
      row-key="ID"
      :loading="racaoStore.loading"
      :pagination="racaoStore.pagination"
      @request="onRequest"
      binary-state-sort
      flat
      class="fornecimentos-table"
    >
      <template v-slot:body-cell-animal_nome="props">
        <q-td :props="props">
          <div class="text-weight-medium">{{ props.value }}</div>
          <div class="text-caption text-grey-6">
            {{ props.row.animal_numero_registro }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-produto_nome="props">
        <q-td :props="props">
          <div class="text-weight-medium">{{ props.value }}</div>
          <div class="text-caption text-grey-6">
            {{ props.row.produto_unidade }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-refeicao="props">
        <q-td :props="props">
          <div class="text-center">
            <q-chip
              :color="getCorRefeicao(props.row.NUMERO_REFEICAO)"
              text-color="white"
              size="sm"
            >
              {{ props.row.NUMERO_REFEICAO }}ª
            </q-chip>
            <div class="text-caption">
              {{ props.row.HORARIO_FORNECIMENTO || '-' }}
            </div>
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-quantidades="props">
        <q-td :props="props">
          <div class="text-weight-medium">
            {{ racaoStore.formatarPeso(props.row.QUANTIDADE_FORNECIDA) }}
          </div>
          <div
            v-if="props.row.QUANTIDADE_PLANEJADA"
            class="text-caption"
          >
            Planejado:
            {{ racaoStore.formatarPeso(props.row.QUANTIDADE_PLANEJADA) }}
          </div>
          <div
            v-if="props.row.PESO_ANIMAL_REFERENCIA"
            class="text-caption text-grey-6"
          >
            Animal:
            {{ racaoStore.formatarPeso(props.row.PESO_ANIMAL_REFERENCIA) }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-custo_fornecimento="props">
        <q-td :props="props">
          {{ racaoStore.formatarMoeda(props.row.custo_fornecimento) }}
        </q-td>
      </template>

      <template v-slot:body-cell-DATA_FORNECIMENTO="props">
        <q-td :props="props">
          {{
            props.row.DATA_FORNECIMENTO +
            ' ' +
            (props.row.HORARIO_FORNECIMENTO ?? '')
          }}
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
              @click="viewFornecimento(props.row)"
            >
              <q-tooltip>Visualizar</q-tooltip>
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
            <q-btn
              flat
              round
              color="negative"
              icon="delete"
              size="sm"
              @click="confirmDelete(props.row)"
            >
              <q-tooltip>Excluir</q-tooltip>
            </q-btn>
          </q-btn-group>
        </q-td>
      </template>
    </q-table>

    <!-- DIALOG FORMULÁRIO -->
    <q-dialog
      v-model="dialog"
      persistent
    >
      <q-card style="min-width: 700px">
        <q-card-section>
          <div class="text-h6">
            {{ form.ID ? 'Editar Fornecimento' : 'Novo Fornecimento' }}
          </div>
        </q-card-section>

        <q-card-section>
          <q-form
            @submit="submitForm"
            class="q-gutter-md"
            ref="formRef"
          >
            <!-- Animal e Produto -->
            <div class="row q-gutter-md justify-between">
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
                v-model="form.ID_PRODUTO"
                :options="produtoOptionsDialog"
                label="Produto *"
                :rules="[val => !!val || 'Produto é obrigatório']"
                use-input
                @filter="filterProdutosDialog"
                @update:model-value="onProdutoSelected"
                class="col-6"
              />
            </div>

            <!-- Plano Alimentar Ativo -->
            <q-card
              v-if="planoAtivo"
              flat
              bordered
              class="bg-green-1"
            >
              <q-card-section class="q-pa-sm">
                <div class="text-subtitle2">
                  <q-icon
                    name="restaurant_menu"
                    class="q-mr-xs"
                  />
                  Plano Alimentar Ativo
                </div>
                <div class="text-body2">
                  {{
                    racaoStore.getCategoriaLabel(
                      planoAtivo.CATEGORIA_NUTRICIONAL
                    )
                  }}
                  -
                  {{
                    racaoStore.formatarPeso(planoAtivo.QUANTIDADE_DIARIA_TOTAL)
                  }}/dia em {{ planoAtivo.NUMERO_REFEICOES }} refeições
                </div>
                <q-btn
                  flat
                  color="primary"
                  label="Usar Plano"
                  size="sm"
                  @click="usarPlanoAtivo"
                />
              </q-card-section>
            </q-card>

            <!-- Estoque Disponível -->
            <q-card
              v-if="estoqueDisponivel > 0"
              flat
              bordered
              class="bg-blue-1"
            >
              <q-card-section class="q-pa-sm">
                <div class="text-caption">Estoque Disponível</div>
                <div class="text-h6">
                  {{ racaoStore.formatarPeso(estoqueDisponivel) }}
                </div>
              </q-card-section>
            </q-card>

            <!-- Data e Horário -->
            <div class="row q-gutter-md justify-between">
              <calendario-component
                v-model="form.DATA_FORNECIMENTO"
                label="Data do Fornecimento *"
                :rules="[val => !!val || 'Data é obrigatória']"
                class="col-4"
              />
              <q-input
                v-model="form.HORARIO_FORNECIMENTO"
                label="Horário"
                mask="##:##"
                placeholder="HH:MM"
                class="col-3"
              />
              <q-select
                v-model="form.NUMERO_REFEICAO"
                :options="refeicaoOptionsDialog"
                label="Número da Refeição"
                class="col-4"
              />
            </div>

            <!-- Quantidades -->
            <div class="row q-gutter-md">
              <q-input
                v-model.number="form.QUANTIDADE_PLANEJADA"
                label="Quantidade Planejada"
                type="number"
                step="0.001"
                min="0"
                :suffix="unidadeSelecionada"
                class="col-3"
              />
              <q-input
                v-model.number="form.QUANTIDADE_FORNECIDA"
                label="Quantidade Fornecida *"
                type="number"
                step="0.001"
                min="0.001"
                :max="estoqueDisponivel"
                :rules="[
                  val => val > 0 || 'Quantidade deve ser maior que 0',
                  val =>
                    val <= estoqueDisponivel ||
                    `Máximo disponível: ${estoqueDisponivel}`,
                ]"
                :suffix="unidadeSelecionada"
                class="col-3"
              />
              <q-input
                v-model.number="form.PESO_ANIMAL_REFERENCIA"
                label="Peso do Animal (kg)"
                type="number"
                step="0.1"
                min="0"
                class="col-5"
              />
            </div>

            <!-- Responsável -->
            <q-input
              v-model="form.FUNCIONARIO_RESPONSAVEL"
              label="Funcionário Responsável"
            />

            <!-- Observações -->
            <q-input
              v-model="form.OBSERVACOES"
              label="Observações"
              type="textarea"
              rows="2"
            />

            <!-- Resumo do Fornecimento -->
            <q-card
              v-if="form.QUANTIDADE_FORNECIDA && custoEstimado > 0"
              flat
              bordered
              class="bg-grey-1"
            >
              <q-card-section class="q-pa-sm">
                <div class="text-subtitle2 q-mb-xs">Resumo do Fornecimento</div>
                <div class="row q-gutter-md">
                  <div class="col">
                    <div class="text-caption">Quantidade</div>
                    <div class="text-weight-medium">
                      {{ racaoStore.formatarPeso(form.QUANTIDADE_FORNECIDA) }}
                    </div>
                  </div>
                  <div class="col">
                    <div class="text-caption">Custo Estimado</div>
                    <div class="text-weight-medium">
                      {{ racaoStore.formatarMoeda(custoEstimado) }}
                    </div>
                  </div>
                  <div
                    v-if="form.PESO_ANIMAL_REFERENCIA"
                    class="col"
                  >
                    <div class="text-caption">% Peso Vivo</div>
                    <div class="text-weight-medium">
                      {{ percentualPesoVivo.toFixed(2) }}%
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancelar"
            color="grey"
            @click="dialog = false"
          />
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
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Detalhes do Fornecimento</div>
        </q-card-section>

        <q-card-section>
          <q-list v-if="viewData">
            <q-item>
              <q-item-section>
                <q-item-label caption>Animal</q-item-label>
                <q-item-label>{{ viewData.animal_nome }}</q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Produto</q-item-label>
                <q-item-label>{{ viewData.produto_nome }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Data/Horário</q-item-label>
                <q-item-label>
                  {{ formatarDataHora(viewData.DATA_FORNECIMENTO) }}
                </q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Refeição</q-item-label>
                <q-item-label>
                  {{ viewData.NUMERO_REFEICAO }}ª -
                  {{ viewData.HORARIO_FORNECIMENTO || 'Sem horário' }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Quantidade Fornecida</q-item-label>
                <q-item-label>
                  {{ racaoStore.formatarPeso(viewData.QUANTIDADE_FORNECIDA) }}
                </q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Custo</q-item-label>
                <q-item-label>
                  {{ racaoStore.formatarMoeda(viewData.custo_fornecimento) }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData.QUANTIDADE_PLANEJADA">
              <q-item-section>
                <q-item-label caption>Quantidade Planejada</q-item-label>
                <q-item-label>
                  {{ racaoStore.formatarPeso(viewData.QUANTIDADE_PLANEJADA) }}
                </q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Diferença</q-item-label>
                <q-item-label :class="getDiferencaClass(viewData)">
                  {{ getDiferencaTexto(viewData) }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData.PESO_ANIMAL_REFERENCIA">
              <q-item-section>
                <q-item-label caption>Peso do Animal</q-item-label>
                <q-item-label>
                  {{ racaoStore.formatarPeso(viewData.PESO_ANIMAL_REFERENCIA) }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData.FUNCIONARIO_RESPONSAVEL">
              <q-item-section>
                <q-item-label caption>Responsável</q-item-label>
                <q-item-label>
                  {{ viewData.FUNCIONARIO_RESPONSAVEL }}
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
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Fechar"
            color="grey"
            @click="viewDialog = false"
          />
          <q-btn
            label="Editar"
            color="primary"
            @click="(openDialog(viewData), (viewDialog = false))"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG CONFIRMAÇÃO EXCLUSÃO -->
    <q-dialog
      v-model="deleteDialog"
      persistent
    >
      <q-card>
        <q-card-section>
          <div class="text-h6">Confirmar Exclusão</div>
        </q-card-section>
        <q-card-section>
          Tem certeza que deseja excluir o fornecimento
          <strong>{{ recordToDelete?.NOME }}</strong>
          ?
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancelar"
            color="grey"
            @click="deleteDialog = false"
          />
          <q-btn
            label="Excluir"
            color="negative"
            @click="deleteFornecimento"
            :loading="racaoStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
  import { ref, onMounted, computed } from 'vue'
  import { useQuasar } from 'quasar'
  import { useRacaoStore } from 'stores/racao'
  import { useAnimalStore } from 'stores/animal'
  import { ErrorHandler } from 'src/utils/errorHandler'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

  // Composables
  const $q = useQuasar()
  const racaoStore = useRacaoStore()
  const animalStore = useAnimalStore()

  // Estado reativo
  const dialog = ref(false)
  const viewDialog = ref(false)
  const viewData = ref(null)
  const planoAtivo = ref(null)
  const formRef = ref(null)
  const recordToDelete = ref(null)
  const deleteDialog = ref(false)

  // Filtros
  const filtros = ref({
    animal_id: null,
    produto_id: null,
    data_inicio: '',
    data_fim: '',
  })

  // Formulário
  const form = ref({})

  // Opções
  const animalOri = ref([])
  const animalOptions = ref([])
  const animalOptionsDialog = ref([])
  const produtoOri = ref([])
  const produtoOptions = ref([])
  const produtoOptionsDialog = ref([])
  const refeicaoOptionsDialog = ref([
    { value: 1, label: '1ª Refeição' },
    { value: 2, label: '2ª Refeição' },
    { value: 3, label: '3ª Refeição' },
    { value: 4, label: '4ª Refeição' },
  ])

  // Computed
  const resumoHoje = computed(() => {
    const hoje = new Date().toLocaleDateString('pt-br').split(',')[0]
    const fornecimentosHoje = racaoStore.fornecimentos.filter(f =>
      f.DATA_FORNECIMENTO?.startsWith(hoje)
    )

    return {
      totalFornecimentos: fornecimentosHoje.length,
      animaisAlimentados: new Set(fornecimentosHoje.map(f => f.ID_ANIMAL)).size,
      totalRacao: fornecimentosHoje.reduce(
        (sum, f) => sum + (f.QUANTIDADE_FORNECIDA || 0),
        0
      ),
      custoTotal: fornecimentosHoje.reduce(
        (sum, f) => sum + (f.custo_fornecimento || 0),
        0
      ),
    }
  })

  const unidadeSelecionada = computed(() => {
    if (!form.value.ID_PRODUTO?.unidade_medida) return ''
    return form.value.ID_PRODUTO.unidade_medida
  })

  const estoqueDisponivel = computed(() => {
    if (!form.value.ID_PRODUTO?.estoque_atual) return 0
    return form.value.ID_PRODUTO.estoque_atual
  })

  const custoEstimado = computed(() => {
    if (
      !form.value.QUANTIDADE_FORNECIDA ||
      !form.value.ID_PRODUTO?.preco_unitario
    )
      return 0
    return (
      form.value.QUANTIDADE_FORNECIDA * form.value.ID_PRODUTO.preco_unitario
    )
  })

  const percentualPesoVivo = computed(() => {
    if (!form.value.QUANTIDADE_FORNECIDA || !form.value.PESO_ANIMAL_REFERENCIA)
      return 0
    return (
      (form.value.QUANTIDADE_FORNECIDA / form.value.PESO_ANIMAL_REFERENCIA) *
      100
    )
  })

  // Colunas
  const columns = [
    {
      name: 'animal_nome',
      label: 'Animal',
      field: 'animal_nome',
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
      name: 'refeicao',
      label: 'Refeição',
      field: 'refeicao',
      sortable: false,
      align: 'center',
    },
    {
      name: 'quantidades',
      label: 'Quantidades',
      field: 'quantidades',
      sortable: false,
      align: 'center',
    },
    {
      name: 'custo_fornecimento',
      label: 'Custo',
      field: 'custo_fornecimento',
      sortable: true,
      align: 'right',
    },
    {
      name: 'DATA_FORNECIMENTO',
      label: 'Data/Hora',
      field: 'DATA_FORNECIMENTO',
      sortable: true,
      align: 'left',
    },
    { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' },
  ]

  // Métodos
  async function onRequest(props) {
    const { page, rowsPerPage, sortBy, descending } = props.pagination
    racaoStore.pagination.page = page
    racaoStore.pagination.rowsPerPage = rowsPerPage
    racaoStore.pagination.sortBy = sortBy
    racaoStore.pagination.descending = descending
    await racaoStore.fetchFornecimentos({ ...props, filtros: filtros.value })
  }

  async function onFilterChange() {
    racaoStore.pagination.page = 1
    await racaoStore.fetchFornecimentos({ filtros: filtros.value })
  }

  function openDialog(record) {
    initializeForm(record)
    dialog.value = true
  }

  function initializeForm(record) {
    planoAtivo.value = null
    form.value = { ...record }
    if (record) {
      const idAnimal = record.ID_ANIMAL
      const idProduto = record.ID_PRODUTO

      if (idAnimal && typeof idAnimal === 'number') {
        const animalOption = animalOri.value.find(f => f.value === idAnimal)
        if (animalOption) {
          form.value.ID_ANIMAL = animalOption
        } else {
          form.value.ID_ANIMAL = {
            value: idAnimal,
            label: record.animal_nome || `Animal: ${idAnimal}`,
          }
        }
      }

      if (idProduto && typeof idProduto === 'number') {
        const produtoOption = produtoOri.value.find(f => f.value === idProduto)
        if (produtoOption) {
          form.value.ID_PRODUTO = produtoOption
        } else {
          form.value.ID_PRODUTO = {
            value: idProduto,
            label: record.produto_nome || `Produto: ${idProduto}`,
          }
        }
      }
    } else {
      form.value = {
        ID_ANIMAL: null,
        ID_PRODUTO: null,
        ID_PLANO: null,
        DATA_FORNECIMENTO: new Date().toISOString().split('T')[0],
        HORARIO_FORNECIMENTO: '',
        NUMERO_REFEICAO: 1,
        QUANTIDADE_PLANEJADA: null,
        QUANTIDADE_FORNECIDA: null,
        PESO_ANIMAL_REFERENCIA: null,
        FUNCIONARIO_RESPONSAVEL: '',
        OBSERVACOES: '',
      }
    }

    if (
      form.value.NUMERO_REFEICAO &&
      typeof form.value.NUMERO_REFEICAO === 'number'
    ) {
      const refeicaoOption = refeicaoOptionsDialog.value.find(
        f => f.value === form.value.NUMERO_REFEICAO
      )
      if (refeicaoOption) {
        form.value.NUMERO_REFEICAO = refeicaoOption
      }
    }
  }

  async function submitForm() {
    try {
      const isValid = await formRef.value?.validate()

      if (!isValid) {
        ErrorHandler.handle({}, 'Por favor, corrija os campos obrigatórios')
        return
      }

      const data = { ...form.value }

      if (data.ID_ANIMAL?.value) data.ID_ANIMAL = data.ID_ANIMAL.value
      if (data.ID_PRODUTO?.value) data.ID_PRODUTO = data.ID_PRODUTO.value
      if (data.NUMERO_REFEICAO?.value)
        data.NUMERO_REFEICAO = data.NUMERO_REFEICAO.value
      if (data.HORARIO_FORNECIMENTO === '') delete data.HORARIO_FORNECIMENTO
      if (data.QUANTIDADE_PLANEJADA === '') delete data.QUANTIDADE_PLANEJADA

      if (form.value.ID) {
        await racaoStore.updateFornecimento(form.value.ID, data)
        $q.notify({ type: 'positive', message: 'Fornecimento atualizado!' })
      } else {
        await racaoStore.registrarFornecimento(data)
        $q.notify({ type: 'positive', message: 'Fornecimento registrado!' })
      }

      dialog.value = false
      await racaoStore.fetchFornecimentos({ filtros: filtros.value })
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: error.message || 'Erro ao salvar',
      })
    }
  }

  function viewFornecimento(fornecimento) {
    viewData.value = fornecimento
    viewDialog.value = true
  }

  async function onAnimalSelected(animal) {
    if (animal?.value) {
      // Buscar plano ativo do animal
      const planosAtivos = racaoStore.planosAtivos.filter(
        p => p.ID_ANIMAL === animal.value
      )
      if (planosAtivos.length > 0) {
        planoAtivo.value = planosAtivos[0]
      }

      // Definir peso se disponível
      if (animal.peso_atual) {
        form.value.PESO_ANIMAL_REFERENCIA = animal.peso_atual
      }
    }
  }

  function onProdutoSelected(produto) {
    if (produto?.value) {
      form.value.ID_PRODUTO = {
        value: produto.value,
        label: produto.label,
        estoque_atual: produto.estoque_atual || 0,
        unidade_medida: produto.unidade_medida,
        preco_unitario: produto.preco_unitario,
      }
    }
  }

  function usarPlanoAtivo() {
    if (planoAtivo.value) {
      form.value.ID_PLANO = planoAtivo.value.ID
      form.value.QUANTIDADE_PLANEJADA =
        planoAtivo.value.QUANTIDADE_DIARIA_TOTAL /
        planoAtivo.value.NUMERO_REFEICOES
      form.value.QUANTIDADE_FORNECIDA = form.value.QUANTIDADE_PLANEJADA
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
        status: 'ATIVO',
      }

      const data = await animalStore.fetchAnimais()

      animalOri.value = data.animais.map(el => {
        return {
          value: el.ID,
          label: el.NOME,
          peso_atual: el.PESO_ATUAL,
        }
      })
      animalOptions.value = [...animalOri.value]
      animalOptionsDialog.value = [...animalOri.value]
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar animais')
    }
  }

  async function loadOptionsProdutos() {
    try {
      // Carregar produtos
      const produtos = await racaoStore.autocompleProdutos('')
      produtoOri.value = produtos.map(p => ({
        value: p.value,
        label: p.label,
        estoque_atual: p.estoque_atual,
        unidade_medida: p.unidade_medida,
        preco_unitario: p.preco_unitario,
      }))
      produtoOptionsDialog.value = [...produtoOri.value]
    } catch (error) {
      console.error('Erro ao carregar opções:', error)
    }
  }

  function filterAnimais(val, update) {
    update(() => {
      if (val === '') {
        animalOptions.value = [...animalOri.value]
      } else {
        const needle = val.toLowerCase()
        animalOptions.value = animalOri.value.filter(a =>
          a.label.toLowerCase().includes(needle)
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
        animalOptionsDialog.value = animalOri.value.filter(a =>
          a.label.toLowerCase().includes(needle)
        )
      }
    })
  }

  function filterProdutos(val, update) {
    update(() => {
      if (val === '') {
        produtoOptions.value = [...produtoOri.value]
      } else {
        const needle = val.toLowerCase()
        produtoOptions.value = produtoOri.value.filter(p =>
          p.label.toLowerCase().includes(needle)
        )
      }
    })
  }

  function filterProdutosDialog(val, update) {
    update(() => {
      if (val === '') {
        produtoOptionsDialog.value = [...produtoOri.value]
      } else {
        const needle = val.toLowerCase()
        produtoOptionsDialog.value = produtoOri.value.filter(p =>
          p.label.toLowerCase().includes(needle)
        )
      }
    })
  }

  function confirmDelete(record) {
    recordToDelete.value = record
    deleteDialog.value = true
  }

  async function deleteFornecimento() {
    try {
      await racaoStore.deleteFornecimento(recordToDelete.value.ID)
      ErrorHandler.success('Fornecimento excluído com sucesso!')
      deleteDialog.value = false
      await racaoStore.fetchFornecimentos({ filtros: filtros.value })
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao excluir produto')
    }
  }

  // Funções auxiliares
  function getCorRefeicao(numero) {
    const cores = { 1: 'primary', 2: 'secondary', 3: 'accent', 4: 'warning' }
    return cores[numero] || 'grey'
  }

  function getDiferencaClass(fornecimento) {
    const planejada = fornecimento.QUANTIDADE_PLANEJADA || 0
    const fornecida = fornecimento.QUANTIDADE_FORNECIDA || 0
    const diferenca = fornecida - planejada

    if (diferenca > 0) return 'text-warning'
    if (diferenca < 0) return 'text-negative'
    return 'text-positive'
  }

  function getDiferencaTexto(fornecimento) {
    const planejada = fornecimento.QUANTIDADE_PLANEJADA || 0
    const fornecida = fornecimento.QUANTIDADE_FORNECIDA || 0
    const diferenca = fornecida - planejada

    if (diferenca === 0) return 'Conforme planejado'
    if (diferenca > 0) return `+${racaoStore.formatarPeso(diferenca)}`
    return racaoStore.formatarPeso(diferenca)
  }

  function formatarDataHora(data) {
    if (!data) return '-'
    return new Date(data).toLocaleString('pt-BR')
  }

  // Lifecycle
  onMounted(async () => {
    await loadAnimalOptions()
    await loadOptionsProdutos()
    await racaoStore.fetchFornecimentos({ filtros: filtros.value })
  })
</script>

<style scoped>
  .fornecimento-racao-container {
    width: 100%;
  }

  .fornecimentos-table {
    border-radius: 8px;
  }

  .fornecimentos-table .q-table__top {
    padding: 16px;
  }
</style>
