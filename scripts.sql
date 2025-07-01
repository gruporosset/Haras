-- ========================================
-- Tables
-- ========================================

create table usuarios (
   id                    number
      generated always as identity
   primary key,
   nome_completo         varchar2(200) not null,
   email                 varchar2(100) not null unique,
   senha_hash            varchar2(500), -- Aumentar para algoritmos modernos 
   salt                  varchar2(100), -- CRÍTICO: Salt único por usuário 
   data_cadastro         date default sysdate,
   data_ultimo_login     date,
   token_cadastro        varchar2(500),
   token_cadastro_expira date, -- CRÍTICO: Expiração do token
   reset_password_token  varchar2(500),
   reset_token_expira    date, -- CRÍTICO: Expiração do reset 
   tentativas_login      number default 0, -- Controle de força bruta
   bloqueado_ate         date, -- Bloqueio temporário 
   perfil                varchar2(20) default 'USER' check ( perfil in ( 'ADMIN',
                                                          'USER',
                                                          'READONLY' ) ),
   primeiro_acesso       char(1) default 'S',
   ativo                 char(1) default 'S' check ( ativo in ( 'S',
                                                'N' ) ),
   mfa_ativo             char(1) default 'N' check ( mfa_ativo in ( 'S',
                                                        'N' ) )
);

create table animais (
   id                    number
      generated always as identity
   primary key,
   nome                  varchar2(100) not null,
   numero_registro       varchar2(50) unique,
   chip_identificacao    varchar2(50) unique,
   sexo                  char(1) check ( sexo in ( 'M',
                                  'F' ) ),
   data_nascimento       date,
   pelagem               varchar2(50),
   status_animal         varchar2(20) default 'ATIVO',
   id_pai                number
      references animais ( id ),
   id_mae                number
      references animais ( id ),
   origem                varchar2(100),
   id_usuario_cadastro   number
      references usuarios ( id ),
   data_cadastro         date default sysdate,
   id_usuario_alteracao  number
      references usuarios ( id ),
   data_alteracao        date,
   observacoes           clob,
   proprietario          varchar2(200),
   contato_proprietario  varchar2(200),
   cpf_cnpj_proprietario varchar2(20)
);

create table medicamentos (
   id                  number
      generated always as identity
   primary key,
   nome                varchar2(200) not null,
   principio_ativo     varchar2(200),
   concentracao        varchar2(100),
   forma_farmaceutica  varchar2(50), -- INJETAVEL, ORAL, TOPICO
   fabricante          varchar2(100),
   registro_mapa       varchar2(50),
    
    -- Controle de Estoque
   estoque_atual       number(10,2) default 0,
   estoque_minimo      number(10,2) default 0,
   unidade_medida      varchar2(20) not null, -- ML, G, COMPRIMIDO, DOSE
    
    -- Validade e Lote
   lote_atual          varchar2(50),
   data_validade       date,
   data_fabricacao     date,
    
    -- Custos
   preco_unitario      number(10,2),
   fornecedor          varchar2(100),
    
    -- Prescrição
   requer_receita      char(1) default 'N' check ( requer_receita in ( 'S',
                                                                  'N' ) ),
   periodo_carencia    number(3), -- dias para abate

   observacoes         clob,
   ativo               char(1) default 'S' check ( ativo in ( 'S',
                                                'N' ) ),
   id_usuario_cadastro number
      references usuarios ( id ),
   data_cadastro       date default sysdate
);

create table movimentacao_medicamentos (
   id                  number
      generated always as identity
   primary key,
   id_medicamento      number not null
      references medicamentos ( id ),
   tipo_movimentacao   varchar2(20) not null, -- ENTRADA, SAIDA, AJUSTE
   quantidade          number(10,2) not null,
   quantidade_anterior number(10,2),
   quantidade_atual    number(10,2),
    
    -- Referência para saída (aplicação em animal)
   id_animal           number
      references animais ( id ),
   id_saude_animal     number
      references saude_animais ( id ),
    
    -- Dados da entrada (compra)
   nota_fiscal         varchar2(100),
   fornecedor          varchar2(100),
   preco_unitario      number(10,2),
   lote                varchar2(50),
   data_validade       date,
   motivo              varchar2(200),
   observacoes         clob,
   id_usuario_registro number
      references usuarios ( id ),
   data_registro       date default sysdate
);


create table terrenos (
   id                  number
      generated always as identity
   primary key,
   nome                varchar2(100) not null,
   area_hectares       number(8,4) not null,
   tipo_solo           varchar2(50),
   topografia          varchar2(50),
   tipo_pastagem       varchar2(100),
   capacidade_animais  number(3),
   latitude            number(9,6) not null,
   longitude           number(9,6) not null,
   status_terreno      varchar2(20) default 'DISPONIVEL',
   observacoes         clob,
   id_usuario_cadastro number
      references usuarios ( id ),
   data_cadastro       date default sysdate
);


create table historico_crescimento (
   id                      number
      generated always as identity
   primary key,
   id_animal               number not null
      references animais ( id ),
   data_medicao            date not null,
   peso                    number(6,2),
   altura                  number(5,2),
   circunferencia_canela   number(5,2),
   circunferencia_toracica number(5,2),
   comprimento_corpo       number(5,2),
   observacoes             varchar2(500),
   id_usuario_registro     number
      references usuarios ( id ),
   data_registro           date default sysdate
);

create table movimentacoes_animais (
   id                  number
      generated always as identity
   primary key,
   id_animal           number not null
      references animais ( id ),
   tipo_movimentacao   varchar2(50) not null,
   data_movimentacao   date not null,
   id_terreno_origem   number
      references terrenos ( id ), -- FK em vez de texto
   id_terreno_destino  number
      references terrenos ( id ), -- FK em vez de texto
   origem_externa      varchar2(100), -- Para origens fora da fazenda
   destino_externo     varchar2(100), -- Para destinos fora da fazenda 
   motivo              varchar2(200),
   observacoes         clob,
   id_usuario_registro number
      references usuarios ( id ),
   data_registro       date default sysdate, -- Constraint para garantir origem ou destino 
   constraint chk_movimentacao_origem
      check ( id_terreno_origem is not null
          or origem_externa is not null ),
   constraint chk_movimentacao_destino
      check ( id_terreno_destino is not null
          or destino_externo is not null )
);

