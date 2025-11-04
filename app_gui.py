import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
# Importa as classes traduzidas do nosso outro arquivo
from conversor_moedas import ProvedorTaxasCambio, LogicaConversao

# --- Princípio 2: Responsabilidade Única (Interface do Usuário) ---
class AppConversorMoedas:
    """
    Esta classe tem a única responsabilidade de construir e gerenciar
    a interface gráfica (GUI) com o Tkinter.
    
    Ela *recebe* as dependências (provedor e logica) em seu construtor
    (Injeção de Dependência), em vez de criá-las.
    """
    def __init__(self, root: tk.Tk, provedor: ProvedorTaxasCambio, logica: LogicaConversao, moedas: List[str]):
        self.root = root
        self.provedor = provedor
        self.logica = logica
        self.moedas = moedas
        self.taxas = {} # Dicionário para armazenar as taxas carregadas

        self.root.title("Conversor de Moedas SOLID")
        self.root.geometry("350x250")

        self.criar_componentes()
        self.carregar_taxas_iniciais()

    def criar_componentes(self):
        """Cria os componentes da interface (labels, campos, botões)."""
        # Frame principal
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # --- Valor
        ttk.Label(frame, text="Valor:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.var_valor = tk.DoubleVar()
        self.campo_valor = ttk.Entry(frame, textvariable=self.var_valor, width=15)
        self.campo_valor.grid(row=0, column=1, padx=5, pady=5)

        # --- Moeda "De"
        ttk.Label(frame, text="De:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.var_moeda_de = tk.StringVar(value=self.moedas[0])
        self.combo_moeda_de = ttk.Combobox(frame, textvariable=self.var_moeda_de, values=self.moedas, width=12)
        self.combo_moeda_de.grid(row=1, column=1, padx=5, pady=5)
        self.combo_moeda_de.bind("<<ComboboxSelected>>", self.ao_mudar_moeda_base)

        # --- Moeda "Para"
        ttk.Label(frame, text="Para:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.var_moeda_para = tk.StringVar(value=self.moedas[1])
        self.combo_moeda_para = ttk.Combobox(frame, textvariable=self.var_moeda_para, values=self.moedas, width=12)
        self.combo_moeda_para.grid(row=2, column=1, padx=5, pady=5)

        # --- Botão
        self.botao_converter = ttk.Button(frame, text="Converter", command=self.executar_conversao)
        self.botao_converter.grid(row=3, column=0, columnspan=2, padx=5, pady=15)

        # --- Resultado
        self.label_resultado = ttk.Label(frame, text="Resultado:", font=("Arial", 12))
        self.label_resultado.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def carregar_taxas_iniciais(self):
        """Carrega as taxas da moeda base inicial (ex: BRL) ao abrir o app."""
        moeda_base = self.var_moeda_de.get()
        # Chama o método traduzido do provedor
        self.taxas = self.provedor.obter_taxas(moeda_base) 
        if not self.taxas:
            messagebox.showerror("Erro de API", "Não foi possível carregar as taxas de câmbio. Verifique a conexão.")
            self.botao_converter.config(state=tk.DISABLED)

    def ao_mudar_moeda_base(self, event=None):
        """Recarrega as taxas quando o usuário muda a moeda base."""
        moeda_base = self.var_moeda_de.get()
        # Chama o método traduzido do provedor
        self.taxas = self.provedor.obter_taxas(moeda_base)
        if not self.taxas:
            messagebox.showerror("Erro de API", f"Não foi possível carregar as taxas para {moeda_base}.")
        
    def executar_conversao(self):
        """
        Função chamada pelo botão "Converter".
        Delega a busca da taxa e o cálculo da conversão.
        """
        try:
            valor = self.var_valor.get()
            moeda_para = self.var_moeda_para.get()

            # Se as taxas não foram carregadas, para
            if not self.taxas:
                self.carregar_taxas_iniciais() # Tenta carregar novamente
                if not self.taxas:
                    messagebox.showerror("Erro", "Taxas de câmbio indisponíveis.")
                    return

            # Busca a taxa de conversão específica
            taxa = self.taxas.get(moeda_para)
            if taxa is None:
                messagebox.showerror("Erro", f"Taxa para {moeda_para} não encontrada.")
                return

            # Delega o cálculo para a classe de lógica
            # Chama o método traduzido da lógica
            resultado = self.logica.converter(valor, taxa)

            self.label_resultado.config(text=f"Resultado: {resultado:.2f} {moeda_para}")

        except tk.TclError:
            messagebox.showerror("Erro de Entrada", "Por favor, insira um valor numérico válido.")
        except ValueError as e:
            messagebox.showerror("Erro de Lógica", str(e))
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")