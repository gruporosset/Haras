<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md text-primary">
      <q-icon name="medication" class="q-mr-sm" />
      Controle de Medicamentos
    </div>

    <q-card>
      <q-card-section>
        <!-- Alertas de Estoque -->
        <div v-if="medicamentoStore.alertasEstoque.length > 0" class="q-mt-md">
          <q-banner class="bg-warning text-dark">
            <template v-slot:avatar>
              <q-icon name="warning" />
            </template>
            {{ medicamentoStore.alertasEstoque.length }} medicamento(s) com alerta de estoque!
            <template v-slot:action>
              <q-btn
                flat
                label="Ver Alertas"
                @click="activeTab = 'alertas'"
              />
            </template>
          </q-banner>
        </div>
      </q-card-section>
      
      <q-card-section>
        <!-- Filtros Gerais -->
        <div class="col-12 q-mb-md">
          <q-card flat bordered class="q-pa-md">
            <div class="row q-gutter-md q-mb-md">
              <div class="col-md-3 col-12">
                <q-input
                  v-model="medicamentoStore.filters.nome"
                  label="Filtrar por Nome"
                  clearable
                  @update:model-value="onFilterChange"
                  :debounce="300"
                  class="col-3"
                />
              </div>
              <div class="col-md-3 col-12">
                <q-select
                  v-model="medicamentoStore.filters.forma_farmaceutica"
                  :options="medicamentoStore.formasFarmaceuticas"
                  label="Forma Farmacêutica"
                  clearable
                  @update:model-value="onFilterChange"
                  class="col-2"
                />
              </div>
              <div class="col-md-3 col-12">
                <q-toggle
                  v-model="medicamentoStore.filters.estoque_baixo"
                  label="Apenas Estoque Baixo"
                  @update:model-value="onFilterChange"
                />
              </div>
            </div>
          </q-card>
        </div>
        
        <!-- Estatísticas Rápidas -->
        <div class="row q-gutter-md q-mb-md">
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-primary">{{ medicamentoStore.estatisticasGerais.totalMedicamentos }}</div>
              <div class="text-caption">Total Medicamentos</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-positive">{{ medicamentoStore.estatisticasGerais.comEstoque }}</div>
              <div class="text-caption">Com Estoque</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-warning">{{ medicamentoStore.estatisticasGerais.alertas }}</div>
              <div class="text-caption">Alertas</div>
            </q-card-section>
          </q-card>
          <q-card flat bordered class="col">
            <q-card-section class="text-center">
              <div class="text-h4 text-accent">R$ {{ medicamentoStore.estatisticasGerais.valorTotal.toFixed(2) }}</div>
              <div class="text-caption">Valor Estoque</div>
            </q-card-section>
          </q-card>
        </div>
        
        <!-- Abas -->
        <q-tabs v-model="activeTab" class="q-mb-md">
          <q-tab name="medicamentos" label="Medicamentos" />
          <q-tab name="estoque" label="Controle de Estoque" />
          <q-tab name="aplicacoes" label="Aplicações" />
          <q-tab name="movimentacoes" label="Movimentações" />
          <q-tab name="alertas" label="Alertas" :badge="medicamentoStore.alertasEstoque.length || undefined" />
          <q-tab name="relatorios" label="Relatórios" />
        </q-tabs>
        
        <q-tab-panels v-model="activeTab" animated>
            <!-- ABA MEDICAMENTOS -->
            <q-tab-panel name="medicamentos">
            <div class="row q-gutter-md q-mb-md">
                <q-btn
                color="primary"
                label="Novo Medicamento"
                icon="add"
                @click="openDialog(null, 'medicamento')"
                />
            </div>

            <q-table
                :rows="medicamentoStore.medicamentos"
                :columns="medicamentoColumns"
                row-key="ID"
                :loading="medicamentoStore.loading"
                :pagination="medicamentoStore.pagination"
                @request="onRequestMedicamentos"
                binary-state-sort
            >
                <template v-slot:body-cell-forma="props">
                <q-td :props="props">
                    <q-chip
                    :color="getFormaColor(props.row.FORMA_FARMACEUTICA)"
                    text-color="white"
                    dense
                    >
                    {{ medicamentoStore.getFormaLabel(props.row.FORMA_FARMACEUTICA) }}
                    </q-chip>
                </q-td>
                </template>
                <template v-slot:body-cell-estoque="props">
                <q-td :props="props">
                    <div class="row items-center">
                    <span>{{ props.row.ESTOQUE_ATUAL }} {{ props.row.UNIDADE_MEDIDA }}</span>
                    <q-icon
                        v-if="props.row.status_estoque !== 'OK'"
                        :name="getStatusIcon(props.row.status_estoque)"
                        :color="medicamentoStore.getStatusEstoqueColor(props.row.status_estoque)"
                        class="q-ml-sm"
                        size="sm"
                    />
                    </div>
                </q-td>
                </template>
                <template v-slot:body-cell-status="props">
                <q-td :props="props">
                    <q-chip
                    :color="medicamentoStore.getStatusEstoqueColor(props.row.status_estoque)"
                    text-color="white"
                    dense
                    >
                    {{ medicamentoStore.getStatusEstoqueLabel(props.row.status_estoque) }}
                    </q-chip>
                </q-td>
                </template>
                <template v-slot:body-cell-valor="props">
                <q-td :props="props">
                    <span v-if="props.row.valor_estoque">
                    R$ {{ props.row.valor_estoque.toFixed(2) }}
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
                    @click="viewRecord(props.row, 'medicamento')"
                    />
                    <q-btn
                    flat
                    round
                    color="primary"
                    icon="edit"
                    @click="openDialog(props.row, 'medicamento')"
                    />
                    <q-btn
                    flat
                    round
                    color="positive"
                    icon="add_shopping_cart"
                    @click="openEstoqueDialog(props.row, 'entrada')"
                    :disable="props.row.ATIVO === 'N'"
                    />
                    <q-btn
                    flat
                    round
                    color="negative"
                    icon="delete"
                    @click="confirmDelete(props.row, 'medicamento')"
                    />
                </q-td>
                </template>
            </q-table>
            </q-tab-panel>

            <!-- ABA CONTROLE DE ESTOQUE -->
            <q-tab-panel name="estoque">
            <div class="row q-gutter-md q-mb-md">
                <q-btn
                color="positive"
                label="Entrada de Estoque"
                icon="shopping_cart"
                @click="openEstoqueDialog(null, 'entrada')"
                />
                <q-btn
                color="secondary"
                label="Aplicar Medicamento"
                icon="medication"
                @click="openAplicacaoDialog()"
                />
            </div>
            
            <!-- Resumo de Estoque -->
            <q-card flat bordered class="q-mb-md">
                <q-card-section>
                <div class="text-h6">Resumo do Estoque</div>
                <div class="row q-gutter-md q-mt-md">
                    <div 
                    v-for="medicamento in medicamentoStore.medicamentosComEstoque.slice(0, 6)" 
                    :key="medicamento.ID"
                    class="col-2"
                    >
                    <q-card flat bordered>
                        <q-card-section class="text-center">
                        <div class="text-subtitle2">{{ medicamento.NOME }}</div>
                        <div class="text-h6" :class="getEstoqueColorClass(medicamento)">
                            {{ medicamento.ESTOQUE_ATUAL }} {{ medicamento.UNIDADE_MEDIDA }}
                        </div>
                        <q-linear-progress
                            :value="medicamento.ESTOQUE_ATUAL / (medicamento.ESTOQUE_MINIMO || 1)"
                            :color="getEstoqueProgressColor(medicamento)"
                            size="sm"
                            class="q-mt-sm"
                        />
                        </q-card-section>
                    </q-card>
                    </div>
                </div>
                </q-card-section>
            </q-card>
            
            <!-- Últimas Movimentações -->
            <q-card flat bordered>
                <q-card-section>
                <div class="text-h6">Últimas Movimentações</div>
                <q-table
                    :rows="medicamentoStore.movimentacoes.slice(0, 10)"
                    :columns="movimentacaoColumns.slice(0, 6)"
                    row-key="ID"
                    flat
                    :pagination="{ rowsPerPage: 10 }"
                >
                    <template v-slot:body-cell-tipo="props">
                    <q-td :props="props">
                        <q-chip
                        :color="medicamentoStore.getTipoMovimentacaoColor(props.row.TIPO_MOVIMENTACAO)"
                        text-color="white"
                        dense
                        >
                        {{ medicamentoStore.getTipoMovimentacaoLabel(props.row.TIPO_MOVIMENTACAO) }}
                        </q-chip>
                    </q-td>
                    </template>
                </q-table>
                </q-card-section>
            </q-card>
            </q-tab-panel>            

            <!-- ABA APLICAÇÕES RÁPIDAS -->
            <q-tab-panel name="aplicacoes">
            <div class="q-mb-md">
                <div class="text-h6">Aplicação Rápida de Medicamentos</div>
                <div class="text-caption">Para aplicações simples com baixa automática do estoque</div>
            </div>
            
            <q-form @submit="aplicarMedicamento" class="q-gutter-md">
                <div class="row q-gutter-md">
                <q-select
                    v-model="aplicacaoForm.ID_ANIMAL"
                    :options="animalOptions"
                    label="Animal"
                    use-input
                    @filter="filterAnimais"
                    class="col-3"
                    :rules="[val => !!val || 'Selecione um animal']"
                />
                <q-select
                    v-model="aplicacaoForm.ID_MEDICAMENTO"
                    :options="medicamentoOptions"
                    label="Medicamento"
                    use-input
                    @filter="filterMedicamentos"
                    @update:model-value="onMedicamentoSelect"
                    class="col-3"
                    :rules="[val => !!val || 'Selecione um medicamento']"
                />
                <q-input
                    v-model.number="aplicacaoForm.QUANTIDADE_APLICADA"
                    label="Quantidade"
                    type="number"
                    step="0.1"
                    :suffix="medicamentoSelecionado?.unidade || ''"
                    class="col-2"
                    :rules="[val => val > 0 || 'Quantidade deve ser maior que zero']"
                />
                <q-input
                    v-model="aplicacaoForm.VETERINARIO_RESPONSAVEL"
                    label="Veterinário"
                    class="col-3"
                />
                </div>
                
                <div class="row q-gutter-md">
                <q-input
                    v-model="aplicacaoForm.OBSERVACOES"
                    label="Observações"
                    type="textarea"
                    rows="2"
                    class="col"
                />
                </div>
                
                <!-- Validação de Estoque -->
                <div v-if="medicamentoSelecionado && aplicacaoForm.QUANTIDADE_APLICADA" class="q-mt-md">
                <q-banner
                    v-if="!estoqueValido.valido"
                    class="bg-negative text-white"
                >
                    <template v-slot:avatar>
                    <q-icon name="error" />
                    </template>
                    {{ estoqueValido.erro }}
                </q-banner>
                <q-banner
                    v-else
                    class="bg-positive text-white"
                >
                    <template v-slot:avatar>
                    <q-icon name="check_circle" />
                    </template>
                    Estoque suficiente. Restará: {{ (medicamentoSelecionado.estoque - aplicacaoForm.QUANTIDADE_APLICADA).toFixed(2) }} {{ medicamentoSelecionado.unidade }}
                </q-banner>
                </div>
                
                <div class="row">
                <q-btn
                    type="submit"
                    color="primary"
                    label="Aplicar Medicamento"
                    :disable="!estoqueValido.valido || medicamentoStore.loading"
                    :loading="medicamentoStore.loading"
                />
                <q-btn
                    flat
                    label="Limpar"
                    @click="resetAplicacaoForm"
                    class="q-ml-md"
                />
                </div>
            </q-form>
            </q-tab-panel>

            <!-- ABA MOVIMENTAÇÕES -->
            <q-tab-panel name="movimentacoes">
            <div class="row q-gutter-md q-mb-md">
                <q-select
                v-model="medicamentoStore.filters.medicamento_id"
                :options="medicamentoSelectOptions"
                label="Filtrar por Medicamento"
                clearable
                @update:model-value="onFilterChangeMovimentacoes"
                class="col-3"
                />
                <q-select
                v-model="medicamentoStore.filters.tipo"
                :options="medicamentoStore.tiposMovimentacao"
                label="Tipo"
                clearable
                @update:model-value="onFilterChangeMovimentacoes"
                class="col-2"
                />
                <calendario-component
                v-model="medicamentoStore.filters.data_inicio"
                label="Data Início"
                @update:model-value="onFilterChangeMovimentacoes"
                class="col-2"
                />
                <calendario-component
                v-model="medicamentoStore.filters.data_fim"
                label="Data Fim"
                @update:model-value="onFilterChangeMovimentacoes"
                class="col-2"
                />
            </div>

            <q-table
                :rows="medicamentoStore.movimentacoes"
                :columns="movimentacaoColumns"
                row-key="ID"
                :loading="medicamentoStore.loading"
                :pagination="medicamentoStore.pagination"
                @request="onRequestMovimentacoes"
                binary-state-sort
            >
                <template v-slot:body-cell-tipo="props">
                <q-td :props="props">
                    <q-chip
                    :color="medicamentoStore.getTipoMovimentacaoColor(props.row.TIPO_MOVIMENTACAO)"
                    text-color="white"
                    dense
                    >
                    {{ medicamentoStore.getTipoMovimentacaoLabel(props.row.TIPO_MOVIMENTACAO) }}
                    </q-chip>
                </q-td>
                </template>
                <template v-slot:body-cell-quantidade="props">
                <q-td :props="props">
                    <span :class="props.row.TIPO_MOVIMENTACAO === 'ENTRADA' ? 'text-positive' : 'text-negative'">
                    {{ props.row.TIPO_MOVIMENTACAO === 'ENTRADA' ? '+' : '-' }}{{ props.row.QUANTIDADE }}
                    </span>
                </q-td>
                </template>
            </q-table>
            </q-tab-panel>            

            
            <!-- ABA ALERTAS -->
            <q-tab-panel name="alertas">
            <div class="text-h6 q-mb-md">Alertas de Estoque e Validade</div>
            
            <q-list bordered>
                <q-item
                v-for="medicamento in medicamentoStore.alertasEstoque"
                :key="medicamento.ID"
                clickable
                >
                <q-item-section avatar>
                    <q-icon
                    :name="getStatusIcon(medicamento.status_estoque)"
                    :color="medicamentoStore.getStatusEstoqueColor(medicamento.status_estoque)"
                    />
                </q-item-section>
                <q-item-section>
                    <q-item-label>{{ medicamento.NOME }}</q-item-label>
                    <q-item-label caption>
                    {{ medicamentoStore.getStatusEstoqueLabel(medicamento.status_estoque) }}
                    <span v-if="medicamento.dias_vencimento !== null">
                        - {{ medicamento.dias_vencimento }} dias
                    </span>
                    </q-item-label>
                </q-item-section>
                <q-item-section side>
                    <div class="text-right">
                    <div>{{ medicamento.ESTOQUE_ATUAL }} {{ medicamento.UNIDADE_MEDIDA }}</div>
                    <div class="text-caption">
                        Mín: {{ medicamento.ESTOQUE_MINIMO }} {{ medicamento.UNIDADE_MEDIDA }}
                    </div>
                    </div>
                </q-item-section>
                <q-item-section side>
                    <q-btn
                    flat
                    round
                    color="positive"
                    icon="add_shopping_cart"
                    @click="openEstoqueDialog(medicamento, 'entrada')"
                    />
                </q-item-section>
                </q-item>
                <q-item v-if="!medicamentoStore.alertasEstoque.length">
                <q-item-section>
                    <q-item-label class="text-center text-positive">
                    <q-icon name="check_circle" size="md" />
                    <div>Todos os medicamentos estão com estoque adequado</div>
                    </q-item-label>
                </q-item-section>
                </q-item>
            </q-list>
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
            
            <!-- Previsão de Consumo -->
            <q-card class="q-mb-md">
                <q-card-section>
                <div class="text-h6">Previsão de Consumo</div>
                </q-card-section>
                <q-card-section>
                <q-table
                    :rows="medicamentoStore.previsaoConsumo"
                    :columns="previsaoColumns"
                    row-key="medicamento_id"
                    flat
                    :pagination="{ rowsPerPage: 0 }"
                >
                    <template v-slot:body-cell-recomendacao="props">
                    <q-td :props="props">
                        <q-chip
                        :color="medicamentoStore.getRecomendacaoColor(props.row.recomendacao)"
                        text-color="white"
                        dense
                        >
                        {{ medicamentoStore.getRecomendacaoLabel(props.row.recomendacao) }}
                        </q-chip>
                    </q-td>
                    </template>
                    <template v-slot:body-cell-dias_restantes="props">
                    <q-td :props="props">
                        <span :class="props.row.dias_restantes <= 7 ? 'text-negative' : props.row.dias_restantes <= 30 ? 'text-warning' : 'text-positive'">
                        {{ props.row.dias_restantes }} dias
                        </span>
                    </q-td>
                    </template>
                </q-table>
                </q-card-section>
            </q-card>
            </q-tab-panel>            

        </q-tab-panels>
      </q-card-section>
    </q-card>
    
    <!-- MODAIS -->

    <!-- Modal de Entrada de Estoque -->
    <q-dialog v-model="estoqueDialog" persistent>
        <q-card style="width: 600px; max-width: 90vw">
            <q-form @submit="salvarEstoque">
            <q-card-section>
                <div class="text-h6">Entrada de Estoque</div>
            </q-card-section>
            <q-card-section class="q-pt-none">
                <div class="row q-gutter-md">
                <q-select
                    v-if="!estoqueForm.ID_MEDICAMENTO"
                    v-model="estoqueForm.medicamento_select"
                    :options="medicamentoSelectOptions"
                    label="Medicamento"
                    use-input
                    @filter="filterMedicamentosEstoque"
                    @update:model-value="onMedicamentoEstoqueSelect"
                    class="col"
                    :rules="[val => !!val || 'Selecione um medicamento']"
                />
                <q-input
                    v-else
                    :model-value="estoqueForm.medicamento_nome"
                    label="Medicamento"
                    readonly
                    class="col"
                />
                </div>
                
                <div class="row q-gutter-md q-mt-md">
                <q-input
                    v-model.number="estoqueForm.QUANTIDADE"
                    label="Quantidade"
                    type="number"
                    step="0.1"
                    :suffix="estoqueForm.unidade_medida || ''"
                    class="col-4"
                    :rules="[val => val > 0 || 'Quantidade deve ser maior que zero']"
                />
                <q-input
                    v-model="estoqueForm.LOTE"
                    label="Lote"
                    class="col-4"
                    :rules="[val => !!val || 'Lote é obrigatório']"
                />
                <calendario-component
                    v-model="estoqueForm.DATA_VALIDADE"
                    label="Data Validade"
                    class="col-4"
                    :rules="[val => !!val || 'Data de validade é obrigatória']"
                />
                </div>
                
                <div class="row q-gutter-md q-mt-md">
                <q-input
                    v-model="estoqueForm.NOTA_FISCAL"
                    label="Nota Fiscal"
                    class="col-4"
                />
                <q-input
                    v-model="estoqueForm.FORNECEDOR"
                    label="Fornecedor"
                    class="col-4"
                />
                <q-input
                    v-model.number="estoqueForm.PRECO_UNITARIO"
                    label="Preço Unitário"
                    type="number"
                    step="0.01"
                    prefix="R$"
                    class="col-4"
                />
                </div>
                
                <div class="row q-mt-md">
                <q-input
                    v-model="estoqueForm.OBSERVACOES"
                    label="Observações"
                    type="textarea"
                    rows="2"
                    class="col"
                />
                </div>
            </q-card-section>
            <q-card-actions align="right">
                <q-btn flat label="Cancelar" color="grey" @click="estoqueDialog = false" />
                <q-btn type="submit" color="primary" label="Salvar" :loading="medicamentoStore.loading" />
            </q-card-actions>
            </q-form>
        </q-card>
    </q-dialog>

    <!-- Modal de Aplicação Simplificada -->
    <q-dialog v-model="aplicacaoDialog" persistent>
        <q-card style="width: 500px; max-width: 90vw">
            <q-form @submit="aplicarMedicamentoModal">
            <q-card-section>
                <div class="text-h6">Aplicação Rápida</div>
            </q-card-section>
            <q-card-section class="q-pt-none">
                <div class="row q-gutter-md">
                <q-select
                    v-model="aplicacaoModalForm.ID_ANIMAL"
                    :options="animalOptions"
                    label="Animal"
                    use-input
                    @filter="filterAnimais"
                    class="col"
                    :rules="[val => !!val || 'Selecione um animal']"
                />
                </div>
                <div class="row q-gutter-md q-mt-md">
                <q-select
                    v-model="aplicacaoModalForm.ID_MEDICAMENTO"
                    :options="medicamentoOptionsModal"
                    label="Medicamento"
                    use-input
                    @filter="filterMedicamentosModal"
                    class="col"
                    :rules="[val => !!val || 'Selecione um medicamento']"
                />
                </div>
                <div class="row q-gutter-md q-mt-md">
                <q-input
                    v-model.number="aplicacaoModalForm.QUANTIDADE_APLICADA"
                    label="Quantidade"
                    type="number"
                    step="0.1"
                    class="col-6"
                    :rules="[val => val > 0 || 'Quantidade deve ser maior que zero']"
                />
                <q-input
                    v-model="aplicacaoModalForm.VETERINARIO_RESPONSAVEL"
                    label="Veterinário"
                    class="col-6"
                />
                </div>
                <div class="row q-mt-md">
                <q-input
                    v-model="aplicacaoModalForm.OBSERVACOES"
                    label="Observações"
                    type="textarea"
                    rows="2"
                    class="col"
                />
                </div>
            </q-card-section>
            <q-card-actions align="right">
                <q-btn flat label="Cancelar" color="grey" @click="aplicacaoDialog = false" />
                <q-btn type="submit" color="primary" label="Aplicar" :loading="medicamentoStore.loading" />
            </q-card-actions>
            </q-form>
        </q-card>
    </q-dialog>

    <!-- Modal de Cadastro/Edição Medicamento -->
    <q-dialog v-model="dialog" persistent>
        <q-card style="width: 700px; max-width: 90vw">
            <q-form @submit="saveRecord">
            <q-card-section>
                <div class="text-h6">{{ form.ID ? 'Editar' : 'Cadastrar' }} Medicamento</div>
            </q-card-section>
            <q-card-section class="q-pt-none">
                <div class="row q-gutter-md">
                <q-input
                    v-model="form.NOME"
                    label="Nome do Medicamento"
                    class="col-6"
                    :rules="[val => !!val || 'Nome é obrigatório']"
                />
                <q-input
                    v-model="form.PRINCIPIO_ATIVO"
                    label="Princípio Ativo"
                    class="col-6"
                />
                </div>
                
                <div class="row q-gutter-md q-mt-md">
                <q-input
                    v-model="form.CONCENTRACAO"
                    label="Concentração"
                    class="col-4"
                />
                <q-select
                    v-model="form.FORMA_FARMACEUTICA"
                    :options="medicamentoStore.formasFarmaceuticas"
                    label="Forma Farmacêutica"
                    class="col-4"
                />
                <q-select
                    v-model="form.UNIDADE_MEDIDA"
                    :options="medicamentoStore.unidadesMedida"
                    label="Unidade de Medida"
                    class="col-4"
                    :rules="[val => !!val || 'Unidade é obrigatória']"
                />
                </div>
                
                <div class="row q-gutter-md q-mt-md">
                <q-input
                    v-model="form.FABRICANTE"
                    label="Fabricante"
                    class="col-6"
                />
                <q-input
                    v-model="form.REGISTRO_MAPA"
                    label="Registro MAPA"
                    class="col-6"
                />
                </div>
                
                <div class="row q-gutter-md q-mt-md">
                <q-input
                    v-model.number="form.ESTOQUE_MINIMO"
                    label="Estoque Mínimo"
                    type="number"
                    step="0.1"
                    class="col-4"
                />
                <q-input
                    v-model.number="form.PRECO_UNITARIO"
                    label="Preço Unitário"
                    type="number"
                    step="0.01"
                    prefix="R$"
                    class="col-4"
                />
                <q-input
                    v-model.number="form.PERIODO_CARENCIA"
                    label="Carência (dias)"
                    type="number"
                    class="col-4"
                />
                </div>
                
                <div class="row q-gutter-md q-mt-md">
                <q-toggle
                    v-model="form.REQUER_RECEITA_BOOL"
                    label="Requer Receita Veterinária"
                />
                </div>
                
                <div class="row q-mt-md">
                <q-input
                    v-model="form.OBSERVACOES"
                    label="Observações"
                    type="textarea"
                    rows="3"
                    class="col"
                />
                </div>
            </q-card-section>
            <q-card-actions align="right">
                <q-btn flat label="Cancelar" color="grey" @click="dialog = false" />
                <q-btn type="submit" color="primary" label="Salvar" :loading="medicamentoStore.loading" />
            </q-card-actions>
            </q-form>
        </q-card>
    </q-dialog>

    <!-- Modal de Visualização -->
    <q-dialog v-model="viewDialog" persistent>
        <q-card style="width: 600px; max-width: 90vw">
            <q-card-section>
            <div class="text-h6">Detalhes do Medicamento</div>
            </q-card-section>
            <q-card-section v-if="viewData">
            <div class="row q-gutter-md">
                <div class="col-6">
                <q-list>
                    <q-item>
                    <q-item-section>
                        <q-item-label overline>Nome</q-item-label>
                        <q-item-label>{{ viewData.NOME }}</q-item-label>
                    </q-item-section>
                    </q-item>
                    <q-item>
                    <q-item-section>
                        <q-item-label overline>Princípio Ativo</q-item-label>
                        <q-item-label>{{ viewData.PRINCIPIO_ATIVO || '-' }}</q-item-label>
                    </q-item-section>
                    </q-item>
                    <q-item>
                    <q-item-section>
                        <q-item-label overline>Estoque Atual</q-item-label>
                        <q-item-label>{{ viewData.ESTOQUE_ATUAL }} {{ viewData.UNIDADE_MEDIDA }}</q-item-label>
                    </q-item-section>
                    </q-item>
                </q-list>
                </div>
                <div class="col-6">
                <q-list>
                    <q-item>
                    <q-item-section>
                        <q-item-label overline>Fabricante</q-item-label>
                        <q-item-label>{{ viewData.FABRICANTE || '-' }}</q-item-label>
                    </q-item-section>
                    </q-item>
                    <q-item>
                    <q-item-section>
                        <q-item-label overline>Status</q-item-label>
                        <q-item-label>
                        <q-chip
                            :color="medicamentoStore.getStatusEstoqueColor(viewData.status_estoque)"
                            text-color="white"
                            dense
                        >
                            {{ medicamentoStore.getStatusEstoqueLabel(viewData.status_estoque) }}
                        </q-chip>
                        </q-item-label>
                    </q-item-section>
                    </q-item>
                    <q-item>
                    <q-item-section>
                        <q-item-label overline>Valor do Estoque</q-item-label>
                        <q-item-label>
                        {{ viewData.valor_estoque ? `R$ ${viewData.valor_estoque.toFixed(2)}` : '-' }}
                        </q-item-label>
                    </q-item-section>
                    </q-item>
                </q-list>
                </div>
            </div>
            </q-card-section>
            <q-card-actions align="right">
            <q-btn flat label="Editar" color="primary" @click="editFromView" />
            <q-btn flat label="Fechar" color="grey" @click="viewDialog = false" />
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
            Deseja excluir este medicamento?
            </q-card-section>
            <q-card-actions align="right">
            <q-btn flat label="Cancelar" color="grey" @click="deleteDialog = false" />
            <q-btn color="negative" label="Excluir" @click="performDelete" :loading="medicamentoStore.loading" />
            </q-card-actions>
        </q-card>
    </q-dialog>     
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '../stores/auth'
import { useMedicamentoStore } from '../stores/medicamento'
import { useAnimalStore } from '../stores/animal'
import CalendarioComponent from '../components/CalendarioComponent.vue'
import { prepareFormData } from '../utils/dateUtils'

