<template>
  <div class="map-container">
    <div v-if="!terrenos.length" class="text-center q-pa-md">
      Nenhum terreno encontrado para exibir no mapa.
    </div>
    <l-map
      v-else
      ref="map"
      :center="mapCenter"
      :zoom="zoom"
      style="height: 500px; width: 100%"
      aria-label="Mapa interativo de terrenos"
      @ready="onMapReady"
    >
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <l-marker
        v-for="terreno in terrenos"
        :key="terreno.ID"
        :lat-lng="[terreno.LATITUDE, terreno.LONGITUDE]"
        :aria-label="`Marcador do terreno ${terreno.NOME}`"
      >
        <l-popup>
          <div>
            <strong>{{ terreno.NOME }}</strong><br>
            Status: {{ terreno.STATUS_TERRENO }}<br>
            Área: {{ terreno.AREA_HECTARES }} ha
          </div>
        </l-popup>
      </l-marker>
    </l-map>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  LMap,
  LTileLayer,
  LMarker,
  LPopup
} from '@vue-leaflet/vue-leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  terrenos: {
    type: Array,
    required: true,
    default: () => []
  }
})

const zoom = ref(13)
const map = ref(null)

const mapCenter = computed(() => {
  if (!props.terrenos?.length) return [-15.0, -47.0] // Centro do Brasil
  const avgLat = props.terrenos.reduce((sum, t) => sum + t.LATITUDE, 0) / props.terrenos.length
  const avgLng = props.terrenos.reduce((sum, t) => sum + t.LONGITUDE, 0) / props.terrenos.length
  return [avgLat, avgLng]
})

function onMapReady() {
  // Ajustar acessibilidade
  const mapElement = map.value?.leafletObject?.getContainer()
  if (mapElement) {
    mapElement.setAttribute('role', 'region')
    mapElement.setAttribute('aria-describedby', 'map-description')
  }
}

// Corrigir ícones após montagem
onMounted(() => {
})
</script>

<style>
.map-container {
  position: relative;
  height: 500px;
  z-index: 0; /* Importante para o Quasar */
}

.leaflet-container {
  background: #f8f8f8;
}
</style>