--TABELAS 
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
                                                        'N' ) ),
   peso_atual            number(6,2),           -- Peso mais recente
   foto_principal        varchar2(500)      -- URL da foto principal
);

create table animais (
   id                   number
      generated always as identity
   primary key,
   nome                 varchar2(100) not null,
   numero_registro      varchar2(50) unique,
   chip_identificacao   varchar2(50) unique,
   sexo                 char(1) check ( sexo in ( 'M',
                                  'F' ) ),
   data_nascimento      date,
   pelagem              varchar2(50),
   status_animal        varchar2(20) default 'ATIVO',
   id_pai               number
      references animais ( id ),
   id_mae               number
      references animais ( id ),
   origem               varchar2(100),
   id_usuario_cadastro  number
      references usuarios ( id ),
   data_cadastro        date default sysdate,
   id_usuario_alteracao number
      references usuarios ( id ),
   data_alteracao       date,
   observacoes          clob
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
   id                  number
      generated always as identity
   primary key,
   id_animal           number not null
      references animais ( id ),
   data_medicao        date not null,
   peso                number(6,2),
   altura              number(5,2),
   perimetro_toracico  number(5,2),
   comprimento_corpo   number(5,2),
   diametro_canela     number(5,2),
   observacoes         varchar2(500),
   id_usuario_registro number
      references usuarios ( id ),
   data_registro       date default sysdate
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
                                                                                 'FALHADO' ) ),
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
   data_registro           date default sysdate
);

create table produtos_manejo (
   id                  number
      generated always as identity
   primary key,
   nome                varchar2(100) not null,
   tipo_produto        varchar2(50) not null, -- FERTILIZANTE, DEFENSIVO, CORRETIVO
   principio_ativo     varchar2(200),
   concentracao        varchar2(50),
   unidade_medida      varchar2(20) not null, -- KG, L, SC (saca)
   fabricante          varchar2(100),
   registro_ministerio varchar2(50),
   observacoes         clob,
   ativo               char(1) default 'S' check ( ativo in ( 'S',
                                                'N' ) ),
   id_usuario_cadastro number
      references usuarios ( id ),
   data_cadastro       date default sysdate
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
   data_liberacao        date -- calculado automaticamente    
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
   fosforo             number(6,2), -- mg/dm³
   potassio            number(6,2), -- cmolc/dm³
   calcio              number(6,2), -- cmolc/dm³
   magnesio            number(6,2), -- cmolc/dm³
   aluminio            number(6,2), -- cmolc/dm³
   h_al                number(6,2), -- cmolc/dm³ (H+Al)
   ctc                 number(6,2), -- cmolc/dm³
   saturacao_bases     number(4,1), -- %
   saturacao_aluminio  number(4,1), -- %
   enxofre             number(6,2), -- mg/dm³
   boro                number(6,2), -- mg/dm³
   cobre               number(6,2), -- mg/dm³
   ferro               number(6,2), -- mg/dm³
   manganes            number(6,2), -- mg/dm³
   zinco               number(6,2), -- mg/dm³
   observacoes         clob,
   recomendacoes       clob,
   arquivo_laudo       varchar2(500), -- path do PDF
   id_usuario_cadastro number
      references usuarios ( id ),
   data_cadastro       date default sysdate
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

create or replace trigger haras.audit_trigger_animais after
   insert or update or delete on animais
   for each row
declare
   v_operacao         varchar2(10);
   v_dados_anteriores clob;
   v_dados_novos      clob;
begin
   if inserting then
      v_operacao := 'INSERT';
      v_dados_novos :=
         json_object(
            'id' value :new.id,
                     'nome' value :new.nome,
                     'numero_registro' value :new.numero_registro
         );
   elsif updating then
      v_operacao := 'UPDATE';
      v_dados_anteriores :=
         json_object(
            'id' value :old.id,
                     'nome' value :old.nome,
                     'numero_registro' value :old.numero_registro
         );
      v_dados_novos :=
         json_object(
            'id' value :new.id,
                     'nome' value :new.nome,
                     'numero_registro' value :new.numero_registro
         );
   elsif deleting then
      v_operacao := 'DELETE';
      v_dados_anteriores :=
         json_object(
            'id' value :old.id,
                     'nome' value :old.nome,
                     'numero_registro' value :old.numero_registro
         );
   end if;

   insert into audit_log (
      tabela,
      id_registro,
      operacao,
      dados_anteriores,
      dados_novos,
      id_usuario,
      ip_usuario
   ) values ( 'ANIMAIS',
              :new.id,
              v_operacao,
              v_dados_anteriores,
              v_dados_novos,
              :new.id_usuario_alteracao,
              sys_context(
                 'USERENV',
                 'IP_ADDRESS'
              ) );
end;

-- Comentários nas colunas para documentação
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

-- Índices para performance
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

-- Inserir alguns produtos padrão
insert into produtos_manejo (
   nome,
   tipo_produto,
   unidade_medida,
   id_usuario_cadastro
) values ( 'Ureia 45%',
           'FERTILIZANTE',
           'KG',
           6 );
insert into produtos_manejo (
   nome,
   tipo_produto,
   unidade_medida,
   id_usuario_cadastro
) values ( 'NPK 20-05-20',
           'FERTILIZANTE',
           'KG',
           6 );
insert into produtos_manejo (
   nome,
   tipo_produto,
   unidade_medida,
   id_usuario_cadastro
) values ( 'Calcário Dolomítico',
           'CORRETIVO',
           'T',
           6 );
insert into produtos_manejo (
   nome,
   tipo_produto,
   unidade_medida,
   id_usuario_cadastro
) values ( 'Superfosfato Simples',
           'FERTILIZANTE',
           'KG',
           6 );
insert into produtos_manejo (
   nome,
   tipo_produto,
   unidade_medida,
   id_usuario_cadastro
) values ( 'Glifosato 480g/L',
           'DEFENSIVO',
           'L',
           6 );
insert into produtos_manejo (
   nome,
   tipo_produto,
   unidade_medida,
   id_usuario_cadastro
) values ( 'Sementes Brachiaria Brizantha',
           'SEMENTE',
           'KG',
           6 );

commit;