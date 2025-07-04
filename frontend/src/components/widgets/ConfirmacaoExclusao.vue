<template>
  <q-dialog
    v-model="dialogModel"
    persistent
  >
    <q-card style="min-width: 400px">
      <q-card-section class="row items-center">
        <q-avatar
          icon="warning"
          color="negative"
          text-color="white"
        />
        <span class="q-ml-sm text-h6">Confirmar Exclusão</span>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <div class="text-body1">
          {{ mensagem }}
        </div>
        <div
          v-if="itemSelecionado"
          class="text-weight-bold q-mt-sm"
        >
          {{
            itemSelecionado.NOME || itemSelecionado.nome || 'Item selecionado'
          }}
        </div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn
          flat
          label="Cancelar"
          color="grey"
          @click="cancelar"
        />
        <q-btn
          label="Excluir"
          color="negative"
          @click="confirmar"
          :loading="loading"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
  import { computed } from 'vue'

  // Props
  const props = defineProps({
    modelValue: {
      type: Boolean,
      default: false,
    },
    mensagem: {
      type: String,
      default: 'Deseja realmente excluir este item?',
    },
    itemSelecionado: {
      type: Object,
      default: null,
    },
    loading: {
      type: Boolean,
      default: false,
    },
  })

  // Emits
  const emit = defineEmits(['update:modelValue', 'confirmar', 'cancelar'])

  // Computed
  const dialogModel = computed({
    get: () => props.modelValue,
    set: val => emit('update:modelValue', val),
  })

  // Métodos
  function confirmar() {
    emit('confirmar')
  }

  function cancelar() {
    emit('cancelar')
    emit('update:modelValue', false)
  }
</script>
