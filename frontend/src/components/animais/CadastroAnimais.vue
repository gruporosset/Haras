<template>
  <div>
    <!-- Dialog de Cadastro/Edição -->
    <q-dialog
      v-model="dialogModel"
      persistent
    >
      <q-card style="min-width: 800px; max-width: 1000px">
        <q-card-section>
          <div class="text-h6">
            {{ editandoAnimal ? 'Editar Animal' : 'Novo Animal' }}
          </div>
        </q-card-section>

        <q-card-section>
          <q-form
            ref="formRef"
            @submit="saveAnimal"
            greedy
          >
            <!-- Dados Básicos -->
            <div class="text-subtitle1 q-mb-md">Dados Básicos</div>
            <div class="row q-gutter-md">
              <q-input
                v-model="form.NOME"
                label="Nome *"
                :rules="[val => !!val || 'Nome é obrigatório']"
                class="col-md-4 col-12"
              />
              <q-select
                v-model="form.SEXO"
                label="Sexo *"
                :options="sexoOptions"
                emit-value
                map-options
                :rules="[val => !!val || 'Sexo é obrigatório']"
                class="col-md-3 col-12"
              />
              <q-input
                v-model="form.NUMERO_REGISTRO"
                label="Número de Registro"
                class="col-md-4 col-12"
              />
            </div>

            <div class="row q-gutter-md">
              <q-input
                v-model="form.CHIP_IDENTIFICACAO"
                label="Chip de Identificação"
                class="col-md-4 col-12"
              />
              <calendario-component
                v-model="form.DATA_NASCIMENTO"
                label="Data de Nascimento *"
                :rules="[val => !!val || 'Data é obrigatória']"
                class="col-md-4 col-12"
              />
              <q-input
                v-model="form.PELAGEM"
                label="Pelagem *"
                :rules="[val => !!val || 'Pelagem é obrigatória']"
                class="col-md-3 col-12"
              />
            </div>

            <div class="row q-gutter-md">
              <q-select
                v-model="form.STATUS_ANIMAL"
                label="Status"
                :options="statusOptions"
                emit-value
                map-options
                class="col-md-3 col-12"
              />
              <q-input
                v-model="form.ORIGEM"
                label="Origem"
                class="col-md-4 col-12"
              />
              <q-input
                v-model.number="form.PESO_ATUAL"
                label="Peso Atual (kg)"
                type="number"
                step="0.1"
                min="0"
                class="col-md-3 col-12"
              />
            </div>

            <q-separator class="q-my-md" />

            <!-- Genealogia -->
            <div class="text-subtitle1 q-mb-md">Genealogia</div>
            <div class="row q-gutter-md">
              <q-select
                v-model="form.ID_PAI"
                label="Pai"
                :options="paiOptions"
                emit-value
                map-options
                clearable
                use-input
                input-debounce="300"
                @filter="filterPai"
                class="col-md-5 col-12"
              >
                <template v-slot:no-option>
                  <q-item>
                    <q-item-section class="text-grey">
                      Nenhum animal encontrado
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
              <q-select
                v-model="form.ID_MAE"
                label="Mãe"
                :options="maeOptions"
                emit-value
                map-options
                clearable
                use-input
                input-debounce="300"
                @filter="filterMae"
                class="col-md-5 col-12"
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

            <q-separator class="q-my-md" />

            <!-- Dados do Proprietário -->
            <div class="text-subtitle1 q-mb-md">Dados do Proprietário</div>
            <div class="row q-gutter-md">
              <q-input
                v-model="form.PROPRIETARIO"
                label="Nome do Proprietário"
                class="col-md-5 col-12"
              />
              <q-input
                v-model="form.CONTATO_PROPRIETARIO"
                label="Contato"
                class="col-md-3 col-12"
              />
              <q-input
                v-model="form.CPF_CNPJ_PROPRIETARIO"
                label="CPF/CNPJ"
                class="col-md-3 col-12"
              />
            </div>

            <!-- Observações -->
            <div class="row q-gutter-md">
              <q-input
                v-model="form.OBSERVACOES"
                label="Observações"
                type="textarea"
                rows="3"
                class="col-12"
              />
            </div>
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
            label="Salvar"
            color="primary"
            @click="saveAnimal"
            :loading="animalStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
  import { ref, computed, watch } from 'vue'
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
  const animalStore = useAnimalStore()
  const authStore = useAuthStore()

  // Estado reativo
  const dialog = ref(false)
  const formRef = ref(null)
  const editandoAnimal = ref(false)

  // Formulário
  const form = ref({})

  // Opções para seleção
  const animalOri = ref([])
  const paiOptions = ref([])
  const maeOptions = ref([])

  const sexoOptions = [
    { value: 'M', label: 'Macho' },
    { value: 'F', label: 'Fêmea' },
  ]

  const statusOptions = [
    { value: 'ATIVO', label: 'Ativo' },
    { value: 'VENDIDO', label: 'Vendido' },
    { value: 'MORTO', label: 'Morto' },
    { value: 'EMPRESTADO', label: 'Emprestado' },
    { value: 'APOSENTADO', label: 'Aposentado' },
  ]

  // Computed
  const dialogModel = computed({
    get: () => dialog.value,
    set: val => {
      dialog.value = val
      emit('update:modelValue', val)
    },
  })

  // Watchers
  watch(
    () => dialog.value,
    newVal => {
      if (newVal) {
        loadAnimalOptions()
      }
    }
  )

  // Métodos
  async function loadAnimalOptions() {
    try {
      await animalStore.fetchAnimais({ limit: 200 })
      animalOri.value = animalStore.animais.map(a => ({
        value: a.ID,
        label: `${a.NOME} (${a.NUMERO_REGISTRO || 'S/N'})`,
      }))

      // Filtrar opções iniciais
      updatePaiOptions()
      updateMaeOptions()
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar animais')
    }
  }

  function updatePaiOptions() {
    paiOptions.value = animalOri.value.filter(a => {
      const animal = animalStore.animais.find(an => an.ID === a.value)
      return animal && animal.SEXO === 'M' && animal.ID !== form.value.ID
    })
  }

  function updateMaeOptions() {
    maeOptions.value = animalOri.value.filter(a => {
      const animal = animalStore.animais.find(an => an.ID === a.value)
      return animal && animal.SEXO === 'F' && animal.ID !== form.value.ID
    })
  }

  function filterPai(val, update) {
    update(() => {
      if (val === '') {
        updatePaiOptions()
      } else {
        const needle = val.toLowerCase()
        paiOptions.value = animalOri.value.filter(a => {
          const animal = animalStore.animais.find(an => an.ID === a.value)
          return (
            animal &&
            animal.SEXO === 'M' &&
            animal.ID !== form.value.ID &&
            a.label.toLowerCase().indexOf(needle) > -1
          )
        })
      }
    })
  }

  function filterMae(val, update) {
    update(() => {
      if (val === '') {
        updateMaeOptions()
      } else {
        const needle = val.toLowerCase()
        maeOptions.value = animalOri.value.filter(a => {
          const animal = animalStore.animais.find(an => an.ID === a.value)
          return (
            animal &&
            animal.SEXO === 'F' &&
            animal.ID !== form.value.ID &&
            a.label.toLowerCase().indexOf(needle) > -1
          )
        })
      }
    })
  }

  async function saveAnimal() {
    try {
      const valid = await formRef.value.validate()
      if (!valid) return

      const dateFields = ['DATA_NASCIMENTO']
      const formData = prepareFormData(form.value, dateFields)

      if (formData.ID) {
        await animalStore.updateAnimal(formData.ID, formData)
        ErrorHandler.success('Animal atualizado com sucesso!')
      } else {
        await animalStore.createAnimal(formData)
        ErrorHandler.success('Animal cadastrado com sucesso!')
      }

      emit('saved')
      closeDialog()
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao salvar animal')
    }
  }

  function openDialog(animal = null) {
    if (animal) {
      editandoAnimal.value = true
      form.value = {
        ...animal,
        ID_USUARIO_CADASTRO: authStore.user.ID,
      }
    } else {
      editandoAnimal.value = false
      form.value = {
        ID: null,
        NOME: '',
        NUMERO_REGISTRO: '',
        CHIP_IDENTIFICACAO: '',
        SEXO: null,
        DATA_NASCIMENTO: '',
        PELAGEM: '',
        STATUS_ANIMAL: 'ATIVO',
        ID_PAI: null,
        ID_MAE: null,
        ORIGEM: '',
        OBSERVACOES: '',
        PESO_ATUAL: null,
        PROPRIETARIO: '',
        CONTATO_PROPRIETARIO: '',
        CPF_CNPJ_PROPRIETARIO: '',
        ID_USUARIO_CADASTRO: authStore.user.ID,
      }
    }
    dialog.value = true
  }

  function closeDialog() {
    dialog.value = false
    form.value = {}
    editandoAnimal.value = false
  }

  // Expor métodos para o componente pai
  defineExpose({
    openDialog,
    closeDialog,
  })
</script>

<style scoped>
  .q-card {
    max-height: 80vh;
    overflow-y: auto;
  }
</style>
