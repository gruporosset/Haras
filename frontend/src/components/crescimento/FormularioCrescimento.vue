<template>
  <q-dialog v-model="dialogModel" persistent>
    <q-card style="width: 700px; max-width: 90vw">
      <q-card-section>
        <div class="text-h6">
          {{ editando ? 'Editar' : 'Nova' }} Medição de Crescimento
        </div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-form ref="formRef" @submit="salvarMedicao">
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
              v-model="form.DATA_MEDICAO"
              label="Data da Medição *"
              class="col-3"
              :rules="[val => !!val || 'Data é obrigatória']"
            />
            <q-input
              v-if="form.dias_desde_ultima"
              :model-value="`${form.dias_desde_ultima} dias`"
              label="Desde última medição"
              readonly
              class="col-3"
              hint="Calculado automaticamente"
            />
          </div>

          <!-- Medidas Principais -->
          <q-separator class="q-my-md" />
          <div class="text-subtitle1 q-mb-md">Medidas Principais</div>
          
          <div class="row q-gutter-md">
            <q-input
              v-model.number="form.PESO"
              label="Peso"
              type="number"
              step="0.1"
              suffix="kg"
              class="col-3"
              :rules="[
                val => val === null || val === undefined || val >= 0 || 'Peso deve ser positivo'
              ]"
              hint="Peso em quilogramas"
            />
            <q-input
              v-model.number="form.ALTURA"
              label="Altura"
              type="number"
              step="0.1"
              suffix="cm"
              class="col-3"
              :rules="[
                val => val === null || val === undefined || val >= 0 || 'Altura deve ser positiva'
              ]"
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
                v-model.number="form.CIRCUNFERENCIA_TORACICA"
                label="Circunferência Torácica"
                type="number"
                step="0.1"
                suffix="cm"
                class="col-md-4 col-6"
                hint="Medida atrás da cernelha"
              />
              <q-input
                v-model.number="form.COMPRIMENTO_CORPO"
                label="Comprimento do Corpo"
                type="number"
                step="0.1"
                suffix="cm"
                class="col-md-4 col-6"
                hint="Da ponta do ombro à ponta da nádega"
              />
              <q-input
                v-model.number="form.CIRCUNFERENCIA_CANELA"
                label="Circunferência da Canela"
                type="number"
                step="0.1"
                suffix="cm"
                class="col-md-4 col-6"
                hint="Parte mais fina da canela"
              />
              <q-input
                v-model.number="form.ALTURA_ANTERIOR"
                label="Altura Anterior"
                type="number"
                step="0.1"
                suffix="cm"
                class="col-md-4 col-6"
                hint="Altura dos membros anteriores"
              />
              <q-input
                v-model.number="form.ALTURA_POSTERIOR"
                label="Altura Posterior"
                type="number"
                step="0.1"
                suffix="cm"
                class="col-md-4 col-6"
                hint="Altura dos membros posteriores"
              />
              <q-input
                v-model.number="form.LARGURA_PEITO"
                label="Largura do Peito"
                type="number"
                step="0.1"
                suffix="cm"
                class="col-md-4 col-6"
                hint="Largura entre os membros anteriores"
              />
            </div>
          </q-slide-transition>

          <!-- Observações -->
          <q-separator class="q-my-md" />
          <q-input
            v-model="form.OBSERVACOES"
            label="Observações"
            type="textarea"
            rows="3"
            class="full-width"
            hint="Informações adicionais sobre a medição"
          />
        </q-form>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancelar" color="grey" @click="cancelar" />
        <q-btn 
          label="Salvar" 
          color="primary" 
          @click="salvarMedicao"
          :loading="crescimentoStore.loading"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useCrescimentoStore } from 'stores/crescimento'
import { useAnimalStore } from 'stores/animal'
import { useAuthStore } from 'stores/auth'
import { ErrorHandler } from 'src/utils/errorHandler'
import { prepareFormData } from 'src/utils/dateUtils'
import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

// Props
defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'saved'])

// Stores
const crescimentoStore = useCrescimentoStore()
const animalStore = useAnimalStore()
const authStore = useAuthStore()

// Estado reativo
const dialog = ref(false)
const formRef = ref(null)
const editando = ref(false)
const mostrarComplementares = ref(false)
const ultimaMedicao = ref(null)

// Opções
const animalOri = ref([])
const animalOptions = ref([])

// Formulário
const form = ref({})

// Computed
const dialogModel = computed({
  get: () => dialog.value,
  set: (val) => {
    dialog.value = val
    emit('update:modelValue', val)
  }
})

const variacao = computed(() => {
  if (!ultimaMedicao.value) return { peso: null, altura: null }
  
  return {
    peso: form.value.PESO && ultimaMedicao.value.PESO ? 
          form.value.PESO - ultimaMedicao.value.PESO : null,
    altura: form.value.ALTURA && ultimaMedicao.value.ALTURA ? 
            form.value.ALTURA - ultimaMedicao.value.ALTURA : null
  }
})

// Watchers
watch(() => form.value.ID_ANIMAL, async (novoAnimal) => {
  if (novoAnimal) {
    await carregarUltimaMedicao(novoAnimal)
  }
})

// Métodos
async function loadAnimais() {
  try {
    await animalStore.fetchAnimais({ limit: 100 })
    animalOri.value = animalStore.animais.map(a => ({
      value: a.ID,
      label: a.NOME
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

async function carregarUltimaMedicao(animalId) {
  try {
    ultimaMedicao.value = await crescimentoStore.getUltimaMedicao(animalId)
  } catch {
    ultimaMedicao.value = null
  }
}

async function salvarMedicao() {
  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    const dateFields = ['DATA_MEDICAO']
    const formData = prepareFormData(form.value, dateFields)
    
    if (editando.value) {
      await crescimentoStore.updateCrescimento(formData.ID, formData)
      ErrorHandler.success('Medição atualizada com sucesso!')
    } else {
      await crescimentoStore.createCrescimento(formData)
      ErrorHandler.success('Medição registrada com sucesso!')
    }
    
    emit('saved')
    fecharDialog()
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao salvar medição')
  }
}

function openDialog(medicao = null) {
  if (medicao) {
    editando.value = true
    form.value = { 
      ...medicao,
      ID_USUARIO_CADASTRO: authStore.user.ID
    }
    mostrarComplementares.value = !!(
      medicao.CIRCUNFERENCIA_TORACICA ||
      medicao.COMPRIMENTO_CORPO ||
      medicao.CIRCUNFERENCIA_CANELA ||
      medicao.ALTURA_ANTERIOR ||
      medicao.ALTURA_POSTERIOR ||
      medicao.LARGURA_PEITO
    )
  } else {
    editando.value = false
    form.value = {
      ID: null,
      ID_ANIMAL: null,
      DATA_MEDICAO: new Date().toISOString().slice(0, 10),
      PESO: null,
      ALTURA: null,
      CIRCUNFERENCIA_TORACICA: null,
      COMPRIMENTO_CORPO: null,
      CIRCUNFERENCIA_CANELA: null,
      ALTURA_ANTERIOR: null,
      ALTURA_POSTERIOR: null,
      LARGURA_PEITO: null,
      OBSERVACOES: '',
      ID_USUARIO_CADASTRO: authStore.user.ID
    }
    mostrarComplementares.value = false
  }
  
  loadAnimais()
  dialog.value = true
}

function fecharDialog() {
  dialog.value = false
  form.value = {}
  editando.value = false
  ultimaMedicao.value = null
  mostrarComplementares.value = false
}

function cancelar() {
  fecharDialog()
}

// Expor métodos
defineExpose({
  openDialog
})
</script>