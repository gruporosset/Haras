from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.terreno import Terreno
from app.models.user import User
from app.schemas.terreno import TerrenoCreate, TerrenoResponse, TerrenoUpdate
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/terrenos", tags=["Terrenos"])


@router.post("/", response_model=TerrenoResponse, status_code=status.HTTP_201_CREATED)
async def create_terreno(
    terreno: TerrenoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if terreno.ID_USUARIO_CADASTRO != current_user.ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a cadastrar para outro usuário",
        )

    db_terreno = Terreno(**terreno.dict())
    db.add(db_terreno)
    db.commit()
    db.refresh(db_terreno)
    return db_terreno


@router.get("/", response_model=dict)
async def list_terrenos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    nome: Optional[str] = Query(None, description="Filtrar por nome do terreno"),
    status: Optional[str] = Query(None, description="Filtrar por status do terreno"),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    sort_by: Optional[str] = Query("ID", description="Coluna para ordenação"),
    order: Optional[str] = Query("asc", description="Ordem: asc ou desc"),
):
    query = db.query(Terreno)

    # Aplicar filtros
    if nome:
        query = query.filter(Terreno.NOME.ilike(f"%{nome}%"))
    if status:
        query = query.filter(Terreno.STATUS_TERRENO == status)

    # Contar total de registros
    total = query.count()

    # Aplicar ordenação
    if sort_by in [
        "ID",
        "NOME",
        "AREA_HECTARES",
        "STATUS_TERRENO",
        "LATITUDE",
        "LONGITUDE",
    ]:
        order_column = getattr(Terreno, sort_by)
        if order.lower() == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

    # Aplicar paginação
    offset = (page - 1) * limit
    terrenos = query.offset(offset).limit(limit).all()

    # Converter os objetos SQLAlchemy para modelos Pydantic
    terrenos_response = [TerrenoResponse.from_orm(terreno) for terreno in terrenos]

    return {"terrenos": terrenos_response, "total": total, "page": page, "limit": limit}


@router.get("/{id}", response_model=TerrenoResponse)
async def get_terreno(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    terreno = db.query(Terreno).filter(Terreno.ID == id).first()
    if not terreno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Terreno não encontrado"
        )
    return terreno


@router.put("/{id}", response_model=TerrenoResponse)
async def update_terreno(
    id: int,
    terreno: TerrenoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_terreno = db.query(Terreno).filter(Terreno.ID == id).first()
    if not db_terreno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Terreno não encontrado"
        )

    for key, value in terreno.dict(exclude_unset=True).items():
        setattr(db_terreno, key, value)

    db.commit()
    db.refresh(db_terreno)
    return db_terreno


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_terreno(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_terreno = db.query(Terreno).filter(Terreno.ID == id).first()
    if not db_terreno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Terreno não encontrado"
        )

    db.delete(db_terreno)
    db.commit()
    return None