create table reproducao (
   id                    number
      generated always as identity
   primary key,
   id_egua               number not null
      references animais ( id ),
   id_parceiro           number
      references animais ( id ),
   tipo_cobertura        varchar2(20) check ( tipo_cobertura in ( 'NATURAL',
                                                           'IA',
                                                           'TE' ) ),
   data_cobertura        date not null,
   data_diagnostico      date,
   resultado_diagnostico varchar2(20) check ( resultado_diagnostico in ( 'POSITIVO',
                                                                         'NEGATIVO',
                                                                         'PENDENTE' ) ),
   data_parto_prevista   date,
   data_parto_real       date,
   observacoes           clob,
   status_reproducao     varchar2(20) default 'ATIVO' check ( status_reproducao in ( 'ATIVO',
                                                                                 'CONCLUIDO',
                                                                                 'FALHADO' ) ), -- Ativo, Concluído, Falhado
   id_usuario_registro   number
      references usuarios ( id ),
   data_registro         date default sysdate,
    
    -- Validações importantes
   constraint chk_datas_logicas
      check ( data_diagnostico >= data_cobertura
         and ( data_parto_prevista is null
          or data_parto_prevista >= data_cobertura )
         and ( data_parto_real is null
          or data_parto_real >= data_cobertura ) )
);

create table saude_animais (
   id                      number
      generated always as identity
   primary key,
   id_animal               number not null
      references animais ( id ),
   tipo_registro           varchar2(50) not null,
   data_ocorrencia         date not null,
   descricao               varchar2(1000), -- Aumentar limite 
   veterinario_responsavel varchar2(200),
   medicamento_aplicado    varchar2(500),
   dose_aplicada           varchar2(100),
   proxima_aplicacao       date, -- Para vacinas/vermífugos 
   custo                   number(10,2),
   observacoes             clob,
   id_usuario_registro     number
      references usuarios ( id ),
   data_registro           date default sysdate,
   id_medicamento          number
      references medicamentos ( id ),
   quantidade_aplicada     number(10,2),
   unidade_aplicada        varchar2(20),
   tipo_ferradura          varchar2(100),  -- Tipo de ferradura aplicada
   membro_tratado          varchar2(50),   -- AD, AE, PD, PE, TODOS
   problema_detectado      varchar2(500),  -- Problemas encontrados no casco
   tecnica_aplicada        varchar2(200),  -- Técnica utilizada
   ferrador_responsavel    varchar2(200), -- Nome do ferrador terceirizado
   status_casco            varchar2(100),  -- Estado geral do casco
   proxima_avaliacao       date,            -- Data sugerida para próxima avaliação
   constraint chk_membro_tratado
      check ( membro_tratado in ( 'AD',
                                  'AE',
                                  'PD',
                                  'PE',
                                  'TODOS' ) ),
   constraint chk_status_casco
      check ( status_casco in ( 'BOM',
                                'REGULAR',
                                'RUIM',
                                'PROBLEMA' ) )
);

alter table saude_animais
   add constraint chk_status_casco
      check ( status_casco in ( 'BOM',
                                'REGULAR',
                                'RUIM',
                                'PROBLEMA' ) );

create table produtos_manejo (
   id                      number
      generated always as identity
   primary key,
   nome                    varchar2(100) not null,
   tipo_produto            varchar2(50) not null, -- FERTILIZANTE, DEFENSIVO, CORRETIVO
   principio_ativo         varchar2(200),
   concentracao            varchar2(50),
   unidade_medida          varchar2(20) not null, -- KG, L, SC (SACA)
   fabricante              varchar2(100),
   registro_ministerio     varchar2(50),
   estoque_atual           number(12,3) default 0 not null,
   estoque_minimo          number(12,3) default 0 not null,
   estoque_maximo          number(12,3),
   preco_unitario          number(12,2),
   fornecedor_principal    varchar2(100),
   codigo_fornecedor       varchar2(50),
   lote_atual              varchar2(50),
   data_validade           date,
   data_ultima_compra      date,
   dose_recomendada        number(8,3),
   periodo_carencia        number(3),
   requer_receituario      char(1) default 'N' check ( requer_receituario in ( 'S',
                                                                          'N' ) ),
   local_armazenamento     varchar2(100),
   condicoes_armazenamento varchar2(200),
   observacoes             clob,
   ativo                   char(1) default 'S' check ( ativo in ( 'S',
                                                'N' ) ),
   id_usuario_cadastro     number
      references usuarios ( id ),
   data_cadastro           date default sysdate
);


create table movimentacao_produtos_manejo (
   id                  number
      generated always as identity
   primary key,
   id_produto          number not null
      references produtos_manejo ( id ),
   tipo_movimentacao   varchar2(20) not null check ( tipo_movimentacao in ( 'ENTRADA',
                                                                          'SAIDA',
                                                                          'AJUSTE' ) ),
    -- Quantidades
   quantidade          number(12,3) not null,
   quantidade_anterior number(12,3),
   quantidade_atual    number(12,3),
    -- Referência para aplicação (saída)
   id_manejo_terreno   number
      references manejo_terrenos ( id ),
   id_terreno          number
      references terrenos ( id ),
    -- Dados da entrada (compra)
   nota_fiscal         varchar2(100),
   fornecedor          varchar2(100),
   preco_unitario      number(12,2),
   lote                varchar2(50),
   data_validade       date,
   data_fabricacao     date,
    -- Observações
   motivo              varchar2(200),
   observacoes         clob,
   id_usuario_registro number
      references usuarios ( id ),
   data_registro       date default sysdate
);


