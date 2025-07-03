from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# === DASHBOARD CARDS ===
class DashboardCard(BaseModel):
    titulo: str
    valor: str
    subtitulo: Optional[str] = None
    cor: str = "primary"  # primary, warning, negative, positive
    icone: str = "info"
    url_detalhes: Optional[str] = None


class DashboardKPIs(BaseModel):
    total_animais: int
    total_terrenos: int
    animais_tratamento: int
    alertas_estoque: int
    proximas_aplicacoes: int
    gestacoes_ativas: int


# === ALERTAS ===
class AlertaSaude(BaseModel):
    animal_id: int
    animal_nome: str
    tipo_alerta: str  # VACINA_VENCIDA, TRATAMENTO_PENDENTE, VERMIFUGACAO
    descricao: str
    dias_atraso: int
    prioridade: str  # ALTA, MEDIA, BAIXA
    data_vencimento: datetime


class AlertaEstoque(BaseModel):
    produto_id: int
    produto_nome: str
    tipo_produto: str  # MEDICAMENTO, RACAO, MANEJO
    estoque_atual: float
    estoque_minimo: float
    unidade_medida: str
    status: str  # CRITICO, BAIXO, VENCENDO
    dias_vencimento: Optional[int] = None


# === CUSTOS ===
class CustoProprietario(BaseModel):
    proprietario: str
    total_medicamentos: float
    total_racao: float
    total_manejo: float
    total_geral: float
    numero_animais: int
    custo_por_animal: float
    periodo: str


class CustoAnimal(BaseModel):
    animal_id: int
    animal_nome: str
    proprietario: str
    total_medicamentos: float
    total_racao: float
    total_manejo: float
    total_geral: float
    periodo: str


# === GRÁFICOS ===
class GraficoBarras(BaseModel):
    labels: List[str]
    datasets: List[dict]
    titulo: str
    tipo: str = "bar"


class GraficoPizza(BaseModel):
    labels: List[str]
    data: List[float]
    titulo: str
    tipo: str = "doughnut"


class GraficoLinha(BaseModel):
    labels: List[str]
    datasets: List[dict]
    titulo: str
    tipo: str = "line"


# === RELATÓRIOS ===
class RelatorioAnimal(BaseModel):
    animal_id: int
    animal_nome: str
    raca: str
    proprietario: str
    data_nascimento: Optional[datetime] = None
    idade_anos: Optional[int] = None

    # Saúde
    ultima_vacina: Optional[datetime] = None
    ultimo_vermifugo: Optional[datetime] = None
    tratamentos_ativos: int

    # Custos período
    custo_medicamentos: float = 0
    custo_racao: float = 0
    custo_total: float = 0

    # Reprodução
    status_reproducao: Optional[str] = None
    data_ultima_cobertura: Optional[datetime] = None


class RelatorioTerreno(BaseModel):
    terreno_id: int
    terreno_nome: str
    area_hectares: float
    tipo_uso: str

    # Animais
    animais_atuais: int
    capacidade_maxima: Optional[int] = None
    taxa_ocupacao: Optional[float] = None

    # Manejo
    ultima_aplicacao: Optional[datetime] = None
    produtos_aplicados: int
    custo_manejo: float = 0

    # Solo
    ultima_analise: Optional[datetime] = None
    ph_medio: Optional[float] = None


# === DASHBOARD RESPONSE ===
class DashboardResponse(BaseModel):
    kpis: DashboardKPIs
    alertas_saude: List[AlertaSaude]
    alertas_estoque: List[AlertaEstoque]
    custos_proprietarios: List[CustoProprietario]
    grafico_custos_mensal: GraficoBarras
    grafico_distribuicao_animais: GraficoPizza
    ultimo_update: datetime


# === FILTROS ===
class DashboardFiltros(BaseModel):
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    proprietario: Optional[str] = None
    terreno_ids: Optional[List[int]] = None
