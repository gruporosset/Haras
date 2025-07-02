from datetime import datetime
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.animal import Animal
from app.models.crescimento import HistoricoCrescimento
from app.models.racao import (
    FornecimentoRacaoAnimal,
    ItemPlanoAlimentar,
    MovimentacaoProdutoRacao,
    PlanoAlimentar,
    ProdutoRacao,
)
from app.models.user import User
from app.schemas.racao import (  # Produtos; Movimentação; Planos; Fornecimento; Relatórios
    AjusteRacaoCreate,
    CalculoNutricional,
    CategoriaNutricionalEnum,
    ConsumoAnimalResumo,
    EntradaRacaoCreate,
    EstoqueRacaoBaixo,
    FornecimentoRacaoCreate,
    FornecimentoRacaoResponse,
    FornecimentoRacaoUpdate,
    ItemPlanoAlimentarCreate,
    ItemPlanoAlimentarResponse,
    ItemPlanoAlimentarUpdate,
    MovimentacaoRacaoResponse,
    PlanoAlimentarCreate,
    PlanoAlimentarResponse,
    PlanoAlimentarUpdate,
    PrevisaoConsumoRacao,
    ProdutoRacaoAutocomplete,
    ProdutoRacaoCreate,
    ProdutoRacaoResponse,
    ProdutoRacaoUpdate,
    SaidaRacaoCreate,
    StatusEstoqueRacaoEnum,
    TipoAlimentoEnum,
    TipoMovimentacaoRacaoEnum,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import desc, text

router = APIRouter(prefix="/api/racao", tags=["Ração e Suplementos"])

# ======================================
# PRODUTOS RAÇÃO - CRUD + ESTOQUE
# ======================================


@router.post(
    "/produtos",
    response_model=ProdutoRacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_produto_racao(
    produto: ProdutoRacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Criar produto de ração/suplemento"""
    # Verificar duplicatas
    existing = (
        db.query(ProdutoRacao)
        .filter(ProdutoRacao.NOME == produto.NOME, ProdutoRacao.ATIVO == "S")
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produto com este nome já existe",
        )

    db_produto = ProdutoRacao(**produto.dict(), ID_USUARIO_CADASTRO=current_user.ID)
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)

    return await _enrich_produto_response(db_produto, db)


@router.get("/produtos", response_model=dict)
async def list_produtos_racao(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    tipo_alimento: Optional[TipoAlimentoEnum] = Query(
        None, description="Filtrar por tipo"
    ),
    estoque_baixo: Optional[bool] = Query(False, description="Apenas estoque baixo"),
    ativo: Optional[str] = Query(None, description="Filtrar por status"),
    page: int = Query(1, ge=1, description="Página"),
    limit: int = Query(20, ge=1, le=100, description="Itens por página"),
):
    """Listar produtos de ração"""
    query = db.query(ProdutoRacao)

    # Filtros
    if nome:
        query = query.filter(ProdutoRacao.NOME.ilike(f"%{nome}%"))
    if tipo_alimento:
        query = query.filter(ProdutoRacao.TIPO_ALIMENTO == tipo_alimento)
    if estoque_baixo:
        query = query.filter(ProdutoRacao.ESTOQUE_ATUAL <= ProdutoRacao.ESTOQUE_MINIMO)
    if ativo:
        query = query.filter(ProdutoRacao.ATIVO == ativo.upper())

    # Paginação
    total = query.count()
    offset = (page - 1) * limit
    produtos = query.order_by(ProdutoRacao.NOME).offset(offset).limit(limit).all()

    # Enriquecer resposta
    produtos_response = []
    for produto in produtos:
        response = await _enrich_produto_response(produto, db)
        produtos_response.append(response)

    return {
        "produtos": produtos_response,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
    }


@router.get("/produtos/{produto_id}", response_model=ProdutoRacaoResponse)
async def get_produto_racao(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obter produto específico"""
    produto = (
        db.query(ProdutoRacao)
        .filter(ProdutoRacao.ID == produto_id, ProdutoRacao.ATIVO == "S")
        .first()
    )

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return await _enrich_produto_response(produto, db)


@router.put("/produtos/{produto_id}", response_model=ProdutoRacaoResponse)
async def update_produto_racao(
    produto_id: int,
    produto_update: ProdutoRacaoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualizar produto de ração"""
    produto = (
        db.query(ProdutoRacao)
        .filter(ProdutoRacao.ID == produto_id, ProdutoRacao.ATIVO == "S")
        .first()
    )

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Verificar duplicata de nome se alterado
    if produto_update.NOME and produto_update.NOME != produto.NOME:
        existing = (
            db.query(ProdutoRacao)
            .filter(
                ProdutoRacao.NOME == produto_update.NOME,
                ProdutoRacao.ID != produto_id,
                ProdutoRacao.ATIVO == "S",
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="Nome já existe para outro produto"
            )

    # Atualizar campos
    for field, value in produto_update.dict(exclude_unset=True).items():
        setattr(produto, field, value)

    db.commit()
    db.refresh(produto)

    return await _enrich_produto_response(produto, db)


@router.delete("/produtos/{produto_id}")
async def delete_produto_racao(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Inativar produto de ração"""
    produto = (
        db.query(ProdutoRacao)
        .filter(ProdutoRacao.ID == produto_id, ProdutoRacao.ATIVO == "S")
        .first()
    )

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.ATIVO = "N"
    db.commit()

    return {"message": "Produto inativado com sucesso"}


# ======================================
# MOVIMENTAÇÃO DE ESTOQUE
# ======================================


@router.post(
    "/estoque/entrada",
    response_model=MovimentacaoRacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def entrada_estoque_racao(
    entrada: EntradaRacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Registrar entrada de estoque (compra)"""
    produto = (
        db.query(ProdutoRacao)
        .filter(ProdutoRacao.ID == entrada.ID_PRODUTO, ProdutoRacao.ATIVO == "S")
        .first()
    )

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    db_movimentacao = MovimentacaoProdutoRacao(
        **entrada.dict(), ID_USUARIO_REGISTRO=current_user.ID
    )
    db.add(db_movimentacao)
    db.commit()
    db.refresh(db_movimentacao)

    return await _enrich_movimentacao_response(db_movimentacao, db)


@router.post(
    "/estoque/saida",
    response_model=MovimentacaoRacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def saida_estoque_racao(
    saida: SaidaRacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Registrar saída manual de estoque"""
    produto = (
        db.query(ProdutoRacao)
        .filter(ProdutoRacao.ID == saida.ID_PRODUTO, ProdutoRacao.ATIVO == "S")
        .first()
    )

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Verificar estoque
    if produto.ESTOQUE_ATUAL < saida.QUANTIDADE:
        raise HTTPException(
            status_code=400,
            detail=f"Estoque insuficiente. Disponível: {produto.ESTOQUE_ATUAL} {produto.UNIDADE_MEDIDA}",
        )

    db_movimentacao = MovimentacaoProdutoRacao(
        ID_PRODUTO=saida.ID_PRODUTO,
        TIPO_MOVIMENTACAO=TipoMovimentacaoRacaoEnum.SAIDA,
        QUANTIDADE=saida.QUANTIDADE,
        ID_ANIMAL=saida.ID_ANIMAL,
        MOTIVO=saida.MOTIVO,
        OBSERVACOES=saida.OBSERVACOES,
        ID_USUARIO_REGISTRO=current_user.ID,
    )
    db.add(db_movimentacao)
    db.commit()
    db.refresh(db_movimentacao)

    return await _enrich_movimentacao_response(db_movimentacao, db)


@router.post(
    "/estoque/ajuste",
    response_model=MovimentacaoRacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ajuste_estoque_racao(
    ajuste: AjusteRacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ajustar estoque para quantidade específica"""
    produto = (
        db.query(ProdutoRacao)
        .filter(ProdutoRacao.ID == ajuste.ID_PRODUTO, ProdutoRacao.ATIVO == "S")
        .first()
    )

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    db_movimentacao = MovimentacaoProdutoRacao(
        ID_PRODUTO=ajuste.ID_PRODUTO,
        TIPO_MOVIMENTACAO=TipoMovimentacaoRacaoEnum.AJUSTE,
        QUANTIDADE=ajuste.QUANTIDADE_NOVA,
        MOTIVO=ajuste.MOTIVO,
        OBSERVACOES=ajuste.OBSERVACOES,
        ID_USUARIO_REGISTRO=current_user.ID,
    )
    db.add(db_movimentacao)
    db.commit()
    db.refresh(db_movimentacao)

    return await _enrich_movimentacao_response(db_movimentacao, db)


@router.get("/estoque/movimentacoes", response_model=dict)
async def list_movimentacoes_racao(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    produto_id: Optional[int] = Query(None, description="Filtrar por produto"),
    tipo_movimentacao: Optional[TipoMovimentacaoRacaoEnum] = Query(
        None, description="Filtrar por tipo"
    ),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Página"),
    limit: int = Query(20, ge=1, le=100, description="Itens por página"),
):
    """Listar movimentações de ração"""
    query = db.query(MovimentacaoProdutoRacao).join(
        ProdutoRacao, MovimentacaoProdutoRacao.ID_PRODUTO == ProdutoRacao.ID
    )

    # Filtros
    if produto_id:
        query = query.filter(MovimentacaoProdutoRacao.ID_PRODUTO == produto_id)
    if tipo_movimentacao:
        query = query.filter(
            MovimentacaoProdutoRacao.TIPO_MOVIMENTACAO == tipo_movimentacao
        )
    if data_inicio:
        try:
            data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.filter(
                MovimentacaoProdutoRacao.DATA_REGISTRO >= data_inicio_dt
            )
        except ValueError:
            pass
    if data_fim:
        try:
            data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")
            data_fim_dt = data_fim_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(MovimentacaoProdutoRacao.DATA_REGISTRO <= data_fim_dt)
        except ValueError:
            pass

    # Paginação
    total = query.count()
    offset = (page - 1) * limit
    movimentacoes = (
        query.order_by(desc(MovimentacaoProdutoRacao.DATA_REGISTRO))
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Enriquecer resposta
    movimentacoes_response = []
    for mov in movimentacoes:
        response = await _enrich_movimentacao_response(mov, db)
        movimentacoes_response.append(response)

    return {
        "movimentacoes": movimentacoes_response,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
    }


# ======================================
# PLANOS ALIMENTARES
# ======================================


@router.post(
    "/planos",
    response_model=PlanoAlimentarResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_plano_alimentar(
    plano: PlanoAlimentarCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Criar plano alimentar para animal"""
    # Verificar se animal existe
    animal = (
        db.query(Animal)
        .filter(Animal.ID == plano.ID_ANIMAL, Animal.STATUS_ANIMAL == "ATIVO")
        .first()
    )

    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")

    # Inativar planos anteriores do animal
    db.query(PlanoAlimentar).filter(
        PlanoAlimentar.ID_ANIMAL == plano.ID_ANIMAL,
        PlanoAlimentar.STATUS_PLANO == "ATIVO",
    ).update({"STATUS_PLANO": "INATIVO"})

    db_plano = PlanoAlimentar(**plano.dict(), ID_USUARIO_CADASTRO=current_user.ID)
    db.add(db_plano)
    db.commit()
    db.refresh(db_plano)

    return await _enrich_plano_response(db_plano, db)


@router.get("/planos", response_model=dict)
async def list_planos_alimentares(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    animal_id: Optional[int] = Query(None, description="Filtrar por animal"),
    categoria: Optional[CategoriaNutricionalEnum] = Query(
        None, description="Filtrar por categoria"
    ),
    status_plano: Optional[str] = Query(None, description="Filtrar planos"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Listar planos alimentares"""
    query = db.query(PlanoAlimentar)

    # Filtros
    if animal_id:
        query = query.filter(PlanoAlimentar.ID_ANIMAL == animal_id)
    if categoria:
        query = query.filter(PlanoAlimentar.CATEGORIA_NUTRICIONAL == categoria)
    if status_plano:
        query = query.filter(PlanoAlimentar.STATUS_PLANO == status_plano)

    # Paginação
    total = query.count()
    offset = (page - 1) * limit
    planos = (
        query.order_by(desc(PlanoAlimentar.DATA_INICIO))
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Enriquecer resposta
    planos_response = []
    for plano in planos:
        response = await _enrich_plano_response(plano, db)
        planos_response.append(response)

    return {
        "planos": planos_response,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
    }


# ======================================
# FORNECIMENTO INDIVIDUAL
# ======================================


@router.post(
    "/fornecimento",
    response_model=FornecimentoRacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registrar_fornecimento(
    fornecimento: FornecimentoRacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Registrar fornecimento de ração para animal"""
    # Verificar animal e produto
    animal = (
        db.query(Animal)
        .filter(Animal.ID == fornecimento.ID_ANIMAL, Animal.STATUS_ANIMAL == "ATIVO")
        .first()
    )
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")

    produto = (
        db.query(ProdutoRacao)
        .filter(ProdutoRacao.ID == fornecimento.ID_PRODUTO, ProdutoRacao.ATIVO == "S")
        .first()
    )
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Verificar estoque
    if produto.ESTOQUE_ATUAL < fornecimento.QUANTIDADE_FORNECIDA:
        raise HTTPException(
            status_code=400,
            detail=f"Estoque insuficiente. Disponível: {produto.ESTOQUE_ATUAL} {produto.UNIDADE_MEDIDA}",
        )

    # Buscar peso atual do animal se não informado
    if not fornecimento.PESO_ANIMAL_REFERENCIA:
        ultimo_peso = (
            db.query(HistoricoCrescimento)
            .filter(
                HistoricoCrescimento.ID_ANIMAL == fornecimento.ID_ANIMAL,
                HistoricoCrescimento.PESO.isnot(None),
            )
            .order_by(desc(HistoricoCrescimento.DATA_MEDICAO))
            .first()
        )

        if ultimo_peso:
            fornecimento.PESO_ANIMAL_REFERENCIA = ultimo_peso.PESO

    db_fornecimento = FornecimentoRacaoAnimal(
        **fornecimento.dict(), ID_USUARIO_REGISTRO=current_user.ID
    )
    db.add(db_fornecimento)
    db.commit()
    db.refresh(db_fornecimento)

    return await _enrich_fornecimento_response(db_fornecimento, db)


# ======================================
# ITENS DO PLANO ALIMENTAR
# ======================================


@router.post(
    "/planos/{plano_id}/itens",
    response_model=ItemPlanoAlimentarResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_item_plano(
    plano_id: int,
    item: ItemPlanoAlimentarCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Adicionar produto ao plano alimentar"""
    plano = db.query(PlanoAlimentar).filter(PlanoAlimentar.ID == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")

    produto = (
        db.query(ProdutoRacao)
        .filter(ProdutoRacao.ID == item.ID_PRODUTO, ProdutoRacao.ATIVO == "S")
        .first()
    )
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    db_item = ItemPlanoAlimentar(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return await _enrich_item_response(db_item, db)


@router.get("/planos/{plano_id}/itens", response_model=List[ItemPlanoAlimentarResponse])
async def list_itens_plano(
    plano_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Listar itens do plano alimentar"""
    itens = (
        db.query(ItemPlanoAlimentar)
        .filter(
            ItemPlanoAlimentar.ID_PLANO == plano_id, ItemPlanoAlimentar.ATIVO == "S"
        )
        .all()
    )

    return [await _enrich_item_response(item, db) for item in itens]


@router.put("/planos/itens/{item_id}", response_model=ItemPlanoAlimentarResponse)
async def update_item_plano(
    item_id: int,
    item_update: ItemPlanoAlimentarUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualizar item do plano"""
    item = (
        db.query(ItemPlanoAlimentar)
        .filter(ItemPlanoAlimentar.ID == item_id, ItemPlanoAlimentar.ATIVO == "S")
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    for field, value in item_update.dict(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)

    return await _enrich_item_response(item, db)


@router.put("/planos/{plano_id}", response_model=PlanoAlimentarResponse)
async def update_plano_alimentar(
    plano_id: int,
    plano_update: PlanoAlimentarUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualizar plano alimentar"""
    plano = db.query(PlanoAlimentar).filter(PlanoAlimentar.ID == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")

    for field, value in plano_update.dict(exclude_unset=True).items():
        setattr(plano, field, value)

    db.commit()
    db.refresh(plano)

    return await _enrich_plano_response(plano, db)


@router.put("/fornecimento/{fornecimento_id}", response_model=FornecimentoRacaoResponse)
async def update_fornecimento(
    fornecimento_id: int,
    fornecimento_update: FornecimentoRacaoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualizar registro de fornecimento"""
    fornecimento = (
        db.query(FornecimentoRacaoAnimal)
        .filter(FornecimentoRacaoAnimal.ID == fornecimento_id)
        .first()
    )
    if not fornecimento:
        raise HTTPException(status_code=404, detail="Fornecimento não encontrado")

    for field, value in fornecimento_update.dict(exclude_unset=True).items():
        setattr(fornecimento, field, value)

    db.commit()
    db.refresh(fornecimento)

    return await _enrich_fornecimento_response(fornecimento, db)


@router.delete("/planos/itens/{item_id}")
async def delete_item_plano(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Inativar produto de ração"""
    item = (
        db.query(ItemPlanoAlimentar)
        .filter(ItemPlanoAlimentar.ID == item_id, ItemPlanoAlimentar.ATIVO == "S")
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    item.ATIVO = "N"
    db.commit()

    return {"message": "Item inativado com sucesso"}


# ======================================
# AUTOCOMPLETE E BUSCA
# ======================================


@router.get(
    "/produtos/search/autocomplete", response_model=List[ProdutoRacaoAutocomplete]
)
async def autocomplete_produtos(
    q: Optional[str] = Query("", description="Termo de busca"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Busca produtos para autocomplete"""
    query = db.query(ProdutoRacao).filter(ProdutoRacao.ATIVO == "S")

    if q:
        query = query.filter(ProdutoRacao.NOME.ilike(f"%{q}%"))

    produtos = query.order_by(ProdutoRacao.NOME).limit(50).all()

    return [
        ProdutoRacaoAutocomplete(
            value=p.ID,
            label=f"{p.NOME} ({p.ESTOQUE_ATUAL} {p.UNIDADE_MEDIDA})",
            nome=p.NOME,
            estoque_atual=p.ESTOQUE_ATUAL,
            unidade_medida=p.UNIDADE_MEDIDA,
            tipo_alimento=p.TIPO_ALIMENTO,
            status_estoque=_calcular_status_estoque(p),
        )
        for p in produtos
    ]


# ======================================
# CÁLCULOS NUTRICIONAIS
# ======================================


@router.get("/calculo-nutricional/{animal_id}", response_model=CalculoNutricional)
async def calcular_necessidades_nutricionais(
    animal_id: int,
    categoria: CategoriaNutricionalEnum,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calcular necessidades nutricionais do animal"""
    animal = (
        db.query(Animal)
        .filter(Animal.ID == animal_id, Animal.STATUS_ANIMAL == "ATIVO")
        .first()
    )

    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")

    # Buscar último peso
    ultimo_peso = (
        db.query(HistoricoCrescimento)
        .filter(
            HistoricoCrescimento.ID_ANIMAL == animal_id,
            HistoricoCrescimento.PESO.isnot(None),
        )
        .order_by(desc(HistoricoCrescimento.DATA_MEDICAO))
        .first()
    )

    peso = ultimo_peso.PESO if ultimo_peso else animal.PESO_ATUAL or 500

    # Cálculos baseados na categoria
    percentual_peso = _get_percentual_por_categoria(categoria)
    quantidade_diaria = peso * (percentual_peso / 100)

    # Distribuição padrão por refeições
    distribuicao = {
        "manha": round(quantidade_diaria * 0.4, 2),
        "tarde": round(quantidade_diaria * 0.35, 2),
        "noite": round(quantidade_diaria * 0.25, 2),
    }

    return CalculoNutricional(
        categoria_nutricional=categoria,
        peso_animal=peso,
        quantidade_sugerida_kg=quantidade_diaria,
        percentual_peso_vivo=percentual_peso,
        distribuicao_refeicoes=distribuicao,
        observacoes_nutricionais=_get_observacoes_categoria(categoria),
    )


@router.get("/relatorios/consumo-animal", response_model=List[ConsumoAnimalResumo])
async def relatorio_consumo_animal(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    animal_id: Optional[int] = Query(None, description="Filtrar por animal"),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
):
    """Relatório de consumo por animal"""
    query = text(
        """
        SELECT a.ID as animal_id, a.NOME as animal_nome, a.NUMERO_REGISTRO,
               p.NOME as produto_nome, p.TIPO_ALIMENTO,
               SUM(f.QUANTIDADE_FORNECIDA) as total_consumido,
               AVG(f.QUANTIDADE_FORNECIDA) as media_diaria,
               SUM(f.QUANTIDADE_FORNECIDA * NVL(p.PRECO_UNITARIO, 0)) as custo_total,
               MAX(f.DATA_FORNECIMENTO) as ultima_refeicao
        FROM VW_CONSUMO_RACAO_ANIMAL v
        JOIN ANIMAIS a ON v.ANIMAL_ID = a.ID
        JOIN PRODUTOS_RACAO p ON v.PRODUTO_ID = p.ID
        JOIN FORNECIMENTO_RACAO_ANIMAL f ON f.ID_ANIMAL = a.ID AND f.ID_PRODUTO = p.ID
        WHERE a.STATUS_ANIMAL = 'ATIVO'
    """
    )

    conditions = []
    params = {}

    if animal_id:
        conditions.append("a.ID = :animal_id")
        params["animal_id"] = animal_id

    if data_inicio:
        conditions.append("f.DATA_FORNECIMENTO >= TO_DATE(:data_inicio, 'YYYY-MM-DD')")
        params["data_inicio"] = data_inicio

    if data_fim:
        conditions.append(
            "f.DATA_FORNECIMENTO <= TO_DATE(:data_fim, 'YYYY-MM-DD') + INTERVAL '1' DAY"
        )
        params["data_fim"] = data_fim

    if conditions:
        query = text(str(query) + " AND " + " AND ".join(conditions))

    query = text(
        str(query)
        + " GROUP BY a.ID, a.NOME, a.NUMERO_REGISTRO, p.NOME, p.TIPO_ALIMENTO ORDER BY a.NOME, p.NOME"
    )

    result = db.execute(query, params).fetchall()
    return [
        ConsumoAnimalResumo(
            animal_id=row.animal_id,
            animal_nome=row.animal_nome,
            numero_registro=row.numero_registro,
            produto_nome=row.produto_nome,
            tipo_alimento=row.tipo_alimento,
            total_consumido=row.total_consumido,
            media_diaria=row.media_diaria,
            custo_total=row.custo_total,
            ultima_refeicao=row.ultima_refeicao,
        )
        for row in result
    ]


@router.get("/relatorios/previsao-consumo", response_model=List[PrevisaoConsumoRacao])
async def relatorio_previsao_consumo(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Previsão de consumo baseada no histórico"""
    query = text(
        """
        WITH consumo_diario AS (
            SELECT ID_PRODUTO,
                   AVG(QUANTIDADE_FORNECIDA) as media_diaria
            FROM FORNECIMENTO_RACAO_ANIMAL f
            WHERE f.DATA_FORNECIMENTO >= SYSDATE - 30
            GROUP BY ID_PRODUTO
        )
        SELECT p.ID as produto_id, p.NOME as produto_nome,
               NVL(c.media_diaria, 0) as consumo_diario_medio,
               p.ESTOQUE_ATUAL,
               CASE 
                   WHEN NVL(c.media_diaria, 0) > 0 THEN 
                       FLOOR(p.ESTOQUE_ATUAL / c.media_diaria)
                   ELSE 999
               END as dias_restantes,
               CASE 
                   WHEN NVL(c.media_diaria, 0) > 0 THEN 
                       SYSDATE + (p.ESTOQUE_ATUAL / c.media_diaria)
                   ELSE SYSDATE + 999
               END as data_prevista_fim
        FROM PRODUTOS_RACAO p
        LEFT JOIN consumo_diario c ON p.ID = c.ID_PRODUTO
        WHERE p.ATIVO = 'S'
        ORDER BY dias_restantes
    """
    )

    result = db.execute(query).fetchall()
    previsoes = []

    for row in result:
        recomendacao = "OK"
        if row.dias_restantes <= 7:
            recomendacao = "COMPRAR_URGENTE"
        elif row.dias_restantes <= 15:
            recomendacao = "COMPRAR_BREVE"

        previsoes.append(
            PrevisaoConsumoRacao(
                produto_id=row.produto_id,
                produto_nome=row.produto_nome,
                consumo_diario_medio=row.consumo_diario_medio,
                estoque_atual=row.estoque_atual,
                dias_restantes=row.dias_restantes,
                data_prevista_fim=row.data_prevista_fim,
                recomendacao=recomendacao,
            )
        )

    return previsoes


# ======================================
# FUNÇÕES AUXILIARES
# ======================================


@router.get("/relatorios/estoque-baixo", response_model=List[EstoqueRacaoBaixo])
async def relatorio_estoque_baixo(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Relatório de produtos com estoque baixo ou vencimento próximo"""
    query = text(
        """
        SELECT ID AS id, 
               NOME AS nome, 
               TIPO_ALIMENTO as tipo_alimento, 
               ESTOQUE_ATUAL as estoque_atual, 
               ESTOQUE_MINIMO as estoque_minimo,
               UNIDADE_MEDIDA as unidade_medida,  
               FORNECEDOR_PRINCIPAL as fornecedor_principal, 
               DATA_VALIDADE as data_validade,
               STATUS_ALERTA as status_alerta, 
               DIAS_VENCIMENTO as dias_vencimento
        FROM VW_PRODUTOS_RACAO_ALERTAS
        ORDER BY 
            CASE STATUS_ALERTA
                WHEN 'SEM_ESTOQUE' THEN 1
                WHEN 'ESTOQUE_BAIXO' THEN 2
                WHEN 'VENCIDO' THEN 3
                WHEN 'VENCIMENTO_PROXIMO' THEN 4
                ELSE 5
            END,
            ESTOQUE_ATUAL
    """
    )

    result = db.execute(query).fetchall()
    return [
        EstoqueRacaoBaixo(
            produto_id=row.id,
            nome=row.nome,
            tipo_alimento=row.tipo_alimento,
            estoque_atual=row.estoque_atual,
            estoque_minimo=row.estoque_minimo,
            unidade_medida=row.unidade_medida,
            status_alerta=row.status_alerta,
            dias_vencimento=row.dias_vencimento,
            fornecedor_principal=row.fornecedor_principal,
        )
        for row in result
    ]


# ======================================
# FUNÇÕES AUXILIARES
# ======================================


async def _enrich_item_response(
    item: ItemPlanoAlimentar, db: Session
) -> ItemPlanoAlimentarResponse:
    """Enriquecer resposta do item do plano"""
    response = ItemPlanoAlimentarResponse.from_orm(item)

    # Dados do produto
    produto = db.query(ProdutoRacao).filter(ProdutoRacao.ID == item.ID_PRODUTO).first()
    if produto:
        response.produto_nome = produto.NOME
        response.produto_unidade = produto.UNIDADE_MEDIDA
        response.produto_tipo = produto.TIPO_ALIMENTO.value
        if produto.PRECO_UNITARIO:
            response.custo_diario = item.QUANTIDADE_DIARIA * produto.PRECO_UNITARIO

    return response


async def _enrich_produto_response(
    produto: ProdutoRacao, db: Session
) -> ProdutoRacaoResponse:
    """Enriquecer resposta do produto com dados calculados"""
    response = ProdutoRacaoResponse.from_orm(produto)

    # Status do estoque
    response.status_estoque = _calcular_status_estoque(produto)

    # Dias para vencimento
    if produto.DATA_VALIDADE:
        dias = (produto.DATA_VALIDADE - datetime.now()).days
        response.dias_vencimento = max(0, dias)

    # Valor total do estoque
    if produto.PRECO_UNITARIO:
        response.valor_total_estoque = produto.ESTOQUE_ATUAL * produto.PRECO_UNITARIO

    return response


async def _enrich_movimentacao_response(
    movimentacao: MovimentacaoProdutoRacao, db: Session
) -> MovimentacaoRacaoResponse:
    """Enriquecer resposta da movimentação"""
    response = MovimentacaoRacaoResponse.from_orm(movimentacao)

    # Dados do produto
    produto = (
        db.query(ProdutoRacao)
        .filter(ProdutoRacao.ID == movimentacao.ID_PRODUTO)
        .first()
    )
    if produto:
        response.produto_nome = produto.NOME
        response.produto_unidade = produto.UNIDADE_MEDIDA

    # Dados do animal se aplicável
    if movimentacao.ID_ANIMAL:
        animal = db.query(Animal).filter(Animal.ID == movimentacao.ID_ANIMAL).first()
        if animal:
            response.animal_nome = animal.NOME

    return response


async def _enrich_plano_response(
    plano: PlanoAlimentar, db: Session
) -> PlanoAlimentarResponse:
    """Enriquecer resposta do plano alimentar"""
    response = PlanoAlimentarResponse.from_orm(plano)

    # Dados do animal
    animal = db.query(Animal).filter(Animal.ID == plano.ID_ANIMAL).first()
    if animal:
        response.animal_nome = animal.NOME
        response.animal_numero_registro = animal.NUMERO_REGISTRO

    # Contar produtos do plano
    item_plano = db.query(ItemPlanoAlimentar).filter(
        ItemPlanoAlimentar.ID_PLANO == plano.ID, ItemPlanoAlimentar.ATIVO == "S"
    )

    total_produtos = item_plano.count()

    response.total_produtos = total_produtos

    # Calcular custo diario
    custo_diario_estimado = 0
    if item_plano:
        for item in item_plano:
            # Dados do produto
            produto = (
                db.query(ProdutoRacao)
                .filter(ProdutoRacao.ID == item.ID_PRODUTO)
                .first()
            )
            if produto:
                if produto.PRECO_UNITARIO:
                    custo_diario_estimado += (
                        item.QUANTIDADE_DIARIA * produto.PRECO_UNITARIO
                    )
    response.custo_diario_estimado = custo_diario_estimado
    return response


async def _enrich_fornecimento_response(
    fornecimento: FornecimentoRacaoAnimal, db: Session
) -> FornecimentoRacaoResponse:
    """Enriquecer resposta do fornecimento"""
    response = FornecimentoRacaoResponse.from_orm(fornecimento)

    # Dados do animal
    animal = db.query(Animal).filter(Animal.ID == fornecimento.ID_ANIMAL).first()
    if animal:
        response.animal_nome = animal.NOME
        response.animal_numero_registro = animal.NUMERO_REGISTRO

    # Dados do produto
    produto = (
        db.query(ProdutoRacao)
        .filter(ProdutoRacao.ID == fornecimento.ID_PRODUTO)
        .first()
    )
    if produto:
        response.produto_nome = produto.NOME
        response.produto_unidade = produto.UNIDADE_MEDIDA
        if produto.PRECO_UNITARIO:
            response.custo_fornecimento = (
                fornecimento.QUANTIDADE_FORNECIDA * produto.PRECO_UNITARIO
            )

    return response


def _calcular_status_estoque(produto: ProdutoRacao) -> StatusEstoqueRacaoEnum:
    """Calcular status do estoque"""
    if produto.ESTOQUE_ATUAL <= 0:
        return StatusEstoqueRacaoEnum.SEM_ESTOQUE
    elif produto.ESTOQUE_ATUAL <= produto.ESTOQUE_MINIMO:
        return StatusEstoqueRacaoEnum.ESTOQUE_BAIXO
    elif produto.DATA_VALIDADE:
        data_validade = produto.DATA_VALIDADE.date()
        data_hoje = datetime.now().date()
        dias = (data_validade - data_hoje).days
        if dias <= 0:
            return StatusEstoqueRacaoEnum.VENCIDO
        elif dias <= 30:
            return StatusEstoqueRacaoEnum.VENCIMENTO_PROXIMO

    return StatusEstoqueRacaoEnum.OK


def _get_percentual_por_categoria(categoria: CategoriaNutricionalEnum) -> float:
    """Retornar percentual do peso vivo por categoria"""
    percentuais = {
        CategoriaNutricionalEnum.POTRO: 3.5,
        CategoriaNutricionalEnum.JOVEM: 3.0,
        CategoriaNutricionalEnum.ADULTO_MANUTENCAO: 2.0,
        CategoriaNutricionalEnum.ADULTO_TRABALHO_LEVE: 2.5,
        CategoriaNutricionalEnum.ADULTO_TRABALHO_MODERADO: 3.0,
        CategoriaNutricionalEnum.ADULTO_TRABALHO_INTENSO: 3.5,
        CategoriaNutricionalEnum.EGUA_GESTANTE: 2.5,
        CategoriaNutricionalEnum.EGUA_LACTANTE: 3.0,
        CategoriaNutricionalEnum.REPRODUTOR: 2.5,
        CategoriaNutricionalEnum.IDOSO: 2.5,
    }
    return percentuais.get(categoria, 2.0)


def _get_observacoes_categoria(categoria: CategoriaNutricionalEnum) -> str:
    """Retornar observações específicas por categoria"""
    observacoes = {
        CategoriaNutricionalEnum.POTRO: "Ração com alta digestibilidade e proteína para crescimento",
        CategoriaNutricionalEnum.JOVEM: "Balanceamento adequado para desenvolvimento",
        CategoriaNutricionalEnum.ADULTO_MANUTENCAO: "Manutenção do peso e condição corporal",
        CategoriaNutricionalEnum.ADULTO_TRABALHO_LEVE: "Energia adicional para atividade leve",
        CategoriaNutricionalEnum.ADULTO_TRABALHO_MODERADO: "Suporte energético para trabalho moderado",
        CategoriaNutricionalEnum.ADULTO_TRABALHO_INTENSO: "Alta energia e proteína para performance",
        CategoriaNutricionalEnum.EGUA_GESTANTE: "Nutrição adequada para gestação",
        CategoriaNutricionalEnum.EGUA_LACTANTE: "Suporte nutricional para lactação",
        CategoriaNutricionalEnum.REPRODUTOR: "Nutrição para manutenção da fertilidade",
        CategoriaNutricionalEnum.IDOSO: "Digestibilidade facilitada para cavalos idosos",
    }
    return observacoes.get(categoria, "Consulte um nutricionista equino")
