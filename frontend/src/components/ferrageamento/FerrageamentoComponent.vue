<template>
  <div>

    <!-- Abas -->
    <q-tabs v-model="activeTab" class="q-mb-md">
      <q-tab name="registros" label="Registros" />
      <q-tab name="aplicacao-rapida" label="Aplicação Rápida" />
      <q-tab name="alertas" label="Alertas" :badge="ferrageamentoStore.alertasVencimento.length || undefined" />
      <q-tab name="estatisticas" label="Estatísticas" />
      <q-tab name="relatorios" label="Relatórios" />
    </q-tabs>

    <q-tab-panels v-model="activeTab" animated>
      <!-- ABA REGISTROS -->
      <q-tab-panel name="registros">
        <div class="row q-gutter-md q-mb-md">
          <q-btn
            color="primary"
            label="Novo Registro"
            icon="add"
            @click="openDialog(null)"
          />         
        </div>

        <q-table
          :rows="ferrageamentoStore.ferrageamentos"
          :columns="registroColumns"
          row-key="ID"
          :loading="ferrageamentoStore.loading"
          :pagination="ferrageamentoStore.pagination"
          @request="onRequestRegistros"
          binary-state-sort
        >
          <template v-slot:body-cell-TIPO_REGISTRO="props">
            <q-td :props="props">
              <q-chip
                :color="ferrageamentoStore.getTipoColor(props.value)"
                text-color="white"
                :label="ferrageamentoStore.getTipoLabel(props.value)"
                dense
              />
            </q-td>
          </template>

          <template v-slot:body-cell-STATUS_CASCO="props">
            <q-td :props="props">
              <q-chip
                v-if="props.value"
                :color="ferrageamentoStore.getStatusCascoColor(props.value)"
                text-color="white"
                :label="props.value"
                dense
              />
              <span v-else class="text-grey-6">-</span>
            </q-td>
          </template>

          <template v-slot:body-cell-status_vencimento="props">
            <q-td :props="props">
              <q-chip
                :color="ferrageamentoStore.getStatusVencimentoColor(props.value)"
                text-color="white"
                :label="ferrageamentoStore.getStatusVencimentoLabel(props.value)"
                dense
              />
            </q-td>
          </template>

          <template v-slot:body-cell-DATA_OCORRENCIA="props">
            <q-td :props="props">
              {{ formatarData(props.value) }}
            </q-td>
          </template>

          <template v-slot:body-cell-PROXIMA_AVALIACAO="props">
            <q-td :props="props">
              <div v-if="props.value">
                {{ formatarData(props.value) }}
                <div class="text-caption" :class="getClasseDiasVencimento(props.row.dias_proxima_avaliacao)">
                  {{ getTextoDiasVencimento(props.row.dias_proxima_avaliacao) }}
                </div>
              </div>
              <span v-else class="text-grey-6">-</span>
            </q-td>
          </template>

          <template v-slot:body-cell-CUSTO="props">
            <q-td :props="props">
              <span v-if="props.value">R$ {{ props.value.toFixed(2) }}</span>
              <span v-else class="text-grey-6">-</span>
            </q-td>
          </template>

          <template v-slot:body-cell-acoes="props">
            <q-td :props="props">
              <q-btn flat round color="primary" icon="visibility" @click="viewRecord(props.row)" />
              <q-btn flat round color="orange" icon="edit" @click="openDialog(props.row)" />
              <q-btn flat round color="red" icon="delete" @click="confirmDelete(props.row)" />
            </q-td>
          </template>
        </q-table>
      </q-tab-panel>

      <!-- ABA APLICAÇÃO RÁPIDA -->
      <q-tab-panel name="aplicacao-rapida">
        <q-card>
          <q-card-section>
            <div class="text-h6">Aplicação Rápida</div>
            <div class="text-caption">Para registros simples de ferrageamento/casqueamento</div>
          </q-card-section>
          <q-card-section>
            <q-form @submit="aplicarRapido" class="q-gutter-md">
              <div class="row q-gutter-md">
                <div class="col-md-6 col-12">
                  <q-select
                    v-model="aplicacaoRapida.ID_ANIMAL"
                    :options="animalOptions"
                    option-value="value"
                    option-label="label"
                    emit-value
                    map-options
                    use-input
                    @filter="filterAnimais"
                    label="Animal *"
                    :rules="[val => !!val || 'Animal é obrigatório']"
                  />
                </div>
                <div class="col-md-6 col-12">
                  <q-select
                    v-model="aplicacaoRapida.TIPO_REGISTRO"
                    :options="ferrageamentoStore.tiposFerrageamento"
                    option-value="value"
                    option-label="label"
                    emit-value
                    map-options
                    label="Tipo *"
                    :rules="[val => !!val || 'Tipo é obrigatório']"
                  />
                </div>
              </div>

              <div class="row q-gutter-md">
                <div class="col-md-6 col-12">
                  <q-select
                    v-model="aplicacaoRapida.MEMBRO_TRATADO"
                    :options="ferrageamentoStore.membrosOpcoes"
                    option-value="value"
                    option-label="label"
                    emit-value
                    map-options
                    label="Membro(s) Tratado(s)"
                  />
                </div>
                <div class="col-md-6 col-12">
                  <q-select
                    v-model="aplicacaoRapida.STATUS_CASCO"
                    :options="ferrageamentoStore.statusCasco"
                    option-value="value"
                    option-label="label"
                    emit-value
                    map-options
                    label="Status do Casco"
                  />
                </div>
              </div>

              <div class="row q-gutter-md">
                <div class="col-md-8 col-12">
                  <q-input
                    v-model="aplicacaoRapida.FERRADOR_RESPONSAVEL"
                    label="Ferrador Responsável *"
                    :rules="[val => !!val || 'Ferrador é obrigatório']"
                  />
                </div>
                <div class="col-md-4 col-12">
                  <q-input
                    v-model.number="aplicacaoRapida.CUSTO"
                    type="number"
                    step="0.01"
                    label="Custo (R$)"
                    prefix="R$"
                  />
                </div>
              </div>

              <q-input
                v-model="aplicacaoRapida.OBSERVACOES"
                label="Observações"
                type="textarea"
                rows="3"
              />

              <div class="text-right">
                <q-btn type="submit" color="primary" :loading="loadingAplicacao">
                  Registrar Aplicação
                </q-btn>
              </div>
            </q-form>
          </q-card-section>
        </q-card>
      </q-tab-panel>

      <!-- ABA ALERTAS -->
      <q-tab-panel name="alertas">
        <q-card>
          <q-card-section>
            <div class="text-h6">Alertas de Vencimento</div>
            <div class="text-caption">Animais que precisam de ferrageamento/casqueamento</div>
          </q-card-section>
          <q-card-section>
            <div class="row q-gutter-md q-mb-md">
              <q-btn
                color="primary"
                label="Atualizar Alertas"
                icon="refresh"
                @click="carregarAlertas"
              />
              <q-input
                v-model.number="diasAntecedencia"
                type="number"
                label="Dias de antecedência"
                style="width: 150px"
                @update:model-value="carregarAlertas"
              />
            </div>

            <q-list bordered separator>
              <q-item v-for="alerta in ferrageamentoStore.alertasVencimento" :key="alerta.animal_id">
                <q-item-section avatar>
                  <q-avatar :color="ferrageamentoStore.getStatusVencimentoColor(alerta.status_vencimento)" text-color="white">
                    {{ alerta.dias_vencimento }}
                  </q-avatar>
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ alerta.animal_nome }}</q-item-label>
                  <q-item-label caption>
                    {{ ferrageamentoStore.getTipoLabel(alerta.tipo_registro) }} - 
                    {{ formatarData(alerta.data_vencimento) }}
                  </q-item-label>
                  <q-item-label caption v-if="alerta.ferrador_anterior">
                    Último ferrador: {{ alerta.ferrador_anterior }}
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <div>
                    <q-chip
                      :color="ferrageamentoStore.getStatusVencimentoColor(alerta.status_vencimento)"
                      text-color="white"
                      :label="ferrageamentoStore.getStatusVencimentoLabel(alerta.status_vencimento)"
                      dense
                    />
                    <div class="text-caption" v-if="alerta.custo_estimado">
                      Custo estimado: R$ {{ alerta.custo_estimado.toFixed(2) }}
                    </div>
                  </div>
                </q-item-section>
                <q-item-section side>
                  <q-btn
                    flat
                    round
                    color="primary"
                    icon="add"
                    @click="agendarFerrageamento(alerta)"
                  />
                </q-item-section>
              </q-item>
              <q-item v-if="ferrageamentoStore.alertasVencimento.length === 0">
                <q-item-section>
                  <q-item-label class="text-center text-grey-6">
                    Nenhum alerta no período selecionado
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </q-tab-panel>

      <!-- ABA ESTATÍSTICAS -->
      <q-tab-panel name="estatisticas">
        <div class="row q-gutter-md">
          <div class="col-md-6 col-12">
            <q-card>
              <q-card-section>
                <div class="text-h6">Estatísticas por Animal</div>
              </q-card-section>
              <q-card-section>
                <q-list bordered separator>
                  <q-item v-for="stat in ferrageamentoStore.estatisticasAnimais" :key="stat.animal_id">
                    <q-item-section>
                      <q-item-label>{{ stat.animal_nome }}</q-item-label>
                      <q-item-label caption>
                        {{ stat.total_ferrageamentos }} ferrageamentos, {{ stat.total_casqueamentos }} casqueamentos
                      </q-item-label>
                      <q-item-label caption v-if="stat.custo_total">
                        Custo total: R$ {{ stat.custo_total.toFixed(2) }}
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-chip
                        :color="ferrageamentoStore.getStatusVencimentoColor(stat.status_vencimento)"
                        text-color="white"
                        :label="ferrageamentoStore.getStatusVencimentoLabel(stat.status_vencimento)"
                        dense
                      />
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>

      <!-- ABA RELATÓRIOS -->
      <q-tab-panel name="relatorios">
        <q-card>
          <q-card-section>
            <div class="text-h6">Gerar Relatório</div>
          </q-card-section>
          <q-card-section>
            <q-form @submit="gerarRelatorio" class="q-gutter-md">
              <div class="row q-gutter-md">
                <div class="col-md-4 col-12">
                  <CalendarioComponent
                    v-model="filtrosRelatorio.data_inicio"
                    label="Data Início *"
                    :rules="[val => !!val || 'Data início é obrigatória']"
                  />
                </div>
                <div class="col-md-4 col-12">
                  <CalendarioComponent
                    v-model="filtrosRelatorio.data_fim"
                    label="Data Fim *"
                    :rules="[val => !!val || 'Data fim é obrigatória']"
                  />
                </div>
                <div class="col-md-4 col-12">
                  <q-select
                    v-model="filtrosRelatorio.tipo_registro"
                    :options="ferrageamentoStore.tiposFerrageamento"
                    option-value="value"
                    option-label="label"
                    emit-value
                    map-options
                    label="Tipo (opcional)"
                    clearable
                  />
                </div>
              </div>

              <div class="text-right">
                <q-btn type="submit" color="primary" :loading="loadingRelatorio">
                  Gerar Relatório
                </q-btn>
              </div>
            </q-form>
          </q-card-section>
        </q-card>

        <!-- Relatório Gerado -->
        <q-card v-if="ferrageamentoStore.relatorio" class="q-mt-md">
          <q-card-section>
            <div class="text-h6">Relatório de Ferrageamento</div>
            <div class="text-caption">
              Período: {{ formatarData(ferrageamentoStore.relatorio.periodo_inicio) }} a 
              {{ formatarData(ferrageamentoStore.relatorio.periodo_fim) }}
            </div>
          </q-card-section>
          <q-card-section>
            <div class="row q-gutter-md">
              <div class="col-md-3 col-6">
                <q-card flat bordered>
                  <q-card-section class="text-center">
                    <div class="text-h4">{{ ferrageamentoStore.relatorio.total_registros }}</div>
                    <div class="text-caption">Total Registros</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-md-3 col-6">
                <q-card flat bordered>
                  <q-card-section class="text-center">
                    <div class="text-h4">{{ ferrageamentoStore.relatorio.animais_atendidos }}</div>
                    <div class="text-caption">Animais Atendidos</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-md-3 col-6">
                <q-card flat bordered>
                  <q-card-section class="text-center">
                    <div class="text-h4">{{ ferrageamentoStore.relatorio.ferradores_utilizados }}</div>
                    <div class="text-caption">Ferradores</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-md-3 col-6">
                <q-card flat bordered>
                  <q-card-section class="text-center">
                    <div class="text-h4">
                      R$ {{ (ferrageamentoStore.relatorio.custo_total || 0).toFixed(2) }}
                    </div>
                    <div class="text-caption">Custo Total</div>
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <div class="q-mt-md" v-if="Object.keys(ferrageamentoStore.relatorio.tipos_mais_realizados).length">
              <div class="text-subtitle2">Tipos Mais Realizados</div>
              <q-list dense>
                <q-item v-for="(quantidade, tipo) in ferrageamentoStore.relatorio.tipos_mais_realizados" :key="tipo">
                  <q-item-section>
                    <q-item-label>{{ ferrageamentoStore.getTipoLabel(tipo) }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-chip color="primary" text-color="white" :label="quantidade" dense />
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </q-card-section>
        </q-card>
      </q-tab-panel>
    </q-tab-panels>

    <!-- Modal de Cadastro/Edição -->
    <q-dialog v-model="dialog" persistent>
      <q-card style="width: 800px; max-width: 90vw">
        <q-form @submit="saveRecord">
          <q-card-section>
            <div class="text-h6">{{ editandoRegistro ? 'Editar' : 'Novo' }} Registro de Ferrageamento</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <div class="row q-gutter-md">
              <div class="col-md-6 col-12">
                <q-select
                  v-model="form.ID_ANIMAL"
                  :options="animalOptions"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  use-input
                  @filter="filterAnimais"
                  label="Animal *"
                  :rules="[val => !!val || 'Animal é obrigatório']"
                />
              </div>
              <div class="col-md-6 col-12">
                <q-select
                  v-model="form.TIPO_REGISTRO"
                  :options="ferrageamentoStore.tiposFerrageamento"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  label="Tipo *"
                  :rules="[val => !!val || 'Tipo é obrigatório']"
                />
              </div>
            </div>

            <div class="row q-gutter-md">
              <div class="col-md-6 col-12">
                <CalendarioComponent
                  v-model="form.DATA_OCORRENCIA"
                  label="Data da Ocorrência *"
                  :rules="[val => !!val || 'Data é obrigatória']"
                />
              </div>
              <div class="col-md-6 col-12">
                <CalendarioComponent
                  v-model="form.PROXIMA_AVALIACAO"
                  label="Próxima Avaliação"
                />
              </div>
            </div>

            <q-input
              v-model="form.DESCRICAO"
              label="Descrição"
              type="textarea"
              rows="2"
            />

            <q-separator class="q-my-md" />
            <div class="text-subtitle2">Detalhes do Ferrageamento</div>

            <div class="row q-gutter-md">
              <div class="col-md-6 col-12">
                <q-select
                  v-model="form.TIPO_FERRADURA"
                  :options="ferrageamentoStore.tiposFerradura"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  label="Tipo de Ferradura"
                  clearable
                />
              </div>
              <div class="col-md-6 col-12">
                <q-select
                  v-model="form.MEMBRO_TRATADO"
                  :options="ferrageamentoStore.membrosOpcoes"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  label="Membro(s) Tratado(s)"
                />
              </div>
            </div>

            <div class="row q-gutter-md">
              <div class="col-md-6 col-12">
                <q-select
                  v-model="form.STATUS_CASCO"
                  :options="ferrageamentoStore.statusCasco"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  label="Status do Casco"
                />
              </div>
              <div class="col-md-6 col-12">
                <q-input
                  v-model="form.TECNICA_APLICADA"
                  label="Técnica Aplicada"
                />
              </div>
            </div>

            <q-input
              v-model="form.PROBLEMA_DETECTADO"
              label="Problemas Detectados"
              type="textarea"
              rows="2"
            />

            <div class="row q-gutter-md">
              <div class="col-md-8 col-12">
                <q-input
                  v-model="form.FERRADOR_RESPONSAVEL"
                  label="Ferrador Responsável"
                />
              </div>
              <div class="col-md-4 col-12">
                <q-input
                  v-model.number="form.CUSTO"
                  type="number"
                  step="0.01"
                  label="Custo (R$)"
                  prefix="R$"
                />
              </div>
            </div>

            <q-input
              v-model="form.OBSERVACOES"
              label="Observações"
              type="textarea"
              rows="3"
            />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancelar" color="grey" @click="dialog = false" />
            <q-btn type="submit" color="primary" :loading="loading">
              {{ editandoRegistro ? 'Atualizar' : 'Salvar' }}
            </q-btn>
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- Modal de Visualização -->
    <q-dialog v-model="viewDialog" persistent>
      <q-card style="width: 600px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6">Detalhes do Registro</div>
        </q-card-section>
        <q-card-section v-if="viewData">
          <div class="row q-gutter-md">
            <div class="col-6">
              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label overline>Animal</q-item-label>
                    <q-item-label>{{ viewData.animal_nome }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label overline>Tipo</q-item-label>
                    <q-item-label>{{ ferrageamentoStore.getTipoLabel(viewData.TIPO_REGISTRO) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label overline>Data Ocorrência</q-item-label>
                    <q-item-label>{{ formatarData(viewData.DATA_OCORRENCIA) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="viewData.PROXIMA_AVALIACAO">
                  <q-item-section>
                    <q-item-label overline>Próxima Avaliação</q-item-label>
                    <q-item-label>{{ formatarData(viewData.PROXIMA_AVALIACAO) }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
            <div class="col-6">
              <q-list>
                <q-item v-if="viewData.TIPO_FERRADURA">
                  <q-item-section>
                    <q-item-label overline>Tipo Ferradura</q-item-label>
                    <q-item-label>{{ viewData.TIPO_FERRADURA }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="viewData.MEMBRO_TRATADO">
                  <q-item-section>
                    <q-item-label overline>Membro(s)</q-item-label>
                    <q-item-label>{{ ferrageamentoStore.getMembroLabel(viewData.MEMBRO_TRATADO) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="viewData.STATUS_CASCO">
                  <q-item-section>
                    <q-item-label overline>Status Casco</q-item-label>
                    <q-item-label>{{ viewData.STATUS_CASCO }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="viewData.FERRADOR_RESPONSAVEL">
                  <q-item-section>
                    <q-item-label overline>Ferrador</q-item-label>
                    <q-item-label>{{ viewData.FERRADOR_RESPONSAVEL }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="viewData.CUSTO">
                  <q-item-section>
                    <q-item-label overline>Custo</q-item-label>
                    <q-item-label>R$ {{ viewData.CUSTO.toFixed(2) }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
          
          <div v-if="viewData.PROBLEMA_DETECTADO" class="q-mt-md">
            <q-item-label overline>Problemas Detectados</q-item-label>
            <div class="q-pa-sm bg-grey-1 rounded-borders">
              {{ viewData.PROBLEMA_DETECTADO }}
            </div>
          </div>
          
          <div v-if="viewData.OBSERVACOES" class="q-mt-md">
            <q-item-label overline>Observações</q-item-label>
            <div class="q-pa-sm bg-grey-1 rounded-borders">
              {{ viewData.OBSERVACOES }}
            </div>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Fechar" color="grey" @click="viewDialog = false" />
          <q-btn label="Editar" color="primary" @click="editFromView" />
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
          Tem certeza que deseja excluir este registro de ferrageamento?
          <div class="text-weight-bold q-mt-sm" v-if="recordToDelete">
            Animal: {{ recordToDelete.animal_nome }} - 
            {{ ferrageamentoStore.getTipoLabel(recordToDelete.TIPO_REGISTRO) }}
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" @click="deleteDialog = false" />
          <q-btn label="Excluir" color="negative" @click="performDelete" :loading="loading" />
        </q-card-actions>
      </q-card>
    </q-dialog>

   
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFerrageamentoStore } from 'stores/ferrageamento'
import { useAnimalStore } from 'stores/animal'
import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'
import { formatDate, convertToISO } from 'src/utils/dateUtils'
import { ErrorHandler } from 'src/utils/errorHandler'

// Composables
const ferrageamentoStore = useFerrageamentoStore()
const animalStore = useAnimalStore()

// Estado reativo
const activeTab = ref('registros')
const dialog = ref(false)
const viewDialog = ref(false)
const deleteDialog = ref(false)

const loading = ref(false)
const loadingAplicacao = ref(false)
const loadingRelatorio = ref(false)
const editandoRegistro = ref(false)
const viewData = ref(null)
const recordToDelete = ref(null)
const diasAntecedencia = ref(15)

// Opções
const animalOptions = ref([])

// Formulários
const form = ref({})
const aplicacaoRapida = ref({
  ID_ANIMAL: null,
  TIPO_REGISTRO: 'FERRAGEAMENTO',
  MEMBRO_TRATADO: 'TODOS',
  FERRADOR_RESPONSAVEL: '',
  STATUS_CASCO: 'BOM',
  CUSTO: null,
  OBSERVACOES: ''
})

const filtrosRelatorio = ref({
  data_inicio: '',
  data_fim: '',
  tipo_registro: null
})

// Colunas da tabela
const registroColumns = [
  { name: 'DATA_OCORRENCIA', label: 'Data', field: 'DATA_OCORRENCIA', sortable: true, align: 'left' },
  { name: 'animal_nome', label: 'Animal', field: 'animal_nome', sortable: true, align: 'left' },
  { name: 'TIPO_REGISTRO', label: 'Tipo', field: 'TIPO_REGISTRO', sortable: true, align: 'center' },
  { name: 'FERRADOR_RESPONSAVEL', label: 'Ferrador', field: 'FERRADOR_RESPONSAVEL', align: 'left' },
  { name: 'STATUS_CASCO', label: 'Status Casco', field: 'STATUS_CASCO', align: 'center' },
  { name: 'PROXIMA_AVALIACAO', label: 'Próxima Avaliação', field: 'PROXIMA_AVALIACAO', sortable: true, align: 'left' },
  { name: 'status_vencimento', label: 'Status', field: 'status_vencimento', align: 'center' },
  { name: 'CUSTO', label: 'Custo', field: 'CUSTO', sortable: true, align: 'right' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

// Métodos
async function onRequestRegistros(props) {
  const { page, rowsPerPage } = props.pagination
  
  ferrageamentoStore.setPagination({
    page,
    rowsPerPage
  })
  
  await ferrageamentoStore.fetchFerrageamentos()
}

function openDialog(record = null) {
  editandoRegistro.value = !!record
  
  if (record) {
    form.value = {
      ...record,
      DATA_OCORRENCIA: record.DATA_OCORRENCIA,
      PROXIMA_AVALIACAO: record.PROXIMA_AVALIACAO ? record.PROXIMA_AVALIACAO : ''
    }
  } else {
    form.value = {
      ID: null,
      ID_ANIMAL: null,
      TIPO_REGISTRO: 'FERRAGEAMENTO',
      DATA_OCORRENCIA: '',
      DESCRICAO: '',
      TIPO_FERRADURA: null,
      MEMBRO_TRATADO: 'TODOS',
      PROBLEMA_DETECTADO: '',
      TECNICA_APLICADA: '',
      FERRADOR_RESPONSAVEL: '',
      STATUS_CASCO: 'BOM',
      PROXIMA_AVALIACAO: '',
      CUSTO: null,
      OBSERVACOES: ''
    }
  }
  
  dialog.value = true
}

async function saveRecord() {
  loading.value = true
  try {
    const formData = {
      ...form.value,
      ID_ANIMAL: typeof form.value.ID_ANIMAL === 'object' 
        ? form.value.ID_ANIMAL.value 
        : form.value.ID_ANIMAL
    }

    console.log('Dados do formulário:', formData) 

    if (editandoRegistro.value) {
      await ferrageamentoStore.updateFerrageamento(formData.ID, formData)
      ErrorHandler.success('Registro atualizado com sucesso!')
    } else {
      await ferrageamentoStore.createFerrageamento(formData)
      ErrorHandler.success('Registro criado com sucesso!')
    }
    
    dialog.value = false
  } catch (error) {
    ErrorHandler.handle(error)
  } finally {
    loading.value = false
  }
}

function viewRecord(record) {
  viewData.value = record
  viewDialog.value = true
}

function editFromView() {
  viewDialog.value = false
  openDialog(viewData.value)
}

function confirmDelete(record) {
  recordToDelete.value = record
  deleteDialog.value = true
}

async function performDelete() {
  loading.value = true
  try {
    await ferrageamentoStore.deleteFerrageamento(recordToDelete.value.ID)
    ErrorHandler.success('Registro excluído com sucesso')
    deleteDialog.value = false
  } catch (error) {
    ErrorHandler.handle(error)
  } finally {
    loading.value = false
  }
}

async function aplicarRapido() {
  loadingAplicacao.value = true
  try {
    await ferrageamentoStore.aplicacaoRapida(aplicacaoRapida.value)
    ErrorHandler.success('Aplicação registrada com sucesso!')
    
    // Limpar formulário
    aplicacaoRapida.value = {
      ID_ANIMAL: null,
      TIPO_REGISTRO: 'FERRAGEAMENTO',
      MEMBRO_TRATADO: 'TODOS',
      FERRADOR_RESPONSAVEL: '',
      STATUS_CASCO: 'BOM',
      CUSTO: null,
      OBSERVACOES: ''
    }
  } catch (error) {
    ErrorHandler.handle(error)
  } finally {
    loadingAplicacao.value = false
  }
}

async function carregarAlertas() {
  await ferrageamentoStore.fetchAlertasVencimento(diasAntecedencia.value)
}

function agendarFerrageamento(alerta) {
  // Preencher formulário com dados do alerta
  form.value = {
    ID: null,
    ID_ANIMAL: alerta.animal_id,
    TIPO_REGISTRO: alerta.tipo_registro,
    DATA_OCORRENCIA: '',
    DESCRICAO: '',
    TIPO_FERRADURA: null,
    MEMBRO_TRATADO: 'TODOS',
    PROBLEMA_DETECTADO: '',
    TECNICA_APLICADA: '',
    FERRADOR_RESPONSAVEL: alerta.ferrador_anterior || '',
    STATUS_CASCO: 'BOM',
    PROXIMA_AVALIACAO: '',
    CUSTO: alerta.custo_estimado || null,
    OBSERVACOES: `Agendado através de alerta de vencimento`
  }
  
  editandoRegistro.value = false
  dialog.value = true
}

async function gerarRelatorio() {
  loadingRelatorio.value = true
  try {
    const filtrosFormatados = {
      ...filtrosRelatorio.value,
      data_inicio: convertToISO(filtrosRelatorio.value.data_inicio).split('T')[0],
      data_fim: convertToISO(filtrosRelatorio.value.data_fim).split('T')[0]
    }
    
    await ferrageamentoStore.gerarRelatorio(filtrosFormatados)
    ErrorHandler.success('Relatório gerado com sucesso')
  } catch (error) {
    ErrorHandler.handle(error)
  } finally {
    loadingRelatorio.value = false
  }
}

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

// Helpers para formatação
function formatarData(data) {
  return formatDate(data)
}

function getClasseDiasVencimento(dias) {
  if (dias < 0) return 'text-negative'
  if (dias <= 7) return 'text-warning'
  if (dias <= 15) return 'text-orange'
  return 'text-positive'
}

function getTextoDiasVencimento(dias) {
  if (dias < 0) return `${Math.abs(dias)} dias em atraso`
  if (dias === 0) return 'Vence hoje'
  if (dias === 1) return 'Vence amanhã'
  return `${dias} dias restantes`
}

// Lifecycle
onMounted(async () => {
  await animalStore.fetchAnimais()
  animalOptions.value = animalStore.animais.map(a => ({ value: a.ID, label: a.NOME }))
  
  await ferrageamentoStore.fetchFerrageamentos()
  await carregarAlertas()
  await ferrageamentoStore.fetchEstatisticasAnimais(6)
})
</script>