create table manejo_terrenos (
   id                    number
      generated always as identity
   primary key,
   id_terreno            number not null
      references terrenos ( id ),
   tipo_manejo           varchar2(50) not null,
   data_aplicacao        date not null,
   id_produto            number not null
      references produtos_manejo ( id ),
   quantidade            number(10,3),
   unidade_medida        varchar2(20),
   observacoes           clob,
   dose_hectare          float,
   area_aplicada         float,
   custo_total           float,
   equipamento_utilizado varchar2(100),
   condicoes_climaticas  varchar2(100),
   id_usuario_registro   number
      references usuarios ( id ),
   data_registro         date default sysdate,
   periodo_carencia      number(3), -- dias sem animais
   data_liberacao        date, -- calculado automaticamente    
   custo_produto         number(12,2),
   custo_aplicacao       number(12,2),
   periodo_carencia      number(3), -- DIAS SEM ANIMAIS
   data_liberacao        date -- CALCULADO AUTOMATICAMENTE

);

create table audit_log (
   id               number
      generated always as identity
   primary key,
   tabela           varchar2(50) not null,
   id_registro      number not null,
   operacao         varchar2(10) not null,
   dados_anteriores clob,
   dados_novos      clob,
   id_usuario       number
      references usuarios ( id )
   not null,
   data_operacao    date default sysdate,
   ip_usuario       varchar2(15)
);


create table sessoes (
   id                 number
      generated always as identity
   primary key,
   id_usuario         number not null
      references usuarios ( id ),
   token_sessao       varchar2(500) not null unique,
   ip_origem          varchar2(45), -- Suporte IPv6
   user_agent         varchar2(500),
   data_criacao       date default sysdate,
   data_expiracao     date not null,
   ativa              char(1) default 'S' check ( ativa in ( 'S',
                                                'N' ) ),
   data_ultimo_acesso date default sysdate
);

create table config_mfa (
   id            number
      generated always as identity
   primary key,
   id_usuario    number not null
      references usuarios ( id ),
   segredo_totp  varchar2(100) not null,
   ativo         char(1) default 'S' check ( ativo in ( 'S',
                                                'N' ) ),
   data_cadastro date default sysdate
);

create table embeddings (
   id           number
      generated always as identity
   primary key,
   tabela       varchar2(50) not null,
   id_registro  number not null,
   vetor        clob, -- Armazena vetor como JSON
   data_criacao date default sysdate
);

create table analises_solo (
   id                  number
      generated always as identity
   primary key,
   id_terreno          number not null
      references terrenos ( id ),
   data_coleta         date not null,
   data_resultado      date,
   laboratorio         varchar2(100),
   ph_agua             number(3,1),
   ph_cacl2            number(3,1),
   materia_organica    number(4,2), -- %
   fosforo             number(6,2), -- MG/DM³
   potassio            number(6,2), -- CMOLC/DM³
   calcio              number(6,2), -- CMOLC/DM³
   magnesio            number(6,2), -- CMOLC/DM³
   aluminio            number(6,2), -- CMOLC/DM³
   h_al                number(6,2), -- CMOLC/DM³ (H+AL)
   ctc                 number(6,2), -- CMOLC/DM³
   saturacao_bases     number(4,1), -- %
   saturacao_aluminio  number(4,1), -- %
   enxofre             number(6,2), -- MG/DM³
   boro                number(6,2), -- MG/DM³
   cobre               number(6,2), -- MG/DM³
   ferro               number(6,2), -- MG/DM³
   manganes            number(6,2), -- MG/DM³
   zinco               number(6,2), -- MG/DM³
   observacoes         clob,
   recomendacoes       clob,
   arquivo_laudo       varchar2(500), -- PATH DO PDF
   id_usuario_cadastro number
      references usuarios ( id ),
   data_cadastro       date default sysdate
);

-- ========================================
-- MÓDULO DE RAÇÃO E SUPLEMENTOS
-- ========================================

-- Tabela principal de produtos de nutrição
create table produtos_racao (
   id                      number
      generated always as identity
   primary key,
   nome                    varchar2(100) not null,
   tipo_alimento           varchar2(30) not null check ( tipo_alimento in ( 'CONCENTRADO',
                                                                  'VOLUMOSO',
                                                                  'SUPLEMENTO',
                                                                  'PREMIX',
                                                                  'SAL_MINERAL' ) ),
   marca                   varchar2(100),
   fabricante              varchar2(100),
    
    -- Composição nutricional
   proteina_bruta          number(5,2), -- %
   fibra_bruta             number(5,2), -- %
   energia_digestivel      number(6,2), -- Mcal/kg
   calcio                  number(5,3), -- %
   fosforo                 number(5,3), -- %
   magnesio                number(5,3), -- %
   potassio                number(5,3), -- %
   sodio                   number(5,3), -- %
    
    -- Controle de estoque
   estoque_atual           number(12,3) default 0,
   estoque_minimo          number(12,3) default 0,
   estoque_maximo          number(12,3),
   unidade_medida          varchar2(20) default 'KG',
    
    -- Dados comerciais
   preco_unitario          number(12,2),
   fornecedor_principal    varchar2(100),
   codigo_fornecedor       varchar2(50),
    
    -- Controle de qualidade
   lote_atual              varchar2(50),
   data_fabricacao         date,
   data_validade           date,
   registro_ministerio     varchar2(50),
    
    -- Armazenamento
   local_armazenamento     varchar2(100),
   condicoes_armazenamento varchar2(200), -- Temperatura, umidade

   observacoes             clob,
   ativo                   char(1) default 'S' check ( ativo in ( 'S',
                                                'N' ) ),
   id_usuario_cadastro     number
      references usuarios ( id ),
   data_cadastro           date default sysdate,
   data_ultima_compra      date
);

-- Movimentação de estoque (entrada/saída)
create table movimentacao_produtos_racao (
   id                     number
      generated always as identity
   primary key,
   id_produto             number not null
      references produtos_racao ( id ),
   tipo_movimentacao      varchar2(20) not null check ( tipo_movimentacao in ( 'ENTRADA',
                                                                          'SAIDA',
                                                                          'AJUSTE' ) ),
    
    -- Quantidades
   quantidade             number(12,3) not null,
   quantidade_anterior    number(12,3),
   quantidade_atual       number(12,3),
    
    -- Referência para saída (fornecimento)
   id_fornecimento_animal number,
   id_animal              number
      references animais ( id ),
    
    -- Dados da entrada (compra)
   nota_fiscal            varchar2(100),
   fornecedor             varchar2(100),
   preco_unitario         number(12,2),
   lote                   varchar2(50),
   data_validade          date,
   data_fabricacao        date,
    
    -- Observações
   motivo                 varchar2(200),
   observacoes            clob,
   id_usuario_registro    number
      references usuarios ( id ),
   data_registro          date default sysdate
);

