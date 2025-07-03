<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md text-primary">
      <q-icon name="pets" class="q-mr-sm" />
      Gestão dos Animais
    </div>

    <!-- Lista de Animais -->
    <ListaAnimais 
      @novo-animal="abrirCadastro()"
      @visualizar="abrirDetalhes"
      @editar="abrirEdicao"
      @excluir="confirmarExclusao"
      @upload-foto="abrirUploadFoto"
      @ver-foto="abrirVisualizacaoFoto"
      @ver-genealogia="abrirGenealogia"
      ref="listaAnimaisRef"
    />

    <!-- Componente de Cadastro -->
    <CadastroAnimais 
      v-model="cadastroDialog"
      @saved="onAnimalSaved"
      ref="cadastroRef"
    />

    <!-- Componente de Detalhes -->
    <DetalhesAnimal 
      @refresh="refreshAnimais"
      ref="detalhesRef"
    />

    <!-- Confirmação de Exclusão -->
    <ConfirmacaoExclusao 
      v-model="deleteDialog"
      mensagem="Deseja excluir este animal?"
      :item-selecionado="animalToDelete"
      :loading="animalStore.loading"
      @confirmar="excluirAnimal"
    />
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAnimalStore } from 'stores/animal'
import { ErrorHandler } from 'src/utils/errorHandler'

// Componentes
import ListaAnimais from 'components/animais/ListaAnimais.vue'
import CadastroAnimais from 'components/animais/CadastroAnimais.vue'
import DetalhesAnimal from 'components/animais/DetalhesAnimal.vue'
import ConfirmacaoExclusao from 'components/widgets/ConfirmacaoExclusao.vue'

// Store
const animalStore = useAnimalStore()

// Refs dos componentes
const listaAnimaisRef = ref(null)
const cadastroRef = ref(null)
const detalhesRef = ref(null)

// Estado reativo
const cadastroDialog = ref(false)
const deleteDialog = ref(false)
const animalToDelete = ref(null)

// Métodos de abertura de dialogs
function abrirCadastro() {
  cadastroRef.value?.openDialog()
}

function abrirEdicao(animal) {
  cadastroRef.value?.openDialog(animal)
}

function abrirDetalhes(animal) {
  detalhesRef.value?.openViewDialog(animal)
}

function abrirUploadFoto(animal) {
  detalhesRef.value?.openFotoDialog(animal)
}

function abrirVisualizacaoFoto(animal) {
  detalhesRef.value?.openFotoViewDialog(animal)
}

function abrirGenealogia(animal) {
  detalhesRef.value?.openViewGenealogia(animal)
}

// Métodos de ação
function confirmarExclusao(animal) {
  animalToDelete.value = animal
  deleteDialog.value = true
}

async function excluirAnimal() {
  try {
    await animalStore.deleteAnimal(animalToDelete.value.ID)
    ErrorHandler.success('Animal excluído com sucesso!')
    deleteDialog.value = false
    refreshAnimais()
  } catch (error) {
    ErrorHandler.handle(error, 'Erro ao excluir animal')
  }
}

function onAnimalSaved() {
  refreshAnimais()
}

function refreshAnimais() {
  listaAnimaisRef.value?.fetchAnimais()
}

// Lifecycle
onMounted(() => {
  refreshAnimais()
})
</script>