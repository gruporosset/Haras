<template>
  <q-card>
    <q-card-section>
      <div class="text-h6">Aplicação Rápida</div>
      <div class="text-caption">
        Para registros simples de ferrageamento/casqueamento
      </div>
    </q-card-section>

    <q-card-section>
      <q-form
        @submit="aplicarRapido"
        class="q-gutter-md"
      >
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
          <q-btn
            type="submit"
            color="primary"
            :loading="loadingAplicacao"
          >
            Registrar Aplicação
          </q-btn>
        </div>
      </q-form>
    </q-card-section>
  </q-card>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useFerrageamentoStore } from 'stores/ferrageamento'
  import { useAnimalStore } from 'stores/animal'
  import { ErrorHandler } from 'src/utils/errorHandler'

  // Emits
  const emit = defineEmits(['aplicacao-registrada'])

  // Stores
  const ferrageamentoStore = useFerrageamentoStore()
  const animalStore = useAnimalStore()

  // Estado reativo
  const loadingAplicacao = ref(false)
  const animalOptions = ref([])

  // Formulário de aplicação rápida
  const aplicacaoRapida = ref({
    ID_ANIMAL: null,
    TIPO_REGISTRO: 'FERRAGEAMENTO',
    MEMBRO_TRATADO: 'TODOS',
    FERRADOR_RESPONSAVEL: '',
    STATUS_CASCO: 'BOM',
    CUSTO: null,
    OBSERVACOES: '',
  })

  // Métodos
  async function loadAnimais() {
    try {
      await animalStore.fetchAnimais()
      animalOptions.value = animalStore.animais.map(a => ({
        value: a.ID,
        label: a.NOME,
      }))
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar animais')
    }
  }

  function filterAnimais(val, update) {
    update(() => {
      if (val === '') {
        animalOptions.value = animalStore.animais.map(a => ({
          value: a.ID,
          label: a.NOME,
        }))
      } else {
        const needle = val.toLowerCase()
        const allAnimais = animalStore.animais.map(a => ({
          value: a.ID,
          label: a.NOME,
        }))
        animalOptions.value = allAnimais.filter(
          v => v.label.toLowerCase().indexOf(needle) > -1
        )
      }
    })
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
        OBSERVACOES: '',
      }

      emit('aplicacao-registrada')
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao registrar aplicação')
    } finally {
      loadingAplicacao.value = false
    }
  }

  // Lifecycle
  onMounted(() => {
    loadAnimais()
  })
</script>
