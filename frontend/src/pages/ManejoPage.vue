<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Manejo de Terrenos</div>
      </q-card-section>
      <q-card-section>
        <!-- Filtros -->
        <div class="row q-gutter-md q-mb-md">
          <q-select
            v-model="manejoStore.filters.terreno_id"
            :options="terrenoOptions"
            label="Terreno"
            clearable
            use-input
            @filter="filterTerrenos"
            @update:model-value="onFilterChange"
            class="col-3"
          />
          <q-select
            v-model="manejoStore.filters.tipo_manejo"
            :options="manejoStore.tiposManejo"
            label="Tipo Manejo"
            clearable
            @update:model-value="onFilterChange"
            class="col-2"
          />
          <calendario-component
            v-model="manejoStore.filters.data_inicio"
            label="Data Início"
            @update:model-value="onFilterChange"
            class="col-2"
          />
          <calendario-component
            v-model="manejoStore.filters.data_fim"
            label="Data Fim"
            @update:model-value="onFilterChange"
            class="col-2"
          />
        </div>
        
        <!-- Abas -->
        <q-tabs v-model="activeTab" class="q-mb-md">
          <q-tab name="aplicacoes" label="Aplicações" />
          <q-tab name="produtos" label="Produtos" />
          <q-tab name="analises" label="Análises de Solo" />
          <q-tab name="relatorios" label="Relatórios" />
        </q-tabs>
        
        <q-tab-panels v-model="activeTab" animated>
          <!-- ABA APLICAÇÕES -->
          <q-tab-panel name="aplicacoes">
            <div class="row q-gutter-md q-mb-md">
              <q-btn
                color="primary"
                label="Nova Aplicação"
                icon="add"
                @click="openDialog(null, 'aplicacao')"
              />
              <q-btn
                color="warning"
                label="Terrenos Bloqueados"
                icon="block"
                @click="showTerrenosBloqueados"
                :badge="manejoStore.terrenosComCarencia.length || undefined"
              />
            </div>

            <q-table
              :rows="manejoStore.aplicacoes"
              :columns="aplicacaoColumns"
              row-key="ID"
              :loading="manejoStore.loading"
              :pagination="manejoStore.pagination"
              @request="onRequestAplicacoes"
              binary-state-sort
            >
              <template v-slot:body-cell-tipo="props">
                <q-td :props="props">
                  <q-chip
                    :color="getTipoManejoColor(props.row.TIPO_MANEJO)"
                    text-color="white"
                    dense
                  >
                    {{ manejoStore.getManejoLabel(props.row.TIPO_MANEJO) }}
                  </q-chip>
                </q-td>
              </template>
              <template v-slot:body-cell-status="props">
                <q-td :props="props">
                  <q-chip
                    v-if="props.row.dias_para_liberacao !== null"
                    :color="props.row.dias_para_liberacao > 0 ? 'negative' : 'positive'"
                    text-color="white"
                    dense
                  >
                    {{ props.row.dias_para_liberacao > 0 ? `${props.row.dias_para_liberacao} dias` : 'Liberado' }}
                  </q-chip>
                  <span v-else class="text-grey">Sem carência</span>
                </q-td>
              </template>
              <template v-slot:body-cell-acoes="props">
                <q-td :props="props">
                  <q-btn
                    flat
                    round
                    color="info"
                    icon="visibility"
                    @click="viewRecord(props.row, 'aplicacao')"
                  />
                  <q-btn
                    flat
                    round
                    color="primary"
                    icon="edit"
                    @click="openDialog(props.row, 'aplicacao')"
                  />
                  <q-btn
                    flat
                    round
                    color="negative"
                    icon="delete"
                    @click="confirmDelete(props.row, 'aplicacao')"
                  />
                </q-td>
              </template>
            </q-table>
          </q-tab-panel>
          
          <!-- ABA PRODUTOS -->
          <q-tab-panel name="produtos">
            <div class="row q-gutter-md q-mb-md">
              <q-input
                v-model="manejoStore.filters.nome"
                label="Filtrar por Nome"
                clearable
                @update:model-value="onFilterChangeProdutos"
                :debounce="300"
                class="col-3"
              />
              <q-select
                v-model="manejoStore.filters.tipo_produto"
                :options="manejoStore.tiposProduto"
                label="Tipo Produto"
                clearable
                @update:model-value="onFilterChangeProdutos"
                class="col-2"
              />
              <q-btn
                color="secondary"
                label="Novo Produto"
                icon="add"
                @click="openDialog(null, 'produto')"
              />
            </div>
            
            <q-table
              :rows="manejoStore.produtos"
              :columns="produtoColumns"
              row-key="ID"
              :loading="manejoStore.loading"
              :pagination="manejoStore.pagination"
              @request="onRequestProdutos"
              binary-state-sort
            >
              <template v-slot:body-cell-tipo="props">
                <q-td :props="props">
                  <q-chip
                    :color="getTipoProdutoColor(props.row.TIPO_PRODUTO)"
                    text-color="white"
                    dense
                  >
                    {{ manejoStore.getTipoLabel(props.row.TIPO_PRODUTO) }}
                  </q-chip>
                </q-td>
              </template>
              <template v-slot:body-cell-ativo="props">
                <q-td :props="props">
                  <q-icon
                    :name="props.row.ATIVO === 'S' ? 'check_circle' : 'cancel'"
                    :color="props.row.ATIVO === 'S' ? 'positive' : 'negative'"
                  />
                </q-td>
              </template>
              <template v-slot:body-cell-acoes="props">
                <q-td :props="props">
                  <q-btn
                    flat
                    round
                    color="info"
                    icon="visibility"
                    @click="viewRecord(props.row, 'produto')"
                  />
                  <q-btn
                    flat
                    round
                    color="primary"
                    icon="edit"
                    @click="openDialog(props.row, 'produto')"
                  />
                  <q-btn
                    flat
                    round
                    color="negative"
                    icon="delete"
                    @click="confirmDelete(props.row, 'produto')"
                  />
                </q-td>
              </template>
            </q-table>
          </q-tab-panel>
          
          <!-- ABA ANÁLISES -->
          <q-tab-panel name="analises">
            <div class="row q-gutter-md q-mb-md">
              <q-btn
                color="accent"
                label="Nova Análise"
                icon="add"
                @click="openDialog(null, 'analise')"
              />
            </div>
            
            <q-table
              :rows="manejoStore.analisesSolo"
              :columns="analiseColumns"
              row-key="ID"
              :loading="manejoStore.loading"
              :pagination="manejoStore.pagination"
              @request="onRequestAnalises"
              binary-state-sort
            >
              <template v-slot:body-cell-ph="props">
                <q-td :props="props">
                  <span v-if="props.row.PH_AGUA">
                    {{ props.row.PH_AGUA.toFixed(1) }}
                    <q-icon
                      :name="props.row.PH_AGUA >= 6.0 ? 'check_circle' : 'warning'"
                      :color="props.row.PH_AGUA >= 6.0 ? 'positive' : 'warning'"
                      size="xs"
                    />
                  </span>
                  <span v-else class="text-grey">-</span>
                </q-td>
              </template>
              <template v-slot:body-cell-saturacao="props">
                <q-td :props="props">
                  <span v-if="props.row.SATURACAO_BASES">
                    {{ props.row.SATURACAO_BASES.toFixed(1) }}%
                    <q-icon
                      :name="props.row.SATURACAO_BASES >= 60 ? 'check_circle' : 'warning'"
                      :color="props.row.SATURACAO_BASES >= 60 ? 'positive' : 'warning'"
                      size="xs"
                    />
                  </span>
                  <span v-else class="text-grey">-</span>
                </q-td>
              </template>
              <template v-slot:body-cell-acoes="props">
                <q-td :props="props">
                  <q-btn
                    flat
                    round
                    color="info"
                    icon="visibility"
                    @click="viewRecord(props.row, 'analise')"
                  />
                  <q-btn
                    flat
                    round
                    color="primary"
                    icon="edit"
                    @click="openDialog(props.row, 'analise')"
                  />
                  <q-btn
                    flat
                    round
                    color="accent"
                    icon="upload_file"
                    @click="openUploadDialog(props.row)"
                  />
                  <q-btn
                    flat
                    round
                    color="negative"
                    icon="delete"
                    @click="confirmDelete(props.row, 'analise')"
                  />
                </q-td>
              </template>
            </q-table>
          </q-tab-panel>
          
          <!-- ABA RELATÓRIOS -->
          <q-tab-panel name="relatorios">
            <div class="row q-gutter-md q-mb-md">
              <q-btn
                color="info"
                label="Atualizar Relatórios"
                icon="refresh"
                @click="loadRelatorios"
              />
            </div>
            
            <!-- Cronograma de Aplicações -->
            <q-card class="q-mb-md">
              <q-card-section>
                <div class="text-h6">Cronograma de Aplicações (Próximos 30 dias)</div>
              </q-card-section>
              <q-card-section>
                <q-table
                  :rows="manejoStore.cronograma"
                  :columns="cronogramaColumns"
                  row-key="manejo_id"
                  flat
                  :pagination="{ rowsPerPage: 0 }"
                >
                  <template v-slot:body-cell-status="props">
                    <q-td :props="props">
                      <q-chip
                        :color="manejoStore.getCronogramaStatusColor(props.row.status)"
                        text-color="white"
                        dense
                      >
                        {{ props.row.status }}
                      </q-chip>
                    </q-td>
                  </template>
                </q-table>
              </q-card-section>
            </q-card>
            
            <!-- Capacidade vs Ocupação -->
            <q-card class="q-mb-md">
              <q-card-section>
                <div class="text-h6">Capacidade vs Ocupação</div>
              </q-card-section>
              <q-card-section>
                <q-table
                  :rows="manejoStore.capacidadeOcupacao"
                  :columns="capacidadeColumns"
                  row-key="terreno_id"
                  flat
                  :pagination="{ rowsPerPage: 0 }"
                >
                  <template v-slot:body-cell-ocupacao="props">
                    <q-td :props="props">
                      <div class="row items-center">
                        <span class="q-mr-sm">{{ props.row.taxa_ocupacao }}%</span>
                        <q-linear-progress
                          :value="props.row.taxa_ocupacao / 100"
                          :color="props.row.taxa_ocupacao > 100 ? 'negative' : 'positive'"
                          size="lg"
                          class="col"
                        />
                      </div>
                    </q-td>
                  </template>
                  <template v-slot:body-cell-status_lotacao="props">
                    <q-td :props="props">
                      <q-chip
                        :color="manejoStore.getStatusLotacaoColor(props.row.status_lotacao)"
                        text-color="white"
                        dense
                      >
                        {{ getStatusLotacaoLabel(props.row.status_lotacao) }}
                      </q-chip>
                    </q-td>
                  </template>
                </q-table>
              </q-card-section>
            </q-card>
            
            <!-- Histórico Nutricional -->
            <q-card>
              <q-card-section>
                <div class="text-h6">Histórico Nutricional</div>
              </q-card-section>
              <q-card-section>
                <q-table
                  :rows="manejoStore.historicoNutricional"
                  :columns="nutricionaColumns"
                  row-key="terreno_id"
                  flat
                  :pagination="{ rowsPerPage: 0 }"
                >
                  <template v-slot:body-cell-status_solo="props">
                    <q-td :props="props">
                      <q-chip
                        :color="manejoStore.getStatusSoloColor(props.row.status_solo)"
                        text-color="white"
                        dense
                      >
                        {{ getStatusSoloLabel(props.row.status_solo) }}
                      </q-chip>
                    </q-td>
                  </template>
                </q-table>
              </q-card-section>
            </q-card>
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>
    </q-card>

    <!-- Modal de Visualização -->
    <q-dialog v-model="viewDialog" persistent>
      <q-card style="width: 600px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6">
            Detalhes {{ getDialogTitle(viewType) }}
          </div>
        </q-card-section>
        <q-card-section v-if="viewData">
          <!-- APLICAÇÃO -->
          <q-list v-if="viewType === 'aplicacao'">
            <q-item>
              <q-item-section>
                <q-item-label caption>Terreno</q-item-label>
                <q-item-label>{{ viewData.terreno_nome }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label caption>Produto</q-item-label>
                <q-item-label>{{ viewData.produto_nome }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label caption>Tipo de Manejo</q-item-label>
                <q-item-label>{{ manejoStore.getManejoLabel(viewData.TIPO_MANEJO) }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label caption>Data de Aplicação</q-item-label>
                <q-item-label>{{ formatDate(viewData.DATA_APLICACAO) }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label caption>Quantidade</q-item-label>
                <q-item-label>{{ viewData.QUANTIDADE }} {{ viewData.UNIDADE_MEDIDA }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="viewData.PERIODO_CARENCIA">
              <q-item-section>
                <q-item-label caption>Período de Carência</q-item-label>
                <q-item-label>{{ viewData.PERIODO_CARENCIA }} dias</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="viewData.DATA_LIBERACAO">
              <q-item-section>
                <q-item-label caption>Data de Liberação</q-item-label>
                <q-item-label>{{ formatDate(viewData.DATA_LIBERACAO) }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="viewData.OBSERVACOES">
              <q-item-section>
                <q-item-label caption>Observações</q-item-label>
                <q-item-label>{{ viewData.OBSERVACOES }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>

          <!-- PRODUTO -->
          <q-list v-if="viewType === 'produto'">
            <q-item>
              <q-item-section>
                <q-item-label caption>Nome</q-item-label>
                <q-item-label>{{ viewData.NOME }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label caption>Tipo</q-item-label>
                <q-item-label>{{ manejoStore.getTipoLabel(viewData.TIPO_PRODUTO) }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="viewData.PRINCIPIO_ATIVO">
              <q-item-section>
                <q-item-label caption>Princípio Ativo</q-item-label>
                <q-item-label>{{ viewData.PRINCIPIO_ATIVO }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label caption>Unidade de Medida</q-item-label>
                <q-item-label>{{ viewData.UNIDADE_MEDIDA }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="viewData.FABRICANTE">
              <q-item-section>
                <q-item-label caption>Fabricante</q-item-label>
                <q-item-label>{{ viewData.FABRICANTE }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="viewData.OBSERVACOES">
              <q-item-section>
                <q-item-label caption>Observações</q-item-label>
                <q-item-label>{{ viewData.OBSERVACOES }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>

          <!-- ANÁLISE -->
          <q-list v-if="viewType === 'analise'">
            <q-item>
              <q-item-section>
                <q-item-label caption>Terreno</q-item-label>
                <q-item-label>{{ viewData.terreno_nome }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label caption>Data da Coleta</q-item-label>
                <q-item-label>{{ formatDate(viewData.DATA_COLETA) }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="viewData.LABORATORIO">
              <q-item-section>
                <q-item-label caption>Laboratório</q-item-label>
                <q-item-label>{{ viewData.LABORATORIO }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="viewData.PH_AGUA">
              <q-item-section>
                <q-item-label caption>pH (água)</q-item-label>
                <q-item-label>{{ viewData.PH_AGUA.toFixed(1) }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="viewData.SATURACAO_BASES">
              <q-item-section>
                <q-item-label caption>Saturação por Bases</q-item-label>
                <q-item-label>{{ viewData.SATURACAO_BASES.toFixed(1) }}%</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="viewData.MATERIA_ORGANICA">
              <q-item-section>
                <q-item-label caption>Matéria Orgânica</q-item-label>
                <q-item-label>{{ viewData.MATERIA_ORGANICA.toFixed(1) }}%</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="viewData.RECOMENDACOES">
              <q-item-section>
                <q-item-label caption>Recomendações</q-item-label>
                <q-item-label>{{ viewData.RECOMENDACOES }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            label="Editar"
            color="primary"
            @click="editFromView"
          />
          <q-btn
            flat
            label="Fechar"
            color="gray"
            @click="viewDialog = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Modal de Cadastro/Edição -->
    <q-dialog v-model="dialog" persistent>
      <q-card style="width: 700px; max-width: 90vw">
        <q-form @submit="saveRecord">
          <q-card-section>
            <div class="text-h6">
              {{ form.ID ? 'Editar' : 'Cadastrar' }} {{ getDialogTitle(dialogType) }}
            </div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            
            <!-- FORMULÁRIO APLICAÇÃO -->
            <template v-if="dialogType === 'aplicacao'">
              <div class="row q-gutter-md">
                <q-select
                  v-model="form.ID_TERRENO"
                  :options="terrenoOptions"
                  label="Terreno *"
                  :rules="[val => !!val || 'Terreno é obrigatório']"
                  class="col-5"
                />
                <q-select
                  v-model="form.ID_PRODUTO"
                  :options="produtoOptions"
                  label="Produto *"
                  :rules="[val => !!val || 'Produto é obrigatório']"
                  class="col-5"
                />
              </div>
              
              <div class="row q-gutter-md q-mt-sm">
                <q-select
                  v-model="form.TIPO_MANEJO"
                  :options="manejoStore.tiposManejo"
                  label="Tipo de Manejo *"
                  :rules="[val => !!val || 'Tipo é obrigatório']"
                  class="col-5"
                />
                <calendario-component
                  v-model="form.DATA_APLICACAO"
                  label="Data de Aplicação *"
                  :rules="[val => !!val || 'Data é obrigatória']"
                  class="col-5"
                />
              </div>

              <div class="row q-gutter-md q-mt-sm">
                <q-input
                  v-model.number="form.QUANTIDADE"
                  label="Quantidade *"
                  type="number"
                  step="0.01"
                  :rules="[val => val > 0 || 'Quantidade deve ser maior que 0']"
                  class="col-3"
                />
                <q-input
                  v-model="form.UNIDADE_MEDIDA"
                  label="Unidade *"
                  :rules="[val => !!val || 'Unidade é obrigatória']"
                  class="col-3"
                />
                <q-input
                  v-model.number="form.DOSE_HECTARE"
                  label="Dose/ha"
                  type="number"
                  step="0.01"
                  class="col-3"
                />
                <q-input
                  v-model.number="form.AREA_APLICADA"
                  label="Área (ha)"
                  type="number"
                  step="0.01"
                  class="col-3"
                />
              </div>

              <div class="row q-gutter-md q-mt-sm">
                <q-input
                  v-model.number="form.CUSTO_TOTAL"
                  label="Custo Total"
                  type="number"
                  step="0.01"
                  class="col-4"
                />
                <q-input
                  v-model.number="form.PERIODO_CARENCIA"
                  label="Carência (dias)"
                  type="number"
                  class="col-3"
                />
                <q-input
                  v-model="form.EQUIPAMENTO_UTILIZADO"
                  label="Equipamento"
                  class="col-4"
                />
              </div>

              <q-input
                v-model="form.OBSERVACOES"
                label="Observações"
                type="textarea"
                rows="3"
                class="q-mt-sm"
              />
            </template>

            <!-- FORMULÁRIO PRODUTO -->
            <template v-if="dialogType === 'produto'">
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

              <div class="row q-gutter-md q-mt-sm">
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

              <q-input
                v-model="form.REGISTRO_MINISTERIO"
                label="Registro Ministério"
                class="q-mt-sm"
              />

              <q-input
                v-model="form.OBSERVACOES"
                label="Observações"
                type="textarea"
                rows="3"
                class="q-mt-sm"
              />
            </template>

            <!-- FORMULÁRIO ANÁLISE -->
            <template v-if="dialogType === 'analise'">
              <div class="row q-gutter-md">
                <q-select
                  v-model="form.ID_TERRENO"
                  :options="terrenoOptions"
                  label="Terreno *"
                  :rules="[val => !!val || 'Terreno é obrigatório']"
                  class="col-5"
                />
                <calendario-component
                  v-model="form.DATA_COLETA"
                  label="Data da Coleta *"
                  :rules="[val => !!val || 'Data é obrigatória']"
                  class="col-3"
                />
                <q-input
                  v-model="form.LABORATORIO"
                  label="Laboratório"
                  class="col-3"
                />
              </div>

              <div class="text-subtitle2 q-mt-md q-mb-sm">Parâmetros Químicos</div>
              <div class="row q-gutter-md">
                <q-input
                  v-model.number="form.PH_AGUA"
                  label="pH (água)"
                  type="number"
                  step="0.1"
                  class="col-2"
                />
                <q-input
                  v-model.number="form.PH_CACL2"
                  label="pH (CaCl2)"
                  type="number"
                  step="0.1"
                  class="col-2"
                />
                <q-input
                  v-model.number="form.MATERIA_ORGANICA"
                  label="M.O. (%)"
                  type="number"
                  step="0.1"
                  class="col-2"
                />
                <q-input
                  v-model.number="form.SATURACAO_BASES"
                  label="Sat. Bases (%)"
                  type="number"
                  step="0.1"
                  class="col-2"
                />
              </div>

              <div class="row q-gutter-md q-mt-sm">
                <q-input
                  v-model.number="form.FOSFORO"
                  label="Fósforo (mg/dm³)"
                  type="number"
                  step="0.1"
                  class="col-3"
                />
                <q-input
                  v-model.number="form.POTASSIO"
                  label="Potássio (cmolc/dm³)"
                  type="number"
                  step="0.1"
                  class="col-3"
                />
                <q-input
                  v-model.number="form.CALCIO"
                  label="Cálcio (cmolc/dm³)"
                  type="number"
                  step="0.1"
                  class="col-3"
                />
                <q-input
                  v-model.number="form.MAGNESIO"
                  label="Magnésio (cmolc/dm³)"
                  type="number"
                  step="0.1"
                  class="col-3"
                />
              </div>

              <q-input
                v-model="form.RECOMENDACOES"
                label="Recomendações"
                type="textarea"
                rows="3"
                class="q-mt-sm"
              />

              <q-input
                v-model="form.OBSERVACOES"
                label="Observações"
                type="textarea"
                rows="2"
                class="q-mt-sm"
              />
            </template>

          </q-card-section>
          <q-card-actions align="right">
            <q-btn
              flat
              label="Cancelar"
              color="gray"
              @click="dialog = false"
            />
            <q-btn
              type="submit"
              color="primary"
              label="Salvar"
              :disable="manejoStore.loading"
            />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- Modal de Upload de Laudo -->
    <q-dialog v-model="uploadDialog" persistent>
      <q-card style="width: 500px">
        <q-card-section>
          <div class="text-h6">Upload de Laudo</div>
        </q-card-section>
        <q-card-section>
          <q-file
            v-model="arquivoLaudo"
            label="Selecionar PDF"
            accept=".pdf"
            outlined
            @update:model-value="uploadLaudo"
          >
            <template v-slot:prepend>
              <q-icon name="attach_file" />
            </template>
          </q-file>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            label="Fechar"
            color="gray"
            @click="uploadDialog = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Modal de Terrenos Bloqueados -->
    <q-dialog v-model="bloqueadosDialog" persistent>
      <q-card style="width: 700px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6">Terrenos em Período de Carência</div>
        </q-card-section>
        <q-card-section>
          <q-list bordered>
            <q-item
              v-for="terreno in manejoStore.terrenosBloqueados"
              :key="`${terreno.terreno_id}-${terreno.data_aplicacao}`"
              clickable
            >
              <q-item-section avatar>
                <q-icon name="block" color="negative" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ terreno.terreno_nome }}</q-item-label>
                <q-item-label caption>{{ terreno.tipo_manejo }} - {{ terreno.data_aplicacao }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-item-label>{{ terreno.data_liberacao }}</q-item-label>
                <q-item-label caption>
                  <q-chip
                    color="negative"
                    text-color="white"
                    size="sm"
                  >
                    {{ terreno.dias_restantes }} dias
                  </q-chip>
                </q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="!manejoStore.terrenosBloqueados.length">
              <q-item-section>
                <q-item-label class="text-center text-grey">
                  Nenhum terreno bloqueado
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            label="Fechar"
            color="gray"
            @click="bloqueadosDialog = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Modal de Confirmação de Exclusão -->
    <q-dialog v-model="deleteDialog" persistent>
      <q-card>
        <q-card-section>
          <div class="text-h6">Confirmar Exclusão</div>
        </q-card-section>
        <q-card-section>
          Deseja excluir este registro?
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancelar"
            color="gray"
            @click="deleteDialog = false"
          />
          <q-btn
            color="negative"
            label="Excluir"
            @click="performDelete"
            :disable="manejoStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '../stores/auth'
import { useManejoStore } from '../stores/manejo'
import { useTerrenoStore } from '../stores/terreno'
import CalendarioComponent from '../components/CalendarioComponent.vue'
import { formatDate, prepareFormData } from '../utils/dateUtils'

const $q = useQuasar()
const authStore = useAuthStore()
const manejoStore = useManejoStore()
const terrenoStore = useTerrenoStore()

// Estado da interface
const activeTab = ref('aplicacoes')
const dialog = ref(false)
const viewDialog = ref(false)
const uploadDialog = ref(false)
const bloqueadosDialog = ref(false)
const deleteDialog = ref(false)
const dialogType = ref('aplicacao')
const viewType = ref('aplicacao')
const viewData = ref(null)
const recordToDelete = ref(null)
const deleteType = ref('aplicacao')
const selectedAnalise = ref(null)
const arquivoLaudo = ref(null)

// Opções
const terrenoOptions = ref([])
const produtoOptions = ref([])

// Formulário
const form = ref({})

// Colunas das tabelas
const aplicacaoColumns = [
  { name: 'terreno_nome', label: 'Terreno', field: 'terreno_nome', sortable: true, align: 'left' },
  { name: 'produto_nome', label: 'Produto', field: 'produto_nome', sortable: true, align: 'left' },
  { name: 'DATA_APLICACAO', label: 'Data', field: 'DATA_APLICACAO', sortable: true, align: 'left' },
  { name: 'tipo', label: 'Tipo', field: 'TIPO_MANEJO', sortable: true, align: 'center' },
  { name: 'QUANTIDADE', label: 'Quantidade', field: 'QUANTIDADE', sortable: true, align: 'left' },
  { name: 'status', label: 'Status', field: 'status', sortable: false, align: 'center' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

const produtoColumns = [
  { name: 'NOME', label: 'Nome', field: 'NOME', sortable: true, align: 'left' },
  { name: 'tipo', label: 'Tipo', field: 'TIPO_PRODUTO', sortable: true, align: 'center' },
  { name: 'UNIDADE_MEDIDA', label: 'Unidade', field: 'UNIDADE_MEDIDA', sortable: true, align: 'left' },
  { name: 'FABRICANTE', label: 'Fabricante', field: 'FABRICANTE', sortable: true, align: 'left' },
  { name: 'ativo', label: 'Ativo', field: 'ATIVO', sortable: true, align: 'center' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

const analiseColumns = [
  { name: 'terreno_nome', label: 'Terreno', field: 'terreno_nome', sortable: true, align: 'left' },
  { name: 'DATA_COLETA', label: 'Data Coleta', field: 'DATA_COLETA', sortable: true, align: 'left' },
  { name: 'ph', label: 'pH', field: 'PH_AGUA', sortable: true, align: 'center' },
  { name: 'saturacao', label: 'Sat. Bases', field: 'SATURACAO_BASES', sortable: true, align: 'center' },
  { name: 'LABORATORIO', label: 'Laboratório', field: 'LABORATORIO', sortable: true, align: 'left' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

const cronogramaColumns = [
  { name: 'terreno_nome', label: 'Terreno', field: 'terreno_nome', align: 'left' },
  { name: 'tipo_manejo', label: 'Tipo', field: 'tipo_manejo', align: 'left' },
  { name: 'produto_nome', label: 'Produto', field: 'produto_nome', align: 'left' },
  { name: 'data_aplicacao', label: 'Aplicação', field: 'data_aplicacao', align: 'left' },
  { name: 'data_liberacao', label: 'Liberação', field: 'data_liberacao', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'center' }
]

const capacidadeColumns = [
  { name: 'terreno_nome', label: 'Terreno', field: 'terreno_nome', align: 'left' },
  { name: 'area_hectares', label: 'Área (ha)', field: 'area_hectares', align: 'left' },
  { name: 'capacidade_animais', label: 'Capacidade', field: 'capacidade_animais', align: 'center' },
  { name: 'animais_atuais', label: 'Animais Atuais', field: 'animais_atuais', align: 'center' },
  { name: 'ocupacao', label: 'Ocupação', field: 'taxa_ocupacao', align: 'center' },
  { name: 'status_lotacao', label: 'Status', field: 'status_lotacao', align: 'center' }
]

const nutricionaColumns = [
  { name: 'terreno_nome', label: 'Terreno', field: 'terreno_nome', align: 'left' },
  { name: 'ultima_analise', label: 'Última Análise', field: 'ultima_analise', align: 'left' },
  { name: 'ph_atual', label: 'pH', field: 'ph_atual', align: 'center' },
  { name: 'total_aplicacoes', label: 'Aplicações', field: 'total_aplicacoes', align: 'center' },
  { name: 'custo_total_ano', label: 'Custo Ano', field: 'custo_total_ano', align: 'right' },
  { name: 'status_solo', label: 'Status Solo', field: 'status_solo', align: 'center' }
]

// Funções
async function loadOptions() {
  try {
    await terrenoStore.fetchTerrenos({ limit: 100 })
    terrenoOptions.value = terrenoStore.terrenos.map(t => ({
      value: t.ID,
      label: t.NOME
    }))
    
    produtoOptions.value = await manejoStore.loadProdutoOptions()
  } catch (error) {
    console.error('Erro ao carregar opções:', error)
  }
}

async function onFilterChange() {
  if (activeTab.value === 'aplicacoes') {
    await manejoStore.fetchAplicacoes()
  }
}

async function onFilterChangeProdutos() {
  await manejoStore.fetchProdutos()
}

async function onRequestAplicacoes(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  manejoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  await manejoStore.fetchAplicacoes(props)
}

async function onRequestProdutos(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  manejoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  await manejoStore.fetchProdutos(props)
}

async function onRequestAnalises(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  manejoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  await manejoStore.fetchAnalisesSolo(props)
}

function openDialog(record, type) {
  dialogType.value = type
  initializeForm(record, type)
  dialog.value = true
}

function initializeForm(record, type) {
  const baseForm = {
    ID: null,
    ID_USUARIO_CADASTRO: authStore.user.ID,
    ID_USUARIO_REGISTRO: authStore.user.ID
  }

  if (type === 'aplicacao') {
    // Encontrar objetos completos para os selects se for edição
    const terreno = record ? terrenoOptions.value.find(t => t.value === record.ID_TERRENO) : null
    const produto = record ? produtoOptions.value.find(p => p.value === record.ID_PRODUTO) : null
    const tipoManejo = record ? manejoStore.tiposManejo.find(t => t.value === record.TIPO_MANEJO) : null

    form.value = record ? {
      ...record,
      ID_TERRENO: terreno || record.ID_TERRENO,
      ID_PRODUTO: produto || record.ID_PRODUTO,
      TIPO_MANEJO: tipoManejo || record.TIPO_MANEJO,
      ID_USUARIO_REGISTRO: authStore.user.ID
    } : {
      ...baseForm,
      ID_TERRENO: null,
      ID_PRODUTO: null,
      TIPO_MANEJO: null,
      DATA_APLICACAO: '',
      QUANTIDADE: null,
      UNIDADE_MEDIDA: '',
      DOSE_HECTARE: null,
      AREA_APLICADA: null,
      CUSTO_TOTAL: null,
      PERIODO_CARENCIA: null,
      EQUIPAMENTO_UTILIZADO: '',
      OBSERVACOES: ''
    }
  } else if (type === 'produto') {
    const tipoProduto = record ? manejoStore.tiposProduto.find(t => t.value === record.TIPO_PRODUTO) : null

    form.value = record ? {
      ...record,
      TIPO_PRODUTO: tipoProduto || record.TIPO_PRODUTO,
      ID_USUARIO_CADASTRO: authStore.user.ID
    } : {
      ...baseForm,
      NOME: '',
      TIPO_PRODUTO: null,
      PRINCIPIO_ATIVO: '',
      CONCENTRACAO: '',
      UNIDADE_MEDIDA: '',
      FABRICANTE: '',
      REGISTRO_MINISTERIO: '',
      OBSERVACOES: ''
    }
  } else if (type === 'analise') {
    const terreno = record ? terrenoOptions.value.find(t => t.value === record.ID_TERRENO) : null

    form.value = record ? {
      ...record,
      ID_TERRENO: terreno || record.ID_TERRENO,
      ID_USUARIO_CADASTRO: authStore.user.ID
    } : {
      ...baseForm,
      ID_TERRENO: null,
      DATA_COLETA: '',
      DATA_RESULTADO: '',
      LABORATORIO: '',
      PH_AGUA: null,
      PH_CACL2: null,
      MATERIA_ORGANICA: null,
      FOSFORO: null,
      POTASSIO: null,
      CALCIO: null,
      MAGNESIO: null,
      SATURACAO_BASES: null,
      OBSERVACOES: '',
      RECOMENDACOES: ''
    }
  }
}

async function saveRecord() {
  try {
    const dateFields = ['DATA_APLICACAO', 'DATA_COLETA', 'DATA_RESULTADO']
    const formData = prepareFormData(form.value, dateFields)

    if (dialogType.value === 'aplicacao') {
      if (formData.ID) {
        await manejoStore.updateAplicacao(formData.ID, formData)
        $q.notify({ type: 'positive', message: 'Aplicação atualizada com sucesso' })
      } else {
        await manejoStore.createAplicacao(formData)
        $q.notify({ type: 'positive', message: 'Aplicação criada com sucesso' })
      }
    } else if (dialogType.value === 'produto') {
      if (formData.ID) {
        await manejoStore.updateProduto(formData.ID, formData)
        $q.notify({ type: 'positive', message: 'Produto atualizado com sucesso' })
      } else {
        await manejoStore.createProduto(formData)
        $q.notify({ type: 'positive', message: 'Produto criado com sucesso' })
      }
    } else if (dialogType.value === 'analise') {
      if (formData.ID) {
        await manejoStore.updateAnaliseSolo(formData.ID, formData)
        $q.notify({ type: 'positive', message: 'Análise atualizada com sucesso' })
      } else {
        await manejoStore.createAnaliseSolo(formData)
        $q.notify({ type: 'positive', message: 'Análise criada com sucesso' })
      }
    }
    dialog.value = false
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

function viewRecord(record, type) {
  viewData.value = record
  viewType.value = type
  viewDialog.value = true
}

function editFromView() {
  viewDialog.value = false
  openDialog(viewData.value, viewType.value)
}

function confirmDelete(record, type) {
  recordToDelete.value = record
  deleteType.value = type
  deleteDialog.value = true
}

async function performDelete() {
  try {
    if (deleteType.value === 'aplicacao') {
      await manejoStore.deleteAplicacao(recordToDelete.value.ID)
    } else if (deleteType.value === 'produto') {
      await manejoStore.deleteProduto(recordToDelete.value.ID)
    } else if (deleteType.value === 'analise') {
      // Assumindo que há método para deletar análise (implementar no store)
      await manejoStore.deleteAnaliseSolo(recordToDelete.value.ID)
    }
    $q.notify({ type: 'positive', message: 'Registro excluído com sucesso' })
    deleteDialog.value = false
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

function openUploadDialog(analise) {
  selectedAnalise.value = analise
  uploadDialog.value = true
}

async function uploadLaudo() {
  if (!arquivoLaudo.value || !selectedAnalise.value) return
  
  try {
    await manejoStore.uploadLaudo(selectedAnalise.value.ID, arquivoLaudo.value)
    $q.notify({ type: 'positive', message: 'Laudo enviado com sucesso' })
    arquivoLaudo.value = null
    uploadDialog.value = false
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

async function showTerrenosBloqueados() {
  await manejoStore.fetchTerrenosBloqueados()
  bloqueadosDialog.value = true
}

async function loadRelatorios() {
  try {
    await Promise.all([
      manejoStore.fetchCronograma(),
      manejoStore.fetchCapacidadeOcupacao(),
      manejoStore.fetchHistoricoNutricional()
    ])
    $q.notify({ type: 'positive', message: 'Relatórios atualizados' })
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

function filterTerrenos(val, update) {
  update(() => {
    if (val === '') {
      terrenoOptions.value = terrenoStore.terrenos.map(t => ({ value: t.ID, label: t.NOME }))
    } else {
      const needle = val.toLowerCase()
      const allTerrenos = terrenoStore.terrenos.map(t => ({ value: t.ID, label: t.NOME }))
      terrenoOptions.value = allTerrenos.filter(v => v.label.toLowerCase().indexOf(needle) > -1)
    }
  })
}

// Funções auxiliares para cores e labels
function getTipoManejoColor(tipo) {
  const colors = {
    'ADUBACAO': 'positive',
    'CALAGEM': 'secondary',
    'PLANTIO': 'accent',
    'APLICACAO_DEFENSIVO': 'warning',
    'ROÇADA': 'info',
    'IRRIGACAO': 'primary'
  }
  return colors[tipo] || 'grey'
}

function getTipoProdutoColor(tipo) {
  const colors = {
    'FERTILIZANTE': 'positive',
    'DEFENSIVO': 'warning',
    'CORRETIVO': 'secondary',
    'SEMENTE': 'accent'
  }
  return colors[tipo] || 'grey'
}

function getDialogTitle(type) {
  const titles = {
    'aplicacao': 'Aplicação',
    'produto': 'Produto',
    'analise': 'Análise de Solo'
  }
  return titles[type] || 'Registro'
}

function getStatusLotacaoLabel(status) {
  const labels = {
    'ADEQUADA': 'Adequada',
    'SOBRELOTADO': 'Sobrelotado',
    'SUBLOTADO': 'Sublotado',
    'SEM_LIMITE': 'Sem Limite'
  }
  return labels[status] || status
}

function getStatusSoloLabel(status) {
  const labels = {
    'BOM': 'Bom',
    'REGULAR': 'Regular',
    'RUIM': 'Ruim',
    'SEM_ANALISE': 'Sem Análise'
  }
  return labels[status] || status
}

// Watchers para mudança de aba
async function onTabChange() {
  if (activeTab.value === 'aplicacoes') {
    await manejoStore.fetchAplicacoes()
  } else if (activeTab.value === 'produtos') {
    await manejoStore.fetchProdutos()
  } else if (activeTab.value === 'analises') {
    await manejoStore.fetchAnalisesSolo()
  } else if (activeTab.value === 'relatorios') {
    await loadRelatorios()
  }
}

// Inicialização
onMounted(async () => {
  await loadOptions()
  await onTabChange()
  await manejoStore.fetchTerrenosBloqueados() // Para badge de alerta
})

watch(activeTab, onTabChange)
</script>