import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os

# Função para selecionar imagens manualmente
def selecionar_imagens():
    global lista_arquivos
    arquivos = filedialog.askopenfilenames(filetypes=[("Imagens", "*.png;*.jpeg;*.bmp;*.gif;*.pdf")])
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
        return  # Se o usuário cancelar, não faz nada

    progresso["value"] = 0  # Reseta a barra de progresso
    total = len(lista_arquivos)

    try:
        for i, arquivo in enumerate(lista_arquivos):
            nome_base = os.path.basename(arquivo).split('.')[0]  # Nome sem extensão
            caminho_saida = os.path.join(pasta_destino, f"{nome_base}.{formato_saida}")

            if arquivo.lower().endswith(".pdf"):
                # Converter PDF para imagens (apenas primeira página)
                from pdf2image import convert_from_path
                imagens = convert_from_path(arquivo)
                imagens[0].save(caminho_saida, format=formato_saida.upper())
            else:
                img = Image.open(arquivo)
                if formato_saida == "jpeg":  # Para JPEG, aplicamos a compressão de qualidade
                    img.convert("RGB").save(caminho_saida, format="JPEG", quality=qualidade)
                elif formato_saida == "pdf":
                    img.convert("RGB").save(caminho_saida, format="PDF")
                else:
                    img.save(caminho_saida, format=formato_saida.upper())

            # Atualiza a barra de progresso
            progresso["value"] = ((i + 1) / total) * 100
            root.update_idletasks()  # Atualiza a interface

        messagebox.showinfo("Sucesso", f"{total} arquivos convertidos e salvos em {pasta_destino}!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao converter: {str(e)}")

# Criar janela
root = tk.Tk()
root.title("Conversor de Imagens e PDFs")
root.geometry("500x500")

# Variáveis
entrada_var = tk.StringVar()
formato_var = tk.StringVar(value="png")  # Formato padrão
qualidade_var = tk.IntVar(value=90)  # Qualidade padrão (0 a 100)
lista_arquivos = []  # Lista de arquivos selecionados

# Widgets
tk.Label(root, text="Arraste e solte arquivos aqui ou clique para procurar:").pack(pady=5)
tk.Entry(root, textvariable=entrada_var, width=50, state="readonly").pack()
tk.Button(root, text="Procurar", command=selecionar_imagens).pack(pady=5)

# Escolha do formato de saída
tk.Label(root, text="Escolha o formato de saída:").pack(pady=5)
tk.OptionMenu(root, formato_var, "png", "jpeg", "bmp", "gif", "pdf").pack()

# Controle de qualidade para JPEG
tk.Label(root, text="Qualidade (JPEG)").pack(pady=5)
tk.Scale(root, from_=10, to=100, orient="horizontal", variable=qualidade_var).pack()

# Barra de progresso
progresso = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progresso.pack(pady=10)

tk.Button(root, text="Converter", command=converter_imagens, bg="green", fg="white").pack(pady=10)

# Texto de copyright
tk.Label(root, text="© 2025 Pato.inc. Todos os direitos reservados.", font=("Arial", 8), fg="gray").pack(side="bottom", pady=10)

# Rodar aplicação
root.mainloop()
