<template>
  <div class="produtos-manejo-container">
    <!-- HEADER COM FILTROS -->
    <q-card
      flat
      class="q-mb-md"
    >
      <q-card-section>
        <div class="row q-gutter-md items-end">
          <div class="col-md-3 col-12">
            <q-input
              v-model="filtros.nome"
              label="Buscar por nome"
              dense
              clearable
              @update:model-value="onFilterChange"
              debounce="300"
            >
              <template v-slot:prepend>
                <q-icon name="search" />
              </template>
            </q-input>
          </div>

          <div class="col-md-2 col-12">
            <q-select
              v-model="filtros.tipo_produto"
              :options="manejoStore.tiposProduto"
              label="Tipo de Produto"
              dense
              clearable
              @update:model-value="onFilterChange"
            />
          </div>

          <div class="col-md-2 col-12">
            <q-toggle
              v-model="filtros.estoque_baixo"
              label="Apenas estoque baixo"
              @update:model-value="onFilterChange"
            />
          </div>

          <div class="col-md-2 col-12">
            <q-select
              v-model="filtros.ativo"
              :options="[
                { label: 'Ativos', value: 'S' },
                { label: 'Inativos', value: 'N' },
                { label: 'Todos', value: '' },
              ]"
              label="Status"
              clearable
              dense
              @update:model-value="onFilterChange"
            />
          </div>
        </div>

        <div class="row q-gutter-md items-end q-mt-sm">
          <div class="col-auto">
            <q-btn
              color="primary"
              icon="add"
              label="Novo Produto"
              @click="openDialog(null)"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- ALERTAS DE ESTOQUE -->
    <q-card
      v-if="alertasEstoque.length > 0"
      flat
      class="bg-orange-1 q-mb-md"
    >
      <q-card-section>
        <div class="text-h6 text-orange-8 q-mb-sm">
          <q-icon
            name="warning"
            class="q-mr-sm"
          />
          Alertas de Estoque ({{ alertasEstoque.length }})
        </div>
        <div class="row q-gutter-sm">
          <q-chip
            v-for="alerta in alertasEstoque.slice(0, 5)"
            :key="alerta.produto_id"
            :color="getCorAlerta(alerta.status_alerta)"
            text-color="white"
            size="sm"
            @click="viewProduto(alerta.produto_id)"
            clickable
          >
            {{ alerta.nome }} - {{ alerta.estoque_atual }}
            {{ alerta.unidade_medida }}
          </q-chip>
          <q-btn
            v-if="alertasEstoque.length > 5"
            flat
            color="orange"
            size="sm"
            :label="`+${alertasEstoque.length - 5} mais`"
            @click="showAllAlertas"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- TABELA DE PRODUTOS -->
    <q-table
      :rows="manejoStore.produtos"
      :columns="columns"
      row-key="ID"
      :loading="manejoStore.loading"
      :pagination="manejoStore.pagination"
      @request="onRequest"
      binary-state-sort
      flat
      class="produtos-table"
    >
      <template v-slot:body-cell-TIPO_PRODUTO="props">
        <q-td :props="props">
          <q-chip
            :color="getCorTipo(props.value)"
            text-color="white"
            size="sm"
          >
            {{ manejoStore.getTipoLabel(props.value) }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-estoque="props">
        <q-td :props="props">
          <div class="text-weight-medium">
            {{ props.row.ESTOQUE_ATUAL || 0 }} {{ props.row.UNIDADE_MEDIDA }}
          </div>
          <div class="text-caption">
            Mín: {{ props.row.ESTOQUE_MINIMO || 0 }}
          </div>
          <q-linear-progress
            :value="getPercentualEstoque(props.row)"
            :color="getCorEstoque(props.row)"
            size="4px"
            class="q-mt-xs"
          />
        </q-td>
      </template>

      <template v-slot:body-cell-status_estoque="props">
        <q-td :props="props">
          <q-chip
            :color="getCorStatusEstoque(props.row.status_estoque)"
            text-color="white"
            size="sm"
          >
            {{ getStatusEstoqueLabel(props.row.status_estoque) }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-ATIVO="props">
        <q-td :props="props">
          <q-chip
            :color="props.value === 'S' ? 'positive' : 'negative'"
            text-color="white"
            size="sm"
          >
            {{ props.value === 'S' ? 'Ativo' : 'Inativo' }}
          </q-chip>
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
              @click="viewProduto(props.row)"
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
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">
            {{ form.ID ? 'Editar Produto' : 'Novo Produto' }}
          </div>
        </q-card-section>

        <q-card-section>
          <q-form
            @submit="submitForm"
            class="q-gutter-md"
          >
            <!-- Linha 1: Nome, Tipo, Unidade -->
            <div class="row q-gutter-md">
              <q-input
                v-model="form.NOME"
                label="Nome *"
                :rules="[val => !!val || 'Nome é obrigatório']"
                class="col-5"
              />
              <q-select
                v-model="form.TIPO_PRODUTO"
                :options="manejoStore.tiposProduto"
                label="Tipo *"
                :rules="[val => !!val || 'Tipo é obrigatório']"
                class="col-3"
              />
              <q-input
                v-model="form.UNIDADE_MEDIDA"
                label="Unidade *"
                :rules="[val => !!val || 'Unidade é obrigatória']"
                class="col-3"
              />
            </div>

            <!-- Linha 2: Princípio Ativo, Concentração, Fabricante -->
            <div class="row q-gutter-md">
              <q-input
                v-model="form.PRINCIPIO_ATIVO"
                label="Princípio Ativo"
                class="col-5"
              />
              <q-input
                v-model="form.CONCENTRACAO"
                label="Concentração"
                class="col-3"
              />
              <q-input
                v-model="form.FABRICANTE"
                label="Fabricante"
                class="col-3"
              />
            </div>

            <!-- Linha 3: Estoque -->
            <div class="row q-gutter-md">
              <q-input
                v-model.number="form.ESTOQUE_ATUAL"
                label="Estoque Atual"
                type="number"
                step="0.01"
                min="0"
                readonly
                :hint="
                  form.ID
                    ? 'Use os botões ao lado para ajustar o estoque'
                    : 'Será definido após criação'
                "
                class="col-auto"
              >
                <template
                  v-slot:append
                  v-if="form.ID"
                >
                  <q-btn-group flat>
                    <q-btn
                      icon="add_box"
                      color="positive"
                      flat
                      round
                      size="sm"
                      @click="openMovimentacaoDialog('ENTRADA')"
                    >
                      <q-tooltip>Entrada de Estoque</q-tooltip>
                    </q-btn>
                    <q-btn
                      icon="remove_circle_outline"
                      color="negative"
                      flat
                      round
                      size="sm"
                      @click="openMovimentacaoDialog('SAIDA')"
                    >
                      <q-tooltip>Saída de Estoque</q-tooltip>
                    </q-btn>
                    <q-btn
                      icon="tune"
                      color="warning"
                      flat
                      round
                      size="sm"
                      @click="openMovimentacaoDialog('AJUSTE')"
                    >
                      <q-tooltip>Ajustar Estoque</q-tooltip>
                    </q-btn>
                  </q-btn-group>
                </template>
              </q-input>
            </div>

            <div class="row q-gutter-md">
              <q-input
                v-model.number="form.ESTOQUE_MINIMO"
                label="Estoque Mínimo *"
                type="number"
                step="0.01"
                min="0"
                :rules="[val => val >= 0 || 'Deve ser maior ou igual a 0']"
                class="col-auto"
              />
              <q-input
                v-model.number="form.ESTOQUE_MAXIMO"
                label="Estoque Máximo"
                type="number"
                step="0.01"
                min="0"
                class="col-auto"
              />
              <q-input
                v-model.number="form.PRECO_UNITARIO"
                label="Preço Unitário"
                type="number"
                step="0.01"
                min="0"
                prefix="R$"
                class="col-auto"
              />
            </div>

            <!-- Linha 4: Fornecedor e Aplicação -->
            <div class="row q-gutter-md">
              <q-input
                v-model="form.FORNECEDOR_PRINCIPAL"
                label="Fornecedor Principal"
                class="col-4"
              />
              <q-input
                v-model="form.CODIGO_FORNECEDOR"
                label="Código do Fornecedor"
                class="col-3"
              />
              <q-input
                v-model.number="form.DOSE_RECOMENDADA"
                label="Dose Recomendada (por HA)"
                type="number"
                step="0.01"
                min="0"
                class="col-2"
              />
              <q-input
                v-model.number="form.PERIODO_CARENCIA"
                label="Carência (dias)"
                type="number"
                min="0"
                class="col-2"
              />
            </div>

            <!-- Linha 5: Validade e Lote -->
            <div class="row q-gutter-md">
              <q-input
                v-model="form.LOTE_ATUAL"
                label="Lote Atual"
                class="col-3"
              />
              <calendario-component
                v-model="form.DATA_VALIDADE"
                label="Data de Validade"
                class="col-3"
              />
              <q-input
                v-model="form.LOCAL_ARMAZENAMENTO"
                label="Local de Armazenamento"
                class="col-5"
              />
            </div>

            <!-- Linha 6: Registro e Receituário -->
            <div class="row q-gutter-md">
              <q-input
                v-model="form.REGISTRO_MINISTERIO"
                label="Registro MAPA/ANVISA"
                class="col-4"
              />
              <q-toggle
                v-model="requiresReceita"
                label="Requer Receituário"
                class="col-3"
              />
              <q-input
                v-model="form.CONDICOES_ARMAZENAMENTO"
                label="Condições de Armazenamento"
                class="col-4"
              />
            </div>

            <!-- Observações -->
            <q-input
              v-model="form.OBSERVACOES"
              label="Observações"
              type="textarea"
              rows="3"
            />
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
            :loading="manejoStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG VISUALIZAÇÃO -->
    <q-dialog v-model="viewDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">{{ viewData?.NOME }}</div>
        </q-card-section>

        <q-card-section>
          <q-list>
            <q-item>
              <q-item-section>
                <q-item-label caption>Tipo</q-item-label>
                <q-item-label>
                  {{ manejoStore.getTipoLabel(viewData?.TIPO_PRODUTO) }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Estoque Atual</q-item-label>
                <q-item-label>
                  {{ viewData?.ESTOQUE_ATUAL || 0 }}
                  {{ viewData?.UNIDADE_MEDIDA }}
                </q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Estoque Mínimo</q-item-label>
                <q-item-label>
                  {{ viewData?.ESTOQUE_MINIMO || 0 }}
                  {{ viewData?.UNIDADE_MEDIDA }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.PRINCIPIO_ATIVO">
              <q-item-section>
                <q-item-label caption>Princípio Ativo</q-item-label>
                <q-item-label>{{ viewData.PRINCIPIO_ATIVO }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.FABRICANTE">
              <q-item-section>
                <q-item-label caption>Fabricante</q-item-label>
                <q-item-label>{{ viewData.FABRICANTE }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.DOSE_RECOMENDADA">
              <q-item-section>
                <q-item-label caption>Dose Recomendada (por HA)</q-item-label>
                <q-item-label>
                  {{ viewData.DOSE_RECOMENDADA }}
                  {{ viewData.UNIDADE_MEDIDA }}/HA
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.PERIODO_CARENCIA">
              <q-item-section>
                <q-item-label caption>Período de Carência</q-item-label>
                <q-item-label>
                  {{ viewData.PERIODO_CARENCIA }} dias
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="viewData?.OBSERVACOES">
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
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG MOVIMENTAÇÃO DE ESTOQUE -->
    <q-dialog
      v-model="movimentacaoDialog"
      persistent
    >
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">
            {{ getTituloMovimentacao(tipoMovimentacao) }}
          </div>
          <div class="text-subtitle2 text-grey-6">Produto: {{ form.NOME }}</div>
        </q-card-section>

        <q-card-section>
          <q-form
            @submit="submitMovimentacao"
            class="q-gutter-md"
          >
            <!-- ENTRADA -->
            <template v-if="tipoMovimentacao === 'ENTRADA'">
              <div class="row q-gutter-md">
                <q-input
                  v-model.number="movimentacaoForm.QUANTIDADE"
                  label="Quantidade *"
                  type="number"
                  step="0.01"
                  min="0.01"
                  :suffix="form.UNIDADE_MEDIDA"
                  :rules="[val => val > 0 || 'Quantidade deve ser maior que 0']"
                  class="col-5"
                />
                <q-input
                  v-model="movimentacaoForm.NOTA_FISCAL"
                  label="Nota Fiscal *"
                  :rules="[val => !!val || 'Nota fiscal é obrigatória']"
                  class="col-6"
                />
              </div>

              <div class="row q-gutter-md">
                <q-input
                  v-model="movimentacaoForm.FORNECEDOR"
                  label="Fornecedor *"
                  :rules="[val => !!val || 'Fornecedor é obrigatório']"
                  class="col-5"
                />
                <q-input
                  v-model.number="movimentacaoForm.PRECO_UNITARIO"
                  label="Preço Unitário *"
                  type="number"
                  step="0.01"
                  min="0"
                  prefix="R$"
                  :rules="[
                    val => val >= 0 || 'Preço deve ser maior ou igual a 0',
                  ]"
                  class="col-3"
                />
                <q-input
                  v-model="movimentacaoForm.LOTE"
                  label="Lote *"
                  :rules="[val => !!val || 'Lote é obrigatório']"
                  class="col-3"
                />
              </div>

              <div class="row q-gutter-md">
                <calendario-component
                  v-model="movimentacaoForm.DATA_FABRICACAO"
                  label="Data de Fabricação"
                  class="col-6"
                />

                <calendario-component
                  v-model="movimentacaoForm.DATA_VALIDADE"
                  label="Data de Validade"
                  class="col-5"
                />
              </div>
            </template>

            <!-- SAÍDA -->
            <template v-if="tipoMovimentacao === 'SAIDA'">
              <div class="row q-gutter-md">
                <q-input
                  v-model.number="movimentacaoForm.QUANTIDADE"
                  label="Quantidade *"
                  type="number"
                  step="0.01"
                  min="0.01"
                  :max="form.ESTOQUE_ATUAL"
                  :suffix="form.UNIDADE_MEDIDA"
                  :rules="[
                    val => val > 0 || 'Quantidade deve ser maior que 0',
                    val =>
                      val <= form.ESTOQUE_ATUAL ||
                      `Máximo disponível: ${form.ESTOQUE_ATUAL}`,
                  ]"
                  class="col-5"
                />
                <q-input
                  v-model="movimentacaoForm.MOTIVO"
                  label="Motivo *"
                  :rules="[val => !!val || 'Motivo é obrigatório']"
                  placeholder="Ex: Aplicação em terreno X"
                  class="col-6"
                />
              </div>

              <div class="text-caption text-grey-6 q-mt-sm">
                Estoque atual: {{ form.ESTOQUE_ATUAL }}
                {{ form.UNIDADE_MEDIDA }}
              </div>
            </template>

            <!-- AJUSTE -->
            <template v-if="tipoMovimentacao === 'AJUSTE'">
              <div class="row q-gutter-md">
                <q-input
                  v-model.number="movimentacaoForm.QUANTIDADE_NOVA"
                  label="Nova Quantidade *"
                  type="number"
                  step="0.01"
                  min="0"
                  :suffix="form.UNIDADE_MEDIDA"
                  :rules="[
                    val => val >= 0 || 'Quantidade deve ser maior ou igual a 0',
                  ]"
                  class="col-5"
                />
                <q-input
                  v-model="movimentacaoForm.MOTIVO"
                  label="Motivo *"
                  :rules="[val => !!val || 'Motivo é obrigatório']"
                  placeholder="Ex: Correção de inventário"
                  class="col-6"
                />
              </div>

              <div class="q-mt-sm">
                <div class="text-caption text-grey-6">
                  Estoque atual: {{ form.ESTOQUE_ATUAL }}
                  {{ form.UNIDADE_MEDIDA }}
                </div>
                <div
                  class="text-caption"
                  :class="getDiferencaClass()"
                >
                  {{ getDiferencaTexto() }}
                </div>
              </div>
            </template>

            <!-- Observações (todos os tipos) -->
            <q-input
              v-model="movimentacaoForm.OBSERVACOES"
              label="Observações"
              type="textarea"
              rows="2"
            />
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancelar"
            color="grey"
            @click="movimentacaoDialog = false"
          />
          <q-btn
            :label="getLabelBotaoMovimentacao()"
            :color="getCorBotaoMovimentacao()"
            @click="submitMovimentacao"
            :loading="manejoStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG CONFIRMAÇÃO DELETE -->
    <q-dialog
      v-model="deleteDialog"
      persistent
    >
      <q-card>
        <q-card-section>
          <div class="text-h6">Confirmar Exclusão</div>
        </q-card-section>
        <q-card-section>
          Tem certeza que deseja excluir o produto
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
            @click="deleteProduto"
            :loading="manejoStore.loading"
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
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

  // Composables
  const $q = useQuasar()
  const manejoStore = useManejoStore()

  // Estado reativo
  const dialog = ref(false)
  const viewDialog = ref(false)
  const deleteDialog = ref(false)
  const movimentacaoDialog = ref(false)
  const viewData = ref(null)
  const recordToDelete = ref(null)
  const tipoMovimentacao = ref('ENTRADA') // ENTRADA, SAIDA, AJUSTE

  // Filtros
  const filtros = ref({
    nome: '',
    tipo_produto: null,
    estoque_baixo: false,
    ativo: null,
  })

  // Formulários
  const form = ref({})
  const movimentacaoForm = ref({})
  const requiresReceita = computed({
    get: () => form.value.REQUER_RECEITUARIO === 'S',
    set: val => (form.value.REQUER_RECEITUARIO = val ? 'S' : 'N'),
  })

  // Alertas de estoque
  const alertasEstoque = ref([])

  // Colunas da tabela
  const columns = [
    {
      name: 'NOME',
      label: 'Nome',
      field: 'NOME',
      sortable: true,
      align: 'left',
    },
    {
      name: 'TIPO_PRODUTO',
      label: 'Tipo',
      field: 'TIPO_PRODUTO',
      sortable: true,
      align: 'center',
    },
    {
      name: 'estoque',
      label: 'Estoque',
      field: 'ESTOQUE_ATUAL',
      sortable: true,
      align: 'left',
    },
    {
      name: 'status_estoque',
      label: 'Status',
      field: 'status_estoque',
      sortable: false,
      align: 'center',
    },
    {
      name: 'FABRICANTE',
      label: 'Fabricante',
      field: 'FABRICANTE',
      sortable: true,
      align: 'left',
    },
    {
      name: 'ATIVO',
      label: 'Ativo',
      field: 'ATIVO',
      sortable: true,
      align: 'center',
    },
    { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' },
  ]

  // Métodos
  async function onRequest(props) {
    const { page, rowsPerPage, sortBy, descending } = props.pagination
    manejoStore.setPagination({ page, rowsPerPage, sortBy, descending })
    await manejoStore.fetchProdutos({ ...props, filtros: filtros.value })
  }

  async function onFilterChange() {
    await manejoStore.fetchProdutos({ filtros: filtros.value })
  }

  function openDialog(record) {
    initializeForm(record)
    dialog.value = true
  }

  function initializeForm(record) {
    if (record) {
      form.value = { ...record }
    } else {
      form.value = {
        NOME: '',
        TIPO_PRODUTO: null,
        PRINCIPIO_ATIVO: '',
        CONCENTRACAO: '',
        UNIDADE_MEDIDA: '',
        FABRICANTE: '',
        REGISTRO_MINISTERIO: '',
        ESTOQUE_ATUAL: 0,
        ESTOQUE_MINIMO: 0,
        ESTOQUE_MAXIMO: null,
        PRECO_UNITARIO: null,
        FORNECEDOR_PRINCIPAL: '',
        CODIGO_FORNECEDOR: '',
        LOTE_ATUAL: '',
        DATA_VALIDADE: '',
        DOSE_RECOMENDADA: null,
        PERIODO_CARENCIA: null,
        REQUER_RECEITUARIO: 'N',
        LOCAL_ARMAZENAMENTO: '',
        CONDICOES_ARMAZENAMENTO: '',
        OBSERVACOES: '',
      }
    }
  }

  async function submitForm() {
    try {
      if (form.value.ID) {
        await manejoStore.updateProduto(form.value.ID, form.value)
        $q.notify({
          type: 'positive',
          message: 'Produto atualizado com sucesso!',
        })
      } else {
        await manejoStore.createProduto(form.value)
        $q.notify({ type: 'positive', message: 'Produto criado com sucesso!' })
      }

      dialog.value = false
      await manejoStore.fetchProdutos({ filtros: filtros.value })
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: error.message || 'Erro ao salvar produto',
      })
    }
  }

  function viewProduto(produto) {
    if (typeof produto === 'number') {
      viewData.value = manejoStore.produtos.find(p => p.ID === produto)
    } else {
      viewData.value = produto
    }
    viewDialog.value = true
  }

  function confirmDelete(record) {
    recordToDelete.value = record
    deleteDialog.value = true
  }

  async function deleteProduto() {
    try {
      await manejoStore.deleteProduto(recordToDelete.value.ID)
      $q.notify({ type: 'positive', message: 'Produto excluído com sucesso!' })
      deleteDialog.value = false
      await manejoStore.fetchProdutos({ filtros: filtros.value })
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: error.message || 'Erro ao excluir produto',
      })
    }
  }

  async function loadAlertas() {
    try {
      alertasEstoque.value = await manejoStore.getAlertasEstoque()
    } catch (error) {
      console.error('Erro ao carregar alertas:', error)
    }
  }

  function showAllAlertas() {
    // Implementar modal com todos os alertas
    $q.notify({ type: 'info', message: 'Funcionalidade em desenvolvimento' })
  }

  // Helpers
  function getCorTipo(tipo) {
    const cores = {
      FERTILIZANTE: 'green',
      DEFENSIVO: 'red',
      CORRETIVO: 'blue',
      SEMENTE: 'orange',
    }
    return cores[tipo] || 'grey'
  }

  function getCorEstoque(produto) {
    if (!produto.ESTOQUE_ATUAL || produto.ESTOQUE_ATUAL === 0) return 'red'
    if (produto.ESTOQUE_ATUAL <= produto.ESTOQUE_MINIMO) return 'orange'
    return 'green'
  }

  function getPercentualEstoque(produto) {
    if (!produto.ESTOQUE_MAXIMO) return 1
    return Math.min(produto.ESTOQUE_ATUAL / produto.ESTOQUE_MAXIMO, 1)
  }

  function getCorStatusEstoque(status) {
    const cores = {
      SEM_ESTOQUE: 'red',
      ESTOQUE_BAIXO: 'orange',
      VENCIMENTO_PROXIMO: 'purple',
      OK: 'green',
    }
    return cores[status] || 'grey'
  }

  function getStatusEstoqueLabel(status) {
    const labels = {
      SEM_ESTOQUE: 'Sem Estoque',
      ESTOQUE_BAIXO: 'Estoque Baixo',
      VENCIMENTO_PROXIMO: 'Venc. Próximo',
      OK: 'OK',
    }
    return labels[status] || 'N/A'
  }

  function getCorAlerta(status) {
    return getCorStatusEstoque(status)
  }

  // Funções para movimentação de estoque
  function openMovimentacaoDialog(tipo) {
    tipoMovimentacao.value = tipo
    initializeMovimentacaoForm()
    movimentacaoDialog.value = true
  }

  function initializeMovimentacaoForm() {
    movimentacaoForm.value = {
      ID_PRODUTO: form.value.ID,
      QUANTIDADE: null,
      QUANTIDADE_NOVA: form.value.ESTOQUE_ATUAL || 0,
      NOTA_FISCAL: '',
      FORNECEDOR: '',
      PRECO_UNITARIO: form.value.PRECO_UNITARIO || null,
      LOTE: '',
      DATA_VALIDADE: '',
      DATA_FABRICACAO: '',
      MOTIVO: '',
      OBSERVACOES: '',
    }
  }

  async function submitMovimentacao() {
    try {
      switch (tipoMovimentacao.value) {
        case 'ENTRADA':
          await manejoStore.entradaEstoque(movimentacaoForm.value)
          $q.notify({
            type: 'positive',
            message: 'Entrada registrada com sucesso!',
          })
          break

        case 'SAIDA':
          await manejoStore.saidaEstoque(movimentacaoForm.value)
          $q.notify({
            type: 'positive',
            message: 'Saída registrada com sucesso!',
          })
          break

        case 'AJUSTE':
          await manejoStore.ajusteEstoque(movimentacaoForm.value)
          $q.notify({
            type: 'positive',
            message: 'Ajuste realizado com sucesso!',
          })
          break
      }

      movimentacaoDialog.value = false

      // Atualizar o produto no formulário
      const produtoAtualizado = await manejoStore.getProdutoById(form.value.ID)
      form.value.ESTOQUE_ATUAL = produtoAtualizado.ESTOQUE_ATUAL

      // Recarregar lista de produtos
      await manejoStore.fetchProdutos({ filtros: filtros.value })
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: error.message || 'Erro na movimentação',
      })
    }
  }

  function getTituloMovimentacao(tipo) {
    const titulos = {
      ENTRADA: 'Entrada de Estoque',
      SAIDA: 'Saída de Estoque',
      AJUSTE: 'Ajustar Estoque',
    }
    return titulos[tipo] || 'Movimentação'
  }

  function getLabelBotaoMovimentacao() {
    const labels = {
      ENTRADA: 'Registrar Entrada',
      SAIDA: 'Registrar Saída',
      AJUSTE: 'Confirmar Ajuste',
    }
    return labels[tipoMovimentacao.value] || 'Confirmar'
  }

  function getCorBotaoMovimentacao() {
    const cores = {
      ENTRADA: 'positive',
      SAIDA: 'negative',
      AJUSTE: 'warning',
    }
    return cores[tipoMovimentacao.value] || 'primary'
  }

  function getDiferencaClass() {
    const diferenca =
      (movimentacaoForm.value.QUANTIDADE_NOVA || 0) -
      (form.value.ESTOQUE_ATUAL || 0)
    if (diferenca > 0) return 'text-positive'
    if (diferenca < 0) return 'text-negative'
    return 'text-grey-6'
  }

  function getDiferencaTexto() {
    const estoque = form.value.ESTOQUE_ATUAL || 0
    const nova = movimentacaoForm.value.QUANTIDADE_NOVA || 0
    const diferenca = nova - estoque

    if (diferenca === 0) return 'Sem alteração'
    if (diferenca > 0)
      return `+${diferenca.toLocaleString('pt-BR')} ${form.value.UNIDADE_MEDIDA}`
    return `${diferenca.toLocaleString('pt-BR')} ${form.value.UNIDADE_MEDIDA}`
  }

  // Lifecycle
  onMounted(async () => {
    await manejoStore.fetchProdutos({ filtros: filtros.value })
    await loadAlertas()
  })
</script>

<style scoped>
  .produtos-manejo-container {
    width: 100%;
  }

  .produtos-table {
    border-radius: 8px;
  }

  .produtos-table .q-table__top {
    padding: 16px;
  }
</style>
