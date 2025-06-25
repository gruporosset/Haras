# backend/app/api/v1/manejo.py
import os
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.sql import desc, text
from sqlalchemy import and_, or_
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.manejo import ProdutoManejo, AnalisesSolo, ManejoTerrenos, MovimentacaoProdutoManejo
from app.models.terreno import Terreno
from app.models.user import User
from app.schemas.manejo import (
    # Produtos
    ProdutoManejoCreate, ProdutoManejoUpdate, ProdutoManejoResponse,
    ProdutoAutocomplete, TipoProdutoEnum,
    # Movimentação
    EntradaEstoqueCreate, SaidaEstoqueCreate, AjusteEstoqueCreate,
    MovimentacaoEstoqueResponse, TipoMovimentacaoManejoEnum,
    # Manejo
    ManejoTerrenosCreate, ManejoTerrenosUpdate, ManejoTerrenosResponse, TipoManejoEnum,
    # Análises
    AnalisesSoloCreate, AnalisesSoloUpdate, AnalisesSoloResponse,
    # Relatórios
    EstoqueBaixo, MovimentacaoResumo, ConsumoTerrenoResumo, PrevisaoConsumo, StatusEstoqueEnum
)

router = APIRouter(prefix="/api/manejo", tags=["Manejo de Terrenos"])

