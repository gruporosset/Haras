# backend/app/api/v1/saude.py
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, desc
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.saude import SaudeAnimais, TipoRegistroEnum
from app.models.animal import Animal
from app.models.user import User
from app.schemas.saude import (
    SaudeCreate, SaudeUpdate, SaudeResponse, AplicacaoRapida,
    EstatisticasSaude, ProximasAplicacoes, HistoricoSaude,
    CalendarioSaude, ConsumoPorTipo, MedicamentoAutocomplete
)

router = APIRouter(prefix="/api/saude", tags=["Saúde"])


@router.post("/", response_model=SaudeResponse, status_code=status.HTTP_201_CREATED)
async def create_registro_saude(
    saude: SaudeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar se animal existe
    animal = db.query(Animal).filter(Animal.ID == saude.ID_ANIMAL).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado")

    # Se especificou medicamento do estoque, fazer validações
    if saude.ID_MEDICAMENTO and saude.QUANTIDADE_APLICADA:
        # Importar aqui para evitar dependência circular
        from app.models.medicamento import Medicamento, MovimentacaoMedicamento, TipoMovimentacaoEnum

        medicamento = db.query(Medicamento).filter(
            Medicamento.ID == saude.ID_MEDICAMENTO).first()
        if not medicamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Medicamento não encontrado")

        # Verificar se medicamento está ativo
        if medicamento.ATIVO != 'S':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Medicamento não está ativo"
            )

        # Verificar estoque suficiente
        if medicamento.ESTOQUE_ATUAL < saude.QUANTIDADE_APLICADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente. Disponível: {medicamento.ESTOQUE_ATUAL} {medicamento.UNIDADE_MEDIDA}"
            )

        # Preencher campos automáticos baseados no medicamento
        if not saude.MEDICAMENTO_APLICADO:
            saude.MEDICAMENTO_APLICADO = medicamento.NOME
        if not saude.DOSE_APLICADA:
            saude.DOSE_APLICADA = f"{saude.QUANTIDADE_APLICADA} {medicamento.UNIDADE_MEDIDA}"
        if not saude.UNIDADE_APLICADA:
            saude.UNIDADE_APLICADA = medicamento.UNIDADE_MEDIDA

    # Criar registro de saúde
    db_saude = SaudeAnimais(**saude.dict())
    db.add(db_saude)
    db.flush()  # Para obter o ID antes do commit

    # Se tem medicamento do estoque, criar movimentação
    if saude.ID_MEDICAMENTO and saude.QUANTIDADE_APLICADA:
        from app.models.medicamento import MovimentacaoMedicamento, TipoMovimentacaoEnum

        movimentacao = MovimentacaoMedicamento(
            ID_MEDICAMENTO=saude.ID_MEDICAMENTO,
            TIPO_MOVIMENTACAO=TipoMovimentacaoEnum.SAIDA,
            QUANTIDADE=saude.QUANTIDADE_APLICADA,
            ID_ANIMAL=saude.ID_ANIMAL,
            ID_SAUDE_ANIMAL=db_saude.ID,
            MOTIVO=f"Aplicação de saúde - {saude.TIPO_REGISTRO}",
            OBSERVACOES=saude.OBSERVACOES,
            ID_USUARIO_REGISTRO=current_user.ID
        )

        db.add(movimentacao)

    db.commit()
    db.refresh(db_saude)

    return await _enrich_saude_response(db_saude, db)