const $q = useQuasar()
const authStore = useAuthStore()
const medicamentoStore = useMedicamentoStore()
const animalStore = useAnimalStore()

// Estado da interface
const activeTab = ref('medicamentos')
const dialog = ref(false)
const viewDialog = ref(false)
const estoqueDialog = ref(false)
const aplicacaoDialog = ref(false)
const deleteDialog = ref(false)
const viewData = ref(null)
const recordToDelete = ref(null)

// Opções
const animalOptions = ref([])
const medicamentoOptions = ref([])
const medicamentoOptionsModal = ref([])
const medicamentoSelectOptions = ref([])

// Formulários
const form = ref({})
const estoqueForm = ref({})
const aplicacaoForm = ref({
  ID_ANIMAL: null,
  ID_MEDICAMENTO: null,
  QUANTIDADE_APLICADA: null,
  VETERINARIO_RESPONSAVEL: '',
  OBSERVACOES: ''
})
const aplicacaoModalForm = ref({})

// Computed
const medicamentoSelecionado = computed(() => {
  if (!aplicacaoForm.value.ID_MEDICAMENTO?.value) return null
  return medicamentoOptions.value.find(m => m.value === aplicacaoForm.value.ID_MEDICAMENTO.value)
})

const estoqueValido = computed(() => {
  if (!medicamentoSelecionado.value || !aplicacaoForm.value.QUANTIDADE_APLICADA) {
    return { valido: true }
  }
  return medicamentoStore.validarEstoque(
    medicamentoSelecionado.value.value,
    aplicacaoForm.value.QUANTIDADE_APLICADA
  )
})

