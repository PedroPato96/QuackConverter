# -*- coding: utf-8 -*-
"""
QuackConverter - Conversor de Imagens e PDFs
Versão: Alpha 2.0.0
Autor: Pedro Silveira Ricardo
Copyright © 2024-2025 Pedro Silveira Ricardo. Todos os direitos reservados.

Descrição:
Aplicativo em Tkinter para converter imagens (PNG, JPG, HEIC, etc.) e PDFs
com opções de corte e ajuste de qualidade. Suporte para conversão em lote
com possibilidade de combinar tudo em um único PDF ou salvar separadamente.

Licença: Uso pessoal e não comercial. Distribuição proibida sem autorização.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import sys
from pillow_heif import register_heif_opener
import fitz  # PyMuPDF
import ctypes

register_heif_opener()

if getattr(sys, 'frozen', False):
    caminho_icone = os.path.join(sys._MEIPASS, "logo.ico")
else:
    caminho_icone = "C:/Users/techhelp/Documents/GitHub/ImgConverterAppTest/logo.ico"

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ImgConverterApp")

root = tk.Tk()
root.title("Conversor de Imagens e PDFs")
root.iconbitmap(caminho_icone)

largura_janela = 450
altura_janela = 570
largura_tela = root.winfo_screenwidth()
altura_tela = root.winfo_screenheight()
pos_x = (largura_tela - largura_janela) // 2
pos_y = (altura_tela - altura_janela) // 2
root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")
root.resizable(False, False)
root.configure(bg="#f5f5f5")

estilo_botoes = {
    "font": ("Arial", 10, "bold"),
    "bg": "#4CAF50",
    "fg": "white",
    "bd": 2,
    "relief": "raised",
    "activebackground": "#45a049",
    "activeforeground": "white",
    "cursor": "hand2"
}

entrada_var = tk.StringVar()
formato_var = tk.StringVar(value="png")
qualidade_var = tk.IntVar(value=90)
cortar_var = tk.BooleanVar(value=False)
corte_manual_var = tk.BooleanVar(value=False)
um_pdf_var = tk.BooleanVar(value=False)
nome_arquivo_var = tk.StringVar()
lista_arquivos = []

def mostrar_previa(imagem, titulo="Prévia do Corte"):
    previa = tk.Toplevel()
    previa.title(titulo)
    img = imagem.copy()
    img.thumbnail((600, 600))
    tk_img = ImageTk.PhotoImage(img)
    canvas = tk.Canvas(previa, width=tk_img.width(), height=tk_img.height())
    canvas.pack()
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img
    return previa

def selecionar_imagens():
    global lista_arquivos
    arquivos = filedialog.askopenfilenames(filetypes=[("Imagens", "*.png;*.jpeg;*.bmp;*.gif;*.heic;*.heif;*.jpg;*.pdf")])
    if arquivos:
        lista_arquivos = arquivos
        entrada_var.set("\n".join(arquivos))

def cortar_para_quadrado(imagem):
    largura, altura = imagem.size
    tamanho = min(largura, altura)
    esquerda = (largura - tamanho) // 2
    topo = (altura - tamanho) // 2
    direita = esquerda + tamanho
    base = topo + tamanho
    cortada = imagem.crop((esquerda, topo, direita, base))
    janela = mostrar_previa(cortada, "Prévia do Corte Automático")
    resposta = messagebox.askyesno("Confirmar Corte", "Aplicar este corte?")
    janela.destroy()
    return cortada if resposta else imagem

def cortar_manual(imagem):
    from PIL import ImageTk

    win = tk.Toplevel()
    win.title("Corte Manual")
    img_tk = ImageTk.PhotoImage(imagem)

    canvas = tk.Canvas(win, width=imagem.width, height=imagem.height, cursor="cross")
    canvas.pack()
    canvas.create_image(0, 0, anchor="nw", image=img_tk)

    rect_id = None
    handles = {}
    dragging_handle = None
    selecao = {"x0": None, "y0": None, "x1": None, "y1": None}

    handle_size = 6

    def draw_handles(x0, y0, x1, y1):
        nonlocal handles
        for handle in handles.values():
            canvas.delete(handle)
        handles = {}

        # Canto inferior direito apenas (pode expandir para todos depois)
        handles["br"] = canvas.create_rectangle(
            x1 - handle_size, y1 - handle_size, x1 + handle_size, y1 + handle_size,
            fill="red", tags="handle"
        )

    def on_mouse_down(event):
        nonlocal rect_id, dragging_handle

        if rect_id is not None:
            # Verifica se clicou em um handle
            x, y = event.x, event.y
            coords = canvas.coords(rect_id)
            x0, y0, x1, y1 = coords

            hx, hy = x1, y1
            if abs(x - hx) < 10 and abs(y - hy) < 10:
                dragging_handle = "br"
                return

            return  # Ignora outras áreas

        selecao["x0"] = event.x
        selecao["y0"] = event.y
        rect_id = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red", width=2)

    def on_mouse_drag(event):
        nonlocal rect_id
        if dragging_handle == "br":
            selecao["x1"] = event.x
            selecao["y1"] = event.y
            canvas.coords(rect_id, selecao["x0"], selecao["y0"], selecao["x1"], selecao["y1"])
            draw_handles(selecao["x0"], selecao["y0"], selecao["x1"], selecao["y1"])
        elif rect_id and selecao["x0"] is not None:
            selecao["x1"] = event.x
            selecao["y1"] = event.y
            canvas.coords(rect_id, selecao["x0"], selecao["y0"], selecao["x1"], selecao["y1"])
            draw_handles(selecao["x0"], selecao["y0"], selecao["x1"], selecao["y1"])

    def on_mouse_up(event):
        nonlocal dragging_handle
        dragging_handle = None

    def confirmar():
        if rect_id and all(selecao[k] is not None for k in ["x0", "y0", "x1", "y1"]):
            win.destroy()
        else:
            messagebox.showwarning("Aviso", "Selecione uma área antes de confirmar.")

    canvas.bind("<Button-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

    tk.Button(win, text="Confirmar corte", command=confirmar).pack(pady=10)

    root.wait_window(win)

    if all(selecao[k] is not None for k in ["x0", "y0", "x1", "y1"]):
        box = (
            min(selecao["x0"], selecao["x1"]),
            min(selecao["y0"], selecao["y1"]),
            max(selecao["x0"], selecao["x1"]),
            max(selecao["y0"], selecao["y1"]),
        )
        return imagem.crop(box)

    return imagem

def ao_alterar_um_pdf():
    if um_pdf_var.get():
        formato_var.set("pdf")
        formato_menu.config(state="disabled")
        nome_arquivo_entry.config(state="normal")
    else:
        formato_menu.config(state="readonly")
        nome_arquivo_entry.config(state="disabled")
        nome_arquivo_var.set("")

def ao_alterar_corte():
    if cortar_var.get():
        corte_manual_var.set(False)
    elif corte_manual_var.get():
        cortar_var.set(False)

def converter_imagens():
    if not lista_arquivos:
        messagebox.showerror("Erro", "Selecione pelo menos uma imagem ou PDF!")
        return

    formato_saida = formato_var.get()
    qualidade = qualidade_var.get()
    cortar = cortar_var.get()
    corte_manual = corte_manual_var.get()
    nome_arquivo_final = nome_arquivo_var.get().strip()

    if um_pdf_var.get() and not nome_arquivo_final:
        messagebox.showerror("Erro", "Digite um nome para o arquivo final PDF.")
        return

    pasta_destino = filedialog.askdirectory()
    if not pasta_destino:
        return

    progresso["value"] = 0
    total = len(lista_arquivos)
    erros = []
    imagens_para_pdf = []

    for i, arquivo in enumerate(lista_arquivos):
        try:
            nome_base = os.path.basename(arquivo).split('.')[0]

            if arquivo.lower().endswith(".pdf"):
                doc = fitz.open(arquivo)
                for pagina_num in range(doc.page_count):
                    pagina = doc.load_page(pagina_num)
                    imagem = pagina.get_pixmap()
                    img_pil = Image.frombytes("RGB", [imagem.width, imagem.height], imagem.samples)
                    if cortar:
                        img_pil = cortar_para_quadrado(img_pil)
                    elif corte_manual:
                        img_pil = cortar_manual(img_pil)
                    if um_pdf_var.get():
                        imagens_para_pdf.append(img_pil.convert("RGB"))
                    else:
                        caminho_saida = os.path.join(pasta_destino, f"{nome_base}_pagina{pagina_num + 1}.{formato_saida}")
                        img_pil.save(caminho_saida)
            else:
                img = Image.open(arquivo)
                if cortar:
                    img = cortar_para_quadrado(img)
                elif corte_manual:
                    img = cortar_manual(img)
                if um_pdf_var.get():
                    imagens_para_pdf.append(img.convert("RGB"))
                else:
                    caminho_saida = os.path.join(pasta_destino, f"{nome_base}.{formato_saida}")
                    if formato_saida in ["jpeg", "jpg"]:
                        img.convert("RGB").save(caminho_saida, format="JPEG", quality=qualidade)
                    elif formato_saida == "pdf":
                        img.convert("RGB").save(caminho_saida, format="PDF")
                    else:
                        img.save(caminho_saida, format=formato_saida.upper())

            progresso["value"] = ((i + 1) / total) * 100
            root.update_idletasks()

        except Exception as e:
            erros.append(f"{arquivo}: {str(e)}")

    if um_pdf_var.get() and imagens_para_pdf:
        caminho_pdf_final = os.path.join(pasta_destino, f"{nome_arquivo_final}.pdf")
        try:
            imagens_para_pdf[0].save(caminho_pdf_final, save_all=True, append_images=imagens_para_pdf[1:])
        except Exception as e:
            erros.append(f"Erro ao salvar PDF combinado: {str(e)}")

    if erros:
        erro_msg = "\n".join(erros)
        messagebox.showwarning("Algumas conversões falharam", f"Os seguintes arquivos não foram convertidos:\n{erro_msg}")
    else:
        messagebox.showinfo("Sucesso", f"{total} arquivos convertidos e salvos em {pasta_destino}!")
        os.startfile(pasta_destino)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

header_label = tk.Label(root, text="Conversor de Imagens e PDFs", font=("Arial", 16, 'bold'), bg="#4CAF50", fg="white", height=2)
header_label.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)

tk.Label(root, text="Selecione os arquivos:", font=("Arial", 10), bg="#f5f5f5").grid(row=1, column=0, padx=10, pady=5, sticky="w")
tk.Entry(root, textvariable=entrada_var, state="readonly").grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
tk.Button(root, text="Procurar Arquivos", command=selecionar_imagens, **estilo_botoes).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

tk.Label(root, text="Formato de saída:", font=("Arial", 10), bg="#f5f5f5").grid(row=4, column=0, padx=10, pady=5, sticky="w")
formatos_suportados = ["png", "jpeg", "bmp", "gif", "pdf", "jpg", "heif"]
formato_menu = ttk.Combobox(root, textvariable=formato_var, values=formatos_suportados, state="readonly", font=("Arial", 10))
formato_menu.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

cortar_check = tk.Checkbutton(root, text="Cortar em quadrado", variable=cortar_var, bg="#f5f5f5", command=ao_alterar_corte)
cortar_check.grid(row=6, column=0, sticky="w", padx=10)

corte_manual_check = tk.Checkbutton(root, text="Corte manual", variable=corte_manual_var, bg="#f5f5f5", command=ao_alterar_corte)
corte_manual_check.grid(row=6, column=1, sticky="w", padx=10)

um_pdf_check = tk.Checkbutton(root, text="Salvar tudo em um único PDF", variable=um_pdf_var, bg="#f5f5f5", command=ao_alterar_um_pdf)
um_pdf_check.grid(row=7, column=0, columnspan=2, sticky="w", padx=10)

tk.Label(root, text="Nome do arquivo final (se único PDF):", font=("Arial", 10), bg="#f5f5f5").grid(row=8, column=0, columnspan=2, padx=10, pady=5, sticky="w")
nome_arquivo_entry = tk.Entry(root, textvariable=nome_arquivo_var, state="disabled")
nome_arquivo_entry.grid(row=9, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

tk.Label(root, text="Qualidade de Imagem (Quanto maior, mais pesada):", font=("Arial", 10), bg="#f5f5f5").grid(row=10, column=0, columnspan=2, padx=10, pady=5, sticky="w")
qualidade_slider = tk.Scale(root, from_=10, to=100, orient="horizontal", variable=qualidade_var)
qualidade_slider.grid(row=11, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

progresso = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", maximum=100)
progresso.grid(row=12, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

tk.Button(root, text="Converter", command=converter_imagens, **estilo_botoes).grid(row=13, column=0, columnspan=2, padx=10, pady=20)

root.mainloop()
