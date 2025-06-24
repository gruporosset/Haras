<template>
  <div class="calendario-container">
    <!-- Header do Calendário -->
    <div class="calendar-header q-mb-md">
      <q-btn flat round icon="chevron_left" @click="mesAnterior" />
      <div class="text-h6 flex-1 text-center">
        {{ mesAtualFormatado }}
      </div>
      <q-btn flat round icon="chevron_right" @click="proximoMes" />
    </div>

    <!-- Grid do Calendário -->
    <div class="calendar-grid">
      <!-- Cabeçalho dos dias da semana -->
      <div class="calendar-header-days">
        <div v-for="dia in diasSemana" :key="dia" class="day-header">
          {{ dia }}
        </div>
      </div>

      <!-- Dias do mês -->
      <div class="calendar-body">
        <div
          v-for="dia in diasMes"
          :key="dia.data"
          :class="['calendar-day', {
            'day-other-month': !dia.mesAtual,
            'day-today': dia.hoje,
            'day-has-events': dia.eventos.length > 0
          }]"
          @click="selecionarDia(dia)"
        >
          <div class="day-number">{{ dia.numero }}</div>
          
          <!-- Eventos do dia -->
          <div class="day-events" v-if="dia.eventos.length > 0">
            <div
              v-for="evento in dia.eventos.slice(0, 3)"
              :key="evento.id"
              :class="['event-item', `event-${evento.tipo.toLowerCase()}`]"
              :title="evento.descricao"
            >
              <div class="event-dot"></div>
              <div class="event-text">{{ evento.animal_nome }}</div>
            </div>
            
            <!-- Indicador de mais eventos -->
            <div v-if="dia.eventos.length > 3" class="more-events">
              +{{ dia.eventos.length - 3 }} mais
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Legenda -->
    <div class="calendar-legend q-mt-md">
      <div class="legend-title text-subtitle2 q-mb-sm">Legenda:</div>
      <div class="legend-items">
        <div class="legend-item">
          <div class="legend-dot event-vacina"></div>
          <span>Vacinas</span>
        </div>
        <div class="legend-item">
          <div class="legend-dot event-vermifugo"></div>
          <span>Vermífugos</span>
        </div>
        <div class="legend-item">
          <div class="legend-dot event-medicamento"></div>
          <span>Medicamentos</span>
        </div>
        <div class="legend-item">
          <div class="legend-dot event-exame"></div>
          <span>Exames</span>
        </div>
        <div class="legend-item">
          <div class="legend-dot event-consulta"></div>
          <span>Consultas</span>
        </div>
        <div class="legend-item">
          <div class="legend-dot event-cirurgia"></div>
          <span>Cirurgias</span>
        </div>
      </div>
    </div>

    <!-- Modal de Detalhes do Dia -->
    <q-dialog v-model="modalDia" position="right">
      <q-card style="width: 400px; max-width: 80vw;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">{{ diaSelecionado?.dataFormatada }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <div v-if="diaSelecionado?.eventos.length > 0">
            <q-list bordered separator>
              <q-item v-for="evento in diaSelecionado.eventos" :key="evento.id">
                <q-item-section avatar>
                  <q-avatar
                    :color="getTipoColor(evento.tipo)"
                    text-color="white"
                    size="sm"
                  >
                    <q-icon :name="getTipoIcon(evento.tipo)" />
                  </q-avatar>
                </q-item-section>
                
                <q-item-section>
                  <q-item-label>{{ evento.animal_nome }}</q-item-label>
                  <q-item-label caption>{{ evento.descricao }}</q-item-label>
                  <q-item-label caption v-if="evento.veterinario">
                    Dr. {{ evento.veterinario }}
                  </q-item-label>
                </q-item-section>
                
                <q-item-section side>
                  <q-chip
                    :color="getTipoColor(evento.tipo)"
                    text-color="white"
                    :label="evento.tipo"
                    dense
                  />
                </q-item-section>
              </q-item>
            </q-list>
          </div>
          
          <div v-else class="text-center q-pa-lg text-grey-6">
            Nenhum evento agendado para este dia
          </div>
        </q-card-section>

        <q-card-actions align="right" v-if="diaSelecionado?.eventos.length > 0">
          <q-btn
            flat
            color="primary"
            label="Novo Registro"
            @click="novoRegistroDia"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useSaudeStore } from 'src/stores/saude'

