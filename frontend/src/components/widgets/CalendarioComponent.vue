<template>
  <q-input
    :model-value="displayValue"
    @update:model-value="onInputChange"
    :label="label"
    :placeholder="placeholder"
    :rules="rules"
    :disable="disable"
    :mask="inputMask"
    fill-mask
    filled
    v-bind="$attrs"
  >
    <template v-slot:prepend>
      <q-icon
        name="event"
        class="cursor-pointer"
      >
        <q-popup-proxy
          cover
          transition-show="scale"
          transition-hide="scale"
        >
          <q-date
            :model-value="modelValue"
            @update:model-value="onDateChange"
            :mask="mask"
            today-btn
            minimal
          >
            <div class="row items-center justify-end">
              <q-btn
                v-close-popup
                label="Fechar"
                color="primary"
                flat
              />
            </div>
          </q-date>
        </q-popup-proxy>
      </q-icon>
    </template>

    <template
      v-slot:append
      v-if="withTime"
    >
      <q-icon
        name="access_time"
        class="cursor-pointer"
      >
        <q-popup-proxy
          cover
          transition-show="scale"
          transition-hide="scale"
        >
          <q-time
            :model-value="timeValue"
            @update:model-value="onTimeChange"
            format24h
            with-seconds
          >
            <div class="row items-center justify-end">
              <q-btn
                v-close-popup
                label="Fechar"
                color="primary"
                flat
              />
            </div>
          </q-time>
        </q-popup-proxy>
      </q-icon>
    </template>

    <template
      v-slot:after
      v-if="clearable && modelValue"
    >
      <q-btn
        round
        dense
        flat
        icon="clear"
        @click="clearValue"
        size="sm"
      />
    </template>
  </q-input>
</template>

<script setup>
  import { computed } from 'vue'

  const props = defineProps({
    modelValue: {
      type: String,
      default: '',
    },
    label: {
      type: String,
      default: 'Data',
    },
    placeholder: {
      type: String,
      default: 'Selecione uma data',
    },
    withTime: {
      type: Boolean,
      default: false,
    },
    rules: {
      type: Array,
      default: () => [],
    },
    readonly: {
      type: Boolean,
      default: false,
    },
    disable: {
      type: Boolean,
      default: false,
    },
    clearable: {
      type: Boolean,
      default: true,
    },
    format: {
      type: String,
      default: 'DD/MM/YYYY',
    },
  })

  const emit = defineEmits(['update:modelValue'])

  // Máscara baseada no formato
  const mask = computed(() => {
    if (props.withTime) {
      return 'YYYY-MM-DD HH:mm:ss'
    }
    return 'YYYY-MM-DD'
  })

  // Valor de exibição formatado
  const displayValue = computed(() => {
    if (!props.modelValue) return ''
    try {
      const date = new Date(props.modelValue + 'T00:00:00')
      if (isNaN(date.getTime())) return props.modelValue

      if (props.withTime) {
        return date.toLocaleString('pt-BR', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })
      } else {
        return date.toLocaleDateString('pt-BR')
      }
    } catch {
      return props.modelValue
    }
  })

  // Valor do tempo separado
  const timeValue = computed(() => {
    if (!props.modelValue || !props.withTime) return ''

    try {
      const date = new Date(props.modelValue)
      if (isNaN(date.getTime())) return ''

      return date.toTimeString().slice(0, 8)
    } catch {
      return ''
    }
  })

  // Máscara para digitação
  const inputMask = computed(() => {
    return props.withTime ? '##/##/#### ##:##' : '##/##/####'
  })

  function onDateChange(newDate) {
    if (!newDate) {
      emit('update:modelValue', '')
      return
    }

    // Corrigir timezone - forçar data local
    const correctedDate = new Date(newDate + 'T00:00:00')
    // const correctedDate = new Date(localDate.getTime() - (localDate.getTimezoneOffset() * 60000))

    if (props.withTime && props.modelValue) {
      // Manter horário existente
      try {
        const existingDate = new Date(props.modelValue)
        if (!isNaN(existingDate.getTime())) {
          correctedDate.setHours(existingDate.getHours())
          correctedDate.setMinutes(existingDate.getMinutes())
          correctedDate.setSeconds(existingDate.getSeconds())
        }
        emit('update:modelValue', correctedDate.toISOString().slice(0, 19))
      } catch {
        emit('update:modelValue', newDate + 'T00:00:00')
      }
    } else if (props.withTime) {
      emit('update:modelValue', newDate + 'T00:00:00')
    } else {
      emit('update:modelValue', newDate)
    }
  }

  function onTimeChange(newTime) {
    if (!newTime) return

    let dateToUse = props.modelValue
    if (!dateToUse) {
      dateToUse = new Date().toISOString().slice(0, 10)
    }

    try {
      const date = new Date(dateToUse)
      const [hours, minutes, seconds] = newTime.split(':')

      date.setHours(parseInt(hours))
      date.setMinutes(parseInt(minutes))
      date.setSeconds(parseInt(seconds || 0))

      emit('update:modelValue', date.toISOString().slice(0, 19))
    } catch {
      emit('update:modelValue', dateToUse.slice(0, 10) + 'T' + newTime)
    }
  }

  // Função para tratar digitação direta
  function onInputChange(value) {
    if (!value) {
      emit('update:modelValue', '')
      return
    }

    // Converter formato brasileiro para ISO
    try {
      let isoDate = ''

      if (props.withTime) {
        // Formato: 31/05/2025 14:30
        const [datePart, timePart] = value.split(' ')
        const [day, month, year] = datePart.split('/')
        const time = timePart || '00:00'
        isoDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}T${time}:00`
      } else {
        // Formato: 31/05/2025
        const [day, month, year] = value.split('/')
        isoDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
      }

      // Validar data
      const date = new Date(isoDate)
      if (!isNaN(date.getTime())) {
        emit('update:modelValue', isoDate)
      }
    } catch {
      // Se não conseguir converter, manter valor original
      emit('update:modelValue', value)
    }
  }

  function clearValue() {
    emit('update:modelValue', '')
  }
</script>

<style scoped>
  .cursor-pointer {
    cursor: pointer;
  }
</style>
