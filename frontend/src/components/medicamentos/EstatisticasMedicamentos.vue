<template>
  <div>
    <!-- Alertas de Estoque -->
    <div
      v-if="medicamentoStore.alertasEstoque.length > 0"
      class="q-mb-md"
    >
      <q-banner
        class="bg-warning text-dark"
        inline-actions
      >
        <template v-slot:avatar>
          <q-icon name="warning" />
        </template>
        {{ medicamentoStore.alertasEstoque.length }} medicamento(s) com alerta
        de estoque!
        <template v-slot:action>
          <q-btn
            flat
            label="Ver Alertas"
            @click="$emit('ir-para-alertas')"
          />
        </template>
      </q-banner>
    </div>

    <!-- Estatísticas Rápidas -->
    <div class="row q-gutter-md q-mb-md">
      <q-card
        flat
        bordered
        class="col"
      >
        <q-card-section class="text-center">
          <div class="text-h4 text-primary">
            {{ estatisticas.totalMedicamentos }}
          </div>
          <div class="text-caption">Total Medicamentos</div>
        </q-card-section>
      </q-card>

      <q-card
        flat
        bordered
        class="col"
      >
        <q-card-section class="text-center">
          <div class="text-h4 text-positive">{{ estatisticas.comEstoque }}</div>
          <div class="text-caption">Com Estoque</div>
        </q-card-section>
      </q-card>

      <q-card
        flat
        bordered
        class="col"
      >
        <q-card-section class="text-center">
          <div class="text-h4 text-warning">{{ estatisticas.alertas }}</div>
          <div class="text-caption">Alertas</div>
        </q-card-section>
      </q-card>

      <q-card
        flat
        bordered
        class="col"
      >
        <q-card-section class="text-center">
          <div class="text-h4 text-accent">
            R$ {{ estatisticas.valorTotal.toFixed(2) }}
          </div>
          <div class="text-caption">Valor Estoque</div>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup>
  import { computed } from 'vue'
  import { useMedicamentoStore } from 'stores/medicamento'

  // Emits
  defineEmits(['ir-para-alertas'])

  // Store
  const medicamentoStore = useMedicamentoStore()

  // Computed
  const estatisticas = computed(() => {
    return (
      medicamentoStore.estatisticasGerais || {
        totalMedicamentos: 0,
        comEstoque: 0,
        alertas: 0,
        valorTotal: 0,
      }
    )
  })
</script>
