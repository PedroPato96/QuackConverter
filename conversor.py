import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
from pillow_heif import register_heif_opener
import fitz  # PyMuPDF

# Registrar suporte para HEIF/HEIC
register_heif_opener()

# Função para selecionar imagens manualmente
def selecionar_imagens():
    global lista_arquivos
    arquivos = filedialog.askopenfilenames(filetypes=[("Imagens", "*.png;*.jpeg;*.bmp;*.gif;*.heic;*.heif;*.jpg;*.pdf")])
    if arquivos:
        lista_arquivos = arquivos
        entrada_var.set("\n".join(arquivos))

# Função para converter as imagens
def converter_imagens():
    if not lista_arquivos:
        messagebox.showerror("Erro", "Selecione pelo menos uma imagem ou PDF!")
        return

    formato_saida = formato_var.get()
    qualidade = qualidade_var.get()

    # Escolher a pasta de destino
    pasta_destino = filedialog.askdirectory()
    if not pasta_destino:
        return

    progresso["value"] = 0
    total = len(lista_arquivos)
    erros = []  # Lista para armazenar arquivos que falharam

    for i, arquivo in enumerate(lista_arquivos):
        try:
            nome_base = os.path.basename(arquivo).split('.')[0]

            if arquivo.lower().endswith(".pdf"):
                # Converter todas as páginas do PDF para imagens usando PyMuPDF
                doc = fitz.open(arquivo)
                for pagina_num in range(doc.page_count):
                    pagina = doc.load_page(pagina_num)
                    imagem = pagina.get_pixmap()
                    caminho_saida = os.path.join(pasta_destino, f"{nome_base}_pagina{pagina_num + 1}.{formato_saida}")
                    imagem.save(caminho_saida)
            else:
                # Converter imagens
                caminho_saida = os.path.join(pasta_destino, f"{nome_base}.{formato_saida}")
                img = Image.open(arquivo)
                if formato_saida == "jpeg" or formato_saida == "jpg":
                    img.convert("RGB").save(caminho_saida, format="JPEG", quality=qualidade)
                elif formato_saida == "pdf":
                    img.convert("RGB").save(caminho_saida, format="PDF")
                else:
                    img.save(caminho_saida, format=formato_saida.upper())

            progresso["value"] = ((i + 1) / total) * 100
            root.update_idletasks()

        except Exception as e:
            erros.append(f"{arquivo}: {str(e)}")

    if erros:
        erro_msg = "\n".join(erros)
        messagebox.showwarning("Algumas conversões falharam", f"Os seguintes arquivos não foram convertidos:\n{erro_msg}")
    else:
        messagebox.showinfo("Sucesso", f"{total} arquivos convertidos e salvos em {pasta_destino}!")

# Criar janela
root = tk.Tk()
root.title("Conversor de Imagens e PDFs")
root.geometry("600x500")
root.config(bg="#f5f5f5")

# Variáveis
entrada_var = tk.StringVar()
formato_var = tk.StringVar(value="png")
qualidade_var = tk.IntVar(value=90)
lista_arquivos = []

# Adicionar estilo ao botão
button_style = {'font': ('Arial', 12, 'bold'), 'bg': '#4CAF50', 'fg': 'white', 'relief': 'flat', 'width': 15, 'height': 2, 'bd': 0, 'highlightthickness': 0, 'cursor': 'hand2'}
entry_style = {'font': ('Arial', 10), 'bg': '#eaeaea', 'relief': 'solid', 'bd': 1, 'width': 60, 'highlightthickness': 0, 'borderwidth': 0}

# Widgets
header_label = tk.Label(root, text="Conversor de Imagens e PDFs", font=("Arial", 16, 'bold'), bg="#4CAF50", fg="white", height=2)
header_label.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)

tk.Label(root, text="Selecione os arquivos de imagem ou PDF:", font=("Arial", 10), bg="#f5f5f5").grid(row=1, column=0, padx=10, pady=5, sticky="w")
tk.Entry(root, textvariable=entrada_var, state="readonly", **entry_style).grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
tk.Button(root, text="Procurar Arquivos", command=selecionar_imagens, **button_style).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Escolha do formato de saída
tk.Label(root, text="Escolha o formato de saída:", font=("Arial", 10), bg="#f5f5f5").grid(row=4, column=0, padx=10, pady=5, sticky="w")
formatos_suportados = ["png", "jpeg", "bmp", "gif", "pdf", "jpg"]
formato_menu = ttk.Combobox(root, textvariable=formato_var, values=formatos_suportados, state="readonly", font=("Arial", 10), width=17)
formato_menu.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

# Controle de qualidade para JPEG
tk.Label(root, text="Qualidade (JPEG)", font=("Arial", 10), bg="#f5f5f5").grid(row=6, column=0, padx=10, pady=5, sticky="w")
tk.Scale(root, from_=10, to=100, orient="horizontal", variable=qualidade_var, sliderlength=20, length=300).grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

# Barra de progresso
progresso = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", maximum=100)
progresso.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

tk.Button(root, text="Converter", command=converter_imagens, **button_style).grid(row=9, column=0, columnspan=2, padx=10, pady=20)

# Texto de copyright com sticky=se
footer_label = tk.Label(root, text="© 2025 Pato.inc. Todos os direitos reservados.", font=("Arial", 8), fg="gray", bg="#f5f5f5")
footer_label.grid(row=10, column=0, columnspan=2, pady=10, sticky="s")

# Configuração de redimensionamento da janela
root.grid_rowconfigure(0, weight=0)
root.grid_rowconfigure(1, weight=0)
root.grid_rowconfigure(2, weight=1, minsize=40)
root.grid_rowconfigure(3, weight=0)
root.grid_rowconfigure(4, weight=0)
root.grid_rowconfigure(5, weight=0)
root.grid_rowconfigure(6, weight=0)
root.grid_rowconfigure(7, weight=0)
root.grid_rowconfigure(8, weight=0)
root.grid_rowconfigure(9, weight=0)
root.grid_rowconfigure(10, weight=0)  # Garantir que a última linha do copyright tenha peso 0

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Definir altura mínima para a janela para garantir que o copyright seja visível
root.minsize(600, 600)

# Rodar aplicação
root.mainloop()
