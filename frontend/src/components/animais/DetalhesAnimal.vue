<template>
  <div>
    <!-- Modal de Visualização -->
    <q-dialog
      v-model="viewDialog"
      persistent
    >
      <q-card style="min-width: 600px">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Detalhes do Animal</div>
          <q-space />
          <q-btn
            icon="close"
            flat
            round
            dense
            @click="closeDialog"
          />
        </q-card-section>

        <q-card-section v-if="animalData">
          <q-list>
            <q-item>
              <q-item-section avatar>
                <q-avatar
                  v-if="animalData.FOTO_PRINCIPAL"
                  size="80px"
                >
                  <img
                    :src="`http://localhost:8000${animalData.FOTO_PRINCIPAL}`"
                  />
                </q-avatar>
                <q-icon
                  v-else
                  name="pets"
                  size="80px"
                  color="grey-5"
                />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-h6">
                  {{ animalData.NOME }}
                </q-item-label>
                <q-item-label caption>
                  {{ animalData.NUMERO_REGISTRO || 'Sem registro' }}
                </q-item-label>
                <q-item-label
                  v-if="animalData.CHIP_IDENTIFICACAO"
                  caption
                >
                  Chip: {{ animalData.CHIP_IDENTIFICACAO }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-separator />

            <q-item>
              <q-item-section>
                <q-item-label caption>Sexo</q-item-label>
                <q-item-label>
                  {{ animalData.SEXO === 'M' ? 'Macho' : 'Fêmea' }}
                </q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Status</q-item-label>
                <q-chip
                  :color="getStatusColor(animalData.STATUS_ANIMAL)"
                  text-color="white"
                  size="sm"
                >
                  {{ animalData.STATUS_ANIMAL }}
                </q-chip>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Data de Nascimento</q-item-label>
                <q-item-label>
                  {{
                    formatDate(animalData.DATA_NASCIMENTO) || 'Não informado'
                  }}
                </q-item-label>
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Pelagem</q-item-label>
                <q-item-label>
                  {{ animalData.PELAGEM || 'Não informado' }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="animalData.ORIGEM">
              <q-item-section>
                <q-item-label caption>Origem</q-item-label>
                <q-item-label>{{ animalData.ORIGEM }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="animalData.PESO_ATUAL">
              <q-item-section>
                <q-item-label caption>Peso Atual</q-item-label>
                <q-item-label>{{ animalData.PESO_ATUAL }} kg</q-item-label>
              </q-item-section>
            </q-item>

            <!-- Dados do Proprietário -->
            <q-separator class="q-my-md" />
            <q-item-label header>Proprietário</q-item-label>

            <q-item v-if="animalData.PROPRIETARIO">
              <q-item-section>
                <q-item-label caption>Nome</q-item-label>
                <q-item-label>{{ animalData.PROPRIETARIO }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="animalData.CONTATO_PROPRIETARIO">
              <q-item-section>
                <q-item-label caption>Contato</q-item-label>
                <q-item-label>
                  {{ animalData.CONTATO_PROPRIETARIO }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="animalData.CPF_CNPJ_PROPRIETARIO">
              <q-item-section>
                <q-item-label caption>CPF/CNPJ</q-item-label>
                <q-item-label>
                  {{ animalData.CPF_CNPJ_PROPRIETARIO }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="animalData.OBSERVACOES">
              <q-item-section>
                <q-item-label caption>Observações</q-item-label>
                <q-item-label>{{ animalData.OBSERVACOES }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Ver Genealogia"
            color="primary"
            @click="openGenealogia"
            :disable="!animalData?.ID_PAI && !animalData?.ID_MAE"
          />
          <q-btn
            flat
            label="Fechar"
            color="grey"
            @click="closeDialog"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Modal de Genealogia -->
    <q-dialog
      v-model="genealogiaDialog"
      persistent
    >
      <q-card style="min-width: 900px; max-width: 1200px">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Árvore Genealógica</div>
          <q-space />
          <q-btn
            icon="close"
            flat
            round
            dense
            @click="genealogiaDialog = false"
          />
        </q-card-section>

        <q-card-section v-if="genealogiaData">
          <div class="q-pa-md">
            <!-- Animal principal -->
            <div class="text-center q-mb-md">
              <q-card class="animal-card q-pa-md">
                <div class="row items-center justify-center">
                  <q-avatar
                    v-if="genealogiaData.animal.FOTO_PRINCIPAL"
                    size="80px"
                    class="q-mr-md"
                  >
                    <img
                      :src="`http://localhost:8000${genealogiaData.animal.FOTO_PRINCIPAL}`"
                    />
                  </q-avatar>
                  <q-icon
                    v-else
                    name="pets"
                    size="80px"
                    color="grey-5"
                    class="q-mr-md"
                  />
                  <div>
                    <div class="text-h6">{{ genealogiaData.animal.NOME }}</div>
                    <div class="text-caption">
                      {{
                        genealogiaData.animal.SEXO === 'M' ? 'Macho' : 'Fêmea'
                      }}
                    </div>
                  </div>
                </div>
              </q-card>
            </div>

            <!-- Pais -->
            <div class="row q-gutter-md justify-center q-mb-md">
              <!-- Pai -->
              <div class="col-5">
                <div class="text-center text-subtitle2 q-mb-sm">Pai</div>
                <q-card
                  v-if="genealogiaData.pai"
                  class="animal-card q-pa-md"
                >
                  <div class="row items-center">
                    <q-avatar
                      v-if="genealogiaData.pai.animal.FOTO_PRINCIPAL"
                      size="60px"
                      class="q-mr-sm"
                    >
                      <img
                        :src="`http://localhost:8000${genealogiaData.pai.animal.FOTO_PRINCIPAL}`"
                      />
                    </q-avatar>
                    <q-icon
                      v-else
                      name="pets"
                      size="60px"
                      color="grey-5"
                      class="q-mr-sm"
                    />
                    <div>
                      <div class="text-body1">
                        {{ genealogiaData.pai.animal.NOME }}
                      </div>
                      <div class="text-caption">Macho</div>
                    </div>
                  </div>
                </q-card>
                <div
                  v-else
                  class="text-center text-grey-5"
                >
                  Não informado
                </div>
              </div>

              <!-- Mãe -->
              <div class="col-5">
                <div class="text-center text-subtitle2 q-mb-sm">Mãe</div>
                <q-card
                  v-if="genealogiaData.mae"
                  class="animal-card q-pa-md"
                >
                  <div class="row items-center">
                    <q-avatar
                      v-if="genealogiaData.mae.animal.FOTO_PRINCIPAL"
                      size="60px"
                      class="q-mr-sm"
                    >
                      <img
                        :src="`http://localhost:8000${genealogiaData.mae.animal.FOTO_PRINCIPAL}`"
                      />
                    </q-avatar>
                    <q-icon
                      v-else
                      name="pets"
                      size="60px"
                      color="grey-5"
                      class="q-mr-sm"
                    />
                    <div>
                      <div class="text-body1">
                        {{ genealogiaData.mae.animal.NOME }}
                      </div>
                      <div class="text-caption">Fêmea</div>
                    </div>
                  </div>
                </q-card>
                <div
                  v-else
                  class="text-center text-grey-5"
                >
                  Não informado
                </div>
              </div>
            </div>

            <!-- Avós -->
            <div class="row q-gutter-md justify-center q-mt-md">
              <!-- Avô paterno -->
              <div class="col-2">
                <div class="text-center text-caption q-mb-sm">Avô Paterno</div>
                <q-card
                  v-if="genealogiaData.pai?.pai"
                  class="animal-card-small q-pa-sm"
                >
                  <q-avatar
                    v-if="genealogiaData.pai.pai.animal.FOTO_PRINCIPAL"
                    size="40px"
                  >
                    <img
                      :src="`http://localhost:8000${genealogiaData.pai.pai.animal.FOTO_PRINCIPAL}`"
                    />
                  </q-avatar>
                  <q-icon
                    v-else
                    name="pets"
                    size="40px"
                    color="grey-5"
                  />
                  <div class="text-caption">
                    {{ genealogiaData.pai.pai.animal.NOME }}
                  </div>
                </q-card>
                <div
                  v-else
                  class="text-center text-grey-5 text-caption"
                >
                  -
                </div>
              </div>

              <!-- Avó paterna -->
              <div class="col-2">
                <div class="text-center text-caption q-mb-sm">Avó Paterna</div>
                <q-card
                  v-if="genealogiaData.pai?.mae"
                  class="animal-card-small q-pa-sm"
                >
                  <q-avatar
                    v-if="genealogiaData.pai.mae.animal.FOTO_PRINCIPAL"
                    size="40px"
                  >
                    <img
                      :src="`http://localhost:8000${genealogiaData.pai.mae.animal.FOTO_PRINCIPAL}`"
                    />
                  </q-avatar>
                  <q-icon
                    v-else
                    name="pets"
                    size="40px"
                    color="grey-5"
                  />
                  <div class="text-caption">
                    {{ genealogiaData.pai.mae.animal.NOME }}
                  </div>
                </q-card>
                <div
                  v-else
                  class="text-center text-grey-5 text-caption"
                >
                  -
                </div>
              </div>

              <!-- Avô materno -->
              <div class="col-2">
                <div class="text-center text-caption q-mb-sm">Avô Materno</div>
                <q-card
                  v-if="genealogiaData.mae?.pai"
                  class="animal-card-small q-pa-sm"
                >
                  <q-avatar
                    v-if="genealogiaData.mae.pai.animal.FOTO_PRINCIPAL"
                    size="40px"
                  >
                    <img
                      :src="`http://localhost:8000${genealogiaData.mae.pai.animal.FOTO_PRINCIPAL}`"
                    />
                  </q-avatar>
                  <q-icon
                    v-else
                    name="pets"
                    size="40px"
                    color="grey-5"
                  />
                  <div class="text-caption">
                    {{ genealogiaData.mae.pai.animal.NOME }}
                  </div>
                </q-card>
                <div
                  v-else
                  class="text-center text-grey-5 text-caption"
                >
                  -
                </div>
              </div>

              <!-- Avó materna -->
              <div class="col-2">
                <div class="text-center text-caption q-mb-sm">Avó Materna</div>
                <q-card
                  v-if="genealogiaData.mae?.mae"
                  class="animal-card-small q-pa-sm"
                >
                  <q-avatar
                    v-if="genealogiaData.mae.mae.animal.FOTO_PRINCIPAL"
                    size="40px"
                  >
                    <img
                      :src="`http://localhost:8000${genealogiaData.mae.mae.animal.FOTO_PRINCIPAL}`"
                    />
                  </q-avatar>
                  <q-icon
                    v-else
                    name="pets"
                    size="40px"
                    color="grey-5"
                  />
                  <div class="text-caption">
                    {{ genealogiaData.mae.mae.animal.NOME }}
                  </div>
                </q-card>
                <div
                  v-else
                  class="text-center text-grey-5 text-caption"
                >
                  -
                </div>
              </div>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Fechar"
            color="grey"
            @click="genealogiaDialog = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Modal de Upload de Foto -->
    <q-dialog
      v-model="fotoDialog"
      persistent
    >
      <q-card style="min-width: 400px">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Adicionar Foto</div>
          <q-space />
          <q-btn
            icon="close"
            flat
            round
            dense
            @click="fotoDialog = false"
          />
        </q-card-section>

        <q-card-section>
          <div class="text-center q-mb-md">
            <q-avatar
              size="120px"
              class="q-mb-md"
            >
              <img
                v-if="selectedAnimal?.FOTO_PRINCIPAL"
                :src="`http://localhost:8000${selectedAnimal.FOTO_PRINCIPAL}`"
              />
              <q-icon
                v-else
                name="pets"
                size="60px"
                color="grey-5"
              />
            </q-avatar>
            <div class="text-h6">{{ selectedAnimal?.NOME }}</div>
          </div>

          <q-file
            v-model="novaFoto"
            label="Selecionar foto"
            accept="image/*"
            max-file-size="5242880"
            @rejected="onRejected"
          >
            <template v-slot:prepend>
              <q-icon name="photo_camera" />
            </template>
          </q-file>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancelar"
            color="grey"
            @click="fotoDialog = false"
          />
          <q-btn
            label="Enviar"
            color="primary"
            @click="uploadFoto"
            :loading="animalStore.loading"
            :disable="!novaFoto"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Modal de visualização de foto -->
    <q-dialog v-model="fotoViewDialog">
      <q-card style="min-width: 400px">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">{{ selectedAnimal?.NOME }}</div>
          <q-space />
          <q-btn
            icon="close"
            flat
            round
            dense
            @click="fotoViewDialog = false"
          />
        </q-card-section>

        <q-card-section class="text-center">
          <img
            v-if="selectedAnimal?.FOTO_PRINCIPAL"
            :src="`http://localhost:8000${selectedAnimal.FOTO_PRINCIPAL}`"
            style="max-width: 100%; max-height: 400px"
          />
          <div
            v-else
            class="q-pa-xl"
          >
            <q-icon
              name="pets"
              size="120px"
              color="grey-5"
            />
            <div class="text-h6 text-grey-5 q-mt-md">Sem foto</div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  import { useAnimalStore } from 'stores/animal'
  import { ErrorHandler } from 'src/utils/errorHandler'
  import { formatDate } from 'src/utils/dateUtils'

  // Emits
  const emit = defineEmits(['refresh'])

  // Composables
  const animalStore = useAnimalStore()

  // Estado reativo
  const viewDialog = ref(false)
  const genealogiaDialog = ref(false)
  const fotoDialog = ref(false)
  const fotoViewDialog = ref(false)

  const animalData = ref(null)
  const selectedAnimal = ref(null)
  const genealogiaData = ref(null)
  const novaFoto = ref(null)

  // Métodos
  function openViewDialog(animal) {
    animalData.value = animal
    viewDialog.value = true
  }

  function openFotoDialog(animal) {
    selectedAnimal.value = animal
    novaFoto.value = null
    fotoDialog.value = true
  }

  function openFotoViewDialog(animal) {
    selectedAnimal.value = animal
    fotoViewDialog.value = true
  }

  function openViewGenealogia(animal) {
    animalData.value = animal
    openGenealogia()
  }

  async function openGenealogia() {
    if (!animalData.value) return

    try {
      const data = await animalStore.getGenealogia(animalData.value.ID)
      genealogiaData.value = data
      genealogiaDialog.value = true
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao carregar genealogia')
    }
  }

  async function uploadFoto() {
    if (!novaFoto.value || !selectedAnimal.value) return

    try {
      await animalStore.uploadFoto(selectedAnimal.value.ID, novaFoto.value)
      ErrorHandler.success('Foto enviada com sucesso!')
      fotoDialog.value = false
      novaFoto.value = null
      emit('refresh')
    } catch (error) {
      ErrorHandler.handle(error, 'Erro ao enviar foto')
    }
  }

  function onRejected() {
    ErrorHandler.warning('Arquivo muito grande ou formato inválido')
  }

  function closeDialog() {
    viewDialog.value = false
    animalData.value = null
  }

  function getStatusColor(status) {
    const colors = {
      ATIVO: 'green',
      VENDIDO: 'blue',
      MORTO: 'red',
      EMPRESTADO: 'orange',
      APOSENTADO: 'grey',
    }
    return colors[status] || 'grey'
  }

  // Expor métodos
  defineExpose({
    openViewDialog,
    openFotoDialog,
    openFotoViewDialog,
    openViewGenealogia,
    openGenealogia,
  })
</script>

<style scoped>
  .animal-card {
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    background: #fafafa;
  }

  .animal-card-small {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background: #f9f9f9;
    text-align: center;
  }

  .animal-card-small .text-caption {
    font-size: 0.7rem;
    font-weight: 500;
    margin-top: 4px;
  }
</style>
