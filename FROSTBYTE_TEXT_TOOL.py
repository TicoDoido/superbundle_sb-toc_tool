import os
import struct
import tkinter as tk
from tkinter import filedialog

def definir_endianness(file):
    # Ler os primeiros 4 bytes (magic)
    file.seek(0)
    magic = file.read(4)
    
    if magic == b'\x00\x90\x03\x00':
        return 'little'  # Little Endian
    elif magic == b'\x00\x03\x90\x00':
        return 'big'  # Big Endian
    else:
        raise ValueError("Magic number não reconhecido. O arquivo pode estar corrompido ou não suportado.")

def extrair_dados(filename):
    with open(filename, 'rb') as file:
        # Definir endianness
        endianness = definir_endianness(file)

        # Ler total de ponteiros na posição 8
        file.seek(8)
        total_ponteiros = int.from_bytes(file.read(4), endianness)
        print(f"Total de ponteiros: {total_ponteiros:08X}")

        # Ler posição inicial dos ponteiros na posição 12
        file.seek(12)
        pos_ponteiros = int.from_bytes(file.read(4), endianness)
        print(f"Posição inicial dos ponteiros: {pos_ponteiros:08X}")
        
        # Posição onde começam os textos
        file.seek(16)
        inicio_bloco = int.from_bytes(file.read(4), endianness)

        # Somar 8 à posição inicial dos ponteiros
        ponteiros_real = pos_ponteiros + 8
        print(f"Posição real dos ponteiros: {ponteiros_real:08X}")

        # Ir para a posição dos ponteiros
        file.seek(ponteiros_real)

        # Armazenar todos os ponteiros em uma lista
        ponteiros = []
        for _ in range(total_ponteiros):
            # Pular 4 bytes
            file.seek(4, os.SEEK_CUR)

            # Ler o valor do ponteiro (4 bytes)
            ponteiro = int.from_bytes(file.read(4), endianness)
            ponteiros.append(ponteiro)

        # Definir o nome do arquivo de saída
        output_filename = filename + '.txt'

        # Abrir arquivo para salvar todos os dados extraídos
        with open(output_filename, 'wb') as output_file:
            # Processar cada ponteiro
            for i, ponteiro in enumerate(ponteiros):

                # Calcular a posição real do ponteiro
                ponteiro_real = ponteiro + inicio_bloco + 8  # valor na posição + 8 bytes

                # Ir para o valor apontado pelo ponteiro real
                file.seek(ponteiro_real)

                # Ler dados até encontrar um byte 00
                dados = b""
                while True:
                    byte = file.read(1)
                    if byte == b'\x00':
                        break
                    dados += byte

                # Salvar os dados extraídos no arquivo
                output_file.write(dados)
                output_file.write(b'[fim]\n')  # Adiciona um delimitador entre conjuntos de dados

        print(f'Todos os dados foram salvos em {output_filename}')

def recriar_arquivo(filename):
    # Nome do arquivo .txt correspondente
    txt_filename = filename + '.txt'

    # Ler o cabeçalho do arquivo original
    with open(filename, 'rb') as file:
        # Definir endianness
        endianness = definir_endianness(file)

        # Ler o valor na posição 16 (4 bytes Little Endian ou Big Endian)
        file.seek(16)
        tamanho_cabecalho = int.from_bytes(file.read(4), endianness) + 8

        # Ler o cabeçalho completo
        file.seek(0)
        cabecalho = file.read(tamanho_cabecalho)

        # Ler a posição inicial dos ponteiros na posição 12
        file.seek(12)
        pos_ponteiros = int.from_bytes(file.read(4), endianness)

    # Ler a conteúdo do arquivo .txt em modo binário
    with open(txt_filename, 'rb') as txt_file:
        conteudo_txt = txt_file.read()

    # Dividir o conteúdo entre [fim]\n e remover o último item
    partes = conteudo_txt.split(b'[fim]\n')
    partes.pop()  # Remover o último item que é vazio

    # Criar o novo arquivo
    novo_filename = 'novo_' + os.path.basename(filename)
    with open(novo_filename, 'wb') as novo_arquivo:
        # Escrever o cabeçalho no novo arquivo
        novo_arquivo.write(cabecalho)

        # Escrever o conteúdo do .txt no novo arquivo e guardar os ponteiros
        ponteiros = []
        for parte in partes:
            ponteiros.append(novo_arquivo.tell())
            novo_arquivo.write(parte)
            novo_arquivo.write(b'\x00')
        
        novo_tamanho = novo_arquivo.tell() - 8
        
        novo_arquivo.seek(4)
        
        # Verificar a ordem dos bytes e usar o formato correto para o struct
        if endianness == 'little':
            novo_arquivo.write(struct.pack('<I', novo_tamanho))
        else:
            novo_arquivo.write(struct.pack('>I', novo_tamanho))
        
        # Atualizar a posição dos ponteiros
        novo_arquivo.seek(pos_ponteiros + 8)

        # Escrever os valores dos ponteiros
        for ponteiro in ponteiros:
            # Subtrair tamanho_cabecalho do valor do ponteiro
            ponteiro_ajustado = ponteiro - tamanho_cabecalho
            print(f"Escrevendo ponteiro ajustado: {ponteiro_ajustado:08X}")

            # Pular 4 bytes
            novo_arquivo.seek(4, os.SEEK_CUR)

            # Verificar a ordem dos bytes e usar o formato correto para o struct
            if endianness == 'little':
                novo_arquivo.write(struct.pack('<I', ponteiro_ajustado))
            else:
                novo_arquivo.write(struct.pack('>I', ponteiro_ajustado))

    print(f'Novo arquivo criado: {novo_filename}')  

# Função chamada pelo botão para escolher o arquivo
def escolher_arquivo():
    filename = filedialog.askopenfilename(title="Escolha o arquivo", filetypes=[("Arquivos binários", "*.bin *.chunk"), ("Todos os arquivos", "*.*")])
    if filename:
        extrair_dados(filename)
        
# Função chamada pelo botão para recriar o arquivo
def escolher_arquivo_recriar():
    filename = filedialog.askopenfilename(title="Escolha o arquivo original", filetypes=[("Arquivos binários", "*.bin *.chunk"), ("Todos os arquivos", "*.*")])
    if filename:
        recriar_arquivo(filename)        

# Configurando a interface gráfica principal
def criar_interface():
    root = tk.Tk()
    root.title("Extrator/Reconstrutor de Textos FROSTBYTE")
    root.geometry("400x150")
    root.resizable(False, False)
    
    # Botão para escolher o arquivo
    btn_escolher_arquivo = tk.Button(root, text="Escolher Arquivo para extrair o texto", command=escolher_arquivo)
    btn_escolher_arquivo.pack(pady=20)
    
    # Botão para escolher o arquivo e recriar
    btn_recriar_arquivo = tk.Button(root, text="Recriar Arquivo binário de texto", command=escolher_arquivo_recriar)
    btn_recriar_arquivo.pack(pady=20)

    # Mantém a janela aberta
    root.mainloop()

# Executar a interface gráfica
criar_interface()
