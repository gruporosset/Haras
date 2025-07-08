from datetime import datetime
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.animal import Animal
from app.models.movimentacao import MovimentacaoAnimais
from app.models.terreno import Terreno
from app.models.user import User
from app.schemas.movimentacao import (
    HistoricoMovimentacao,
    LocalizacaoAtual,
    MovimentacaoCreate,
    MovimentacaoResponse,
    MovimentacaoUpdate,
    TipoMovimentacaoEnum,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import desc, func

router = APIRouter(prefix="/api/movimentacoes", tags=["Movimentações"])


@router.post(
    "/", response_model=MovimentacaoResponse, status_code=status.HTTP_201_CREATED
)
async def create_movimentacao(
    movimentacao: MovimentacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verificar se animal existe
    animal = db.query(Animal).filter(Animal.ID == movimentacao.ID_ANIMAL).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    # Validar terrenos se informados
    if movimentacao.ID_TERRENO_ORIGEM:
        terreno_origem = (
            db.query(Terreno)
            .filter(Terreno.ID == movimentacao.ID_TERRENO_ORIGEM)
            .first()
        )
        if not terreno_origem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Terreno de origem não encontrado",
            )

    if movimentacao.ID_TERRENO_DESTINO:
        terreno_destino = (
            db.query(Terreno)
            .filter(Terreno.ID == movimentacao.ID_TERRENO_DESTINO)
            .first()
        )
        if not terreno_destino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Terreno de destino não encontrado",
            )

    # Validar que pelo menos origem ou destino esteja preenchido
    # if not any([movimentacao.ID_TERRENO_ORIGEM, movimentacao.ID_TERRENO_DESTINO,
    #             movimentacao.ORIGEM_EXTERNA, movimentacao.DESTINO_EXTERNO]):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
    #                       detail="Deve informar pelo menos origem ou destino")

    db_movimentacao = MovimentacaoAnimais(**movimentacao.dict())
    db.add(db_movimentacao)
    db.commit()
    db.refresh(db_movimentacao)

    return await _enrich_movimentacao_response(db_movimentacao, db)


