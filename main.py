import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
from processador import ProcessadorTabelas


class AppEnriquecedorTabelas:
    """Aplicação desktop para enriquecimento de tabelas com busca CAIXA/VOTO."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Enriquecedor de Tabelas - CAIXA/VOTO")
        self.root.geometry("800x700")
        
        self.processador = ProcessadorTabelas(coluna_busca="numeroProcesso")
        
        # Variáveis para armazenar caminhos
        self.referencia_path = tk.StringVar(value="")
        self.caixa1_path = tk.StringVar(value="")
        self.caixa2_path = tk.StringVar(value="")
        self.voto_path = tk.StringVar(value="")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura interface do usuário."""
        # Frame título
        titulo_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        titulo_frame.pack(fill=tk.X)
        
        titulo_label = tk.Label(
            titulo_frame,
            text="Enriquecedor de Tabelas - CAIXA/VOTO",
            font=("Arial", 14, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=10
        )
        titulo_label.pack()
        
        # Frame principal com scroll
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Seção: Seleção de Arquivos
        self._criar_secao_arquivos(main_frame)
        
        # Seção: Log/Status
        self._criar_secao_log(main_frame)
        
        # Seção: Botões de Ação
        self._criar_secao_botoes(main_frame)
    
    def _criar_secao_arquivos(self, parent):
        """Cria seção de seleção de arquivos."""
        frame = tk.LabelFrame(parent, text="Selecionar Arquivos", font=("Arial", 10, "bold"), padx=10, pady=10)
        frame.pack(fill=tk.X, pady=10)
        
        # Tabela de Referência
        self._criar_linha_arquivo(frame, "Tabela de Referência:", self.referencia_path, 0)
        
        # CAIXA 1
        self._criar_linha_arquivo(frame, "Planilha CAIXA 1:", self.caixa1_path, 1)
        
        # CAIXA 2 (opcional)
        self._criar_linha_arquivo(frame, "Planilha CAIXA 2 (opcional):", self.caixa2_path, 2)
        
        # VOTO
        self._criar_linha_arquivo(frame, "Tabela VOTO:", self.voto_path, 3)
    
    def _criar_linha_arquivo(self, parent, label_text, var, row):
        """Cria linha com label, campo e botão de seleção."""
        label = tk.Label(parent, text=label_text, font=("Arial", 9), width=20, justify=tk.LEFT)
        label.grid(row=row, column=0, sticky=tk.W, pady=5)
        
        entry = tk.Entry(parent, textvariable=var, font=("Arial", 9), width=50, state=tk.DISABLED)
        entry.grid(row=row, column=1, sticky=tk.EW, padx=5)
        
        btn = tk.Button(
            parent,
            text="Selecionar",
            command=lambda: self._selecionar_arquivo(var),
            width=12
        )
        btn.grid(row=row, column=2, padx=5)
        
        parent.columnconfigure(1, weight=1)
    
    def _criar_secao_log(self, parent):
        """Cria seção de log/status."""
        frame = tk.LabelFrame(parent, text="Log de Processamento", font=("Arial", 10, "bold"), padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(frame, height=12, font=("Courier", 9), state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def _criar_secao_botoes(self, parent):
        """Cria seção de botões de ação."""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=10)
        
        btn_processar = tk.Button(
            frame,
            text="Processar Tabelas",
            command=self._processar_tabelas,
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            padx=15,
            pady=10,
            width=20
        )
        btn_processar.pack(side=tk.LEFT, padx=5)
        
        btn_salvar = tk.Button(
            frame,
            text="Salvar Resultado (Excel)",
            command=self._salvar_resultado,
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            padx=15,
            pady=10,
            width=20,
            state=tk.DISABLED
        )
        btn_salvar.pack(side=tk.LEFT, padx=5)
        self.btn_salvar = btn_salvar
        
        btn_limpar = tk.Button(
            frame,
            text="Limpar",
            command=self._limpar_tudo,
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=10,
            width=10
        )
        btn_limpar.pack(side=tk.RIGHT, padx=5)
    
    def _selecionar_arquivo(self, var):
        """Abre diálogo para seleção de arquivo CSV."""
        arquivo = filedialog.askopenfilename(
            title="Selecionar arquivo CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if arquivo:
            var.set(arquivo)
            self._escrever_log(f"Arquivo selecionado: {Path(arquivo).name}")
    
    def _validar_arquivos(self):
        """Valida se todos os arquivos foram selecionados."""
        if not self.referencia_path.get():
            messagebox.showerror("Erro", "Selecione a Tabela de Referência")
            return False
        if not self.caixa1_path.get():
            messagebox.showerror("Erro", "Selecione a Planilha CAIXA 1")
            return False
        if not self.voto_path.get():
            messagebox.showerror("Erro", "Selecione a Tabela VOTO")
            return False
        return True
    
    def _processar_tabelas(self):
        """Processa as tabelas em thread separada."""
        if not self._validar_arquivos():
            return
        
        # Desabilitar botão durante processamento
        self._escrever_log("Iniciando processamento...\n")
        
        thread = threading.Thread(target=self._executar_processamento)
        thread.daemon = True
        thread.start()
    
    def _executar_processamento(self):
        """Executa o processamento das tabelas."""
        try:
            self._escrever_log("Carregando tabela de referência...")
            self.processador.carregar_referencia(self.referencia_path.get())
            self._escrever_log("✓ Tabela de referência carregada\n")
            
            self._escrever_log("Carregando planilhas CAIXA...")
            self.processador.carregar_caixa(self.caixa1_path.get(), self.caixa2_path.get())
            if self.caixa2_path.get():
                self._escrever_log("✓ Planilhas CAIXA carregadas e concatenadas\n")
            else:
                self._escrever_log("✓ Planilha CAIXA 1 carregada; CAIXA 2 não informada\n")
            
            self._escrever_log("Carregando tabela VOTO...")
            self.processador.carregar_voto(self.voto_path.get())
            self._escrever_log("✓ Tabela VOTO carregada\n")
            
            self._escrever_log("Adicionando colunas de busca...")
            self.processador.adicionar_colunas_busca()
            self._escrever_log("✓ Colunas 'Ta na caixa?' e 'Tem voto?' adicionadas\n")
            
            resultado = self.processador.get_resultado()
            votos_sem_referencia = self.processador.get_votos_sem_referencia()
            self._escrever_log(f"\n✓ Processamento concluído com sucesso!")
            self._escrever_log(f"Total de linhas: {len(resultado)}")
            self._escrever_log(f"Votos sem tabela de referencia: {len(votos_sem_referencia)}")
            self._escrever_log(f"Colunas criadas: Ta na caixa?, Tem voto?")
            
            # Habilitar botão de salvar
            self.root.after(0, lambda: self.btn_salvar.config(state=tk.NORMAL))
            messagebox.showinfo("Sucesso", "Processamento concluído!\nAgora clique em 'Salvar Resultado' para exportar")
            
        except Exception as e:
            self._escrever_log(f"\n✗ ERRO: {str(e)}")
            self.root.after(0, lambda erro=str(e): messagebox.showerror("Erro", f"Erro no processamento:\n{erro}"))
    
    def _salvar_resultado(self):
        """Salva resultado em arquivo Excel."""
        if self.processador.resultado_df is None:
            messagebox.showerror("Erro", "Nenhum resultado para salvar. Processe as tabelas primeiro.")
            return
        
        arquivo_saida = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="resultado_enriquecido.xlsx"
        )
        
        if arquivo_saida:
            try:
                self._escrever_log(f"\nSalvando resultado em: {Path(arquivo_saida).name}...")
                self.processador.exportar_excel(arquivo_saida)
                self._escrever_log("✓ Arquivo Excel exportado com sucesso!")
                messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{arquivo_saida}")
            except Exception as e:
                self._escrever_log(f"\n✗ Erro ao salvar: {str(e)}")
                messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{str(e)}")
    
    def _limpar_tudo(self):
        """Limpa todos os campos e logs."""
        self.referencia_path.set("")
        self.caixa1_path.set("")
        self.caixa2_path.set("")
        self.voto_path.set("")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.btn_salvar.config(state=tk.DISABLED)
        self.processador = ProcessadorTabelas(coluna_busca="numeroProcesso")
        self._escrever_log("Tudo limpo. Pronto para novo processamento.\n")
    
    def _escrever_log(self, mensagem):
        """Escreve mensagem no log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, mensagem + "\n")
        self.log_text.see(tk.END)  # Auto-scroll
        self.log_text.config(state=tk.DISABLED)
        self.root.update()


def main():
    """Função principal."""
    root = tk.Tk()
    app = AppEnriquecedorTabelas(root)
    root.mainloop()


if __name__ == "__main__":
    main()
