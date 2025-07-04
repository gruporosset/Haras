<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md text-primary">
      <q-icon
        name="healing"
        class="q-mr-sm"
      />
      Saúde dos Animais
    </div>

    <q-card class="q-mb-md">
      <q-card-section>
        <!-- Filtros -->
        <div class="col-12">
          <q-card
            flat
            bordered
            class="q-pa-md"
          >
            <div class="row q-gutter-md">
              <div class="col-md-3 col-12">
                <q-select
                  v-model="filtros.animal_id"
                  :options="animalsOptions"
                  label="Filtrar por Animal"
                  clearable
                  use-input
                  @filter="filterAnimais"
                  @update:model-value="buscarRegistros"
                />
              </div>
              <div class="col-md-3 col-12">
                <q-select
                  v-model="filtros.tipo_registro"
                  :options="tiposRegistro"
                  clearable
                  label="Tipo"
                  @update:model-value="buscarRegistros"
                />
              </div>
              <div class="col-md-2 col-12">
                <calendario-component
                  v-model="filtros.data_inicio"
                  label="Data Início"
                  @update:model-value="buscarRegistros"
                  class="col-2"
                />
              </div>
              <div class="col-md-2 col-12">
                <calendario-component
                  v-model="filtros.data_fim"
                  label="Data Fim"
                  @update:model-value="buscarRegistros"
                  class="col-2"
                />
              </div>
            </div>
          </q-card>
        </div>

        <!-- Abas -->
        <q-tabs
          v-model="activeTab"
          class="q-mb-md"
        >
          <q-tab
            name="registros"
            label="Registros"
          />
          <q-tab
            name="calendario"
            label="Calendário"
          />
          <q-tab
            name="estatisticas"
            label="Estatísticas"
          />
          <q-tab
            name="aplicacao-rapida"
            label="Aplicação Rápida"
          />
        </q-tabs>

        <q-tab-panels
          v-model="activeTab"
          animated
        >
          <!-- ABA REGISTROS -->
          <q-tab-panel name="registros">
            <div class="row q-gutter-md">
              <!-- Botão Novo Registro -->
              <div class="col-12">
                <q-btn
                  color="primary"
                  @click="novoRegistro"
                  icon="add"
                >
                  Novo Registro de Saúde
                </q-btn>
              </div>

              <!-- Lista de Registros -->
              <div class="col-12">
                <q-card
                  flat
                  bordered
                >
                  <q-table
                    :rows="registros"
                    :columns="columns"
                    :loading="loading"
                    :pagination="pagination"
                    @request="onRequest"
                    row-key="ID"
                    flat
                    bordered
                  >
                    <template v-slot:body-cell-TIPO_REGISTRO="props">
                      <q-td :props="props">
                        <q-chip
                          :color="getTipoColor(props.value)"
                          text-color="white"
                          :label="props.value"
                          dense
                        />
                      </q-td>
                    </template>

                    <template v-slot:body-cell-status_aplicacao="props">
                      <q-td :props="props">
                        <q-chip
                          :color="getStatusColor(props.value)"
                          text-color="white"
                          :label="props.value || 'APLICADO'"
                          dense
                        />
                      </q-td>
                    </template>

                    <template v-slot:body-cell-acoes="props">
                      <q-td :props="props">
                        <q-btn
                          flat
                          round
                          color="primary"
                          icon="visibility"
                          @click="visualizarRegistro(props.row)"
                        />
                        <q-btn
                          flat
                          round
                          color="orange"
                          icon="edit"
                          @click="editarRegistro(props.row)"
                        />
                        <q-btn
                          flat
                          round
                          color="red"
                          icon="delete"
                          @click="excluirRegistro(props.row)"
                        />
                      </q-td>
                    </template>
                  </q-table>
                </q-card>
              </div>
            </div>
          </q-tab-panel>

          <!-- ABA CALENDÁRIO -->
          <q-tab-panel name="calendario">
            <div class="row q-gutter-md">
              <div class="col-12">
                <q-card
                  flat
                  bordered
                  class="q-pa-md"
                >
                  <div class="text-h6 q-mb-md">Próximos Eventos</div>
                  <q-list
                    bordered
                    separator
                    v-if="proximasAplicacoes.length"
                  >
                    <q-item
                      v-for="(aplicacao, index) in proximasAplicacoes"
                      :key="`aplicacao-${index}`"
                    >
                      <q-item-section avatar>
                        <q-avatar
                          :color="getPrioridadeColor(aplicacao.prioridade)"
                          text-color="white"
                        >
                          {{ aplicacao.dias_vencimento }}
                        </q-avatar>
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>{{ aplicacao.animal_nome }}</q-item-label>
                        <q-item-label caption>
                          {{ getLabelEvento(aplicacao) }}
                        </q-item-label>
                        <q-item-label caption>
                          {{
                            formatDateForDisplay(aplicacao.proxima_aplicacao)
                          }}
                        </q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-chip
                          :color="getPrioridadeColor(aplicacao.prioridade)"
                          text-color="white"
                          :label="aplicacao.prioridade"
                          dense
                        />
                      </q-item-section>
                    </q-item>
                  </q-list>

                  <div
                    v-else
                    class="text-center q-pa-lg text-grey-6"
                  >
                    Nenhum evento agendado para os próximos dias.
                  </div>
                </q-card>
              </div>
            </div>
          </q-tab-panel>

          <!-- ABA ESTATÍSTICAS -->
          <q-tab-panel name="estatisticas">
            <div class="row q-gutter-md">
              <!-- Resumo por Tipo -->
              <div class="col-md-6 col-12">
                <q-card
                  flat
                  bordered
                  class="q-pa-md"
                >
                  <div class="text-h6 q-mb-md">Registros por Tipo</div>
                  <canvas
                    ref="tiposChart"
                    style="max-height: 300px"
                  ></canvas>
                </q-card>
              </div>

              <!-- Consumo Mensal -->
              <div class="col-md-6 col-12">
                <q-card
                  flat
                  bordered
                  class="q-pa-md"
                >
                  <div class="text-h6 q-mb-md">Aplicações Mensais</div>
                  <canvas
                    ref="mensalChart"
                    style="max-height: 300px"
                  ></canvas>
                </q-card>
              </div>

              <!-- Top Veterinários -->
              <!-- <div class="col-12">
                  <q-card flat bordered class="q-pa-md">
                    <div class="text-h6 q-mb-md">Veterinários Mais Ativos</div>
                    <q-table
                      :rows="estatisticasVeterinarios"
                      :columns="columnsVeterinarios"
                      flat
                      hide-pagination
                      :rows-per-page-options="[0]"
                    />
                  </q-card>
                </div> -->
            </div>
          </q-tab-panel>

          <!-- ABA APLICAÇÃO RÁPIDA -->
          <q-tab-panel name="aplicacao-rapida">
            <div class="row q-gutter-md">
              <div class="col-md-8 col-12">
                <q-card
                  flat
                  bordered
                  class="q-pa-md"
                >
                  <div class="text-h6 q-mb-md">Aplicação Rápida</div>

                  <q-form
                    @submit="aplicarRapido"
                    class="q-gutter-md"
                  >
                    <div class="row q-gutter-md">
                      <div class="col-md-6 col-12">
                        <q-select
                          v-model="aplicacaoRapida.ID_ANIMAL"
                          :options="animalsOptions"
                          option-value="value"
                          option-label="label"
                          emit-value
                          map-options
                          label="Animal *"
                          dense
                          :rules="[val => !!val || 'Animal é obrigatório']"
                        />
                      </div>
                      <div class="col-md-6 col-12">
                        <q-select
                          v-model="aplicacaoRapida.TIPO_REGISTRO"
                          :options="tiposRegistro"
                          label="Tipo *"
                          dense
                          :rules="[val => !!val || 'Tipo é obrigatório']"
                        />
                      </div>
                    </div>

                    <div class="row q-gutter-md">
                      <div class="col-md-6 col-12">
                        <q-select
                          v-model="aplicacaoRapida.ID_MEDICAMENTO"
                          :options="medicamentosEstoque"
                          option-value="value"
                          option-label="label"
                          emit-value
                          map-options
                          use-input
                          @filter="buscarMedicamentos"
                          label="Medicamento (estoque)"
                          dense
                          clearable
                        />
                      </div>
                      <div class="col-md-3 col-12">
                        <q-input
                          v-model.number="aplicacaoRapida.QUANTIDADE_APLICADA"
                          type="number"
                          step="0.1"
                          label="Quantidade"
                          dense
                        />
                      </div>
                    </div>

                    <div class="row q-gutter-md">
                      <div class="col-md-6 col-12">
                        <q-input
                          v-model="aplicacaoRapida.VETERINARIO_RESPONSAVEL"
                          label="Veterinário"
                          dense
                        />
                      </div>
                    </div>

                    <q-input
                      v-model="aplicacaoRapida.OBSERVACOES"
                      type="textarea"
                      label="Observações"
                      rows="3"
                    />

                    <div class="text-right">
                      <q-btn
                        type="submit"
                        color="primary"
                        :loading="loadingAplicacao"
                      >
                        <q-icon
                          name="flash_on"
                          class="q-mr-xs"
                        />
                        Aplicar Agora
                      </q-btn>
                    </div>
                  </q-form>
                </q-card>
              </div>
            </div>
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>
    </q-card>
    <!-- Modal de Novo/Editar Registro -->
    <q-dialog
      v-model="modalRegistro"
      persistent
    >
      <q-card style="min-width: 800px">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">
            {{ editandoRegistro ? 'Editar' : 'Novo' }} Registro de Saúde
          </div>
          <q-space />
          <q-btn
            icon="close"
            flat
            round
            dense
            v-close-popup
          />
        </q-card-section>

        <q-card-section>
          <q-form
            @submit="salvarRegistro"
            class="q-gutter-md"
          >
            <div class="row q-gutter-md">
              <div class="col-md-6 col-12">
                <q-select
                  v-model="formRegistro.ID_ANIMAL"
                  :options="animalsOptions"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  label="Animal *"
                  :rules="[val => !!val || 'Animal é obrigatório']"
                />
              </div>
              <div class="col-md-6 col-12">
                <q-select
                  v-model="formRegistro.TIPO_REGISTRO"
                  :options="tiposRegistro"
                  label="Tipo *"
                  :rules="[val => !!val || 'Tipo é obrigatório']"
                />
              </div>
            </div>

            <div class="row q-gutter-md">
              <div class="col-md-6 col-12">
                <CalendarioComponent
                  v-model="formRegistro.DATA_OCORRENCIA"
                  label="Data da Ocorrência *"
                  :rules="[
                    val => !!val || 'Data é obrigatória',
                    val =>
                      (val && new Date(convertToISO(val)) <= new Date()) ||
                      'Data não pode ser futura',
                  ]"
                />
              </div>
              <div class="col-md-6 col-12">
                <CalendarioComponent
                  v-if="formRegistro.TIPO_REGISTRO"
                  v-model="formRegistro.PROXIMA_APLICACAO"
                  :label="getProximoLabel(formRegistro.TIPO_REGISTRO)"
                />
              </div>
            </div>

            <q-input
              v-model="formRegistro.DESCRICAO"
              label="Descrição"
              type="textarea"
              rows="2"
            />

            <div class="row q-gutter-md">
              <div class="col-md-6 col-12">
                <q-input
                  v-model="formRegistro.VETERINARIO_RESPONSAVEL"
                  label="Veterinário Responsável"
                />
              </div>
              <div class="col-md-6 col-12">
                <q-input
                  v-model.number="formRegistro.CUSTO"
                  type="number"
                  step="0.01"
                  label="Custo (R$)"
                  prefix="R$"
                />
              </div>
            </div>

            <!-- Medicamento do Estoque -->
            <q-separator />
            <div class="text-subtitle2 q-mt-md">
              Medicamento do Estoque (opcional)
            </div>

            <div class="row q-gutter-md">
              <div class="col-md-6 col-12">
                <q-select
                  v-model="formRegistro.ID_MEDICAMENTO"
                  :options="medicamentosEstoque"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  use-input
                  @filter="buscarMedicamentos"
                  label="Medicamento"
                  clearable
                />
              </div>
              <div class="col-md-3 col-12">
                <q-input
                  v-model.number="formRegistro.QUANTIDADE_APLICADA"
                  type="number"
                  step="0.1"
                  label="Quantidade"
                />
              </div>
              <div class="col-md-3 col-12">
                <q-input
                  v-model="formRegistro.UNIDADE_APLICADA"
                  label="Unidade"
                />
              </div>
            </div>

            <q-input
              v-model="formRegistro.OBSERVACOES"
              label="Observações"
              type="textarea"
              rows="3"
            />

            <div class="text-right q-mt-md">
              <q-btn
                flat
                label="Cancelar"
                v-close-popup
                class="q-mr-sm"
              />
              <q-btn
                type="submit"
                color="primary"
                :loading="loading"
              >
                {{ editandoRegistro ? 'Atualizar' : 'Salvar' }}
              </q-btn>
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Modal de Visualização -->
    <q-dialog v-model="modalVisualizacao">
      <q-card style="min-width: 600px">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Detalhes do Registro</div>
          <q-space />
          <q-btn
            icon="close"
            flat
            round
            dense
            v-close-popup
          />
        </q-card-section>

        <q-card-section v-if="registroSelecionado">
          <div class="q-gutter-sm">
            <q-chip
              color="primary"
              text-color="white"
              :label="registroSelecionado.TIPO_REGISTRO"
            />

            <div class="row q-gutter-md q-mt-md">
              <div class="col-6">
                <strong>Animal:</strong>
                {{ registroSelecionado.animal_nome }}
              </div>
              <div class="col-6">
                <strong>Data:</strong>
                {{ registroSelecionado.DATA_OCORRENCIA }}
              </div>
            </div>

            <div
              class="row q-gutter-md"
              v-if="registroSelecionado.VETERINARIO_RESPONSAVEL"
            >
              <div class="col-12">
                <strong>Veterinário:</strong>
                {{ registroSelecionado.VETERINARIO_RESPONSAVEL }}
              </div>
            </div>

            <div
              class="row q-gutter-md"
              v-if="registroSelecionado.DESCRICAO"
            >
              <div class="col-12">
                <strong>Descrição:</strong>
                {{ registroSelecionado.DESCRICAO }}
              </div>
            </div>

            <div
              class="row q-gutter-md"
              v-if="registroSelecionado.MEDICAMENTO_APLICADO"
            >
              <div class="col-6">
                <strong>Medicamento:</strong>
                {{ registroSelecionado.MEDICAMENTO_APLICADO }}
              </div>
              <div
                class="col-6"
                v-if="registroSelecionado.DOSE_APLICADA"
              >
                <strong>Dose:</strong>
                {{ registroSelecionado.DOSE_APLICADA }}
              </div>
            </div>

            <div
              class="row q-gutter-md"
              v-if="registroSelecionado.CUSTO"
            >
              <div class="col-6">
                <strong>Custo:</strong>
                R$ {{ registroSelecionado.CUSTO.toFixed(2) }}
              </div>
            </div>

            <div
              class="row q-gutter-md"
              v-if="registroSelecionado.PROXIMA_APLICACAO"
            >
              <div class="col-12">
                <strong>
                  {{ getProximoLabel(registroSelecionado.TIPO_REGISTRO) }}
                </strong>
                {{ registroSelecionado.PROXIMA_APLICACAO }}
              </div>
            </div>

            <div
              class="row q-gutter-md"
              v-if="registroSelecionado.OBSERVACOES"
            >
              <div class="col-12">
                <strong>Observações:</strong>
                {{ registroSelecionado.OBSERVACOES }}
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
  import { ref, onMounted, nextTick, watch } from 'vue'
  import { useQuasar } from 'quasar'
  import { useSaudeStore } from 'stores/saude'
  import { useAnimalStore } from 'stores/animal'
  import { useMedicamentoStore } from 'src/stores/medicamento'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'
  import Chart from 'chart.js/auto'
  import { ErrorHandler } from 'src/utils/errorHandler'
  import { convertToISO, formatDateForDisplay } from 'src/utils/dateUtils'

  const $q = useQuasar()
  const saudeStore = useSaudeStore()
  const animalStore = useAnimalStore()
  const medicamentoStore = useMedicamentoStore()

  // Refs
  const activeTab = ref('registros')
  const loading = ref(false)
  const loadingAplicacao = ref(false)
  const modalRegistro = ref(false)
  const modalVisualizacao = ref(false)
  const editandoRegistro = ref(false)
  const registroSelecionado = ref(null)
  const tiposChart = ref(null)
  const mensalChart = ref(null)

  // Dados
  const registros = ref([])
  const animalsOptions = ref([])
  const medicamentosEstoque = ref([])
  const proximasAplicacoes = ref([])
  const estatisticasVeterinarios = ref([])

  // Filtros
  const filtros = ref({
    animal_id: null,
    tipo_registro: null,
    data_inicio: null,
    data_fim: null,
  })

  // Paginação
  const pagination = ref({
    sortBy: 'DATA_OCORRENCIA',
    descending: true,
    page: 1,
    rowsPerPage: 10,
    rowsNumber: 0,
  })

  // Formulários
  const formRegistro = ref({
    ID_ANIMAL: null,
    TIPO_REGISTRO: null,
    DATA_OCORRENCIA: null,
    DESCRICAO: '',
    VETERINARIO_RESPONSAVEL: '',
    MEDICAMENTO_APLICADO: '',
    DOSE_APLICADA: '',
    PROXIMA_APLICACAO: null,
    CUSTO: null,
    OBSERVACOES: '',
    ID_MEDICAMENTO: null,
    QUANTIDADE_APLICADA: null,
    UNIDADE_APLICADA: '',
  })

  const aplicacaoRapida = ref({
    ID_ANIMAL: null,
    TIPO_REGISTRO: null,
    ID_MEDICAMENTO: null,
    QUANTIDADE_APLICADA: null,
    MEDICAMENTO_APLICADO: '',
    DOSE_APLICADA: '',
    VETERINARIO_RESPONSAVEL: '',
    OBSERVACOES: '',
  })

  // Opções

  const tiposRegistro = [
    { value: 'VACINA', label: 'Vacina', genero: 'feminino' },
    { value: 'VERMIFUGO', label: 'Vermífugo', genero: 'masculino' },
    { value: 'MEDICAMENTO', label: 'Medicamento', genero: 'masculino' },
    { value: 'EXAME', label: 'Exame', genero: 'masculino' },
    { value: 'CONSULTA', label: 'Consulta', genero: 'feminino' },
    { value: 'CIRURGIA', label: 'Cirurgia', genero: 'feminino' },
    { value: 'TRATAMENTO', label: 'Tratamento', genero: 'masculino' },
  ]

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
      name: 'animal_nome',
      label: 'Animal',
      field: 'animal_nome',
      sortable: true,
      align: 'left',
    },
    {
      name: 'TIPO_REGISTRO',
      label: 'Tipo',
      field: 'TIPO_REGISTRO',
      sortable: true,
      align: 'center',
    },
    {
      name: 'MEDICAMENTO_APLICADO',
      label: 'Medicamento',
      field: 'MEDICAMENTO_APLICADO',
      align: 'left',
    },
    {
      name: 'VETERINARIO_RESPONSAVEL',
      label: 'Veterinário',
      field: 'VETERINARIO_RESPONSAVEL',
      align: 'left',
    },
    {
      name: 'CUSTO',
      label: 'Custo',
      field: 'CUSTO',
      format: val => (val ? `R$ ${val.toFixed(2)}` : ''),
      align: 'right',
    },
    {
      name: 'status_aplicacao',
      label: 'Status',
      field: 'status_aplicacao',
      align: 'center',
    },
    {
      name: 'PROXIMA_APLICACAO',
      label: 'Próxima Aplicação',
      field: 'PROXIMA_APLICACAO',
      align: 'left',
      sortable: true,
    },
    { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' },
  ]

  // Métodos
  const buscarRegistros = async () => {
    loading.value = true
    try {
      const params = {
        page: pagination.value.page,
        limit: pagination.value.rowsPerPage,
        ...filtros.value,
      }

      const response = await saudeStore.fetchRegistros(params)
      registros.value = response.registros
      pagination.value.rowsNumber = response.total
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao buscar registros')
    } finally {
      loading.value = false
    }
  }

  const onRequest = props => {
    pagination.value = props.pagination
    buscarRegistros()
  }

  const carregarAnimais = async () => {
    try {
      await animalStore.fetchAnimais({ limit: 100 })
      animalsOptions.value = animalStore.animais.map(animal => ({
        value: animal.ID,
        label: `${animal.NOME} - ${animal.NUMERO_REGISTRO || 'S/N'}`,
      }))
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar animais')
    }
  }

  const carregarMedicamentos = async () => {
    try {
      // Carregar todos os medicamentos ativos com estoque > 0 uma única vez
      const response = await medicamentoStore.autocompleteMedicamentos('')
      console.log(response)
      medicamentosEstoque.value = response.map(med => ({
        value: med.value,
        label: `${med.label} - Estoque: ${med.estoque} ${med.unidade}`,
        nome: med.label,
        estoque: med.estoque,
        unidade: med.unidade,
      }))
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar medicamentos')
      medicamentosEstoque.value = []
    }
  }

  const buscarMedicamentos = async (val, update) => {
    // Filtro local - não faz chamada para o backend
    update(() => {
      if (val === '') {
        carregarMedicamentos()
      } else {
        // Filtrar localmente pelos medicamentos já carregados
        const needle = val.toLowerCase()
        medicamentosEstoque.value = medicamentosEstoque.value.filter(
          med =>
            med.label.toLowerCase().indexOf(needle) > -1 ||
            med.nome.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  const carregarProximasAplicacoes = async () => {
    try {
      proximasAplicacoes.value = await saudeStore.fetchProximasAplicacoes()
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar próximas aplicações')
    }
  }

  const carregarEstatisticas = async () => {
    try {
      const [tiposData, veterinariosData, aplicacoesMensais] =
        await Promise.all([
          saudeStore.consumoPorTipo(),
          saudeStore.estatisticasVeterinarios(),
          saudeStore.aplicacoesMensais(6),
        ])

      estatisticasVeterinarios.value = veterinariosData

      // Renderizar gráficos
      nextTick(() => {
        renderTiposChart(tiposData)
        renderMensalChart(aplicacoesMensais)
      })
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar estatísticas')
    }
  }

  const renderTiposChart = data => {
    if (!tiposChart.value) return

    new Chart(tiposChart.value, {
      type: 'doughnut',
      data: {
        labels: data.map(item => item.tipo_registro),
        datasets: [
          {
            data: data.map(item => item.total_aplicacoes),
            backgroundColor: [
              '#1976D2',
              '#388E3C',
              '#F57C00',
              '#D32F2F',
              '#7B1FA2',
              '#00796B',
              '#FBC02D',
              '#455A64',
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

  const renderMensalChart = dadosMensais => {
    if (!mensalChart.value) return

    // Se não houver dados, não renderizar o gráfico
    if (!dadosMensais || dadosMensais.length === 0) {
      // Criar gráfico vazio com mensagem
      new Chart(mensalChart.value, {
        type: 'line',
        data: {
          labels: ['Sem dados'],
          datasets: [
            {
              label: 'Aplicações',
              data: [0],
              borderColor: '#1976D2',
              backgroundColor: 'rgba(25, 118, 210, 0.1)',
              tension: 0.4,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
            },
          },
          plugins: {
            title: {
              display: true,
              text: 'Nenhum dado encontrado',
            },
          },
        },
      })
      return
    }

    // Usar dados reais do banco
    const labels = dadosMensais.map(item => item.periodo)
    const dados = dadosMensais.map(item => item.total_aplicacoes)

    new Chart(mensalChart.value, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Aplicações',
            data: dados,
            borderColor: '#1976D2',
            backgroundColor: 'rgba(25, 118, 210, 0.1)',
            tension: 0.4,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    })
  }

  const novoRegistro = () => {
    editandoRegistro.value = false
    formRegistro.value = {
      ID_ANIMAL: null,
      TIPO_REGISTRO: null,
      DATA_OCORRENCIA: null,
      DESCRICAO: '',
      VETERINARIO_RESPONSAVEL: '',
      MEDICAMENTO_APLICADO: '',
      DOSE_APLICADA: '',
      PROXIMA_APLICACAO: null,
      CUSTO: null,
      OBSERVACOES: '',
      ID_MEDICAMENTO: null,
      QUANTIDADE_APLICADA: null,
      UNIDADE_APLICADA: '',
    }
    modalRegistro.value = true
  }

  const editarRegistro = registro => {
    editandoRegistro.value = true
    formRegistro.value = { ...registro }
    modalRegistro.value = true
  }

  const salvarRegistro = async () => {
    loading.value = true
    try {
      if (editandoRegistro.value) {
        await saudeStore.updateRegistro(
          formRegistro.value.ID,
          formRegistro.value
        )
        ErrorHandler.success('Registro atualizado com sucesso!')
      } else {
        await saudeStore.createRegistro(formRegistro.value)

        ErrorHandler.success('Registro criado com sucesso!')
      }

      modalRegistro.value = false
      buscarRegistros()
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao salvar registro')
    } finally {
      loading.value = false
    }
  }

  const visualizarRegistro = registro => {
    registroSelecionado.value = registro
    modalVisualizacao.value = true
  }

  const excluirRegistro = registro => {
    $q.dialog({
      title: 'Confirmar exclusão',
      message: `Deseja realmente excluir este registro de ${registro.TIPO_REGISTRO}?`,
      cancel: true,
      persistent: true,
    }).onOk(async () => {
      try {
        await saudeStore.deleteRegistro(registro.ID)
        ErrorHandler.success('Registro excluído com sucesso!')
        buscarRegistros()
      } catch (error) {
        ErrorHandler.handle(error, 'Erro ao excluir registro')
      }
    })
  }

  const aplicarRapido = async () => {
    loadingAplicacao.value = true
    try {
      await saudeStore.aplicacaoRapida(aplicacaoRapida.value)
      ErrorHandler.success('Aplicação registrada com sucesso!')

      // Limpar formulário
      aplicacaoRapida.value = {
        ID_ANIMAL: null,
        TIPO_REGISTRO: null,
        ID_MEDICAMENTO: null,
        QUANTIDADE_APLICADA: null,
        MEDICAMENTO_APLICADO: '',
        DOSE_APLICADA: '',
        VETERINARIO_RESPONSAVEL: '',
        OBSERVACOES: '',
      }

      // Atualizar lista se estiver na aba registros
      if (activeTab.value === 'registros') {
        buscarRegistros()
      }
    } catch (error) {
      ErrorHandler.handle(error, 'Erro na aplicação')
    } finally {
      loadingAplicacao.value = false
    }
  }

  // Helpers para cores
  const getTipoColor = tipo => {
    const cores = {
      VACINA: 'green',
      VERMIFUGO: 'orange',
      MEDICAMENTO: 'blue',
      EXAME: 'purple',
      CONSULTA: 'teal',
      CIRURGIA: 'red',
      TRATAMENTO: 'indigo',
    }
    return cores[tipo] || 'grey'
  }

  const getStatusColor = status => {
    const cores = {
      PENDENTE: 'orange',
      APLICADO: 'green',
      ATRASADO: 'red',
    }
    return cores[status] || 'green'
  }

  const getPrioridadeColor = prioridade => {
    const cores = {
      URGENTE: 'red',
      NORMAL: 'orange',
      BAIXA: 'green',
    }
    return cores[prioridade] || 'grey'
  }

  const getProximoLabel = tipo => {
    if (typeof tipo === 'string') {
      tipo = tiposRegistro.find(t => t.value === tipo)
    }

    const label = tipo.genero === 'masculino' ? 'Próximo' : 'Próxima'
    return `${label} ${tipo.label}`
  }

  const getLabelEvento = aplicacao => {
    return `${aplicacao.tipo_registro}: ${aplicacao.descricao}`
  }

  function filterAnimais(val, update) {
    update(() => {
      if (val === '') {
        animalsOptions.value = animalStore.animais.map(a => ({
          value: a.ID,
          label: a.NOME,
        }))
      } else {
        const needle = val.toLowerCase()
        const allAnimais = animalStore.animais.map(a => ({
          value: a.ID,
          label: a.NOME,
        }))
        animalsOptions.value = allAnimais.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  // Watchers
  const watchActiveTab = () => {
    if (activeTab.value === 'calendario') {
      carregarProximasAplicacoes()
    } else if (activeTab.value === 'estatisticas') {
      carregarEstatisticas()
    }
  }

  // Lifecycle
  onMounted(() => {
    carregarAnimais()
    carregarMedicamentos()
    buscarRegistros()
  })

  watch(activeTab, watchActiveTab)
</script>
