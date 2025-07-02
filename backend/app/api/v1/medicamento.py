from datetime import datetime, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.animal import Animal
from app.models.medicamento import Medicamento, MovimentacaoMedicamento
from app.models.saude import SaudeAnimais
from app.models.user import User
from app.schemas.medicamento import (
    AplicacaoMedicamento,
    ConsumoPorAnimal,
    EntradaEstoque,
    EstoqueMedicamentoBaixo,
    FormaFarmaceuticaEnum,
    MedicamentoCreate,
    MedicamentoResponse,
    MedicamentoUpdate,
    MovimentacaoEstoque,
    MovimentacaoMedicamentoResponse,
    PrevisaoMedicamentoConsumo,
    StatusEstoqueEnum,
    TipoMovimentacaoEnum,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import desc, func

router = APIRouter(prefix="/api/medicamentos", tags=["Medicamentos"])

# === MEDICAMENTOS ===


@router.post(
    "/", response_model=MedicamentoResponse, status_code=status.HTTP_201_CREATED
)
async def create_medicamento(
    medicamento: MedicamentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verificar duplicatas
    existing = (
        db.query(Medicamento)
        .filter(Medicamento.NOME == medicamento.NOME, Medicamento.ATIVO == "S")
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medicamento com este nome já existe",
        )

    db_medicamento = Medicamento(**medicamento.dict())
    db.add(db_medicamento)
    db.commit()
    db.refresh(db_medicamento)

    return await _enrich_medicamento_response(db_medicamento, db)


@router.get("/", response_model=dict)
async def list_medicamentos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    forma_farmaceutica: Optional[FormaFarmaceuticaEnum] = Query(None),
    estoque_baixo: Optional[bool] = Query(False, description="Apenas estoque baixo"),
    vencimento: Optional[int] = Query(None, description="Dias para vencimento"),
    ativo: Optional[str] = Query("S", description="Filtrar por status"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    query = db.query(Medicamento)

    if nome:
        query = query.filter(Medicamento.NOME.ilike(f"%{nome}%"))
    if forma_farmaceutica:
        query = query.filter(Medicamento.FORMA_FARMACEUTICA == forma_farmaceutica)
    if ativo:
        query = query.filter(Medicamento.ATIVO == ativo)
    if estoque_baixo:
        query = query.filter(Medicamento.ESTOQUE_ATUAL <= Medicamento.ESTOQUE_MINIMO)
    if vencimento:
        data_limite = datetime.now() + timedelta(days=vencimento)
        query = query.filter(Medicamento.DATA_VALIDADE <= data_limite)

    total = query.count()
    offset = (page - 1) * limit
    medicamentos = query.order_by(Medicamento.NOME).offset(offset).limit(limit).all()

    # Enriquecer com dados calculados
    enriched_medicamentos = []
    for med in medicamentos:
        enriched = await _enrich_medicamento_response(med, db)
        enriched_medicamentos.append(enriched)

    return {
        "medicamentos": enriched_medicamentos,
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/{id}", response_model=MedicamentoResponse)
async def get_medicamento(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    medicamento = db.query(Medicamento).filter(Medicamento.ID == id).first()
    if not medicamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medicamento não encontrado"
        )

    return await _enrich_medicamento_response(medicamento, db)


@router.put("/{id}", response_model=MedicamentoResponse)
async def update_medicamento(
    id: int,
    medicamento: MedicamentoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_medicamento = db.query(Medicamento).filter(Medicamento.ID == id).first()
    if not db_medicamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medicamento não encontrado"
        )

    for key, value in medicamento.dict(exclude_unset=True).items():
        setattr(db_medicamento, key, value)

    db.commit()
    db.refresh(db_medicamento)
    return await _enrich_medicamento_response(db_medicamento, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medicamento(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_medicamento = db.query(Medicamento).filter(Medicamento.ID == id).first()
    if not db_medicamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medicamento não encontrado"
        )

    # Verificar se há movimentações
    movimentacoes = (
        db.query(MovimentacaoMedicamento)
        .filter(MovimentacaoMedicamento.ID_MEDICAMENTO == id)
        .first()
    )

    if movimentacoes:
        # Soft delete
        db_medicamento.ATIVO = "N"
    else:
        # Hard delete
        db.delete(db_medicamento)

    db.commit()


# === MOVIMENTAÇÕES ===


@router.post("/entrada-estoque", response_model=dict)
async def entrada_estoque(
    entrada: EntradaEstoque,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verificar se medicamento existe
    medicamento = (
        db.query(Medicamento).filter(Medicamento.ID == entrada.ID_MEDICAMENTO).first()
    )
    if not medicamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medicamento não encontrado"
        )

    # Criar movimentação de entrada
    movimentacao = MovimentacaoMedicamento(
        ID_MEDICAMENTO=entrada.ID_MEDICAMENTO,
        TIPO_MOVIMENTACAO=TipoMovimentacaoEnum.ENTRADA,
        QUANTIDADE=entrada.QUANTIDADE,
        NOTA_FISCAL=entrada.NOTA_FISCAL,
        FORNECEDOR=entrada.FORNECEDOR,
        PRECO_UNITARIO=entrada.PRECO_UNITARIO,
        LOTE=entrada.LOTE,
        DATA_VALIDADE=entrada.DATA_VALIDADE,
        MOTIVO="Entrada de estoque",
        OBSERVACOES=entrada.OBSERVACOES,
        ID_USUARIO_REGISTRO=current_user.ID,
    )

    db.add(movimentacao)
    db.commit()
    db.refresh(movimentacao)

    return {
        "message": "Entrada registrada com sucesso",
        "movimentacao_id": movimentacao.ID,
        "estoque_atual": movimentacao.QUANTIDADE_ATUAL,
    }


@router.post("/aplicar-medicamento", response_model=dict)
async def aplicar_medicamento(
    aplicacao: AplicacaoMedicamento,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verificar medicamento e animal
    medicamento = (
        db.query(Medicamento).filter(Medicamento.ID == aplicacao.ID_MEDICAMENTO).first()
    )
    if not medicamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medicamento não encontrado"
        )

    animal = db.query(Animal).filter(Animal.ID == aplicacao.ID_ANIMAL).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    # Verificar estoque
    if medicamento.ESTOQUE_ATUAL < aplicacao.QUANTIDADE_APLICADA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente. Disponível: {medicamento.ESTOQUE_ATUAL} {medicamento.UNIDADE_MEDIDA}",
        )

    custo = (
        medicamento.PRECO_UNITARIO * aplicacao.QUANTIDADE_APLICADA
        if medicamento.PRECO_UNITARIO
        else 0
    )

    # Criar registro de saúde
    saude = SaudeAnimais(
        ID_ANIMAL=aplicacao.ID_ANIMAL,
        TIPO_REGISTRO="MEDICAMENTO",
        DATA_OCORRENCIA=datetime.now(),
        DESCRICAO=f"Aplicação de {medicamento.NOME}",
        VETERINARIO_RESPONSAVEL=aplicacao.VETERINARIO_RESPONSAVEL,
        MEDICAMENTO_APLICADO=medicamento.NOME,
        DOSE_APLICADA=f"{aplicacao.QUANTIDADE_APLICADA} {medicamento.UNIDADE_MEDIDA}",
        CUSTO=custo,
        OBSERVACOES=aplicacao.OBSERVACOES,
        DATA_REGISTRO=datetime.now(),
        ID_MEDICAMENTO=aplicacao.ID_MEDICAMENTO,
        QUANTIDADE_APLICADA=aplicacao.QUANTIDADE_APLICADA,
        UNIDADE_APLICADA=medicamento.UNIDADE_MEDIDA,
        ID_USUARIO_REGISTRO=current_user.ID,
    )

    db.add(saude)
    # db.flush()  # Para obter o ID

    # Movimentação será criada automaticamente pelo trigger
    # Mas vamos criar manualmente para ter controle total
    # movimentacao = MovimentacaoMedicamento(
    #     ID_MEDICAMENTO=aplicacao.ID_MEDICAMENTO,
    #     TIPO_MOVIMENTACAO=TipoMovimentacaoEnum.SAIDA,
    #     QUANTIDADE=aplicacao.QUANTIDADE_APLICADA,
    #     ID_ANIMAL=aplicacao.ID_ANIMAL,
    #     ID_SAUDE_ANIMAL=saude.ID,
    #     MOTIVO=f"Aplicação em {animal.NOME}",
    #     OBSERVACOES=aplicacao.OBSERVACOES,
    #     ID_USUARIO_REGISTRO=current_user.ID
    # )

    # db.add(movimentacao)
    db.commit()

    return {
        "message": "Medicamento aplicado com sucesso",
        "saude_id": saude.ID,
        # "movimentacao_id": movimentacao.ID,
        # "estoque_restante": movimentacao.QUANTIDADE_ATUAL
    }


@router.get("/movimentacoes/lista", response_model=dict)
async def list_movimentacoes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    medicamento_id: Optional[int] = Query(None),
    animal_id: Optional[int] = Query(None),
    tipo: Optional[TipoMovimentacaoEnum] = Query(None),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    query = db.query(MovimentacaoMedicamento).join(Medicamento)

    if medicamento_id:
        query = query.filter(MovimentacaoMedicamento.ID_MEDICAMENTO == medicamento_id)
    if animal_id:
        query = query.filter(MovimentacaoMedicamento.ID_ANIMAL == animal_id)
    if tipo:
        query = query.filter(MovimentacaoMedicamento.TIPO_MOVIMENTACAO == tipo)
    if data_inicio:
        query = query.filter(
            MovimentacaoMedicamento.DATA_REGISTRO >= datetime.fromisoformat(data_inicio)
        )
    if data_fim:
        query = query.filter(
            MovimentacaoMedicamento.DATA_REGISTRO <= datetime.fromisoformat(data_fim)
        )

    total = query.count()
    offset = (page - 1) * limit
    movimentacoes = (
        query.order_by(desc(MovimentacaoMedicamento.DATA_REGISTRO))
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


# === RELATÓRIOS ===


@router.get("/relatorio/estoque-baixo", response_model=List[EstoqueMedicamentoBaixo])
async def get_estoque_baixo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    dias_vencimento: int = Query(
        30, description="Dias para considerar próximo ao vencimento"
    ),
):
    data_limite = datetime.now() + timedelta(days=dias_vencimento)

    medicamentos = (
        db.query(Medicamento)
        .filter(Medicamento.ATIVO == "S")
        .filter(
            (Medicamento.ESTOQUE_ATUAL <= Medicamento.ESTOQUE_MINIMO)
            | (Medicamento.DATA_VALIDADE <= data_limite)
        )
        .all()
    )

    resultado = []
    for med in medicamentos:
        # Determinar status
        if med.DATA_VALIDADE and med.DATA_VALIDADE <= datetime.now():
            status = StatusEstoqueEnum.VENCIDO
            dias = (datetime.now() - med.DATA_VALIDADE).days
        elif med.DATA_VALIDADE and med.DATA_VALIDADE <= data_limite:
            status = StatusEstoqueEnum.VENCENDO
            dias = (med.DATA_VALIDADE - datetime.now()).days
        elif med.ESTOQUE_ATUAL <= med.ESTOQUE_MINIMO:
            status = StatusEstoqueEnum.ESTOQUE_BAIXO
            dias = None
        else:
            status = StatusEstoqueEnum.OK
            dias = None

        resultado.append(
            EstoqueMedicamentoBaixo(
                medicamento_id=med.ID,
                nome=med.NOME,
                estoque_atual=med.ESTOQUE_ATUAL,
                estoque_minimo=med.ESTOQUE_MINIMO,
                unidade_medida=med.UNIDADE_MEDIDA,
                status_alerta=status,
                dias_vencimento=dias,
            )
        )

    return resultado


@router.get(
    "/relatorio/consumo-animal/{animal_id}", response_model=List[ConsumoPorAnimal]
)
async def get_consumo_por_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
):
    # Verificar se animal existe
    animal = db.query(Animal).filter(Animal.ID == animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    query = (
        db.query(
            MovimentacaoMedicamento.ID_MEDICAMENTO,
            Medicamento.NOME.label("medicamento_nome"),
            Medicamento.UNIDADE_MEDIDA,
            func.sum(MovimentacaoMedicamento.QUANTIDADE).label("total_aplicado"),
            func.count(MovimentacaoMedicamento.ID).label("numero_aplicacoes"),
            func.max(MovimentacaoMedicamento.DATA_REGISTRO).label("ultima_aplicacao"),
            func.sum(
                MovimentacaoMedicamento.PRECO_UNITARIO
                * MovimentacaoMedicamento.QUANTIDADE
            ).label("custo_total"),
        )
        .join(Medicamento)
        .filter(
            MovimentacaoMedicamento.ID_ANIMAL == animal_id,
            MovimentacaoMedicamento.TIPO_MOVIMENTACAO == TipoMovimentacaoEnum.SAIDA,
        )
    )

    if data_inicio:
        query = query.filter(
            MovimentacaoMedicamento.DATA_REGISTRO >= datetime.fromisoformat(data_inicio)
        )
    if data_fim:
        query = query.filter(
            MovimentacaoMedicamento.DATA_REGISTRO <= datetime.fromisoformat(data_fim)
        )

    resultados = query.group_by(
        MovimentacaoMedicamento.ID_MEDICAMENTO,
        Medicamento.NOME,
        Medicamento.UNIDADE_MEDIDA,
    ).all()

    consumos = []
    for resultado in resultados:
        consumos.append(
            ConsumoPorAnimal(
                animal_id=animal_id,
                animal_nome=animal.NOME,
                medicamento_nome=resultado.medicamento_nome,
                total_aplicado=float(resultado.total_aplicado),
                unidade_medida=resultado.UNIDADE_MEDIDA,
                numero_aplicacoes=resultado.numero_aplicacoes,
                ultima_aplicacao=resultado.ultima_aplicacao,
                custo_total=(
                    float(resultado.custo_total) if resultado.custo_total else None
                ),
            )
        )

    return consumos


@router.get(
    "/relatorio/previsao-consumo", response_model=List[PrevisaoMedicamentoConsumo]
)
async def get_previsao_consumo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    dias_analise: int = Query(90, description="Dias para calcular média de consumo"),
):
    data_inicio = datetime.now() - timedelta(days=dias_analise)

    # Calcular consumo médio mensal
    consumos = (
        db.query(
            MovimentacaoMedicamento.ID_MEDICAMENTO,
            Medicamento.NOME.label("medicamento_nome"),
            Medicamento.ESTOQUE_ATUAL,
            func.sum(MovimentacaoMedicamento.QUANTIDADE).label("total_consumo"),
        )
        .join(Medicamento)
        .filter(
            MovimentacaoMedicamento.TIPO_MOVIMENTACAO == TipoMovimentacaoEnum.SAIDA,
            MovimentacaoMedicamento.DATA_REGISTRO >= data_inicio,
            Medicamento.ATIVO == "S",
        )
        .group_by(
            MovimentacaoMedicamento.ID_MEDICAMENTO,
            Medicamento.NOME,
            Medicamento.ESTOQUE_ATUAL,
        )
        .all()
    )

    previsoes = []
    for consumo in consumos:
        # Calcular consumo mensal médio
        meses = dias_analise / 30
        consumo_mensal = float(consumo.total_consumo) / meses if meses > 0 else 0

        # Calcular dias restantes
        if consumo_mensal > 0:
            dias_restantes = int((consumo.ESTOQUE_ATUAL / consumo_mensal) * 30)
            data_prevista = datetime.now() + timedelta(days=dias_restantes)

            # Determinar recomendação
            if dias_restantes <= 7:
                recomendacao = "COMPRAR_URGENTE"
            elif dias_restantes <= 30:
                recomendacao = "COMPRAR_BREVE"
            else:
                recomendacao = "OK"
        else:
            dias_restantes = 999
            data_prevista = datetime.now() + timedelta(days=999)
            recomendacao = "SEM_CONSUMO"

        previsoes.append(
            PrevisaoMedicamentoConsumo(
                medicamento_id=consumo.ID_MEDICAMENTO,
                medicamento_nome=consumo.medicamento_nome,
                consumo_mensal_medio=round(consumo_mensal, 2),
                estoque_atual=consumo.ESTOQUE_ATUAL,
                dias_restantes=dias_restantes,
                data_prevista_fim=data_prevista,
                recomendacao=recomendacao,
            )
        )

    # Ordenar por urgência
    previsoes.sort(key=lambda x: x.dias_restantes)
    return previsoes


@router.get("/relatorio/movimentacao-periodo", response_model=List[MovimentacaoEstoque])
async def get_movimentacao_periodo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
):
    query = db.query(
        MovimentacaoMedicamento.ID_MEDICAMENTO,
        Medicamento.NOME.label("medicamento_nome"),
        func.sum(
            func.case(
                (
                    MovimentacaoMedicamento.TIPO_MOVIMENTACAO
                    == TipoMovimentacaoEnum.ENTRADA,
                    MovimentacaoMedicamento.QUANTIDADE,
                ),
                else_=0,
            )
        ).label("total_entradas"),
        func.sum(
            func.case(
                (
                    MovimentacaoMedicamento.TIPO_MOVIMENTACAO
                    == TipoMovimentacaoEnum.SAIDA,
                    MovimentacaoMedicamento.QUANTIDADE,
                ),
                else_=0,
            )
        ).label("total_saidas"),
        Medicamento.ESTOQUE_ATUAL.label("saldo_atual"),
        func.sum(
            MovimentacaoMedicamento.PRECO_UNITARIO * MovimentacaoMedicamento.QUANTIDADE
        ).label("valor_total"),
        func.max(MovimentacaoMedicamento.DATA_REGISTRO).label("ultima_movimentacao"),
    ).join(Medicamento)

    if data_inicio:
        query = query.filter(
            MovimentacaoMedicamento.DATA_REGISTRO >= datetime.fromisoformat(data_inicio)
        )
    if data_fim:
        query = query.filter(
            MovimentacaoMedicamento.DATA_REGISTRO <= datetime.fromisoformat(data_fim)
        )

    resultados = query.group_by(
        MovimentacaoMedicamento.ID_MEDICAMENTO,
        Medicamento.NOME,
        Medicamento.ESTOQUE_ATUAL,
    ).all()

    movimentacoes = []
    for resultado in resultados:
        movimentacoes.append(
            MovimentacaoEstoque(
                medicamento_id=resultado.ID_MEDICAMENTO,
                medicamento_nome=resultado.medicamento_nome,
                total_entradas=float(resultado.total_entradas),
                total_saidas=float(resultado.total_saidas),
                saldo_atual=resultado.saldo_atual,
                valor_total=(
                    float(resultado.valor_total) if resultado.valor_total else 0
                ),
                ultima_movimentacao=resultado.ultima_movimentacao,
            )
        )

    return movimentacoes


# === OPÇÕES PARA SELECTS ===


@router.get("/options/formas-farmaceuticas")
async def get_formas_farmaceuticas(current_user: User = Depends(get_current_user)):
    return [
        {"value": "INJETAVEL", "label": "Injetável"},
        {"value": "ORAL", "label": "Oral"},
        {"value": "TOPICO", "label": "Tópico"},
    ]


@router.get("/options/unidades-medida")
async def get_unidades_medida(current_user: User = Depends(get_current_user)):
    return [
        {"value": "ML", "label": "Mililitros (ml)"},
        {"value": "G", "label": "Gramas (g)"},
        {"value": "COMPRIMIDO", "label": "Comprimidos"},
        {"value": "DOSE", "label": "Doses"},
        {"value": "AMPOLA", "label": "Ampolas"},
        {"value": "FRASCO", "label": "Frascos"},
    ]


@router.get("/autocomplete", response_model=List[dict])
async def autocomplete_medicamentos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    termo: str = Query(..., description="Termo para busca"),
    limit: int = Query(10, ge=1, le=50),
):
    """Autocomplete para medicamentos com estoque > 0"""
    medicamentos = (
        db.query(Medicamento)
        .filter(
            Medicamento.NOME.ilike(f"%{termo}%"),
            Medicamento.ATIVO == "S",
            Medicamento.ESTOQUE_ATUAL > 0,
        )
        .order_by(Medicamento.NOME)
        .limit(limit)
        .all()
    )

    return [
        {
            "value": med.ID,
            "label": f"{med.NOME} ({med.ESTOQUE_ATUAL} {med.UNIDADE_MEDIDA})",
            "estoque": med.ESTOQUE_ATUAL,
            "unidade": med.UNIDADE_MEDIDA,
            "forma": med.FORMA_FARMACEUTICA,
            "carencia": med.PERIODO_CARENCIA,
        }
        for med in medicamentos
    ]


# === FUNÇÕES AUXILIARES ===


async def _enrich_medicamento_response(
    medicamento: Medicamento, db: Session
) -> MedicamentoResponse:
    """Enriquece resposta do medicamento com dados calculados"""
    response_data = MedicamentoResponse.from_orm(medicamento)

    # Calcular status do estoque
    hoje = datetime.now()

    if medicamento.DATA_VALIDADE and medicamento.DATA_VALIDADE <= hoje:
        response_data.status_estoque = StatusEstoqueEnum.VENCIDO
        response_data.dias_vencimento = (hoje - medicamento.DATA_VALIDADE).days
    elif medicamento.DATA_VALIDADE and medicamento.DATA_VALIDADE <= hoje + timedelta(
        days=30
    ):
        response_data.status_estoque = StatusEstoqueEnum.VENCENDO
        response_data.dias_vencimento = (medicamento.DATA_VALIDADE - hoje).days
    elif medicamento.ESTOQUE_ATUAL <= medicamento.ESTOQUE_MINIMO:
        response_data.status_estoque = StatusEstoqueEnum.ESTOQUE_BAIXO
    else:
        response_data.status_estoque = StatusEstoqueEnum.OK

    # Calcular valor do estoque
    if medicamento.PRECO_UNITARIO:
        response_data.valor_estoque = (
            medicamento.ESTOQUE_ATUAL * medicamento.PRECO_UNITARIO
        )

    return response_data


async def _enrich_movimentacao_response(
    movimentacao: MovimentacaoMedicamento, db: Session
) -> MovimentacaoMedicamentoResponse:
    """Enriquece resposta da movimentação com dados relacionados"""
    medicamento = (
        db.query(Medicamento)
        .filter(Medicamento.ID == movimentacao.ID_MEDICAMENTO)
        .first()
    )
    animal = None
    if movimentacao.ID_ANIMAL:
        animal = db.query(Animal).filter(Animal.ID == movimentacao.ID_ANIMAL).first()

    response_data = MovimentacaoMedicamentoResponse.from_orm(movimentacao)
    response_data.medicamento_nome = medicamento.NOME if medicamento else None
    response_data.animal_nome = animal.NOME if animal else None

    return response_data
