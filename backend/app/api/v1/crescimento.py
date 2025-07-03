# backend/app/api/v1/crescimento.py
from datetime import datetime, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.animal import Animal
from app.models.crescimento import HistoricoCrescimento
from app.models.user import User
from app.schemas.crescimento import (
    ComparacaoMedidas,
    CrescimentoCreate,
    CrescimentoDetalhado,
    CrescimentoResponse,
    CrescimentoUpdate,
    EstatisticasCrescimento,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import desc, func

router = APIRouter(prefix="/api/crescimento", tags=["Crescimento"])


@router.post(
    "/", response_model=CrescimentoResponse, status_code=status.HTTP_201_CREATED
)
async def create_crescimento(
    crescimento: CrescimentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verificar se animal existe
    animal = db.query(Animal).filter(Animal.ID == crescimento.ID_ANIMAL).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    # Verificar se já existe medição para a mesma data
    existing = (
        db.query(HistoricoCrescimento)
        .filter(
            HistoricoCrescimento.ID_ANIMAL == crescimento.ID_ANIMAL,
            func.trunc(HistoricoCrescimento.DATA_MEDICAO)
            == crescimento.DATA_MEDICAO.date(),
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma medição para este animal nesta data",
        )

    db_crescimento = HistoricoCrescimento(**crescimento.dict())
    db_crescimento.ID_USUARIO_REGISTRO = current_user.ID
    db.add(db_crescimento)

    # Atualizar peso atual do animal se informado
    if crescimento.PESO:
        animal.PESO_ATUAL = crescimento.PESO

    db.commit()
    db.refresh(db_crescimento)

    return await _enrich_crescimento_response(db_crescimento, db)


@router.get("/", response_model=dict)
async def list_crescimentos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    animal_id: Optional[int] = Query(None, description="Filtrar por animal"),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    query = db.query(HistoricoCrescimento).join(Animal)

    if animal_id:
        query = query.filter(HistoricoCrescimento.ID_ANIMAL == animal_id)
    if data_inicio:
        query = query.filter(
            HistoricoCrescimento.DATA_MEDICAO >= datetime.fromisoformat(data_inicio)
        )
    if data_fim:
        query = query.filter(
            HistoricoCrescimento.DATA_MEDICAO <= datetime.fromisoformat(data_fim)
        )

    total = query.count()
    offset = (page - 1) * limit
    registros = (
        query.order_by(desc(HistoricoCrescimento.DATA_MEDICAO))
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Enriquecer com dados calculados
    enriched_registros = []
    for registro in registros:
        enriched = await _enrich_crescimento_response(registro, db)
        enriched_registros.append(enriched)

    return {
        "registros": enriched_registros,
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/{id}", response_model=CrescimentoResponse)
async def get_crescimento(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    registro = (
        db.query(HistoricoCrescimento).filter(HistoricoCrescimento.ID == id).first()
    )
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado"
        )

    return await _enrich_crescimento_response(registro, db)


@router.put("/{id}", response_model=CrescimentoResponse)
async def update_crescimento(
    id: int,
    crescimento: CrescimentoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_crescimento = (
        db.query(HistoricoCrescimento).filter(HistoricoCrescimento.ID == id).first()
    )
    if not db_crescimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado"
        )

    # Verificar duplicata de data se alterou
    if (
        crescimento.DATA_MEDICAO
        and crescimento.DATA_MEDICAO != db_crescimento.DATA_MEDICAO
    ):
        existing = (
            db.query(HistoricoCrescimento)
            .filter(
                HistoricoCrescimento.ID_ANIMAL == db_crescimento.ID_ANIMAL,
                func.trunc(HistoricoCrescimento.DATA_MEDICAO)
                == crescimento.DATA_MEDICAO.date(),
                HistoricoCrescimento.ID != id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma medição para este animal nesta data",
            )

    for key, value in crescimento.dict(exclude_unset=True).items():
        setattr(db_crescimento, key, value)

    # Atualizar peso atual do animal se alterou
    if crescimento.PESO:
        animal = db.query(Animal).filter(Animal.ID == db_crescimento.ID_ANIMAL).first()
        if animal:
            # Verificar se esta é a medição mais recente
            ultima_medicao = (
                db.query(HistoricoCrescimento)
                .filter(HistoricoCrescimento.ID_ANIMAL == db_crescimento.ID_ANIMAL)
                .order_by(desc(HistoricoCrescimento.DATA_MEDICAO))
                .first()
            )

            if ultima_medicao and ultima_medicao.ID == id:
                animal.PESO_ATUAL = crescimento.PESO

    db.commit()
    db.refresh(db_crescimento)
    return await _enrich_crescimento_response(db_crescimento, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crescimento(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_crescimento = (
        db.query(HistoricoCrescimento).filter(HistoricoCrescimento.ID == id).first()
    )
    if not db_crescimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado"
        )

    db.delete(db_crescimento)
    db.commit()


# === RELATÓRIOS E ESTATÍSTICAS ===


@router.get("/animal/{animal_id}/historico", response_model=List[CrescimentoDetalhado])
async def get_historico_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Histórico detalhado de crescimento de um animal com variações"""
    # Verificar se animal existe
    animal = db.query(Animal).filter(Animal.ID == animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    medicoes = (
        db.query(HistoricoCrescimento)
        .filter(HistoricoCrescimento.ID_ANIMAL == animal_id)
        .order_by(HistoricoCrescimento.DATA_MEDICAO)
        .all()
    )

    historico = []
    for i, medicao in enumerate(medicoes):
        # Calcular variações em relação à medição anterior
        variacao_peso = None
        variacao_altura = None
        dias_crescimento = None
        taxa_crescimento_dia = None

        if i > 0:
            medicao_anterior = medicoes[i - 1]

            if medicao.PESO and medicao_anterior.PESO:
                variacao_peso = medicao.PESO - medicao_anterior.PESO

            if medicao.ALTURA and medicao_anterior.ALTURA:
                variacao_altura = medicao.ALTURA - medicao_anterior.ALTURA

            dias_crescimento = (
                medicao.DATA_MEDICAO - medicao_anterior.DATA_MEDICAO
            ).days

            if variacao_peso and dias_crescimento > 0:
                taxa_crescimento_dia = variacao_peso / dias_crescimento

        # Enriquecer medição
        medicao_enriquecida = await _enrich_crescimento_response(medicao, db)

        historico.append(
            CrescimentoDetalhado(
                medicao=medicao_enriquecida,
                variacao_peso=variacao_peso,
                variacao_altura=variacao_altura,
                dias_crescimento=dias_crescimento,
                taxa_crescimento_dia=taxa_crescimento_dia,
            )
        )

    return historico


@router.get("/estatisticas/geral", response_model=List[EstatisticasCrescimento])
async def get_estatisticas_gerais(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    meses_periodo: int = Query(12, description="Período em meses para análise"),
):
    """Estatísticas de crescimento de todos os animais"""
    data_limite = datetime.now() - timedelta(days=meses_periodo * 30)

    # Buscar animais com medições
    animais_com_medicoes = (
        db.query(Animal.ID, Animal.NOME).join(HistoricoCrescimento).distinct().all()
    )

    estatisticas = []
    for animal_id, animal_nome in animais_com_medicoes:
        # Buscar medições do animal no período
        medicoes = (
            db.query(HistoricoCrescimento)
            .filter(
                HistoricoCrescimento.ID_ANIMAL == animal_id,
                HistoricoCrescimento.DATA_MEDICAO >= data_limite,
            )
            .order_by(HistoricoCrescimento.DATA_MEDICAO)
            .all()
        )

        if not medicoes:
            continue

        primeira_medicao = medicoes[0]
        ultima_medicao = medicoes[-1]

        # Calcular estatísticas
        peso_inicial = primeira_medicao.PESO
        peso_atual = ultima_medicao.PESO
        ganho_peso_total = None
        ganho_peso_medio_mes = None

        if peso_inicial and peso_atual:
            ganho_peso_total = peso_atual - peso_inicial
            dias_periodo = (
                ultima_medicao.DATA_MEDICAO - primeira_medicao.DATA_MEDICAO
            ).days
            if dias_periodo > 0:
                ganho_peso_medio_mes = (ganho_peso_total / dias_periodo) * 30

        altura_inicial = primeira_medicao.ALTURA
        altura_atual = ultima_medicao.ALTURA

        estatisticas.append(
            EstatisticasCrescimento(
                animal_id=animal_id,
                animal_nome=animal_nome,
                total_medicoes=len(medicoes),
                peso_inicial=peso_inicial,
                peso_atual=peso_atual,
                ganho_peso_total=ganho_peso_total,
                ganho_peso_medio_mes=ganho_peso_medio_mes,
                altura_inicial=altura_inicial,
                altura_atual=altura_atual,
                primeira_medicao=primeira_medicao.DATA_MEDICAO,
                ultima_medicao=ultima_medicao.DATA_MEDICAO,
            )
        )

    return estatisticas


@router.get("/comparacao/medidas", response_model=List[ComparacaoMedidas])
async def get_comparacao_medidas(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Comparação das medidas atuais dos animais"""
    # Subquery para última medição de cada animal
    subq_ultima = (
        db.query(
            HistoricoCrescimento.ID_ANIMAL,
            func.max(HistoricoCrescimento.DATA_MEDICAO).label("ultima_data"),
        )
        .group_by(HistoricoCrescimento.ID_ANIMAL)
        .subquery()
    )

    # Query principal
    resultados = (
        db.query(
            Animal.ID,
            Animal.NOME,
            Animal.DATA_NASCIMENTO,
            HistoricoCrescimento.PESO,
            HistoricoCrescimento.ALTURA,
        )
        .join(HistoricoCrescimento)
        .join(
            subq_ultima,
            (HistoricoCrescimento.ID_ANIMAL == subq_ultima.c.ID_ANIMAL)
            & (HistoricoCrescimento.DATA_MEDICAO == subq_ultima.c.ultima_data),
        )
        .all()
    )

    comparacoes = []
    for animal_id, nome, data_nascimento, peso, altura in resultados:
        # Calcular idade em meses
        idade_meses = None
        if data_nascimento:
            dias_vida = (datetime.now() - data_nascimento).days
            idade_meses = int(dias_vida / 30)

        # Classificação simples (pode ser expandida com dados da raça)
        classificacao = "IDEAL"
        if peso:
            if peso < 300:  # Valores exemplo
                classificacao = "ABAIXO"
            elif peso > 600:
                classificacao = "ACIMA"

        comparacoes.append(
            ComparacaoMedidas(
                animal_id=animal_id,
                animal_nome=nome,
                idade_meses=idade_meses,
                peso_atual=peso,
                peso_ideal_raca=None,  # Para futuro
                altura_atual=altura,
                classificacao=classificacao,
            )
        )

    return comparacoes


# === FUNÇÃO AUXILIAR ===


async def _enrich_crescimento_response(
    crescimento: HistoricoCrescimento, db: Session
) -> CrescimentoResponse:
    """Enriquece resposta com dados calculados"""
    animal = db.query(Animal).filter(Animal.ID == crescimento.ID_ANIMAL).first()

    # Buscar medição anterior para calcular ganho
    medicao_anterior = (
        db.query(HistoricoCrescimento)
        .filter(
            HistoricoCrescimento.ID_ANIMAL == crescimento.ID_ANIMAL,
            HistoricoCrescimento.DATA_MEDICAO < crescimento.DATA_MEDICAO,
        )
        .order_by(desc(HistoricoCrescimento.DATA_MEDICAO))
        .first()
    )

    ganho_peso = None
    dias_desde_ultima = None

    if medicao_anterior:
        if crescimento.PESO and medicao_anterior.PESO:
            ganho_peso = crescimento.PESO - medicao_anterior.PESO

        dias_desde_ultima = (
            crescimento.DATA_MEDICAO - medicao_anterior.DATA_MEDICAO
        ).days

    response_data = CrescimentoResponse.from_orm(crescimento)
    response_data.animal_nome = animal.NOME if animal else None
    response_data.ganho_peso = ganho_peso
    response_data.dias_desde_ultima = dias_desde_ultima

    return response_data