-- Planos alimentares por animal
create table planos_alimentares (
   id                      number
      generated always as identity
   primary key,
   id_animal               number not null
      references animais ( id ),
    
    -- Categoria nutricional
   categoria_nutricional   varchar2(30) not null check ( categoria_nutricional in ( 'POTRO',
                                                                                  'JOVEM',
                                                                                  'ADULTO_MANUTENCAO',
                                                                                  'ADULTO_TRABALHO_LEVE',
                                                                                  'ADULTO_TRABALHO_MODERADO',
                                                                                  'ADULTO_TRABALHO_INTENSO',
                                                                                  'EGUA_GESTANTE',
                                                                                  'EGUA_LACTANTE',
                                                                                  'REPRODUTOR',
                                                                                  'IDOSO' ) ),
    
    -- Dados do animal no momento do plano
   peso_referencia         number(6,2) not null,
   escore_corporal         number(2,1) check ( escore_corporal between 1 and 9 ),
   intensidade_trabalho    varchar2(20) check ( intensidade_trabalho in ( 'REPOUSO',
                                                                       'LEVE',
                                                                       'MODERADO',
                                                                       'INTENSO' ) ),
    
    -- Parâmetros do plano
   quantidade_diaria_total number(6,3), -- kg/dia
   numero_refeicoes        number(2) default 3,
   percentual_peso_vivo    number(4,2), -- % do peso vivo
    
    -- Período de vigência
   data_inicio             date not null,
   data_fim                date,
    
    -- Status
   status_plano            varchar2(20) default 'ATIVO' check ( status_plano in ( 'ATIVO',
                                                                       'INATIVO',
                                                                       'SUSPENSO' ) ),
   observacoes             clob,
   id_usuario_cadastro     number
      references usuarios ( id ),
   data_cadastro           date default sysdate,
    
    -- Constraint para datas
   constraint chk_periodo_plano
      check ( data_fim is null
          or data_fim >= data_inicio )
);

-- Itens do plano alimentar (produtos específicos)
create table itens_plano_alimentar (
   id                      number
      generated always as identity
   primary key,
   id_plano                number not null
      references planos_alimentares ( id ),
   id_produto              number not null
      references produtos_racao ( id ),
    
    -- Quantidades
   quantidade_por_refeicao number(6,3) not null,
   quantidade_diaria       number(6,3) not null,
   ordem_fornecimento      number(2), -- Para controlar sequência
    
    -- Horários (opcional)
   horario_refeicao_1      varchar2(5), -- HH:MM
   horario_refeicao_2      varchar2(5),
   horario_refeicao_3      varchar2(5),
   horario_refeicao_4      varchar2(5),
   observacoes             varchar2(500),
   ativo                   char(1) default 'S' check ( ativo in ( 'S',
                                                'N' ) )
);

-- Registro de fornecimento individual por animal
create table fornecimento_racao_animal (
   id                      number
      generated always as identity
   primary key,
   id_animal               number not null
      references animais ( id ),
   id_produto              number not null
      references produtos_racao ( id ),
   id_plano                number
      references planos_alimentares ( id ),
    
    -- Dados do fornecimento
   data_fornecimento       date not null,
   horario_fornecimento    varchar2(5), -- HH:MM
   numero_refeicao         number(1) check ( numero_refeicao between 1 and 4 ),
    
    -- Quantidades
   quantidade_planejada    number(6,3),
   quantidade_fornecida    number(6,3) not null,
   peso_animal_referencia  number(6,2), -- Peso no momento do fornecimento
    
    -- Controle
   funcionario_responsavel varchar2(100),
   observacoes             varchar2(500),
   id_usuario_registro     number
      references usuarios ( id ),
   data_registro           date default sysdate
);

-- ========================================
-- Comments
-- ========================================
comment on column produtos_manejo.tipo_produto is
   'FERTILIZANTE, DEFENSIVO, CORRETIVO, SEMENTE';
comment on column analises_solo.ph_agua is
   'pH em água - faixa ideal 6.0-7.0';
comment on column analises_solo.materia_organica is
   'Matéria orgânica em % - ideal > 2.5%';
comment on column analises_solo.saturacao_bases is
   'Saturação por bases em % - ideal > 60%';
comment on column manejo_terrenos.periodo_carencia is
   'Dias que os animais devem ficar fora do terreno';
comment on column manejo_terrenos.data_liberacao is
   'Data calculada automaticamente para liberação do terreno';
comment on column movimentacao_produtos_manejo.tipo_movimentacao is
   'ENTRADA=Compra, SAIDA=Aplicação, AJUSTE=Correção';
comment on column movimentacao_produtos_manejo.quantidade is
   'Quantidade movimentada';
comment on column movimentacao_produtos_manejo.quantidade_anterior is
   'Estoque antes da movimentação';
comment on column movimentacao_produtos_manejo.quantidade_atual is
   'Estoque após a movimentação';
comment on column produtos_manejo.estoque_atual is
   'Quantidade atual em estoque';
comment on column produtos_manejo.estoque_minimo is
   'Quantidade mínima para alerta de reposição';
comment on column produtos_manejo.estoque_maximo is
   'Limite máximo de armazenamento';
comment on column produtos_manejo.dose_recomendada is
   'Dose padrão por hectare';
comment on column produtos_manejo.periodo_carencia is
   'Dias para liberação do terreno após aplicação';
comment on column produtos_manejo.requer_receituario is
   'S=Sim, N=Não - Para defensivos controlados';
comment on column saude_animais.id_medicamento is
   'Referência ao medicamento aplicado';
comment on column saude_animais.quantidade_aplicada is
   'Quantidade do medicamento aplicada';
