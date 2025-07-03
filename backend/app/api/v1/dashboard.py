from datetime import datetime, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.animal import Animal
from app.models.manejo import ProdutoManejo
from app.models.medicamento import Medicamento, MovimentacaoMedicamento
from app.models.racao import FornecimentoRacaoAnimal, ProdutoRacao
from app.models.reproducao import Reproducao
from app.models.saude import SaudeAnimais
from app.models.terreno import Terreno
from app.models.user import User
from app.schemas.dashboard import (
    AlertaEstoque,
    AlertaSaude,
    CustoProprietario,
    DashboardKPIs,
    DashboardResponse,
    GraficoBarras,
    GraficoPizza,
    RelatorioAnimal,
    RelatorioTerreno,
)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql import desc, text

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    proprietario: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dashboard principal com KPIs, alertas e gráficos"""

    # Filtros de data
    if data_inicio:
        data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d")
    else:
        data_inicio_dt = datetime.now() - timedelta(days=30)

    if data_fim:
        data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")
    else:
        data_fim_dt = datetime.now()

    # === KPIs ===
    total_animais = (
        db.query(func.count(Animal.ID)).filter(Animal.STATUS_ANIMAL == "ATIVO").scalar()
    )
    total_terrenos = (
        db.query(func.count(Terreno.ID))
        .filter(Terreno.STATUS_TERRENO == "DISPONIVEL")
        .scalar()
    )

    # Animais em tratamento (com aplicações nos últimos 7 dias)
    animais_tratamento = (
        db.query(func.count(func.distinct(SaudeAnimais.ID_ANIMAL)))
        .filter(
            SaudeAnimais.DATA_OCORRENCIA >= datetime.now() - timedelta(days=7),
        )
        .scalar()
    )

    # Alertas de estoque baixo
    alertas_medicamentos = (
        db.query(func.count(Medicamento.ID))
        .filter(
            Medicamento.ATIVO == "S",
            Medicamento.ESTOQUE_ATUAL <= Medicamento.ESTOQUE_MINIMO,
        )
        .scalar()
    )

    alertas_racao = (
        db.query(func.count(ProdutoRacao.ID))
        .filter(
            ProdutoRacao.ATIVO == "S",
            ProdutoRacao.ESTOQUE_ATUAL <= ProdutoRacao.ESTOQUE_MINIMO,
        )
        .scalar()
    )

    alertas_manejo = (
        db.query(func.count(ProdutoManejo.ID))
        .filter(
            ProdutoManejo.ATIVO == "S",
            ProdutoManejo.ESTOQUE_ATUAL <= ProdutoManejo.ESTOQUE_MINIMO,
        )
        .scalar()
    )

    alertas_estoque_total = alertas_medicamentos + alertas_racao + alertas_manejo

    # Próximas aplicações (próximos 7 dias)
    proximas_aplicacoes = (
        db.query(func.count(SaudeAnimais.ID))
        .filter(
            SaudeAnimais.PROXIMA_APLICACAO.between(
                datetime.now().date(), (datetime.now() + timedelta(days=7)).date()
            ),
        )
        .scalar()
    )

    # Gestações ativas
    gestacoes_ativas = (
        db.query(func.count(Reproducao.ID))
        .filter(Reproducao.STATUS_REPRODUCAO == "GESTANTE", Reproducao.ATIVO == "S")
        .scalar()
    )

    kpis = DashboardKPIs(
        total_animais=total_animais or 0,
        total_terrenos=total_terrenos or 0,
        animais_tratamento=animais_tratamento or 0,
        alertas_estoque=alertas_estoque_total or 0,
        proximas_aplicacoes=proximas_aplicacoes or 0,
        gestacoes_ativas=gestacoes_ativas or 0,
    )

    # === ALERTAS DE SAÚDE ===
    alertas_saude = await _get_alertas_saude(db)

    # === ALERTAS DE ESTOQUE ===
    alertas_estoque = await _get_alertas_estoque(db)

    # === CUSTOS POR PROPRIETÁRIO ===
    custos_proprietarios = await _get_custos_proprietarios(
        db, data_inicio_dt, data_fim_dt, proprietario
    )

    # === GRÁFICOS ===
    grafico_custos = await _get_grafico_custos_mensal(db, data_inicio_dt, data_fim_dt)
    grafico_animais = await _get_grafico_distribuicao_animais(db)

    return DashboardResponse(
        kpis=kpis,
        alertas_saude=alertas_saude,
        alertas_estoque=alertas_estoque,
        custos_proprietarios=custos_proprietarios,
        grafico_custos_mensal=grafico_custos,
        grafico_distribuicao_animais=grafico_animais,
        ultimo_update=datetime.now(),
    )


@router.get("/relatorio-animal/{animal_id}", response_model=RelatorioAnimal)
async def get_relatorio_animal(
    animal_id: int,
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Relatório detalhado de um animal"""

    # Filtros de data
    data_inicio_dt = None
    if data_inicio:
        data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d")
    else:
        data_inicio_dt = datetime.now() - timedelta(days=90)

    data_fim_dt = None
    if data_fim:
        data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")
    else:
        data_fim_dt = datetime.now()

    # Buscar animal
    animal = (
        db.query(Animal).filter(Animal.ID == animal_id, Animal.ATIVO == "S").first()
    )
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")

    # Calcular idade
    idade_anos = None
    if animal.DATA_NASCIMENTO:
        idade_anos = (datetime.now().date() - animal.DATA_NASCIMENTO).days // 365

    # Última vacina
    ultima_vacina = (
        db.query(SaudeAnimais.DATA_OCORRENCIA)
        .filter(
            SaudeAnimais.ID_ANIMAL == animal_id,
            SaudeAnimais.TIPO_APLICACAO == "VACINA",
        )
        .order_by(desc(SaudeAnimais.DATA_OCORRENCIA))
        .first()
    )

    # Último vermífugo
    ultimo_vermifugo = (
        db.query(SaudeAnimais.DATA_OCORRENCIA)
        .filter(
            SaudeAnimais.ID_ANIMAL == animal_id,
            SaudeAnimais.TIPO_APLICACAO == "VERMIFUGO",
        )
        .order_by(desc(SaudeAnimais.DATA_OCORRENCIA))
        .first()
    )

    # Tratamentos ativos
    tratamentos_ativos = (
        db.query(func.count(SaudeAnimais.ID))
        .filter(
            SaudeAnimais.ID_ANIMAL == animal_id,
            SaudeAnimais.STATUS_TRATAMENTO == "ATIVO",
        )
        .scalar()
    )

    # Custos no período (placeholder - implementar conforme necessário)
    custo_medicamentos = (
        db.query(
            func.coalesce(
                func.sum(
                    MovimentacaoMedicamento.PRECO_UNITARIO
                    * MovimentacaoMedicamento.QUANTIDADE
                ),
                0,
            )
        )
        .join(
            SaudeAnimais,
            MovimentacaoMedicamento.ID_MEDICAMENTO == SaudeAnimais.ID_MEDICAMENTO,
        )
        .filter(
            SaudeAnimais.ID_ANIMAL == animal_id,
            SaudeAnimais.DATA_OCORRENCIA.between(data_inicio_dt, data_fim_dt),
        )
        .scalar()
        or 0.0
    )

    custo_racao = (
        db.query(
            func.coalesce(
                func.sum(
                    FornecimentoRacaoAnimal.QUANTIDADE
                    * FornecimentoRacaoAnimal.PRECO_UNITARIO
                ),
                0,
            )
        )
        .filter(
            FornecimentoRacaoAnimal.ID_ANIMAL == animal_id,
            FornecimentoRacaoAnimal.DATA_FORNECIMENTO.between(
                data_inicio_dt, data_fim_dt
            ),
            FornecimentoRacaoAnimal.ATIVO == "S",
        )
        .scalar()
        or 0.0
    )

    # Status reprodução
    status_reproducao = (
        db.query(Reproducao.STATUS_REPRODUCAO)
        .filter(Reproducao.ID_EGUA == animal_id, Reproducao.ATIVO == "S")
        .order_by(desc(Reproducao.DATA_REGISTRO))
        .first()
    )

    # Última cobertura
    data_ultima_cobertura = (
        db.query(Reproducao.DATA_COBERTURA)
        .filter(Reproducao.ID_EGUA == animal_id, Reproducao.ATIVO == "S")
        .order_by(desc(Reproducao.DATA_COBERTURA))
        .first()
    )

    return RelatorioAnimal(
        animal_id=animal.ID,
        animal_nome=animal.NOME,
        raca=animal.RACA or "",
        proprietario=animal.PROPRIETARIO or "",
        data_nascimento=animal.DATA_NASCIMENTO,
        idade_anos=idade_anos,
        ultima_vacina=ultima_vacina[0] if ultima_vacina else None,
        ultimo_vermifugo=ultimo_vermifugo[0] if ultimo_vermifugo else None,
        tratamentos_ativos=tratamentos_ativos or 0,
        custo_medicamentos=custo_medicamentos,
        custo_racao=custo_racao,
        custo_total=custo_medicamentos + custo_racao,
        status_reproducao=status_reproducao[0] if status_reproducao else None,
        data_ultima_cobertura=(
            data_ultima_cobertura[0] if data_ultima_cobertura else None
        ),
    )


