<template>
  <q-dialog
    v-model="dialogModel"
    persistent
  >
    <q-card style="width: 700px; max-width: 90vw">
      <q-card-section>
        <div class="text-h6">
          {{ editando ? 'Editar' : 'Novo' }} Registro de Ferrageamento
        </div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-form
          ref="formRef"
          @submit="salvarRegistro"
        >
          <!-- Dados Básicos -->
          <div class="row q-gutter-md">
            <q-select
              v-model="form.ID_ANIMAL"
              :options="animalOptions"
              label="Animal *"
              use-input
              @filter="filterAnimais"
              class="col-5"
              :rules="[val => !!val || 'Selecione um animal']"
              emit-value
              map-options
            />
            <calendario-component
              v-model="form.DATA_OCORRENCIA"
              label="Data da Ocorrência *"
              class="col-3"
              :rules="[val => !!val || 'Data é obrigatória']"
            />
            <q-select
              v-model="form.TIPO_FERRAGEAMENTO"
              :options="ferrageamentoStore.tiposFerrageamento"
              label="Tipo *"
              emit-value
              map-options
              class="col-3"
              :rules="[val => !!val || 'Tipo é obrigatório']"
            />
          </div>

          <!-- Detalhes do Serviço -->
          <q-separator class="q-my-md" />
          <div class="text-subtitle1 q-mb-md">Detalhes do Serviço</div>

          <div class="row q-gutter-md">
            <q-select
              v-model="form.MEMBRO_TRATADO"
              :options="ferrageamentoStore.membrosOpcoes"
              label="Membro(s) Tratado(s)"
              emit-value
              map-options
              class="col-4"
            />
            <q-select
              v-model="form.STATUS_CASCO"
              :options="ferrageamentoStore.statusCasco"
              label="Status do Casco"
              emit-value
              map-options
              class="col-4"
            />
            <q-select
              v-model="form.TIPO_FERRADURA"
              :options="ferrageamentoStore.tiposFerradura"
              label="Tipo de Ferradura"
              emit-value
              map-options
              clearable
              class="col-3"
            />
          </div>

          <div class="row q-gutter-md">
            <q-input
              v-model="form.FERRADOR_RESPONSAVEL"
              label="Ferrador Responsável *"
              class="col-6"
              :rules="[val => !!val || 'Ferrador é obrigatório']"
            />
            <q-input
              v-model.number="form.CUSTO"
              label="Custo (R$)"
              type="number"
              step="0.01"
              min="0"
              prefix="R$"
              class="col-3"
            />
          </div>

          <!-- Datas de Controle -->
          <q-separator class="q-my-md" />
          <div class="text-subtitle1 q-mb-md">Controle de Datas</div>

          <div class="row q-gutter-md">
            <calendario-component
              v-model="form.PROXIMA_AVALIACAO"
              label="Próxima Avaliação"
              class="col-4"
              hint="Data sugerida para próxima verificação"
            />
            <calendario-component
              v-model="form.DATA_PREV_PROX_FERRAGEAMENTO"
              label="Próximo Ferrageamento Previsto"
              class="col-4"
              hint="Previsão para próximo ferrageamento"
            />
          </div>

          <!-- Observações e Detalhes -->
          <q-separator class="q-my-md" />
          <div class="text-subtitle1 q-mb-md">
            Observações e Detalhes
            <q-btn
              flat
              size="sm"
              :icon="mostrarDetalhes ? 'expand_less' : 'expand_more'"
              @click="mostrarDetalhes = !mostrarDetalhes"
              class="q-ml-sm"
            />
          </div>

          <q-slide-transition>
            <div v-show="mostrarDetalhes">
              <div class="row q-gutter-md">
                <q-input
                  v-model="form.PROBLEMAS_IDENTIFICADOS"
                  label="Problemas Identificados"
                  type="textarea"
                  rows="2"
                  class="col-6"
                  hint="Descreva problemas encontrados"
                />
                <q-input
                  v-model="form.TRATAMENTO_REALIZADO"
                  label="Tratamento Realizado"
                  type="textarea"
                  rows="2"
                  class="col-5"
                  hint="Detalhe o tratamento aplicado"
                />
              </div>

              <div class="row q-gutter-md">
                <q-input
                  v-model="form.MEDICAMENTOS_UTILIZADOS"
                  label="Medicamentos Utilizados"
                  class="col-6"
                  hint="Liste medicamentos aplicados"
                />
                <q-input
                  v-model="form.RECOMENDACOES"
                  label="Recomendações"
                  type="textarea"
                  rows="2"
                  class="col-5"
                  hint="Orientações para cuidados futuros"
                />
              </div>
            </div>
          </q-slide-transition>

          <!-- Observações Gerais -->
          <q-input
            v-model="form.OBSERVACOES"
            label="Observações Gerais"
            type="textarea"
            rows="3"
            class="full-width q-mt-md"
            hint="Informações adicionais sobre o procedimento"
          />
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
          @click="salvarRegistro"
          :loading="ferrageamentoStore.loading"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
  import { ref, computed } from 'vue'
  import { useFerrageamentoStore } from 'stores/ferrageamento'
  import { useAnimalStore } from 'stores/animal'
  import { useAuthStore } from 'stores/auth'
  import { ErrorHandler } from 'src/utils/errorHandler'
  import { prepareFormData } from 'src/utils/dateUtils'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

  // Props
  defineProps({
    modelValue: {
      type: Boolean,
      default: false,
    },
  })

  // Emits
  const emit = defineEmits(['update:modelValue', 'saved'])

  // Stores
  const ferrageamentoStore = useFerrageamentoStore()
  const animalStore = useAnimalStore()
  const authStore = useAuthStore()

  // Estado reativo
  const dialog = ref(false)
  const formRef = ref(null)
  const editando = ref(false)
  const mostrarDetalhes = ref(false)

  // Opções
  const animalOri = ref([])
  const animalOptions = ref([])

  // Formulário
  const form = ref({})

  // Computed
  const dialogModel = computed({
    get: () => dialog.value,
    set: val => {
      dialog.value = val
      emit('update:modelValue', val)
    },
  })

  // Métodos
  async function loadAnimais() {
    try {
      await animalStore.fetchAnimais({ limit: 100 })
      animalOri.value = animalStore.animais.map(a => ({
        value: a.ID,
        label: a.NOME,
      }))
      animalOptions.value = [...animalOri.value]
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar animais')
    }
  }

  function filterAnimais(val, update) {
    update(() => {
      if (val === '') {
        animalOptions.value = animalOri.value
      } else {
        const needle = val.toLowerCase()
        animalOptions.value = animalOri.value.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  async function salvarRegistro() {
    try {
      const valid = await formRef.value.validate()
      if (!valid) return

      const dateFields = [
        'DATA_OCORRENCIA',
        'PROXIMA_AVALIACAO',
        'DATA_PREV_PROX_FERRAGEAMENTO',
      ]
      const formData = prepareFormData(form.value, dateFields)

      if (editando.value) {
        await ferrageamentoStore.updateFerrageamento(formData.ID, formData)
        ErrorHandler.success('Registro atualizado com sucesso!')
      } else {
        await ferrageamentoStore.createFerrageamento(formData)
        ErrorHandler.success('Registro criado com sucesso!')
      }

      emit('saved')
      fecharDialog()
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao salvar registro')
    }
  }

  function openDialog(registro = null) {
    if (registro) {
      editando.value = true
      form.value = {
        ...registro,
        ID_USUARIO_CADASTRO: authStore.user.ID,
      }
      mostrarDetalhes.value = !!(
        registro.PROBLEMAS_IDENTIFICADOS ||
        registro.TRATAMENTO_REALIZADO ||
        registro.MEDICAMENTOS_UTILIZADOS ||
        registro.RECOMENDACOES
      )
    } else {
      editando.value = false
      form.value = {
        ID: null,
        ID_ANIMAL: null,
        DATA_OCORRENCIA: new Date().toISOString().slice(0, 10),
        TIPO_FERRAGEAMENTO: 'FERRAGEAMENTO',
        MEMBRO_TRATADO: 'TODOS',
        FERRADOR_RESPONSAVEL: '',
        STATUS_CASCO: 'BOM',
        TIPO_FERRADURA: null,
        CUSTO: null,
        PROXIMA_AVALIACAO: '',
        DATA_PREV_PROX_FERRAGEAMENTO: '',
        PROBLEMAS_IDENTIFICADOS: '',
        TRATAMENTO_REALIZADO: '',
        MEDICAMENTOS_UTILIZADOS: '',
        RECOMENDACOES: '',
        OBSERVACOES: '',
        ID_USUARIO_CADASTRO: authStore.user.ID,
      }
      mostrarDetalhes.value = false
    }

    loadAnimais()
    dialog.value = true
  }

  function fecharDialog() {
    dialog.value = false
    form.value = {}
    editando.value = false
    mostrarDetalhes.value = false
  }

  function cancelar() {
    fecharDialog()
  }

  // Expor métodos
  defineExpose({
    openDialog,
  })
</script>
