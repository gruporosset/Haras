# backend/app/api/v1/saude.py
from datetime import datetime, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.animal import Animal
from app.models.medicamento import (
    Medicamento,
    MovimentacaoMedicamento,
    TipoMovimentacaoEnum,
)
from app.models.saude import SaudeAnimais, TipoRegistroEnum
from app.models.user import User
from app.schemas.saude import (
    AplicacaoRapida,
    CalendarioSaude,
    ConsumoPorTipo,
    EstatisticasSaude,
    HistoricoSaude,
    MedicamentoAutocomplete,
    ProximasAplicacoes,
    SaudeCreate,
    SaudeResponse,
    SaudeUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import desc, func

router = APIRouter(prefix="/api/saude", tags=["Saúde"])


@router.post("/", response_model=SaudeResponse, status_code=status.HTTP_201_CREATED)
async def create_registro_saude(
    saude: SaudeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Criar novo registro de saúde"""
    # Verificar se animal existe
    animal = db.query(Animal).filter(Animal.ID == saude.ID_ANIMAL).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    # Se especificou medicamento do estoque, fazer validações
    if saude.ID_MEDICAMENTO and saude.QUANTIDADE_APLICADA:
        medicamento = (
            db.query(Medicamento).filter(Medicamento.ID == saude.ID_MEDICAMENTO).first()
        )
        if not medicamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medicamento não encontrado",
            )

        # Verificar se medicamento está ativo
        if medicamento.ATIVO != "S":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Medicamento não está ativo",
            )

        # Verificar estoque suficiente
        if medicamento.ESTOQUE_ATUAL < saude.QUANTIDADE_APLICADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente. Disponível: {medicamento.ESTOQUE_ATUAL} "
                f"{medicamento.UNIDADE_MEDIDA}",
            )

    # Criar registro de saúde
    db_saude = SaudeAnimais(
        ID_ANIMAL=saude.ID_ANIMAL,
        TIPO_REGISTRO=saude.TIPO_REGISTRO.value,
        DATA_OCORRENCIA=saude.DATA_OCORRENCIA,
        DESCRICAO=saude.DESCRICAO,
        VETERINARIO_RESPONSAVEL=saude.VETERINARIO_RESPONSAVEL,
        MEDICAMENTO_APLICADO=saude.MEDICAMENTO_APLICADO,
        DOSE_APLICADA=saude.DOSE_APLICADA,
        PROXIMA_APLICACAO=saude.PROXIMA_APLICACAO,
        CUSTO=saude.CUSTO,
        OBSERVACOES=saude.OBSERVACOES,
        ID_MEDICAMENTO=saude.ID_MEDICAMENTO,
        QUANTIDADE_APLICADA=saude.QUANTIDADE_APLICADA,
        UNIDADE_APLICADA=saude.UNIDADE_APLICADA,
        ID_USUARIO_REGISTRO=current_user.ID,
    )

    db.add(db_saude)
    db.flush()  # Para obter o ID

    # Se usou medicamento do estoque, fazer movimentação
    if saude.ID_MEDICAMENTO and saude.QUANTIDADE_APLICADA:
        # Atualizar estoque do medicamento
        medicamento.ESTOQUE_ATUAL -= saude.QUANTIDADE_APLICADA

        # Registrar movimentação
        movimentacao = MovimentacaoMedicamento(
            ID_MEDICAMENTO=saude.ID_MEDICAMENTO,
            TIPO_MOVIMENTACAO=TipoMovimentacaoEnum.SAIDA,
            QUANTIDADE=saude.QUANTIDADE_APLICADA,
            QUANTIDADE_ANTERIOR=medicamento.ESTOQUE_ATUAL + saude.QUANTIDADE_APLICADA,
            QUANTIDADE_ATUAL=medicamento.ESTOQUE_ATUAL,
            ID_ANIMAL=saude.ID_ANIMAL,
            ID_SAUDE_ANIMAL=db_saude.ID,
            MOTIVO=f"Aplicação de {saude.TIPO_REGISTRO.value}",
            OBSERVACOES=f"Aplicado em {animal.NOME}",
            ID_USUARIO_REGISTRO=current_user.ID,
        )
        db.add(movimentacao)

    db.commit()
    db.refresh(db_saude)

    # Preparar resposta
    response_data = SaudeResponse.model_validate(db_saude)
    response_data.animal_nome = animal.NOME
    if saude.ID_MEDICAMENTO:
        response_data.medicamento_nome = medicamento.NOME

    return response_data


@router.get("/", response_model=dict)
async def get_registros_saude(
    db: Session = Depends(get_db),
    animal_id: Optional[int] = Query(None, description="Filtrar por animal"),
    tipo_registro: Optional[TipoRegistroEnum] = Query(
        None, description="Filtrar por tipo"
    ),
    veterinario: Optional[str] = Query(None, description="Filtrar por veterinário"),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=1000),
):
    """Listar registros de saúde com paginação"""
    query = (
        db.query(SaudeAnimais, Animal.NOME)
        .join(Animal, SaudeAnimais.ID_ANIMAL == Animal.ID)
        .order_by(desc(SaudeAnimais.DATA_OCORRENCIA))
    )

    # Aplicar filtros
    if animal_id:
        query = query.filter(SaudeAnimais.ID_ANIMAL == animal_id)

    if tipo_registro:
        query = query.filter(SaudeAnimais.TIPO_REGISTRO == tipo_registro.value)

    if veterinario:
        query = query.filter(
            SaudeAnimais.VETERINARIO_RESPONSAVEL.ilike(f"%{veterinario}%")
        )

    if data_inicio:
        try:
            data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.filter(SaudeAnimais.DATA_OCORRENCIA >= data_inicio_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data inválido. Use YYYY-MM-DD",
            )

    if data_fim:
        try:
            data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")
            query = query.filter(SaudeAnimais.DATA_OCORRENCIA <= data_fim_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data inválido. Use YYYY-MM-DD",
            )

    # Contar total para paginação
    total = query.count()

    # Aplicar paginação
    offset = (page - 1) * limit
    registros = query.offset(offset).limit(limit).all()

    # Preparar resposta com nomes dos animais e medicamentos
    enriched_registros = []
    for registro, animal_nome in registros:
        response_data = SaudeResponse.model_validate(registro)
        response_data.animal_nome = animal_nome

        # Adicionar nome do medicamento se houver
        if registro.ID_MEDICAMENTO:
            medicamento = (
                db.query(Medicamento)
                .filter(Medicamento.ID == registro.ID_MEDICAMENTO)
                .first()
            )
            if medicamento:
                response_data.medicamento_nome = medicamento.NOME

        enriched_registros.append(response_data)

    # Retornar no formato esperado pelo frontend
    return {
        "registros": enriched_registros,
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/{registro_id}", response_model=SaudeResponse)
async def get_registro_saude(
    registro_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obter registro específico de saúde"""
    registro = (
        db.query(SaudeAnimais, Animal.NOME)
        .join(Animal, SaudeAnimais.ID_ANIMAL == Animal.ID)
        .filter(SaudeAnimais.ID == registro_id)
        .first()
    )

    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado"
        )

    saude_registro, animal_nome = registro
    response_data = SaudeResponse.model_validate(saude_registro)
    response_data.animal_nome = animal_nome

    # Adicionar nome do medicamento se houver
    if saude_registro.ID_MEDICAMENTO:
        medicamento = (
            db.query(Medicamento)
            .filter(Medicamento.ID == saude_registro.ID_MEDICAMENTO)
            .first()
        )
        if medicamento:
            response_data.medicamento_nome = medicamento.NOME

    return response_data


@router.put("/{registro_id}", response_model=SaudeResponse)
async def update_registro_saude(
    registro_id: int,
    dados: SaudeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualizar registro de saúde"""
    registro = db.query(SaudeAnimais).filter(SaudeAnimais.ID == registro_id).first()

    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado"
        )

    # Atualizar campos
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        if hasattr(registro, campo.upper()):
            if hasattr(valor, "value"):  # Enum
                setattr(registro, campo.upper(), valor.value)
            else:
                setattr(registro, campo.upper(), valor)

    db.commit()
    db.refresh(registro)

    # Buscar dados completos para resposta
    animal = db.query(Animal).filter(Animal.ID == registro.ID_ANIMAL).first()
    response_data = SaudeResponse.model_validate(registro)
    response_data.animal_nome = animal.NOME if animal else None

    return response_data


@router.delete("/{registro_id}")
async def delete_registro_saude(
    registro_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Excluir registro de saúde"""
    registro = db.query(SaudeAnimais).filter(SaudeAnimais.ID == registro_id).first()

    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado"
        )

    db.delete(registro)
    db.commit()

    return {"message": "Registro excluído com sucesso"}


@router.post(
    "/aplicacao-rapida",
    response_model=SaudeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def aplicacao_rapida(
    dados: AplicacaoRapida,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aplicação rápida para mobile"""
    # Verificar se animal existe
    animal = db.query(Animal).filter(Animal.ID == dados.ID_ANIMAL).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    # Validações de medicamento se informado
    medicamento = None
    if dados.ID_MEDICAMENTO:
        medicamento = (
            db.query(Medicamento).filter(Medicamento.ID == dados.ID_MEDICAMENTO).first()
        )
        if not medicamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medicamento não encontrado",
            )

        if (
            dados.QUANTIDADE_APLICADA
            and medicamento.ESTOQUE_ATUAL < dados.QUANTIDADE_APLICADA
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estoque insuficiente para aplicação",
            )

    # Criar registro
    db_registro = SaudeAnimais(
        ID_ANIMAL=dados.ID_ANIMAL,
        TIPO_REGISTRO=dados.TIPO_REGISTRO.value,
        DATA_OCORRENCIA=datetime.now(),
        DESCRICAO=f"{dados.TIPO_REGISTRO.value} - Aplicação rápida",
        MEDICAMENTO_APLICADO=dados.MEDICAMENTO_APLICADO,
        DOSE_APLICADA=dados.DOSE_APLICADA,
        CUSTO=dados.CUSTO,
        OBSERVACOES=dados.OBSERVACOES,
        ID_MEDICAMENTO=dados.ID_MEDICAMENTO,
        QUANTIDADE_APLICADA=dados.QUANTIDADE_APLICADA,
        ID_USUARIO_REGISTRO=current_user.ID,
    )

    db.add(db_registro)
    db.flush()

    # Movimentação de estoque se necessário
    if dados.ID_MEDICAMENTO and dados.QUANTIDADE_APLICADA:
        medicamento.ESTOQUE_ATUAL -= dados.QUANTIDADE_APLICADA

        movimentacao = MovimentacaoMedicamento(
            ID_MEDICAMENTO=dados.ID_MEDICAMENTO,
            TIPO_MOVIMENTACAO=TipoMovimentacaoEnum.SAIDA,
            QUANTIDADE=dados.QUANTIDADE_APLICADA,
            QUANTIDADE_ANTERIOR=medicamento.ESTOQUE_ATUAL + dados.QUANTIDADE_APLICADA,
            QUANTIDADE_ATUAL=medicamento.ESTOQUE_ATUAL,
            ID_ANIMAL=dados.ID_ANIMAL,
            ID_SAUDE_ANIMAL=db_registro.ID,
            MOTIVO="Aplicação rápida",
            ID_USUARIO_REGISTRO=current_user.ID,
        )
        db.add(movimentacao)

    db.commit()
    db.refresh(db_registro)

    response_data = SaudeResponse.model_validate(db_registro)
    response_data.animal_nome = animal.NOME
    if medicamento:
        response_data.medicamento_nome = medicamento.NOME

    return response_data


@router.get("/proximas-aplicacoes/", response_model=List[ProximasAplicacoes])
async def get_proximas_aplicacoes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    dias_antecedencia: int = Query(30, description="Dias de antecedência"),
):
    """Obter próximas aplicações programadas"""
    data_limite = datetime.now() + timedelta(days=dias_antecedencia)

    query = (
        db.query(SaudeAnimais, Animal.NOME)
        .join(Animal, SaudeAnimais.ID_ANIMAL == Animal.ID)
        .filter(
            SaudeAnimais.PROXIMA_APLICACAO.isnot(None),
            SaudeAnimais.PROXIMA_APLICACAO <= data_limite,
            SaudeAnimais.PROXIMA_APLICACAO >= datetime.now(),
        )
        .order_by(SaudeAnimais.PROXIMA_APLICACAO)
    )

    registros = query.all()

    result = []
    for registro, animal_nome in registros:
        data_proxima = registro.PROXIMA_APLICACAO.date()
        data_hoje = datetime.now().date()
        dias_vencimento = (data_proxima - data_hoje).days

        proxima = ProximasAplicacoes(
            animal_id=registro.ID_ANIMAL,
            animal_nome=animal_nome,
            tipo_registro=registro.TIPO_REGISTRO,
            proxima_aplicacao=registro.PROXIMA_APLICACAO,
            dias_vencimento=dias_vencimento,
        )
        result.append(proxima)

    return result


@router.get("/estatisticas/geral", response_model=EstatisticasSaude)
async def get_estatisticas_saude(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ano: Optional[int] = Query(None, description="Ano para estatísticas"),
    mes: Optional[int] = Query(None, description="Mês para estatísticas"),
):
    """Obter estatísticas gerais de saúde"""
    from sqlalchemy import extract

    base_query = db.query(SaudeAnimais)

    if ano:
        base_query = base_query.filter(
            extract("year", SaudeAnimais.DATA_OCORRENCIA) == ano
        )
    if mes:
        base_query = base_query.filter(
            extract("month", SaudeAnimais.DATA_OCORRENCIA) == mes
        )

    # Estatísticas gerais
    total_registros = base_query.count()

    # Registros do mês atual
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    registros_mes_atual = (
        db.query(SaudeAnimais)
        .filter(
            extract("year", SaudeAnimais.DATA_OCORRENCIA) == ano_atual,
            extract("month", SaudeAnimais.DATA_OCORRENCIA) == mes_atual,
        )
        .count()
    )

    # Custo total do mês
    custo_mes = (
        db.query(func.sum(SaudeAnimais.CUSTO))
        .filter(
            extract("year", SaudeAnimais.DATA_OCORRENCIA) == ano_atual,
            extract("month", SaudeAnimais.DATA_OCORRENCIA) == mes_atual,
        )
        .scalar()
        or 0
    )

    # Próximas aplicações (próximos 30 dias)
    data_limite = datetime.now() + timedelta(days=30)
    proximas_aplicacoes = (
        db.query(SaudeAnimais)
        .filter(SaudeAnimais.PROXIMA_APLICACAO.between(datetime.now(), data_limite))
        .count()
    )

    # Animais em tratamento (com registros nos últimos 30 dias)
    data_limite_tratamento = datetime.now() - timedelta(days=30)
    animais_em_tratamento = (
        db.query(func.count(func.distinct(SaudeAnimais.ID_ANIMAL)))
        .filter(SaudeAnimais.DATA_OCORRENCIA >= data_limite_tratamento)
        .scalar()
        or 0
    )

    # Breakdown por tipo
    tipos = ["VACINA", "VERMIFUGO", "MEDICAMENTO", "EXAME", "CONSULTA"]
    totals_por_tipo = {}
    for tipo in tipos:
        total = base_query.filter(SaudeAnimais.TIPO_REGISTRO == tipo).count()
        totals_por_tipo[tipo] = total

    return EstatisticasSaude(
        total_registros=total_registros,
        registros_mes_atual=registros_mes_atual,
        custo_total_mes=custo_mes,
        proximas_aplicacoes=proximas_aplicacoes,
        animais_em_tratamento=animais_em_tratamento,
        total_vacinas=totals_por_tipo.get("VACINA", 0),
        total_vermifugos=totals_por_tipo.get("VERMIFUGO", 0),
        total_medicamentos=totals_por_tipo.get("MEDICAMENTO", 0),
        total_exames=totals_por_tipo.get("EXAME", 0),
        total_consultas=totals_por_tipo.get("CONSULTA", 0),
    )


@router.get("/historico/{animal_id}", response_model=HistoricoSaude)
async def get_historico_saude(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    meses: int = Query(12, description="Período em meses para análise"),
):
    """Histórico completo de saúde do animal"""
    # Verificar se animal existe
    animal = db.query(Animal).filter(Animal.ID == animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )

    data_limite = datetime.now() - timedelta(days=meses * 30)

    registros = (
        db.query(SaudeAnimais)
        .filter(
            SaudeAnimais.ID_ANIMAL == animal_id,
            SaudeAnimais.DATA_OCORRENCIA >= data_limite,
        )
        .order_by(desc(SaudeAnimais.DATA_OCORRENCIA))
        .all()
    )

    # Enriquecer registros com dados relacionados
    registros_enriched = []
    for registro in registros:
        response_data = SaudeResponse.model_validate(registro)
        response_data.animal_nome = animal.NOME

        # Adicionar nome do medicamento se houver
        if registro.ID_MEDICAMENTO:
            medicamento = (
                db.query(Medicamento)
                .filter(Medicamento.ID == registro.ID_MEDICAMENTO)
                .first()
            )
            if medicamento:
                response_data.medicamento_nome = medicamento.NOME

        registros_enriched.append(response_data)

    return HistoricoSaude(
        animal_id=animal_id, animal_nome=animal.NOME, registros=registros_enriched
    )


@router.get("/calendario/", response_model=List[CalendarioSaude])
async def get_calendario_saude(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data_inicio: str = Query(..., description="Data início (YYYY-MM-DD)"),
    data_fim: str = Query(..., description="Data fim (YYYY-MM-DD)"),
):
    """Calendário de aplicações programadas"""
    try:
        inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        fim = datetime.strptime(data_fim, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data inválido. Use YYYY-MM-DD",
        )

    # Buscar aplicações no período
    aplicacoes = (
        db.query(SaudeAnimais, Animal.NOME)
        .join(Animal, SaudeAnimais.ID_ANIMAL == Animal.ID)
        .filter(SaudeAnimais.PROXIMA_APLICACAO.between(inicio, fim))
        .all()
    )

    # Agrupar por data
    calendario = {}
    for saude, animal_nome in aplicacoes:
        data_key = saude.PROXIMA_APLICACAO.date().isoformat()

        if data_key not in calendario:
            calendario[data_key] = {
                "data": saude.PROXIMA_APLICACAO,
                "eventos": [],
            }

        evento = {
            "animal_id": saude.ID_ANIMAL,
            "animal_nome": animal_nome,
            "tipo": saude.TIPO_REGISTRO,
            "descricao": saude.DESCRICAO or saude.MEDICAMENTO_APLICADO,
            "veterinario": saude.VETERINARIO_RESPONSAVEL,
        }

        calendario[data_key]["eventos"].append(evento)

    # Converter para lista de CalendarioSaude
    resultado = []
    for data_key, dados in calendario.items():
        resultado.append(CalendarioSaude(data=dados["data"], eventos=dados["eventos"]))

    # Ordenar por data
    resultado.sort(key=lambda x: x.data)
    return resultado


@router.get("/relatorio/consumo-por-tipo", response_model=List[ConsumoPorTipo])
async def get_consumo_por_tipo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    meses_periodo: int = Query(6, description="Período em meses para análise"),
):
    """Relatório de consumo por tipo de registro"""
    data_limite = datetime.now() - timedelta(days=meses_periodo * 30)

    # Buscar registros agrupados por tipo
    resultados = (
        db.query(
            SaudeAnimais.TIPO_REGISTRO,
            func.count(SaudeAnimais.ID).label("total_registros"),
            func.sum(SaudeAnimais.CUSTO).label("custo_total"),
        )
        .filter(SaudeAnimais.DATA_OCORRENCIA >= data_limite)
        .group_by(SaudeAnimais.TIPO_REGISTRO)
        .order_by(desc("total_registros"))
        .all()
    )

    consumo_list = []
    for resultado in resultados:
        consumo = ConsumoPorTipo(
            tipo_registro=resultado.TIPO_REGISTRO,
            total_registros=resultado.total_registros,
            custo_total=resultado.custo_total or 0.0,
        )
        consumo_list.append(consumo)

    return consumo_list


@router.get("/medicamentos/autocomplete", response_model=List[MedicamentoAutocomplete])
async def get_medicamentos_autocomplete(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    query: str = Query(..., min_length=2, description="Termo de busca"),
):
    """Autocomplete para medicamentos ativos"""
    medicamentos = (
        db.query(Medicamento)
        .filter(Medicamento.ATIVO == "S", Medicamento.NOME.ilike(f"%{query}%"))
        .order_by(Medicamento.NOME)
        .limit(10)
        .all()
    )

    result = []
    for medicamento in medicamentos:
        autocomplete_item = MedicamentoAutocomplete(
            id=medicamento.ID,
            nome=medicamento.NOME,
            unidade_medida=medicamento.UNIDADE_MEDIDA,
            estoque_atual=medicamento.ESTOQUE_ATUAL,
        )
        result.append(autocomplete_item)

    return result
