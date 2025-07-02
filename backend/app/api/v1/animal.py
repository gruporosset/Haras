import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.animal import Animal
from app.models.user import User
from app.schemas.animal import (
    AnimalCreate,
    AnimalGenealogia,
    AnimalResponse,
    AnimalUpdate,
    FotoUploadResponse,
    SexoEnum,
    StatusAnimalEnum,
)
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

router = APIRouter(prefix="/api/animais", tags=["Animais"])

# Diretório para upload de fotos
UPLOAD_DIR = Path("uploads/animais")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=AnimalResponse, status_code=status.HTTP_201_CREATED)
async def create_animal(
    animal: AnimalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if animal.ID_USUARIO_CADASTRO != current_user.ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a cadastrar para outro usuário",
        )

    # Verificar se número de registro já existe
    if animal.NUMERO_REGISTRO:
        existing = (
            db.query(Animal)
            .filter(Animal.NUMERO_REGISTRO == animal.NUMERO_REGISTRO)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de registro já existe",
            )

    # Verificar se chip já existe
    if animal.CHIP_IDENTIFICACAO:
        existing = (
            db.query(Animal)
            .filter(Animal.CHIP_IDENTIFICACAO == animal.CHIP_IDENTIFICACAO)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chip de identificação já existe",
            )

    db_animal = Animal(**animal.model_dump())
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    return db_animal


@router.get("/", response_model=dict)
async def list_animais(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    nome: Optional[str] = Query(None, description="Filtrar por nome do animal"),
    sexo: Optional[SexoEnum] = Query(None, description="Filtrar por sexo"),
    status: Optional[StatusAnimalEnum] = Query(None, description="Filtrar por status"),
    numero_registro: Optional[str] = Query(
        None, description="Filtrar por número de registro"
    ),
    chip: Optional[str] = Query(None, description="Filtrar por chip"),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    sort_by: Optional[str] = Query("ID", description="Coluna para ordenação"),
    order: Optional[str] = Query("asc", description="Ordem: asc ou desc"),
):
    query = db.query(Animal)

    # Aplicar filtros
    if nome:
        query = query.filter(Animal.NOME.ilike(f"%{nome}%"))
    if sexo:
        query = query.filter(Animal.SEXO == sexo)
    if status:
        query = query.filter(Animal.STATUS_ANIMAL == status)
    if numero_registro:
        query = query.filter(Animal.NUMERO_REGISTRO.ilike(f"%{numero_registro}%"))
    if chip:
        query = query.filter(Animal.CHIP_IDENTIFICACAO.ilike(f"%{chip}%"))

    # Contar total de registros
    total = query.count()

    # Aplicar ordenação
    valid_sort_fields = [
        "ID",
        "NOME",
        "DATA_NASCIMENTO",
        "SEXO",
        "STATUS_ANIMAL",
        "NUMERO_REGISTRO",
    ]
    if sort_by in valid_sort_fields:
        order_column = getattr(Animal, sort_by)
        if order and order.lower() == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

    # Aplicar paginação
    offset = (page - 1) * limit
    animais = query.offset(offset).limit(limit).all()

    # Converter para Pydantic
    animais_response = [AnimalResponse.from_orm(animal) for animal in animais]

    return {"animais": animais_response, "total": total, "page": page, "limit": limit}


@router.get("/{id}", response_model=AnimalResponse)
async def get_animal(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    animal = db.query(Animal).filter(Animal.ID == id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )
    return animal


@router.put("/{id}", response_model=AnimalResponse)
async def update_animal(
    id: int,
    animal: AnimalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_animal = db.query(Animal).filter(Animal.ID == id).first()
    if not db_animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    # Verificar unicidade se alterando registro/chip
    if animal.NUMERO_REGISTRO and animal.NUMERO_REGISTRO != db_animal.NUMERO_REGISTRO:
        existing = (
            db.query(Animal)
            .filter(Animal.NUMERO_REGISTRO == animal.NUMERO_REGISTRO, Animal.ID != id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de registro já existe",
            )

    if (
        animal.CHIP_IDENTIFICACAO
        and animal.CHIP_IDENTIFICACAO != db_animal.CHIP_IDENTIFICACAO
    ):
        existing = (
            db.query(Animal)
            .filter(
                Animal.CHIP_IDENTIFICACAO == animal.CHIP_IDENTIFICACAO, Animal.ID != id
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chip de identificação já existe",
            )

    # Atualizar campos
    for key, value in animal.dict(exclude_unset=True).items():
        setattr(db_animal, key, value)

    db_animal.ID_USUARIO_ALTERACAO = current_user.ID
    db_animal.DATA_ALTERACAO = func.now()

    db.commit()
    db.refresh(db_animal)
    return db_animal


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_animal = db.query(Animal).filter(Animal.ID == id).first()
    if not db_animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    db.delete(db_animal)
    db.commit()
    return None


@router.get("/{id}/genealogia", response_model=AnimalGenealogia)
async def get_genealogia(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def get_animal_with_parents(animal_id):
        if not animal_id:
            return None

        animal = db.query(Animal).filter(Animal.ID == animal_id).first()
        if not animal:
            return None

        return {
            "animal": AnimalResponse.from_orm(animal),
            "pai": get_animal_with_parents(animal.ID_PAI),
            "mae": get_animal_with_parents(animal.ID_MAE),
        }

    genealogia = get_animal_with_parents(id)
    if not genealogia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    return genealogia


@router.post("/{id}/foto", response_model=FotoUploadResponse)
async def upload_foto(
    id: int,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verificar se animal existe
    animal = db.query(Animal).filter(Animal.ID == id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    # Validar tipo de arquivo
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if foto.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de arquivo não permitido",
        )

    # Gerar nome único
    if not foto.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado não possui um nome válido",
        )
    file_extension = foto.filename.split(".")[-1]
    filename = f"animal_{id}_{int(datetime.now().timestamp())}.{file_extension}"
    file_path = UPLOAD_DIR / filename

    # Salvar arquivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    # Atualizar animal se for primeira foto
    if animal.FOTO_PRINCIPAL is None:
        animal.FOTO_PRINCIPAL = f"/uploads/animais/{filename}"
        db.commit()

    return {
        "filename": filename,
        "url": f"/uploads/animais/{filename}",
        "message": "Foto enviada com sucesso",
    }


@router.get("/options/parents")
async def get_parent_options(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sexo: Optional[SexoEnum] = Query(
        None, description="Filtrar por sexo para parentesco"
    ),
):
    """Retorna lista de animais para seleção de pais/mães"""
    query = db.query(Animal).filter(Animal.STATUS_ANIMAL == StatusAnimalEnum.ATIVO)

    if sexo:
        query = query.filter(Animal.SEXO == sexo)

    animais = query.order_by(Animal.NOME).all()

    return [
        {
            "value": animal.ID,
            "label": f"{animal.NOME} ({animal.NUMERO_REGISTRO or 'S/R'})",
        }
        for animal in animais
    ]