@router.get("/relatorio-terreno/{terreno_id}", response_model=RelatorioTerreno)
async def get_relatorio_terreno(
    terreno_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Relatório detalhado de um terreno"""

    # Buscar terreno
    terreno = (
        db.query(Terreno).filter(Terreno.ID == terreno_id, Terreno.ATIVO == "S").first()
    )
    if not terreno:
        raise HTTPException(status_code=404, detail="Terreno não encontrado")

    # Animais atuais
    animais_atuais = (
        db.query(func.count(Animal.ID))
        .filter(Animal.ID_TERRENO_ATUAL == terreno_id, Animal.ATIVO == "S")
        .scalar()
    )

    # Taxa de ocupação
    taxa_ocupacao = None
    if terreno.CAPACIDADE_ANIMAIS and terreno.CAPACIDADE_ANIMAIS > 0:
        taxa_ocupacao = (animais_atuais / terreno.CAPACIDADE_ANIMAIS) * 100

    return RelatorioTerreno(
        terreno_id=terreno.ID,
        terreno_nome=terreno.NOME,
        area_hectares=terreno.AREA_HECTARES or 0,
        tipo_uso=terreno.TIPO_USO or "",
        animais_atuais=animais_atuais or 0,
        capacidade_maxima=terreno.CAPACIDADE_ANIMAIS,
        taxa_ocupacao=taxa_ocupacao,
        ultima_aplicacao=None,  # Implementar se necessário
        produtos_aplicados=0,  # Implementar se necessário
        custo_manejo=0.0,  # Implementar se necessário
        ultima_analise=None,  # Implementar se necessário
        ph_medio=None,  # Implementar se necessário
    )


# === FUNÇÕES AUXILIARES ===


async def _get_alertas_saude(db: Session) -> List[AlertaSaude]:
    """Buscar alertas de saúde"""
    alertas = []

    # Vacinas vencidas ou próximas do vencimento
    query = text(
        """
        SELECT a.ID, a.NOME, s.PROXIMA_APLICACAO, s.TIPO_APLICACAO
        FROM ANIMAIS a
        JOIN SAUDE_ANIMAIS s ON a.ID = s.ID_ANIMAL
        WHERE s.PROXIMA_APLICACAO <= SYSDATE + 7
        AND s.ATIVO = 'S'
        AND a.ATIVO = 'S'
        ORDER BY s.PROXIMA_APLICACAO
    """
    )

    resultado = db.execute(query).fetchall()

    for row in resultado:
        dias_atraso = (datetime.now().date() - row[2]).days if row[2] else 0
        prioridade = "ALTA" if dias_atraso > 0 else "MEDIA"

        alertas.append(
            AlertaSaude(
                animal_id=row[0],
                animal_nome=row[1],
                tipo_alerta=(
                    f"{row[3]}_VENCIDA" if dias_atraso > 0 else f"{row[3]}_PROXIMA"
                ),
                descricao=f"{row[3]} {'vencida' if dias_atraso > 0 else 'próxima'} "
                f"para {row[1]}",
                dias_atraso=dias_atraso,
                prioridade=prioridade,
                data_vencimento=row[2],
            )
        )

    return alertas[:10]  # Limitar a 10 alertas


async def _get_alertas_estoque(db: Session) -> List[AlertaEstoque]:
    """Buscar alertas de estoque baixo"""
    alertas = []

    # Medicamentos
    medicamentos = (
        db.query(Medicamento)
        .filter(
            Medicamento.ATIVO == "S",
            Medicamento.ESTOQUE_ATUAL <= Medicamento.ESTOQUE_MINIMO,
        )
        .all()
    )

    for med in medicamentos:
        status = "CRITICO" if (med.ESTOQUE_ATUAL or 0) == 0 else "BAIXO"
        alertas.append(
            AlertaEstoque(
                produto_id=med.ID,
                produto_nome=med.NOME,
                tipo_produto="MEDICAMENTO",
                estoque_atual=med.ESTOQUE_ATUAL or 0,
                estoque_minimo=med.ESTOQUE_MINIMO or 0,
                unidade_medida=med.UNIDADE_MEDIDA or "",
                status=status,
            )
        )

    # Ração
    racoes = (
        db.query(ProdutoRacao)
        .filter(
            ProdutoRacao.ATIVO == "S",
            ProdutoRacao.ESTOQUE_ATUAL <= ProdutoRacao.ESTOQUE_MINIMO,
        )
        .all()
    )

    for racao in racoes:
        status = "CRITICO" if (racao.ESTOQUE_ATUAL or 0) == 0 else "BAIXO"
        alertas.append(
            AlertaEstoque(
                produto_id=racao.ID,
                produto_nome=racao.NOME,
                tipo_produto="RACAO",
                estoque_atual=racao.ESTOQUE_ATUAL or 0,
                estoque_minimo=racao.ESTOQUE_MINIMO or 0,
                unidade_medida=racao.UNIDADE_MEDIDA or "",
                status=status,
            )
        )

    return alertas


async def _get_custos_proprietarios(
    db: Session, data_inicio: datetime, data_fim: datetime, proprietario: Optional[str]
) -> List[CustoProprietario]:
    """Calcular custos por proprietário"""

    # Query simplificada - implementar cálculos reais conforme necessário
    query = text(
        """
        SELECT 
            a.PROPRIETARIO,
            COUNT(a.ID) as total_animais,
            0 as total_medicamentos,
            0 as total_racao,
            0 as total_manejo
        FROM ANIMAIS a
        WHERE a.STATUS_ANIMAL = 'ATIVO'
        AND (:proprietario IS NULL OR a.PROPRIETARIO = :proprietario)
        GROUP BY a.PROPRIETARIO
        ORDER BY a.PROPRIETARIO
    """
    )

    resultado = db.execute(query, {"proprietario": proprietario}).fetchall()

    custos = []
    for row in resultado:
        if row[0]:  # Se tem proprietário
            total_geral = row[2] + row[3] + row[4]
            custo_por_animal = total_geral / row[1] if row[1] > 0 else 0

            custos.append(
                CustoProprietario(
                    proprietario=row[0],
                    total_medicamentos=row[2],
                    total_racao=row[3],
                    total_manejo=row[4],
                    total_geral=total_geral,
                    numero_animais=row[1],
                    custo_por_animal=custo_por_animal,
                    periodo=f"{data_inicio.strftime('%d/%m/%Y')} - "
                    f"{data_fim.strftime('%d/%m/%Y')}",
                )
            )

    return custos


async def _get_grafico_custos_mensal(
    db: Session, data_inicio: datetime, data_fim: datetime
) -> GraficoBarras:
    """Gráfico de custos mensais"""

    # Dados mock para demonstração
    labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
    datasets = [
        {
            "label": "Medicamentos",
            "data": [1200, 1100, 1300, 1150, 1400, 1250],
            "backgroundColor": "#42A5F5",
        },
        {
            "label": "Ração",
            "data": [2800, 2600, 3100, 2900, 3200, 2950],
            "backgroundColor": "#66BB6A",
        },
        {
            "label": "Manejo",
            "data": [800, 750, 900, 850, 950, 825],
            "backgroundColor": "#FFA726",
        },
    ]

    return GraficoBarras(
        labels=labels, datasets=datasets, titulo="Custos Mensais por Categoria"
    )


async def _get_grafico_distribuicao_animais(db: Session) -> GraficoPizza:
    """Gráfico de distribuição de animais por raça"""

    query = text(
        """
        SELECT COALESCE(RACA, 'Não informado') as raca, COUNT(*) as total
        FROM ANIMAIS 
        WHERE ATIVO = 'S'
        GROUP BY RACA
        ORDER BY total DESC
    """
    )

    resultado = db.execute(query).fetchall()

    labels = [row[0] for row in resultado]
    data = [float(row[1]) for row in resultado]

    return GraficoPizza(
        labels=labels, data=data, titulo="Distribuição de Animais por Raça"
    )
