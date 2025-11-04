import tkinter as tk 
import ttkbootstrap as ttk
from tkinter import messagebox # O messagebox é do tkinter, o ttkbootstrap só o estiliza
from ttkbootstrap.constants import *
from typing import List
from conversor_moedas import ProvedorTaxasCambio, LogicaConversao

# --- Princípio SRP: Classe focada em UI/GUI ---
class AppConversorMoedas:
    """
    Classe principal da Interface Gráfica (GUI).
    
    Sua única responsabilidade (SRP) é montar a tela, 
    capturar eventos do usuário (cliques, seleções) e orquestrar as
    chamadas para as classes de lógica e de API.
    """
    def __init__(self, root: tk.Tk, provedor: ProvedorTaxasCambio, logica: LogicaConversao, moedas: List[str]):
        self.root = root
        
        # Injeção de Dependência (DIP): A GUI recebe as dependências
        # prontas, em vez de criá-las aqui dentro.
        self.provedor = provedor
        self.logica = logica
        
        self.moedas = moedas
        self.taxas = {} # Cache simples para guardar as taxas buscadas

        self.root.title("Conversor de Moedas SOLID")
        self.root.geometry("350x250")

        self.criar_componentes()
        self.carregar_taxas_iniciais()

    def criar_componentes(self):
        """Cria e posiciona os widgets (componentes) do tkinter na tela."""
        
        # Frame principal para organizar os widgets
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(W, E, N, S))

        # --- Seção do Valor de Entrada ---
        ttk.Label(frame, text="Valor:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.var_valor = tk.DoubleVar()
        self.campo_valor = ttk.Entry(frame, textvariable=self.var_valor, width=15)
        self.campo_valor.grid(row=0, column=1, padx=5, pady=5)

        # --- Seção da Moeda Origem ("De") ---
        ttk.Label(frame, text="De:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.var_moeda_de = tk.StringVar(value=self.moedas[0])
        self.combo_moeda_de = ttk.Combobox(frame, textvariable=self.var_moeda_de, values=self.moedas, width=12)
        self.combo_moeda_de.grid(row=1, column=1, padx=5, pady=5)
        # "Bind" (liga) um evento à combobox para atualizar as taxas
        self.combo_moeda_de.bind("<<ComboboxSelected>>", self.ao_mudar_moeda_base)

        # --- Seção da Moeda Destino ("Para") ---
        ttk.Label(frame, text="Para:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.var_moeda_para = tk.StringVar(value=self.moedas[1])
        self.combo_moeda_para = ttk.Combobox(frame, textvariable=self.var_moeda_para, values=self.moedas, width=12)
        self.combo_moeda_para.grid(row=2, column=1, padx=5, pady=5)

        # --- Botão de Ação ---
        self.botao_converter = ttk.Button(frame, text="Converter", command=self.executar_conversao)
        self.botao_converter.grid(row=3, column=0, columnspan=2, padx=5, pady=15)

        # --- Label de Resultado ---
        self.label_resultado = ttk.Label(frame, text="Resultado:", font=("Arial", 12))
        self.label_resultado.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def carregar_taxas_iniciais(self):
        """Busca as taxas de câmbio assim que o app abre (para a moeda padrão)."""
        moeda_base = self.var_moeda_de.get()
        # Delega a busca ao provedor (que foi injetado)
        self.taxas = self.provedor.obter_taxas(moeda_base) 
        if not self.taxas:
            messagebox.showerror("Erro de API", "Não foi possível carregar as taxas de câmbio. Verifique a conexão.")
            # Desabilita o botão se a API falhar, impedindo o uso.
            self.botao_converter.config(state=DISABLED)

    def ao_mudar_moeda_base(self, event=None):
        """
        Handler de evento: chamado quando o usuário troca a moeda "De:".
        Atualiza o cache local de taxas (self.taxas).
        """
        moeda_base = self.var_moeda_de.get()
        self.taxas = self.provedor.obter_taxas(moeda_base)
        if not self.taxas:
            messagebox.showerror("Erro de API", f"Não foi possível carregar as taxas para {moeda_base}.")
        
    def executar_conversao(self):
        """
        Handler de evento: chamado pelo clique no botão "Converter".
        Orquestra todo o processo: pega dados da tela, valida, chama a lógica e mostra o resultado.
        """
        try:
            # 1. Pega os dados da tela
            valor = self.var_valor.get()
            moeda_para = self.var_moeda_para.get()

            # 2. Validação: Garante que as taxas estão carregadas
            if not self.taxas:
                self.carregar_taxas_iniciais() # Tenta carregar novamente
                if not self.taxas:
                    messagebox.showerror("Erro", "Taxas de câmbio indisponíveis.")
                    return

            # 3. Pega a taxa específica do nosso cache local
            taxa = self.taxas.get(moeda_para)
            if taxa is None:
                messagebox.showerror("Erro", f"Taxa para {moeda_para} não encontrada.")
                return

            # 4. Delega o cálculo para a classe de lógica (injetada)
            resultado = self.logica.converter(valor, taxa)

            # 5. Atualiza a interface com o resultado formatado
            self.label_resultado.config(text=f"Resultado: {resultado:.2f} {moeda_para}")

        # --- Tratamento de Erros ---
        except tk.TclError:
            # Erro comum se o usuário digitar "abc" no campo de valor
            messagebox.showerror("Erro de Entrada", "Por favor, insira um valor numérico válido.")
        except ValueError as e:
            # Erro vindo da nossa 'LogicaConversao' (ex: valor negativo)
            messagebox.showerror("Erro de Lógica", str(e))
        except Exception as e:
            # Captura genérica para outros erros inesperados
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")