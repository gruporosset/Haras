<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">Perfil</div>
        <div class="text-subtitle1">Gerencie suas configurações de conta</div>
      </q-card-section>
      <q-card-section>
        <p><strong>Nome:</strong> {{ authStore.user?.NOME_COMPLETO }}</p>
        <p><strong>E-mail:</strong> {{ authStore.user?.EMAIL }}</p>
        <p><strong>Perfil:</strong> {{ authStore.user?.PERFIL }}</p>
        <p>
          <strong>MFA:</strong> 
          {{ mfaEnabled ? 'Ativado' : 'Desativado' }}
          <q-icon :name="mfaEnabled ? 'check_circle' : 'cancel'" :color="mfaEnabled ? 'positive' : 'negative'" />
        </p>
      </q-card-section>
      <q-card-section>
        <q-btn
          color="primary"
          label="Configurar MFA"
          @click="handleMfaSetup"
          :loading="loading"
          :disable="mfaEnabled"
        />
        <q-btn
          v-if="mfaEnabled"
          color="negative"
          label="Desativar MFA"
          @click="handleMfaDisable"
          :loading="loading"
          class="q-ml-sm"
        />
        <q-card v-if="authStore.mfaSetup" class="q-mt-md">
          <q-card-section class="text-center">
            <div class="text-subtitle1">Configure o Autenticador</div>
            <p class="q-mt-sm">
              Para ativar o MFA, instale o <strong>Google Authenticator</strong> no seu dispositivo:
            </p>
            <div class="row justify-center q-gutter-md q-mb-md">
              <a
                href="https://apps.apple.com/us/app/google-authenticator/id388497605"
                target="_blank"
                aria-label="Baixar Google Authenticator na App Store"
              >
                <q-img
                  src="https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg"
                  width="120px"
                  alt="Download on the App Store"
                />
              </a>
              <a
                href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2"
                target="_blank"
                aria-label="Baixar Google Authenticator na Play Store"
              >
                <q-img
                  src="https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png"
                  width="120px"
                  alt="Get it on Google Play"
                />
              </a>
            </div>
            <p>
              Escaneie o QR code abaixo com o Google Authenticator para configurar sua conta.
            </p>
            <q-img
              :src="authStore.mfaSetup.qr_code_url"
              style="max-width: 200px; margin: auto;"
              class="q-mt-md"
              alt="QR Code para configuração de MFA"
            />
          </q-card-section>
        </q-card>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script>
import { ref, computed } from 'vue';
import { useAuthStore } from 'stores/auth';
import { useQuasar } from 'quasar';

export default {
  setup() {
    const authStore = useAuthStore();
    const $q = useQuasar();
    const loading = ref(false);

    const mfaEnabled = computed(() => authStore.user?.MFA_ATIVO === 'S');

    const handleMfaSetup = async () => {
      loading.value = true;
      try {
        await authStore.setupMfa(authStore.user.ID);
        $q.notify({ type: 'positive', message: 'QR code gerado para MFA!' });
      } catch (err) {
        $q.notify({ type: 'negative', message: err.message || 'Erro ao configurar MFA' });
      } finally {
        loading.value = false;
      }
    };

    const handleMfaDisable = async () => {
      loading.value = true;
      try {
        await authStore.disableMfa(authStore.user.ID);
        $q.notify({ type: 'positive', message: 'MFA desativado com sucesso!' });
      } catch (err) {
        $q.notify({ type: 'negative', message: err.message || 'Erro ao desativar MFA' });
      } finally {
        loading.value = false;
      }
    };

    return { authStore, loading, mfaEnabled, handleMfaSetup, handleMfaDisable };
  },
};
</script>