@router.get("/", response_model=dict)
async def list_movimentacoes(
    db: Session = Depends(get_db),
    animal_id: Optional[int] = Query(None, description="Filtrar por animal"),
    tipo_movimentacao: Optional[TipoMovimentacaoEnum] = Query(
        None, description="Filtrar por tipo"
    ),
    terreno_id: Optional[int] = Query(
        None, description="Filtrar por terreno (origem ou destino)"
    ),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    query = db.query(MovimentacaoAnimais)

    if animal_id:
        query = query.filter(MovimentacaoAnimais.ID_ANIMAL == animal_id)
    if tipo_movimentacao:
        query = query.filter(MovimentacaoAnimais.TIPO_MOVIMENTACAO == tipo_movimentacao)
    if terreno_id:
        query = query.filter(
            (MovimentacaoAnimais.ID_TERRENO_ORIGEM == terreno_id)
            | (MovimentacaoAnimais.ID_TERRENO_DESTINO == terreno_id)
        )
    if data_inicio:
        query = query.filter(
            MovimentacaoAnimais.DATA_MOVIMENTACAO >= datetime.fromisoformat(data_inicio)
        )
    if data_fim:
        query = query.filter(
            MovimentacaoAnimais.DATA_MOVIMENTACAO <= datetime.fromisoformat(data_fim)
        )

    total = query.count()
    offset = (page - 1) * limit
    movimentacoes = (
        query.order_by(desc(MovimentacaoAnimais.DATA_MOVIMENTACAO))
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Enriquecer com dados relacionados
    enriched_movimentacoes = []
    for mov in movimentacoes:
        enriched = await _enrich_movimentacao_response(mov, db)
        enriched_movimentacoes.append(enriched)

    return {
        "movimentacoes": enriched_movimentacoes,
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/{id}", response_model=MovimentacaoResponse)
async def get_movimentacao(
    id: int,
    db: Session = Depends(get_db),
):
    movimentacao = (
        db.query(MovimentacaoAnimais).filter(MovimentacaoAnimais.ID == id).first()
    )
    if not movimentacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movimentação não encontrada"
        )

    return await _enrich_movimentacao_response(movimentacao, db)


@router.put("/{id}", response_model=MovimentacaoResponse)
async def update_movimentacao(
    id: int,
    movimentacao: MovimentacaoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_movimentacao = (
        db.query(MovimentacaoAnimais).filter(MovimentacaoAnimais.ID == id).first()
    )
    if not db_movimentacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movimentação não encontrada"
        )

    for key, value in movimentacao.dict(exclude_unset=True).items():
        setattr(db_movimentacao, key, value)

    db.commit()
    db.refresh(db_movimentacao)
    return await _enrich_movimentacao_response(db_movimentacao, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movimentacao(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_movimentacao = (
        db.query(MovimentacaoAnimais).filter(MovimentacaoAnimais.ID == id).first()
    )
    if not db_movimentacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movimentação não encontrada"
        )

    db.delete(db_movimentacao)
    db.commit()


@router.get("/animal/{animal_id}/historico", response_model=HistoricoMovimentacao)
async def get_historico_animal(
    animal_id: int,
    db: Session = Depends(get_db),
):
    # Verificar se animal existe
    animal = db.query(Animal).filter(Animal.ID == animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    # Buscar todas movimentações do animal
    movimentacoes = (
        db.query(MovimentacaoAnimais)
        .filter(MovimentacaoAnimais.ID_ANIMAL == animal_id)
        .order_by(desc(MovimentacaoAnimais.DATA_MOVIMENTACAO))
        .all()
    )

    # Enriquecer dados
    enriched_movimentacoes = []
    for mov in movimentacoes:
        enriched = await _enrich_movimentacao_response(mov, db)
        enriched_movimentacoes.append(enriched)

    # Determinar localização atual
    localizacao_atual = "Não informado"
    if movimentacoes:
        ultima = movimentacoes[0]
        if ultima.ID_TERRENO_DESTINO:
            terreno = (
                db.query(Terreno)
                .filter(Terreno.ID == ultima.ID_TERRENO_DESTINO)
                .first()
            )
            localizacao_atual = (
                terreno.NOME if terreno else f"Terreno #{ultima.ID_TERRENO_DESTINO}"
            )
        elif ultima.DESTINO_EXTERNO:
            localizacao_atual = ultima.DESTINO_EXTERNO

    return HistoricoMovimentacao(
        movimentacoes=enriched_movimentacoes, localizacao_atual=localizacao_atual
    )


@router.get("/relatorio/localizacoes", response_model=List[LocalizacaoAtual])
async def get_localizacoes_atuais(
    animal_id: Optional[int] = Query(None, description="Filtrar por animal"),
    terreno_id: Optional[int] = Query(
        None, description="Filtrar por terreno (origem ou destino)"
    ),
    db: Session = Depends(get_db),
):
    # Buscar última movimentação de cada animal
    subquery = (
        db.query(
            MovimentacaoAnimais.ID_ANIMAL,
            func.max(MovimentacaoAnimais.DATA_MOVIMENTACAO).label("ultima_data"),
        )
        .group_by(MovimentacaoAnimais.ID_ANIMAL)
        .subquery()
    )

    query = (
        db.query(MovimentacaoAnimais, Animal.NOME)
        .join(Animal, MovimentacaoAnimais.ID_ANIMAL == Animal.ID)
        .join(
            subquery,
            (MovimentacaoAnimais.ID_ANIMAL == subquery.c.ID_ANIMAL)
            & (MovimentacaoAnimais.DATA_MOVIMENTACAO == subquery.c.ultima_data),
        )
    )

    if animal_id:
        query = query.filter(MovimentacaoAnimais.ID_ANIMAL == animal_id)

    if terreno_id:
        query = query.filter((MovimentacaoAnimais.ID_TERRENO_DESTINO == terreno_id))

    ultimas_movimentacoes = query.all()

    resultado = []
    localizacao_tipo = None
    localizacao = None
    for mov, animal_nome in ultimas_movimentacoes:
        terreno_atual = None
        local_externo = None

        if mov.ID_TERRENO_DESTINO:
            terreno = (
                db.query(Terreno).filter(Terreno.ID == mov.ID_TERRENO_DESTINO).first()
            )
            terreno_atual = (
                terreno.NOME if terreno else f"Terreno #{mov.ID_TERRENO_DESTINO}"
            )
            localizacao_tipo = "terreno"
            localizacao = terreno_atual
        elif mov.DESTINO_EXTERNO:
            local_externo = mov.DESTINO_EXTERNO
            localizacao_tipo = "externo"
            localizacao = local_externo

        resultado.append(
            LocalizacaoAtual(
                animal_id=mov.ID_ANIMAL,
                animal_nome=animal_nome,
                terreno_atual=terreno_atual,
                local_externo=local_externo,
                data_ultima_movimentacao=mov.DATA_MOVIMENTACAO,
                tipo_ultima_movimentacao=mov.TIPO_MOVIMENTACAO,
                localizacao_tipo=localizacao_tipo,
                localizacao=localizacao,
            )
        )

    return resultado


@router.get("/options/tipos")
async def get_tipos_movimentacao():
    return [
        {"value": "TRANSFERENCIA", "label": "Transferência"},
        {"value": "ENTRADA", "label": "Entrada"},
        {"value": "SAIDA", "label": "Saída"},
        {"value": "VENDA", "label": "Venda"},
        {"value": "EMPRESTIMO", "label": "Empréstimo"},
        {"value": "RETORNO", "label": "Retorno"},
    ]


# Função auxiliar para enriquecer resposta


async def _enrich_movimentacao_response(
    movimentacao: MovimentacaoAnimais, db: Session
) -> MovimentacaoResponse:
    # Buscar dados relacionados
    animal = db.query(Animal).filter(Animal.ID == movimentacao.ID_ANIMAL).first()
    terreno_origem = None
    terreno_destino = None

    if movimentacao.ID_TERRENO_ORIGEM:
        terreno_origem = (
            db.query(Terreno)
            .filter(Terreno.ID == movimentacao.ID_TERRENO_ORIGEM)
            .first()
        )

    if movimentacao.ID_TERRENO_DESTINO:
        terreno_destino = (
            db.query(Terreno)
            .filter(Terreno.ID == movimentacao.ID_TERRENO_DESTINO)
            .first()
        )

    # Criar response com dados enriquecidos
    response_data = MovimentacaoResponse.from_orm(movimentacao)
    response_data.animal_nome = animal.NOME if animal else None
    response_data.terreno_origem_nome = terreno_origem.NOME if terreno_origem else None
    response_data.terreno_destino_nome = (
        terreno_destino.NOME if terreno_destino else None
    )

    return response_data
