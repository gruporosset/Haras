from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from sqlalchemy import desc, asc
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.crescimento import HistoricoCrescimento
from app.models.saude import SaudeAnimais
from app.models.animal import Animal
from app.models.user import User
from app.schemas.crescimento import (
    CrescimentoCreate, CrescimentoUpdate, CrescimentoResponse,
    SaudeCreate, SaudeUpdate, SaudeResponse, TipoRegistroEnum,
    EstatisticasCrescimento, ProximasAplicacoes
)
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/crescimento-saude",
                   tags=["Crescimento e Saúde"])

# === ENDPOINTS CRESCIMENTO ===


@router.post("/crescimento", response_model=CrescimentoResponse, status_code=status.HTTP_201_CREATED)
async def create_crescimento(
    crescimento: CrescimentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar se animal existe
    animal = db.query(Animal).filter(
        Animal.ID == crescimento.ID_ANIMAL).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado")

    db_crescimento = HistoricoCrescimento(**crescimento.dict())
    db.add(db_crescimento)

    # Atualizar peso atual do animal se informado
    if crescimento.PESO:
        animal.PESO_ATUAL = crescimento.PESO

    db.commit()
    db.refresh(db_crescimento)
    return db_crescimento


@router.get("/crescimento", response_model=dict)
async def list_crescimento(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    animal_id: Optional[int] = Query(None, description="Filtrar por animal"),
    data_inicio: Optional[str] = Query(
        None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    query = db.query(HistoricoCrescimento).join(Animal)

    if animal_id:
        query = query.filter(HistoricoCrescimento.ID_ANIMAL == animal_id)
    if data_inicio:
        query = query.filter(HistoricoCrescimento.DATA_MEDICAO >=
                             datetime.fromisoformat(data_inicio))
    if data_fim:
        query = query.filter(HistoricoCrescimento.DATA_MEDICAO <=
                             datetime.fromisoformat(data_fim))

    total = query.count()
    offset = (page - 1) * limit
    registros = query.order_by(desc(HistoricoCrescimento.DATA_MEDICAO)).offset(
        offset).limit(limit).all()

    return {
        "registros": [CrescimentoResponse.from_orm(r) for r in registros],
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/crescimento/{id}", response_model=CrescimentoResponse)
async def get_crescimento(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    registro = db.query(HistoricoCrescimento).filter(
        HistoricoCrescimento.ID == id).first()
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Registro não encontrado")
    return registro


@router.put("/crescimento/{id}", response_model=CrescimentoResponse)
async def update_crescimento(
    id: int,
    crescimento: CrescimentoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_crescimento = db.query(HistoricoCrescimento).filter(
        HistoricoCrescimento.ID == id).first()
    if not db_crescimento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Registro não encontrado")

    for key, value in crescimento.dict(exclude_unset=True).items():
        setattr(db_crescimento, key, value)

    # Atualizar peso atual do animal se for o registro mais recente
    if crescimento.PESO:
        latest = db.query(HistoricoCrescimento)\
            .filter(HistoricoCrescimento.ID_ANIMAL == db_crescimento.ID_ANIMAL)\
            .order_by(desc(HistoricoCrescimento.DATA_MEDICAO))\
            .first()

        if latest and latest.ID == id:
            animal = db.query(Animal).filter(
                Animal.ID == db_crescimento.ID_ANIMAL).first()
            if animal:
                animal.PESO_ATUAL = crescimento.PESO

    db.commit()
    db.refresh(db_crescimento)
    return db_crescimento


@router.delete("/crescimento/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crescimento(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_crescimento = db.query(HistoricoCrescimento).filter(
        HistoricoCrescimento.ID == id).first()
    if not db_crescimento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Registro não encontrado")

    db.delete(db_crescimento)
    db.commit()

# === ENDPOINTS SAÚDE ===


@router.post("/saude", response_model=SaudeResponse, status_code=status.HTTP_201_CREATED)
async def create_saude(
    saude: SaudeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar se animal existe
    animal = db.query(Animal).filter(Animal.ID == saude.ID_ANIMAL).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado")

    # Se especificou medicamento, fazer validações
    if saude.ID_MEDICAMENTO and saude.QUANTIDADE_APLICADA:
        from app.models.medicamento import Medicamento, MovimentacaoMedicamento

        medicamento = db.query(Medicamento).filter(
            Medicamento.ID == saude.ID_MEDICAMENTO).first()
        if not medicamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Medicamento não encontrado")

        # Verificar se medicamento está ativo
        if medicamento.ATIVO != 'S':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Medicamento não está ativo"
            )

        # Verificar estoque suficiente
        if medicamento.ESTOQUE_ATUAL < saude.QUANTIDADE_APLICADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente. Disponível: {medicamento.ESTOQUE_ATUAL} {medicamento.UNIDADE_MEDIDA}"
            )

        # Preencher campos automáticos baseados no medicamento
        if not saude.MEDICAMENTO_APLICADO:
            saude.MEDICAMENTO_APLICADO = medicamento.NOME
        if not saude.DOSE_APLICADA:
            saude.DOSE_APLICADA = f"{saude.QUANTIDADE_APLICADA} {medicamento.UNIDADE_MEDIDA}"
        if not saude.UNIDADE_APLICADA:
            saude.UNIDADE_APLICADA = medicamento.UNIDADE_MEDIDA

        # Definir tipo de registro como MEDICAMENTO se não foi especificado
        if not saude.TIPO_REGISTRO and saude.ID_MEDICAMENTO:
            saude.TIPO_REGISTRO = TipoRegistroEnum.MEDICAMENTO

    # Criar registro de saúde
    db_saude = SaudeAnimais(**saude.dict())
    db.add(db_saude)
    db.flush()  # Para obter o ID antes do commit

    # Se tem medicamento, criar movimentação de estoque
    if saude.ID_MEDICAMENTO and saude.QUANTIDADE_APLICADA:
        from app.models.medicamento import MovimentacaoMedicamento, TipoMovimentacaoEnum

        movimentacao = MovimentacaoMedicamento(
            ID_MEDICAMENTO=saude.ID_MEDICAMENTO,
            TIPO_MOVIMENTACAO=TipoMovimentacaoEnum.SAIDA,
            QUANTIDADE=saude.QUANTIDADE_APLICADA,
            ID_ANIMAL=saude.ID_ANIMAL,
            ID_SAUDE_ANIMAL=db_saude.ID,
            MOTIVO=f"Aplicação em {animal.NOME} - {saude.TIPO_REGISTRO}",
            OBSERVACOES=saude.OBSERVACOES,
            ID_USUARIO_REGISTRO=current_user.ID
        )

        db.add(movimentacao)

    db.commit()
    db.refresh(db_saude)

    return await _enrich_saude_response(db_saude, db)


@router.get("/saude", response_model=dict)
async def list_saude(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    animal_id: Optional[int] = Query(None, description="Filtrar por animal"),
    tipo_registro: Optional[TipoRegistroEnum] = Query(
        None, description="Filtrar por tipo"),
    data_inicio: Optional[str] = Query(
        None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    query = db.query(SaudeAnimais).join(Animal)

    if animal_id:
        query = query.filter(SaudeAnimais.ID_ANIMAL == animal_id)
    if tipo_registro:
        query = query.filter(SaudeAnimais.TIPO_REGISTRO == tipo_registro)
    if data_inicio:
        query = query.filter(SaudeAnimais.DATA_OCORRENCIA >=
                             datetime.fromisoformat(data_inicio))
    if data_fim:
        query = query.filter(SaudeAnimais.DATA_OCORRENCIA <=
                             datetime.fromisoformat(data_fim))

    total = query.count()
    offset = (page - 1) * limit
    registros = query.order_by(desc(SaudeAnimais.DATA_OCORRENCIA)).offset(
        offset).limit(limit).all()

    return {
        "registros": [SaudeResponse.from_orm(r) for r in registros],
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/saude/{id}", response_model=SaudeResponse)
async def get_saude(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    registro = db.query(SaudeAnimais).filter(SaudeAnimais.ID == id).first()
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Registro não encontrado")
    return registro


@router.put("/saude/{id}", response_model=SaudeResponse)
async def update_saude(
    id: int,
    saude: SaudeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_saude = db.query(SaudeAnimais).filter(SaudeAnimais.ID == id).first()
    if not db_saude:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Registro não encontrado")

    # Verificar se está alterando medicamento
    medicamento_alterado = False
    if (hasattr(saude, 'ID_MEDICAMENTO') and saude.ID_MEDICAMENTO != db_saude.ID_MEDICAMENTO) or \
       (hasattr(saude, 'QUANTIDADE_APLICADA') and saude.QUANTIDADE_APLICADA != db_saude.QUANTIDADE_APLICADA):
        medicamento_alterado = True

    # Se alterou medicamento, precisamos reverter a movimentação anterior e criar nova
    if medicamento_alterado and db_saude.ID_MEDICAMENTO:
        from app.models.medicamento import MovimentacaoMedicamento, TipoMovimentacaoEnum

        # Reverter movimentação anterior (criar entrada para compensar)
        if db_saude.QUANTIDADE_APLICADA:
            reversao = MovimentacaoMedicamento(
                ID_MEDICAMENTO=db_saude.ID_MEDICAMENTO,
                TIPO_MOVIMENTACAO=TipoMovimentacaoEnum.ENTRADA,
                QUANTIDADE=db_saude.QUANTIDADE_APLICADA,
                ID_ANIMAL=db_saude.ID_ANIMAL,
                ID_SAUDE_ANIMAL=db_saude.ID,
                MOTIVO=f"Reversão por alteração de registro - {db_saude.TIPO_REGISTRO}",
                OBSERVACOES="Estorno automático por edição",
                ID_USUARIO_REGISTRO=current_user.ID
            )
            db.add(reversao)

    # Atualizar campos
    for key, value in saude.dict(exclude_unset=True).items():
        setattr(db_saude, key, value)

    # Se tem novo medicamento, criar nova movimentação
    if db_saude.ID_MEDICAMENTO and db_saude.QUANTIDADE_APLICADA:
        from app.models.medicamento import Medicamento, MovimentacaoMedicamento, TipoMovimentacaoEnum

        medicamento = db.query(Medicamento).filter(
            Medicamento.ID == db_saude.ID_MEDICAMENTO).first()
        if medicamento:
            # Verificar estoque
            if medicamento.ESTOQUE_ATUAL < db_saude.QUANTIDADE_APLICADA:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente. Disponível: {medicamento.ESTOQUE_ATUAL} {medicamento.UNIDADE_MEDIDA}"
                )

            # Criar nova movimentação
            nova_movimentacao = MovimentacaoMedicamento(
                ID_MEDICAMENTO=db_saude.ID_MEDICAMENTO,
                TIPO_MOVIMENTACAO=TipoMovimentacaoEnum.SAIDA,
                QUANTIDADE=db_saude.QUANTIDADE_APLICADA,
                ID_ANIMAL=db_saude.ID_ANIMAL,
                ID_SAUDE_ANIMAL=db_saude.ID,
                MOTIVO=f"Aplicação atualizada em {db_saude.ID_ANIMAL} - {db_saude.TIPO_REGISTRO}",
                OBSERVACOES=db_saude.OBSERVACOES,
                ID_USUARIO_REGISTRO=current_user.ID
            )
            db.add(nova_movimentacao)

    db.commit()
    db.refresh(db_saude)
    return await _enrich_saude_response(db_saude, db)


@router.delete("/saude/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saude(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_saude = db.query(SaudeAnimais).filter(SaudeAnimais.ID == id).first()
    if not db_saude:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Registro não encontrado")

    db.delete(db_saude)
    db.commit()


@router.get("/medicamentos-autocomplete", response_model=List[dict])
async def autocomplete_medicamentos_saude(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    termo: str = Query(..., description="Termo para busca"),
    limit: int = Query(10, ge=1, le=50)
):
    """Autocomplete para medicamentos com estoque > 0 para uso em saúde"""
    from app.models.medicamento import Medicamento

    medicamentos = db.query(Medicamento).filter(
        Medicamento.NOME.ilike(f"%{termo}%"),
        Medicamento.ATIVO == 'S',
        Medicamento.ESTOQUE_ATUAL > 0
    ).order_by(Medicamento.NOME).limit(limit).all()

    return [
        {
            "value": med.ID,
            "label": f"{med.NOME} ({med.ESTOQUE_ATUAL} {med.UNIDADE_MEDIDA})",
            "nome": med.NOME,
            "estoque": med.ESTOQUE_ATUAL,
            "unidade": med.UNIDADE_MEDIDA,
            "forma": med.FORMA_FARMACEUTICA,
            "carencia": med.PERIODO_CARENCIA,
            "principio_ativo": med.PRINCIPIO_ATIVO
        }
        for med in medicamentos
    ]

# Endpoint para validar estoque antes da aplicação


@router.post("/validar-estoque-medicamento")
async def validar_estoque_medicamento(
    medicamento_id: int,
    quantidade: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Valida se há estoque suficiente para aplicação"""
    from app.models.medicamento import Medicamento

    medicamento = db.query(Medicamento).filter(
        Medicamento.ID == medicamento_id).first()
    if not medicamento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Medicamento não encontrado")

    estoque_suficiente = medicamento.ESTOQUE_ATUAL >= quantidade

    return {
        "valido": estoque_suficiente,
        "estoque_atual": medicamento.ESTOQUE_ATUAL,
        "unidade_medida": medicamento.UNIDADE_MEDIDA,
        "estoque_restante": medicamento.ESTOQUE_ATUAL - quantidade if estoque_suficiente else None,
        "erro": None if estoque_suficiente else f"Estoque insuficiente. Disponível: {medicamento.ESTOQUE_ATUAL} {medicamento.UNIDADE_MEDIDA}"
    }

# === ENDPOINTS RELATÓRIOS ===


@router.get("/proximas-aplicacoes", response_model=List[ProximasAplicacoes])
async def get_proximas_aplicacoes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    dias: int = Query(30, description="Próximos X dias")
):
    data_limite = datetime.now() + timedelta(days=dias)

    registros = db.query(SaudeAnimais, Animal.NOME)\
        .join(Animal)\
        .filter(SaudeAnimais.PROXIMA_APLICACAO.isnot(None))\
        .filter(SaudeAnimais.PROXIMA_APLICACAO <= data_limite)\
        .filter(SaudeAnimais.PROXIMA_APLICACAO >= datetime.now())\
        .order_by(SaudeAnimais.PROXIMA_APLICACAO)\
        .all()

    return [
        ProximasAplicacoes(
            animal_id=r.SaudeAnimais.ID_ANIMAL,
            animal_nome=r.NOME,
            tipo_registro=r.SaudeAnimais.TIPO_REGISTRO,
            data_aplicacao=r.SaudeAnimais.PROXIMA_APLICACAO,
            descricao=r.SaudeAnimais.DESCRICAO or "",
            dias_restantes=(r.SaudeAnimais.PROXIMA_APLICACAO -
                            datetime.now()).days
        )
        for r in registros
    ]


@router.get("/estatisticas-crescimento", response_model=List[EstatisticasCrescimento])
async def get_estatisticas_crescimento(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Subquery para primeiro e último peso
    subq_primeiro = db.query(
        HistoricoCrescimento.ID_ANIMAL,
        func.min(HistoricoCrescimento.DATA_MEDICAO).label('primeira_data')
    ).group_by(HistoricoCrescimento.ID_ANIMAL).subquery()

    subq_ultimo = db.query(
        HistoricoCrescimento.ID_ANIMAL,
        func.max(HistoricoCrescimento.DATA_MEDICAO).label('ultima_data')
    ).group_by(HistoricoCrescimento.ID_ANIMAL).subquery()

    # Query principal
    query = db.query(
        Animal.ID,
        Animal.NOME,
        func.count(HistoricoCrescimento.ID).label('total_medicoes'),
        func.avg(HistoricoCrescimento.PESO).label('media_peso')
    ).outerjoin(HistoricoCrescimento)\
        .group_by(Animal.ID, Animal.NOME)\
        .having(func.count(HistoricoCrescimento.ID) > 0)

    resultados = []
    for animal in query.all():
        # Buscar primeiro peso
        primeiro = db.query(HistoricoCrescimento.PESO)\
            .join(subq_primeiro,
                  (HistoricoCrescimento.ID_ANIMAL == subq_primeiro.c.ID_ANIMAL) &
                  (HistoricoCrescimento.DATA_MEDICAO == subq_primeiro.c.primeira_data))\
            .filter(HistoricoCrescimento.ID_ANIMAL == animal.ID)\
            .first()

        # Buscar último peso
        ultimo = db.query(HistoricoCrescimento.PESO)\
            .join(subq_ultimo,
                  (HistoricoCrescimento.ID_ANIMAL == subq_ultimo.c.ID_ANIMAL) &
                  (HistoricoCrescimento.DATA_MEDICAO == subq_ultimo.c.ultima_data))\
            .filter(HistoricoCrescimento.ID_ANIMAL == animal.ID)\
            .first()

        peso_inicial = primeiro.PESO if primeiro else None
        peso_atual = ultimo.PESO if ultimo else None
        ganho_peso = (
            peso_atual - peso_inicial) if (peso_inicial and peso_atual) else None

        resultados.append(EstatisticasCrescimento(
            animal_id=animal.ID,
            animal_nome=animal.NOME,
            total_medicoes=animal.total_medicoes,
            peso_inicial=peso_inicial,
            peso_atual=peso_atual,
            ganho_peso=ganho_peso,
            media_peso=float(animal.media_peso) if animal.media_peso else None
        ))

    return resultados

# Função auxiliar para enriquecer resposta


async def _enrich_saude_response(saude: SaudeAnimais, db: Session) -> SaudeResponse:
    animal = db.query(Animal).filter(Animal.ID == saude.ID_ANIMAL).first()
    medicamento = None
    estoque_suficiente = None

    if saude.ID_MEDICAMENTO:
        from app.models.medicamento import Medicamento
        medicamento = db.query(Medicamento).filter(
            Medicamento.ID == saude.ID_MEDICAMENTO).first()
        if medicamento and saude.QUANTIDADE_APLICADA:
            estoque_suficiente = medicamento.ESTOQUE_ATUAL >= saude.QUANTIDADE_APLICADA

    response_data = SaudeResponse.from_orm(saude)
    response_data.animal_nome = animal.NOME if animal else None
    response_data.medicamento_nome = medicamento.NOME if medicamento else None
    response_data.estoque_suficiente = estoque_suficiente

    return response_data
