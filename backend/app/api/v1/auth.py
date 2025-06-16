from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_jwt_token, generate_reset_token
from app.models.user import User
from app.schemas.user import UserLogin, UserResetPassword, UserResponse, UserCreate, UserForgotPassword
from app.services.email_service import EmailService
from datetime import datetime, timedelta
import aiosmtplib
from email.message import EmailMessage

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar se o e-mail já existe
    db_user = db.query(User).filter(User.EMAIL == user.EMAIL).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já registrado")
    
    # Criar novo usuário
    hashed_password = hash_password(user.SENHA)
    new_user = User(
        NOME_COMPLETO=user.NOME_COMPLETO,
        EMAIL=user.EMAIL,
        SENHA_HASH=hashed_password,
        PERFIL=user.PERFIL,
        ATIVO='S'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=UserResponse)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.EMAIL == user.EMAIL, User.ATIVO == 'S').first()
    if not db_user or not verify_password(user.SENHA, db_user.SENHA_HASH):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    if db_user.BLOQUEADO_ATE and db_user.BLOQUEADO_ATE > datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário bloqueado")
    
    db_user.DATA_ULTIMO_LOGIN = datetime.utcnow()
    db_user.TENTATIVAS_LOGIN = 0
    db.commit()
    
    token = create_jwt_token({"sub": str(db_user.ID), "perfil": db_user.PERFIL})
    return db_user

@router.post("/forgot-password")
async def forgot_password(user: UserForgotPassword, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.EMAIL == user.EMAIL, User.ATIVO ==  'S').first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    
    token = generate_reset_token()
    db_user.RESET_PASSWORD_TOKEN = token
    db_user.RESET_TOKEN_EXPIRA = datetime.utcnow() + timedelta(hours=1)
    db.commit()

    email_service = EmailService()

    await email_service.send_template_email(
        # to_email="adriano@rosset.com.br",
        to_email=user.EMAIL,
        subject="Redefinição de Senha",
        template_name="reset_password.txt",
        context={"token": token}
    )

    return {"message": "E-mail de redefinição enviado"}

@router.post("/reset-password")
async def reset_password(data: UserResetPassword, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    db_user = db.query(User).filter(User.RESET_PASSWORD_TOKEN == data.TOKEN).first()

    if not db_user or db_user.RESET_TOKEN_EXPIRA < now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido ou expirado")
    
    db_user.SENHA_HASH = hash_password(data.SENHA)
    db_user.RESET_PASSWORD_TOKEN = None
    db_user.RESET_TOKEN_EXPIRA = None
    db.commit()

    return {"message": "Senha redefinida com sucesso"}