comment on column saude_animais.unidade_aplicada is
   'Unidade da quantidade aplicada';
comment on column animais.proprietario is
   'Nome do proprietário do animal';
comment on column animais.contato_proprietario is
   'Telefone/email do proprietário';
comment on column animais.cpf_cnpj_proprietario is
   'CPF ou CNPJ do proprietário';
comment on column saude_animais.tipo_ferradura is
   'Tipo de ferradura: Comum, Ortopédica, Alumínio, Borracha, Colagem, Descalço';
comment on column saude_animais.membro_tratado is
   'Membro(s) tratado(s): AD=Anterior Direito, AE=Anterior Esquerdo, PD=Posterior Direito, PE=Posterior Esquerdo, TODOS=Todos os membros'
   ;
comment on column saude_animais.problema_detectado is
   'Problemas detectados: rachadura, laminite, sensibilidade, etc.';
comment on column saude_animais.tecnica_aplicada is
   'Técnica de ferrageamento aplicada';
comment on column saude_animais.ferrador_responsavel is
   'Nome do ferrador terceirizado responsável';
comment on column saude_animais.status_casco is
   'Estado do casco: BOM, REGULAR, RUIM, PROBLEMA';
comment on column saude_animais.proxima_avaliacao is
   'Data sugerida para próxima avaliação do casco';
comment on table produtos_racao is
   'Cadastro de produtos para nutrição animal (rações, suplementos, etc.)';
comment on table movimentacao_produtos_racao is
   'Controle de entrada e saída de produtos no estoque';
comment on table planos_alimentares is
   'Planos nutricionais individuais por animal';
comment on table itens_plano_alimentar is
   'Produtos específicos de cada plano alimentar';
comment on table fornecimento_racao_animal is
   'Registro de fornecimento individual de ração por refeição';
comment on column produtos_racao.proteina_bruta is
   'Percentual de proteína bruta do produto';
comment on column produtos_racao.energia_digestivel is
   'Energia digestível em Mcal/kg';
comment on column planos_alimentares.percentual_peso_vivo is
   'Quantidade diária como percentual do peso vivo';
comment on column fornecimento_racao_animal.peso_animal_referencia is
   'Peso do animal no momento do fornecimento';
-- ========================================
-- Indexes
-- ========================================

create index idx_medicamentos_nome on
   medicamentos (
      nome
   );
create index idx_medicamentos_estoque on
   medicamentos (
      estoque_atual,
      estoque_minimo
   );
create index idx_movimentacao_medicamento on
   movimentacao_medicamentos (
      id_medicamento,
      data_registro
   );
create index idx_movimentacao_animal on
   movimentacao_medicamentos (
      id_animal
   );
create index idx_saude_medicamento on
   saude_animais (
      id_medicamento
   );

create index idx_mov_produto_data on
   movimentacao_produtos_manejo (
      id_produto,
      data_registro
   );
create index idx_mov_tipo on
   movimentacao_produtos_manejo (
      tipo_movimentacao,
      data_registro
   );
create index idx_produtos_estoque_min on
   produtos_manejo (
      estoque_atual,
      estoque_minimo
   );
create index idx_produtos_validade on
   produtos_manejo (
      data_validade
   );

create index idx_analises_terreno_data on
   analises_solo (
      id_terreno,
      data_coleta
   );
create index idx_manejo_terreno_data on
   manejo_terrenos (
      id_terreno,
      data_aplicacao
   );
create index idx_manejo_liberacao on
   manejo_terrenos (
      data_liberacao
   );

create index idx_sessoes_usuario_ativa on
   sessoes (
      id_usuario,
      ativa
   );
create index idx_movimentacoes_animal_data on
   movimentacoes_animais (
      id_animal,
      data_movimentacao
   );
create index idx_historico_animal_data on
   historico_crescimento (
      id_animal,
      data_medicao
   );
create index idx_reproducao_egua on
   reproducao (
      id_egua
   );
create index idx_saude_animal_data on
   saude_animais (
      id_animal,
      data_ocorrencia
   );
create index idx_audit_tabela_data on
   audit_log (
      tabela,
      data_operacao
   );

create index idx_produtos_racao_nome on
   produtos_racao (
      nome
   );
create index idx_produtos_racao_tipo on
   produtos_racao (
      tipo_alimento
   );
create index idx_produtos_racao_estoque on
   produtos_racao (
      estoque_atual,
      estoque_minimo
   );
create index idx_produtos_racao_validade on
   produtos_racao (
      data_validade
   );

create index idx_mov_racao_produto_data on
   movimentacao_produtos_racao (
      id_produto,
      data_registro
   );
create index idx_mov_racao_tipo on
   movimentacao_produtos_racao (
      tipo_movimentacao,
      data_registro
   );
create index idx_mov_racao_animal on
   movimentacao_produtos_racao (
      id_animal
   );

create index idx_planos_animal_status on
   planos_alimentares (
      id_animal,
      status_plano
   );
create index idx_planos_categoria on
   planos_alimentares (
      categoria_nutricional
   );
create index idx_planos_vigencia on
   planos_alimentares (
      data_inicio,
      data_fim
   );

create index idx_fornecimento_animal_data on
   fornecimento_racao_animal (
      id_animal,
      data_fornecimento
   );
create index idx_fornecimento_produto on
   fornecimento_racao_animal (
      id_produto,
      data_fornecimento
   );

-- ========================================
-- Triggers
-- ========================================

-- TRIGGER PARA CONTROLE AUTOMÁTICO DE ESTOQUE
create or replace trigger trg_movimentacao_estoque_manejo before
   insert on movimentacao_produtos_manejo
   for each row
declare
   v_estoque_atual number(
      12,
      3
   );
