<template>
  <div class="produtos-racao-container">

    <!-- FILTROS -->
    <q-card flat bordered class="q-mb-md">
      <q-card-section>
        <div class="row q-gutter-md justify-between">
          <q-input
            v-model="filtros.nome"
            label="Buscar por nome"
            debounce="500"
            @update:model-value="onFilterChange"
            class="col-md-3 col-12"
          >
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>

          <q-select
            v-model="filtros.tipo_alimento"
            :options="racaoStore.tiposAlimento"
            label="Tipo de Alimento"
            clearable
            @update:model-value="onFilterChange"
            class="col-md-2 col-12"
          />

          <q-toggle
            v-model="filtros.estoque_baixo"
            label="Apenas estoque baixo"
            @update:model-value="onFilterChange"
            class="col-md-2 col-12"
          />

          <q-select
            v-model="filtros.ativo"
            :options="[
              { value: 'S', label: 'Ativos' },
              { value: 'N', label: 'Inativos' },
              { value: null, label: 'Todos' }
            ]"
            label="Status"
            @update:model-value="onFilterChange"
            class="col-md-2 col-12"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- ALERTAS DE ESTOQUE -->
    <div v-if="alertasEstoque.length > 0" class="row q-mb-md">
      <div class="col-12">
        <q-banner class="bg-warning text-white" inline-actions>
          <template v-slot:avatar>
            <q-icon name="warning" />
          </template>
          {{ alertasEstoque.length }} produto(s) com estoque baixo ou vencimento próximo
          <template v-slot:action>
            <q-btn flat color="white" label="Ver Relatório" @click="$emit('show-relatorios')" />
          </template>
        </q-banner>
      </div>
    </div>

    <div class="row q-mb-md items-center justify-between">
      <q-btn
        color="primary"
        icon="add"
        label="Novo Produto"
        @click="openDialog()"
      />
    </div>

    <!-- TABELA -->
    <q-table
      :rows="racaoStore.produtos"
      :columns="columns"
      row-key="ID"
      :loading="racaoStore.loading"
      :pagination="racaoStore.pagination"
      @request="onRequest"
      binary-state-sort
      flat
      class="produtos-table"
    >
      <template v-slot:body-cell-TIPO_ALIMENTO="props">
        <q-td :props="props">
          <q-chip
            :color="getCorTipo(props.value)"
            text-color="white"
            size="sm"
          >
            {{ racaoStore.getTipoAlimentoLabel(props.value) }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-estoque="props">
        <q-td :props="props">
          <div class="text-weight-medium">
            {{ racaoStore.formatarPeso(props.row.ESTOQUE_ATUAL) }}
          </div>
          <div class="text-caption">
            Mín: {{ racaoStore.formatarPeso(props.row.ESTOQUE_MINIMO) }}
          </div>
          <q-linear-progress
            :value="getPercentualEstoque(props.row)"
            :color="getCorEstoque(props.row)"
            size="4px"
            class="q-mt-xs"
          />
        </q-td>
      </template>

      <template v-slot:body-cell-composicao="props">
        <q-td :props="props">
          <div v-if="props.row.PROTEINA_BRUTA" class="text-caption">
            PB: {{ props.row.PROTEINA_BRUTA }}%
          </div>
          <div v-if="props.row.ENERGIA_DIGESTIVEL" class="text-caption">
            ED: {{ props.row.ENERGIA_DIGESTIVEL }} Mcal/kg
          </div>
          <div v-if="props.row.FIBRA_BRUTA" class="text-caption">
            FB: {{ props.row.FIBRA_BRUTA }}%
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-status_estoque="props">
        <q-td :props="props">
          <q-chip
            :color="racaoStore.getStatusColor(props.row.status_estoque)"
            text-color="white"
            size="sm"
          >
            {{ getStatusEstoqueLabel(props.row.status_estoque) }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-valor_estoque="props">
        <q-td :props="props">
          {{ racaoStore.formatarMoeda(props.row.valor_total_estoque) }}
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
              color="info"
              icon="swap_horiz"
              size="sm"
              @click="openMovimentacaoDialog(props.row, 'ENTRADA')"
            >
              <q-tooltip>Movimentar Estoque</q-tooltip>
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
    <q-dialog v-model="dialog" persistent>
      <q-card style="min-width: 800px; max-height: 80vh">
        <q-card-section>
          <div class="text-h6">
            {{ form.ID ? 'Editar Produto' : 'Novo Produto' }}
          </div>
        </q-card-section>

        <q-card-section style="max-height: 60vh; overflow-y: auto">
          <q-form @submit="submitForm" class="q-gutter-md">
            <!-- Informações Básicas -->
            <div class="text-subtitle1 q-mb-sm">Informações Básicas</div>
            <div class="row q-gutter-md">
              <q-input
                v-model="form.NOME"
                label="Nome do Produto *"
                :rules="[val => !!val || 'Nome é obrigatório']"
                class="col-md-5 col-12"
              />
              <q-select
                v-model="form.TIPO_ALIMENTO"
                :options="racaoStore.tiposAlimento"
                label="Tipo de Alimento *"
                :rules="[val => !!val || 'Tipo é obrigatório']"
                class="col-md-3 col-12"
              />
              <q-input
                v-model="form.MARCA"
                label="Marca"
                class="col-md-3 col-12"
              />
            </div>

            <div class="row q-gutter-md">
              <q-input
                v-model="form.FABRICANTE"
                label="Fabricante"
                class="col-md-4 col-12"
              />
              <q-input
                v-model="form.REGISTRO_MINISTERIO"
                label="Registro Ministério"
                class="col-md-4 col-12"
              />
              <q-input
                v-model="form.UNIDADE_MEDIDA"
                label="Unidade de Medida"
                placeholder="Ex: KG, L, SC"
                class="col-md-3 col-12"
              />
            </div>

            <q-separator class="q-my-md" />

            <!-- Composição Nutricional -->
            <div class="text-subtitle1 q-mb-sm">Composição Nutricional</div>
            <div class="row q-gutter-md">
              <q-input
                v-model.number="form.PROTEINA_BRUTA"
                label="Proteína Bruta (%)"
                type="number"
                step="0.1"
                min="0"
                max="100"
                class="col-md-2 col-6"
              />
              <q-input
                v-model.number="form.FIBRA_BRUTA"
                label="Fibra Bruta (%)"
                type="number"
                step="0.1"
                min="0"
                max="100"
                class="col-md-2 col-6"
              />
              <q-input
                v-model.number="form.ENERGIA_DIGESTIVEL"
                label="Energia (Mcal/kg)"
                type="number"
                step="0.01"
                min="0"
                class="col-md-2 col-6"
              />
              <q-input
                v-model.number="form.CALCIO"
                label="Cálcio (%)"
                type="number"
                step="0.01"
                min="0"
                max="10"
                class="col-md-2 col-6"
              />
              <q-input
                v-model.number="form.FOSFORO"
                label="Fósforo (%)"
                type="number"
                step="0.01"
                min="0"
                max="10"
                class="col-md-2 col-6"
              />
              <q-input
                v-model.number="form.SODIO"
                label="Sódio (%)"
                type="number"
                step="0.01"
                min="0"
                max="10"
                class="col-md-1 col-6"
              />
            </div>

            <q-separator class="q-my-md" />

            <!-- Controle de Estoque -->
            <div class="text-subtitle1 q-mb-sm">Controle de Estoque</div>
            <div class="row q-gutter-md">
              <q-input
                v-model.number="form.ESTOQUE_ATUAL"
                label="Estoque Atual"
                type="number"
                step="0.001"
                min="0"
                class="col-md-2 col-6"
              />
              <q-input
                v-model.number="form.ESTOQUE_MINIMO"
                label="Estoque Mínimo *"
                type="number"
                step="0.001"
                min="0"
                :rules="[val => val >= 0 || 'Deve ser maior ou igual a 0']"
                class="col-md-2 col-6"
              />
              <q-input
                v-model.number="form.ESTOQUE_MAXIMO"
                label="Estoque Máximo"
                type="number"
                step="0.001"
                min="0"
                class="col-md-2 col-6"
              />
              <q-input
                v-model.number="form.PRECO_UNITARIO"
                label="Preço Unitário (R$)"
                type="number"
                step="0.01"
                min="0"
                prefix="R$"
                class="col-md-2 col-6"
              />
            </div>

            <q-separator class="q-my-md" />

            <!-- Dados Comerciais -->
            <div class="text-subtitle1 q-mb-sm">Dados Comerciais</div>
            <div class="row q-gutter-md">
              <q-input
                v-model="form.FORNECEDOR_PRINCIPAL"
                label="Fornecedor Principal"
                class="col-md-4 col-12"
              />
              <q-input
                v-model="form.CODIGO_FORNECEDOR"
                label="Código do Fornecedor"
                class="col-md-3 col-12"
              />
              <q-input
                v-model="form.LOTE_ATUAL"
                label="Lote Atual"
                class="col-md-2 col-12"
              />
            </div>

            <div class="row q-gutter-md">
              <calendario-component
                v-model="form.DATA_FABRICACAO"
                label="Data de Fabricação *"
                :rules="[val => !!val || 'Data é obrigatória']"
                class="col-md-3 col-12"
              />

              <calendario-component
                v-model="form.DATA_VALIDADE"
                label="Data de Validade *"
                :rules="[val => !!val || 'Data é obrigatória']"
                class="col-md-3 col-12"
              />

            </div>

            <q-separator class="q-my-md" />

            <!-- Armazenamento -->
            <div class="text-subtitle1 q-mb-sm">Armazenamento</div>
            <div class="row q-gutter-md">
              <q-input
                v-model="form.LOCAL_ARMAZENAMENTO"
                label="Local de Armazenamento"
                class="col-md-4 col-12"
              />
              <q-input
                v-model="form.CONDICOES_ARMAZENAMENTO"
                label="Condições de Armazenamento"
                placeholder="Ex: Temperatura ambiente, local seco"
                class="col-md-7 col-12"
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
          <div class="text-h6">{{ viewData?.NOME }}</div>
          <div class="text-subtitle2 text-grey-6">{{ racaoStore.getTipoAlimentoLabel(viewData?.TIPO_ALIMENTO) }}</div>
        </q-card-section>

        <q-card-section>
          <div class="row q-gutter-md">
            <!-- Estoque -->
            <div class="col-md-5 col-12">
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-subtitle1 q-mb-sm">Estoque</div>
                  <q-list>
                    <q-item>
                      <q-item-section>
                        <q-item-label caption>Atual</q-item-label>
                        <q-item-label>{{ racaoStore.formatarPeso(viewData?.ESTOQUE_ATUAL) }}</q-item-label>
                      </q-item-section>
                      <q-item-section>
                        <q-item-label caption>Mínimo</q-item-label>
                        <q-item-label>{{ racaoStore.formatarPeso(viewData?.ESTOQUE_MINIMO) }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item v-if="viewData?.PRECO_UNITARIO">
                      <q-item-section>
                        <q-item-label caption>Valor Total</q-item-label>
                        <q-item-label>{{ racaoStore.formatarMoeda(viewData?.valor_total_estoque) }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </div>

            <!-- Composição Nutricional -->
            <div class="col-md-6 col-12">
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-subtitle1 q-mb-sm">Composição Nutricional</div>
                  <q-list>
                    <q-item v-if="viewData?.PROTEINA_BRUTA">
                      <q-item-section>
                        <q-item-label caption>Proteína Bruta</q-item-label>
                        <q-item-label>{{ viewData.PROTEINA_BRUTA }}%</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item v-if="viewData?.ENERGIA_DIGESTIVEL">
                      <q-item-section>
                        <q-item-label caption>Energia Digestível</q-item-label>
                        <q-item-label>{{ viewData.ENERGIA_DIGESTIVEL }} Mcal/kg</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item v-if="viewData?.FIBRA_BRUTA">
                      <q-item-section>
                        <q-item-label caption>Fibra Bruta</q-item-label>
                        <q-item-label>{{ viewData.FIBRA_BRUTA }}%</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item v-if="viewData?.CALCIO">
                      <q-item-section>
                        <q-item-label caption>Cálcio</q-item-label>
                        <q-item-label>{{ viewData.CALCIO }}%</q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </div>
          </div>

          <div v-if="viewData?.OBSERVACOES" class="q-mt-md">
            <div class="text-subtitle1 q-mb-sm">Observações</div>
            <q-card flat bordered>
              <q-card-section>
                <div class="text-body2" style="white-space: pre-line;">
                  {{ viewData.OBSERVACOES }}
                </div>
              </q-card-section>
            </q-card>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Fechar" color="grey" @click="viewDialog = false" />
          <q-btn
            label="Editar"
            color="primary"
            @click="openDialog(viewData); viewDialog = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG MOVIMENTAÇÃO -->
    <q-dialog v-model="movimentacaoDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">{{ getTituloMovimentacao(tipoMovimentacao) }}</div>
          <div class="text-subtitle2">{{ form.NOME }}</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="submitMovimentacao" class="q-gutter-md">
            <!-- Tipo de Movimentação -->
            <q-btn-toggle
              v-model="tipoMovimentacao"
              :options="[
                { label: 'Entrada', value: 'ENTRADA' },
                { label: 'Saída', value: 'SAIDA' },
                { label: 'Ajuste', value: 'AJUSTE' }
              ]"
              @update:model-value="initializeMovimentacaoForm"
            />

            <!-- Estoque Atual -->
            <q-card flat bordered class="bg-blue-1">
              <q-card-section class="q-pa-sm">
                <div class="text-caption">Estoque Atual</div>
                <div class="text-h6">{{ racaoStore.formatarPeso(form.ESTOQUE_ATUAL) }}</div>
              </q-card-section>
            </q-card>

            <!-- Campos específicos por tipo -->
            <div v-if="tipoMovimentacao === 'ENTRADA'">
              <div class="row q-gutter-md">
                <q-input
                  v-model="movimentacaoForm.NOTA_FISCAL"
                  label="Nota Fiscal *"
                  :rules="[val => !!val || 'Nota fiscal é obrigatória']"
                  class="col-5"
                />
                <q-input
                  v-model="movimentacaoForm.FORNECEDOR"
                  label="Fornecedor *"
                  :rules="[val => !!val || 'Fornecedor é obrigatório']"
                  class="col-6"
                />
              </div>

              <div class="row q-gutter-md">
                <q-input
                  v-model.number="movimentacaoForm.QUANTIDADE"
                  label="Quantidade *"
                  type="number"
                  step="0.001"
                  min="0.001"
                  :rules="[val => val > 0 || 'Quantidade deve ser maior que 0']"
                  :suffix="form.UNIDADE_MEDIDA"
                  class="col-3"
                />
                <q-input
                  v-model.number="movimentacaoForm.PRECO_UNITARIO"
                  label="Preço Unitário *"
                  type="number"
                  step="0.01"
                  min="0"
                  prefix="R$"
                  :rules="[val => val >= 0 || 'Preço deve ser maior ou igual a 0']"
                  class="col-3"
                />
                <q-input
                  v-model="movimentacaoForm.LOTE"
                  label="Lote *"
                  :rules="[val => !!val || 'Lote é obrigatório']"
                  class="col-5"
                />
              </div>

              <div class="row q-gutter-md">
                 <calendario-component
                   v-model="form.DATA_FABRICACAO"
                   label="Data de Fabricação *"
                   :rules="[val => !!val || 'Data é obrigatória']"
                   class="col-6"
                 />
   
                 <calendario-component
                   v-model="form.DATA_VALIDADE"
                   label="Data de Validade *"
                   :rules="[val => !!val || 'Data é obrigatória']"
                   class="col-6"
                 />
              </div>
            </div>

            <div v-else-if="tipoMovimentacao === 'SAIDA'">
              <div class="row q-gutter-md">
                <q-input
                  v-model.number="movimentacaoForm.QUANTIDADE"
                  label="Quantidade *"
                  type="number"
                  step="0.001"
                  min="0.001"
                  :max="form.ESTOQUE_ATUAL"
                  :rules="[
                    val => val > 0 || 'Quantidade deve ser maior que 0',
                    val => val <= form.ESTOQUE_ATUAL || 'Quantidade maior que estoque disponível'
                  ]"
                  :suffix="form.UNIDADE_MEDIDA"
                  class="col-6"
                />
                <q-input
                  v-model="movimentacaoForm.MOTIVO"
                  label="Motivo *"
                  :rules="[val => !!val || 'Motivo é obrigatório']"
                  class="col-5"
                />
              </div>
            </div>

            <div v-else-if="tipoMovimentacao === 'AJUSTE'">
              <div class="row q-gutter-md">
                <q-input
                  v-model.number="movimentacaoForm.QUANTIDADE_NOVA"
                  label="Nova Quantidade *"
                  type="number"
                  step="0.001"
                  min="0"
                  :rules="[val => val >= 0 || 'Quantidade deve ser maior ou igual a 0']"
                  :suffix="form.UNIDADE_MEDIDA"
                  class="col-6"
                />
                <q-input
                  v-model="movimentacaoForm.MOTIVO"
                  label="Motivo do Ajuste *"
                  :rules="[val => !!val || 'Motivo é obrigatório']"
                  class="col-5"
                />
              </div>

              <!-- Mostrar diferença -->
              <q-card flat bordered class="q-mt-sm" :class="getDiferencaClass()">
                <q-card-section class="q-pa-sm">
                  <div class="text-caption">Diferença</div>
                  <div class="text-weight-medium">{{ getDiferencaTexto() }}</div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Observações -->
            <q-input
              v-model="movimentacaoForm.OBSERVACOES"
              label="Observações"
              type="textarea"
              rows="2"
            />
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" @click="movimentacaoDialog = false" />
          <q-btn
            :label="getLabelBotaoMovimentacao()"
            :color="getCorBotaoMovimentacao()"
            @click="submitMovimentacao"
            :loading="racaoStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG CONFIRMAÇÃO EXCLUSÃO -->
    <q-dialog v-model="deleteDialog" persistent>
      <q-card>
        <q-card-section>
          <div class="text-h6">Confirmar Exclusão</div>
        </q-card-section>
        <q-card-section>
          Tem certeza que deseja excluir o produto <strong>{{ recordToDelete?.NOME }}</strong>?
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" @click="deleteDialog = false" />
          <q-btn
            label="Excluir"
            color="negative"
            @click="deleteProduto"
            :loading="racaoStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRacaoStore } from 'stores/racao'
import { ErrorHandler } from 'src/utils/errorHandler'
import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

// Emits
// const emit = defineEmits(['show-relatorios'])

// Composables
const racaoStore = useRacaoStore()

// Estado reativo
const dialog = ref(false)
const viewDialog = ref(false)
const deleteDialog = ref(false)
const movimentacaoDialog = ref(false)
const viewData = ref(null)
const recordToDelete = ref(null)
const tipoMovimentacao = ref('ENTRADA')

// Filtros
const filtros = ref({
  nome: '',
  tipo_alimento: null,
  estoque_baixo: false,
  ativo: ''
})

// Formulários
const form = ref({})
const movimentacaoForm = ref({})

// Alertas de estoque
const alertasEstoque = ref([])

// Colunas da tabela
const columns = [
  { name: 'NOME', label: 'Nome', field: 'NOME', sortable: true, align: 'left' },
  { name: 'TIPO_ALIMENTO', label: 'Tipo', field: 'TIPO_ALIMENTO', sortable: true, align: 'center' },
  { name: 'estoque', label: 'Estoque', field: 'ESTOQUE_ATUAL', sortable: true, align: 'left' },
  { name: 'composicao', label: 'Composição', field: 'composicao', sortable: false, align: 'left' },
  { name: 'status_estoque', label: 'Status', field: 'status_estoque', sortable: false, align: 'center' },
  { name: 'valor_estoque', label: 'Valor', field: 'valor_total_estoque', sortable: true, align: 'right' },
  { name: 'ATIVO', label: 'Ativo', field: 'ATIVO', sortable: true, align: 'center' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

// Métodos
async function onRequest(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  racaoStore.pagination.page = page
  racaoStore.pagination.rowsPerPage = rowsPerPage
  racaoStore.pagination.sortBy = sortBy
  racaoStore.pagination.descending = descending
  await racaoStore.fetchProdutos({ ...props, filtros: filtros.value })
}

async function onFilterChange() {
  racaoStore.pagination.page = 1
  await racaoStore.fetchProdutos({ filtros: filtros.value })
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
      TIPO_ALIMENTO: null,
      MARCA: '',
      FABRICANTE: '',
      PROTEINA_BRUTA: null,
      FIBRA_BRUTA: null,
      ENERGIA_DIGESTIVEL: null,
      CALCIO: null,
      FOSFORO: null,
      MAGNESIO: null,
      POTASSIO: null,
      SODIO: null,
      ESTOQUE_ATUAL: 0,
      ESTOQUE_MINIMO: 0,
      ESTOQUE_MAXIMO: null,
      UNIDADE_MEDIDA: 'KG',
      PRECO_UNITARIO: null,
      FORNECEDOR_PRINCIPAL: '',
      CODIGO_FORNECEDOR: '',
      LOTE_ATUAL: '',
      DATA_FABRICACAO: '',
      DATA_VALIDADE: '',
      REGISTRO_MINISTERIO: '',
      LOCAL_ARMAZENAMENTO: '',
      CONDICOES_ARMAZENAMENTO: '',
      OBSERVACOES: ''
    }
  }
}

async function submitForm() {
  try {
    if (form.value.ID) {
      await racaoStore.updateProduto(form.value.ID, form.value)
      ErrorHandler.success('Produto atualizado com sucesso!')
    } else {
      await racaoStore.createProduto(form.value)
      ErrorHandler.success('Produto criado com sucesso!')
    }
    
    dialog.value = false
    await racaoStore.fetchProdutos({ filtros: filtros.value })
    
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao salvar produto')
  }
}

function viewProduto(produto) {
  if (typeof produto === 'number') {
    viewData.value = racaoStore.produtos.find(p => p.ID === produto)
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
    await racaoStore.deleteProduto(recordToDelete.value.ID)
    ErrorHandler.success('Produto excluído com sucesso!')
    deleteDialog.value = false
    await racaoStore.fetchProdutos({ filtros: filtros.value })
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao excluir produto')
  }
}

function openMovimentacaoDialog(produto, tipo) {
  form.value = produto
  tipoMovimentacao.value = tipo
  initializeMovimentacaoForm()
  movimentacaoDialog.value = true
}

function initializeMovimentacaoForm() {
  movimentacaoForm.value = {
    ID_PRODUTO: form.value.ID,
    QUANTIDADE: null,
    QUANTIDADE_NOVA: form.value.ESTOQUE_ATUAL,
    NOTA_FISCAL: '',
    FORNECEDOR: form.value.FORNECEDOR_PRINCIPAL || '',
    PRECO_UNITARIO: form.value.PRECO_UNITARIO || null,
    LOTE: '',
    DATA_FABRICACAO: '',
    DATA_VALIDADE: '',
    MOTIVO: '',
    OBSERVACOES: ''
  }
}

async function submitMovimentacao() {
  try {
    switch (tipoMovimentacao.value) {
      case 'ENTRADA':
        await racaoStore.entradaEstoque(movimentacaoForm.value)
        ErrorHandler.success('Entrada registrada com sucesso!')
        break
        
      case 'SAIDA':
        await racaoStore.saidaEstoque(movimentacaoForm.value)
        ErrorHandler.success('Saída registrada com sucesso!')
        break
        
      case 'AJUSTE':
        await racaoStore.ajusteEstoque(movimentacaoForm.value)
        ErrorHandler.success('Ajuste de estoque realizado com sucesso!')
        break
    }
    
    movimentacaoDialog.value = false
    await racaoStore.fetchProdutos({ filtros: filtros.value })
    
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao registrar movimentação')
  }
}

async function loadAlertas() {
  try {
    await racaoStore.getAlertasEstoque()
    alertasEstoque.value = racaoStore.alertasEstoque
    console.log('Alertas de estoque carregados:', alertasEstoque.value)
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao carregar alertas de estoque')
  }
}

// Funções auxiliares
function getCorTipo(tipo) {
  const cores = {
    'CONCENTRADO': 'primary',
    'VOLUMOSO': 'green',
    'SUPLEMENTO': 'orange',
    'PREMIX': 'purple',
    'SAL_MINERAL': 'brown'
  }
  return cores[tipo] || 'grey'
}

function getPercentualEstoque(produto) {
  const atual = produto.ESTOQUE_ATUAL || 0
  const minimo = produto.ESTOQUE_MINIMO || 0
  const maximo = produto.ESTOQUE_MAXIMO || (minimo * 3)
  
  if (maximo <= minimo) return 0
  return Math.min(atual / maximo, 1)
}

function getCorEstoque(produto) {
  const atual = produto.ESTOQUE_ATUAL || 0
  const minimo = produto.ESTOQUE_MINIMO || 0
  
  if (atual <= 0) return 'red'
  if (atual <= minimo) return 'orange'
  return 'green'
}

function getStatusEstoqueLabel(status) {
  const labels = {
    'SEM_ESTOQUE': 'Sem Estoque',
    'ESTOQUE_BAIXO': 'Estoque Baixo',
    'VENCIMENTO_PROXIMO': 'Vencimento Próximo',
    'VENCIDO': 'Vencido',
    'OK': 'OK'
  }
  return labels[status] || status
}

function getTituloMovimentacao(tipo) {
  const titulos = {
    'ENTRADA': 'Entrada de Estoque',
    'SAIDA': 'Saída de Estoque',
    'AJUSTE': 'Ajustar Estoque'
  }
  return titulos[tipo] || 'Movimentação'
}

function getLabelBotaoMovimentacao() {
  const labels = {
    'ENTRADA': 'Registrar Entrada',
    'SAIDA': 'Registrar Saída',
    'AJUSTE': 'Confirmar Ajuste'
  }
  return labels[tipoMovimentacao.value] || 'Confirmar'
}

function getCorBotaoMovimentacao() {
  const cores = {
    'ENTRADA': 'positive',
    'SAIDA': 'negative',
    'AJUSTE': 'warning'
  }
  return cores[tipoMovimentacao.value] || 'primary'
}

function getDiferencaClass() {
  const diferenca = (movimentacaoForm.value.QUANTIDADE_NOVA || 0) - (form.value.ESTOQUE_ATUAL || 0)
  if (diferenca > 0) return 'text-positive'
  if (diferenca < 0) return 'text-negative'
  return 'text-grey-6'
}

function getDiferencaTexto() {
  const estoque = form.value.ESTOQUE_ATUAL || 0
  const nova = movimentacaoForm.value.QUANTIDADE_NOVA || 0
  const diferenca = nova - estoque
  
  if (diferenca === 0) return 'Sem alteração'
  if (diferenca > 0) return `+${diferenca.toLocaleString('pt-BR')} ${form.value.UNIDADE_MEDIDA}`
  return `${diferenca.toLocaleString('pt-BR')} ${form.value.UNIDADE_MEDIDA}`
}

// Lifecycle
onMounted(async () => {
  await racaoStore.fetchProdutos({ filtros: filtros.value })
  await loadAlertas()
})
</script>

<style scoped>
.produtos-racao-container {
  width: 100%;
}

.produtos-table {
  border-radius: 8px;
}

.produtos-table .q-table__top {
  padding: 16px;
}
</style>