<template>
  <q-dialog
    v-model="dialog"
    persistent
  >
    <q-card style="min-width: 600px">
      <q-card-section>
        <div class="text-h6">
          {{ form.ID ? 'Editar Item do Plano' : 'Adicionar Produto ao Plano' }}
        </div>
        <div class="text-subtitle2 text-grey-6">
          {{ planoInfo?.animal_nome }} -
          {{ racaoStore.getCategoriaLabel(planoInfo?.CATEGORIA_NUTRICIONAL) }}
        </div>
      </q-card-section>

      <q-card-section>
        <q-form
          @submit="submitForm"
          class="q-gutter-md"
        >
          <!-- Produto -->
          <q-select
            v-model="form.ID_PRODUTO"
            :options="produtoOptions"
            label="Produto *"
            :rules="[val => !!val || 'Produto é obrigatório']"
            use-input
            @filter="filterProdutos"
            @update:model-value="onProdutoSelected"
          >
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.label }}</q-item-label>
                  <q-item-label caption>
                    {{
                      racaoStore.getTipoAlimentoLabel(scope.opt.tipo_alimento)
                    }}
                    - Estoque:
                    {{ racaoStore.formatarPeso(scope.opt.estoque_atual) }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>

          <!-- Estoque Disponível -->
          <q-card
            v-if="produtoSelecionado"
            flat
            bordered
            class="bg-blue-1"
          >
            <q-card-section class="q-pa-sm">
              <div class="row q-gutter-md">
                <div class="col">
                  <div class="text-caption">Estoque Disponível</div>
                  <div class="text-weight-medium">
                    {{
                      racaoStore.formatarPeso(produtoSelecionado.estoque_atual)
                    }}
                  </div>
                </div>
                <div class="col">
                  <div class="text-caption">Tipo</div>
                  <div class="text-weight-medium">
                    {{
                      racaoStore.getTipoAlimentoLabel(
                        produtoSelecionado.tipo_alimento
                      )
                    }}
                  </div>
                </div>
                <div
                  class="col"
                  v-if="produtoSelecionado.preco_unitario"
                >
                  <div class="text-caption">Preço Unitário</div>
                  <div class="text-weight-medium">
                    {{
                      racaoStore.formatarMoeda(
                        produtoSelecionado.preco_unitario
                      )
                    }}
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Quantidades -->
          <div class="row q-gutter-md">
            <q-input
              v-model.number="form.QUANTIDADE_DIARIA"
              label="Quantidade Diária *"
              type="number"
              step="0.001"
              min="0.001"
              :rules="[val => val > 0 || 'Quantidade deve ser maior que 0']"
              :suffix="unidadeSelecionada"
              @update:model-value="calcularPorRefeicao"
              class="col-5"
            />
            <q-input
              v-model.number="form.QUANTIDADE_POR_REFEICAO"
              label="Quantidade por Refeição *"
              type="number"
              step="0.001"
              min="0.001"
              :rules="[val => val > 0 || 'Quantidade deve ser maior que 0']"
              :suffix="unidadeSelecionada"
              @update:model-value="calcularDiaria"
              class="col-6"
            />
          </div>

          <!-- Número de Refeições e Ordem -->
          <div class="row q-gutter-md">
            <q-input
              v-model.number="numeroRefeicoes"
              label="Número de Refeições"
              type="number"
              min="1"
              max="4"
              readonly
              class="col-5"
            />
            <q-input
              v-model.number="form.ORDEM_FORNECIMENTO"
              label="Ordem de Fornecimento"
              type="number"
              min="1"
              max="10"
              hint="Ordem de fornecimento na refeição"
              class="col-6"
            />
          </div>

          <!-- Horários das Refeições -->
          <div class="text-subtitle2 q-mt-md q-mb-sm">
            Horários das Refeições (opcional)
          </div>
          <div class="row q-gutter-md">
            <q-input
              v-model="form.HORARIO_REFEICAO_1"
              label="1ª Refeição"
              mask="##:##"
              placeholder="HH:MM"
              class="col-2"
            />
            <q-input
              v-if="numeroRefeicoes >= 2"
              v-model="form.HORARIO_REFEICAO_2"
              label="2ª Refeição"
              mask="##:##"
              placeholder="HH:MM"
              class="col-2"
            />
            <q-input
              v-if="numeroRefeicoes >= 3"
              v-model="form.HORARIO_REFEICAO_3"
              label="3ª Refeição"
              mask="##:##"
              placeholder="HH:MM"
              class="col-2"
            />
            <q-input
              v-if="numeroRefeicoes >= 4"
              v-model="form.HORARIO_REFEICAO_4"
              label="4ª Refeição"
              mask="##:##"
              placeholder="HH:MM"
              class="col-2"
            />
          </div>

          <!-- Observações -->
          <q-input
            v-model="form.OBSERVACOES"
            label="Observações"
            type="textarea"
            rows="2"
          />

          <!-- Resumo do Item -->
          <q-card
            v-if="form.QUANTIDADE_DIARIA && custoEstimado > 0"
            flat
            bordered
            class="bg-grey-1"
          >
            <q-card-section class="q-pa-sm">
              <div class="text-subtitle2 q-mb-xs">Resumo do Item</div>
              <div class="row q-gutter-md">
                <div class="col">
                  <div class="text-caption">Quantidade Diária</div>
                  <div class="text-weight-medium">
                    {{ racaoStore.formatarPeso(form.QUANTIDADE_DIARIA) }}
                  </div>
                </div>
                <div class="col">
                  <div class="text-caption">Por Refeição</div>
                  <div class="text-weight-medium">
                    {{ racaoStore.formatarPeso(form.QUANTIDADE_POR_REFEICAO) }}
                  </div>
                </div>
                <div class="col">
                  <div class="text-caption">Custo Diário</div>
                  <div class="text-weight-medium">
                    {{ racaoStore.formatarMoeda(custoEstimado) }}
                  </div>
                </div>
                <div class="col">
                  <div class="text-caption">Custo Mensal</div>
                  <div class="text-weight-medium">
                    {{ racaoStore.formatarMoeda(custoEstimado * 30) }}
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
          @click="cancelar"
        />
        <q-btn
          label="Salvar"
          color="primary"
          @click="submitForm"
          :loading="loading"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
  import { ref, computed, watch } from 'vue'
  import { useRacaoStore } from 'stores/racao'
  import { ErrorHandler } from 'src/utils/errorHandler'

  // Props
  const props = defineProps({
    modelValue: {
      type: Boolean,
      default: false,
    },
    planoInfo: {
      type: Object,
      default: null,
    },
    itemEdit: {
      type: Object,
      default: null,
    },
  })

  // Emits
  const emit = defineEmits(['update:modelValue', 'saved', 'cancelled'])

  // Composables
  const racaoStore = useRacaoStore()

  // Estado reativo
  const loading = ref(false)
  const produtoOptions = ref([])
  const produtoOptionsOriginal = ref([])

  // Formulário
  const form = ref({
    ID_PLANO: null,
    ID_PRODUTO: null,
    QUANTIDADE_DIARIA: null,
    QUANTIDADE_POR_REFEICAO: null,
    ORDEM_FORNECIMENTO: 1,
    HORARIO_REFEICAO_1: '',
    HORARIO_REFEICAO_2: '',
    HORARIO_REFEICAO_3: '',
    HORARIO_REFEICAO_4: '',
    OBSERVACOES: '',
  })

  // Computed
  const dialog = computed({
    get: () => props.modelValue,
    set: value => emit('update:modelValue', value),
  })

  const numeroRefeicoes = computed(() => {
    return props.planoInfo?.NUMERO_REFEICOES || 3
  })

  const produtoSelecionado = computed(() => {
    if (!form.value.ID_PRODUTO?.value) return null
    return produtoOptionsOriginal.value.find(
      p => p.value === form.value.ID_PRODUTO.value
    )
  })

  const unidadeSelecionada = computed(() => {
    return produtoSelecionado.value?.unidade_medida || 'KG'
  })

  const custoEstimado = computed(() => {
    if (
      !form.value.QUANTIDADE_DIARIA ||
      !produtoSelecionado.value?.preco_unitario
    )
      return 0
    return (
      form.value.QUANTIDADE_DIARIA * produtoSelecionado.value.preco_unitario
    )
  })

  // Métodos
  async function initializeForm() {
    if (props.itemEdit) {
      // Editando item existente
      form.value = { ...props.itemEdit }

      // Converter ID_PRODUTO para objeto se necessário
      if (
        props.itemEdit.ID_PRODUTO &&
        typeof props.itemEdit.ID_PRODUTO === 'number'
      ) {
        const produtoOption = produtoOptionsOriginal.value.find(
          p => p.value === props.itemEdit.ID_PRODUTO
        )
        if (produtoOption) {
          form.value.ID_PRODUTO = produtoOption
        }
      }
    } else {
      // Novo item
      form.value = {
        ID_PLANO: props.planoInfo?.ID || null,
        ID_PRODUTO: null,
        QUANTIDADE_DIARIA: null,
        QUANTIDADE_POR_REFEICAO: null,
        ORDEM_FORNECIMENTO: 1,
        HORARIO_REFEICAO_1: '',
        HORARIO_REFEICAO_2: '',
        HORARIO_REFEICAO_3: '',
        HORARIO_REFEICAO_4: '',
        OBSERVACOES: '',
      }
    }
  }

  async function loadProdutoOptions() {
    try {
      const produtos = await racaoStore.autocompleProdutos('')
      produtoOptionsOriginal.value = produtos.map(p => ({
        value: p.value,
        label: p.label,
        estoque_atual: p.estoque_atual,
        unidade_medida: p.unidade_medida,
        tipo_alimento: p.tipo_alimento,
        preco_unitario: p.preco_unitario || 0,
      }))
      produtoOptions.value = [...produtoOptionsOriginal.value]
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar produtos')
    }
  }

  function filterProdutos(val, update) {
    update(() => {
      if (val === '') {
        produtoOptions.value = [...produtoOptionsOriginal.value]
      } else {
        const needle = val.toLowerCase()
        produtoOptions.value = produtoOptionsOriginal.value.filter(p =>
          p.label.toLowerCase().includes(needle)
        )
      }
    })
  }

  function onProdutoSelected(produto) {
    if (produto?.value) {
      form.value.ID_PRODUTO = produto
    }
  }

  function calcularPorRefeicao() {
    if (form.value.QUANTIDADE_DIARIA && numeroRefeicoes.value) {
      form.value.QUANTIDADE_POR_REFEICAO =
        form.value.QUANTIDADE_DIARIA / numeroRefeicoes.value
    }
  }

  function calcularDiaria() {
    if (form.value.QUANTIDADE_POR_REFEICAO && numeroRefeicoes.value) {
      form.value.QUANTIDADE_DIARIA =
        form.value.QUANTIDADE_POR_REFEICAO * numeroRefeicoes.value
    }
  }

  async function submitForm() {
    try {
      loading.value = true

      // Preparar dados
      const data = { ...form.value }
      if (data.ID_PRODUTO?.value) {
        data.ID_PRODUTO = data.ID_PRODUTO.value
      }

      // Remover HORARIO_REFEICAO_* se forem strings vazias
      const horarios = [
        'HORARIO_REFEICAO_1',
        'HORARIO_REFEICAO_2',
        'HORARIO_REFEICAO_3',
        'HORARIO_REFEICAO_4',
      ]
      horarios.forEach(horario => {
        if (data[horario] === '') {
          delete data[horario]
        }
      })

      if (props.itemEdit?.ID) {
        // Atualizar item existente
        await racaoStore.updateItemPlano(props.itemEdit.ID, data)
        ErrorHandler.success('Item atualizado com sucesso!')
      } else {
        // Criar novo item
        await racaoStore.createItemPlano(props.planoInfo.ID, data)
        ErrorHandler.success('Item adicionado com sucesso!')
      }

      emit('saved')
      dialog.value = false
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao salvar item')
    } finally {
      loading.value = false
    }
  }

  function cancelar() {
    emit('cancelled')
    dialog.value = false
  }

  // Watchers
  watch(
    () => props.modelValue,
    async newVal => {
      if (newVal) {
        await loadProdutoOptions()
        await initializeForm()
      }
    }
  )

  watch(
    () => numeroRefeicoes.value,
    () => {
      if (form.value.QUANTIDADE_DIARIA) {
        calcularPorRefeicao()
      }
    }
  )
</script>
