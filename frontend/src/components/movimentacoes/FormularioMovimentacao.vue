<template>
  <q-dialog
    v-model="dialog"
    persistent
    full-width
  >
    <q-card style="min-width: 800px">
      <q-card-section>
        <div class="text-h6">
          {{ form.ID ? 'Editar Movimentação' : 'Nova Movimentação' }}
        </div>
        <div class="text-subtitle2 text-grey-6">
          {{
            form.ID
              ? `Editando movimentação #${form.ID}`
              : 'Registrar nova movimentação de animal'
          }}
        </div>
      </q-card-section>

      <q-card-section>
        <q-form
          @submit="submitForm"
          ref="formRef"
          class="q-gutter-md"
        >
          <!-- Animal -->
          <div class="row q-gutter-md">
            <div class="col-12 col-md-5">
              <q-select
                v-model="form.ID_ANIMAL"
                :options="animalOptions"
                label="Animal *"
                clearable
                use-input
                hide-selected
                fill-input
                input-debounce="300"
                @filter="filterAnimais"
                :rules="[val => !!val || 'Animal é obrigatório']"
              >
                <template v-slot:no-option>
                  <q-item>
                    <q-item-section class="text-grey">
                      Nenhum animal encontrado
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
            </div>

            <div class="col-12 col-md-3">
              <q-select
                v-model="form.TIPO_MOVIMENTACAO"
                :options="movimentacaoStore.tiposMovimentacao"
                label="Tipo de Movimentação *"
                :rules="[val => !!val || 'Tipo é obrigatório']"
                @update:model-value="onTipoChange"
              />
            </div>

            <div class="col-12 col-md-4">
              <CalendarioComponent
                v-model="form.DATA_MOVIMENTACAO"
                label="Data da Movimentação *"
                :rules="[
                  val => !!val || 'Data é obrigatória',
                  val => !isDataFutura(val) || 'Data não pode ser no futuro',
                ]"
              />
            </div>
          </div>

          <!-- Origem e Destino -->
          <div class="row q-gutter-md">
            <!-- Origem -->
            <div class="col-12 col-md-6">
              <q-card
                flat
                bordered
                class="q-pa-md"
              >
                <div class="text-subtitle2 q-mb-md">
                  Origem
                  <span
                    v-if="origemObrigatoria"
                    class="text-red"
                  >
                    *
                  </span>
                </div>

                <q-select
                  v-model="form.ID_TERRENO_ORIGEM"
                  :options="terrenoOptions"
                  label="Terreno de Origem"
                  clearable
                  :disable="!form.TIPO_MOVIMENTACAO"
                  :rules="
                    origemObrigatoria
                      ? [
                          val =>
                            !!val ||
                            !!form.ORIGEM_EXTERNA ||
                            'Origem é obrigatória',
                        ]
                      : []
                  "
                />

                <div class="text-center q-my-sm text-grey-6">OU</div>

                <q-input
                  v-model="form.ORIGEM_EXTERNA"
                  label="Origem Externa"
                  placeholder="Ex: Haras XYZ, Feira de Cavalos..."
                  :disable="!form.TIPO_MOVIMENTACAO"
                  :rules="
                    origemObrigatoria && !form.ID_TERRENO_ORIGEM
                      ? [val => !!val || 'Origem é obrigatória']
                      : []
                  "
                />
              </q-card>
            </div>

            <!-- Destino -->
            <div class="col-12 col-md-6">
              <q-card
                flat
                bordered
                class="q-pa-md"
              >
                <div class="text-subtitle2 q-mb-md">
                  Destino
                  <span
                    v-if="destinoObrigatorio"
                    class="text-red"
                  >
                    *
                  </span>
                </div>

                <q-select
                  v-model="form.ID_TERRENO_DESTINO"
                  :options="terrenoOptions"
                  label="Terreno de Destino"
                  clearable
                  :disable="!form.TIPO_MOVIMENTACAO"
                  :rules="
                    destinoObrigatorio
                      ? [
                          val =>
                            !!val ||
                            !!form.DESTINO_EXTERNO ||
                            'Destino é obrigatório',
                        ]
                      : []
                  "
                />

                <div class="text-center q-my-sm text-grey-6">OU</div>

                <q-input
                  v-model="form.DESTINO_EXTERNO"
                  label="Destino Externo"
                  placeholder="Ex: Haras ABC, Comprador..."
                  :disable="!form.TIPO_MOVIMENTACAO"
                  :rules="
                    destinoObrigatorio && !form.ID_TERRENO_DESTINO
                      ? [val => !!val || 'Destino é obrigatório']
                      : []
                  "
                />
              </q-card>
            </div>
          </div>

          <!-- Motivo e Observações -->
          <div class="row q-gutter-md">
            <div class="col-12 col-md-6">
              <q-input
                v-model="form.MOTIVO"
                label="Motivo"
                placeholder="Ex: Mudança de pasto, venda..."
                maxlength="200"
              />
            </div>

            <div class="col-12 col-md-6">
              <q-input
                v-model="form.OBSERVACOES"
                label="Observações"
                type="textarea"
                rows="3"
                placeholder="Observações adicionais..."
              />
            </div>
          </div>

          <!-- Alertas de Validação -->
          <q-banner
            v-if="form.TIPO_MOVIMENTACAO"
            class="bg-blue-1 text-primary"
          >
            <template v-slot:avatar>
              <q-icon name="info" />
            </template>
            {{ getValidationMessage() }}
          </q-banner>
        </q-form>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn
          flat
          label="Cancelar"
          color="grey"
          @click="closeDialog"
        />
        <q-btn
          color="primary"
          label="Salvar"
          type="submit"
          :loading="movimentacaoStore.loading"
          @click="submitForm"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useMovimentacaoStore } from 'stores/movimentacao'
  import { useAnimalStore } from 'stores/animal'
  import { useTerrenoStore } from 'stores/terreno'
  import { useAuthStore } from 'stores/auth'
  import { ErrorHandler } from 'src/utils/errorHandler'
  import { convertToISO } from 'src/utils/dateUtils'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

  // Emits
  const emit = defineEmits(['saved'])

  // Stores
  const movimentacaoStore = useMovimentacaoStore()
  const animalStore = useAnimalStore()
  const terrenoStore = useTerrenoStore()
  const authStore = useAuthStore()

  // Estado reativo
  const dialog = ref(false)
  const formRef = ref(null)
  const animalOptions = ref([])
  const terrenoOptions = ref([])

  // Formulário
  const form = ref({
    ID: null,
    ID_ANIMAL: null,
    TIPO_MOVIMENTACAO: null,
    DATA_MOVIMENTACAO: '',
    ID_TERRENO_ORIGEM: null,
    ID_TERRENO_DESTINO: null,
    ORIGEM_EXTERNA: '',
    DESTINO_EXTERNO: '',
    MOTIVO: '',
    OBSERVACOES: '',
    ID_USUARIO_REGISTRO: authStore.user?.ID,
  })

  // Computed
  const origemObrigatoria = computed(() => {
    const tipo = form.value.TIPO_MOVIMENTACAO?.value
    return ['SAIDA', 'TRANSFERENCIA', 'VENDA', 'EMPRESTIMO'].includes(tipo)
  })

  const destinoObrigatorio = computed(() => {
    const tipo = form.value.TIPO_MOVIMENTACAO?.value
    return ['ENTRADA', 'TRANSFERENCIA', 'RETORNO'].includes(tipo)
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

      // Carregar terrenos
      await terrenoStore.fetchTerrenos({ limit: 100 })
      terrenoOptions.value = terrenoStore.terrenos.map(t => ({
        value: t.ID,
        label: t.NOME,
      }))
    } catch (error) {
      console.error('Erro ao carregar opções:', error)
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
        const allAnimals = [
          ...animalStore.parentOptions.machos,
          ...animalStore.parentOptions.femeas,
        ]
        animalOptions.value = allAnimals.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  function onTipoChange() {
    // Limpar campos quando mudar o tipo
    form.value.ID_TERRENO_ORIGEM = null
    form.value.ID_TERRENO_DESTINO = null
    form.value.ORIGEM_EXTERNA = ''
    form.value.DESTINO_EXTERNO = ''
  }

  function isDataFutura(data) {
    if (!data) return false
    const hoje = new Date()
    const dataMovimentacao = new Date(data)
    return dataMovimentacao > hoje
  }

  function getValidationMessage() {
    const tipo = form.value.TIPO_MOVIMENTACAO?.value

    switch (tipo) {
      case 'ENTRADA':
        return 'Para ENTRADA: destino é obrigatório (terreno interno ou externo)'
      case 'SAIDA':
        return 'Para SAÍDA: origem é obrigatória (terreno interno ou externo)'
      case 'TRANSFERENCIA':
        return 'Para TRANSFERÊNCIA: origem e destino são obrigatórios'
      case 'VENDA':
        return 'Para VENDA: origem é obrigatória, destino opcional'
      case 'EMPRESTIMO':
        return 'Para EMPRÉSTIMO: origem é obrigatória, destino opcional'
      case 'RETORNO':
        return 'Para RETORNO: destino é obrigatório (terreno interno)'
      default:
        return 'Selecione o tipo de movimentação para ver as regras'
    }
  }

  function openDialog(movimentacao = null) {
    if (movimentacao) {
      // Edição - encontrar objetos completos para os selects
      const terrenoOrigem = terrenoOptions.value.find(
        t => t.value === movimentacao.ID_TERRENO_ORIGEM
      )
      const terrenoDestino = terrenoOptions.value.find(
        t => t.value === movimentacao.ID_TERRENO_DESTINO
      )
      const animal = animalOptions.value.find(
        a => a.value === movimentacao.ID_ANIMAL
      )
      const tipo = movimentacaoStore.tiposMovimentacao.find(
        t => t.value === movimentacao.TIPO_MOVIMENTACAO
      )

      form.value = {
        ...movimentacao,
        ID_ANIMAL: animal || movimentacao.ID_ANIMAL,
        TIPO_MOVIMENTACAO: tipo || movimentacao.TIPO_MOVIMENTACAO,
        ID_TERRENO_ORIGEM: terrenoOrigem || null,
        ID_TERRENO_DESTINO: terrenoDestino || null,
        DATA_MOVIMENTACAO: movimentacao.DATA_MOVIMENTACAO || '',
        ID_USUARIO_REGISTRO: authStore.user?.ID,
      }
    } else {
      // Novo registro
      form.value = {
        ID: null,
        ID_ANIMAL: null,
        TIPO_MOVIMENTACAO: null,
        DATA_MOVIMENTACAO: '',
        ID_TERRENO_ORIGEM: null,
        ID_TERRENO_DESTINO: null,
        ORIGEM_EXTERNA: '',
        DESTINO_EXTERNO: '',
        MOTIVO: '',
        OBSERVACOES: '',
        ID_USUARIO_REGISTRO: authStore.user?.ID,
      }
    }

    dialog.value = true
  }

  async function submitForm() {
    try {
      const isValid = await formRef.value?.validate()
      if (!isValid) {
        ErrorHandler.handle({}, 'Por favor, corrija os campos obrigatórios')
        return
      }

      const formData = {
        ...form.value,
        ID_ANIMAL:
          typeof form.value.ID_ANIMAL === 'object'
            ? form.value.ID_ANIMAL?.value
            : form.value.ID_ANIMAL,
        TIPO_MOVIMENTACAO:
          typeof form.value.TIPO_MOVIMENTACAO === 'object'
            ? form.value.TIPO_MOVIMENTACAO?.value
            : form.value.TIPO_MOVIMENTACAO,
        ID_TERRENO_ORIGEM:
          typeof form.value.ID_TERRENO_ORIGEM === 'object'
            ? form.value.ID_TERRENO_ORIGEM?.value
            : form.value.ID_TERRENO_ORIGEM,
        ID_TERRENO_DESTINO:
          typeof form.value.ID_TERRENO_DESTINO === 'object'
            ? form.value.ID_TERRENO_DESTINO?.value
            : form.value.ID_TERRENO_DESTINO,
        // Converter strings vazias para null
        ORIGEM_EXTERNA: form.value.ORIGEM_EXTERNA || null,
        DESTINO_EXTERNO: form.value.DESTINO_EXTERNO || null,
        MOTIVO: form.value.MOTIVO || null,
        DATA_MOVIMENTACAO: convertToISO(form.value.DATA_MOVIMENTACAO),
      }

      if (formData.ID) {
        await movimentacaoStore.updateMovimentacao(formData.ID, formData)
        ErrorHandler.success('Movimentação atualizada com sucesso!')
      } else {
        await movimentacaoStore.createMovimentacao(formData)
        ErrorHandler.success('Movimentação criada com sucesso!')
      }

      closeDialog()
      emit('saved')
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao salvar movimentação')
    }
  }

  function closeDialog() {
    dialog.value = false
  }

  // Exposição de métodos para o componente pai
  defineExpose({
    openDialog,
  })

  // Lifecycle
  onMounted(async () => {
    await loadOptions()
  })
</script>
