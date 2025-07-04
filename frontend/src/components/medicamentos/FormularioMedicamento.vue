<template>
  <q-dialog
    v-model="dialog"
    persistent
  >
    <q-card style="width: 800px; max-width: 95vw">
      <q-card-section>
        <div class="text-h6">
          {{ editando ? 'Editar' : 'Cadastrar' }} Medicamento
        </div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-form
          @submit="salvarMedicamento"
          class="q-gutter-md"
        >
          <!-- Dados Básicos -->
          <div class="row q-gutter-md">
            <q-input
              v-model="form.NOME"
              label="Nome do Medicamento *"
              class="col-6"
              :rules="[val => !!val || 'Nome é obrigatório']"
            />
            <q-input
              v-model="form.PRINCIPIO_ATIVO"
              label="Princípio Ativo"
              class="col-6"
            />
          </div>

          <div class="row q-gutter-md">
            <q-input
              v-model="form.CONCENTRACAO"
              label="Concentração"
              class="col-4"
            />
            <q-select
              v-model="form.FORMA_FARMACEUTICA"
              :options="medicamentoStore.formasFarmaceuticas"
              label="Forma Farmacêutica *"
              class="col-4"
              :rules="[val => !!val || 'Forma Farmacêutica é obrigatória']"
            />
            <q-select
              v-model="form.UNIDADE_MEDIDA"
              :options="medicamentoStore.unidadesMedida"
              label="Unidade de Medida *"
              class="col-4"
              :rules="[val => !!val || 'Unidade é obrigatória']"
            />
          </div>

          <div class="row q-gutter-md">
            <q-input
              v-model="form.FABRICANTE"
              label="Fabricante"
              class="col-6"
            />
            <q-input
              v-model="form.REGISTRO_MAPA"
              label="Registro MAPA"
              class="col-6"
            />
          </div>

          <!-- Controle de Estoque -->
          <q-separator />
          <div class="text-subtitle2">Controle de Estoque</div>

          <div class="row q-gutter-md">
            <q-input
              v-model.number="form.ESTOQUE_MINIMO"
              label="Estoque Mínimo"
              type="number"
              step="0.1"
              class="col-4"
            />
            <q-input
              v-model.number="form.PRECO_UNITARIO"
              label="Preço Unitário *"
              type="number"
              step="0.01"
              prefix="R$"
              class="col-4"
              :rules="[val => !isNaN(parseFloat(val)) || 'Preço é obrigatório']"
            />
            <q-input
              v-model="form.FORNECEDOR"
              label="Fornecedor"
              class="col-4"
            />
          </div>

          <!-- Dados do Lote (se for entrada) -->
          <div
            v-if="!editando"
            class="row q-gutter-md"
          >
            <q-input
              v-model="form.LOTE_ATUAL"
              label="Lote"
              class="col-4"
            />
            <CalendarioComponent
              v-model="form.DATA_VALIDADE"
              label="Data de Validade"
              class="col-4"
            />
            <CalendarioComponent
              v-model="form.DATA_FABRICACAO"
              label="Data de Fabricação"
              class="col-4"
            />
          </div>

          <!-- Prescrição -->
          <q-separator />
          <div class="text-subtitle2">Prescrição</div>

          <div class="row q-gutter-md">
            <q-toggle
              v-model="form.REQUER_RECEITA"
              label="Requer Receita Veterinária"
              true-value="S"
              false-value="N"
              class="col-6"
            />
            <q-input
              v-model.number="form.PERIODO_CARENCIA"
              label="Período de Carência (dias)"
              type="number"
              class="col-6"
            />
          </div>

          <!-- Observações -->
          <q-input
            v-model="form.OBSERVACOES"
            label="Observações"
            type="textarea"
            rows="3"
          />

          <!-- Ações -->
          <div class="row q-gutter-md q-mt-md">
            <q-btn
              type="submit"
              color="primary"
              :loading="medicamentoStore.loading"
              :label="editando ? 'Salvar Alterações' : 'Cadastrar Medicamento'"
            />
            <q-btn
              flat
              label="Cancelar"
              color="grey"
              @click="fecharDialog"
            />
          </div>
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>
  import { ref, computed } from 'vue'
  import { useMedicamentoStore } from 'stores/medicamento'
  import { useAuthStore } from 'stores/auth'
  import { ErrorHandler } from 'src/utils/errorHandler'
  import CalendarioComponent from 'components/widgets/CalendarioComponent.vue'

  // Emits
  const emit = defineEmits(['saved'])

  // Stores
  const medicamentoStore = useMedicamentoStore()
  const authStore = useAuthStore()

  // Estado reativo
  const dialog = ref(false)
  const editando = ref(false)

  // Formulário
  const form = ref({
    ID: null,
    NOME: '',
    PRINCIPIO_ATIVO: '',
    CONCENTRACAO: '',
    FORMA_FARMACEUTICA: null,
    FABRICANTE: '',
    REGISTRO_MAPA: '',
    ESTOQUE_MINIMO: 0,
    UNIDADE_MEDIDA: null,
    LOTE_ATUAL: '',
    DATA_VALIDADE: '',
    DATA_FABRICACAO: '',
    PRECO_UNITARIO: 0,
    FORNECEDOR: '',
    REQUER_RECEITA: 'N',
    PERIODO_CARENCIA: null,
    OBSERVACOES: '',
    ATIVO: 'S',
    ID_USUARIO_CADASTRO: authStore.user?.ID,
  })

  // Computed
  const formDefault = computed(() => ({
    ID: null,
    NOME: '',
    PRINCIPIO_ATIVO: '',
    CONCENTRACAO: '',
    FORMA_FARMACEUTICA: null,
    FABRICANTE: '',
    REGISTRO_MAPA: '',
    ESTOQUE_MINIMO: 0,
    UNIDADE_MEDIDA: null,
    LOTE_ATUAL: '',
    DATA_VALIDADE: '',
    DATA_FABRICACAO: '',
    PRECO_UNITARIO: 0,
    FORNECEDOR: '',
    REQUER_RECEITA: 'N',
    PERIODO_CARENCIA: null,
    OBSERVACOES: '',
    ATIVO: 'S',
    ID_USUARIO_CADASTRO: authStore.user?.ID,
  }))

  // Métodos
  function openDialog(medicamento = null) {
    if (medicamento) {
      editando.value = true
      form.value = { ...medicamento }
    } else {
      editando.value = false
      form.value = { ...formDefault.value }
    }
    dialog.value = true
  }

  function fecharDialog() {
    dialog.value = false
    editando.value = false
    form.value = { ...formDefault.value }
  }

  async function salvarMedicamento() {
    try {
      if (editando.value) {
        await medicamentoStore.updateMedicamento(form.value.ID, form.value)
        ErrorHandler.success('Medicamento atualizado com sucesso!')
      } else {
        await medicamentoStore.createMedicamento(form.value)
        ErrorHandler.success('Medicamento cadastrado com sucesso!')
      }

      fecharDialog()
      emit('saved')
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao salvar medicamento')
    }
  }

  // Expor métodos
  defineExpose({
    openDialog,
  })
</script>
