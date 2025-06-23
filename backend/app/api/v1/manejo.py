# backend/app/api/v1/manejo.py
import os
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, desc
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.manejo import ProdutoManejo, AnalisesSolo, ManejoTerrenos
from app.models.terreno import Terreno
from app.models.movimentacao import MovimentacaoAnimais
from app.models.user import User
from app.schemas.manejo import (
    ProdutoManejoCreate, ProdutoManejoUpdate, ProdutoManejoResponse,
    AnalisesSoloCreate, AnalisesSoloUpdate, AnalisesSoloResponse,
    ManejoTerrenosCreate, ManejoTerrenosUpdate, ManejoTerrenosResponse,
    TipoProdutoEnum, TipoManejoEnum,
    CronogramaAplicacoes, CapacidadeOcupacao, HistoricoNutricional
)

router = APIRouter(prefix="/api/manejo", tags=["Manejo de Terrenos"])

# Diretório para upload de laudos
UPLOAD_DIR = Path("uploads/laudos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# === PRODUTOS MANEJO ===


@router.post("/produtos", response_model=ProdutoManejoResponse, status_code=status.HTTP_201_CREATED)
async def create_produto(
    produto: ProdutoManejoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar duplicatas
    existing = db.query(ProdutoManejo).filter(
        ProdutoManejo.NOME == produto.NOME,
        ProdutoManejo.ATIVO == 'S'
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produto com este nome já existe"
        )

    db_produto = ProdutoManejo(**produto.dict())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto


@router.get("/produtos", response_model=dict)
async def list_produtos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tipo_produto: Optional[TipoProdutoEnum] = Query(
        None, description="Filtrar por tipo"),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    ativo: Optional[str] = Query("S", description="Filtrar por status"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    query = db.query(ProdutoManejo)

    if tipo_produto:
        query = query.filter(ProdutoManejo.TIPO_PRODUTO == tipo_produto)
    if nome:
        query = query.filter(ProdutoManejo.NOME.ilike(f"%{nome}%"))
    if ativo:
        query = query.filter(ProdutoManejo.ATIVO == ativo)

    total = query.count()
    offset = (page - 1) * limit
    produtos = query.order_by(ProdutoManejo.NOME).offset(
        offset).limit(limit).all()

    return {
        "produtos": [ProdutoManejoResponse.from_orm(p) for p in produtos],
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/produtos/{id}", response_model=ProdutoManejoResponse)
async def get_produto(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    produto = db.query(ProdutoManejo).filter(ProdutoManejo.ID == id).first()
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Produto não encontrado")
    return produto


@router.put("/produtos/{id}", response_model=ProdutoManejoResponse)
async def update_produto(
    id: int,
    produto: ProdutoManejoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_produto = db.query(ProdutoManejo).filter(ProdutoManejo.ID == id).first()
    if not db_produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Produto não encontrado")

    for key, value in produto.dict(exclude_unset=True).items():
        setattr(db_produto, key, value)

    db.commit()
    db.refresh(db_produto)
    return db_produto


@router.delete("/produtos/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_produto(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_produto = db.query(ProdutoManejo).filter(ProdutoManejo.ID == id).first()
    if not db_produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Produto não encontrado")

    # Verificar se produto está sendo usado
    manejo_ativo = db.query(ManejoTerrenos).filter(
        ManejoTerrenos.ID_PRODUTO == id).first()
    if manejo_ativo:
        # Soft delete
        db_produto.ATIVO = 'N'
    else:
        # Hard delete
        db.delete(db_produto)

    db.commit()

# === ANÁLISES DE SOLO ===


@router.post("/analises-solo", response_model=AnalisesSoloResponse, status_code=status.HTTP_201_CREATED)
async def create_analise_solo(
    analise: AnalisesSoloCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar se terreno existe
    terreno = db.query(Terreno).filter(
        Terreno.ID == analise.ID_TERRENO).first()
    if not terreno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Terreno não encontrado")

    db_analise = AnalisesSolo(**analise.dict())
    db.add(db_analise)
    db.commit()
    db.refresh(db_analise)

    return await _enrich_analise_response(db_analise, db)


@router.get("/analises-solo", response_model=dict)
async def list_analises_solo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    terreno_id: Optional[int] = Query(None, description="Filtrar por terreno"),
    data_inicio: Optional[str] = Query(
        None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    query = db.query(AnalisesSolo)

    if terreno_id:
        query = query.filter(AnalisesSolo.ID_TERRENO == terreno_id)
    if data_inicio:
        query = query.filter(AnalisesSolo.DATA_COLETA >=
                             datetime.fromisoformat(data_inicio))
    if data_fim:
        query = query.filter(AnalisesSolo.DATA_COLETA <=
                             datetime.fromisoformat(data_fim))

    total = query.count()
    offset = (page - 1) * limit
    analises = query.order_by(desc(AnalisesSolo.DATA_COLETA)).offset(
        offset).limit(limit).all()

    # Enriquecer com dados relacionados
    enriched_analises = []
    for analise in analises:
        enriched = await _enrich_analise_response(analise, db)
        enriched_analises.append(enriched)

    return {
        "analises": enriched_analises,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/analises-solo/{id}", response_model=AnalisesSoloResponse)
async def get_analise_solo(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    analise = db.query(AnalisesSolo).filter(AnalisesSolo.ID == id).first()
    if not analise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Análise não encontrada")
    return await _enrich_analise_response(analise, db)


@router.put("/analises-solo/{id}", response_model=AnalisesSoloResponse)
async def update_analise_solo(
    id: int,
    analise: AnalisesSoloUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_analise = db.query(AnalisesSolo).filter(AnalisesSolo.ID == id).first()
    if not db_analise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Análise não encontrada")

    for key, value in analise.dict(exclude_unset=True).items():
        setattr(db_analise, key, value)

    db.commit()
    db.refresh(db_analise)
    return await _enrich_analise_response(db_analise, db)


@router.delete("/analises-solo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analise_solo(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_analise = db.query(AnalisesSolo).filter(AnalisesSolo.ID == id).first()
    if not db_analise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Análise não encontrada")

    db.delete(db_analise)
    db.commit()
    return await _enrich_analise_response(db_analise, db)


@router.post("/analises-solo/{id}/upload-laudo")
async def upload_laudo(
    id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analise = db.query(AnalisesSolo).filter(AnalisesSolo.ID == id).first()
    if not analise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Análise não encontrada")

    # Validar tipo de arquivo
    if not arquivo.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Apenas arquivos PDF são permitidos")

    # Salvar arquivo
    filename = f"laudo_{id}_{int(datetime.now().timestamp())}.pdf"
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    # Atualizar registro
    analise.ARQUIVO_LAUDO = f"/uploads/laudos/{filename}"
    db.commit()

    return {"message": "Laudo enviado com sucesso", "arquivo": f"/uploads/laudos/{filename}"}

# === MANEJO TERRENOS ===


@router.post("/aplicacoes", response_model=ManejoTerrenosResponse, status_code=status.HTTP_201_CREATED)
async def create_manejo(
    manejo: ManejoTerrenosCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar se terreno e produto existem
    terreno = db.query(Terreno).filter(Terreno.ID == manejo.ID_TERRENO).first()
    if not terreno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Terreno não encontrado")

    produto = db.query(ProdutoManejo).filter(
        ProdutoManejo.ID == manejo.ID_PRODUTO).first()
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Produto não encontrado")

    db_manejo = ManejoTerrenos(**manejo.dict())
    db.add(db_manejo)
    db.commit()
    db.refresh(db_manejo)

    return await _enrich_manejo_response(db_manejo, db)


@router.get("/aplicacoes", response_model=dict)
async def list_manejos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    terreno_id: Optional[int] = Query(None, description="Filtrar por terreno"),
    tipo_manejo: Optional[TipoManejoEnum] = Query(
        None, description="Filtrar por tipo"),
    data_inicio: Optional[str] = Query(
        None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    query = db.query(ManejoTerrenos)

    if terreno_id:
        query = query.filter(ManejoTerrenos.ID_TERRENO == terreno_id)
    if tipo_manejo:
        query = query.filter(ManejoTerrenos.TIPO_MANEJO == tipo_manejo)
    if data_inicio:
        query = query.filter(ManejoTerrenos.DATA_APLICACAO >=
                             datetime.fromisoformat(data_inicio))
    if data_fim:
        query = query.filter(ManejoTerrenos.DATA_APLICACAO <=
                             datetime.fromisoformat(data_fim))

    total = query.count()
    offset = (page - 1) * limit
    manejos = query.order_by(desc(ManejoTerrenos.DATA_APLICACAO)).offset(
        offset).limit(limit).all()

    # Enriquecer com dados relacionados
    enriched_manejos = []
    for manejo in manejos:
        enriched = await _enrich_manejo_response(manejo, db)
        enriched_manejos.append(enriched)

    return {
        "aplicacoes": enriched_manejos,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/aplicacoes/{id}", response_model=ManejoTerrenosResponse)
async def get_manejo(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    manejo = db.query(ManejoTerrenos).filter(ManejoTerrenos.ID == id).first()
    if not manejo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Aplicação não encontrada")
    return await _enrich_manejo_response(manejo, db)


@router.put("/aplicacoes/{id}", response_model=ManejoTerrenosResponse)
async def update_manejo(
    id: int,
    manejo: ManejoTerrenosUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_manejo = db.query(ManejoTerrenos).filter(
        ManejoTerrenos.ID == id).first()
    if not db_manejo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Aplicação não encontrada")

    for key, value in manejo.dict(exclude_unset=True).items():
        setattr(db_manejo, key, value)

    db.commit()
    db.refresh(db_manejo)
    return await _enrich_manejo_response(db_manejo, db)


@router.delete("/aplicacoes/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_manejo(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_manejo = db.query(ManejoTerrenos).filter(
        ManejoTerrenos.ID == id).first()
    if not db_manejo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Aplicação não encontrada")

    db.delete(db_manejo)
    db.commit()

# === VALIDAÇÃO DE MOVIMENTAÇÕES ===


@router.get("/terrenos-bloqueados", response_model=List[dict])
async def get_terrenos_bloqueados(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna terrenos que estão em período de carência"""
    hoje = datetime.now()

    terrenos_bloqueados = db.query(ManejoTerrenos, Terreno.NOME)\
        .join(Terreno)\
        .filter(ManejoTerrenos.DATA_LIBERACAO > hoje)\
        .order_by(ManejoTerrenos.DATA_LIBERACAO)\
        .all()

    resultado = []
    for manejo, terreno_nome in terrenos_bloqueados:
        dias_restantes = (manejo.DATA_LIBERACAO - hoje).days
        resultado.append({
            "terreno_id": manejo.ID_TERRENO,
            "terreno_nome": terreno_nome,
            "tipo_manejo": manejo.TIPO_MANEJO,
            "data_aplicacao": manejo.DATA_APLICACAO.strftime("%d/%m/%Y"),
            "data_liberacao": manejo.DATA_LIBERACAO.strftime("%d/%m/%Y"),
            "dias_restantes": dias_restantes
        })

    return resultado


@router.post("/validar-movimentacao")
async def validar_movimentacao_terreno(
    terreno_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Valida se terreno pode receber animais (não está em carência)"""
    hoje = datetime.now()

    bloqueio = db.query(ManejoTerrenos)\
        .filter(ManejoTerrenos.ID_TERRENO == terreno_id)\
        .filter(ManejoTerrenos.DATA_LIBERACAO > hoje)\
        .first()

    if bloqueio:
        dias_restantes = (bloqueio.DATA_LIBERACAO - hoje).days
        return {
            "pode_mover": False,
            "motivo": f"Terreno em carência por {bloqueio.TIPO_MANEJO}",
            "data_liberacao": bloqueio.DATA_LIBERACAO.strftime("%d/%m/%Y"),
            "dias_restantes": dias_restantes
        }

    return {"pode_mover": True}

# === RELATÓRIOS ===


@router.get("/relatorio/cronograma", response_model=List[CronogramaAplicacoes])
async def get_cronograma_aplicacoes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    dias: int = Query(30, description="Próximos X dias"),
    terreno_id: Optional[int] = Query(None, description="Filtrar por terreno")
):
    """Cronograma de aplicações e liberações"""
    data_limite = datetime.now() + timedelta(days=dias)

    query = db.query(ManejoTerrenos, Terreno.NOME, ProdutoManejo.NOME)\
        .join(Terreno)\
        .join(ProdutoManejo)\
        .filter(ManejoTerrenos.DATA_APLICACAO <= data_limite)

    if terreno_id:
        query = query.filter(ManejoTerrenos.ID_TERRENO == terreno_id)

    aplicacoes = query.order_by(ManejoTerrenos.DATA_APLICACAO).all()

    resultado = []
    hoje = datetime.now()

    for manejo, terreno_nome, produto_nome in aplicacoes:
        # Determinar status
        if manejo.DATA_LIBERACAO and manejo.DATA_LIBERACAO > hoje:
            status = "PENDENTE"
            dias_liberacao = (manejo.DATA_LIBERACAO - hoje).days
        elif manejo.DATA_LIBERACAO and manejo.DATA_LIBERACAO <= hoje:
            status = "LIBERADO"
            dias_liberacao = 0
        else:
            status = "APLICADO"
            dias_liberacao = None

        resultado.append(CronogramaAplicacoes(
            terreno_id=manejo.ID_TERRENO,
            terreno_nome=terreno_nome,
            manejo_id=manejo.ID,
            tipo_manejo=manejo.TIPO_MANEJO,
            produto_nome=produto_nome,
            data_aplicacao=manejo.DATA_APLICACAO,
            data_liberacao=manejo.DATA_LIBERACAO,
            dias_para_liberacao=dias_liberacao,
            status=status
        ))

    return resultado


@router.get("/relatorio/capacidade-ocupacao", response_model=List[CapacidadeOcupacao])
async def get_capacidade_ocupacao(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Relatório de capacidade vs ocupação dos terrenos"""
    # Subquery para contar animais por terreno (última movimentação)
    subq_ultima_mov = db.query(
        MovimentacaoAnimais.ID_ANIMAL,
        func.max(MovimentacaoAnimais.DATA_MOVIMENTACAO).label('ultima_data')
    ).group_by(MovimentacaoAnimais.ID_ANIMAL).subquery()

    # Query principal
    terrenos = db.query(Terreno).all()
    resultado = []

    for terreno in terrenos:
        # Contar animais atuais no terreno
        animais_atuais = db.query(MovimentacaoAnimais)\
            .join(subq_ultima_mov,
                  (MovimentacaoAnimais.ID_ANIMAL == subq_ultima_mov.c.ID_ANIMAL) &
                  (MovimentacaoAnimais.DATA_MOVIMENTACAO == subq_ultima_mov.c.ultima_data))\
            .filter(MovimentacaoAnimais.ID_TERRENO_DESTINO == terreno.ID)\
            .count()

        # Calcular taxa de ocupação
        if terreno.CAPACIDADE_ANIMAIS and terreno.CAPACIDADE_ANIMAIS > 0:
            taxa_ocupacao = (animais_atuais / terreno.CAPACIDADE_ANIMAIS) * 100

            if taxa_ocupacao > 100:
                status_lotacao = "SOBRELOTADO"
            elif taxa_ocupacao < 50:
                status_lotacao = "SUBLOTADO"
            else:
                status_lotacao = "ADEQUADA"
        else:
            taxa_ocupacao = 0
            status_lotacao = "SEM_LIMITE"

        resultado.append(CapacidadeOcupacao(
            terreno_id=terreno.ID,
            terreno_nome=terreno.NOME,
            area_hectares=terreno.AREA_HECTARES,
            capacidade_animais=terreno.CAPACIDADE_ANIMAIS,
            animais_atuais=animais_atuais,
            taxa_ocupacao=round(taxa_ocupacao, 2),
            status_lotacao=status_lotacao
        ))

    return resultado


@router.get("/relatorio/historico-nutricional", response_model=List[HistoricoNutricional])
async def get_historico_nutricional(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ano: Optional[int] = Query(None, description="Filtrar por ano")
):
    """Relatório nutricional dos terrenos"""
    terrenos = db.query(Terreno).all()
    resultado = []

    for terreno in terrenos:
        # Última análise de solo
        ultima_analise = db.query(AnalisesSolo)\
            .filter(AnalisesSolo.ID_TERRENO == terreno.ID)\
            .order_by(desc(AnalisesSolo.DATA_COLETA))\
            .first()

        # Total de aplicações no ano
        query_aplicacoes = db.query(ManejoTerrenos)\
            .filter(ManejoTerrenos.ID_TERRENO == terreno.ID)

        if ano:
            inicio_ano = datetime(ano, 1, 1)
            fim_ano = datetime(ano, 12, 31, 23, 59, 59)
            query_aplicacoes = query_aplicacoes.filter(
                ManejoTerrenos.DATA_APLICACAO.between(inicio_ano, fim_ano)
            )

        total_aplicacoes = query_aplicacoes.count()
        custo_total = query_aplicacoes.with_entities(
            func.sum(ManejoTerrenos.CUSTO_TOTAL)
        ).scalar() or 0

        # Determinar status do solo
        if ultima_analise:
            status_solo = "BOM"
            if ultima_analise.PH_AGUA and ultima_analise.PH_AGUA < 5.5:
                status_solo = "RUIM"
            elif ultima_analise.SATURACAO_BASES and ultima_analise.SATURACAO_BASES < 50:
                status_solo = "REGULAR"
        else:
            status_solo = "SEM_ANALISE"

        resultado.append(HistoricoNutricional(
            terreno_id=terreno.ID,
            terreno_nome=terreno.NOME,
            ultima_analise=ultima_analise.DATA_COLETA if ultima_analise else None,
            ph_atual=ultima_analise.PH_AGUA if ultima_analise else None,
            saturacao_bases=ultima_analise.SATURACAO_BASES if ultima_analise else None,
            materia_organica=ultima_analise.MATERIA_ORGANICA if ultima_analise else None,
            total_aplicacoes=total_aplicacoes,
            custo_total_ano=float(custo_total),
            status_solo=status_solo
        ))

    return resultado

# === OPÇÕES PARA SELECTS ===


@router.get("/options/tipos-produto")
async def get_tipos_produto(current_user: User = Depends(get_current_user)):
    return [
        {"value": "FERTILIZANTE", "label": "Fertilizante"},
        {"value": "DEFENSIVO", "label": "Defensivo"},
        {"value": "CORRETIVO", "label": "Corretivo"},
        {"value": "SEMENTE", "label": "Semente"}
    ]


@router.get("/options/tipos-manejo")
async def get_tipos_manejo(current_user: User = Depends(get_current_user)):
    return [
        {"value": "ADUBACAO", "label": "Adubação"},
        {"value": "CALAGEM", "label": "Calagem"},
        {"value": "PLANTIO", "label": "Plantio"},
        {"value": "APLICACAO_DEFENSIVO", "label": "Aplicação Defensivo"},
        {"value": "ROÇADA", "label": "Roçada"},
        {"value": "IRRIGACAO", "label": "Irrigação"}
    ]

# === FUNÇÕES AUXILIARES ===


async def _enrich_analise_response(analise: AnalisesSolo, db: Session) -> AnalisesSoloResponse:
    terreno = db.query(Terreno).filter(
        Terreno.ID == analise.ID_TERRENO).first()

    response_data = AnalisesSoloResponse.from_orm(analise)
    response_data.terreno_nome = terreno.NOME if terreno else None

    return response_data


async def _enrich_manejo_response(manejo: ManejoTerrenos, db: Session) -> ManejoTerrenosResponse:
    terreno = db.query(Terreno).filter(Terreno.ID == manejo.ID_TERRENO).first()
    produto = db.query(ProdutoManejo).filter(
        ProdutoManejo.ID == manejo.ID_PRODUTO).first()

    # Calcular dias para liberação
    dias_para_liberacao = None
    if manejo.DATA_LIBERACAO:
        dias_restantes = (manejo.DATA_LIBERACAO - datetime.now()).days
        dias_para_liberacao = max(0, dias_restantes)

    response_data = ManejoTerrenosResponse.from_orm(manejo)
    response_data.terreno_nome = terreno.NOME if terreno else None
    response_data.produto_nome = produto.NOME if produto else None
    response_data.dias_para_liberacao = dias_para_liberacao

    return response_data
