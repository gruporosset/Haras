<template>
  <q-card style="width: 700px; max-width: 90vw">
    <q-form @submit="handleSubmit">
      <q-card-section>
        <div class="text-h6">
          {{ form.ID ? 'Editar' : 'Cadastrar' }} Reprodução
        </div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <div class="row q-gutter-md">
          <q-select
            v-model="form.ID_EGUA"
            :options="femeaOptions"
            label="Égua *"
            :rules="[val => !!val || 'Égua é obrigatória']"
            use-input
            @filter="filterFemeas"
            class="col-5"
          />
          <q-select
            v-model="form.ID_PARCEIRO"
            :options="machoOptions"
            label="Parceiro"
            clearable
            use-input
            @filter="filterMachos"
            class="col-5"
          />
        </div>

        <div class="row q-gutter-md q-mt-sm">
          <q-select
            v-model="form.TIPO_COBERTURA"
            :options="reproducaoStore.tiposCobertura"
            label="Tipo de Cobertura *"
            :rules="[val => !!val || 'Tipo é obrigatório']"
            class="col-5"
          />
          <CalendarioComponent
            v-model="form.DATA_COBERTURA"
            label="Data da Cobertura *"
            :rules="[val => !!val || 'Data é obrigatória']"
            class="col-5"
          />
        </div>

        <div class="row q-gutter-md q-mt-sm">
          <CalendarioComponent
            v-model="form.DATA_DIAGNOSTICO"
            label="Data do Diagnóstico"
            class="col-5"
          />
          <q-select
            v-model="form.RESULTADO_DIAGNOSTICO"
            :options="reproducaoStore.resultadosDiagnostico"
            label="Resultado"
            class="col-5"
          />
        </div>

        <div class="row q-gutter-md q-mt-sm">
          <CalendarioComponent
            v-model="form.DATA_PARTO_PREVISTA"
            label="Parto Previsto"
            class="col-5"
          />
          <CalendarioComponent
            v-model="form.DATA_PARTO_REAL"
            label="Parto Realizado"
            class="col-5"
          />
        </div>

        <q-select
          v-model="form.STATUS_REPRODUCAO"
          :options="reproducaoStore.statusReproducao"
          label="Status"
          class="q-mt-sm"
        />

        <q-input
          v-model="form.OBSERVACOES"
          label="Observações"
          type="textarea"
          rows="3"
          class="q-mt-sm"
        />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn
          flat
          label="Cancelar"
          color="gray"
          @click="$emit('cancelar')"
        />
        <q-btn
          type="submit"
          color="primary"
          label="Salvar"
          :disable="reproducaoStore.loading"
        />
      </q-card-actions>
    </q-form>
  </q-card>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useAuthStore } from 'stores/auth'
  import { useReproducaoStore } from 'stores/reproducao'
  import { useAnimalStore } from 'stores/animal'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'
  import { prepareFormData } from 'src/utils/dateUtils'
  import { ErrorHandler } from 'src/utils/errorHandler'

  // Props
  const props = defineProps({
    reproducao: {
      type: Object,
      default: null,
    },
  })

  // Emits
  const emit = defineEmits(['salvar', 'cancelar'])

  // Stores
  const authStore = useAuthStore()
  const reproducaoStore = useReproducaoStore()
  const animalStore = useAnimalStore()

  // Opções
  const femeaOptions = ref([])
  const machoOptions = ref([])

  // Formulário
  const form = ref({
    ID: null,
    ID_EGUA: null,
    ID_PARCEIRO: null,
    TIPO_COBERTURA: null,
    DATA_COBERTURA: '',
    DATA_DIAGNOSTICO: '',
    RESULTADO_DIAGNOSTICO: { value: 'PENDENTE', label: 'Pendente' },
    STATUS_REPRODUCAO: { value: 'ATIVO', label: 'Ativo' },
    DATA_PARTO_PREVISTA: '',
    DATA_PARTO_REAL: '',
    OBSERVACOES: '',
    ID_USUARIO_REGISTRO: authStore.user.ID,
  })

  // Funções de filtro
  function filterFemeas(val, update) {
    update(() => {
      if (val === '') {
        femeaOptions.value = animalStore.parentOptions.femeas
      } else {
        const needle = val.toLowerCase()
        femeaOptions.value = animalStore.parentOptions.femeas.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  function filterMachos(val, update) {
    update(() => {
      if (val === '') {
        machoOptions.value = animalStore.parentOptions.machos
      } else {
        const needle = val.toLowerCase()
        machoOptions.value = animalStore.parentOptions.machos.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
  }

  // Handlers
  async function handleSubmit() {
    try {
      const dateFields = [
        'DATA_COBERTURA',
        'DATA_DIAGNOSTICO',
        'DATA_PARTO_PREVISTA',
        'DATA_PARTO_REAL',
      ]
      const formData = prepareFormData(form.value, dateFields)

      if (formData.ID) {
        await reproducaoStore.updateReproducao(formData.ID, formData)
      } else {
        await reproducaoStore.createReproducao(formData)
      }

      emit('salvar')
    } catch (error) {
      ErrorHandler.handle(error)
    }
  }

  // Inicialização do formulário
  function initializeForm() {
    if (props.reproducao) {
      const egua = femeaOptions.value.find(
        f => f.value === props.reproducao.ID_EGUA
      )
      const parceiro = machoOptions.value.find(
        m => m.value === props.reproducao.ID_PARCEIRO
      )
      const tipo = reproducaoStore.tiposCobertura.find(
        t => t.value === props.reproducao.TIPO_COBERTURA
      )
      const resultado = reproducaoStore.resultadosDiagnostico.find(
        r => r.value === props.reproducao.RESULTADO_DIAGNOSTICO
      )
      const status = reproducaoStore.statusReproducao.find(
        s => s.value === props.reproducao.STATUS_REPRODUCAO
      )

      form.value = {
        ...props.reproducao,
        ID_EGUA: egua || props.reproducao.ID_EGUA,
        ID_PARCEIRO: parceiro || null,
        TIPO_COBERTURA: tipo || props.reproducao.TIPO_COBERTURA,
        RESULTADO_DIAGNOSTICO:
          resultado || props.reproducao.RESULTADO_DIAGNOSTICO,
        STATUS_REPRODUCAO: status || props.reproducao.STATUS_REPRODUCAO,
        ID_USUARIO_REGISTRO: authStore.user.ID,
      }
    } else {
      form.value = {
        ID: null,
        ID_EGUA: null,
        ID_PARCEIRO: null,
        TIPO_COBERTURA: null,
        DATA_COBERTURA: '',
        DATA_DIAGNOSTICO: '',
        RESULTADO_DIAGNOSTICO: { value: 'PENDENTE', label: 'Pendente' },
        STATUS_REPRODUCAO: { value: 'ATIVO', label: 'Ativo' },
        DATA_PARTO_PREVISTA: '',
        DATA_PARTO_REAL: '',
        OBSERVACOES: '',
        ID_USUARIO_REGISTRO: authStore.user.ID,
      }
    }
  }

  // Carregar opções
  async function loadOptions() {
    try {
      await animalStore.loadParentOptions()
      femeaOptions.value = animalStore.parentOptions.femeas
      machoOptions.value = animalStore.parentOptions.machos
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar opções')
    }
  }

  // Inicialização
  onMounted(async () => {
    await loadOptions()
    initializeForm()
  })
</script>
