# backend/app/api/v1/ferrageamento.py
from datetime import date, datetime, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.animal import Animal
from app.models.saude import SaudeAnimais
from app.models.user import User
from app.schemas.ferrageamento import (
    AlertaVencimento,
    EstatisticasFerrageamento,
    FerrageamentoCreate,
    FerrageamentoRapido,
    FerrageamentoResponse,
    FerrageamentoUpdate,
    RelatorioFerrageamento,
    TipoFerrageamentoEnum,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, func
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
        intervalo = dias_intervalo.get(registro.TIPO_REGISTRO.value, 45)
        registro.PROXIMA_AVALIACAO = registro.DATA_OCORRENCIA + timedelta(
            days=intervalo
        )

    # Criar registro na tabela saude_animais
    db_registro = SaudeAnimais(
        ID_ANIMAL=registro.ID_ANIMAL,
        TIPO_REGISTRO=registro.TIPO_REGISTRO.value,
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

    # Buscar dados completos para response
    resultado = (
        db.query(SaudeAnimais, Animal.NOME.label("animal_nome"))
        .join(Animal, SaudeAnimais.ID_ANIMAL == Animal.ID)
        .filter(SaudeAnimais.ID == db_registro.ID)
        .first()
    )

    response_data = FerrageamentoResponse.model_validate(resultado[0])
    response_data.animal_nome = resultado[1]

    return response_data


@router.get("/", response_model=dict)
async def list_ferrageamentos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    animal_id: Optional[int] = Query(None),
    tipo_registro: Optional[TipoFerrageamentoEnum] = Query(None),
    ferrador: Optional[str] = Query(None),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=100),
):
    """Listar registros de ferrageamento com filtros e paginação"""
    offset = (page - 1) * limit

    query = (
        db.query(SaudeAnimais, Animal.NOME.label("animal_nome"))
        .join(Animal, SaudeAnimais.ID_ANIMAL == Animal.ID)
        .filter(
            SaudeAnimais.TIPO_REGISTRO.in_(
                [
                    "FERRAGEAMENTO",
                    "CASQUEAMENTO",
                    "FERRAGEAMENTO_CORRETIVO",
                    "CASQUEAMENTO_TERAPEUTICO",
                ]
            )
        )
    )

    # Aplicar filtros
    if animal_id:
        query = query.filter(SaudeAnimais.ID_ANIMAL == animal_id)

    if tipo_registro:
        query = query.filter(SaudeAnimais.TIPO_REGISTRO == tipo_registro.value)

    if ferrador:
        query = query.filter(SaudeAnimais.FERRADOR_RESPONSAVEL.ilike(f"%{ferrador}%"))

    if data_inicio:
        query = query.filter(
            SaudeAnimais.DATA_OCORRENCIA >= datetime.fromisoformat(data_inicio)
        )

    if data_fim:
        query = query.filter(
            SaudeAnimais.DATA_OCORRENCIA <= datetime.fromisoformat(data_fim)
        )

    # Contar total
    total = query.count()

    # Ordenar e paginar
    registros = (
        query.order_by(desc(SaudeAnimais.DATA_OCORRENCIA))
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Preparar response
    resultado = []
    for registro, animal_nome in registros:
        response_data = FerrageamentoResponse.model_validate(registro)
        response_data.animal_nome = animal_nome

        # Calcular dias até próxima avaliação
        if registro.PROXIMA_AVALIACAO:
            data_avaliacao = registro.PROXIMA_AVALIACAO.date()
            data_hoje = datetime.now().date()
            delta = (data_avaliacao - data_hoje).days

            response_data.dias_proxima_avaliacao = delta

            # Determinar status de vencimento
            if delta < 0:
                response_data.status_vencimento = "VENCIDO"
            elif delta <= 7:
                response_data.status_vencimento = "VENCE_SEMANA"
            elif delta <= 15:
                response_data.status_vencimento = "VENCE_QUINZENA"
            else:
                response_data.status_vencimento = "EM_DIA"
        else:
            response_data.status_vencimento = "SEM_AGENDAMENTO"

        resultado.append(response_data)

    return {
        "ferrageamentos": resultado,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
    }


@router.get("/{registro_id}", response_model=FerrageamentoResponse)
async def get_ferrageamento(
    registro_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obter registro específico de ferrageamento"""
    resultado = (
        db.query(SaudeAnimais, Animal.NOME.label("animal_nome"))
        .join(Animal, SaudeAnimais.ID_ANIMAL == Animal.ID)
        .filter(
            SaudeAnimais.ID == registro_id,
            SaudeAnimais.TIPO_REGISTRO.in_(
                [
                    "FERRAGEAMENTO",
                    "CASQUEAMENTO",
                    "FERRAGEAMENTO_CORRETIVO",
                    "CASQUEAMENTO_TERAPEUTICO",
                ]
            ),
        )
        .first()
    )

    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de ferrageamento não encontrado",
        )

    registro, animal_nome = resultado
    response_data = FerrageamentoResponse.model_validate(registro)
    response_data.animal_nome = animal_nome

    return response_data


@router.put("/{registro_id}", response_model=FerrageamentoResponse)
async def update_ferrageamento(
    registro_id: int,
    dados: FerrageamentoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualizar registro de ferrageamento"""
    registro = (
        db.query(SaudeAnimais)
        .filter(
            SaudeAnimais.ID == registro_id,
            SaudeAnimais.TIPO_REGISTRO.in_(
                [
                    "FERRAGEAMENTO",
                    "CASQUEAMENTO",
                    "FERRAGEAMENTO_CORRETIVO",
                    "CASQUEAMENTO_TERAPEUTICO",
                ]
            ),
        )
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

    return FerrageamentoResponse.model_validate(registro)


@router.delete("/{registro_id}")
async def delete_ferrageamento(
    registro_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Excluir registro de ferrageamento"""
    registro = (
        db.query(SaudeAnimais)
        .filter(
            SaudeAnimais.ID == registro_id,
            SaudeAnimais.TIPO_REGISTRO.in_(
                [
                    "FERRAGEAMENTO",
                    "CASQUEAMENTO",
                    "FERRAGEAMENTO_CORRETIVO",
                    "CASQUEAMENTO_TERAPEUTICO",
                ]
            ),
        )
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
    intervalo = dias_intervalo.get(dados.TIPO_REGISTRO.value, 45)
    proxima_data = datetime.now() + timedelta(days=intervalo)

    # Criar registro
    db_registro = SaudeAnimais(
        ID_ANIMAL=dados.ID_ANIMAL,
        TIPO_REGISTRO=dados.TIPO_REGISTRO.value,
        DATA_OCORRENCIA=datetime.now(),
        DESCRICAO=f"{dados.TIPO_REGISTRO.value} - Aplicação rápida",
        MEMBRO_TRATADO=dados.MEMBRO_TRATADO.value,
        FERRADOR_RESPONSAVEL=dados.FERRADOR_RESPONSAVEL,
        STATUS_CASCO=dados.STATUS_CASCO.value,
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
    current_user: User = Depends(get_current_user),
    dias_antecedencia: int = Query(15, description="Dias de antecedência para alerta"),
):
    """Obter alertas de vencimento"""
    data_limite = datetime.now() + timedelta(days=dias_antecedencia)

    query = (
        db.query(SaudeAnimais, Animal.NOME)
        .join(Animal, SaudeAnimais.ID_ANIMAL == Animal.ID)
        .filter(
            SaudeAnimais.TIPO_REGISTRO.in_(
                [
                    "FERRAGEAMENTO",
                    "CASQUEAMENTO",
                    "FERRAGEAMENTO_CORRETIVO",
                    "CASQUEAMENTO_TERAPEUTICO",
                ]
            ),
            SaudeAnimais.PROXIMA_AVALIACAO.isnot(None),
            SaudeAnimais.PROXIMA_AVALIACAO <= data_limite,
        )
        .order_by(asc(SaudeAnimais.PROXIMA_AVALIACAO))
    )

    registros = query.all()

    alertas = []
    for registro, animal_nome in registros:
        data_proxima = registro.PROXIMA_AVALIACAO.date()
        data_hoje = datetime.now().date()
        dias_vencimento = (data_proxima - data_hoje).days

        if dias_vencimento < 0:
            status_vencimento = "VENCIDO"
        elif dias_vencimento <= 7:
            status_vencimento = "VENCE_SEMANA"
        else:
            status_vencimento = "VENCE_QUINZENA"

        alerta = AlertaVencimento(
            animal_id=registro.ID_ANIMAL,
            animal_nome=animal_nome,
            tipo_registro=registro.TIPO_REGISTRO,
            data_vencimento=registro.PROXIMA_AVALIACAO,
            dias_vencimento=dias_vencimento,
            status_vencimento=status_vencimento,
            ferrador_anterior=registro.FERRADOR_RESPONSAVEL,
            custo_estimado=registro.CUSTO,
        )
        alertas.append(alerta)

    return alertas


@router.get("/estatisticas/animais", response_model=List[EstatisticasFerrageamento])
async def get_estatisticas_animais(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    meses_periodo: int = Query(12, description="Período em meses para análise"),
):
    """Estatísticas de ferrageamento por animal"""
    data_limite = datetime.now() - timedelta(days=meses_periodo * 30)

    # Buscar animais com registros
    animais_query = (
        db.query(Animal.ID, Animal.NOME)
        .join(SaudeAnimais, Animal.ID == SaudeAnimais.ID_ANIMAL)
        .filter(
            SaudeAnimais.TIPO_REGISTRO.in_(
                [
                    "FERRAGEAMENTO",
                    "CASQUEAMENTO",
                    "FERRAGEAMENTO_CORRETIVO",
                    "CASQUEAMENTO_TERAPEUTICO",
                ]
            ),
            SaudeAnimais.DATA_OCORRENCIA >= data_limite,
        )
        .distinct()
        .all()
    )

    estatisticas = []
    for animal_id, animal_nome in animais_query:
        # Buscar registros do animal
        registros = (
            db.query(SaudeAnimais)
            .filter(
                SaudeAnimais.ID_ANIMAL == animal_id,
                SaudeAnimais.TIPO_REGISTRO.in_(
                    [
                        "FERRAGEAMENTO",
                        "CASQUEAMENTO",
                        "FERRAGEAMENTO_CORRETIVO",
                        "CASQUEAMENTO_TERAPEUTICO",
                    ]
                ),
                SaudeAnimais.DATA_OCORRENCIA >= data_limite,
            )
            .all()
        )

        # Contar tipos
        ferrageamentos = [r for r in registros if "FERRAGEAMENTO" in r.TIPO_REGISTRO]
        casqueamentos = [r for r in registros if "CASQUEAMENTO" in r.TIPO_REGISTRO]

        # Calcular custos
        custo_total = sum(r.CUSTO for r in registros if r.CUSTO)

        # Últimas datas
        ultimo_ferrageamento = (
            max([r.DATA_OCORRENCIA for r in ferrageamentos]) if ferrageamentos else None
        )
        ultimo_casqueamento = (
            max([r.DATA_OCORRENCIA for r in casqueamentos]) if casqueamentos else None
        )

        # Ferrador principal
        ferradores = [
            r.FERRADOR_RESPONSAVEL for r in registros if r.FERRADOR_RESPONSAVEL
        ]
        ferrador_principal = (
            max(set(ferradores), key=ferradores.count) if ferradores else None
        )

        # Status atual e próxima data
        ultimo_registro = (
            max(registros, key=lambda x: x.DATA_OCORRENCIA) if registros else None
        )
        status_atual = ultimo_registro.STATUS_CASCO if ultimo_registro else None
        proxima_data = ultimo_registro.PROXIMA_AVALIACAO if ultimo_registro else None

        # Status de vencimento
        status_vencimento = "SEM_AGENDAMENTO"
        if proxima_data:
            dias = (proxima_data - datetime.now()).days
            if dias < 0:
                status_vencimento = "VENCIDO"
            elif dias <= 7:
                status_vencimento = "VENCE_SEMANA"
            elif dias <= 15:
                status_vencimento = "VENCE_QUINZENA"
            else:
                status_vencimento = "EM_DIA"

        estatistica = EstatisticasFerrageamento(
            animal_id=animal_id,
            animal_nome=animal_nome,
            total_ferrageamentos=len(ferrageamentos),
            total_casqueamentos=len(casqueamentos),
            custo_total=custo_total if custo_total > 0 else None,
            ultimo_ferrageamento=ultimo_ferrageamento,
            ultimo_casqueamento=ultimo_casqueamento,
            status_atual_casco=status_atual,
            ferrador_principal=ferrador_principal,
            proxima_data=proxima_data,
            status_vencimento=status_vencimento,
        )
        estatisticas.append(estatistica)

    # Ordenar por status de vencimento (vencidos primeiro)
    ordem_status = {
        "VENCIDO": 0,
        "VENCE_SEMANA": 1,
        "VENCE_QUINZENA": 2,
        "EM_DIA": 3,
        "SEM_AGENDAMENTO": 4,
    }
    estatisticas.sort(key=lambda x: ordem_status.get(x.status_vencimento, 5))

    return estatisticas


@router.get("/relatorio/resumo", response_model=RelatorioFerrageamento)
async def get_relatorio(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data_inicio: date = Query(..., description="Data início do relatório"),
    data_fim: date = Query(..., description="Data fim do relatório"),
    animal_id: Optional[int] = Query(None, description="ID específico do animal"),
    tipo_registro: Optional[TipoFerrageamentoEnum] = Query(
        None, description="Tipo específico"
    ),
):
    """Gerar relatório completo de ferrageamento"""
    # Query base
    query = (
        db.query(SaudeAnimais, Animal.NOME.label("animal_nome"))
        .join(Animal, SaudeAnimais.ID_ANIMAL == Animal.ID)
        .filter(
            SaudeAnimais.TIPO_REGISTRO.in_(
                [
                    "FERRAGEAMENTO",
                    "CASQUEAMENTO",
                    "FERRAGEAMENTO_CORRETIVO",
                    "CASQUEAMENTO_TERAPEUTICO",
                ]
            ),
            SaudeAnimais.DATA_OCORRENCIA >= data_inicio,
            SaudeAnimais.DATA_OCORRENCIA <= data_fim,
        )
    )

    # Aplicar filtros opcionais
    if animal_id:
        query = query.filter(SaudeAnimais.ID_ANIMAL == animal_id)

    if tipo_registro:
        query = query.filter(SaudeAnimais.TIPO_REGISTRO == tipo_registro.value)

    registros_raw = query.order_by(desc(SaudeAnimais.DATA_OCORRENCIA)).all()

    # Preparar dados do relatório
    registros = []
    custo_total = 0
    animais_atendidos = set()
    ferradores = set()
    tipos_contagem = {}
    problemas = []

    for registro, animal_nome in registros_raw:
        # Adicionar aos registros
        response_registro = FerrageamentoResponse.model_validate(registro)
        response_registro.animal_nome = animal_nome
        registros.append(response_registro)

        # Coletar estatísticas
        if registro.CUSTO:
            custo_total += registro.CUSTO

        animais_atendidos.add(registro.ID_ANIMAL)

        if registro.FERRADOR_RESPONSAVEL:
            ferradores.add(registro.FERRADOR_RESPONSAVEL)

        # Contar tipos
        tipo = registro.TIPO_REGISTRO
        tipos_contagem[tipo] = tipos_contagem.get(tipo, 0) + 1

        # Coletar problemas
        if registro.PROBLEMA_DETECTADO:
            problemas.append(registro.PROBLEMA_DETECTADO)

    # Problemas mais comuns
    problemas_comuns = []
    if problemas:
        palavras_problemas = []
        for problema in problemas:
            palavras_problemas.extend(problema.lower().split())

        # Palavras-chave relevantes
        keywords = ["rachadura", "laminite", "sensibilidade", "ferimento", "inflamação"]
        for keyword in keywords:
            if any(keyword in palavra for palavra in palavras_problemas):
                problemas_comuns.append(keyword.title())

    relatorio = RelatorioFerrageamento(
        periodo_inicio=data_inicio,
        periodo_fim=data_fim,
        total_registros=len(registros),
        custo_total=custo_total if custo_total > 0 else None,
        animais_atendidos=len(animais_atendidos),
        ferradores_utilizados=len(ferradores),
        tipos_mais_realizados=tipos_contagem,
        problemas_mais_comuns=problemas_comuns,
        registros=registros,
    )

    return relatorio