@router.get("/", response_model=dict)
async def list_registros_saude(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    animal_id: Optional[int] = Query(None, description="Filtrar por animal"),
    tipo_registro: Optional[TipoRegistroEnum] = Query(
        None, description="Filtrar por tipo"),
    data_inicio: Optional[str] = Query(
        None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    veterinario: Optional[str] = Query(
        None, description="Filtrar por veterinário"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    query = db.query(SaudeAnimais).join(Animal)

    if animal_id:
        query = query.filter(SaudeAnimais.ID_ANIMAL == animal_id)
    if tipo_registro:
        query = query.filter(SaudeAnimais.TIPO_REGISTRO == tipo_registro)
    if data_inicio:
        query = query.filter(SaudeAnimais.DATA_OCORRENCIA >=
                             datetime.fromisoformat(data_inicio))
    if data_fim:
        query = query.filter(SaudeAnimais.DATA_OCORRENCIA <=
                             datetime.fromisoformat(data_fim))
    if veterinario:
        query = query.filter(
            SaudeAnimais.VETERINARIO_RESPONSAVEL.ilike(f"%{veterinario}%"))

    total = query.count()
    offset = (page - 1) * limit
    registros = query.order_by(desc(SaudeAnimais.DATA_OCORRENCIA)).offset(
        offset).limit(limit).all()

    # Enriquecer com dados relacionados
    enriched_registros = []
    for registro in registros:
        enriched = await _enrich_saude_response(registro, db)
        enriched_registros.append(enriched)

    return {
        "registros": enriched_registros,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/{id}", response_model=SaudeResponse)
async def get_registro_saude(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    registro = db.query(SaudeAnimais).filter(SaudeAnimais.ID == id).first()
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Registro não encontrado")

    return await _enrich_saude_response(registro, db)


@router.put("/{id}", response_model=SaudeResponse)
async def update_registro_saude(
    id: int,
    saude: SaudeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_saude = db.query(SaudeAnimais).filter(SaudeAnimais.ID == id).first()
    if not db_saude:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Registro não encontrado")

    # Verificar se está alterando medicamento do estoque
    medicamento_alterado = False
    if (hasattr(saude, 'ID_MEDICAMENTO') and saude.ID_MEDICAMENTO != db_saude.ID_MEDICAMENTO) or \
       (hasattr(saude, 'QUANTIDADE_APLICADA') and saude.QUANTIDADE_APLICADA != db_saude.QUANTIDADE_APLICADA):
        medicamento_alterado = True

    # Se alterou medicamento, reverter movimentação anterior
    if medicamento_alterado and db_saude.ID_MEDICAMENTO:
        from app.models.medicamento import MovimentacaoMedicamento, TipoMovimentacaoEnum

        # Reverter movimentação anterior (criar entrada para compensar)
        if db_saude.QUANTIDADE_APLICADA:
            reversao = MovimentacaoMedicamento(
                ID_MEDICAMENTO=db_saude.ID_MEDICAMENTO,
                TIPO_MOVIMENTACAO=TipoMovimentacaoEnum.ENTRADA,
                QUANTIDADE=db_saude.QUANTIDADE_APLICADA,
                ID_ANIMAL=db_saude.ID_ANIMAL,
                ID_SAUDE_ANIMAL=db_saude.ID,
                MOTIVO=f"Reversão por alteração de registro de saúde",
                OBSERVACOES="Estorno automático por edição",
                ID_USUARIO_REGISTRO=current_user.ID
            )
            db.add(reversao)

    # Atualizar campos
    for key, value in saude.dict(exclude_unset=True).items():
        setattr(db_saude, key, value)

    # Se tem novo medicamento, criar nova movimentação
    if db_saude.ID_MEDICAMENTO and db_saude.QUANTIDADE_APLICADA:
        from app.models.medicamento import Medicamento, MovimentacaoMedicamento, TipoMovimentacaoEnum

        medicamento = db.query(Medicamento).filter(
            Medicamento.ID == db_saude.ID_MEDICAMENTO).first()
        if medicamento:
            # Verificar estoque
            if medicamento.ESTOQUE_ATUAL < db_saude.QUANTIDADE_APLICADA:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente. Disponível: {medicamento.ESTOQUE_ATUAL} {medicamento.UNIDADE_MEDIDA}"
                )

            # Criar nova movimentação
            nova_movimentacao = MovimentacaoMedicamento(
                ID_MEDICAMENTO=db_saude.ID_MEDICAMENTO,
                TIPO_MOVIMENTACAO=TipoMovimentacaoEnum.SAIDA,
                QUANTIDADE=db_saude.QUANTIDADE_APLICADA,
                ID_ANIMAL=db_saude.ID_ANIMAL,
                ID_SAUDE_ANIMAL=db_saude.ID,
                MOTIVO=f"Aplicação atualizada - {db_saude.TIPO_REGISTRO}",
                OBSERVACOES=db_saude.OBSERVACOES,
                ID_USUARIO_REGISTRO=current_user.ID
            )
            db.add(nova_movimentacao)

    db.commit()
    db.refresh(db_saude)
    return await _enrich_saude_response(db_saude, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_registro_saude(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_saude = db.query(SaudeAnimais).filter(SaudeAnimais.ID == id).first()
    if not db_saude:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Registro não encontrado")

    # Se tinha medicamento do estoque, reverter movimentação
    if db_saude.ID_MEDICAMENTO and db_saude.QUANTIDADE_APLICADA:
        from app.models.medicamento import MovimentacaoMedicamento, TipoMovimentacaoEnum

        reversao = MovimentacaoMedicamento(
            ID_MEDICAMENTO=db_saude.ID_MEDICAMENTO,
            TIPO_MOVIMENTACAO=TipoMovimentacaoEnum.ENTRADA,
            QUANTIDADE=db_saude.QUANTIDADE_APLICADA,
            ID_ANIMAL=db_saude.ID_ANIMAL,
            ID_SAUDE_ANIMAL=db_saude.ID,
            MOTIVO=f"Reversão por exclusão de registro de saúde",
            OBSERVACOES="Estorno automático por exclusão",
            ID_USUARIO_REGISTRO=current_user.ID
        )
        db.add(reversao)

    db.delete(db_saude)
    db.commit()

# === APLICAÇÃO RÁPIDA ===


@router.post("/aplicacao-rapida", response_model=SaudeResponse, status_code=status.HTTP_201_CREATED)
async def aplicacao_rapida(
    aplicacao: AplicacaoRapida,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint para aplicação rápida de medicamentos/vacinas"""
    saude_data = SaudeCreate(
        ID_ANIMAL=aplicacao.ID_ANIMAL,
        TIPO_REGISTRO=aplicacao.TIPO_REGISTRO,
        DATA_OCORRENCIA=datetime.now(),
        ID_MEDICAMENTO=aplicacao.ID_MEDICAMENTO,
        QUANTIDADE_APLICADA=aplicacao.QUANTIDADE_APLICADA,
        MEDICAMENTO_APLICADO=aplicacao.MEDICAMENTO_APLICADO,
        DOSE_APLICADA=aplicacao.DOSE_APLICADA,
        VETERINARIO_RESPONSAVEL=aplicacao.VETERINARIO_RESPONSAVEL,
        OBSERVACOES=aplicacao.OBSERVACOES,
        ID_USUARIO_REGISTRO=current_user.ID
    )

    return await create_registro_saude(saude_data, db, current_user)

# === AUTOCOMPLETE MEDICAMENTOS ===


@router.get("/medicamentos-autocomplete", response_model=List[MedicamentoAutocomplete])
async def autocomplete_medicamentos_saude(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    termo: str = Query(..., description="Termo para busca"),
    limit: int = Query(10, ge=1, le=50)
):
    """Autocomplete para medicamentos com estoque > 0 para uso em saúde"""
    try:
        from app.models.medicamento import Medicamento

        medicamentos = db.query(Medicamento).filter(
            Medicamento.NOME.ilike(f"%{termo}%"),
            Medicamento.ATIVO == 'S',
            Medicamento.ESTOQUE_ATUAL > 0
        ).order_by(Medicamento.NOME).limit(limit).all()

        return [
            MedicamentoAutocomplete(
                value=med.ID,
                label=f"{med.NOME} ({med.ESTOQUE_ATUAL} {med.UNIDADE_MEDIDA})",
                nome=med.NOME,
                estoque=med.ESTOQUE_ATUAL,
                unidade=med.UNIDADE_MEDIDA,
                forma=med.FORMA_FARMACEUTICA,
                carencia=med.PERIODO_CARENCIA,
                principio_ativo=med.PRINCIPIO_ATIVO
            )
            for med in medicamentos
        ]
    except Exception:
        # Se não tiver módulo de medicamentos, retornar lista vazia
        return []


@router.post("/validar-estoque-medicamento")
async def validar_estoque_medicamento(
    medicamento_id: int,
    quantidade: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Valida se há estoque suficiente para aplicação"""
    try:
        from app.models.medicamento import Medicamento

        medicamento = db.query(Medicamento).filter(
            Medicamento.ID == medicamento_id).first()
        if not medicamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Medicamento não encontrado")

        estoque_suficiente = medicamento.ESTOQUE_ATUAL >= quantidade

        return {
            "valido": estoque_suficiente,
            "estoque_atual": medicamento.ESTOQUE_ATUAL,
            "unidade_medida": medicamento.UNIDADE_MEDIDA,
            "estoque_restante": medicamento.ESTOQUE_ATUAL - quantidade if estoque_suficiente else None,
            "erro": None if estoque_suficiente else f"Estoque insuficiente. Disponível: {medicamento.ESTOQUE_ATUAL} {medicamento.UNIDADE_MEDIDA}"
        }
    except Exception as e:
        if "Medicamento não encontrado" in str(e):
            raise e
        return {
            "valido": False,
            "erro": "Módulo de medicamentos não disponível"
        }

# === RELATÓRIOS ===


@router.get("/estatisticas/geral", response_model=List[EstatisticasSaude])
async def get_estatisticas_gerais(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    meses_periodo: int = Query(12, description="Período em meses para análise")
):
    """Estatísticas gerais de saúde por animal"""
    data_limite = datetime.now() - timedelta(days=meses_periodo * 30)

    # Buscar animais com registros de saúde
    animais_com_registros = db.query(Animal.ID, Animal.NOME).join(
        SaudeAnimais).distinct().all()

    estatisticas = []
    for animal_id, animal_nome in animais_com_registros:
        # Buscar registros do animal no período
        registros = db.query(SaudeAnimais).filter(
            SaudeAnimais.ID_ANIMAL == animal_id,
            SaudeAnimais.DATA_OCORRENCIA >= data_limite
        ).all()

        if not registros:
            continue

        # Contar tipos aplicados
        tipos_aplicados = {}
        custo_total = 0
        veterinarios = {}

        for registro in registros:
            tipo = registro.TIPO_REGISTRO
            tipos_aplicados[tipo] = tipos_aplicados.get(tipo, 0) + 1

            if registro.CUSTO:
                custo_total += registro.CUSTO

            if registro.VETERINARIO_RESPONSAVEL:
                vet = registro.VETERINARIO_RESPONSAVEL
                veterinarios[vet] = veterinarios.get(vet, 0) + 1

        # Última aplicação
        ultima_aplicacao = max(
            registros, key=lambda x: x.DATA_OCORRENCIA).DATA_OCORRENCIA

        # Próximas aplicações
        proximas = db.query(SaudeAnimais).filter(
            SaudeAnimais.ID_ANIMAL == animal_id,
            SaudeAnimais.PROXIMA_APLICACAO > datetime.now()
        ).count()

        # Veterinário principal (mais frequente)
        veterinario_principal = max(
            veterinarios.keys()) if veterinarios else None

        estatisticas.append(EstatisticasSaude(
            animal_id=animal_id,
            animal_nome=animal_nome,
            total_registros=len(registros),
            tipos_aplicados=tipos_aplicados,
            ultima_aplicacao=ultima_aplicacao,
            proximas_aplicacoes=proximas,
            custo_total=custo_total if custo_total > 0 else None,
            veterinario_principal=veterinario_principal
        ))

    return estatisticas


@router.get("/calendario", response_model=List[CalendarioSaude])
async def get_calendario_saude(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data_inicio: str = Query(..., description="Data início (YYYY-MM-DD)"),
    data_fim: str = Query(..., description="Data fim (YYYY-MM-DD)")
):
    """Calendário de aplicações programadas"""
    inicio = datetime.fromisoformat(data_inicio)
    fim = datetime.fromisoformat(data_fim)

    # Buscar aplicações no período
    aplicacoes = db.query(SaudeAnimais, Animal.NOME).join(Animal).filter(
        SaudeAnimais.PROXIMA_APLICACAO.between(inicio, fim)
    ).all()

    # Agrupar por data
    calendario = {}
    for saude, animal_nome in aplicacoes:
        data_key = saude.PROXIMA_APLICACAO.date().isoformat()

        if data_key not in calendario:
            calendario[data_key] = {
                'data': saude.PROXIMA_APLICACAO,
                'eventos': [],
                'tipos_eventos': set()
            }

        evento = {
            'animal_id': saude.ID_ANIMAL,
            'animal_nome': animal_nome,
            'tipo': saude.TIPO_REGISTRO,
            'descricao': saude.DESCRICAO or saude.MEDICAMENTO_APLICADO,
            'veterinario': saude.VETERINARIO_RESPONSAVEL
        }

        calendario[data_key]['eventos'].append(evento)
        calendario[data_key]['tipos_eventos'].add(saude.TIPO_REGISTRO)

    # Converter para lista de CalendarioSaude
    resultado = []
    for data_key, dados in calendario.items():
        resultado.append(CalendarioSaude(
            data=dados['data'],
            eventos=dados['eventos'],
            total_eventos=len(dados['eventos']),
            tipos_eventos=list(dados['tipos_eventos'])
        ))

    # Ordenar por data
    resultado.sort(key=lambda x: x.data)
    return resultado


@router.get("/relatorio/consumo-por-tipo", response_model=List[ConsumoPorTipo])
async def get_consumo_por_tipo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    meses_periodo: int = Query(6, description="Período em meses para análise")
):
    """Relatório de consumo por tipo de registro"""
    data_limite = datetime.now() - timedelta(days=meses_periodo * 30)

    # Buscar registros agrupados por tipo
    resultados = db.query(
        SaudeAnimais.TIPO_REGISTRO,
        func.count(SaudeAnimais.ID).label('total_aplicacoes'),
        func.count(func.distinct(SaudeAnimais.ID_MEDICAMENTO)
                   ).label('medicamentos_utilizados'),
        func.sum(SaudeAnimais.CUSTO).label('custo_total'),
        func.count(func.distinct(SaudeAnimais.ID_ANIMAL)
                   ).label('animais_atendidos')
    ).filter(
        SaudeAnimais.DATA_OCORRENCIA >= data_limite
    ).group_by(SaudeAnimais.TIPO_REGISTRO).all()

    consumos = []
    for resultado in resultados:
        # Ajustar medicamentos_utilizados (excluir NULLs)
        medicamentos_count = resultado.medicamentos_utilizados
        if medicamentos_count and medicamentos_count > 0:
            # Verificar se realmente tem medicamentos (não apenas NULLs)
            real_medicamentos = db.query(func.count(func.distinct(SaudeAnimais.ID_MEDICAMENTO))).filter(
                SaudeAnimais.TIPO_REGISTRO == resultado.TIPO_REGISTRO,
                SaudeAnimais.DATA_OCORRENCIA >= data_limite,
                SaudeAnimais.ID_MEDICAMENTO.isnot(None)
            ).scalar()
            medicamentos_count = real_medicamentos
        else:
            medicamentos_count = 0

        consumos.append(ConsumoPorTipo(
            tipo_registro=resultado.TIPO_REGISTRO,
            total_aplicacoes=resultado.total_aplicacoes,
            medicamentos_utilizados=medicamentos_count,
            custo_total=float(
                resultado.custo_total) if resultado.custo_total else None,
            periodo_analise=f"{meses_periodo} meses",
            animais_atendidos=resultado.animais_atendidos
        ))

    return consumos


@router.get("/animal/{animal_id}/historico", response_model=HistoricoSaude)
async def get_historico_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    meses: int = Query(12, description="Período em meses")
):
    """Histórico completo de saúde de um animal"""
    # Verificar se animal existe
    animal = db.query(Animal).filter(Animal.ID == animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado")

    data_limite = datetime.now() - timedelta(days=meses * 30)

    registros = db.query(SaudeAnimais).filter(
        SaudeAnimais.ID_ANIMAL == animal_id,
        SaudeAnimais.DATA_OCORRENCIA >= data_limite
    ).order_by(desc(SaudeAnimais.DATA_OCORRENCIA)).all()

    # Enriquecer registros
    registros_enriched = []
    for registro in registros:
        enriched = await _enrich_saude_response(registro, db)
        registros_enriched.append(enriched)

    # Resumo por tipos
    resumo_tipos = {}
    custo_total = 0

    for registro in registros:
        tipo = registro.TIPO_REGISTRO
        resumo_tipos[tipo] = resumo_tipos.get(tipo, 0) + 1
        if registro.CUSTO:
            custo_total += registro.CUSTO

    return HistoricoSaude(
        animal_id=animal_id,
        animal_nome=animal.NOME,
        registros=registros_enriched,
        resumo_tipos=resumo_tipos,
        periodo_analise=f"{meses} meses",
        total_custo=custo_total if custo_total > 0 else None
    )


@router.get("/proximas-aplicacoes", response_model=List[ProximasAplicacoes])
async def get_proximas_aplicacoes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    dias: int = Query(30, description="Próximos X dias")
):
    """Lista próximas aplicações programadas"""
    data_limite = datetime.now() + timedelta(days=dias)

    registros = db.query(SaudeAnimais, Animal.NOME).join(Animal).filter(
        SaudeAnimais.PROXIMA_APLICACAO.isnot(None),
        SaudeAnimais.PROXIMA_APLICACAO <= data_limite,
        SaudeAnimais.PROXIMA_APLICACAO >= datetime.now()
    ).order_by(SaudeAnimais.PROXIMA_APLICACAO).all()

    proximas = []
    for saude, animal_nome in registros:
        dias_restantes = (saude.PROXIMA_APLICACAO - datetime.now()).days

        # Determinar prioridade
        if dias_restantes <= 3:
            prioridade = "URGENTE"
        elif dias_restantes <= 7:
            prioridade = "NORMAL"
        else:
            prioridade = "BAIXA"

        # Buscar nome do medicamento se tiver
        medicamento_nome = None
        if saude.ID_MEDICAMENTO:
            try:
                from app.models.medicamento import Medicamento
                medicamento = db.query(Medicamento).filter(
                    Medicamento.ID == saude.ID_MEDICAMENTO).first()
                medicamento_nome = medicamento.NOME if medicamento else None
            except:
                pass

        proximas.append(ProximasAplicacoes(
            animal_id=saude.ID_ANIMAL,
            animal_nome=animal_nome,
            tipo_registro=saude.TIPO_REGISTRO,
            data_aplicacao=saude.PROXIMA_APLICACAO,
            descricao=saude.DESCRICAO or f"{saude.TIPO_REGISTRO} - {saude.MEDICAMENTO_APLICADO or 'Não especificado'}",
            dias_restantes=dias_restantes,
            medicamento_nome=medicamento_nome,
            veterinario_responsavel=saude.VETERINARIO_RESPONSAVEL,
            prioridade=prioridade
        ))

    return proximas

# === FUNÇÃO AUXILIAR ===


async def _enrich_saude_response(saude: SaudeAnimais, db: Session) -> SaudeResponse:
    """Enriquece resposta com dados calculados"""
    animal = db.query(Animal).filter(Animal.ID == saude.ID_ANIMAL).first()
    medicamento = None
    estoque_suficiente = None

    if saude.ID_MEDICAMENTO:
        try:
            from app.models.medicamento import Medicamento
            medicamento = db.query(Medicamento).filter(
                Medicamento.ID == saude.ID_MEDICAMENTO).first()
            if medicamento and saude.QUANTIDADE_APLICADA:
                estoque_suficiente = medicamento.ESTOQUE_ATUAL >= saude.QUANTIDADE_APLICADA
        except:
            pass

    # Calcular dias para próxima aplicação
    dias_proxima_aplicacao = None
    status_aplicacao = "APLICADO"

    if saude.PROXIMA_APLICACAO:
        hoje = datetime.now()
        if saude.PROXIMA_APLICACAO > hoje:
            dias_proxima_aplicacao = (saude.PROXIMA_APLICACAO - hoje).days
            status_aplicacao = "PENDENTE"
        else:
            dias_proxima_aplicacao = (hoje - saude.PROXIMA_APLICACAO).days
            status_aplicacao = "ATRASADO"

    response_data = SaudeResponse.from_orm(saude)
    response_data.animal_nome = animal.NOME if animal else None
    response_data.medicamento_nome = medicamento.NOME if medicamento else None
    response_data.estoque_suficiente = estoque_suficiente
    response_data.dias_proxima_aplicacao = dias_proxima_aplicacao
    response_data.status_aplicacao = status_aplicacao

    return response_data
