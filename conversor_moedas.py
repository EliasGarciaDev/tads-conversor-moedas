import requests
from abc import ABC, abstractmethod
from typing import Dict, Optional

# --- Princípio DIP: Abstração do Provedor ---
class ProvedorTaxasCambio(ABC):
    """
    Classe base abstrata (Interface) para os provedores de taxa.
    Define o "contrato" que a GUI (app_gui) espera receber.
    Isso permite que a GUI dependa desta abstração, e não de uma API concreta.
    """
    @abstractmethod
    def obter_taxas(self, moeda_base: str) -> Optional[Dict[str, float]]:
        """Método obrigatório que toda classe filha deve implementar."""
        pass

# --- Princípio SRP: Classe focada em API ---
class ProvedorTaxasApi(ProvedorTaxasCambio):
    """
    Implementação concreta do Provedor, focada em buscar dados de uma API externa.
    
    A única responsabilidade desta classe (SRP) é lidar com a 
    comunicação web (requests), fazer o parse do JSON e tratar erros de rede.
    """
    def __init__(self, url_api: str):
        self.url_api = url_api

    def obter_taxas(self, moeda_base: str) -> Optional[Dict[str, float]]:
        """Implementa o método da interface para buscar dados da API."""
        try:
            url = f"{self.url_api}{moeda_base}"
            resposta = requests.get(url, timeout=5)
            resposta.raise_for_status()  # Lança erro para status HTTP 4xx/5xx
            dados = resposta.json()
            return dados.get('rates')
        except requests.exceptions.RequestException as e:
            # Log do erro no console para depuração (útil para o dev)
            print(f"Erro de rede ao buscar dados da API: {e}")
            return None # Retorna None para a GUI saber que falhou

# --- Princípio SRP: Classe focada em Cálculo ---
class LogicaConversao:
    """
    Classe com a única responsabilidade (SRP) de realizar a lógica de negócio
    (o cálculo matemático da conversão).
    
    Não sabe de onde vêm os dados (API, banco, etc), apenas como calcular.
    """
    def converter(self, valor: float, taxa: float) -> float:
        """Realiza o cálculo matemático da conversão."""
        if valor < 0:
            # Regra de negócio simples: não permitir conversão de valores negativos.
            raise ValueError("O valor não pode ser negativo.")
        return valor * taxa