import os
import shutil
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
from fpdf import FPDF
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gerenciador Inteligente Pro - Portfólio ADS")
        self.geometry("650x700")
        self.config_file = "config.json"
        self.diretorio_selecionado = ""
        self.historico_movimentacao = []
        self.carregar_config()

        # --- UI: Título ---
        self.label = ctk.CTkLabel(self, text="Gerenciador de Arquivos Inteligente", font=("Arial", 24, "bold"))
        self.label.pack(pady=15)

        # --- UI: Gerenciamento de Categorias (CRIAR / EDITAR) ---
        self.frame_gestao = ctk.CTkFrame(self)
        self.frame_gestao.pack(pady=10, padx=20, fill="x")
        
        self.label_gestao = ctk.CTkLabel(self.frame_gestao, text="Adicionar ou Editar Categoria", font=("Arial", 12, "bold"))
        self.label_gestao.grid(row=0, column=0, columnspan=3, pady=5)

        self.entry_nome = ctk.CTkEntry(self.frame_gestao, placeholder_text="Nome (ex: Videos)", width=150)
        self.entry_nome.grid(row=1, column=0, padx=5, pady=10)
        
        self.entry_ext = ctk.CTkEntry(self.frame_gestao, placeholder_text="Extensões (.mp4, .mkv)", width=200)
        self.entry_ext.grid(row=1, column=1, padx=5, pady=10)
        
        self.btn_salvar = ctk.CTkButton(self.frame_gestao, text="Salvar", width=80, fg_color="blue", command=self.salvar_categoria)
        self.btn_salvar.grid(row=1, column=2, padx=5, pady=10)

        # --- UI: Lista de Categorias ---
        self.lista_txt = ctk.CTkTextbox(self, height=120)
        self.lista_txt.pack(pady=10, padx=20, fill="x")

        # --- UI: Seleção e Exclusão ---
        self.frame_acoes_cat = ctk.CTkFrame(self)
        self.frame_acoes_cat.pack(pady=10, padx=20, fill="x")

        self.combo_categorias = ctk.CTkComboBox(self.frame_acoes_cat, values=list(self.categorias.keys()), width=200)
        self.combo_categorias.grid(row=0, column=0, padx=10, pady=10)

        self.btn_excluir = ctk.CTkButton(self.frame_acoes_cat, text="Excluir Categoria", fg_color="#922b21", hover_color="#7b241c", command=self.excluir_categoria)
        self.btn_excluir.grid(row=0, column=1, padx=10, pady=10)

        self.btn_abrir = ctk.CTkButton(self.frame_acoes_cat, text="Abrir Pasta", width=100, command=self.abrir_pasta_categoria)
        self.btn_abrir.grid(row=0, column=2, padx=10, pady=10)

        # --- UI: Ação Principal ---
        self.btn_selecionar = ctk.CTkButton(self, text="1. Selecionar Pasta no PC", height=40, command=self.escolher_pasta)
        self.btn_selecionar.pack(pady=10)

        self.btn_organizar = ctk.CTkButton(self, text="2. ORGANIZAR E GERAR RELATÓRIO", height=50, fg_color="green", state="disabled", command=self.executar_organizacao)
        self.btn_organizar.pack(pady=20)

        self.atualizar_lista_interface()

    def carregar_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.categorias = json.load(f)
        else:
            self.categorias = {"Documentos": [".pdf", ".docx"], "Imagens": [".jpg", ".png", ".webp"]}
            self.salvar_config_json()

    def salvar_config_json(self):
        with open(self.config_file, "w") as f:
            json.dump(self.categorias, f, indent=4)

    def salvar_categoria(self):
        nome = self.entry_nome.get().strip()
        exts = self.entry_ext.get().replace(" ", "").lower().split(",")
        if nome and exts != ['']:
            self.categorias[nome] = exts
            self.salvar_config_json()
            self.atualizar_lista_interface()
            messagebox.showinfo("Sucesso", f"Categoria '{nome}' salva/editada!")
        else:
            messagebox.showwarning("Aviso", "Preencha o nome e as extensões corretamente.")

    def excluir_categoria(self):
        cat = self.combo_categorias.get()
        if cat in self.categorias:
            confirmar = messagebox.askyesno("Confirmar", f"Deseja excluir a categoria '{cat}'?\n(Isso não apagará seus arquivos, apenas a regra)")
            if confirmar:
                del self.categorias[cat]
                self.salvar_config_json()
                self.atualizar_lista_interface()
                messagebox.showinfo("Sucesso", "Categoria removida!")

    def atualizar_lista_interface(self):
        # Atualiza a caixa de texto
        self.lista_txt.configure(state="normal")
        self.lista_txt.delete("1.0", "end")
        for cat, exts in self.categorias.items():
            self.lista_txt.insert("end", f"📂 {cat}: {', '.join(exts)}\n")
        self.lista_txt.configure(state="disabled")
        # Atualiza o menu de seleção
        self.combo_categorias.configure(values=list(self.categorias.keys()))
        if self.categorias:
            self.combo_categorias.set(list(self.categorias.keys())[0])

    def escolher_pasta(self):
        self.diretorio_selecionado = filedialog.askdirectory()
        if self.diretorio_selecionado:
            self.btn_organizar.configure(state="normal")

    def abrir_pasta_categoria(self):
        cat = self.combo_categorias.get()
        if self.diretorio_selecionado:
            caminho = os.path.join(self.diretorio_selecionado, cat)
            if os.path.exists(caminho):
                os.startfile(caminho)
            else:
                messagebox.showwarning("Erro", "Essa pasta ainda não foi criada nesta pasta.")
        else:
            messagebox.showwarning("Erro", "Selecione a pasta principal primeiro.")

    def gerar_pdf(self, total_movidos):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "Relatório de Organização", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        pdf.ln(10)
        pdf.cell(200, 10, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
        pdf.cell(200, 10, f"Total movidos: {total_movidos}", ln=True)
        pdf.ln(5)
        
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(95, 10, "Arquivo", border=1, fill=True)
        pdf.cell(95, 10, "Destino", border=1, ln=True, fill=True)
        
        for item in self.historico_movimentacao:
            nome_curto = (item['arquivo'][:40] + '..') if len(item['arquivo']) > 40 else item['arquivo']
            pdf.cell(95, 10, nome_curto, border=1)
            pdf.cell(95, 10, item['destino'], border=1, ln=True)
            
        nome_relatorio = f"Relatorio_{datetime.now().strftime('%H%M%S')}.pdf"
        pdf.output(os.path.join(self.diretorio_selecionado, nome_relatorio))
        return nome_relatorio

    def executar_organizacao(self):
        self.historico_movimentacao = []
        arquivos = os.listdir(self.diretorio_selecionado)
        total = 0

        for arquivo in arquivos:
            caminho_completo = os.path.join(self.diretorio_selecionado, arquivo)
            if os.path.isfile(caminho_completo):
                ext = os.path.splitext(arquivo)[1].lower()
                for pasta, exts in self.categorias.items():
                    if ext in exts:
                        dest = os.path.join(self.diretorio_selecionado, pasta)
                        os.makedirs(dest, exist_ok=True)
                        shutil.move(caminho_completo, os.path.join(dest, arquivo))
                        self.historico_movimentacao.append({'arquivo': arquivo, 'destino': pasta})
                        total += 1
                        break
        
        if total > 0:
            rel = self.gerar_pdf(total)
            messagebox.showinfo("Sucesso", f"{total} arquivos organizados!\nRelatório: {rel}")
        else:
            messagebox.showinfo("Aviso", "Nada para organizar nesta pasta.")

if __name__ == "__main__":
    app = App()
    app.mainloop()