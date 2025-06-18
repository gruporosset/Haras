from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.terreno import Terreno
from app.models.user import User
from app.schemas.terreno import TerrenoCreate, TerrenoUpdate, TerrenoResponse
from typing import List

router = APIRouter(prefix="/api/terrenos", tags=["Terrenos"])

@router.post("/", response_model=TerrenoResponse, status_code=status.HTTP_201_CREATED)
async def create_terreno(
    terreno: TerrenoCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if terreno.ID_USUARIO_CADASTRO != current_user.ID:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado a cadastrar para outro usuário")
    
    db_terreno = Terreno(**terreno.dict())
    db.add(db_terreno)
    db.commit()
    db.refresh(db_terreno)
    return db_terreno

@router.get("/", response_model=List[TerrenoResponse])
async def list_terrenos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Terreno).all()

@router.get("/{id}", response_model=TerrenoResponse)
async def get_terreno(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    terreno = db.query(Terreno).filter(Terreno.ID == id).first()
    if not terreno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Terreno não encontrado")
    return terreno

@router.put("/{id}", response_model=TerrenoResponse)
async def update_terreno(
    id: int, 
    terreno: TerrenoUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_terreno = db.query(Terreno).filter(Terreno.ID == id).first()
    if not db_terreno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Terreno não encontrado")
    
    for key, value in terreno.dict(exclude_unset=True).items():
        setattr(db_terreno, key, value)
    
    db.commit()
    db.refresh(db_terreno)
    return db_terreno

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_terreno(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_terreno = db.query(Terreno).filter(Terreno.ID == id).first()
    if not db_terreno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Terreno não encontrado")
    
    db.delete(db_terreno)
    db.commit()
    return None