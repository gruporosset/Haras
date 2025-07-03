# Manual do Usuário - Sistema Haras

## Sumário

1. [Introdução](#introdução)
2. [Acesso ao Sistema](#acesso-ao-sistema)
3. [Dashboard Principal](#dashboard-principal)
4. [Módulo Animais](#módulo-animais)
5. [Módulo Terrenos](#módulo-terrenos)
6. [Módulo Saúde](#módulo-saúde)
7. [Módulo Medicamentos](#módulo-medicamentos)
8. [Módulo Ração e Suplementos](#módulo-ração-e-suplementos)
9. [Módulo Manejo de Terrenos](#módulo-manejo-de-terrenos)
10. [Módulo Reprodução](#módulo-reprodução)
11. [Módulo Crescimento](#módulo-crescimento)
12. [Módulo Ferrageamento](#módulo-ferrageamento)
13. [Módulo Movimentações](#módulo-movimentações)
14. [Perfil do Usuário](#perfil-do-usuário)
15. [Dicas e Boas Práticas](#dicas-e-boas-práticas)

---

## Introdução

O Sistema Haras é uma plataforma completa para gestão de haras, desenvolvida especificamente para equinocultores. O sistema permite controlar todos os aspectos da criação de cavalos, desde o cadastro de animais até o manejo de pastagens, controle sanitário e reprodução.

### Principais Funcionalidades:

- **Gestão de Animais**: Cadastro, genealogia, crescimento e localização
- **Controle Sanitário**: Vacinação, tratamentos e medicamentos
- **Manejo de Terrenos**: Aplicações, análises de solo e controle de pastagens
- **Reprodução**: Coberturas, gestações e nascimentos
- **Nutrição**: Planos alimentares e controle de estoque de ração
- **Ferrageamento**: Agendamentos e histórico de serviços
- **Dashboard**: Visão geral com KPIs e alertas importantes

---

## Acesso ao Sistema

### Login

1. Acesse a URL do sistema através do navegador
2. Digite seu **email** e **senha** nos campos correspondentes
3. Clique em **"Entrar"**

### Esqueci Minha Senha

1. Na tela de login, clique em **"Esqueci minha senha"**
2. Digite seu email cadastrado
3. Verifique sua caixa de email para o token de redefinição
4. Clique no link recebido ou acesse a página de redefinição
5. Digite o token e sua nova senha
6. Confirme a nova senha

**Importante**: O token de redefinição é válido por apenas 1 hora.

### Autenticação Multi-Fator (MFA)

O sistema oferece camada adicional de segurança através do MFA:

1. **Configuração do MFA**:

   - No perfil do usuário, ative a opção MFA
   - Escaneie o QR Code com um aplicativo autenticador (Google Authenticator, Authy)
   - Digite o código de 6 dígitos para confirmar a configuração

2. **Login com MFA**:

   - Digite email e senha normalmente
   - Será solicitado o código de 6 dígitos do seu aplicativo autenticador
   - Digite o código e clique em "Verificar"

3. **Desativação do MFA**:
   - Acesse seu perfil
   - Clique em "Desativar MFA"
   - Confirme a desativação

### Primeiro Acesso

- No primeiro acesso, você será direcionado para alterar sua senha inicial
- Escolha uma senha forte com pelo menos 8 caracteres
- Inclua letras maiúsculas, minúsculas, números e símbolos

### Controle de Tentativas

- Após 5 tentativas de login incorretas, a conta é bloqueada por 30 minutos
- Durante o bloqueio, não será possível acessar o sistema
- Aguarde o período ou contate o administrador para desbloqueio

---

## Dashboard Principal

O Dashboard é a tela inicial do sistema, oferecendo uma visão geral do haras.

### KPIs Principais

- **Total de Animais**: Número de animais ativos no haras
- **Total de Terrenos**: Terrenos disponíveis para uso
- **Animais em Tratamento**: Animais com aplicações programadas nos próximos 7 dias
- **Alertas de Estoque**: Produtos com estoque baixo
- **Próximas Aplicações**: Aplicações de medicamentos ou tratamentos programadas
- **Gestações Ativas**: Éguas em período de gestação

### Alertas e Notificações

- **Alertas de Saúde**: Animais que necessitam atenção médica urgente
- **Alertas de Estoque**: Medicamentos, rações ou produtos de manejo com estoque baixo
- **Aplicações Pendentes**: Tratamentos que devem ser realizados

### Gráficos

- **Custos Mensais**: Evolução dos gastos ao longo dos meses
- **Distribuição de Animais**: Visualização da distribuição por categorias

### Filtros

- **Período**: Selecione datas de início e fim para análise
- **Proprietário**: Filtre dados por proprietário específico

---

## Módulo Animais

### Cadastro de Animais

1. Acesse **"Animais"** no menu lateral
2. Clique no botão **"Novo Animal"**
3. Preencha os dados obrigatórios:

   - **Nome**: Nome do animal
   - **Sexo**: Macho (M) ou Fêmea (F)
   - **Data de Nascimento**: Data no formato DD/MM/AAAA
   - **Pelagem**: Cor e características da pelagem

4. Dados opcionais:

   - **Número de Registro**: Registro oficial do animal
   - **Chip de Identificação**: Código do chip implantado
   - **Genealogia**: Selecione pai e mãe se já cadastrados
   - **Origem**: Local de nascimento ou procedência
   - **Proprietário**: Dados do proprietário atual

5. Clique em **"Salvar"**

### Busca e Filtros

- **Busca por Nome**: Digite o nome do animal no campo de busca
- **Filtro por Sexo**: Selecione Macho, Fêmea ou Todos
- **Filtro por Status**: Ativo, Vendido, Morto, etc.
- **Filtro por Proprietário**: Busque animais de um proprietário específico

### Ações Disponíveis

- **Visualizar**: Ver todos os dados do animal
- **Editar**: Alterar informações cadastrais
- **Histórico**: Acessar histórico completo de saúde, crescimento e movimentações

---

## Módulo Terrenos

### Cadastro de Terrenos

1. Acesse **"Terrenos"** no menu lateral
2. Clique em **"Novo Terreno"**
3. Preencha as informações:
   - **Nome**: Identificação do terreno (ex: "Pasto 1", "Piquete Norte")
   - **Área em Hectares**: Tamanho do terreno
   - **Tipo de Solo**: Classificação do solo
   - **Coordenadas**: Latitude e longitude para localização
   - **Capacidade de Animais**: Número máximo recomendado
   - **Tipo de Pastagem**: Espécie de gramínea predominante

### Gestão de Terrenos

- **Status do Terreno**: Disponível, Em Uso, Manutenção, Quarentena
- **Animais Atuais**: Visualize quais animais estão no terreno
- **Histórico de Uso**: Acompanhe o histórico de ocupação
- **Aplicações Realizadas**: Controle de produtos aplicados

### Poços Artesianos

- **Cadastro de Poços**: Registre poços existentes no terreno
- **Medições**: Registre nível e qualidade da água
- **Manutenções**: Controle de limpeza e manutenções

---

## Módulo Saúde

### Registro de Aplicações

1. Acesse **"Saúde"** no menu lateral
2. Clique em **"Nova Aplicação"**
3. Selecione o **Animal**
4. Escolha o **Tipo de Aplicação**:

   - Vacinação
   - Vermifugação
   - Tratamento
   - Exame
   - Preventivo

5. Preencha os dados:
   - **Data da Aplicação**
   - **Medicamento/Produto Usado**
   - **Dosagem Aplicada**
   - **Veterinário Responsável**
   - **Observações**
   - **Próxima Aplicação** (se aplicável)

### Calendário de Saúde

- Visualize todas as aplicações programadas em formato de calendário
- Identifique rapidamente animais que precisam de atenção
- Receba alertas de aplicações pendentes

### Histórico Sanitário

- Acesse o histórico completo de cada animal
- Visualize gráficos de evolução da saúde
- Exporte relatórios para veterinários

### Lembretes e Alertas

- O sistema enviará lembretes automáticos de aplicações próximas
- Alertas para animais que passaram da data programada
- Notificações de estoque baixo de medicamentos

---

## Módulo Medicamentos

### Cadastro de Medicamentos

1. Acesse **"Medicamentos"** no menu lateral
2. Aba **"Medicamentos"** → **"Novo Medicamento"**
3. Preencha as informações:

   - **Nome Comercial**
   - **Princípio Ativo**
   - **Concentração**
   - **Forma Farmacêutica**: Injetável, Oral, Tópico
   - **Fabricante**
   - **Registro MAPA**: Número do registro

4. Controle de Estoque:

   - **Estoque Atual**
   - **Estoque Mínimo**
   - **Unidade de Medida**: ML, G, Comprimido, Dose
   - **Preço Unitário**

5. Informações Técnicas:
   - **Período de Carência**: Dias para abate
   - **Requer Receita**: Sim/Não
   - **Condições de Armazenamento**

### Movimentação de Estoque

1. Aba **"Movimentação Estoque"**
2. Tipos de movimentação:

   - **Entrada**: Compra de medicamentos
   - **Saída**: Aplicação em animais
   - **Ajuste**: Correção de estoque

3. Para **Entrada**:

   - Selecione o medicamento
   - Quantidade adquirida
   - Nota fiscal e fornecedor
   - Lote e validade
   - Preço unitário

4. Para **Saída**:
   - Selecione medicamento e animal
   - Quantidade aplicada
   - Referência à aplicação de saúde

### Aplicação Rápida

- Na aba **"Aplicação"**, registre rapidamente a aplicação de medicamentos
- O sistema debita automaticamente do estoque
- Cria registro no histórico de saúde do animal

### Alertas de Medicamentos

- **Estoque Baixo**: Produtos abaixo do estoque mínimo
- **Validade Próxima**: Medicamentos próximos ao vencimento
- **Ruptura**: Produtos em falta

---

## Módulo Ração e Suplementos

### Cadastro de Produtos

1. Acesse **"Ração"** no menu lateral
2. Aba **"Produtos Ração"** → **"Novo Produto"**
3. Informações básicas:

   - **Nome do Produto**
   - **Tipo de Alimento**: Ração, Suplemento, Concentrado, Volumoso
   - **Marca/Fabricante**
   - **Composição Nutricional**

4. Controle de Estoque:
   - **Estoque Atual**
   - **Estoque Mínimo**
   - **Unidade de Medida**: KG, Saco, Fardo
   - **Preço por Unidade**

### Planos Alimentares

1. Aba **"Planos Alimentares"**
2. Crie planos específicos por categoria:

   - **Potros**: Até 24 meses
   - **Adultos**: Animais em manutenção
   - **Gestantes**: Éguas em gestação
   - **Lactantes**: Éguas com potro ao pé
   - **Atletas**: Animais em treinamento

3. Configure para cada plano:
   - **Quantidade Diária** por produto
   - **Número de Refeições**
   - **Horários de Fornecimento**
   - **Observações Especiais**

### Fornecimento Diário

1. Aba **"Fornecimento"**
2. Registre o fornecimento realizado:
   - **Data do Fornecimento**
   - **Animal ou Grupo**
   - **Produtos Fornecidos**
   - **Quantidades**
   - **Horário**
   - **Responsável**

### Movimentação de Estoque

- **Entrada**: Compra de ração e suplementos
- **Saída**: Fornecimento aos animais
- **Ajuste**: Correções de estoque
- **Transferência**: Entre depósitos

### Relatórios Nutricionais

- **Consumo por Animal**: Acompanhe o consumo individual
- **Custo Alimentar**: Calcule o custo de alimentação
- **Previsão de Compras**: Baseado no consumo histórico
- **Análise Nutricional**: Verifique se as necessidades estão sendo atendidas

---

## Módulo Manejo de Terrenos

### Produtos de Manejo

1. Acesse **"Manejo"** no menu lateral
2. Aba **"Produtos Manejo"** → **"Novo Produto"**
3. Categorias de produtos:

   - **Fertilizantes**: NPK, Ureia, Superfosfatos
   - **Corretivos**: Calcário, Gesso
   - **Herbicidas**: Controle de plantas daninhas
   - **Sementes**: Gramíneas e leguminosas

4. Informações técnicas:
   - **Princípio Ativo**
   - **Concentração**
   - **Dose Recomendada por Hectare**
   - **Período de Carência**
   - **Registro no Ministério**

### Aplicações em Terrenos

1. Aba **"Aplicações Terrenos"**
2. Registre aplicações realizadas:

   - **Terreno**: Selecione o local da aplicação
   - **Tipo de Manejo**: Adubação, Calagem, Controle de Pragas
   - **Produto Aplicado**
   - **Quantidade e Dose**
   - **Data da Aplicação**
   - **Área Aplicada**
   - **Equipamento Utilizado**
   - **Condições Climáticas**

3. **Período de Carência**:
   - O sistema calcula automaticamente quando o terreno pode receber animais
   - Alertas são gerados se animais forem colocados antes do prazo

### Análises de Solo

1. Aba **"Análises Solo"**
2. Registre resultados de análises:

   - **Data da Coleta**
   - **Laboratório Responsável**
   - **pH do Solo**
   - **Matéria Orgânica**
   - **Fósforo (P)**
   - **Potássio (K)**
   - **Cálcio (Ca)**
   - **Magnésio (Mg)**
   - **Alumínio (Al)**

3. **Recomendações**:
   - Com base nos resultados, registre recomendações técnicas
   - Planeje próximas aplicações de corretivos e fertilizantes

### Movimentação de Estoque

- Controle entrada e saída de produtos de manejo
- Rastreie uso por terreno e aplicação
- Calcule custos por hectare

### Relatórios de Manejo

- **Custos por Terreno**: Acompanhe gastos com manejo
- **Histórico de Aplicações**: Visualize todas as aplicações realizadas
- **Eficiência de Produtos**: Compare resultados de diferentes produtos
- **Planejamento de Compras**: Baseado no histórico de uso

---

## Módulo Reprodução

### Cadastro de Coberturas

1. Acesse **"Reprodução"** no menu lateral
2. Clique em **"Nova Cobertura"**
3. Preencha os dados:
   - **Égua**: Selecione a fêmea
   - **Garanhão**: Selecione o macho
   - **Data da Cobertura**
   - **Tipo de Cobertura**: Natural, Inseminação Artificial
   - **Veterinário Responsável**
   - **Observações**

### Diagnóstico de Gestação

1. Após 14-18 dias da cobertura, registre o diagnóstico
2. **Resultado**: Positivo, Negativo, Inconclusivo
3. **Data do Exame**
4. **Método**: Ultrassom, Palpação
5. **Data Prevista do Parto** (calculada automaticamente)

### Acompanhamento da Gestação

- **Exames Periódicos**: Registre ultrassons e exames veterinários
- **Vacinações Específicas**: Controle de vacinas para éguas gestantes
- **Alimentação Especial**: Planos alimentares para gestantes
- **Alertas**: O sistema gera alertas para datas importantes

### Parto e Nascimento

1. Registre o parto quando ocorrer:

   - **Data e Horário do Parto**
   - **Tipo de Parto**: Normal, Assistido, Cesariana
   - **Veterinário Presente**
   - **Observações sobre o Parto**

2. **Dados do Potro**:
   - Automaticamente cadastra o potro no sistema
   - Vincula à mãe na genealogia
   - Define status como "Lactente"

### Desmame

- Registre a data do desmame
- Atualize status do potro para "Desmamado"
- Mude status da égua para "Vazia"

### Relatórios Reprodutivos

- **Taxa de Fertilidade**: Por garanhão e égua
- **Intervalo entre Partos**: Controle de eficiência reprodutiva
- **Previsão de Partos**: Planejamento de nascimentos
- **Custos Reprodutivos**: Análise de gastos com reprodução

---

## Módulo Crescimento

### Medições de Crescimento

1. Acesse **"Crescimento"** no menu lateral
2. Selecione o animal
3. Registre as medidas:
   - **Data da Medição**
   - **Peso (kg)**
   - **Altura na Cernelha (cm)**
   - **Perímetro Torácico (cm)**
   - **Altura na Garupa (cm)**
   - **Comprimento do Corpo (cm)**

### Curvas de Crescimento

- Visualize gráficos de evolução para cada animal
- Compare com padrões da raça
- Identifique desvios de crescimento
- Planeje ajustes nutricionais

### Categorização por Idade

- **Potros**: 0-12 meses
- **Sobreanos**: 12-24 meses
- **Dois Anos**: 24-36 meses
- **Adultos**: Acima de 36 meses

### Alertas de Crescimento

- **Crescimento Lento**: Animais abaixo da curva esperada
- **Perda de Peso**: Reduções significativas de peso
- **Medições Atrasadas**: Lembretes para medir animais jovens

### Relatórios

- **Evolução Individual**: Histórico completo por animal
- **Comparativo por Lote**: Analise grupos de animais
- **Eficiência Alimentar**: Relacione crescimento com fornecimento de ração

---

## Módulo Ferrageamento

### Agendamento de Serviços

1. Acesse **"Ferrageamento"** no menu lateral
2. Clique em **"Novo Agendamento"**
3. Preencha:
   - **Animal**: Selecione o cavalo
   - **Data Programada**
   - **Tipo de Serviço**: Ferrageamento, Casqueamento, Correção
   - **Ferrador**: Profissional responsável
   - **Observações Especiais**

### Registro de Serviços Realizados

1. Após o serviço, atualize o registro:
   - **Data de Realização**
   - **Serviços Executados**
   - **Estado dos Cascos**
   - **Problemas Encontrados**
   - **Recomendações**
   - **Custo do Serviço**
   - **Próximo Agendamento** (automaticamente sugerido)

### Tipos de Serviços

- **Ferrageamento Completo**: Troca de todas as ferraduras
- **Ferrageamento Parcial**: Troca de ferraduras específicas
- **Casqueamento**: Apenas corte e limpeza dos cascos
- **Correção Ortopédica**: Ferraduras especiais para correções
- **Remoção de Ferraduras**: Para animais em descanso

### Histórico por Animal

- Visualize todo o histórico de ferrageamento
- Identifique padrões de desgaste
- Acompanhe a saúde dos cascos
- Planeje manutenções preventivas

### Gestão de Ferradores

- Cadastre profissionais de confiança
- Acompanhe performance e qualidade
- Controle agendas e disponibilidade
- Registre contatos e especialidades

### Alertas e Lembretes

- **Ferrageamento Próximo**: Animais que precisam de serviço em breve
- **Ferrageamento Atrasado**: Animais que passaram da data recomendada
- **Problemas nos Cascos**: Animais que necessitam atenção especial

### Relatórios

- **Custos de Ferrageamento**: Gastos por período e animal
- **Frequência de Serviços**: Intervalos entre ferrageamentos
- **Performance dos Ferradores**: Avaliação dos profissionais

---

## Módulo Movimentações

### Tipos de Movimentação

1. **Entrada no Haras**:

   - Compra de animais
   - Recebimento para estadia
   - Retorno de empréstimo

2. **Saída do Haras**:

   - Venda de animais
   - Empréstimo para terceiros
   - Transferência definitiva

3. **Movimentação Interna**:
   - Troca entre terrenos
   - Transferência para baias
   - Isolamento sanitário

### Registro de Movimentações

1. Acesse **"Movimentações"** no menu lateral
2. Clique em **"Nova Movimentação"**
3. Selecione:
   - **Animal**
   - **Tipo de Movimentação**
   - **Data da Movimentação**
   - **Origem**: Terreno atual ou externo
   - **Destino**: Novo terreno ou externo
   - **Motivo**: Descrição da razão
   - **Observações**

### Localização Atual

- Visualize onde cada animal está localizado
- Consulte histórico de movimentações
- Identifique rapidamente a localização atual
- Planeje movimentações futuras

### Controle de Capacidade

- O sistema verifica a capacidade dos terrenos
- Alerta quando a lotação está próxima do limite
- Sugere redistribuição de animais
- Monitora o bem-estar animal

### Rastreabilidade

- Histórico completo de movimentações por animal
- Relatórios de ocupação por terreno
- Controle de entrada e saída do haras
- Auditoria de movimentações

---

## Perfil do Usuário

### Dados Pessoais

1. Clique no ícone do usuário no canto superior direito
2. Selecione **"Perfil"**
3. Atualize suas informações:
   - **Nome Completo**
   - **Email**
   - **Telefone**
   - **Cargo/Função**

### Alteração de Senha

1. No perfil, clique em **"Alterar Senha"**
2. Digite a **senha atual**
3. Digite a **nova senha**
4. **Confirme a nova senha**
5. Clique em **"Salvar"**

### Configurações

- **Notificações**: Configure quais alertas deseja receber
- **Timezone**: Ajuste o fuso horário
- **Idioma**: Selecione o idioma preferido
- **Formato de Data**: DD/MM/AAAA ou MM/DD/AAAA

### Logout

- Clique no ícone do usuário
- Selecione **"Sair"**
- Confirme o logout

---

## Uso Mobile e Responsivo

### Acesso via Dispositivos Móveis

O Sistema Haras é totalmente responsivo e pode ser acessado através de:

- **Smartphones**: iOS e Android
- **Tablets**: iPad e tablets Android
- **Navegadores Móveis**: Chrome, Safari, Firefox

### Funcionalidades Mobile Otimizadas

As seguintes ações são especialmente otimizadas para uso mobile:

#### Entrada Rápida de Dados

1. **Medições de Crescimento**:

   - Interface simplificada para inserção rápida
   - Campos numéricos otimizados para teclado móvel
   - Validação instantânea de medidas

2. **Aplicações de Medicamentos**:

   - Seleção rápida de animal e medicamento
   - Registro com poucos toques
   - Confirmação visual das aplicações

3. **Registro de Fornecimento de Ração**:

   - Interface intuitiva para registro diário
   - Cálculos automáticos de quantidades
   - Histórico acessível rapidamente

4. **Movimentações de Animais**:
   - Registro rápido de mudanças de terreno
   - Seleção visual de origem e destino
   - Confirmação instantânea

#### Consultas Rápidas

- **Localização de Animais**: Encontre rapidamente onde está cada animal
- **Próximas Aplicações**: Visualize o que precisa ser feito hoje
- **Alertas de Estoque**: Verifique produtos em falta
- **Status de Saúde**: Consulte animais que precisam de atenção

### Dicas para Uso Mobile

#### Navegação

- Use o menu hambúrguer no canto superior esquerdo
- Navegue entre abas deslizando lateralmente
- Use a busca para encontrar animais rapidamente

#### Entrada de Dados

- Aproveite o teclado numérico para medidas e quantidades
- Use a câmera para anexar fotos quando disponível
- Valide os dados antes de salvar

#### Sincronização

- O sistema sincroniza automaticamente quando há conexão
- Dados inseridos offline são salvos localmente
- Sincronização ocorre assim que a conexão é restaurada

#### Performance

- Mantenha o app atualizado no navegador
- Limpe o cache periodicamente
- Use Wi-Fi quando possível para melhor performance

---

## Integração com IA e Análise de Dados

### Preparação para IA

O sistema está preparado para futuras integrações com Inteligência Artificial:

#### Estrutura de Dados

- **Histórico Completo**: Todos os eventos são registrados com timestamp
- **Rastreabilidade**: Cada alteração é auditada
- **Normalização**: Dados estruturados para análise
- **Metadados**: Informações contextuais para melhor análise

#### Possibilidades Futuras

1. **Análise Preditiva**:

   - Previsão de problemas de saúde baseada no histórico
   - Otimização de planos alimentares
   - Predição de performance reprodutiva

2. **BI Conversacional**:

   - Perguntas em linguagem natural: "Quantos potros nasceram este ano?"
   - Geração automática de relatórios
   - Insights baseados em padrões dos dados

3. **Recomendações Inteligentes**:
   - Sugestões de tratamentos baseadas em casos similares
   - Otimização de custos operacionais
   - Alertas preventivos de saúde

### Consultas em Linguagem Natural (Futuro)

Exemplos de perguntas que poderão ser feitas:

- "Qual o custo médio mensal com medicamentos?"
- "Quais animais precisam de vermifugação esta semana?"
- "Como está a evolução do peso dos potros de 2024?"
- "Qual terreno tem melhor taxa de crescimento dos animais?"
- "Mostre um gráfico dos nascimentos por mês"

### Preparação dos Dados

Para maximizar o potencial da IA:

1. **Registre Consistentemente**: Mantenha todos os eventos atualizados
2. **Use Categorias Padronizadas**: Siga nomenclaturas consistentes
3. **Documente Observações**: Inclua observações detalhadas
4. **Mantenha Histórico**: Não delete dados históricos importantes

---

## Dicas e Boas Práticas

### Organização dos Dados

1. **Padronização de Nomes**:

   - Use convenções consistentes para nomes de animais
   - Numere terrenos de forma lógica
   - Mantenha nomenclatura clara para produtos

2. **Backup Regular**:

   - Exporte relatórios importantes periodicamente
   - Mantenha cópias de documentos importantes
   - Verifique a integridade dos dados regularmente

3. **Atualização Constante**:
   - Registre eventos no dia em que acontecem
   - Mantenha estoques sempre atualizados
   - Confirme aplicações realizadas

### Eficiência Operacional

1. **Use os Alertas**:

   - Configure lembretes para não esquecer aplicações
   - Monitore estoques baixos proativamente
   - Acompanhe alertas de saúde diariamente

2. **Planejamento**:

   - Use o calendário para planejar atividades
   - Programe aplicações com antecedência
   - Monitore períodos de carência

3. **Relatórios**:
   - Gere relatórios mensais para análise
   - Compare períodos para identificar tendências
   - Use dados para tomar decisões

### Segurança

1. **Senha Forte**:

   - Use senhas com pelo menos 8 caracteres
   - Inclua números, letras e símbolos
   - Troque a senha periodicamente

2. **Logout Seguro**:

   - Sempre faça logout ao sair
   - Não deixe sessões abertas em computadores compartilhados
   - Verifique se não há outras pessoas usando sua conta

3. **Dados Sensíveis**:
   - Não compartilhe informações de login
   - Mantenha dados de propriedade protegidos
   - Reporte problemas de segurança imediatamente

### Backup e Recuperação de Dados

#### Backup Automático

- O sistema realiza backup automático dos dados diariamente
- Backups são mantidos por 30 dias
- Dados críticos têm backup em tempo real

#### Exportação de Dados

1. **Relatórios**: Exporte relatórios em PDF ou Excel
2. **Dados de Animais**: Exporte cadastros completos
3. **Histórico Sanitário**: Mantenha cópias de tratamentos
4. **Genealogia**: Exporte árvores genealógicas

#### Recuperação

- Em caso de perda de dados, contate o suporte técnico
- Backups podem ser restaurados em até 24 horas
- Dados dos últimos 30 dias sempre disponíveis

### Manutenção Preventiva do Sistema

#### Limpeza Periódica

1. **Mensalmente**:

   - Revise registros duplicados
   - Atualize dados de contato
   - Verifique consistência de estoques

2. **Trimestralmente**:

   - Analise relatórios de uso
   - Remova dados desnecessários
   - Atualize cadastros de produtos

3. **Anualmente**:
   - Revise todos os cadastros de animais
   - Atualize informações de proprietários
   - Archive dados antigos não utilizados

#### Verificação de Consistência

- **Localizações**: Confirme que todos os animais têm localização
- **Estoques**: Valide estoques físicos vs sistema
- **Datas**: Verifique datas de aplicações e tratamentos
- **Genealogia**: Confirme vínculos familiares

### Atualizações do Sistema

#### Notificações

- Você será notificado sobre atualizações importantes
- Mudanças significativas serão comunicadas por email
- Novas funcionalidades serão apresentadas no login

#### Cronograma

- **Atualizações de Segurança**: Aplicadas automaticamente
- **Melhorias de Performance**: Mensalmente
- **Novas Funcionalidades**: Trimestralmente
- **Atualizações Maiores**: Semestralmente

#### Preparação para Atualizações

- Mantenha dados sempre atualizados
- Faça backup de informações críticas
- Teste novas funcionalidades em ambiente controlado

### Troubleshooting Comum

#### Problemas de Login

1. **Senha Incorreta**: Use "Esqueci minha senha"
2. **Conta Bloqueada**: Aguarde 30 minutos ou contate suporte
3. **MFA não Funciona**: Verifique horário do dispositivo

#### Problemas de Performance

1. **Lentidão**: Limpe cache do navegador
2. **Timeout**: Verifique conexão de internet
3. **Erro de Carregamento**: Recarregue a página

#### Problemas de Dados

1. **Dados não Salvam**: Verifique campos obrigatórios
2. **Erro de Validação**: Confirme formato dos dados
3. **Duplicações**: Use busca antes de criar novos registros

### Suporte Técnico

#### Canais de Atendimento

- **Email**: Descreva detalhadamente o problema
- **Telefone**: Para questões urgentes
- **Chat**: Suporte online durante horário comercial
- **Documentação**: Consulte este manual primeiro

#### Informações para Suporte

Ao contatar o suporte, tenha em mãos:

- **Usuário e Email**: Identificação da conta
- **Descrição do Problema**: O que aconteceu e quando
- **Passos Realizados**: O que você tentou fazer
- **Navegador e Versão**: Informações técnicas
- **Capturas de Tela**: Se aplicável

#### Horários de Atendimento

- **Segunda a Sexta**: 8h às 18h
- **Sábados**: 8h às 12h
- **Emergências**: 24h via email
- **Feriados**: Apenas emergências

---

## Glossário de Termos

### Termos Equinos

- **Coberturas**: Processo reprodutivo entre garanhão e égua
- **Gestação**: Período de 11 meses de desenvolvimento do potro
- **Desmame**: Separação do potro da mãe (6-8 meses)
- **Casqueamento**: Limpeza e corte dos cascos
- **Ferrageamento**: Colocação de ferraduras nos cascos

### Termos Técnicos

- **MFA**: Multi-Factor Authentication (Autenticação Multi-Fator)
- **Token**: Código de segurança temporário
- **API**: Interface de programação de aplicações
- **Dashboard**: Painel principal com resumo de informações
- **KPI**: Key Performance Indicator (Indicador de Performance)

### Termos do Sistema

- **Aplicação**: Administração de medicamentos ou tratamentos
- **Movimentação**: Transferência de animais entre locais
- **Manejo**: Cuidados e manutenção de terrenos e pastagens
- **Genealogia**: Registro de parentesco entre animais
- **Rastreabilidade**: Capacidade de rastrear histórico completo

---

## Conclusão

Este manual apresenta as principais funcionalidades do Sistema Haras. Para maximizar os benefícios da plataforma:

- **Registre todos os eventos**: Quanto mais dados você inserir, mais útil o sistema será
- **Use os relatórios**: Analise os dados para tomar decisões melhores
- **Mantenha-se atualizado**: Registre informações regularmente
- **Explore todas as funcionalidades**: Cada módulo oferece ferramentas valiosas

O Sistema Haras foi desenvolvido para simplificar a gestão do seu haras e melhorar a qualidade dos cuidados com os animais. Com uso consistente e adequado, você terá controle total sobre todos os aspectos da criação.

Para dúvidas adicionais ou suporte técnico, entre em contato com nossa equipe de desenvolvimento.