# Diretório para upload de laudos
UPLOAD_DIR = Path("uploads/laudos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ======================================
# PRODUTOS MANEJO - CRUD + ESTOQUE
# ======================================


@router.post("/produtos", response_model=ProdutoManejoResponse, status_code=status.HTTP_201_CREATED)
async def create_produto(
    produto: ProdutoManejoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar novo produto para manejo"""
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

    db_produto = ProdutoManejo(
        **produto.dict(),
        ID_USUARIO_CADASTRO=current_user.ID
    )
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)

    # Calcular status do estoque
    response = ProdutoManejoResponse.from_orm(db_produto)
    response.status_estoque = _calcular_status_estoque(db_produto)
    response.valor_total_estoque = (
        db_produto.ESTOQUE_ATUAL or 0) * (db_produto.PRECO_UNITARIO or 0)

    return response


@router.get("/produtos", response_model=dict)
async def list_produtos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tipo_produto: Optional[TipoProdutoEnum] = Query(None),
    nome: Optional[str] = Query(None),
    estoque_baixo: Optional[bool] = Query(False),
    ativo: Optional[str] = Query("S"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """Listar produtos com filtros e paginação"""
    query = db.query(ProdutoManejo)

    # Filtros
    if tipo_produto:
        query = query.filter(ProdutoManejo.TIPO_PRODUTO == tipo_produto)
    if nome:
        query = query.filter(ProdutoManejo.NOME.ilike(f"%{nome}%"))
    if ativo:
        query = query.filter(ProdutoManejo.ATIVO == ativo)
    if estoque_baixo:
        query = query.filter(
            or_(
                ProdutoManejo.ESTOQUE_ATUAL <= ProdutoManejo.ESTOQUE_MINIMO,
                and_(
                    ProdutoManejo.DATA_VALIDADE.isnot(None),
                    ProdutoManejo.DATA_VALIDADE <= datetime.now() + timedelta(days=30)
                )
            )
        )

    # Paginação
    total = query.count()
    offset = (page - 1) * limit
    produtos = query.order_by(ProdutoManejo.NOME).offset(
        offset).limit(limit).all()

    # Adicionar campos calculados
    produtos_response = []
    for produto in produtos:
        response = ProdutoManejoResponse.from_orm(produto)
        response.status_estoque = _calcular_status_estoque(produto)
        response.dias_vencimento = _calcular_dias_vencimento(produto)
        response.valor_total_estoque = (
            produto.ESTOQUE_ATUAL or 0) * (produto.PRECO_UNITARIO or 0)
        produtos_response.append(response)

    return {
        "produtos": produtos_response,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/produtos/autocomplete", response_model=List[ProdutoAutocomplete])
async def autocomplete_produtos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    q: Optional[str] = Query(None, min_length=2),
    tipo_produto: Optional[TipoProdutoEnum] = Query(None),
    apenas_com_estoque: Optional[bool] = Query(False)
):
    """Autocomplete para produtos com informações de estoque"""
    query = db.query(ProdutoManejo).filter(ProdutoManejo.ATIVO == 'S')

    if q:
        query = query.filter(ProdutoManejo.NOME.ilike(f"%{q}%"))
    if tipo_produto:
        query = query.filter(ProdutoManejo.TIPO_PRODUTO == tipo_produto)
    if apenas_com_estoque:
        query = query.filter(ProdutoManejo.ESTOQUE_ATUAL > 0)

    produtos = query.order_by(ProdutoManejo.NOME).limit(20).all()

    return [
        ProdutoAutocomplete(
            value=p.ID,
            label=f"{p.NOME} ({p.ESTOQUE_ATUAL:.1f} {p.UNIDADE_MEDIDA})",
            nome=p.NOME,
            estoque_atual=p.ESTOQUE_ATUAL or 0,
            estoque_minimo=p.ESTOQUE_MINIMO or 0,
            unidade_medida=p.UNIDADE_MEDIDA,
            tipo_produto=p.TIPO_PRODUTO,
            status_estoque=_calcular_status_estoque(p),
            dose_recomendada=p.DOSE_RECOMENDADA
        )
        for p in produtos
    ]


@router.get("/produtos/{produto_id}", response_model=ProdutoManejoResponse)
async def get_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter produto por ID"""
    produto = db.query(ProdutoManejo).filter(
        ProdutoManejo.ID == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    response = ProdutoManejoResponse.from_orm(produto)
    response.status_estoque = _calcular_status_estoque(produto)
    response.dias_vencimento = _calcular_dias_vencimento(produto)
    response.valor_total_estoque = (
        produto.ESTOQUE_ATUAL or 0) * (produto.PRECO_UNITARIO or 0)

    return response


@router.put("/produtos/{produto_id}", response_model=ProdutoManejoResponse)
async def update_produto(
    produto_id: int,
    produto_update: ProdutoManejoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar produto"""
    db_produto = db.query(ProdutoManejo).filter(
        ProdutoManejo.ID == produto_id).first()
    if not db_produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Verificar duplicata no nome
    if produto_update.NOME and produto_update.NOME != db_produto.NOME:
        existing = db.query(ProdutoManejo).filter(
            ProdutoManejo.NOME == produto_update.NOME,
            ProdutoManejo.ID != produto_id,
            ProdutoManejo.ATIVO == 'S'
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Nome já existe")

    # Atualizar campos
    for field, value in produto_update.model_dump(exclude_unset=True).items():
        setattr(db_produto, field, value)

    db.commit()
    db.refresh(db_produto)

    response = ProdutoManejoResponse.model_validate(db_produto)
    response.status_estoque = _calcular_status_estoque(db_produto)
    response.valor_total_estoque = (
        db_produto.ESTOQUE_ATUAL or 0) * (db_produto.PRECO_UNITARIO or 0)

    return response


@router.delete("/produtos/{produto_id}")
async def delete_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Excluir produto (soft delete)"""
    produto = db.query(ProdutoManejo).filter(
        ProdutoManejo.ID == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.ATIVO = 'N'
    db.commit()

    return {"message": "Produto excluído com sucesso"}


# ======================================
# MOVIMENTAÇÃO DE ESTOQUE
# ======================================

@router.post("/estoque/entrada", response_model=MovimentacaoEstoqueResponse)
async def entrada_estoque(
    entrada: EntradaEstoqueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registrar entrada de estoque (compra)"""
    # Verificar se produto existe
    produto = db.query(ProdutoManejo).filter(
        ProdutoManejo.ID == entrada.ID_PRODUTO,
        ProdutoManejo.ATIVO == 'S'
    ).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Criar movimentação (trigger atualizará o estoque automaticamente)
    db_movimentacao = MovimentacaoProdutoManejo(
        **entrada.dict(),
        ID_USUARIO_REGISTRO=current_user.ID
    )

    db.add(db_movimentacao)
    db.commit()
    db.refresh(db_movimentacao)

    # Buscar dados relacionados
    response = MovimentacaoEstoqueResponse.from_orm(db_movimentacao)
    response.produto_nome = produto.NOME

    return response


@router.post("/estoque/saida", response_model=MovimentacaoEstoqueResponse)
async def saida_estoque(
    saida: SaidaEstoqueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registrar saída de estoque"""
    # Verificar estoque disponível
    produto = db.query(ProdutoManejo).filter(
        ProdutoManejo.ID == saida.ID_PRODUTO,
        ProdutoManejo.ATIVO == 'S'
    ).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if (produto.ESTOQUE_ATUAL or 0) < saida.QUANTIDADE:
        raise HTTPException(
            status_code=400,
            detail=f"Estoque insuficiente. Disponível: {produto.ESTOQUE_ATUAL or 0} {produto.UNIDADE_MEDIDA}"
        )

    # Criar movimentação
    db_movimentacao = MovimentacaoProdutoManejo(
        ID_PRODUTO=saida.ID_PRODUTO,
        TIPO_MOVIMENTACAO=TipoMovimentacaoManejoEnum.SAIDA,
        QUANTIDADE=saida.QUANTIDADE,
        ID_TERRENO=saida.ID_TERRENO,
        MOTIVO=saida.MOTIVO,
        OBSERVACOES=saida.OBSERVACOES,
        ID_USUARIO_REGISTRO=current_user.ID
    )

    db.add(db_movimentacao)
    db.commit()
    db.refresh(db_movimentacao)

    response = MovimentacaoEstoqueResponse.from_orm(db_movimentacao)
    response.produto_nome = produto.NOME

    return response


@router.post("/estoque/ajuste", response_model=MovimentacaoEstoqueResponse)
async def ajuste_estoque(
    ajuste: AjusteEstoqueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ajustar estoque (correção)"""
    produto = db.query(ProdutoManejo).filter(
        ProdutoManejo.ID == ajuste.ID_PRODUTO,
        ProdutoManejo.ATIVO == 'S'
    ).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Criar movimentação de ajuste
    db_movimentacao = MovimentacaoProdutoManejo(
        ID_PRODUTO=ajuste.ID_PRODUTO,
        TIPO_MOVIMENTACAO=TipoMovimentacaoManejoEnum.AJUSTE,
        QUANTIDADE=ajuste.QUANTIDADE_NOVA,
        MOTIVO=ajuste.MOTIVO,
        OBSERVACOES=ajuste.OBSERVACOES,
        ID_USUARIO_REGISTRO=current_user.ID
    )

    db.add(db_movimentacao)
    db.commit()
    db.refresh(db_movimentacao)

    response = MovimentacaoEstoqueResponse.from_orm(db_movimentacao)
    response.produto_nome = produto.NOME

    return response


@router.get("/estoque/movimentacoes", response_model=dict)
async def list_movimentacoes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    produto_id: Optional[int] = Query(None),
    tipo_movimentacao: Optional[TipoMovimentacaoManejoEnum] = Query(None),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """Listar movimentações de estoque"""
    query = db.query(MovimentacaoProdutoManejo)

    # Converter datas se fornecidas
    data_inicio_dt = None
    data_fim_dt = None

    if data_inicio:
        try:
            data_inicio_dt = datetime.fromisoformat(
                data_inicio.replace('Z', '+00:00'))
        except ValueError:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')

    if data_fim:
        try:
            data_fim_dt = datetime.fromisoformat(
                data_fim.replace('Z', '+00:00'))
        except ValueError:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim_dt = data_fim_dt.replace(hour=23, minute=59, second=59)

    # Filtros
    if produto_id:
        query = query.filter(
            MovimentacaoProdutoManejo.ID_PRODUTO == produto_id)
    if tipo_movimentacao:
        query = query.filter(
            MovimentacaoProdutoManejo.TIPO_MOVIMENTACAO == tipo_movimentacao)
    if data_inicio_dt:
        query = query.filter(
            MovimentacaoProdutoManejo.DATA_REGISTRO >= data_inicio_dt)
    if data_fim_dt:
        query = query.filter(
            MovimentacaoProdutoManejo.DATA_REGISTRO <= data_fim_dt)

    # Paginação
    total = query.count()
    offset = (page - 1) * limit
    movimentacoes = query.order_by(
        desc(MovimentacaoProdutoManejo.DATA_REGISTRO)).offset(offset).limit(limit).all()

    # Adicionar dados relacionados
    movimentacoes_response = []
    for mov in movimentacoes:
        response = MovimentacaoEstoqueResponse.from_orm(mov)

        # Buscar produto diretamente
        produto = db.query(ProdutoManejo).filter(
            ProdutoManejo.ID == mov.ID_PRODUTO).first()
        if produto:
            response.produto_nome = produto.NOME
            response.produto_unidade = produto.UNIDADE_MEDIDA
        else:
            response.produto_nome = f"Produto ID {mov.ID_PRODUTO}"
            response.produto_unidade = ""

        # Buscar terreno se existir
        if mov.ID_TERRENO:
            terreno = db.query(Terreno).filter(
                Terreno.ID == mov.ID_TERRENO).first()
            response.terreno_nome = terreno.NOME if terreno else None

        movimentacoes_response.append(response)

    return {
        "movimentacoes": movimentacoes_response,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


# ======================================
# RELATÓRIOS DE ESTOQUE
# ======================================

@router.get("/estoque/alertas", response_model=List[EstoqueBaixo])
async def alertas_estoque(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Produtos com estoque baixo ou próximo ao vencimento"""
    # Usando a VIEW criada no Oracle
    query = """
    SELECT ID,
           NOME,
           TIPO_PRODUTO,
           ESTOQUE_ATUAL,
           ESTOQUE_MINIMO,
           UNIDADE_MEDIDA,
           FORNECEDOR_PRINCIPAL,
           DATA_VALIDADE,
           STATUS_ALERTA,
           DIAS_VENCIMENTO 
    FROM VW_PRODUTOS_ESTOQUE_BAIXO
    ORDER BY STATUS_ALERTA, ESTOQUE_ATUAL
    """
    result = db.execute(text(query)).fetchall()

    alertas = []
    for row in result:
        alertas.append(EstoqueBaixo(
            produto_id=row[0],
            nome=row[1],
            tipo_produto=row[2],
            estoque_atual=row[3] or 0,
            estoque_minimo=row[4] or 0,
            unidade_medida=row[5],
            status_alerta=row[8],
            dias_vencimento=row[9],
            fornecedor_principal=row[6]
        ))

    return alertas


@router.get("/estoque/resumo", response_model=List[MovimentacaoResumo])
async def resumo_estoque(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tipo_produto: Optional[TipoProdutoEnum] = Query(None)
):
    """Resumo de movimentação de estoque"""
    # Usando a VIEW criada no Oracle
    query = "SELECT * FROM VW_MOVIMENTACAO_ESTOQUE_RESUMO"
    params = {}

    if tipo_produto:
        query += " WHERE TIPO_PRODUTO = :tipo_produto"
        params['tipo_produto'] = tipo_produto.value

    query += " ORDER BY PRODUTO_NOME"

    result = db.execute(text(query), params).fetchall()

    resumos = []
    for row in result:
        resumos.append(MovimentacaoResumo(
            produto_id=row.PRODUTO_ID,
            produto_nome=row.PRODUTO_NOME,
            tipo_produto=row.TIPO_PRODUTO,
            estoque_atual=row.ESTOQUE_ATUAL or 0,
            estoque_minimo=row.ESTOQUE_MINIMO or 0,
            unidade_medida=row.UNIDADE_MEDIDA,
            total_entradas=row.TOTAL_ENTRADAS or 0,
            total_saidas=row.TOTAL_SAIDAS or 0,
            valor_entradas=row.VALOR_ENTRADAS or 0,
            ultima_movimentacao=row.ULTIMA_MOVIMENTACAO
        ))

    return resumos


# ======================================
# ANÁLISES DE SOLO
# ======================================

@router.post("/analises-solo", response_model=AnalisesSoloResponse, status_code=status.HTTP_201_CREATED)
async def create_analise_solo(
    analise: AnalisesSoloCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar análise de solo"""
    # Verificar se terreno existe
    terreno = db.query(Terreno).filter(
        Terreno.ID == analise.ID_TERRENO).first()
    if not terreno:
        raise HTTPException(status_code=404, detail="Terreno não encontrado")

    db_analise = AnalisesSolo(
        **analise.dict(),
        ID_USUARIO_CADASTRO=current_user.ID
    )
    db.add(db_analise)
    db.commit()
    db.refresh(db_analise)

    response = AnalisesSoloResponse.from_orm(db_analise)
    response.terreno_nome = terreno.NOME

    return response


@router.get("/analises-solo", response_model=dict)
async def list_analises_solo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    terreno_id: Optional[int] = Query(None),
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    laboratorio: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """Listar análises de solo"""
    query = db.query(AnalisesSolo).join(Terreno)

    # Filtros
    if terreno_id:
        query = query.filter(AnalisesSolo.ID_TERRENO == terreno_id)
    if data_inicio:
        query = query.filter(AnalisesSolo.DATA_COLETA >= data_inicio)
    if data_fim:
        query = query.filter(AnalisesSolo.DATA_COLETA <= data_fim)
    if laboratorio:
        query = query.filter(
            AnalisesSolo.LABORATORIO.ilike(f"%{laboratorio}%"))

    # Paginação
    total = query.count()
    offset = (page - 1) * limit
    analises = query.order_by(desc(AnalisesSolo.DATA_COLETA)).offset(
        offset).limit(limit).all()

    # Adicionar dados relacionados
    analises_response = []
    for analise in analises:
        response = AnalisesSoloResponse.from_orm(analise)
        terreno = db.query(Terreno).filter(
            Terreno.ID == analise.ID_TERRENO).first()
        response.terreno_nome = terreno.NOME if terreno else None
        analises_response.append(response)

    return {
        "analises": analises_response,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/analises-solo/{analise_id}", response_model=AnalisesSoloResponse)
async def get_analise_solo(
    analise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter análise de solo por ID"""
    analise = db.query(AnalisesSolo).filter(
        AnalisesSolo.ID == analise_id).first()
    if not analise:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    response = AnalisesSoloResponse.from_orm(analise)
    terreno = db.query(Terreno).filter(
        Terreno.ID == analise.ID_TERRENO).first()
    response.terreno_nome = terreno.NOME if terreno else None

    return response


@router.put("/analises-solo/{analise_id}", response_model=AnalisesSoloResponse)
async def update_analise_solo(
    analise_id: int,
    analise_update: AnalisesSoloUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar análise de solo"""
    db_analise = db.query(AnalisesSolo).filter(
        AnalisesSolo.ID == analise_id).first()
    if not db_analise:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    # Atualizar campos
    for field, value in analise_update.dict(exclude_unset=True).items():
        setattr(db_analise, field, value)

    db.commit()
    db.refresh(db_analise)

    response = AnalisesSoloResponse.from_orm(db_analise)
    terreno = db.query(Terreno).filter(
        Terreno.ID == db_analise.ID_TERRENO).first()
    response.terreno_nome = terreno.NOME if terreno else None

    return response


@router.post("/analises-solo/{analise_id}/upload-laudo")
async def upload_laudo_analise(
    analise_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload de laudo de análise de solo"""
    # Verificar se análise existe
    analise = db.query(AnalisesSolo).filter(
        AnalisesSolo.ID == analise_id).first()
    if not analise:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    # Validar tipo de arquivo
    if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
        raise HTTPException(
            status_code=400, detail="Tipo de arquivo não permitido. Use PDF ou imagens.")

    # Gerar nome único do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analise_{analise_id}_{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / filename

    # Salvar arquivo
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Atualizar caminho no banco
        analise.ARQUIVO_LAUDO = str(file_path)
        db.commit()

        return {"message": "Laudo enviado com sucesso", "arquivo": filename}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")


@router.delete("/analises-solo/{analise_id}")
async def delete_analise_solo(
    analise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Excluir análise de solo"""
    analise = db.query(AnalisesSolo).filter(
        AnalisesSolo.ID == analise_id).first()
    if not analise:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    # Remover arquivo do laudo se existir
    if analise.ARQUIVO_LAUDO and os.path.exists(analise.ARQUIVO_LAUDO):
        try:
            os.remove(analise.ARQUIVO_LAUDO)
        except:
            pass  # Ignorar erro se arquivo não puder ser removido

    db.delete(analise)
    db.commit()

    return {"message": "Análise excluída com sucesso"}


# ======================================
# MANEJO DE TERRENOS
# ======================================

@router.post("/aplicacoes", response_model=ManejoTerrenosResponse, status_code=status.HTTP_201_CREATED)
async def create_aplicacao(
    aplicacao: ManejoTerrenosCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registrar aplicação em terreno"""
    # Verificar se terreno e produto existem
    terreno = db.query(Terreno).filter(
        Terreno.ID == aplicacao.ID_TERRENO).first()
    if not terreno:
        raise HTTPException(status_code=404, detail="Terreno não encontrado")

    produto = db.query(ProdutoManejo).filter(
        ProdutoManejo.ID == aplicacao.ID_PRODUTO,
        ProdutoManejo.ATIVO == 'S'
    ).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Verificar estoque disponível
    if (produto.ESTOQUE_ATUAL or 0) < aplicacao.QUANTIDADE:
        raise HTTPException(
            status_code=400,
            detail=f"Estoque insuficiente. Disponível: {produto.ESTOQUE_ATUAL or 0} {produto.UNIDADE_MEDIDA}"
        )

    # Calcular data de liberação se houver carência
    data_liberacao = None
    if aplicacao.PERIODO_CARENCIA:
        data_liberacao = aplicacao.DATA_APLICACAO + \
            timedelta(days=aplicacao.PERIODO_CARENCIA)
    elif produto.PERIODO_CARENCIA:
        data_liberacao = aplicacao.DATA_APLICACAO + \
            timedelta(days=produto.PERIODO_CARENCIA)

    # Criar aplicação
    db_aplicacao = ManejoTerrenos(
        **aplicacao.dict(),
        DATA_LIBERACAO=data_liberacao,
        ID_USUARIO_REGISTRO=current_user.ID
    )

    db.add(db_aplicacao)
    db.commit()
    db.refresh(db_aplicacao)

    # O trigger criará automaticamente a movimentação de estoque

    response = ManejoTerrenosResponse.from_orm(db_aplicacao)
    response.terreno_nome = terreno.NOME
    response.produto_nome = produto.NOME
    response.produto_tipo = produto.TIPO_PRODUTO.value

    return response


@router.get("/aplicacoes", response_model=dict)
async def list_aplicacoes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    terreno_id: Optional[int] = Query(None),
    produto_id: Optional[int] = Query(None),
    tipo_manejo: Optional[TipoManejoEnum] = Query(None),
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """Listar aplicações em terrenos"""
    query = db.query(ManejoTerrenos).join(Terreno).join(ProdutoManejo)

    # Filtros
    if terreno_id:
        query = query.filter(ManejoTerrenos.ID_TERRENO == terreno_id)
    if produto_id:
        query = query.filter(ManejoTerrenos.ID_PRODUTO == produto_id)
    if tipo_manejo:
        query = query.filter(ManejoTerrenos.TIPO_MANEJO == tipo_manejo)
    if data_inicio:
        query = query.filter(ManejoTerrenos.DATA_APLICACAO >= data_inicio)
    if data_fim:
        query = query.filter(ManejoTerrenos.DATA_APLICACAO <= data_fim)

    # Paginação
    total = query.count()
    offset = (page - 1) * limit
    aplicacoes = query.order_by(desc(ManejoTerrenos.DATA_APLICACAO)).offset(
        offset).limit(limit).all()

    # Adicionar dados relacionados
    aplicacoes_response = []
    for aplicacao in aplicacoes:
        response = ManejoTerrenosResponse.from_orm(aplicacao)
        # Buscar dados relacionados (join pode não carregar automaticamente)
        terreno = db.query(Terreno).filter(
            Terreno.ID == aplicacao.ID_TERRENO).first()
        produto = db.query(ProdutoManejo).filter(
            ProdutoManejo.ID == aplicacao.ID_PRODUTO).first()
        response.terreno_nome = terreno.NOME if terreno else None
        response.produto_nome = produto.NOME if produto else None
        response.produto_tipo = produto.TIPO_PRODUTO.value if produto else None
        aplicacoes_response.append(response)


@router.get("/aplicacoes/{aplicacao_id}", response_model=ManejoTerrenosResponse)
async def get_aplicacao(
    aplicacao_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter aplicação por ID"""
    aplicacao = db.query(ManejoTerrenos).filter(
        ManejoTerrenos.ID == aplicacao_id).first()
    if not aplicacao:
        raise HTTPException(status_code=404, detail="Aplicação não encontrada")

    response = ManejoTerrenosResponse.from_orm(aplicacao)
    terreno = db.query(Terreno).filter(
        Terreno.ID == aplicacao.ID_TERRENO).first()
    produto = db.query(ProdutoManejo).filter(
        ProdutoManejo.ID == aplicacao.ID_PRODUTO).first()
    response.terreno_nome = terreno.NOME if terreno else None
    response.produto_nome = produto.NOME if produto else None
    response.produto_tipo = produto.TIPO_PRODUTO.value if produto else None

    return response


@router.put("/aplicacoes/{aplicacao_id}", response_model=ManejoTerrenosResponse)
async def update_aplicacao(
    aplicacao_id: int,
    aplicacao_update: ManejoTerrenosUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar aplicação em terreno"""
    db_aplicacao = db.query(ManejoTerrenos).filter(
        ManejoTerrenos.ID == aplicacao_id).first()
    if not db_aplicacao:
        raise HTTPException(status_code=404, detail="Aplicação não encontrada")

    # Se mudou a quantidade, verificar estoque
    if aplicacao_update.QUANTIDADE and aplicacao_update.QUANTIDADE != db_aplicacao.QUANTIDADE:
        produto = db.query(ProdutoManejo).filter(
            ProdutoManejo.ID == db_aplicacao.ID_PRODUTO).first()
        diferenca = aplicacao_update.QUANTIDADE - db_aplicacao.QUANTIDADE

        if diferenca > 0:  # Aumentou a quantidade
            if (produto.ESTOQUE_ATUAL or 0) < diferenca:
                raise HTTPException(
                    status_code=400,
                    detail=f"Estoque insuficiente para o aumento. Disponível: {produto.ESTOQUE_ATUAL or 0} {produto.UNIDADE_MEDIDA}"
                )
            # Criar movimentação de saída adicional
            db_movimentacao = MovimentacaoProdutoManejo(
                ID_PRODUTO=db_aplicacao.ID_PRODUTO,
                TIPO_MOVIMENTACAO=TipoMovimentacaoManejoEnum.SAIDA,
                QUANTIDADE=diferenca,
                ID_MANEJO_TERRENO=aplicacao_id,
                ID_TERRENO=db_aplicacao.ID_TERRENO,
                MOTIVO=f"Ajuste de aplicação - aumento de {diferenca} {produto.UNIDADE_MEDIDA}",
                ID_USUARIO_REGISTRO=current_user.ID
            )
            db.add(db_movimentacao)

        elif diferenca < 0:  # Diminuiu a quantidade
            # Criar movimentação de entrada (estorno)
            db_movimentacao = MovimentacaoProdutoManejo(
                ID_PRODUTO=db_aplicacao.ID_PRODUTO,
                TIPO_MOVIMENTACAO=TipoMovimentacaoManejoEnum.ENTRADA,
                QUANTIDADE=abs(diferenca),
                ID_MANEJO_TERRENO=aplicacao_id,
                ID_TERRENO=db_aplicacao.ID_TERRENO,
                MOTIVO=f"Ajuste de aplicação - redução de {abs(diferenca)} {produto.UNIDADE_MEDIDA}",
                ID_USUARIO_REGISTRO=current_user.ID
            )
            db.add(db_movimentacao)

    # Recalcular data de liberação se mudou carência ou data
    if aplicacao_update.PERIODO_CARENCIA is not None or aplicacao_update.DATA_APLICACAO is not None:
        data_aplicacao = aplicacao_update.DATA_APLICACAO or db_aplicacao.DATA_APLICACAO
        periodo_carencia = aplicacao_update.PERIODO_CARENCIA or db_aplicacao.PERIODO_CARENCIA

        if periodo_carencia:
            aplicacao_update.DATA_LIBERACAO = data_aplicacao + \
                timedelta(days=periodo_carencia)

    # Atualizar campos
    for field, value in aplicacao_update.dict(exclude_unset=True).items():
        setattr(db_aplicacao, field, value)

    db.commit()
    db.refresh(db_aplicacao)

    response = ManejoTerrenosResponse.from_orm(db_aplicacao)
    terreno = db.query(Terreno).filter(
        Terreno.ID == db_aplicacao.ID_TERRENO).first()
    produto = db.query(ProdutoManejo).filter(
        ProdutoManejo.ID == db_aplicacao.ID_PRODUTO).first()
    response.terreno_nome = terreno.NOME if terreno else None
    response.produto_nome = produto.NOME if produto else None
    response.produto_tipo = produto.TIPO_PRODUTO.value if produto else None

    return response


@router.delete("/aplicacoes/{aplicacao_id}")
async def delete_aplicacao(
    aplicacao_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Excluir aplicação (estorna estoque)"""
    aplicacao = db.query(ManejoTerrenos).filter(
        ManejoTerrenos.ID == aplicacao_id).first()
    if not aplicacao:
        raise HTTPException(status_code=404, detail="Aplicação não encontrada")

    # Estornar estoque
    produto = db.query(ProdutoManejo).filter(
        ProdutoManejo.ID == aplicacao.ID_PRODUTO).first()
    db_movimentacao = MovimentacaoProdutoManejo(
        ID_PRODUTO=aplicacao.ID_PRODUTO,
        TIPO_MOVIMENTACAO=TipoMovimentacaoManejoEnum.ENTRADA,
        QUANTIDADE=aplicacao.QUANTIDADE,
        ID_TERRENO=aplicacao.ID_TERRENO,
        MOTIVO=f"Estorno por exclusão de aplicação - {aplicacao.TIPO_MANEJO}",
        ID_USUARIO_REGISTRO=current_user.ID
    )
    db.add(db_movimentacao)

    # Excluir aplicação
    db.delete(aplicacao)
    db.commit()

    return {"message": "Aplicação excluída e estoque estornado com sucesso"}


# ======================================
# RELATÓRIOS AVANÇADOS
# ======================================

@router.get("/relatorios/consumo-terreno", response_model=List[ConsumoTerrenoResumo])
async def relatorio_consumo_terreno(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    terreno_id: Optional[int] = Query(None),
    tipo_produto: Optional[TipoProdutoEnum] = Query(None),
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None)
):
    """Relatório de consumo de produtos por terreno"""
    query = """
    SELECT 
        t.ID as terreno_id,
        t.NOME as terreno_nome,
        p.NOME as produto_nome,
        mt.TIPO_MANEJO,
        SUM(mt.QUANTIDADE) as total_aplicado,
        p.UNIDADE_MEDIDA,
        COUNT(*) as numero_aplicacoes,
        MAX(mt.DATA_APLICACAO) as ultima_aplicacao,
        SUM(NVL(mt.CUSTO_TOTAL, 0)) as custo_total
    FROM MANEJO_TERRENOS mt
    JOIN TERRENOS t ON mt.ID_TERRENO = t.ID
    JOIN PRODUTOS_MANEJO p ON mt.ID_PRODUTO = p.ID
    WHERE 1=1
    """

    params = {}

    if terreno_id:
        query += " AND t.ID = :terreno_id"
        params['terreno_id'] = terreno_id

    if tipo_produto:
        query += " AND p.TIPO_PRODUTO = :tipo_produto"
        params['tipo_produto'] = tipo_produto.value

    if data_inicio:
        query += " AND mt.DATA_APLICACAO >= :data_inicio"
        params['data_inicio'] = data_inicio

    if data_fim:
        query += " AND mt.DATA_APLICACAO <= :data_fim"
        params['data_fim'] = data_fim

    query += """
    GROUP BY t.ID, t.NOME, p.NOME, mt.TIPO_MANEJO, p.UNIDADE_MEDIDA
    ORDER BY t.NOME, p.NOME, mt.TIPO_MANEJO
    """

    result = db.execute(text(query), params).fetchall()

    consumos = []
    for row in result:
        consumos.append(ConsumoTerrenoResumo(
            terreno_id=row.terreno_id,
            terreno_nome=row.terreno_nome,
            produto_nome=row.produto_nome,
            tipo_manejo=row.TIPO_MANEJO,
            total_aplicado=row.total_aplicado or 0,
            unidade_medida=row.UNIDADE_MEDIDA,
            numero_aplicacoes=row.numero_aplicacoes or 0,
            ultima_aplicacao=row.ultima_aplicacao,
            custo_total=row.custo_total
        ))

    return consumos


@router.get("/relatorios/previsao-consumo", response_model=List[PrevisaoConsumo])
async def relatorio_previsao_consumo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tipo_produto: Optional[TipoProdutoEnum] = Query(None)
):
    """Previsão de consumo baseada no histórico"""
    # Calcular consumo médio mensal dos últimos 6 meses
    query = """
    WITH consumo_mensal AS (
        SELECT 
            p.ID,
            p.NOME,
            p.ESTOQUE_ATUAL,
            p.UNIDADE_MEDIDA,
            AVG(monthly_consumption.total_mensal) as consumo_mensal_medio
        FROM PRODUTOS_MANEJO p
        LEFT JOIN (
            SELECT 
                ID_PRODUTO,
                EXTRACT(YEAR FROM DATA_APLICACAO) as ano,
                EXTRACT(MONTH FROM DATA_APLICACAO) as mes,
                SUM(QUANTIDADE) as total_mensal
            FROM MANEJO_TERRENOS 
            WHERE DATA_APLICACAO >= ADD_MONTHS(SYSDATE, -6)
            GROUP BY ID_PRODUTO, EXTRACT(YEAR FROM DATA_APLICACAO), EXTRACT(MONTH FROM DATA_APLICACAO)
        ) monthly_consumption ON p.ID = monthly_consumption.ID_PRODUTO
        WHERE p.ATIVO = 'S'
    """

    params = {}
    if tipo_produto:
        query += " AND p.TIPO_PRODUTO = :tipo_produto"
        params['tipo_produto'] = tipo_produto.value

    query += """
        GROUP BY p.ID, p.NOME, p.ESTOQUE_ATUAL, p.UNIDADE_MEDIDA
        HAVING AVG(monthly_consumption.total_mensal) > 0
        ORDER BY p.NOME
    """

    result = db.execute(text(query), params).fetchall()

    previsoes = []
    for row in result:
        consumo_mensal = row.consumo_mensal_medio or 0
        estoque_atual = row.ESTOQUE_ATUAL or 0

        if consumo_mensal > 0:
            dias_restantes = int((estoque_atual / consumo_mensal) * 30)
            data_prevista_fim = datetime.now() + timedelta(days=dias_restantes)

            # Definir recomendação
            if dias_restantes <= 15:
                recomendacao = "COMPRAR_URGENTE"
            elif dias_restantes <= 45:
                recomendacao = "COMPRAR_BREVE"
            else:
                recomendacao = "OK"

            previsoes.append(PrevisaoConsumo(
                produto_id=row.ID,
                produto_nome=row.NOME,
                consumo_mensal_medio=consumo_mensal,
                estoque_atual=estoque_atual,
                dias_restantes=dias_restantes,
                data_prevista_fim=data_prevista_fim,
                recomendacao=recomendacao
            ))

    return previsoes


@router.get("/relatorios/terrenos-liberacao")
async def relatorio_terrenos_liberacao(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    dias_futuro: int = Query(30, ge=1, le=365)
):
    """Terrenos que serão liberados nos próximos dias"""
    query = """
    SELECT 
        t.ID as terreno_id,
        t.NOME as terreno_nome,
        p.NOME as produto_nome,
        mt.TIPO_MANEJO,
        mt.DATA_APLICACAO,
        mt.DATA_LIBERACAO,
        TRUNC(mt.DATA_LIBERACAO - SYSDATE) as dias_para_liberacao
    FROM MANEJO_TERRENOS mt
    JOIN TERRENOS t ON mt.ID_TERRENO = t.ID
    JOIN PRODUTOS_MANEJO p ON mt.ID_PRODUTO = p.ID
    WHERE mt.DATA_LIBERACAO IS NOT NULL
        AND mt.DATA_LIBERACAO BETWEEN SYSDATE AND SYSDATE + :dias_futuro
        AND mt.DATA_LIBERACAO > SYSDATE
    ORDER BY mt.DATA_LIBERACAO, t.NOME
    """

    result = db.execute(text(query), {'dias_futuro': dias_futuro}).fetchall()

    liberacoes = []
    for row in result:
        liberacoes.append({
            "terreno_id": row.terreno_id,
            "terreno_nome": row.terreno_nome,
            "produto_nome": row.produto_nome,
            "tipo_manejo": row.TIPO_MANEJO,
            "data_aplicacao": row.DATA_APLICACAO.strftime("%d/%m/%Y") if row.DATA_APLICACAO else None,
            "data_liberacao": row.DATA_LIBERACAO.strftime("%d/%m/%Y") if row.DATA_LIBERACAO else None,
            "dias_para_liberacao": row.dias_para_liberacao or 0
        })

    return {"liberacoes": liberacoes}


# ======================================
# FUNÇÕES AUXILIARES
# ======================================

def _calcular_status_estoque(produto: ProdutoManejo) -> StatusEstoqueEnum:
    """Calcular status do estoque do produto"""
    if produto.ESTOQUE_ATUAL == 0:
        return StatusEstoqueEnum.SEM_ESTOQUE
    elif produto.ESTOQUE_ATUAL <= produto.ESTOQUE_MINIMO:
        return StatusEstoqueEnum.ESTOQUE_BAIXO
    elif produto.DATA_VALIDADE and produto.DATA_VALIDADE <= datetime.now() + timedelta(days=30):
        return StatusEstoqueEnum.VENCIMENTO_PROXIMO
    else:
        return StatusEstoqueEnum.OK


def _calcular_dias_vencimento(produto: ProdutoManejo) -> Optional[int]:
    """Calcular dias até o vencimento"""
    if not produto.DATA_VALIDADE:
        return None

    dias = (produto.DATA_VALIDADE - datetime.now()).days
    return max(0, dias)