begin
    -- Buscar estoque atual
   select estoque_atual
     into v_estoque_atual
     from produtos_manejo
    where id = :new.id_produto;
    
    -- Armazenar quantidade anterior
   :new.quantidade_anterior := v_estoque_atual;
    
    -- Calcular nova quantidade
   if :new.tipo_movimentacao = 'ENTRADA' then
      :new.quantidade_atual := v_estoque_atual + :new.quantidade;
   elsif :new.tipo_movimentacao = 'SAIDA' then
      :new.quantidade_atual := v_estoque_atual - :new.quantidade;
        -- Validar se há estoque suficiente
      if :new.quantidade_atual < 0 then
         raise_application_error(
            -20001,
            'Estoque insuficiente. Disponível: ' || v_estoque_atual
         );
      end if;
   elsif :new.tipo_movimentacao = 'AJUSTE' then
      :new.quantidade_atual := :new.quantidade;
   end if;
    
    -- Atualizar estoque na tabela principal
   update produtos_manejo
      set estoque_atual = :new.quantidade_atual,
          data_ultima_compra =
             case
                when :new.tipo_movimentacao = 'ENTRADA' then
                   sysdate
                else
                   data_ultima_compra
             end
    where id = :new.id_produto;
end;


-- TRIGGER PARA ATUALIZAR ESTOQUE QUANDO HOUVER APLICAÇÃO EM TERRENO
create or replace trigger trg_manejo_terreno_estoque after
   insert on manejo_terrenos
   for each row
begin
    -- Criar movimentação de saída automaticamente
   insert into movimentacao_produtos_manejo (
      id_produto,
      tipo_movimentacao,
      quantidade,
      id_manejo_terreno,
      id_terreno,
      motivo,
      id_usuario_registro
   ) values ( :new.id_produto,
              'SAIDA',
              :new.quantidade,
              :new.id,
              :new.id_terreno,
              'Aplicação em terreno - ' || :new.tipo_manejo,
              :new.id_usuario_registro );
end;

-- Trigger para baixa automática no estoque
create or replace trigger trg_saude_baixa_estoque after
   insert on saude_animais
   for each row
begin
    -- Se foi especificado um medicamento e quantidade
   if
      :new.id_medicamento is not null
      and :new.quantidade_aplicada is not null
   then
        -- Registrar saída no estoque
      insert into movimentacao_medicamentos (
         id_medicamento,
         tipo_movimentacao,
         quantidade,
         id_animal,
         id_saude_animal,
         motivo,
         id_usuario_registro
      ) values ( :new.id_medicamento,
                 'SAIDA',
                 :new.quantidade_aplicada,
                 :new.id_animal,
                 :new.id,
                 'Aplicação em animal - ' || :new.tipo_registro,
                 :new.id_usuario_registro );
   end if;
end;


-- Trigger para atualizar estoque automaticamente
create or replace trigger trg_movimentacao_estoque before
   insert on movimentacao_medicamentos
   for each row
declare
   v_estoque_atual number(
      10,
      2
   );
begin
    -- Buscar estoque atual
   select estoque_atual
     into v_estoque_atual
     from medicamentos
    where id = :new.id_medicamento;
    
    -- Armazenar quantidade anterior
   :new.quantidade_anterior := v_estoque_atual;
    
    -- Calcular nova quantidade
   if :new.tipo_movimentacao = 'ENTRADA' then
      :new.quantidade_atual := v_estoque_atual + :new.quantidade;
   elsif :new.tipo_movimentacao = 'SAIDA' then
      :new.quantidade_atual := v_estoque_atual - :new.quantidade;
   elsif :new.tipo_movimentacao = 'AJUSTE' then
      :new.quantidade_atual := :new.quantidade; -- Quantidade é o valor final
      :new.quantidade := :new.quantidade - v_estoque_atual; -- Diferença
   end if;
    
    -- Atualizar estoque na tabela medicamentos
   update medicamentos
      set estoque_atual = :new.quantidade_atual,
          lote_atual = coalesce(
             :new.lote,
             lote_atual
          ),
          data_validade = coalesce(
             :new.data_validade,
             data_validade
          )
    where id = :new.id_medicamento;
end;

-- Trigger para calcular data de liberação automaticamente
create or replace trigger trg_manejo_data_liberacao before
   insert or update on manejo_terrenos
   for each row
begin
   if
      :new.periodo_carencia is not null
      and :new.data_aplicacao is not null
   then
      :new.data_liberacao := :new.data_aplicacao + :new.periodo_carencia;
   end if;
end;

-- Trigger para calcular automaticamente a próxima avaliação
create or replace trigger trg_calcular_proxima_casco before
   insert or update on saude_animais
   for each row
   when ( new.tipo_registro in ( 'FERRAGEAMENTO',
                                 'CASQUEAMENTO',
                                 'FERRAGEAMENTO_CORRETIVO',
                                 'CASQUEAMENTO_TERAPEUTICO' ) )
begin
    -- Calcular próxima avaliação se não foi informada
   if :new.proxima_avaliacao is null then
      :new.proxima_avaliacao := calcular_proxima_data_casco(
         :new.tipo_registro,
         :new.data_ocorrencia,
         'GERAL' -- Modalidade padrão, pode ser personalizada no futuro
      );
   end if;
end;

-- Trigger para controle automático de estoque
create or replace trigger trg_movimentacao_estoque_racao before
   insert on movimentacao_produtos_racao
   for each row
declare
   v_estoque_atual number(
      12,
      3
   );
begin
    -- Buscar estoque atual
   select estoque_atual
     into v_estoque_atual
     from produtos_racao
    where id = :new.id_produto;
    
    -- Armazenar quantidade anterior
   :new.quantidade_anterior := v_estoque_atual;
    
    -- Calcular nova quantidade
   if :new.tipo_movimentacao = 'ENTRADA' then
      :new.quantidade_atual := v_estoque_atual + :new.quantidade;
   elsif :new.tipo_movimentacao = 'SAIDA' then
      :new.quantidade_atual := v_estoque_atual - :new.quantidade;
        -- Validar se há estoque suficiente
      if :new.quantidade_atual < 0 then
         raise_application_error(
            -20001,
            'Estoque insuficiente. Disponível: ' || v_estoque_atual
         );
      end if;
   elsif :new.tipo_movimentacao = 'AJUSTE' then
      :new.quantidade_atual := :new.quantidade;
   end if;
    
    -- Atualizar estoque na tabela principal
   update produtos_racao
      set estoque_atual = :new.quantidade_atual,
          data_ultima_compra =
             case
                when :new.tipo_movimentacao = 'ENTRADA' then
                   sysdate
                else
                   data_ultima_compra
             end
    where id = :new.id_produto;
