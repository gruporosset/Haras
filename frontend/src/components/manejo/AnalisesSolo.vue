<template>
  <div class="analises-solo-container">
    <!-- HEADER COM FILTROS -->
    <q-card flat class="q-mb-md">
      <q-card-section>
        <div class="row q-gutter-md items-end">
          <div class="col-md-3 col-12">
            <q-select
              v-model="filtros.terreno_id"
              :options="terrenoOptions"
              label="Terreno"
              dense
              clearable
              use-input
              @filter="filterTerrenos"
              @update:model-value="onFilterChange"
            />
          </div>
          <div class="col-md-2 col-12">
            <calendario-component
              v-model="filtros.data_inicio"
              label="Data Início"
              @update:model-value="onFilterChange"
            />
          </div>
          
          <div class="col-md-2 col-12">
            <calendario-component
              v-model="filtros.data_fim"
              label="Data Fim"
              @update:model-value="onFilterChange"
            />
          </div>
          
          <div class="col-md-3 col-12">
            <q-input
              v-model="filtros.laboratorio"
              label="Laboratório"
              dense
              clearable
              @update:model-value="onFilterChange"
              debounce="300"
            />
          </div>
          
        </div>
        <div class="row q-gutter-md items-end q-mt-sm">
          <div class="col-auto">
            <q-btn
              color="primary"
              icon="add"
              label="Nova Análise"
              @click="openDialog()"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- CARDS DE RESUMO -->
    <div class="row q-gutter-md q-mb-md justify-center">
      <div class="col-md-3 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6 text-primary">
              <q-icon name="biotech" class="q-mr-sm" />
              {{ estatisticas.totalAnalises }}
            </div>
            <div class="text-subtitle2">Total de Análises</div>
            <div class="text-caption text-grey-6">
              {{ estatisticas.terrenosAnalisados }} terrenos
            </div>
          </q-card-section>
        </q-card>
      </div>
      
      <div class="col-md-3 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6" :class="getClassePHMedio()">
              <q-icon name="science" class="q-mr-sm" />
              {{ estatisticas.phMedio.toFixed(1) }}
            </div>
            <div class="text-subtitle2">pH Médio</div>
            <div class="text-caption text-grey-6">
              {{ getStatusPH(estatisticas.phMedio) }}
            </div>
          </q-card-section>
        </q-card>
      </div>
      
      <div class="col-md-3 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6" :class="getClasseSaturacao()">
              <q-icon name="opacity" class="q-mr-sm" />
              {{ estatisticas.saturacaoMedia.toFixed(1) }}%
            </div>
            <div class="text-subtitle2">Saturação Média</div>
            <div class="text-caption text-grey-6">
              {{ getStatusSaturacao(estatisticas.saturacaoMedia) }}
            </div>
          </q-card-section>
        </q-card>
      </div>
      
      <div class="col-md-2 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6 text-orange">
              <q-icon name="schedule" class="q-mr-sm" />
              {{ estatisticas.analisesPendentes }}
            </div>
            <div class="text-subtitle2">Resultados Pendentes</div>
            <div class="text-caption text-grey-6">
              Última: {{ estatisticas.ultimaAnalise || 'Nunca' }}
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- ALERTAS DE SOLO -->
    <q-card 
      v-if="alertasSolo.length > 0" 
      flat 
      class="bg-orange-1 q-mb-md"
    >
      <q-card-section>
        <div class="text-h6 text-orange-8 q-mb-sm">
          <q-icon name="warning" class="q-mr-sm" />
          Alertas de Solo ({{ alertasSolo.length }})
        </div>
        <div class="row q-gutter-sm">
          <q-chip
            v-for="alerta in alertasSolo.slice(0, 5)"
            :key="alerta.terreno_id"
            :color="getCorAlerta(alerta.status)"
            text-color="white"
            size="sm"
            @click="viewAlerta(alerta)"
            clickable
          >
            {{ alerta.terreno_nome }} - {{ alerta.problema }}
          </q-chip>
          <q-btn
            v-if="alertasSolo.length > 5"
            flat
            color="orange"
            size="sm"
            :label="`+${alertasSolo.length - 5} mais`"
            @click="showAllAlertas"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- TABELA DE ANÁLISES -->
    <q-table
      :rows="manejoStore.analisesSolo"
      :columns="columns"
      row-key="ID"
      :loading="manejoStore.loading"
      :pagination="manejoStore.pagination"
      @request="onRequest"
      binary-state-sort
      flat
      class="analises-table"
    >
      <template v-slot:body-cell-status_resultado="props">
        <q-td :props="props">
          <q-chip
            :color="getCorStatus(props.row)"
            text-color="white"
            size="sm"
            :icon="getIconeStatus(props.row)"
          >
            {{ getStatusResultado(props.row) }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-ph_agua="props">
        <q-td :props="props">
          <div v-if="props.value" class="text-weight-medium" :class="getClassePH(props.value)">
            {{ props.value?.toFixed(1) }}
          </div>
          <div v-else class="text-grey-6">-</div>
          <div v-if="props.value" class="text-caption text-grey-6">
            {{ getStatusPH(props.value) }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-saturacao_bases="props">
        <q-td :props="props">
          <div v-if="props.row.SATURACAO_BASES" class="text-weight-medium" :class="getClasseSaturacaoValor(props.row.SATURACAO_BASES)">
            {{ props.row.SATURACAO_BASES?.toFixed(1) }}%
          </div>
          <div v-else class="text-grey-6">-</div>
          <div v-if="props.row.SATURACAO_BASES" class="text-caption text-grey-6">
            {{ getStatusSaturacao(props.row.SATURACAO_BASES) }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-materia_organica="props">
        <q-td :props="props">
          <div v-if="props.row.MATERIA_ORGANICA" class="text-weight-medium" :class="getClasseMO(props.row.MATERIA_ORGANICA)">
            {{ props.row.MATERIA_ORGANICA?.toFixed(1) }}%
          </div>
          <div v-else class="text-grey-6">-</div>
          <div v-if="props.row.MATERIA_ORGANICA" class="text-caption text-grey-6">
            {{ getStatusMO(props.row.MATERIA_ORGANICA) }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-data_coleta="props">
        <q-td :props="props">
          {{ formatarData(props.value) }}
        </q-td>
      </template>

      <template v-slot:body-cell-arquivo_laudo="props">
        <q-td :props="props">
          <div v-if="props.row.ARQUIVO_LAUDO">
            <q-btn
              flat
              round
              color="primary"
              icon="picture_as_pdf"
              size="sm"
              @click="downloadLaudo(props.row)"
            >
              <q-tooltip>Download Laudo</q-tooltip>
            </q-btn>
          </div>
          <div v-else>
            <q-btn
              flat
              round
              color="grey"
              icon="upload_file"
              size="sm"
              @click="uploadLaudo(props.row)"
            >
              <q-tooltip>Upload Laudo</q-tooltip>
            </q-btn>
          </div>
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
              @click="viewAnalise(props.row)"
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
    <q-dialog v-model="dialog" persistent>
      <q-card style="min-width: 800px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6">
            {{ form.ID ? 'Editar Análise de Solo' : 'Nova Análise de Solo' }}
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none" style="max-height: 70vh; overflow-y: auto;">
          <q-form @submit="submitForm" class="q-gutter-md">
            <!-- Informações Básicas -->
            <div class="text-h6 text-primary q-mb-md">Informações Básicas</div>
            
            <div class="row q-gutter-md">
              <q-select
                v-model="form.ID_TERRENO"
                :options="terrenoOptionsDialog"
                label="Terreno *"
                :rules="[val => !!val || 'Terreno é obrigatório']"
                use-input
                @filter="filterTerrenosDialog"
                class="col-4"
              />

              <calendario-component
                v-model="form.DATA_COLETA"
                label="Data da Coleta *"
                :rules="[val => !!val || 'Data é obrigatória']"
                class="col-3"
              />

              <calendario-component
                v-model="form.DATA_RESULTADO"
                label="Data do Resultado"
                class="col-3"
              />

              <q-input
                v-model="form.LABORATORIO"
                label="Laboratório"
                class="col-5"
              />
            </div>

            <!-- Parâmetros Químicos Principais -->
            <div class="text-h6 text-primary q-mb-md q-mt-lg">Parâmetros Químicos Principais</div>
            
            <div class="row q-gutter-md">
              <q-input
                v-model.number="form.PH_AGUA"
                label="pH (H₂O)"
                type="number"
                step="0.1"
                min="0"
                max="14"
                :hint="getHintPH(form.PH_AGUA)"
                class="col-2"
              />
              <q-input
                v-model.number="form.PH_CACL2"
                label="pH (CaCl₂)"
                type="number"
                step="0.1"
                min="0"
                max="14"
                class="col-2"
              />
              <q-input
                v-model.number="form.MATERIA_ORGANICA"
                label="Matéria Orgânica (%)"
                type="number"
                step="0.1"
                min="0"
                max="100"
                :hint="getHintMO(form.MATERIA_ORGANICA)"
                class="col-2"
              />
              <q-input
                v-model.number="form.FOSFORO"
                label="Fósforo (mg/dm³)"
                type="number"
                step="0.1"
                min="0"
                class="col-2"
              />
              <q-input
                v-model.number="form.POTASSIO"
                label="Potássio (cmolc/dm³)"
                type="number"
                step="0.01"
                min="0"
                class="col-3"
              />
            </div>

            <div class="row q-gutter-md">
              <q-input
                v-model.number="form.CALCIO"
                label="Cálcio (cmolc/dm³)"
                type="number"
                step="0.01"
                min="0"
                class="col-2"
              />
              <q-input
                v-model.number="form.MAGNESIO"
                label="Magnésio (cmolc/dm³)"
                type="number"
                step="0.01"
                min="0"
                class="col-2"
              />
              <q-input
                v-model.number="form.ALUMINIO"
                label="Alumínio (cmolc/dm³)"
                type="number"
                step="0.01"
                min="0"
                class="col-2"
              />
              <q-input
                v-model.number="form.H_AL"
                label="H+Al (cmolc/dm³)"
                type="number"
                step="0.01"
                min="0"
                class="col-2"
              />
              <q-input
                v-model.number="form.CTC"
                label="CTC (cmolc/dm³)"
                type="number"
                step="0.01"
                min="0"
                class="col-3"
              />
            </div>

            <div class="row q-gutter-md">
              <q-input
                v-model.number="form.SATURACAO_BASES"
                label="Saturação de Bases (%)"
                type="number"
                step="0.1"
                min="0"
                max="100"
                :hint="getHintSaturacao(form.SATURACAO_BASES)"
                class="col-3"
              />
              <q-input
                v-model.number="form.SATURACAO_ALUMINIO"
                label="Saturação de Alumínio (%)"
                type="number"
                step="0.1"
                min="0"
                max="100"
                class="col-3"
              />
            </div>

            <!-- Micronutrientes -->
            <div class="text-h6 text-primary q-mb-md q-mt-lg">Micronutrientes (mg/dm³)</div>
            
            <div class="row q-gutter-md">
              <q-input
                v-model.number="form.ENXOFRE"
                label="Enxofre"
                type="number"
                step="0.1"
                min="0"
                class="col-2"
              />
              <q-input
                v-model.number="form.BORO"
                label="Boro"
                type="number"
                step="0.01"
                min="0"
                class="col-2"
              />
              <q-input
                v-model.number="form.COBRE"
                label="Cobre"
                type="number"
                step="0.01"
                min="0"
                class="col-2"
              />
              <q-input
                v-model.number="form.FERRO"
                label="Ferro"
                type="number"
                step="0.1"
                min="0"
                class="col-2"
              />
              <q-input
                v-model.number="form.MANGANES"
                label="Manganês"
                type="number"
                step="0.1"
                min="0"
                class="col-2"
              />
              <q-input
                v-model.number="form.ZINCO"
                label="Zinco"
                type="number"
                step="0.01"
                min="0"
                class="col-2"
              />
            </div>

            <!-- Observações e Recomendações -->
            <div class="text-h6 text-primary q-mb-md q-mt-lg">Observações e Recomendações</div>
            
            <q-input
              v-model="form.OBSERVACOES"
              label="Observações"
              type="textarea"
              rows="3"
            />

            <q-input
              v-model="form.RECOMENDACOES"
              label="Recomendações do Laboratório"
              type="textarea"
              rows="4"
              hint="Recomendações de calagem, adubação, etc."
            />

            <!-- Card de Análise -->
            <q-card flat bordered class="bg-blue-1 q-mt-md" v-if="temParametrosPreenchidos">
              <q-card-section class="q-pa-sm">
                <div class="text-weight-medium text-blue-8">
                  <q-icon name="analytics" class="q-mr-sm" />
                  Análise Rápida
                </div>
                <div class="row q-mt-xs text-body2">
                  <div class="col-6">
                    <div v-if="form.PH_AGUA"><strong>pH:</strong> {{ getStatusPH(form.PH_AGUA) }}</div>
                    <div v-if="form.MATERIA_ORGANICA"><strong>M.O.:</strong> {{ getStatusMO(form.MATERIA_ORGANICA) }}</div>
                  </div>
                  <div class="col-6">
                    <div v-if="form.SATURACAO_BASES"><strong>Sat. Bases:</strong> {{ getStatusSaturacao(form.SATURACAO_BASES) }}</div>
                    <div v-if="form.CTC"><strong>CTC:</strong> {{ getStatusCTC(form.CTC) }}</div>
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
            :loading="manejoStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG VISUALIZAÇÃO -->
    <q-dialog v-model="viewDialog">
      <q-card style="min-width: 700px">
        <q-card-section>
          <div class="text-h6">Análise de Solo - {{ viewData?.terreno_nome }}</div>
          <div class="text-subtitle2 text-grey-6">
            {{ formatarData(viewData?.DATA_COLETA) }}
            {{ viewData?.LABORATORIO ? ` - ${viewData.LABORATORIO}` : '' }}
          </div>
        </q-card-section>

        <q-card-section>
          <div class="row q-gutter-md">
            <!-- Parâmetros Principais -->
            <div class="col-12">
              <div class="text-h6 text-primary q-mb-sm">Parâmetros Principais</div>
              <div class="row q-gutter-md">
                <div class="col-md-2 col-6">
                  <q-card flat bordered>
                    <q-card-section class="text-center q-pa-sm">
                      <div class="text-h5" :class="getClassePH(viewData?.PH_AGUA)">
                        {{ viewData?.PH_AGUA?.toFixed(1) || '-' }}
                      </div>
                      <div class="text-caption">pH (H₂O)</div>
                      <div class="text-caption text-grey-6">
                        {{ viewData?.PH_AGUA ? getStatusPH(viewData.PH_AGUA) : '' }}
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
                
                <div class="col-md-2 col-6">
                  <q-card flat bordered>
                    <q-card-section class="text-center q-pa-sm">
                      <div class="text-h5" :class="getClasseMO(viewData?.MATERIA_ORGANICA)">
                        {{ viewData?.MATERIA_ORGANICA?.toFixed(1) || '-' }}%
                      </div>
                      <div class="text-caption">M.O.</div>
                      <div class="text-caption text-grey-6">
                        {{ viewData?.MATERIA_ORGANICA ? getStatusMO(viewData.MATERIA_ORGANICA) : '' }}
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
                
                <div class="col-md-2 col-6">
                  <q-card flat bordered>
                    <q-card-section class="text-center q-pa-sm">
                      <div class="text-h5" :class="getClasseSaturacaoValor(viewData?.SATURACAO_BASES)">
                        {{ viewData?.SATURACAO_BASES?.toFixed(1) || '-' }}%
                      </div>
                      <div class="text-caption">Sat. Bases</div>
                      <div class="text-caption text-grey-6">
                        {{ viewData?.SATURACAO_BASES ? getStatusSaturacao(viewData.SATURACAO_BASES) : '' }}
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
                
                <div class="col-md-2 col-6">
                  <q-card flat bordered>
                    <q-card-section class="text-center q-pa-sm">
                      <div class="text-h5">
                        {{ viewData?.CTC?.toFixed(1) || '-' }}
                      </div>
                      <div class="text-caption">CTC</div>
                      <div class="text-caption text-grey-6">cmolc/dm³</div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </div>

            <!-- Macronutrientes -->
            <div class="col-md-6 col-12" v-if="temMacronutrientes(viewData)">
              <div class="text-h6 text-primary q-mb-sm">Macronutrientes</div>
              <q-list dense>
                <q-item v-if="viewData?.FOSFORO">
                  <q-item-section>
                    <q-item-label>Fósforo</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>{{ viewData.FOSFORO.toFixed(1) }} mg/dm³</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="viewData?.POTASSIO">
                  <q-item-section>
                    <q-item-label>Potássio</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>{{ viewData.POTASSIO.toFixed(2) }} cmolc/dm³</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="viewData?.CALCIO">
                  <q-item-section>
                    <q-item-label>Cálcio</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>{{ viewData.CALCIO.toFixed(2) }} cmolc/dm³</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="viewData?.MAGNESIO">
                  <q-item-section>
                    <q-item-label>Magnésio</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>{{ viewData.MAGNESIO.toFixed(2) }} cmolc/dm³</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Micronutrientes -->
            <div class="col-md-6 col-12" v-if="temMicronutrientes(viewData)">
              <div class="text-h6 text-primary q-mb-sm">Micronutrientes (mg/dm³)</div>
              <q-list dense>
                <q-item v-if="viewData?.ENXOFRE">
                  <q-item-section>
                    <q-item-label>Enxofre</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>{{ viewData.ENXOFRE.toFixed(1) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="viewData?.BORO">
                  <q-item-section>
                    <q-item-label>Boro</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>{{ viewData.BORO.toFixed(2) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="viewData?.COBRE">
                  <q-item-section>
                    <q-item-label>Cobre</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>{{ viewData.COBRE.toFixed(2) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="viewData?.FERRO">
                  <q-item-section>
                    <q-item-label>Ferro</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>{{ viewData.FERRO.toFixed(1) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="viewData?.MANGANES">
                  <q-item-section>
                    <q-item-label>Manganês</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>{{ viewData.MANGANES.toFixed(1) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="viewData?.ZINCO">
                  <q-item-section>
                    <q-item-label>Zinco</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>{{ viewData.ZINCO.toFixed(2) }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Recomendações -->
            <div class="col-12" v-if="viewData?.RECOMENDACOES">
              <div class="text-h6 text-primary q-mb-sm">Recomendações</div>
              <q-card flat bordered class="bg-green-1">
                <q-card-section>
                  <div class="text-body2" style="white-space: pre-line;">
                    {{ viewData.RECOMENDACOES }}
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Observações -->
            <div class="col-12" v-if="viewData?.OBSERVACOES">
              <div class="text-h6 text-primary q-mb-sm">Observações</div>
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-body2" style="white-space: pre-line;">
                    {{ viewData.OBSERVACOES }}
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Fechar" color="grey" @click="viewDialog = false" />
          <q-btn
            v-if="viewData?.ARQUIVO_LAUDO"
            color="primary"
            icon="download"
            label="Download Laudo"
            @click="downloadLaudo(viewData)"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG UPLOAD LAUDO -->
    <q-dialog v-model="uploadDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Upload de Laudo</div>
          <div class="text-subtitle2 text-grey-6">
            {{ analiseUpload?.terreno_nome }}
          </div>
        </q-card-section>

        <q-card-section>
          <q-file
            v-model="arquivoSelecionado"
            label="Selecionar arquivo"
            accept=".pdf,.jpg,.jpeg,.png"
            max-file-size="5242880"
            @rejected="onFileRejected"
            filled
          >
            <template v-slot:prepend>
              <q-icon name="attach_file" />
            </template>
          </q-file>
          <div class="text-caption text-grey-6 q-mt-sm">
            Formatos aceitos: PDF, JPG, PNG (máximo 5MB)
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" @click="uploadDialog = false" />
          <q-btn
            label="Upload"
            color="primary"
            :disable="!arquivoSelecionado"
            @click="submitUpload"
            :loading="uploadLoading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- DIALOG CONFIRMAÇÃO DELETE -->
    <q-dialog v-model="deleteDialog" persistent>
      <q-card>
        <q-card-section>
          <div class="text-h6">Confirmar Exclusão</div>
        </q-card-section>
        <q-card-section>
          Tem certeza que deseja excluir a análise de solo do terreno 
          <strong>{{ recordToDelete?.terreno_nome }}</strong>?
          <div class="text-caption text-warning q-mt-sm">
            <q-icon name="warning" /> Esta ação não pode ser desfeita.
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" @click="deleteDialog = false" />
          <q-btn
            label="Excluir"
            color="negative"
            @click="deleteAnalise"
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
import { useTerrenoStore } from 'stores/terreno'
import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

// Composables
const $q = useQuasar()
const manejoStore = useManejoStore()
const terrenoStore = useTerrenoStore()

// Estado reativo
const dialog = ref(false)
const viewDialog = ref(false)
const deleteDialog = ref(false)
const uploadDialog = ref(false)
const viewData = ref(null)
const recordToDelete = ref(null)
const analiseUpload = ref(null)
const arquivoSelecionado = ref(null)
const uploadLoading = ref(false)

// Filtros
const filtros = ref({
  terreno_id: null,
  data_inicio: '',
  data_fim: '',
  laboratorio: ''
})

// Formulário
const form = ref({})

// Opções
const terrenoOptions = ref([])
const terrenoOptionsDialog = ref([])

// Alertas
const alertasSolo = ref([])

// Computed
const estatisticas = computed(() => {
  const analises = manejoStore.analisesSolo
  const terrenosUnicos = new Set(analises.map(a => a.ID_TERRENO))
  const hoje = new Date()
  hoje.setHours(23, 59, 59, 999) // Fim do dia atual

  const pHs = analises.filter(a => a.PH_AGUA).map(a => a.PH_AGUA)
  const saturacoes = analises.filter(a => a.SATURACAO_BASES).map(a => a.SATURACAO_BASES)
  
  const phMedio = pHs.length > 0 ? pHs.reduce((sum, ph) => sum + ph, 0) / pHs.length : 0
  const saturacaoMedia = saturacoes.length > 0 ? saturacoes.reduce((sum, sat) => sum + sat, 0) / saturacoes.length : 0
  
  const pendentes = analises.filter(a => {
    if (!a.DATA_RESULTADO) return true // Sem data = pendente
    const dataResultado = new Date(a.DATA_RESULTADO)
    return dataResultado > hoje // Data futura = pendente
  }).length
  
  const ultimaAnalise = analises.length > 0 ? 
    new Date(Math.max(...analises.map(a => new Date(a.DATA_COLETA)))).toLocaleDateString('pt-BR') : null

  return {
    totalAnalises: analises.length,
    terrenosAnalisados: terrenosUnicos.size,
    phMedio,
    saturacaoMedia,
    analisesPendentes: pendentes,
    ultimaAnalise
  }
})

const temParametrosPreenchidos = computed(() => {
  return form.value.PH_AGUA || form.value.MATERIA_ORGANICA || form.value.SATURACAO_BASES || form.value.CTC
})

// Colunas da tabela
const columns = [
  { name: 'terreno_nome', label: 'Terreno', field: 'terreno_nome', sortable: true, align: 'left' },
  { name: 'data_coleta', label: 'Data Coleta', field: 'DATA_COLETA', sortable: true, align: 'left' },
  { name: 'status_resultado', label: 'Status', field: 'status_resultado', sortable: false, align: 'center' },
  { name: 'ph_agua', label: 'pH', field: 'PH_AGUA', sortable: true, align: 'center' },
  { name: 'materia_organica', label: 'M.O. (%)', field: 'materia_organica', sortable: true, align: 'center' },
  { name: 'saturacao_bases', label: 'Sat. Bases (%)', field: 'saturacao_bases', sortable: true, align: 'center' },
  { name: 'LABORATORIO', label: 'Laboratório', field: 'LABORATORIO', sortable: true, align: 'left' },
  { name: 'arquivo_laudo', label: 'Laudo', field: 'arquivo_laudo', sortable: false, align: 'center' },
  { name: 'acoes', label: 'Ações', field: 'acoes', align: 'center' }
]

// Métodos principais
async function onRequest(props) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination
  manejoStore.setPagination({ page, rowsPerPage, sortBy, descending })
  await manejoStore.fetchAnalisesSolo({ ...props, filtros: filtros.value })
}

async function onFilterChange() {
  await manejoStore.fetchAnalisesSolo({ filtros: filtros.value })
}

function openDialog(record) {
  initializeForm(record)
  dialog.value = true
}

function initializeForm(record) {
  if (record) {
    form.value = { ...record }
    // Converter datas para formato de input
    if (form.value.DATA_COLETA) {
      form.value.DATA_COLETA = new Date(form.value.DATA_COLETA).toISOString().split('T')[0]
    }
    if (form.value.DATA_RESULTADO) {
      form.value.DATA_RESULTADO = new Date(form.value.DATA_RESULTADO).toISOString().split('T')[0]
    }
  } else {
    form.value = {
      ID_TERRENO: null,
      DATA_COLETA: new Date().toISOString().split('T')[0],
      DATA_RESULTADO: '',
      LABORATORIO: '',
      PH_AGUA: null,
      PH_CACL2: null,
      MATERIA_ORGANICA: null,
      FOSFORO: null,
      POTASSIO: null,
      CALCIO: null,
      MAGNESIO: null,
      ALUMINIO: null,
      H_AL: null,
      CTC: null,
      SATURACAO_BASES: null,
      SATURACAO_ALUMINIO: null,
      ENXOFRE: null,
      BORO: null,
      COBRE: null,
      FERRO: null,
      MANGANES: null,
      ZINCO: null,
      OBSERVACOES: '',
      RECOMENDACOES: ''
    }
  }
}

async function submitForm() {
  try {
    // Preparar dados
    const data = { ...form.value }
    
    // Converter select para ID
    if (data.ID_TERRENO?.value) data.ID_TERRENO = data.ID_TERRENO.value

    if (form.value.ID) {
      await manejoStore.updateAnaliseSolo(form.value.ID, data)
      $q.notify({ type: 'positive', message: 'Análise atualizada com sucesso!' })
    } else {
      await manejoStore.createAnaliseSolo(data)
      $q.notify({ type: 'positive', message: 'Análise registrada com sucesso!' })
    }
    
    dialog.value = false
    await manejoStore.fetchAnalisesSolo({ filtros: filtros.value })
    await generateAlertas()
    
  } catch (error) {
    $q.notify({ type: 'negative', message: error.message || 'Erro ao salvar análise' })
  }
}

function viewAnalise(analise) {
  viewData.value = analise
  viewDialog.value = true
}

function confirmDelete(record) {
  recordToDelete.value = record
  deleteDialog.value = true
}

async function deleteAnalise() {
  try {
    await manejoStore.deleteAnaliseSolo(recordToDelete.value.ID)
    $q.notify({ type: 'positive', message: 'Análise excluída com sucesso!' })
    deleteDialog.value = false
    await manejoStore.fetchAnalisesSolo({ filtros: filtros.value })
    await generateAlertas()
  } catch (error) {
    $q.notify({ type: 'negative', message: error.message || 'Erro ao excluir análise' })
  }
}

// Upload de laudo
function uploadLaudo(analise) {
  analiseUpload.value = analise
  arquivoSelecionado.value = null
  uploadDialog.value = true
}

async function submitUpload() {
  if (!arquivoSelecionado.value) return
  
  uploadLoading.value = true
  try {
    await manejoStore.uploadLaudoAnalise(analiseUpload.value.ID, arquivoSelecionado.value)
    $q.notify({ type: 'positive', message: 'Laudo enviado com sucesso!' })
    uploadDialog.value = false
    await manejoStore.fetchAnalisesSolo({ filtros: filtros.value })
  } catch (error) {
    $q.notify({ type: 'negative', message: error.message || 'Erro ao enviar laudo' })
  } finally {
    uploadLoading.value = false
  }
}

function onFileRejected(rejectedEntries) {
  $q.notify({
    type: 'negative',
    message: `Arquivo rejeitado: ${rejectedEntries[0].failedPropValidation}`
  })
}

async function downloadLaudo(analise) {
  if (!analise.ARQUIVO_LAUDO) {
    $q.notify({
      type: 'warning',
      message: 'Nenhum laudo disponível para download'
    })
    return
  }
  
  try {
    $q.loading.show({
      message: 'Preparando download...'
    })
    
    // Usar método da store para download
    const result = await manejoStore.downloadLaudoAnalise(analise.ID)
    
    $q.notify({
      type: 'positive',
      message: `Download concluído: ${result.nomeArquivo}`,
      timeout: 3000
    })
    
  } catch (error) {
    console.error('Erro no download:', error)
    $q.notify({
      type: 'negative',
      message: error.message || 'Erro ao fazer download do laudo'
    })
  } finally {
    $q.loading.hide()
  }
}

// Carregamento de opções
async function loadOptions() {
  try {
    await terrenoStore.fetchTerrenos({ limit: 100 })
    terrenoOptions.value = terrenoStore.terrenos.map(t => ({
      value: t.ID,
      label: t.NOME
    }))
    terrenoOptionsDialog.value = [...terrenoOptions.value]
  } catch (error) {
    console.error('Erro ao carregar terrenos:', error)
  }
}

// Filtros
function filterTerrenos(val, update) {
  update(() => {
    if (val === '') {
      terrenoOptions.value = [...terrenoOptionsDialog.value]
    } else {
      const needle = val.toLowerCase()
      terrenoOptions.value = terrenoOptionsDialog.value.filter(
        t => t.label.toLowerCase().includes(needle)
      )
    }
  })
}

function filterTerrenosDialog(val, update) {
  update(() => {
    if (val === '') {
      terrenoOptionsDialog.value = [...terrenoOptions.value]
    } else {
      const needle = val.toLowerCase()
      terrenoOptionsDialog.value = terrenoOptions.value.filter(
        t => t.label.toLowerCase().includes(needle)
      )
    }
  })
}

// Helpers agronômicos
function getStatusPH(ph) {
  if (!ph) return ''
  if (ph < 5.5) return 'Muito Ácido'
  if (ph < 6.0) return 'Ácido'
  if (ph <= 7.0) return 'Adequado'
  if (ph <= 7.5) return 'Neutro'
  return 'Alcalino'
}

function getStatusMO(mo) {
  if (!mo) return ''
  if (mo < 2.0) return 'Baixo'
  if (mo < 3.0) return 'Médio'
  if (mo < 4.0) return 'Bom'
  return 'Alto'
}

function getStatusSaturacao(sat) {
  if (!sat) return ''
  if (sat < 50) return 'Baixo'
  if (sat < 70) return 'Médio'
  if (sat < 80) return 'Bom'
  return 'Alto'
}

function getStatusCTC(ctc) {
  if (!ctc) return ''
  if (ctc < 8) return 'Baixo'
  if (ctc < 15) return 'Médio'
  return 'Alto'
}

function getHintPH(ph) {
  if (!ph) return 'Ideal: 6.0 - 7.0'
  return `Status: ${getStatusPH(ph)}`
}

function getHintMO(mo) {
  if (!mo) return 'Ideal: > 2.5%'
  return `Status: ${getStatusMO(mo)}`
}

function getHintSaturacao(sat) {
  if (!sat) return 'Ideal: > 60%'
  return `Status: ${getStatusSaturacao(sat)}`
}

// Classes CSS
function getClassePH(ph) {
  if (!ph) return ''
  if (ph < 5.5 || ph > 7.5) return 'text-negative'
  if (ph >= 6.0 && ph <= 7.0) return 'text-positive'
  return 'text-warning'
}

function getClassePHMedio() {
  return getClassePH(estatisticas.value.phMedio)
}

function getClasseMO(mo) {
  if (!mo) return ''
  if (mo < 2.0) return 'text-negative'
  if (mo >= 2.5) return 'text-positive'
  return 'text-warning'
}

function getClasseSaturacao() {
  return getClasseSaturacaoValor(estatisticas.value.saturacaoMedia)
}

function getClasseSaturacaoValor(sat) {
  if (!sat) return ''
  if (sat < 50) return 'text-negative'
  if (sat >= 60) return 'text-positive'
  return 'text-warning'
}

// Status da análise
function getCorStatus(analise) {
  if (!analise.DATA_RESULTADO) return 'orange'
  const hoje = new Date()
  const dataResultado = new Date(analise.DATA_RESULTADO)
  
  if (dataResultado > hoje) return 'blue' // Data futura = aguardando
  return 'positive' // Data passada/presente = concluído
}

function getIconeStatus(analise) {
  if (!analise.DATA_RESULTADO) return 'schedule' // Sem data = agendado
  
  const hoje = new Date()
  const dataResultado = new Date(analise.DATA_RESULTADO)
  
  if (dataResultado > hoje) return 'hourglass_empty' // Data futura = aguardando
  return 'check_circle' // Data passada/presente = concluído
}

function getStatusResultado(analise) {
  if (!analise.DATA_RESULTADO) return 'Pendente' // Sem data
  
  const hoje = new Date()
  const dataResultado = new Date(analise.DATA_RESULTADO)
  
  if (dataResultado > hoje) {
    const diasRestantes = Math.ceil((dataResultado - hoje) / (1000 * 60 * 60 * 24))
    return `Aguardando (${diasRestantes}d)`
  }
  
  return 'Concluído'
}

// Helpers de visualização
function temMacronutrientes(analise) {
  return analise?.FOSFORO || analise?.POTASSIO || analise?.CALCIO || analise?.MAGNESIO
}

function temMicronutrientes(analise) {
  return analise?.ENXOFRE || analise?.BORO || analise?.COBRE || analise?.FERRO || analise?.MANGANES || analise?.ZINCO
}

function formatarData(data) {
  if (!data) return '-'
  return new Date(data).toLocaleDateString('pt-BR')
}

// Alertas de solo
async function generateAlertas() {
  const analises = manejoStore.analisesSolo
  const hoje = new Date()
  const alertas = []
  
  analises.forEach(analise => {
    const problemas = []
    
    // Só analisar se tem resultado concluído (data <= hoje)
    const temResultadoConcluido = analise.DATA_RESULTADO && new Date(analise.DATA_RESULTADO) <= hoje
    
    if (temResultadoConcluido) {
      if (analise.PH_AGUA && (analise.PH_AGUA < 5.5 || analise.PH_AGUA > 7.5)) {
        problemas.push('pH inadequado')
      }
      
      if (analise.MATERIA_ORGANICA && analise.MATERIA_ORGANICA < 2.0) {
        problemas.push('M.O. baixa')
      }
      
      if (analise.SATURACAO_BASES && analise.SATURACAO_BASES < 50) {
        problemas.push('Saturação baixa')
      }
      
      if (problemas.length > 0) {
        alertas.push({
          terreno_id: analise.ID_TERRENO,
          terreno_nome: analise.terreno_nome,
          problema: problemas.join(', '),
          status: problemas.length > 2 ? 'critico' : 'atencao'
        })
      }
    }
  })
  
  alertasSolo.value = alertas
}

function getCorAlerta(status) {
  return status === 'critico' ? 'negative' : 'warning'
}

function viewAlerta(alerta) {
  $q.dialog({
    title: 'Alerta de Solo',
    message: `
      <strong>Terreno:</strong> ${alerta.terreno_nome}<br>
      <strong>Problemas:</strong> ${alerta.problema}<br>
      <br>
      <em>Recomenda-se verificar a análise completa e aplicar as correções necessárias.</em>
    `,
    html: true
  })
}

function showAllAlertas() {
  $q.notify({ type: 'info', message: 'Modal com todos os alertas em desenvolvimento' })
}

// Lifecycle
onMounted(async () => {
  await loadOptions()
  await manejoStore.fetchAnalisesSolo({ filtros: filtros.value })
  await generateAlertas()
})
</script>

<style scoped>
@import 'src/css/components/analisessolo.css';
</style>