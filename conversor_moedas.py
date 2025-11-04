import requests
from abc import ABC, abstractmethod
from typing import Dict, Optional

# --- Princípio 1: Inversão de Dependência (Abstração) ---
class ProvedorTaxasCambio(ABC):
    """
    Interface abstrata (Classe Base Abstrata) para um provedor de taxas de câmbio.
    Isso permite "inverter" a dependência: a lógica da aplicação
    dependerá desta abstração, e não de uma API concreta.
    """
    @abstractmethod
    def obter_taxas(self, moeda_base: str) -> Optional[Dict[str, float]]:
        """Busca as taxas de câmbio para uma moeda base."""
        pass

# --- Princípio 2: Responsabilidade Única (Lógica de API) ---
class ProvedorTaxasApi(ProvedorTaxasCambio):
    """
    Implementação concreta do provedor de taxas que busca dados
    de uma API pública. Sua única responsabilidade é lidar
    com a comunicação de rede e o parsing da resposta.
    """
    def __init__(self, url_api: str):
        self.url_api = url_api

    def obter_taxas(self, moeda_base: str) -> Optional[Dict[str, float]]:
        """Busca as taxas da API."""
        try:
            # Constrói a URL completa (ex: https://api.exchangerate-api.com/v4/latest/BRL)
            url = f"{self.url_api}{moeda_base}"
            resposta = requests.get(url, timeout=5)
            resposta.raise_for_status()  # Lança erro para status HTTP 4xx/5xx
            dados = resposta.json()
            return dados.get('rates')
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados da API: {e}")
            return None

# --- Princípio 2: Responsabilidade Única (Lógica de Negócio) ---
class LogicaConversao:
    """
    Esta classe tem a única responsabilidade de calcular a conversão.
    Ela não sabe de onde vêm as taxas (API, cache, mock), apenas como usá-las.
    """
    def converter(self, valor: float, taxa: float) -> float:
        """Realiza o cálculo de conversão."""
        if valor < 0:
            raise ValueError("O valor não pode ser negativo.")
        return valor * taxa