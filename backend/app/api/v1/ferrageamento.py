# backend/app/api/v1/ferrageamento.py
from datetime import datetime, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.animal import Animal
from app.models.ferrageamento import FerrageamentoAnimais  # NOVO MODELO
from app.models.user import User
from app.schemas.ferrageamento import (
    AlertaVencimento,
    EstatisticasFerrageamento,
    FerradorEstatisticas,
    FerrageamentoCreate,
    FerrageamentoRapido,
    FerrageamentoResponse,
    FerrageamentoUpdate,
    RelatorioFerrageamento,
    TipoFerrageamentoEnum,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, extract, func
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/ferrageamento", tags=["Ferrageamento"])


@router.post(
    "/", response_model=FerrageamentoResponse, status_code=status.HTTP_201_CREATED
)
async def create_ferrageamento(
    registro: FerrageamentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Criar novo registro de ferrageamento/casqueamento"""
    # Verificar se animal existe
    animal = db.query(Animal).filter(Animal.ID == registro.ID_ANIMAL).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    # Calcular próxima avaliação se não foi informada
    if not registro.PROXIMA_AVALIACAO:
        dias_intervalo = {
            "FERRAGEAMENTO": 45,
            "CASQUEAMENTO": 40,
            "FERRAGEAMENTO_CORRETIVO": 21,
            "CASQUEAMENTO_TERAPEUTICO": 21,
        }
        intervalo = dias_intervalo.get(registro.TIPO_FERRAGEAMENTO.value, 45)
        registro.PROXIMA_AVALIACAO = registro.DATA_OCORRENCIA + timedelta(
            days=intervalo
        )

    # Criar registro na nova tabela ferrageamento_animais
    db_registro = FerrageamentoAnimais(
        ID_ANIMAL=registro.ID_ANIMAL,
        TIPO_FERRAGEAMENTO=registro.TIPO_FERRAGEAMENTO.value,
        DATA_OCORRENCIA=registro.DATA_OCORRENCIA,
        DESCRICAO=registro.DESCRICAO,
        TIPO_FERRADURA=(
            registro.TIPO_FERRADURA.value if registro.TIPO_FERRADURA else None
        ),
        MEMBRO_TRATADO=registro.MEMBRO_TRATADO.value,
        PROBLEMA_DETECTADO=registro.PROBLEMA_DETECTADO,
        TECNICA_APLICADA=registro.TECNICA_APLICADA,
        FERRADOR_RESPONSAVEL=registro.FERRADOR_RESPONSAVEL,
        STATUS_CASCO=registro.STATUS_CASCO.value if registro.STATUS_CASCO else None,
        PROXIMA_AVALIACAO=registro.PROXIMA_AVALIACAO,
        CUSTO=registro.CUSTO,
        OBSERVACOES=registro.OBSERVACOES,
        ID_USUARIO_REGISTRO=current_user.ID,
        DATA_REGISTRO=func.now(),
    )

    db.add(db_registro)
    db.commit()
    db.refresh(db_registro)

    # Preparar resposta com dados do animal
    response_data = FerrageamentoResponse.model_validate(db_registro)
    response_data.animal_nome = animal.NOME

    return response_data


@router.get("/", response_model=List[FerrageamentoResponse])
async def get_ferrageamentos(
    db: Session = Depends(get_db),
    animal_id: Optional[int] = Query(None, description="Filtrar por animal"),
    tipo_ferrageamento: Optional[TipoFerrageamentoEnum] = Query(
        None, description="Filtrar por tipo"
    ),
    ferrador: Optional[str] = Query(None, description="Filtrar por ferrador"),
    apenas_vencidos: Optional[bool] = Query(
        False, description="Filtrar apenas vencidos"
    ),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
):
    """Listar registros de ferrageamento"""
    query = (
        db.query(FerrageamentoAnimais, Animal.NOME)
        .join(Animal, FerrageamentoAnimais.ID_ANIMAL == Animal.ID)
        .order_by(desc(FerrageamentoAnimais.DATA_OCORRENCIA))
    )

    # Aplicar filtros
    if animal_id:
        query = query.filter(FerrageamentoAnimais.ID_ANIMAL == animal_id)

    if tipo_ferrageamento:
        query = query.filter(
            FerrageamentoAnimais.TIPO_FERRAGEAMENTO == tipo_ferrageamento.value
        )

    if ferrador:
        query = query.filter(
            FerrageamentoAnimais.FERRADOR_RESPONSAVEL.ilike(f"%{ferrador}%")
        )

    if data_inicio:
        try:
            data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.filter(FerrageamentoAnimais.DATA_OCORRENCIA >= data_inicio_dt)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data inválido. Use YYYY-MM-DD",
            ) from e

    if data_fim:
        try:
            data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")
            query = query.filter(FerrageamentoAnimais.DATA_OCORRENCIA <= data_fim_dt)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data inválido. Use YYYY-MM-DD",
            ) from e

    if apenas_vencidos:
        try:
            data_hoje = datetime.now().date()
            query = query.filter(FerrageamentoAnimais.PROXIMA_AVALIACAO <= data_hoje)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data inválido. Use YYYY-MM-DD",
            ) from e

    registros = query.offset(offset).limit(limit).all()

    # Preparar resposta com nomes dos animais e dias para proxima avaliacao
    result = []
    for registro, animal_nome in registros:
        response_data = FerrageamentoResponse.model_validate(registro)
        data_proxima = registro.PROXIMA_AVALIACAO.date()
        data_hoje = datetime.now().date()
        dias_proxima_avaliacao = (data_proxima - data_hoje).days if data_proxima else 0

        if dias_proxima_avaliacao >= 30:
            status_vencimento = "EM_DIA"
        elif dias_proxima_avaliacao >= 0 and dias_proxima_avaliacao < 30:
            status_vencimento = "PROXIMO_VENCIMENTO"
        elif dias_proxima_avaliacao < 0:
            status_vencimento = "VENCIDO"
        else:
            status_vencimento = None

        response_data.animal_nome = animal_nome
        response_data.dias_proxima_avaliacao = dias_proxima_avaliacao
        response_data.status_vencimento = status_vencimento
        result.append(response_data)

    return result


@router.get("/{registro_id}", response_model=FerrageamentoResponse)
async def get_ferrageamento(
    registro_id: int,
    db: Session = Depends(get_db),
):
    """Obter registro específico de ferrageamento"""
    registro = (
        db.query(FerrageamentoAnimais, Animal.NOME)
        .join(Animal, FerrageamentoAnimais.ID_ANIMAL == Animal.ID)
        .filter(FerrageamentoAnimais.ID == registro_id)
        .first()
    )

    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado"
        )

    ferrageamento, animal_nome = registro
    response_data = FerrageamentoResponse.model_validate(ferrageamento)
    response_data.animal_nome = animal_nome

    return response_data


@router.put("/{registro_id}", response_model=FerrageamentoResponse)
async def update_ferrageamento(
    registro_id: int,
    dados: FerrageamentoUpdate,
    db: Session = Depends(get_db),
):
    """Atualizar registro de ferrageamento"""
    registro = (
        db.query(FerrageamentoAnimais)
        .filter(FerrageamentoAnimais.ID == registro_id)
        .first()
    )

    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado"
        )

    # Atualizar campos
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        if hasattr(registro, campo.upper()):
            if hasattr(valor, "value"):  # Enum
                setattr(registro, campo.upper(), valor.value)
            else:
                setattr(registro, campo.upper(), valor)

    db.commit()
    db.refresh(registro)

    # Buscar nome do animal para resposta
    animal = db.query(Animal).filter(Animal.ID == registro.ID_ANIMAL).first()
    response_data = FerrageamentoResponse.model_validate(registro)
    response_data.animal_nome = animal.NOME if animal else None

    return response_data


@router.delete("/{registro_id}")
async def delete_ferrageamento(
    registro_id: int,
    db: Session = Depends(get_db),
):
    """Excluir registro de ferrageamento"""
    registro = (
        db.query(FerrageamentoAnimais)
        .filter(FerrageamentoAnimais.ID == registro_id)
        .first()
    )

    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado"
        )

    db.delete(registro)
    db.commit()

    return {"message": "Registro excluído com sucesso"}


@router.post(
    "/aplicacao-rapida",
    response_model=FerrageamentoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def aplicacao_rapida(
    dados: FerrageamentoRapido,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aplicação rápida para mobile"""
    # Verificar se animal existe
    animal = db.query(Animal).filter(Animal.ID == dados.ID_ANIMAL).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    # Calcular próxima avaliação
    dias_intervalo = {
        "FERRAGEAMENTO": 45,
        "CASQUEAMENTO": 40,
        "FERRAGEAMENTO_CORRETIVO": 21,
        "CASQUEAMENTO_TERAPEUTICO": 21,
    }
    intervalo = dias_intervalo.get(dados.TIPO_FERRAGEAMENTO.value, 45)
    proxima_data = datetime.now() + timedelta(days=intervalo)

    # Criar registro
    db_registro = FerrageamentoAnimais(
        ID_ANIMAL=dados.ID_ANIMAL,
        TIPO_FERRAGEAMENTO=dados.TIPO_FERRAGEAMENTO.value,
        DATA_OCORRENCIA=datetime.now(),
        DESCRICAO=f"{dados.TIPO_FERRAGEAMENTO.value} - Aplicação rápida",
        MEMBRO_TRATADO=dados.MEMBRO_TRATADO.value,
        FERRADOR_RESPONSAVEL=dados.FERRADOR_RESPONSAVEL,
        STATUS_CASCO=dados.STATUS_CASCO.value if dados.STATUS_CASCO else None,
        PROXIMA_AVALIACAO=proxima_data,
        CUSTO=dados.CUSTO,
        OBSERVACOES=dados.OBSERVACOES,
        ID_USUARIO_REGISTRO=current_user.ID,
        DATA_REGISTRO=func.now(),
    )

    db.add(db_registro)
    db.commit()
    db.refresh(db_registro)

    response_data = FerrageamentoResponse.model_validate(db_registro)
    response_data.animal_nome = animal.NOME

    return response_data


@router.get("/alertas/vencimentos", response_model=List[AlertaVencimento])
async def get_alertas_vencimento(
    db: Session = Depends(get_db),
    dias_antecedencia: int = Query(15, description="Dias de antecedência para alerta"),
):
    """Obter alertas de vencimento"""
    data_limite = datetime.now() + timedelta(days=dias_antecedencia)

    query = (
        db.query(FerrageamentoAnimais, Animal.NOME)
        .join(Animal, FerrageamentoAnimais.ID_ANIMAL == Animal.ID)
        .filter(
            FerrageamentoAnimais.PROXIMA_AVALIACAO.isnot(None),
            FerrageamentoAnimais.PROXIMA_AVALIACAO <= data_limite,
        )
        .order_by(asc(FerrageamentoAnimais.PROXIMA_AVALIACAO))
    )

    registros = query.all()

    alertas = []
    for registro, animal_nome in registros:
        data_proxima = registro.PROXIMA_AVALIACAO.date()
        data_hoje = datetime.now().date()
        dias_vencimento = (data_proxima - data_hoje).days

        alerta = AlertaVencimento(
            animal_id=registro.ID_ANIMAL,
            animal_nome=animal_nome,
            tipo_ferrageamento=registro.TIPO_FERRAGEAMENTO,
            data_ultima=registro.DATA_OCORRENCIA,
            proxima_avaliacao=registro.PROXIMA_AVALIACAO,
            dias_vencimento=dias_vencimento,
            ferrador_anterior=registro.FERRADOR_RESPONSAVEL,
            custo_estimado=registro.CUSTO,
        )
        alertas.append(alerta)

    return alertas


@router.get("/estatisticas/geral", response_model=EstatisticasFerrageamento)
async def get_estatisticas_ferrageamento(
    db: Session = Depends(get_db),
    ano: Optional[int] = Query(None, description="Ano para estatísticas"),
    mes: Optional[int] = Query(None, description="Mês para estatísticas"),
):
    """Obter estatísticas gerais de ferrageamento"""
    base_query = db.query(FerrageamentoAnimais)

    if ano:
        base_query = base_query.filter(
            extract("year", FerrageamentoAnimais.DATA_OCORRENCIA) == ano
        )
    if mes:
        base_query = base_query.filter(
            extract("month", FerrageamentoAnimais.DATA_OCORRENCIA) == mes
        )

    # Estatísticas gerais
    total_registros = base_query.count()

    # Registros do mês atual
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    registros_mes_atual = (
        db.query(FerrageamentoAnimais)
        .filter(
            extract("year", FerrageamentoAnimais.DATA_OCORRENCIA) == ano_atual,
            extract("month", FerrageamentoAnimais.DATA_OCORRENCIA) == mes_atual,
        )
        .count()
    )

    # Custo total do mês
    custo_mes = (
        db.query(func.sum(FerrageamentoAnimais.CUSTO))
        .filter(
            extract("year", FerrageamentoAnimais.DATA_OCORRENCIA) == ano_atual,
            extract("month", FerrageamentoAnimais.DATA_OCORRENCIA) == mes_atual,
        )
        .scalar()
        or 0
    )

    # Ferradores ativos
    ferradores_ativos = (
        db.query(func.count(func.distinct(FerrageamentoAnimais.FERRADOR_RESPONSAVEL)))
        .filter(FerrageamentoAnimais.FERRADOR_RESPONSAVEL.isnot(None))
        .scalar()
        or 0
    )

    # Próximas avaliações (próximos 30 dias)
    data_limite = datetime.now() + timedelta(days=30)
    proximas_avaliacoes = (
        db.query(FerrageamentoAnimais)
        .filter(
            FerrageamentoAnimais.PROXIMA_AVALIACAO.between(datetime.now(), data_limite)
        )
        .count()
    )

    # Animais atrasados
    animais_atrasados = (
        db.query(FerrageamentoAnimais)
        .filter(FerrageamentoAnimais.PROXIMA_AVALIACAO < datetime.now())
        .count()
    )

    # Breakdown por tipo
    tipos = [
        "FERRAGEAMENTO",
        "CASQUEAMENTO",
        "FERRAGEAMENTO_CORRETIVO",
        "CASQUEAMENTO_TERAPEUTICO",
    ]
    totals_por_tipo = {}
    for tipo in tipos:
        total = base_query.filter(
            FerrageamentoAnimais.TIPO_FERRAGEAMENTO == tipo
        ).count()
        totals_por_tipo[tipo] = total

    return EstatisticasFerrageamento(
        total_registros=total_registros,
        registros_mes_atual=registros_mes_atual,
        custo_total_mes=custo_mes,
        ferradores_ativos=ferradores_ativos,
        proximas_avaliacoes=proximas_avaliacoes,
        animais_atrasados=animais_atrasados,
        total_ferrageamento=totals_por_tipo.get("FERRAGEAMENTO", 0),
        total_casqueamento=totals_por_tipo.get("CASQUEAMENTO", 0),
        total_corretivo=totals_por_tipo.get("FERRAGEAMENTO_CORRETIVO", 0),
        total_terapeutico=totals_por_tipo.get("CASQUEAMENTO_TERAPEUTICO", 0),
    )


@router.get("/relatorios/ferradores", response_model=List[FerradorEstatisticas])
async def get_relatorio_ferradores(
    db: Session = Depends(get_db),
    ano: Optional[int] = Query(None, description="Ano para relatório"),
):
    """Relatório de estatísticas por ferrador"""
    base_query = db.query(FerrageamentoAnimais).filter(
        FerrageamentoAnimais.FERRADOR_RESPONSAVEL.isnot(None)
    )

    if ano:
        base_query = base_query.filter(
            extract("year", FerrageamentoAnimais.DATA_OCORRENCIA) == ano
        )

    # Agrupar por ferrador
    ferradores_stats = (
        base_query.with_entities(
            FerrageamentoAnimais.FERRADOR_RESPONSAVEL,
            func.count(FerrageamentoAnimais.ID).label("total_atendimentos"),
            func.sum(FerrageamentoAnimais.CUSTO).label("custo_total"),
            func.max(FerrageamentoAnimais.DATA_OCORRENCIA).label("ultima_atividade"),
        )
        .group_by(FerrageamentoAnimais.FERRADOR_RESPONSAVEL)
        .order_by(desc("total_atendimentos"))
        .all()
    )

    resultado = []
    for stats in ferradores_stats:
        ferrador_stat = FerradorEstatisticas(
            ferrador_nome=stats.FERRADOR_RESPONSAVEL,
            total_atendimentos=stats.total_atendimentos,
            custo_total=stats.custo_total or 0,
            ultima_atividade=stats.ultima_atividade,
        )
        resultado.append(ferrador_stat)

    return resultado


@router.get("/relatorios/detalhado", response_model=List[RelatorioFerrageamento])
async def get_relatorio_detalhado(
    db: Session = Depends(get_db),
    animal_id: Optional[int] = Query(None, description="Filtrar por animal"),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
):
    """Relatório detalhado de ferrageamento"""
    query = (
        db.query(FerrageamentoAnimais, Animal.NOME)
        .join(Animal, FerrageamentoAnimais.ID_ANIMAL == Animal.ID)
        .order_by(desc(FerrageamentoAnimais.DATA_OCORRENCIA))
    )

    if animal_id:
        query = query.filter(FerrageamentoAnimais.ID_ANIMAL == animal_id)

    if data_inicio:
        try:
            data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.filter(FerrageamentoAnimais.DATA_OCORRENCIA >= data_inicio_dt)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data inválido. Use YYYY-MM-DD",
            ) from e

    if data_fim:
        try:
            data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")
            query = query.filter(FerrageamentoAnimais.DATA_OCORRENCIA <= data_fim_dt)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data inválido. Use YYYY-MM-DD",
            ) from e

    registros = query.all()

    resultado = []
    for registro, animal_nome in registros:
        relatorio_item = RelatorioFerrageamento(
            animal_nome=animal_nome,
            tipo_ferrageamento=registro.TIPO_FERRAGEAMENTO,
            data_ocorrencia=registro.DATA_OCORRENCIA,
            ferrador_responsavel=registro.FERRADOR_RESPONSAVEL,
            status_casco=registro.STATUS_CASCO,
            proxima_avaliacao=registro.PROXIMA_AVALIACAO,
            custo=registro.CUSTO,
        )
        resultado.append(relatorio_item)

    return resultado
