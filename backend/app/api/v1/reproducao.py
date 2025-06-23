from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import desc
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.reproducao import Reproducao
from app.models.animal import Animal
from app.models.user import User
from app.schemas.reproducao import (
    ReproducaoCreate, ReproducaoUpdate, ReproducaoResponse,
    TipoCoberturaEnum, ResultadoDiagnosticoEnum, StatusReproducaoEnum,
    EstatisticasReproducao, CalendarioReproducao, HistoricoEgua
)

router = APIRouter(prefix="/api/reproducao", tags=["Reprodução"])


@router.post("/", response_model=ReproducaoResponse, status_code=status.HTTP_201_CREATED)
async def create_reproducao(
    reproducao: ReproducaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar se égua existe e é fêmea
    egua = db.query(Animal).filter(Animal.ID == reproducao.ID_EGUA).first()
    if not egua:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Égua não encontrada")

    if egua.SEXO != 'F':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Animal deve ser fêmea")

    # Verificar parceiro se informado
    if reproducao.ID_PARCEIRO:
        parceiro = db.query(Animal).filter(
            Animal.ID == reproducao.ID_PARCEIRO).first()
        if not parceiro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Parceiro não encontrado")

        if parceiro.SEXO != 'M':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Parceiro deve ser macho")

    # Verificar se égua não tem gestação ativa
    gestacao_ativa = db.query(Reproducao).filter(
        Reproducao.ID_EGUA == reproducao.ID_EGUA,
        Reproducao.STATUS_REPRODUCAO == StatusReproducaoEnum.ATIVO,
        Reproducao.RESULTADO_DIAGNOSTICO == ResultadoDiagnosticoEnum.POSITIVO
    ).first()

    if gestacao_ativa:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Égua já possui gestação ativa")

    # Calcular data prevista de parto se diagnóstico positivo
    if (reproducao.RESULTADO_DIAGNOSTICO == ResultadoDiagnosticoEnum.POSITIVO and
            not reproducao.DATA_PARTO_PREVISTA):
        reproducao.DATA_PARTO_PREVISTA = reproducao.DATA_COBERTURA + \
            timedelta(days=340)
    db_reproducao = Reproducao(**reproducao.model_dump())

    db.add(db_reproducao)
    db.commit()
    db.refresh(db_reproducao)

    return await _enrich_reproducao_response(db_reproducao, db)


@router.get("/", response_model=dict)
async def list_reproducoes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    egua_id: Optional[int] = Query(None, description="Filtrar por égua"),
    parceiro_id: Optional[int] = Query(
        None, description="Filtrar por parceiro"),
    tipo_cobertura: Optional[TipoCoberturaEnum] = Query(
        None, description="Filtrar por tipo"),
    resultado: Optional[ResultadoDiagnosticoEnum] = Query(
        None, description="Filtrar por resultado"),
    status: Optional[StatusReproducaoEnum] = Query(
        None, description="Filtrar por status"),
    data_inicio: Optional[str] = Query(
        None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    query = db.query(Reproducao)

    if egua_id:
        query = query.filter(Reproducao.ID_EGUA == egua_id)
    if parceiro_id:
        query = query.filter(Reproducao.ID_PARCEIRO == parceiro_id)
    if tipo_cobertura:
        query = query.filter(Reproducao.TIPO_COBERTURA == tipo_cobertura)
    if resultado:
        query = query.filter(Reproducao.RESULTADO_DIAGNOSTICO == resultado)
    if status:
        query = query.filter(Reproducao.STATUS_REPRODUCAO == status)
    if data_inicio:
        query = query.filter(Reproducao.DATA_COBERTURA >=
                             datetime.fromisoformat(data_inicio))
    if data_fim:
        query = query.filter(Reproducao.DATA_COBERTURA <=
                             datetime.fromisoformat(data_fim))

    total = query.count()
    offset = (page - 1) * limit
    reproducoes = query.order_by(desc(Reproducao.DATA_COBERTURA)).offset(
        offset).limit(limit).all()

    # Enriquecer com dados relacionados
    enriched_reproducoes = []
    for rep in reproducoes:
        enriched = await _enrich_reproducao_response(rep, db)
        enriched_reproducoes.append(enriched)

    return {
        "reproducoes": enriched_reproducoes,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/{id}", response_model=ReproducaoResponse)
async def get_reproducao(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reproducao = db.query(Reproducao).filter(Reproducao.ID == id).first()
    if not reproducao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Reprodução não encontrada")

    return await _enrich_reproducao_response(reproducao, db)


@router.put("/{id}", response_model=ReproducaoResponse)
async def update_reproducao(
    id: int,
    reproducao: ReproducaoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_reproducao = db.query(Reproducao).filter(Reproducao.ID == id).first()
    if not db_reproducao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Reprodução não encontrada")

    # Atualizar campos
    for key, value in reproducao.dict(exclude_unset=True).items():
        setattr(db_reproducao, key, value)

    # Calcular data prevista se mudou para positivo
    if (reproducao.RESULTADO_DIAGNOSTICO == ResultadoDiagnosticoEnum.POSITIVO and
            not db_reproducao.DATA_PARTO_PREVISTA):
        db_reproducao.DATA_PARTO_PREVISTA = db_reproducao.DATA_COBERTURA + \
            timedelta(days=340)

    # Atualizar status automaticamente se nasceu
    if reproducao.DATA_PARTO_REAL and db_reproducao.STATUS_REPRODUCAO == StatusReproducaoEnum.ATIVO:
        db_reproducao.STATUS_REPRODUCAO = StatusReproducaoEnum.CONCLUIDO

    db.commit()
    db.refresh(db_reproducao)
    return await _enrich_reproducao_response(db_reproducao, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reproducao(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_reproducao = db.query(Reproducao).filter(Reproducao.ID == id).first()
    if not db_reproducao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Reprodução não encontrada")

    db.delete(db_reproducao)
    db.commit()


@router.get("/egua/{egua_id}/historico", response_model=HistoricoEgua)
async def get_historico_egua(
    egua_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar se égua existe
    egua = db.query(Animal).filter(Animal.ID == egua_id).first()
    if not egua:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Égua não encontrada")

    # Buscar todas reproduções da égua
    reproducoes = db.query(Reproducao)\
        .filter(Reproducao.ID_EGUA == egua_id)\
        .order_by(desc(Reproducao.DATA_COBERTURA))\
        .all()

    # Enriquecer dados
    enriched_reproducoes = []
    for rep in reproducoes:
        enriched = await _enrich_reproducao_response(rep, db)
        enriched_reproducoes.append(enriched)

    # Calcular estatísticas
    total_coberturas = len(reproducoes)
    partos_realizados = len([r for r in reproducoes if r.DATA_PARTO_REAL])
    taxa_sucesso = (partos_realizados / total_coberturas *
                    100) if total_coberturas > 0 else 0

    return HistoricoEgua(
        reproducoes=enriched_reproducoes,
        total_coberturas=total_coberturas,
        partos_realizados=partos_realizados,
        taxa_sucesso=round(taxa_sucesso, 2)
    )


@router.get("/relatorio/estatisticas", response_model=EstatisticasReproducao)
async def get_estatisticas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ano: Optional[int] = Query(None, description="Filtrar por ano")
):
    query = db.query(Reproducao)

    if ano:
        inicio_ano = datetime(ano, 1, 1)
        fim_ano = datetime(ano, 12, 31, 23, 59, 59)
        query = query.filter(
            Reproducao.DATA_COBERTURA.between(inicio_ano, fim_ano))

    reproducoes = query.all()

    total_coberturas = len(reproducoes)
    positivas = len([r for r in reproducoes if r.RESULTADO_DIAGNOSTICO ==
                    ResultadoDiagnosticoEnum.POSITIVO])
    negativas = len([r for r in reproducoes if r.RESULTADO_DIAGNOSTICO ==
                    ResultadoDiagnosticoEnum.NEGATIVO])
    pendentes = len([r for r in reproducoes if r.RESULTADO_DIAGNOSTICO ==
                    ResultadoDiagnosticoEnum.PENDENTE])

    taxa_sucesso = (positivas / total_coberturas *
                    100) if total_coberturas > 0 else 0
    partos_realizados = len([r for r in reproducoes if r.DATA_PARTO_REAL])
    gestacoes_ativas = len([r for r in reproducoes if r.STATUS_REPRODUCAO ==
                           StatusReproducaoEnum.ATIVO and r.RESULTADO_DIAGNOSTICO == ResultadoDiagnosticoEnum.POSITIVO])

    return EstatisticasReproducao(
        total_coberturas=total_coberturas,
        coberturas_positivas=positivas,
        coberturas_negativas=negativas,
        coberturas_pendentes=pendentes,
        taxa_sucesso=round(taxa_sucesso, 2),
        partos_realizados=partos_realizados,
        gestacoes_ativas=gestacoes_ativas
    )


@router.get("/calendario/eventos", response_model=List[CalendarioReproducao])
async def get_calendario_eventos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    dias: int = Query(60, description="Próximos X dias")
):
    data_limite = datetime.now() + timedelta(days=dias)
    eventos = []

    # Buscar diagnósticos pendentes (15-20 dias após cobertura)
    reproducoes_diagnostico = db.query(Reproducao, Animal.NOME)\
        .join(Animal, Reproducao.ID_EGUA == Animal.ID)\
        .filter(Reproducao.RESULTADO_DIAGNOSTICO == ResultadoDiagnosticoEnum.PENDENTE)\
        .filter(Reproducao.DATA_COBERTURA + timedelta(days=15) <= data_limite)\
        .filter(Reproducao.DATA_COBERTURA + timedelta(days=15) >= datetime.now())\
        .all()

    for rep, egua_nome in reproducoes_diagnostico:
        data_diagnostico = rep.DATA_COBERTURA + \
            timedelta(days=18)  # 18 dias após cobertura
        eventos.append(CalendarioReproducao(
            egua_id=rep.ID_EGUA,
            egua_nome=egua_nome,
            evento_tipo="DIAGNOSTICO",
            data_evento=data_diagnostico,
            dias_restantes=(data_diagnostico - datetime.now()).days,
            observacoes="Diagnóstico de gestação"
        ))

    # Buscar partos previstos
    partos_previstos = db.query(Reproducao, Animal.NOME)\
        .join(Animal, Reproducao.ID_EGUA == Animal.ID)\
        .filter(Reproducao.DATA_PARTO_PREVISTA.isnot(None))\
        .filter(Reproducao.DATA_PARTO_PREVISTA <= data_limite)\
        .filter(Reproducao.DATA_PARTO_PREVISTA >= datetime.now())\
        .filter(Reproducao.STATUS_REPRODUCAO == StatusReproducaoEnum.ATIVO)\
        .all()

    for rep, egua_nome in partos_previstos:
        eventos.append(CalendarioReproducao(
            egua_id=rep.ID_EGUA,
            egua_nome=egua_nome,
            evento_tipo="PARTO_PREVISTO",
            data_evento=rep.DATA_PARTO_PREVISTA,
            dias_restantes=(rep.DATA_PARTO_PREVISTA - datetime.now()).days,
            observacoes="Parto previsto"
        ))

    # Ordenar por data
    eventos.sort(key=lambda x: x.data_evento)

    return eventos


@router.get("/options/tipos-cobertura")
async def get_tipos_cobertura(current_user: User = Depends(get_current_user)):
    return [
        {"value": "NATURAL", "label": "Natural"},
        {"value": "IA", "label": "Inseminação Artificial"},
        {"value": "TE", "label": "Transferência de Embrião"}
    ]


@router.get("/options/resultados")
async def get_resultados_diagnostico(current_user: User = Depends(get_current_user)):
    return [
        {"value": "POSITIVO", "label": "Positivo"},
        {"value": "NEGATIVO", "label": "Negativo"},
        {"value": "PENDENTE", "label": "Pendente"}
    ]


@router.get("/options/status")
async def get_status_reproducao(current_user: User = Depends(get_current_user)):
    return [
        {"value": "A", "label": "Ativo"},
        {"value": "C", "label": "Concluído"},
        {"value": "F", "label": "Falhado"}
    ]

# Função auxiliar para enriquecer resposta


async def _enrich_reproducao_response(reproducao: Reproducao, db: Session) -> ReproducaoResponse:
    # Buscar dados relacionados
    egua = db.query(Animal).filter(Animal.ID == reproducao.ID_EGUA).first()
    parceiro = None
    if reproducao.ID_PARCEIRO:
        parceiro = db.query(Animal).filter(
            Animal.ID == reproducao.ID_PARCEIRO).first()

    # Calcular dias de gestação
    dias_gestacao = None
    if reproducao.RESULTADO_DIAGNOSTICO == ResultadoDiagnosticoEnum.POSITIVO:
        if reproducao.DATA_PARTO_REAL:
            dias_gestacao = (reproducao.DATA_PARTO_REAL -
                             reproducao.DATA_COBERTURA).days
        else:
            dias_gestacao = (datetime.now() - reproducao.DATA_COBERTURA).days

    # Criar response com dados enriquecidos
    response_data = ReproducaoResponse.from_orm(reproducao)
    response_data.egua_nome = egua.NOME if egua else None
    response_data.parceiro_nome = parceiro.NOME if parceiro else None
    response_data.dias_gestacao = dias_gestacao

    return response_data
