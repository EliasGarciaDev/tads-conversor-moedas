import tkinter as tk
# Importa as classes traduzidas
from conversor_moedas import ProvedorTaxasApi, LogicaConversao
from app_gui import AppConversorMoedas

# --- Ponto de Entrada: Configuração das Dependências ---

def main():
    # URL da API pública (v4)
    URL_API = "https://api.exchangerate-api.com/v4/latest/"
    
    # Lista de moedas que queremos usar
    MOEDAS = ["BRL", "USD", "EUR", "JPY", "GBP"]

    # 1. Instancia as dependências concretas
    # (Injeção de Dependência)
    provedor_taxas = ProvedorTaxasApi(url_api=URL_API)
    logica_conversao = LogicaConversao()

    # 2. Configura a raiz do Tkinter
    root = tk.Tk()

    # 3. Injeta as dependências na classe da GUI
    app = AppConversorMoedas(
        root=root, 
        provedor=provedor_taxas, 
        logica=logica_conversao,
        moedas=MOEDAS
    )

    # 4. Inicia a aplicação
    root.mainloop()

if __name__ == "__main__":
    main()