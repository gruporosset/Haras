<template>
  <div>
    <!-- Ações Rápidas -->
    <div class="row q-gutter-md q-mb-md">
      <q-btn
        color="primary"
        label="Nova Aplicação"
        icon="medical_services"
        @click="abrirNovaAplicacao"
      />
      <q-btn
        color="secondary"
        label="Aplicação Rápida"
        icon="flash_on"
        @click="mostrarAplicacaoRapida = !mostrarAplicacaoRapida"
      />
    </div>

    <!-- Aplicação Rápida -->
    <q-slide-transition>
      <div v-show="mostrarAplicacaoRapida">
        <q-card
          flat
          bordered
          class="q-pa-md q-mb-md bg-blue-1"
        >
          <div class="text-h6 q-mb-md">Aplicação Rápida</div>

          <q-form
            @submit="aplicarRapido"
            class="q-gutter-md"
          >
            <div class="row q-gutter-md">
              <div class="col-md-3 col-12">
                <q-select
                  v-model="aplicacaoRapida.ID_ANIMAL"
                  :options="animalOptions"
                  label="Animal *"
                  use-input
                  @filter="filterAnimais"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  :rules="[val => !!val || 'Animal é obrigatório']"
                />
              </div>

              <div class="col-md-3 col-12">
                <q-select
                  v-model="aplicacaoRapida.ID_MEDICAMENTO"
                  :options="medicamentoOptions"
                  label="Medicamento *"
                  use-input
                  @filter="filterMedicamentos"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  :rules="[val => !!val || 'Medicamento é obrigatório']"
                  @update:model-value="onMedicamentoSelect"
                />
              </div>

              <div class="col-md-2 col-12">
                <q-input
                  v-model.number="aplicacaoRapida.QUANTIDADE_APLICADA"
                  label="Quantidade *"
                  type="number"
                  step="0.1"
                  :rules="[val => val > 0 || 'Quantidade obrigatória']"
                  :suffix="medicamentoSelecionado?.unidade || ''"
                />
              </div>

              <div class="col-md-2 col-12">
                <CalendarioComponent
                  v-model="aplicacaoRapida.DATA_OCORRENCIA"
                  label="Data *"
                  :rules="[val => !!val || 'Data é obrigatória']"
                />
              </div>

              <div class="col-md-2 col-12">
                <q-btn
                  type="submit"
                  color="primary"
                  label="Aplicar"
                  icon="check"
                  :loading="loading"
                  :disable="!aplicacaoRapidaValida"
                />
              </div>
            </div>

            <!-- Validação de estoque -->
            <div
              v-if="estoqueInsuficiente"
              class="text-negative q-mt-sm"
            >
              <q-icon name="warning" />
              Estoque insuficiente! Disponível: {{ estoqueDisponivel }}
            </div>
          </q-form>
        </q-card>
      </div>
    </q-slide-transition>

    <!-- Filtros -->
    <q-card
      flat
      bordered
      class="q-pa-md q-mb-md"
    >
      <div class="row q-gutter-md">
        <div class="col-md-3 col-12">
          <q-select
            v-model="filtros.animal_id"
            :options="animalOptions"
            label="Filtrar por Animal"
            clearable
            use-input
            @filter="filterAnimais"
            option-value="value"
            option-label="label"
            emit-value
            map-options
            @update:model-value="onFilterChange"
          />
        </div>

        <div class="col-md-3 col-12">
          <q-select
            v-model="filtros.medicamento_id"
            :options="medicamentoOptions"
            label="Filtrar por Medicamento"
            clearable
            use-input
            @filter="filterMedicamentos"
            option-value="value"
            option-label="label"
            emit-value
            map-options
            @update:model-value="onFilterChange"
          />
        </div>

        <div class="col-md-2 col-12">
          <CalendarioComponent
            v-model="filtros.data_inicio"
            label="Data Início"
            @update:model-value="onFilterChange"
          />
        </div>

        <div class="col-md-2 col-12">
          <CalendarioComponent
            v-model="filtros.data_fim"
            label="Data Fim"
            @update:model-value="onFilterChange"
          />
        </div>

        <div class="col-md-2 col-12">
          <q-btn
            color="primary"
            icon="search"
            @click="onFilterChange"
            style="height: 40px"
          />
        </div>
      </div>
    </q-card>

    <!-- Tabela de Aplicações -->
    <q-table
      :rows="aplicacoes"
      :columns="columns"
      row-key="ID"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      binary-state-sort
    >
      <template v-slot:body-cell-animal="props">
        <q-td :props="props">
          <div class="text-weight-medium">{{ props.row.animal_nome }}</div>
        </q-td>
      </template>

      <template v-slot:body-cell-medicamento="props">
        <q-td :props="props">
          <div class="text-weight-medium">{{ props.row.medicamento_nome }}</div>
          <div class="text-caption text-grey">
            {{ props.row.forma_farmaceutica }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-quantidade="props">
        <q-td :props="props">
          <div class="text-right">
            {{ props.row.QUANTIDADE_APLICADA }} {{ props.row.unidade_aplicada }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-veterinario="props">
        <q-td :props="props">
          {{ props.row.VETERINARIO_RESPONSAVEL || 'Não informado' }}
        </q-td>
      </template>

      <template v-slot:body-cell-proxima="props">
        <q-td :props="props">
          <div v-if="props.row.PROXIMA_APLICACAO">
            {{ formatDate(props.row.PROXIMA_APLICACAO) }}
            <q-chip
              v-if="
                getProximaAplicacaoStatus(props.row.PROXIMA_APLICACAO) !== 'ok'
              "
              :color="getProximaAplicacaoColor(props.row.PROXIMA_APLICACAO)"
              text-color="white"
              dense
              size="sm"
            >
              {{ getProximaAplicacaoLabel(props.row.PROXIMA_APLICACAO) }}
            </q-chip>
          </div>
          <div
            v-else
            class="text-grey"
          >
            Não agendada
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-acoes="props">
        <q-td :props="props">
          <q-btn
            flat
            round
            color="primary"
            icon="visibility"
            @click="visualizarAplicacao(props.row)"
            size="sm"
          >
            <q-tooltip>Visualizar</q-tooltip>
          </q-btn>
          <q-btn
            flat
            round
            color="secondary"
            icon="edit"
            @click="editarAplicacao(props.row)"
            size="sm"
          >
            <q-tooltip>Editar</q-tooltip>
          </q-btn>
          <q-btn
            flat
            round
            color="negative"
            icon="delete"
            @click="excluirAplicacao(props.row)"
            size="sm"
          >
            <q-tooltip>Excluir</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </q-table>

    <!-- Modal de Aplicação Completa -->
    <q-dialog
      v-model="aplicacaoDialog"
      persistent
    >
      <q-card style="width: 700px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6">
            {{ editandoAplicacao ? 'Editar' : 'Nova' }} Aplicação
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form
            @submit="salvarAplicacao"
            class="q-gutter-md"
          >
            <div class="row q-gutter-md">
              <div class="col-6">
                <q-select
                  v-model="formAplicacao.ID_ANIMAL"
                  :options="animalOptions"
                  label="Animal *"
                  use-input
                  @filter="filterAnimais"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  :rules="[val => !!val || 'Animal é obrigatório']"
                />
              </div>

              <div class="col-6">
                <q-select
                  v-model="formAplicacao.ID_MEDICAMENTO"
                  :options="medicamentoOptions"
                  label="Medicamento *"
                  use-input
                  @filter="filterMedicamentos"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  :rules="[val => !!val || 'Medicamento é obrigatório']"
                  @update:model-value="onMedicamentoSelectForm"
                />
              </div>
            </div>

            <div class="row q-gutter-md">
              <div class="col-4">
                <CalendarioComponent
                  v-model="formAplicacao.DATA_OCORRENCIA"
                  label="Data da Aplicação *"
                  :rules="[val => !!val || 'Data é obrigatória']"
                />
              </div>

              <div class="col-4">
                <q-input
                  v-model.number="formAplicacao.QUANTIDADE_APLICADA"
                  label="Quantidade *"
                  type="number"
                  step="0.1"
                  :rules="[val => val > 0 || 'Quantidade obrigatória']"
                  :suffix="medicamentoSelecionadoForm?.unidade || ''"
                />
              </div>

              <div class="col-4">
                <q-input
                  v-model="formAplicacao.UNIDADE_APLICADA"
                  label="Unidade"
                  readonly
                  :model-value="medicamentoSelecionadoForm?.unidade || ''"
                />
              </div>
            </div>

            <div class="row q-gutter-md">
              <div class="col-6">
                <q-input
                  v-model="formAplicacao.VETERINARIO_RESPONSAVEL"
                  label="Veterinário Responsável"
                />
              </div>

              <div class="col-6">
                <CalendarioComponent
                  v-model="formAplicacao.PROXIMA_APLICACAO"
                  label="Próxima Aplicação"
                />
              </div>
            </div>

            <q-input
              v-model="formAplicacao.DESCRICAO"
              label="Descrição"
              type="textarea"
              rows="3"
            />

            <q-input
              v-model="formAplicacao.OBSERVACOES"
              label="Observações"
              type="textarea"
              rows="3"
            />

            <!-- Validação de estoque -->
            <div
              v-if="estoqueInsuficienteForm"
              class="text-negative"
            >
              <q-icon name="warning" />
              Estoque insuficiente! Disponível: {{ estoqueDisponivelForm }}
            </div>

            <div class="row q-gutter-md q-mt-md">
              <q-btn
                type="submit"
                color="primary"
                :loading="loading"
                :disable="estoqueInsuficienteForm"
                :label="
                  editandoAplicacao
                    ? 'Salvar Alterações'
                    : 'Registrar Aplicação'
                "
              />
              <q-btn
                flat
                label="Cancelar"
                color="grey"
                @click="fecharAplicacaoDialog"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useMedicamentoStore } from 'stores/medicamento'
  import { useAnimalStore } from 'stores/animal'
  import { useAuthStore } from 'stores/auth'
  import { ErrorHandler } from 'src/utils/errorHandler'
  import { formatDate } from 'src/utils/dateUtils'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

  // Emits
  const emit = defineEmits(['aplicacao-registrada'])

  // Stores
  const medicamentoStore = useMedicamentoStore()
  const animalStore = useAnimalStore()
  const authStore = useAuthStore()

  // Estado reativo
  const loading = ref(false)
  const aplicacaoDialog = ref(false)
  const editandoAplicacao = ref(false)
  const mostrarAplicacaoRapida = ref(false)
  const aplicacoes = ref([])

  // Opções
  const animalOptions = ref([])
  const medicamentoOptions = ref([])
  const medicamentoSelecionado = ref(null)
  const medicamentoSelecionadoForm = ref(null)

  // Paginação
  const pagination = ref({
    sortBy: 'DATA_OCORRENCIA',
    descending: true,
    page: 1,
    rowsPerPage: 10,
    rowsNumber: 0,
  })

  // Filtros
  const filtros = ref({
    animal_id: null,
    medicamento_id: null,
    data_inicio: '',
    data_fim: '',
  })

  // Formulários
  const aplicacaoRapida = ref({
    ID_ANIMAL: null,
    ID_MEDICAMENTO: null,
    QUANTIDADE_APLICADA: 0,
    DATA_OCORRENCIA: '',
    ID_USUARIO_REGISTRO: authStore.user?.ID,
  })

  const formAplicacao = ref({
    ID: null,
    ID_ANIMAL: null,
    ID_MEDICAMENTO: null,
    DATA_OCORRENCIA: '',
    QUANTIDADE_APLICADA: 0,
    UNIDADE_APLICADA: '',
    VETERINARIO_RESPONSAVEL: '',
    PROXIMA_APLICACAO: '',
    DESCRICAO: '',
    OBSERVACOES: '',
    ID_USUARIO_REGISTRO: authStore.user?.ID,
  })

  // Colunas da tabela
  const columns = [
    {
      name: 'DATA_OCORRENCIA',
      label: 'Data',
      field: 'DATA_OCORRENCIA',
      sortable: true,
      align: 'left',
    },
    {
      name: 'animal',
      label: 'Animal',
      field: 'animal_nome',
      sortable: true,
      align: 'left',
    },
    {
      name: 'medicamento',
      label: 'Medicamento',
      field: 'medicamento_nome',
      sortable: true,
      align: 'left',
    },
    {
      name: 'quantidade',
      label: 'Quantidade',
      field: 'QUANTIDADE_APLICADA',
      sortable: true,
      align: 'right',
    },
    {
      name: 'veterinario',
      label: 'Veterinário',
      field: 'VETERINARIO_RESPONSAVEL',
      sortable: true,
      align: 'left',
    },
    {
      name: 'proxima',
      label: 'Próxima Aplicação',
      field: 'PROXIMA_APLICACAO',
      sortable: true,
      align: 'left',
    },
    { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' },
  ]

  // Computed
  const aplicacaoRapidaValida = computed(() => {
    return (
      aplicacaoRapida.value.ID_ANIMAL &&
      aplicacaoRapida.value.ID_MEDICAMENTO &&
      aplicacaoRapida.value.QUANTIDADE_APLICADA > 0 &&
      aplicacaoRapida.value.DATA_OCORRENCIA &&
      !estoqueInsuficiente.value
    )
  })

  const estoqueDisponivel = computed(() => {
    return medicamentoSelecionado.value?.estoque_atual || 0
  })

  const estoqueInsuficiente = computed(() => {
    return aplicacaoRapida.value.QUANTIDADE_APLICADA > estoqueDisponivel.value
  })

  const estoqueDisponivelForm = computed(() => {
    return medicamentoSelecionadoForm.value?.estoque_atual || 0
  })

  const estoqueInsuficienteForm = computed(() => {
    return formAplicacao.value.QUANTIDADE_APLICADA > estoqueDisponivelForm.value
  })

  // Métodos
  async function loadOptions() {
    try {
      // Carregar animais
      await animalStore.loadParentOptions()
      animalOptions.value = [
        ...animalStore.parentOptions.machos,
        ...animalStore.parentOptions.femeas,
      ]

      // Carregar medicamentos
      await medicamentoStore.fetchMedicamentos({ limit: 100 })
      medicamentoOptions.value = medicamentoStore.medicamentos.map(m => ({
        value: m.ID,
        label: m.NOME,
        unidade: m.UNIDADE_MEDIDA,
        estoque_atual: m.ESTOQUE_ATUAL,
      }))
    } catch (error) {
      console.error('Erro ao carregar opções:', error)
    }
  }

  async function loadAplicacoes() {
    try {
      loading.value = true
      // Implementar método no store para buscar aplicações
      aplicacoes.value = await medicamentoStore.fetchAplicacoes(filtros.value)
    } catch (error) {
      console.error('Erro ao carregar aplicações:', error)
    } finally {
      loading.value = false
    }
  }

  function filterAnimais(val, update) {
    update(() => {
      if (val === '') {
        animalOptions.value = [
          ...animalStore.parentOptions.machos,
          ...animalStore.parentOptions.femeas,
        ]
      } else {
        const needle = val.toLowerCase()
        const allAnimais = [
          ...animalStore.parentOptions.machos,
          ...animalStore.parentOptions.femeas,
        ]
        animalOptions.value = allAnimais.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  function filterMedicamentos(val, update) {
    update(() => {
      if (val === '') {
        medicamentoOptions.value = medicamentoStore.medicamentos.map(m => ({
          value: m.ID,
          label: m.NOME,
          unidade: m.UNIDADE_MEDIDA,
          estoque_atual: m.ESTOQUE_ATUAL,
        }))
      } else {
        const needle = val.toLowerCase()
        const allMedicamentos = medicamentoStore.medicamentos.map(m => ({
          value: m.ID,
          label: m.NOME,
          unidade: m.UNIDADE_MEDIDA,
          estoque_atual: m.ESTOQUE_ATUAL,
        }))
        medicamentoOptions.value = allMedicamentos.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  function onMedicamentoSelect() {
    medicamentoSelecionado.value = medicamentoOptions.value.find(
      m => m.value === aplicacaoRapida.value.ID_MEDICAMENTO
    )
  }

  function onMedicamentoSelectForm() {
    medicamentoSelecionadoForm.value = medicamentoOptions.value.find(
      m => m.value === formAplicacao.value.ID_MEDICAMENTO
    )
    if (medicamentoSelecionadoForm.value) {
      formAplicacao.value.UNIDADE_APLICADA =
        medicamentoSelecionadoForm.value.unidade
    }
  }

  async function onFilterChange() {
    await loadAplicacoes()
  }

  function onRequest(props) {
    const { page, rowsPerPage, sortBy, descending } = props.pagination
    pagination.value = { page, rowsPerPage, sortBy, descending }
    loadAplicacoes()
  }

  // Métodos de aplicação
  async function aplicarRapido() {
    try {
      loading.value = true
      await medicamentoStore.createAplicacao(aplicacaoRapida.value)
      ErrorHandler.success('Aplicação registrada com sucesso!')

      // Reset formulário
      aplicacaoRapida.value = {
        ID_ANIMAL: null,
        ID_MEDICAMENTO: null,
        QUANTIDADE_APLICADA: 0,
        DATA_OCORRENCIA: '',
        ID_USUARIO_REGISTRO: authStore.user?.ID,
      }
      medicamentoSelecionado.value = null

      emit('aplicacao-registrada')
      await loadAplicacoes()
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao registrar aplicação')
    } finally {
      loading.value = false
    }
  }

  function abrirNovaAplicacao() {
    editandoAplicacao.value = false
    formAplicacao.value = {
      ID: null,
      ID_ANIMAL: null,
      ID_MEDICAMENTO: null,
      DATA_OCORRENCIA: '',
      QUANTIDADE_APLICADA: 0,
      UNIDADE_APLICADA: '',
      VETERINARIO_RESPONSAVEL: '',
      PROXIMA_APLICACAO: '',
      DESCRICAO: '',
      OBSERVACOES: '',
      ID_USUARIO_REGISTRO: authStore.user?.ID,
    }
    aplicacaoDialog.value = true
  }

  function editarAplicacao(aplicacao) {
    editandoAplicacao.value = true
    formAplicacao.value = { ...aplicacao }
    aplicacaoDialog.value = true
  }

  function visualizarAplicacao(aplicacao) {
    // Implementar visualização se necessário
    console.log('Visualizar aplicação:', aplicacao)
  }

  function excluirAplicacao(aplicacao) {
    // Implementar exclusão se necessário
    console.log('Excluir aplicação:', aplicacao)
  }

  function fecharAplicacaoDialog() {
    aplicacaoDialog.value = false
    editandoAplicacao.value = false
    medicamentoSelecionadoForm.value = null
  }

  async function salvarAplicacao() {
    try {
      loading.value = true

      if (editandoAplicacao.value) {
        await medicamentoStore.updateAplicacao(
          formAplicacao.value.ID,
          formAplicacao.value
        )
        ErrorHandler.success('Aplicação atualizada com sucesso!')
      } else {
        await medicamentoStore.createAplicacao(formAplicacao.value)
        ErrorHandler.success('Aplicação registrada com sucesso!')
      }

      fecharAplicacaoDialog()
      emit('aplicacao-registrada')
      await loadAplicacoes()
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao salvar aplicação')
    } finally {
      loading.value = false
    }
  }

  // Funções auxiliares
  function getProximaAplicacaoStatus(data) {
    if (!data) return 'ok'

    const hoje = new Date()
    const proxima = new Date(data)
    const diffDias = Math.ceil((proxima - hoje) / (1000 * 60 * 60 * 24))

    if (diffDias < 0) return 'vencida'
    if (diffDias <= 7) return 'proxima'
    return 'ok'
  }

  function getProximaAplicacaoColor(data) {
    const status = getProximaAplicacaoStatus(data)
    const colors = {
      vencida: 'negative',
      proxima: 'warning',
      ok: 'positive',
    }
    return colors[status] || 'grey'
  }

  function getProximaAplicacaoLabel(data) {
    const status = getProximaAplicacaoStatus(data)
    const labels = {
      vencida: 'Vencida',
      proxima: 'Próxima',
      ok: 'OK',
    }
    return labels[status] || ''
  }

  // Lifecycle
  onMounted(async () => {
    await loadOptions()
    await loadAplicacoes()
  })
</script>