end;

-- Trigger para baixa automática no estoque quando fornecido
create or replace trigger trg_fornecimento_baixa_estoque after
   insert on fornecimento_racao_animal
   for each row
begin
    -- Criar movimentação de saída automaticamente
   insert into movimentacao_produtos_racao (
      id_produto,
      tipo_movimentacao,
      quantidade,
      id_fornecimento_animal,
      id_animal,
      motivo,
      id_usuario_registro
   ) values ( :new.id_produto,
              'SAIDA',
              :new.quantidade_fornecida,
              :new.id,
              :new.id_animal,
              'Fornecimento para animal - Refeição ' || :new.numero_refeicao,
              :new.id_usuario_registro );
end;

-- Trigger para atualizar referência de fornecimento na movimentação
create or replace trigger trg_update_fornecimento_ref after
   insert on movimentacao_produtos_racao
   for each row
begin
    -- Se foi criado por fornecimento, atualizar referência
   if :new.id_fornecimento_animal is not null then
      update movimentacao_produtos_racao
         set
         id_fornecimento_animal = :new.id_fornecimento_animal
       where id = :new.id;
   end if;
end;

-- ========================================
-- Views
-- ========================================
-- VIEWS PARA PRODUTOS COM ESTOQUE BAIXO
create or replace view vw_produtos_estoque_baixo as
   select p.id,
          p.nome,
          p.tipo_produto,
          p.estoque_atual,
          p.estoque_minimo,
          p.unidade_medida,
          p.fornecedor_principal,
          p.data_validade,
          case
             when p.estoque_atual = 0                 then
                'SEM_ESTOQUE'
             when p.estoque_atual <= p.estoque_minimo then
                'ESTOQUE_BAIXO'
             when p.data_validade is not null
                and p.data_validade <= sysdate + 30 then
                'VENCIMENTO_PROXIMO'
             else
                'OK'
          end as status_alerta,
          case
             when p.data_validade is not null then
                greatest(
                   0,
                   trunc(trunc(p.data_validade) - trunc(sysdate))
                )
             else
                null
          end as dias_vencimento
     from produtos_manejo p
    where p.ativo = 'S'
      and ( p.estoque_atual <= p.estoque_minimo
       or ( p.data_validade is not null
      and trunc(p.data_validade) <= trunc(sysdate + 30) ) )
    order by
      case
         when p.estoque_atual = 0                 then
            1
         when p.estoque_atual <= p.estoque_minimo then
            2
         when p.data_validade is not null
            and trunc(p.data_validade) <= trunc(sysdate) + 30 then
            3
         else
            4
      end,
      p.estoque_atual;

-- VIEW PARA MOVIMENTAÇÃO DE ESTOQUE (RELATÓRIOS)
create or replace view vw_movimentacao_estoque_resumo as
   select p.id as produto_id,
          p.nome as produto_nome,
          p.tipo_produto,
          p.estoque_atual,
          p.estoque_minimo,
          p.unidade_medida,
          nvl(
             entradas.total_entradas,
             0
          ) as total_entradas,
          nvl(
             saidas.total_saidas,
             0
          ) as total_saidas,
          nvl(
             entradas.valor_entradas,
             0
          ) as valor_entradas,
          movs.ultima_movimentacao
     from produtos_manejo p
     left join (
      select id_produto,
             sum(quantidade) as total_entradas,
             sum(quantidade * nvl(
                preco_unitario,
                0
             )) as valor_entradas
        from movimentacao_produtos_manejo
       where tipo_movimentacao = 'ENTRADA'
       group by id_produto
   ) entradas
   on p.id = entradas.id_produto
     left join (
      select id_produto,
             sum(quantidade) as total_saidas
        from movimentacao_produtos_manejo
       where tipo_movimentacao = 'SAIDA'
       group by id_produto
   ) saidas
   on p.id = saidas.id_produto
     left join (
      select id_produto,
             max(data_registro) as ultima_movimentacao
        from movimentacao_produtos_manejo
       group by id_produto
   ) movs
   on p.id = movs.id_produto
    where p.ativo = 'S'
    order by p.nome;


-- View para medicamentos com estoque baixo
create or replace view vw_medicamentos_estoque_baixo as
   select m.id,
          m.nome,
          m.estoque_atual,
          m.estoque_minimo,
          m.unidade_medida,
          m.data_validade,
          case
             when trunc(m.data_validade) <= trunc(sysdate) + 30 then
                'VENCENDO'
             when trunc(m.data_validade) <= trunc(sysdate)      then
                'VENCIDO'
             when m.estoque_atual <= m.estoque_minimo           then
                'ESTOQUE_BAIXO'
             else
                'OK'
          end as status_alerta,
          case
             when trunc(m.data_validade) <= trunc(sysdate)      then
                trunc(sysdate) - trunc(m.data_validade)
             when trunc(m.data_validade) <= trunc(sysdate) + 30 then
                trunc(m.data_validade) - trunc(sysdate)
             else
                null
          end as dias_vencimento
     from medicamentos m
    where m.ativo = 'S'
      and ( m.estoque_atual <= m.estoque_minimo
       or trunc(m.data_validade) <= trunc(sysdate) + 30 );

