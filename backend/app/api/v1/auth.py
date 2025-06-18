from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_jwt_token, generate_reset_token
from app.models.user import User
from app.models.mfa import MFAConfig
from app.schemas.user import UserLogin, UserResetPassword, UserResponse, UserCreate, UserForgotPassword, LoginResponse
from app.schemas.mfa import MFASetupResponse, MFAVerifyRequest, MFASetupRequest, MFAVerifyResponse, MFADisableResponse
from app.services.email_service import EmailService
from datetime import datetime, timedelta
from email.message import EmailMessage
import pyotp
import qrcode
import io
import base64

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
        ATIVO='S',
        MFA_ATIVO='N',
        PRIMEIRO_ACESSO='S'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=LoginResponse)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.EMAIL == user.EMAIL, User.ATIVO == 'S').first()
    
    if not db_user or not verify_password(user.SENHA, db_user.SENHA_HASH):
        db_user.TENTATIVAS_LOGIN += 1
        if db_user.TENTATIVAS_LOGIN >= 5:
            db_user.BLOQUEADO_ATE = datetime.utcnow() + timedelta(minutes=30)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    
    if db_user.BLOQUEADO_ATE and db_user.BLOQUEADO_ATE > datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário bloqueado")    

    db_user.DATA_ULTIMO_LOGIN = datetime.utcnow()
    db_user.TENTATIVAS_LOGIN = 0
    db.commit()

    # Verificar se MFA está configurado
    mfa_config = db.query(MFAConfig).filter(MFAConfig.ID_USUARIO == db_user.ID, MFAConfig.ATIVO == 'S').first()
    
    token = create_jwt_token({"sub": str(db_user.ID), "perfil": db_user.PERFIL})

    return {
        "token": token, 
        "user": db_user, 
        "requires_mfa": bool(mfa_config),
        "user_id": db_user.ID
    }

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
        to_email="adriano@rosset.com.br",
        # to_email=user.EMAIL,
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


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(data: MFASetupRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.ID == data.user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    
    # Gerar segredo TOTP
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=db_user.EMAIL, issuer_name="Haras System")
    
    # Gerar QR code
    qr = qrcode.QRCode()
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, "PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    qr_code_url = f"data:image/png;base64,{qr_code_base64}"
    
    # Salvar segredo no banco
    mfa_config = db.query(MFAConfig).filter(MFAConfig.ID_USUARIO == data.user_id).first()
    if mfa_config:
        mfa_config.SEGREDO_TOTP = secret
        mfa_config.DATA_CADASTRO = func.now()
        mfa_config.ATIVO = 'S'
    else:
        mfa_config = MFAConfig(ID_USUARIO=data.user_id, SEGREDO_TOTP=secret, ATIVO='S')
        db.add(mfa_config)

    db_user.MFA_ATIVO = 'S'    
    db_user.PRIMEIRO_ACESSO = 'N'
    db.commit()
    
    return {"secret": secret, "qr_code_url": qr_code_url, "user": db_user}

@router.post("/mfa/verify", response_model=MFAVerifyResponse)
async def verify_mfa(data: MFAVerifyRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.ID == data.user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    
    mfa_config = db.query(MFAConfig).filter(MFAConfig.ID_USUARIO == data.user_id, MFAConfig.ATIVO == 'S').first()
    if not mfa_config:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA não configurado")
    
    totp = pyotp.TOTP(mfa_config.SEGREDO_TOTP)

    if not totp.verify(data.code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código TOTP inválido")
    
    db_user.DATA_ULTIMO_LOGIN = datetime.utcnow()
    db_user.TENTATIVAS_LOGIN = 0
    db.commit()
    
    token = create_jwt_token({"sub": str(db_user.ID), "perfil": db_user.PERFIL})

    return {"token": token, "user": db_user}

@router.post("/mfa/disable", response_model=MFADisableResponse)
async def disable_mfa(data: MFASetupRequest, db: Session = Depends(get_db)):
    user_id = data.user_id
    db_user = db.query(User).filter(User.ID == user_id, User.ATIVO == 'S').first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    
    mfa_config = db.query(MFAConfig).filter(MFAConfig.ID_USUARIO == user_id).first()
    if not mfa_config:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA não configurado")
    
    mfa_config.ATIVO = 'N'
    db_user.MFA_ATIVO = 'N'
    db.commit()
    
    return {"user": db_user}    