// Colunas das tabelas
const medicamentoColumns = [
  { name: 'NOME', label: 'Nome', field: 'NOME', sortable: true, align: 'left' },
  { name: 'PRINCIPIO_ATIVO', label: 'Princípio Ativo', field: 'PRINCIPIO_ATIVO', sortable: true, align: 'left' },
  { name: 'forma', label: 'Forma', field: 'FORMA_FARMACEUTICA', sortable: true, align: 'center' },
  { name: 'estoque', label: 'Estoque', field: 'ESTOQUE_ATUAL', sortable: true, align: 'left' },
  { name: 'status', label: 'Status', field: 'status_estoque', sortable: true, align: 'center' },
  { name: 'valor', label: 'Valor Estoque', field: 'valor_estoque', sortable: true, align: 'right' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

const movimentacaoColumns = [
  { name: 'DATA_REGISTRO', label: 'Data', field: 'DATA_REGISTRO', sortable: true, align: 'left' },
  { name: 'medicamento_nome', label: 'Medicamento', field: 'medicamento_nome', sortable: true, align: 'left' },
  { name: 'tipo', label: 'Tipo', field: 'TIPO_MOVIMENTACAO', sortable: true, align: 'center' },
  { name: 'quantidade', label: 'Quantidade', field: 'QUANTIDADE', sortable: true, align: 'right' },
  { name: 'animal_nome', label: 'Animal', field: 'animal_nome', sortable: true, align: 'left' },
  { name: 'MOTIVO', label: 'Motivo', field: 'MOTIVO', sortable: true, align: 'left' }
]

const previsaoColumns = [
  { name: 'medicamento_nome', label: 'Medicamento', field: 'medicamento_nome', align: 'left' },
  { name: 'estoque_atual', label: 'Estoque', field: 'estoque_atual', align: 'right' },
  { name: 'consumo_mensal_medio', label: 'Consumo Médio', field: 'consumo_mensal_medio', align: 'right' },
  { name: 'dias_restantes', label: 'Dias Restantes', field: 'dias_restantes', align: 'center' },
  { name: 'recomendacao', label: 'Recomendação', field: 'recomendacao', align: 'center' }
]

// Funções
async function loadOptions() {
  try {
    await animalStore.fetchAnimais({ limit: 100 })
    animalOptions.value = animalStore.animais.map(a => ({
      value: a.ID,
      label: a.NOME
    }))
    
    medicamentoSelectOptions.value = await medicamentoStore.loadMedicamentoOptions()
  } catch (error) {
    console.error('Erro ao carregar opções:', error)
  }
}

async function onFilterChange() {
  await medicamentoStore.fetchMedicamentos()
}

async function onFilterChangeMovimentacoes() {
  await medicamentoStore.fetchMovimentacoes()
}

async function onRequestMedicamentos(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  medicamentoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  await medicamentoStore.fetchMedicamentos(props)
}

async function onRequestMovimentacoes(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  medicamentoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  await medicamentoStore.fetchMovimentacoes(props)
}

function openDialog(record) {
  initializeForm(record)
  dialog.value = true
}

function initializeForm(record) {
  form.value = record ? { 
    ...record,
    REQUER_RECEITA_BOOL: record.REQUER_RECEITA === 'S'
  } : {
    ID: null,
    NOME: '',
    PRINCIPIO_ATIVO: '',
    CONCENTRACAO: '',
    FORMA_FARMACEUTICA: null,
    FABRICANTE: '',
    REGISTRO_MAPA: '',
    ESTOQUE_ATUAL: 0,
    ESTOQUE_MINIMO: 0,
    UNIDADE_MEDIDA: null,
    PRECO_UNITARIO: null,
    FORNECEDOR: '',
    REQUER_RECEITA_BOOL: false,
    PERIODO_CARENCIA: null,
    OBSERVACOES: '',
    ID_USUARIO_CADASTRO: authStore.user.ID
  }
}

async function saveRecord() {
  try {
    const formData = {
      ...form.value,
      REQUER_RECEITA: form.value.REQUER_RECEITA_BOOL ? 'S' : 'N'
    }
    delete formData.REQUER_RECEITA_BOOL

    // Converter objetos select para valores
    const preparedData = prepareFormData(formData, [])

    if (preparedData.ID) {
      await medicamentoStore.updateMedicamento(preparedData.ID, preparedData)
      $q.notify({ type: 'positive', message: 'Medicamento atualizado com sucesso' })
    } else {
      await medicamentoStore.createMedicamento(preparedData)
      $q.notify({ type: 'positive', message: 'Medicamento criado com sucesso' })
    }
    dialog.value = false
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

function openEstoqueDialog(medicamento) {
  estoqueForm.value = {
    ID_MEDICAMENTO: medicamento?.ID || null,
    medicamento_nome: medicamento?.NOME || '',
    medicamento_select: medicamento ? { value: medicamento.ID, label: medicamento.NOME } : null,
    unidade_medida: medicamento?.UNIDADE_MEDIDA || '',
    QUANTIDADE: null,
    LOTE: '',
    DATA_VALIDADE: '',
    NOTA_FISCAL: '',
    FORNECEDOR: '',
    PRECO_UNITARIO: null,
    OBSERVACOES: ''
  }
  estoqueDialog.value = true
}

async function salvarEstoque() {
  try {
    const entradaData = {
      ID_MEDICAMENTO: estoqueForm.value.ID_MEDICAMENTO || estoqueForm.value.medicamento_select?.value,
      QUANTIDADE: estoqueForm.value.QUANTIDADE,
      LOTE: estoqueForm.value.LOTE,
      DATA_VALIDADE: estoqueForm.value.DATA_VALIDADE,
      NOTA_FISCAL: estoqueForm.value.NOTA_FISCAL,
      FORNECEDOR: estoqueForm.value.FORNECEDOR,
      PRECO_UNITARIO: estoqueForm.value.PRECO_UNITARIO,
      OBSERVACOES: estoqueForm.value.OBSERVACOES
    }

    await medicamentoStore.entradaEstoque(entradaData)
    $q.notify({ type: 'positive', message: 'Entrada registrada com sucesso' })
    estoqueDialog.value = false
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

async function aplicarMedicamento() {
  try {
    const aplicacaoData = {
      ID_ANIMAL: aplicacaoForm.value.ID_ANIMAL?.value,
      ID_MEDICAMENTO: aplicacaoForm.value.ID_MEDICAMENTO?.value,
      QUANTIDADE_APLICADA: aplicacaoForm.value.QUANTIDADE_APLICADA,
      VETERINARIO_RESPONSAVEL: aplicacaoForm.value.VETERINARIO_RESPONSAVEL,
      OBSERVACOES: aplicacaoForm.value.OBSERVACOES
    }

    await medicamentoStore.aplicarMedicamento(aplicacaoData)
    $q.notify({ type: 'positive', message: 'Medicamento aplicado com sucesso' })
    resetAplicacaoForm()
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

function resetAplicacaoForm() {
  aplicacaoForm.value = {
    ID_ANIMAL: null,
    ID_MEDICAMENTO: null,
    QUANTIDADE_APLICADA: null,
    VETERINARIO_RESPONSAVEL: '',
    OBSERVACOES: ''
  }
}

function openAplicacaoDialog() {
  aplicacaoModalForm.value = {
    ID_ANIMAL: null,
    ID_MEDICAMENTO: null,
    QUANTIDADE_APLICADA: null,
    VETERINARIO_RESPONSAVEL: '',
    OBSERVACOES: ''
  }
  aplicacaoDialog.value = true
}

async function aplicarMedicamentoModal() {
  try {
    const aplicacaoData = {
      ID_ANIMAL: aplicacaoModalForm.value.ID_ANIMAL?.value,
      ID_MEDICAMENTO: aplicacaoModalForm.value.ID_MEDICAMENTO?.value,
      QUANTIDADE_APLICADA: aplicacaoModalForm.value.QUANTIDADE_APLICADA,
      VETERINARIO_RESPONSAVEL: aplicacaoModalForm.value.VETERINARIO_RESPONSAVEL,
      OBSERVACOES: aplicacaoModalForm.value.OBSERVACOES
    }

    await medicamentoStore.aplicarMedicamento(aplicacaoData)
    $q.notify({ type: 'positive', message: 'Medicamento aplicado com sucesso' })
    aplicacaoDialog.value = false
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

function viewRecord(record) {
  viewData.value = record
  viewDialog.value = true
}

function editFromView() {
  viewDialog.value = false
  openDialog(viewData.value, 'medicamento')
}

function confirmDelete(record) {
  recordToDelete.value = record
  deleteDialog.value = true
}

async function performDelete() {
  try {
    await medicamentoStore.deleteMedicamento(recordToDelete.value.ID)
    $q.notify({ type: 'positive', message: 'Medicamento excluído com sucesso' })
    deleteDialog.value = false
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

async function loadRelatorios() {
  try {
    await Promise.all([
      medicamentoStore.fetchEstoqueBaixo(),
      medicamentoStore.fetchPrevisaoConsumo()
    ])
    $q.notify({ type: 'positive', message: 'Relatórios atualizados' })
  } catch (error) {
    $q.notify({ type: 'negative', message: error })
  }
}

// Filtros
function filterAnimais(val, update) {
  update(() => {
    if (val === '') {
      animalOptions.value = animalStore.animais.map(a => ({ value: a.ID, label: a.NOME }))
    } else {
      const needle = val.toLowerCase()
      const allAnimais = animalStore.animais.map(a => ({ value: a.ID, label: a.NOME }))
      animalOptions.value = allAnimais.filter(v => v.label.toLowerCase().indexOf(needle) > -1)
    }
  })
}

function filterMedicamentos(val, update) {
  update(() => {
    if (val === '') {
      medicamentoOptions.value = medicamentoSelectOptions.value
    } else {
      const needle = val.toLowerCase()
      medicamentoOptions.value = medicamentoSelectOptions.value.filter(v => 
        v.label.toLowerCase().indexOf(needle) > -1
      )
    }
  })
}

function filterMedicamentosModal(val, update) {
  update(() => {
    if (val === '') {
      medicamentoOptionsModal.value = medicamentoSelectOptions.value
    } else {
      const needle = val.toLowerCase()
      medicamentoOptionsModal.value = medicamentoSelectOptions.value.filter(v => 
        v.label.toLowerCase().indexOf(needle) > -1
      )
    }
  })
}

function filterMedicamentosEstoque(val, update) {
  update(() => {
    if (val === '') {
      // Mostrar todos os medicamentos, não apenas com estoque
      const allMedicamentos = medicamentoStore.medicamentosAtivos.map(m => ({
        value: m.ID,
        label: m.NOME,
        unidade: m.UNIDADE_MEDIDA
      }))
      estoqueForm.value.medicamento_options = allMedicamentos
    } else {
      const needle = val.toLowerCase()
      const allMedicamentos = medicamentoStore.medicamentosAtivos.map(m => ({
        value: m.ID,
        label: m.NOME,
        unidade: m.UNIDADE_MEDIDA
      }))
      estoqueForm.value.medicamento_options = allMedicamentos.filter(v => 
        v.label.toLowerCase().indexOf(needle) > -1
      )
    }
  })
}

// Eventos de seleção
function onMedicamentoSelect(medicamento) {
  if (medicamento) {
    // Atualizar informações do medicamento selecionado
    aplicacaoForm.value.unidade_medida = medicamento.unidade
  }
}

function onMedicamentoEstoqueSelect(medicamento) {
  if (medicamento) {
    estoqueForm.value.ID_MEDICAMENTO = medicamento.value
    estoqueForm.value.medicamento_nome = medicamento.label
    estoqueForm.value.unidade_medida = medicamento.unidade
  }
}

// Funções auxiliares para cores e labels
function getFormaColor(forma) {
  const colors = {
    'INJETAVEL': 'primary',
    'ORAL': 'secondary',
    'TOPICO': 'accent'
  }
  return colors[forma] || 'grey'
}

function getStatusIcon(status) {
  const icons = {
    'OK': 'check_circle',
    'ESTOQUE_BAIXO': 'warning',
    'VENCENDO': 'schedule',
    'VENCIDO': 'error'
  }
  return icons[status] || 'help'
}

function getEstoqueColorClass(medicamento) {
  if (medicamento.ESTOQUE_ATUAL <= medicamento.ESTOQUE_MINIMO) {
    return 'text-negative'
  } else if (medicamento.ESTOQUE_ATUAL <= medicamento.ESTOQUE_MINIMO * 1.5) {
    return 'text-warning'
  }
  return 'text-positive'
}

function getEstoqueProgressColor(medicamento) {
  const ratio = medicamento.ESTOQUE_ATUAL / (medicamento.ESTOQUE_MINIMO || 1)
  if (ratio <= 1) return 'negative'
  if (ratio <= 1.5) return 'warning'
  return 'positive'
}

// Watchers para mudança de aba
async function onTabChange() {
  if (activeTab.value === 'medicamentos') {
    await medicamentoStore.fetchMedicamentos()
  } else if (activeTab.value === 'movimentacoes') {
    await medicamentoStore.fetchMovimentacoes()
  } else if (activeTab.value === 'estoque') {
    await Promise.all([
      medicamentoStore.fetchMedicamentos(),
      medicamentoStore.fetchMovimentacoes({ limit: 10 })
    ])
  } else if (activeTab.value === 'alertas') {
    await medicamentoStore.fetchEstoqueBaixo()
  } else if (activeTab.value === 'relatorios') {
    await loadRelatorios()
  }
}

// Inicialização
onMounted(async () => {
  await loadOptions()
  await onTabChange()
})

watch(activeTab, onTabChange)
</script>

<style scoped>
.q-banner {
  border-radius: 8px;
}

.text-h4 {
  font-weight: 300;
}

.q-chip {
  font-size: 0.75rem;
}
</style>