-- View para relatórios de ferrageamento
create or replace view vw_ferrageamento_resumo as
   select a.id as animal_id,
          a.nome as animal_nome,
          a.numero_registro,
          sa.id as registro_id,
          sa.tipo_registro,
          sa.data_ocorrencia,
          sa.tipo_ferradura,
          sa.membro_tratado,
          sa.problema_detectado,
          sa.ferrador_responsavel,
          sa.status_casco,
          sa.proxima_avaliacao,
          sa.custo,
          sa.observacoes,
    -- Cálculo de dias até próxima avaliação
          case
             when sa.proxima_avaliacao is not null then
                trunc(sa.proxima_avaliacao) - trunc(sysdate)
             else
                null
          end as dias_proxima_avaliacao,
    -- Status de vencimento
          case
             when sa.proxima_avaliacao is null then
                'SEM_AGENDAMENTO'
             when trunc(sa.proxima_avaliacao) < trunc(sysdate)       then
                'VENCIDO'
             when trunc(sa.proxima_avaliacao) - trunc(sysdate) <= 7  then
                'VENCE_SEMANA'
             when trunc(sa.proxima_avaliacao) - trunc(sysdate) <= 15 then
                'VENCE_QUINZENA'
             else
                'EM_DIA'
          end as status_vencimento
     from animais a
     join saude_animais sa
   on a.id = sa.id_animal
    where sa.tipo_registro in ( 'FERRAGEAMENTO',
                                'CASQUEAMENTO',
                                'FERRAGEAMENTO_CORRETIVO',
                                'CASQUEAMENTO_TERAPEUTICO' )
    order by a.nome,
             sa.data_ocorrencia desc;

-- View para produtos com estoque baixo ou vencimento próximo
create or replace view vw_produtos_racao_alertas as
   select p.id,
          p.nome,
          p.tipo_alimento,
          p.estoque_atual,
          p.estoque_minimo,
          p.unidade_medida,
          p.fornecedor_principal,
          p.data_validade,
          p.lote_atual,
          case
             when p.estoque_atual = 0                 then
                'SEM_ESTOQUE'
             when p.estoque_atual <= p.estoque_minimo then
                'ESTOQUE_BAIXO'
             when p.data_validade is not null
                and trunc(p.data_validade) <= trunc(sysdate) + 30 then
                'VENCIMENTO_PROXIMO'
             when p.data_validade is not null
                and trunc(p.data_validade) <= trunc(sysdate) then
                'VENCIDO'
             else
                'OK'
          end as status_alerta,
          case
             when p.data_validade is not null then
                greatest(
                   0,
                   trunc(trunc(p.data_validade) - trunc(sysdate))
                )
             else
                null
          end as dias_vencimento
     from produtos_racao p
    where p.ativo = 'S'
      and ( p.estoque_atual <= p.estoque_minimo
       or ( p.data_validade is not null
      and trunc(p.data_validade) <= trunc(sysdate) + 30 ) )
    order by
      case
         when p.estoque_atual = 0                 then
            1
         when p.estoque_atual <= p.estoque_minimo then
            2
         when p.data_validade is not null
            and trunc(p.data_validade) <= trunc(sysdate) then
            3
         when p.data_validade is not null
            and trunc(p.data_validade) <= trunc(sysdate) + 30 then
            4
         else
            5
      end,
      p.estoque_atual;

-- View para resumo de consumo por animal
create or replace view vw_consumo_racao_animal as
   select a.id as animal_id,
          a.nome as animal_nome,
          a.numero_registro,
          p.id as produto_id,
          p.nome as produto_nome,
          p.tipo_alimento,
          count(f.id) as total_fornecimentos,
          sum(f.quantidade_fornecida) as total_consumido,
          avg(f.quantidade_fornecida) as media_por_fornecimento,
          sum(f.quantidade_fornecida * p.preco_unitario) as custo_total,
          min(f.data_fornecimento) as primeira_data,
          max(f.data_fornecimento) as ultima_data
     from animais a
     join fornecimento_racao_animal f
   on a.id = f.id_animal
     join produtos_racao p
   on f.id_produto = p.id
    where a.status_animal = 'ATIVO'
      and p.ativo = 'S'
    group by a.id,
             a.nome,
             a.numero_registro,
             p.id,
             p.nome,
             p.tipo_alimento;

-- View para planos alimentares ativos com detalhes
create or replace view vw_planos_alimentares_ativos as
   select pl.id as plano_id,
          a.id as animal_id,
          a.nome as animal_nome,
          a.numero_registro,
          pl.categoria_nutricional,
          pl.peso_referencia,
          pl.quantidade_diaria_total,
          pl.numero_refeicoes,
          pl.data_inicio,
          pl.data_fim,
    -- Contar itens do plano
          (
             select count(*)
               from itens_plano_alimentar ipl
              where ipl.id_plano = pl.id
                and ipl.ativo = 'S'
          ) as total_produtos,
    -- Custo estimado diário
          (
             select sum(ipl.quantidade_diaria * pr.preco_unitario)
               from itens_plano_alimentar ipl
               join produtos_racao pr
             on ipl.id_produto = pr.id
              where ipl.id_plano = pl.id
                and ipl.ativo = 'S'
          ) as custo_diario_estimado
     from planos_alimentares pl
     join animais a
   on pl.id_animal = a.id
    where pl.status_plano = 'ATIVO'
      and a.status_animal = 'ATIVO'
      and ( pl.data_fim is null
       or trunc(pl.data_fim) >= trunc(sysdate) );

-- ========================================
-- Functions
-- ========================================

-- Função para calcular próxima data de ferrageamento/casqueamento
create or replace function calcular_proxima_data_casco (
   p_tipo_registro varchar2,
   p_data_atual    date,
   p_modalidade    varchar2 default 'GERAL'
) return date is
   v_dias_intervalo number;
begin
    -- Definir intervalos baseados no tipo e modalidade
   case p_tipo_registro
      when 'FERRAGEAMENTO' then
         case p_modalidade
            when 'CCE' then
               v_dias_intervalo := 30;      -- Concurso Completo mais frequente
            when 'APARTACAO' then
               v_dias_intervalo := 60; -- Apartação menos frequente
            when 'CORRIDA' then
               v_dias_intervalo := 35;   -- Corrida intermediário
            else
               v_dias_intervalo := 45;                  -- Padrão geral
         end case;
      when 'CASQUEAMENTO' then
         v_dias_intervalo := 40; -- Casqueamento padrão
      when 'FERRAGEAMENTO_CORRETIVO' then
         v_dias_intervalo := 21; -- Correção mais frequente
      when 'CASQUEAMENTO_TERAPEUTICO' then
         v_dias_intervalo := 21; -- Terapêutico mais frequente
      else
         v_dias_intervalo := 45; -- Padrão
   end case;

   return p_data_atual + v_dias_intervalo;
end;