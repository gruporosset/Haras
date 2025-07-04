<!-- frontend/src/components/forms/AnimalForm.vue -->
<template>
  <q-form
    @submit="onSubmit"
    class="q-gutter-md"
  >
    <div class="row q-gutter-md">
      <q-input
        filled
        v-model="form.NOME"
        label="Nome *"
        :rules="[val => !!val || 'Nome é obrigatório']"
        class="col-12 col-md-5"
      />

      <q-input
        filled
        v-model="form.NUMERO_REGISTRO"
        label="Número de Registro"
        class="col-12 col-md-3"
      />

      <q-input
        filled
        v-model="form.CHIP_IDENTIFICACAO"
        label="Chip de Identificação"
        class="col-12 col-md-3"
      />
    </div>

    <div class="row q-gutter-md">
      <q-select
        filled
        v-model="form.SEXO"
        :options="sexoOptions"
        label="Sexo"
        emit-value
        map-options
        class="col-12 col-md-2"
      />

      <calendario-component
        v-model="form.DATA_NASCIMENTO"
        label="Data de Nascimento"
        class="col-12 col-md-3"
      />

      <q-input
        filled
        v-model="form.PELAGEM"
        label="Pelagem"
        class="col-12 col-md-3"
      />

      <q-select
        filled
        v-model="form.STATUS_ANIMAL"
        :options="statusOptions"
        label="Status"
        emit-value
        map-options
        class="col-12 col-md-3"
      />
    </div>

    <!-- Seção Proprietário -->
    <q-separator class="q-my-md" />
    <div class="text-h6 q-mb-md">Dados do Proprietário</div>

    <div class="row q-gutter-md">
      <q-input
        filled
        v-model="form.PROPRIETARIO"
        label="Nome do Proprietário"
        class="col-12 col-md-5"
      />

      <q-input
        filled
        v-model="form.CONTATO_PROPRIETARIO"
        label="Contato (Telefone/Email)"
        class="col-12 col-md-3"
      />

      <q-input
        filled
        v-model="form.CPF_CNPJ_PROPRIETARIO"
        label="CPF/CNPJ"
        mask="###.###.###-##"
        fill-mask="#"
        :rules="[validateCpfCnpj]"
        class="col-12 col-md-3"
        @update:model-value="formatCpfCnpj"
      />
    </div>

    <!-- Genealogia -->
    <q-separator class="q-my-md" />
    <div class="text-h6 q-mb-md">Genealogia</div>

    <div class="row q-gutter-md">
      <q-select
        filled
        v-model="form.ID_PAI"
        :options="paiOptions"
        option-value="value"
        option-label="label"
        label="Pai"
        emit-value
        map-options
        use-input
        @filter="filterPai"
        clearable
        class="col-12 col-md-5"
      />

      <q-select
        filled
        v-model="form.ID_MAE"
        :options="maeOptions"
        option-value="value"
        option-label="label"
        label="Mãe"
        emit-value
        map-options
        use-input
        @filter="filterMae"
        clearable
        class="col-12 col-md-5"
      />
    </div>

    <div class="row q-gutter-md">
      <q-input
        filled
        v-model="form.ORIGEM"
        label="Origem"
        class="col-12 col-md-5"
      />

      <q-input
        filled
        v-model="form.PESO_ATUAL"
        label="Peso Atual (kg)"
        type="number"
        step="0.01"
        min="0"
        class="col-12 col-md-3"
      />
    </div>

    <q-input
      filled
      v-model="form.OBSERVACOES"
      label="Observações"
      type="textarea"
      rows="3"
    />

    <div class="row justify-end q-gutter-sm q-mt-md">
      <q-btn
        flat
        label="Cancelar"
        color="grey"
        @click="$emit('cancel')"
      />
      <q-btn
        label="Salvar"
        type="submit"
        color="primary"
        :loading="loading"
      />
    </div>
  </q-form>
</template>

<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useAnimalStore } from 'stores/animal'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

  const props = defineProps({
    modelValue: Object,
    loading: Boolean,
  })

  const emit = defineEmits(['update:modelValue', 'submit', 'cancel'])

  const animalStore = useAnimalStore()

  const form = computed({
    get: () => props.modelValue || {},
    set: val => emit('update:modelValue', val),
  })

  const sexoOptions = [
    { label: 'Macho', value: 'M' },
    { label: 'Fêmea', value: 'F' },
  ]

  const statusOptions = [
    { label: 'Ativo', value: 'ATIVO' },
    { label: 'Vendido', value: 'VENDIDO' },
    { label: 'Morto', value: 'MORTO' },
    { label: 'Emprestado', value: 'EMPRESTADO' },
    { label: 'Aposentado', value: 'APOSENTADO' },
  ]

  const paiOptions = ref([])
  const maeOptions = ref([])
  const allAnimals = ref([])

  onMounted(async () => {
    await loadAnimals()
  })

  const loadAnimals = async () => {
    try {
      const response = await animalStore.fetchAnimais({ limit: 100 })
      allAnimals.value = response
    } catch (error) {
      console.error('Erro ao carregar animais:', error)
    }
  }

  const filterPai = (val, update) => {
    update(() => {
      const needle = val.toLowerCase()
      paiOptions.value = allAnimals.value.animais
        .filter(
          animal =>
            animal.SEXO === 'M' && animal.NOME.toLowerCase().includes(needle)
        )
        .map(animal => ({
          value: animal.ID,
          label: animal.NOME,
        }))
    })
  }

  const filterMae = (val, update) => {
    update(() => {
      const needle = val.toLowerCase()
      maeOptions.value = allAnimals.value.animais
        .filter(
          animal =>
            animal.SEXO === 'F' && animal.NOME.toLowerCase().includes(needle)
        )
        .map(animal => ({
          value: animal.ID,
          label: animal.NOME,
        }))
    })
  }

  const formatCpfCnpj = value => {
    if (!value) return

    const numbers = value.replace(/\D/g, '')

    if (numbers.length <= 11) {
      // CPF
      form.value.CPF_CNPJ_PROPRIETARIO = numbers.replace(
        /(\d{3})(\d{3})(\d{3})(\d{2})/,
        '$1.$2.$3-$4'
      )
    } else {
      // CNPJ
      form.value.CPF_CNPJ_PROPRIETARIO = numbers.replace(
        /(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/,
        '$1.$2.$3/$4-$5'
      )
    }
  }

  const validateCpfCnpj = value => {
    if (!value) return true

    const numbers = value.replace(/\D/g, '')

    if (numbers.length === 11 || numbers.length === 14) {
      return true
    }

    return 'CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos'
  }

  const onSubmit = () => {
    emit('submit', form.value)
  }
</script>
