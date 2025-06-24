<template>
  <div class="crescimento-form">
    <!-- Dados Básicos -->
    <div class="row q-gutter-md">
      <q-select
        v-model="localForm.ID_ANIMAL"
        :options="animalOptions"
        label="Animal *"
        use-input
        @filter="filterAnimais"
        class="col-5"
        :rules="[val => !!val || 'Selecione um animal']"
        :disable="readonly"
      />
      <calendario-component
        v-model="localForm.DATA_MEDICAO"
        label="Data da Medição *"
        class="col-3"
        :rules="[val => !!val || 'Data é obrigatória']"
        :readonly="readonly"
      />
      <q-input
        v-if="localForm.dias_desde_ultima"
        :model-value="`${localForm.dias_desde_ultima} dias`"
        label="Desde última medição"
        readonly
        class="col-3"
        hint="Intervalo calculado automaticamente"
      />
    </div>

    <!-- Medidas Principais -->
    <q-separator class="q-my-md" />
    <div class="text-subtitle1 q-mb-md">Medidas Principais</div>
    
    <div class="row q-gutter-md">
      <q-input
        v-model.number="localForm.PESO"
        label="Peso"
        type="number"
        step="0.1"
        suffix="kg"
        class="col-3"
        :rules="pesoRules"
        :readonly="readonly"
        hint="Peso em quilogramas"
      />
      <q-input
        v-model.number="localForm.ALTURA"
        label="Altura"
        type="number"
        step="0.1"
        suffix="cm"
        class="col-3"
        :rules="alturaRules"
        :readonly="readonly"
        hint="Altura na cernelha"
      />
      
      <!-- Indicadores de Variação -->
      <div v-if="variacao.peso" class="col-3">
        <q-card flat bordered>
          <q-card-section class="text-center q-pa-sm">
            <div class="text-caption">Variação de Peso</div>
            <div :class="variacao.peso > 0 ? 'text-positive' : 'text-negative'" class="text-h6">
              {{ variacao.peso > 0 ? '+' : '' }}{{ variacao.peso.toFixed(1) }} kg
            </div>
          </q-card-section>
        </q-card>
      </div>
      
      <div v-if="variacao.altura" class="col-3">
        <q-card flat bordered>
          <q-card-section class="text-center q-pa-sm">
            <div class="text-caption">Variação de Altura</div>
            <div :class="variacao.altura > 0 ? 'text-positive' : 'text-negative'" class="text-h6">
              {{ variacao.altura > 0 ? '+' : '' }}{{ variacao.altura.toFixed(1) }} cm
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Medidas Complementares -->
    <q-separator class="q-my-md" />
    <div class="text-subtitle1 q-mb-md">
      Medidas Complementares
      <q-btn 
        flat 
        size="sm" 
        :icon="mostrarComplementares ? 'expand_less' : 'expand_more'"
        @click="mostrarComplementares = !mostrarComplementares"
        class="q-ml-sm"
      />
    </div>
    
    <q-slide-transition>
      <div v-show="mostrarComplementares" class="row q-gutter-md">
        <q-input
          v-model.number="localForm.CIRCUNFERENCIA_CANELA"
          label="Circunferência da Canela"
          type="number"
          step="0.1"
          suffix="cm"
          class="col-4"
          :rules="canelaRules"
          :readonly="readonly"
          hint="Medida na canela"
        />
        <q-input
          v-model.number="localForm.CIRCUNFERENCIA_TORACICA"
          label="Circunferência Torácica"
          type="number"
          step="0.1"
          suffix="cm"
          class="col-4"
          :rules="toracicaRules"
          :readonly="readonly"
          hint="Contorno do tórax"
        />
        <q-input
          v-model.number="localForm.COMPRIMENTO_CORPO"
          label="Comprimento do Corpo"
          type="number"
          step="0.1"
          suffix="cm"
          class="col-4"
          :rules="corpoRules"
          :readonly="readonly"
          hint="Da ponta do ombro à ponta da nádega"
        />
      </div>
    </q-slide-transition>

    <!-- Observações -->
    <div class="row q-mt-md">
      <q-input
        v-model="localForm.OBSERVACOES"
        label="Observações"
        type="textarea"
        rows="3"
        class="col"
        :readonly="readonly"
        hint="Observações sobre a medição, comportamento, condições, etc."
      />
    </div>

    <!-- Validações e Alertas -->
    <div v-if="validacoes.length > 0" class="q-mt-md">
      <q-banner 
        v-for="validacao in validacoes" 
        :key="validacao.tipo"
        :class="validacao.cor"
        class="q-mb-sm"
      >
        <template v-slot:avatar>
          <q-icon :name="validacao.icone" />
        </template>
        {{ validacao.mensagem }}
      </q-banner>
    </div>

    <!-- Resumo das Medidas -->
    <div v-if="resumoMedidas.length > 0 && !readonly" class="q-mt-md">
      <q-card flat bordered>
        <q-card-section>
          <div class="text-subtitle2 q-mb-sm">Resumo das Medidas</div>
          <div class="row q-gutter-sm">
            <q-chip 
              v-for="medida in resumoMedidas" 
              :key="medida.nome"
              :color="medida.cor"
              text-color="white"
              size="sm"
            >
              {{ medida.nome }}: {{ medida.valor }}
            </q-chip>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useCrescimentoStore } from '../stores/crescimento'