export default {
  name: 'CalendarioSaude',
  
  emits: ['novo-registro', 'selecionar-evento'],
  
  setup(props, { emit }) {
    const saudeStore = useSaudeStore()
    
    // Refs
    const mesAtual = ref(new Date().getMonth())
    const anoAtual = ref(new Date().getFullYear())
    const eventos = ref([])
    const modalDia = ref(false)
    const diaSelecionado = ref(null)
    
    // Computed
    const mesAtualFormatado = computed(() => {
      const meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
      ]
      return `${meses[mesAtual.value]} ${anoAtual.value}`
    })
    
    const diasSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
    
    const diasMes = computed(() => {
      const primeiroDiaMes = new Date(anoAtual.value, mesAtual.value, 1)
      const ultimoDiaMes = new Date(anoAtual.value, mesAtual.value + 1, 0)
      const primeiroDiaCalendario = new Date(primeiroDiaMes)
      primeiroDiaCalendario.setDate(primeiroDiaCalendario.getDate() - primeiroDiaMes.getDay())
      
      const dias = []
      const hoje = new Date()
      
      // Calcular quantos dias mostrar (sempre mostrar semanas completas)
      const ultimoDiaCalendario = new Date(ultimoDiaMes)
      const diasRestantes = 6 - ultimoDiaMes.getDay()
      ultimoDiaCalendario.setDate(ultimoDiaMes.getDate() + diasRestantes)
      
      // Calcular diferença em dias entre primeiro e último dia do calendário
      const totalDias = Math.ceil((ultimoDiaCalendario - primeiroDiaCalendario) / (1000 * 60 * 60 * 24)) + 1
      
      for (let i = 0; i < totalDias; i++) {
        const data = new Date(primeiroDiaCalendario)
        data.setDate(primeiroDiaCalendario.getDate() + i)
        
        const dataString = data.toISOString().split('T')[0]
        const eventosdia = eventos.value.filter(evento => 
          evento.data_aplicacao.startsWith(dataString)
        )
        
        dias.push({
          data: dataString,
          numero: data.getDate(),
          mesAtual: data.getMonth() === mesAtual.value,
          hoje: data.toDateString() === hoje.toDateString(),
          eventos: eventosdia,
          dataFormatada: data.toLocaleDateString('pt-BR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })
        })
      }
      
      return dias
    })
    
    // Métodos
    const carregarEventos = async () => {
      try {
        const response = await saudeStore.calendarioSaude(mesAtual.value + 1, anoAtual.value)
        eventos.value = response.map(evento => ({
          id: evento.ID,
          animal_nome: evento.animal_nome,
          tipo: evento.TIPO_REGISTRO,
          descricao: evento.DESCRICAO || evento.MEDICAMENTO_APLICADO || evento.TIPO_REGISTRO,
          data_aplicacao: evento.PROXIMA_APLICACAO || evento.DATA_OCORRENCIA,
          veterinario: evento.VETERINARIO_RESPONSAVEL,
          prioridade: evento.prioridade || 'NORMAL'
        }))
      } catch (error) {
        console.error('Erro ao carregar eventos do calendário:', error)
      }
    }
    
    const mesAnterior = () => {
      if (mesAtual.value === 0) {
        mesAtual.value = 11
        anoAtual.value--
      } else {
        mesAtual.value--
      }
    }
    
    const proximoMes = () => {
      if (mesAtual.value === 11) {
        mesAtual.value = 0
        anoAtual.value++
      } else {
        mesAtual.value++
      }
    }
    
    const selecionarDia = (dia) => {
      diaSelecionado.value = dia
      modalDia.value = true
    }
    
    const novoRegistroDia = () => {
      modalDia.value = false
      emit('novo-registro', {
        data: diaSelecionado.value.data,
        animal_id: null
      })
    }
    
    const getTipoColor = (tipo) => {
      const cores = {
        'VACINA': 'green',
        'VERMIFUGO': 'orange',
        'MEDICAMENTO': 'blue',
        'EXAME': 'purple',
        'CONSULTA': 'teal',
        'CIRURGIA': 'red',
        'TRATAMENTO': 'indigo'
      }
      return cores[tipo] || 'grey'
    }
    
    const getTipoIcon = (tipo) => {
      const icons = {
        'VACINA': 'vaccines',
        'VERMIFUGO': 'pest_control',
        'MEDICAMENTO': 'medication',
        'EXAME': 'science',
        'CONSULTA': 'medical_services',
        'CIRURGIA': 'healing',
        'TRATAMENTO': 'local_hospital'
      }
      return icons[tipo] || 'event'
    }
    
    // Watchers
    watch([mesAtual, anoAtual], () => {
      carregarEventos()
    })
    
    // Lifecycle
    onMounted(() => {
      carregarEventos()
    })
    
    return {
      // Refs
      mesAtual,
      anoAtual,
      modalDia,
      diaSelecionado,
      
      // Computed
      mesAtualFormatado,
      diasSemana,
      diasMes,
      
      // Métodos
      mesAnterior,
      proximoMes,
      selecionarDia,
      novoRegistroDia,
      getTipoColor,
      getTipoIcon
    }
  }
}
</script>

<style>
@import 'src/css/components/calendario.css';
</style>