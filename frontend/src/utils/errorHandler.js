// src/utils/errorHandler.js
import { Notify } from 'quasar'

/**
 * Centraliza o tratamento de erros e exibição de notificações
 */
export class ErrorHandler {
  /**
   * Processa e exibe erro de forma padronizada
   * @param {Error|Object} error - Objeto de erro
   * @param {string} defaultMessage - Mensagem padrão caso não encontre erro específico
   * @param {Object} options - Opções adicionais para notificação
   */
  static handle(error, defaultMessage = 'Erro inesperado', options = {}) {
    const message = this.extractMessage(error, defaultMessage)

    const notifyOptions = {
      type: 'negative',
      message,
      position: 'top',
      timeout: 5000,
      actions: [
        {
          icon: 'close',
          color: 'white',
          round: true,
        },
      ],
      ...options,
    }

    Notify.create(notifyOptions)

    // Log para debug
    console.error('ErrorHandler:', error)

    return message
  }

  /**
   * Extrai mensagem de erro de diferentes formatos
   * @param {Error|Object} error
   * @param {string} defaultMessage
   * @returns {string}
   */
  static extractMessage(error, defaultMessage) {
    // 1. Verificar se é erro do backend (FastAPI validation)
    console.log(error?.response?.data?.detail)
    if (error?.response?.data?.detail) {
      const detail = error.response.data.detail

      // Se detail é array (validation errors)
      if (Array.isArray(detail)) {
        const messages = detail.map(err => {
          // Formatar mensagem com campo se disponível
          const field = err.loc?.length > 1 ? err.loc[err.loc.length - 1] : null
          const fieldLabel = this.getFieldLabel(field)

          if (fieldLabel) {
            return `${fieldLabel}: ${err.msg}`
          }
          return err.msg
        })

        // Se múltiplos erros, mostrar apenas o primeiro ou concatenar
        return messages.length > 1
          ? `${messages[0]} (e mais ${messages.length - 1} erro${messages.length > 2 ? 's' : ''})`
          : messages[0]
      }

      // Se detail é string
      if (typeof detail === 'string') {
        return detail
      }
    }

    // 2. Verificar outros formatos de erro HTTP
    if (error?.response?.data?.message) {
      return error.response.data.message
    }

    // 3. Verificar status HTTP
    if (error?.response?.status) {
      return this.getHttpStatusMessage(error.response.status)
    }

    // 4. Verificar se é erro de rede
    if (
      error?.code === 'NETWORK_ERROR' ||
      error?.message?.includes('Network Error')
    ) {
      return 'Erro de conexão. Verifique sua internet.'
    }

    // 5. Verificar se tem message direto
    if (error?.message) {
      return error.message
    }

    // 6. Fallback para mensagem padrão
    return defaultMessage
  }

  /**
   * Converte nomes de campos técnicos para labels amigáveis
   * @param {string} field
   * @returns {string}
   */
  static getFieldLabel(field) {
    const fieldLabels = {
      DATA_OCORRENCIA: 'Data de Ocorrência',
      ID_USUARIO_REGISTRO: 'Usuário',
      ID_ANIMAL: 'Animal',
      TIPO_REGISTRO: 'Tipo de Registro',
      DESCRICAO: 'Descrição',
      VETERINARIO_RESPONSAVEL: 'Veterinário',
      DATA_NASCIMENTO: 'Data de Nascimento',
      NOME: 'Nome',
      SEXO: 'Sexo',
      COR: 'Cor',
      EMAIL: 'E-mail',
      SENHA: 'Senha',
      CONFIRM_SENHA: 'Confirmação de Senha',
      TELEFONE: 'Telefone',
      CPF: 'CPF',
      CNPJ: 'CNPJ',
      ENDERECO: 'Endereço',
      CIDADE: 'Cidade',
      ESTADO: 'Estado',
      CEP: 'CEP',
      DATA_INICIO: 'Data de Início',
      DATA_FIM: 'Data de Fim',
      VALOR: 'Valor',
      QUANTIDADE: 'Quantidade',
      PRECO: 'Preço',
      ESTOQUE: 'Estoque',
      // Adicione mais conforme necessário
    }

    return fieldLabels[field] || field
  }

  /**
   * Retorna mensagem amigável baseada no status HTTP
   * @param {number} status
   * @returns {string}
   */
  static getHttpStatusMessage(status) {
    const statusMessages = {
      400: 'Dados inválidos',
      401: 'Acesso não autorizado',
      403: 'Acesso negado',
      404: 'Recurso não encontrado',
      409: 'Conflito de dados',
      422: 'Dados inválidos',
      500: 'Erro interno do servidor',
      502: 'Servidor indisponível',
      503: 'Serviço temporariamente indisponível',
    }

    return statusMessages[status] || `Erro HTTP ${status}`
  }

  /**
   * Método específico para success (pode ser útil)
   * @param {string} message
   * @param {Object} options
   */
  static success(message, options = {}) {
    Notify.create({
      type: 'positive',
      message,
      position: 'top',
      timeout: 3000,
      ...options,
    })
  }

  /**
   * Método específico para warning
   * @param {string} message
   * @param {Object} options
   */
  static warning(message, options = {}) {
    Notify.create({
      type: 'warning',
      message,
      position: 'top',
      timeout: 4000,
      ...options,
    })
  }

  /**
   * Método específico para info
   * @param {string} message
   * @param {Object} options
   */
  static info(message, options = {}) {
    Notify.create({
      type: 'info',
      message,
      position: 'top',
      timeout: 3000,
      ...options,
    })
  }
}