import CalendarioComponent from './CalendarioComponent.vue'

const crescimentoStore = useCrescimentoStore()

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  animalOptions: {
    type: Array,
    default: () => []
  },
  readonly: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:modelValue'])

// Estado local
const localForm = ref({ ...props.modelValue })
const mostrarComplementares = ref(false)
const animalOptionsFiltrados = ref([...props.animalOptions])

// Computed
const variacao = computed(() => {
  const variacao = { peso: null, altura: null }
  
  // Aqui seria calculado baseado na última medição do animal
  // Por simplicidade, usando valores mockados se existirem
  if (localForm.value.ganho_peso) {
    variacao.peso = localForm.value.ganho_peso
  }
  
  return variacao
})

const validacoes = computed(() => {
  const alertas = []
  
  // Validar faixas de peso
  if (localForm.value.PESO) {
    if (localForm.value.PESO < 100) {
      alertas.push({
        tipo: 'peso_baixo',
        mensagem: 'Peso muito baixo para um equino adulto',
        cor: 'bg-warning text-dark',
        icone: 'warning'
      })
    } else if (localForm.value.PESO > 800) {
      alertas.push({
        tipo: 'peso_alto',
        mensagem: 'Peso muito alto - verificar se está correto',
        cor: 'bg-warning text-dark',
        icone: 'warning'
      })
    }
  }
  
  // Validar faixas de altura
  if (localForm.value.ALTURA) {
    if (localForm.value.ALTURA < 120) {
      alertas.push({
        tipo: 'altura_baixa',
        mensagem: 'Altura baixa para um equino adulto',
        cor: 'bg-info text-white',
        icone: 'info'
      })
    } else if (localForm.value.ALTURA > 190) {
      alertas.push({
        tipo: 'altura_alta',
        mensagem: 'Altura acima da média - animal de grande porte',
        cor: 'bg-info text-white',
        icone: 'info'
      })
    }
  }
  
  return alertas
})

const resumoMedidas = computed(() => {
  const medidas = []
  
  if (localForm.value.PESO) {
    const classificacao = crescimentoStore.compararComMedia(localForm.value.PESO, 'peso')
    medidas.push({
      nome: 'Peso',
      valor: `${localForm.value.PESO} kg`,
      cor: crescimentoStore.getClassificacaoColor(classificacao)
    })
  }
  
  if (localForm.value.ALTURA) {
    const classificacao = crescimentoStore.compararComMedia(localForm.value.ALTURA, 'altura')
    medidas.push({
      nome: 'Altura',
      valor: `${localForm.value.ALTURA} cm`,
      cor: crescimentoStore.getClassificacaoColor(classificacao)
    })
  }
  
  return medidas
})

// Regras de validação
const pesoRules = [
  val => !val || (val > 0 && val <= 2000) || 'Peso deve estar entre 0 e 2000 kg'
]

const alturaRules = [
  val => !val || (val > 0 && val <= 300) || 'Altura deve estar entre 0 e 300 cm'
]

const canelaRules = [
  val => !val || (val > 0 && val <= 100) || 'Circunferência deve estar entre 0 e 100 cm'
]

const toracicaRules = [
  val => !val || (val > 0 && val <= 500) || 'Circunferência deve estar entre 0 e 500 cm'
]

const corpoRules = [
  val => !val || (val > 0 && val <= 500) || 'Comprimento deve estar entre 0 e 500 cm'
]

// Funções
function filterAnimais(val, update) {
  update(() => {
    if (val === '') {
      animalOptionsFiltrados.value = [...props.animalOptions]
    } else {
      const needle = val.toLowerCase()
      animalOptionsFiltrados.value = props.animalOptions.filter(
        v => v.label.toLowerCase().indexOf(needle) > -1
      )
    }
  })
}

// Watchers
watch(localForm, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })

watch(() => props.modelValue, (newVal) => {
  // Evitar loop infinito - só atualizar se realmente mudou
  if (JSON.stringify(newVal) !== JSON.stringify(localForm.value)) {
    localForm.value = { ...newVal }
  }
}, { deep: true })

// Mostrar medidas complementares automaticamente se já estiverem preenchidas
watch(localForm, (newVal) => {
  if (newVal.CIRCUNFERENCIA_CANELA || newVal.CIRCUNFERENCIA_TORACICA || newVal.COMPRIMENTO_CORPO) {
    mostrarComplementares.value = true
  }
}, { immediate: true })
</script>

<style scoped>
.crescimento-form {
  max-width: 100%;
}

.q-chip {
  margin: 2px;
}
</style>