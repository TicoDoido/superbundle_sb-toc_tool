import os
import zlib
import tkinter as tk
from tkinter import filedialog, messagebox

CHUNK_SIZE = 64 * 1024  # 64 KB

def decrypt_chunk_file(chunk_path):
    try:
        with open(chunk_path, 'rb') as chunk_file:
            chunk_data = chunk_file.read()

        decompressed_data = bytearray()
        position = 0

        while position < len(chunk_data):
            position += 4
            if position >= len(chunk_data):
                break

            decompressed_size = int.from_bytes(chunk_data[position:position + 4], byteorder='big')
            position += 4
            if position >= len(chunk_data):
                break

            compressed_data = chunk_data[position:position + decompressed_size]
            position += decompressed_size

            try:
                decompressed_piece = zlib.decompress(compressed_data)
                decompressed_data.extend(decompressed_piece)
            except zlib.error as e:
                messagebox.showerror("Erro de Descompressão", f"Erro ao descomprimir o pedaço do chunk {os.path.basename(chunk_path)}: {e}")
                return

        with open(chunk_path, 'wb') as decompressed_file:
            decompressed_file.write(decompressed_data)

        messagebox.showinfo("Sucesso", f"O chunk {os.path.basename(chunk_path)} foi descomprimido com sucesso e substituiu o original.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao descomprimir o chunk: {str(e)}")

def compress_chunk_file(chunk_path):
    try:
        with open(chunk_path, 'rb') as chunk_file:
            decompressed_data = chunk_file.read()

        compressed_data = bytearray()
        position = 0

        while position < len(decompressed_data):
            part = decompressed_data[position:position + CHUNK_SIZE]
            decompressed_size = len(part)
            compressed_part = zlib.compress(part, level=9)
            compressed_size = len(compressed_part)

            # Adiciona os tamanhos descomprimido e comprimido e a parte comprimida ao resultado final
            compressed_data.extend(decompressed_size.to_bytes(4, byteorder='big'))
            compressed_data.extend(compressed_size.to_bytes(4, byteorder='big'))
            compressed_data.extend(compressed_part)

            position += CHUNK_SIZE

        with open(chunk_path, 'wb') as compressed_file:
            compressed_file.write(compressed_data)

        messagebox.showinfo("Sucesso", f"O chunk {os.path.basename(chunk_path)} foi comprimido com sucesso e substituiu o original.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao comprimir o chunk: {str(e)}")


def encrypt_decrypt_toc_file(file_path, decrypt=True):
    try:
        with open(file_path, 'rb') as file:
            toc_bytes = bytearray(file.read())

        magic = toc_bytes[:4]
        if magic == b'\x00\xd1\xce\x00' or magic == b'\x00\xd1\xce\x01':
        # Código a ser executado se magic corresponder a um dos valores

            hash_data = toc_bytes[8:8+256]
            xor_table = toc_bytes[296:296+257]
            data = toc_bytes[556:]

            for i in range(len(data)):
                data[i] = data[i] ^ xor_table[i % 257] ^ 0x7b

            toc_bytes[556:] = data

            with open(file_path, 'wb') as file:
                file.write(toc_bytes)

            if decrypt:
                messagebox.showinfo("Sucesso", "Descriptografia concluída")
            else:
                messagebox.showinfo("Sucesso", "Encriptação concluída")
        else:
            messagebox.showerror("Erro", "Não é um arquivo .toc válido ou suportado")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

def extract_files_from_sb(toc_path, sb_path):
    output_dir = os.path.splitext(os.path.basename(toc_path))[0]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(toc_path, 'rb') as toc_file:
        toc_data = toc_file.read()
    
    if b'bundles' not in toc_data:
        encrypt_decrypt_toc_file(toc_path, decrypt=True)
        with open(toc_path, 'rb') as toc_file:
            toc_data = toc_file.read()

    file_chunks = []
    
    position = toc_data.find(b'bundles')
    while position != -1:
        position = toc_data.find(b'id', position)
        if position == -1:
            break

        position = toc_data.find(b'offset', position)
        position += 7
        offset = int.from_bytes(toc_data[position:position+4], 'little')
        
        position = toc_data.find(b'size', position)
        position += 5
        size = int.from_bytes(toc_data[position:position+4], 'little')
        
        file_chunks.append((offset, size))

    for chunk_index, (offset, size) in enumerate(file_chunks):
        with open(sb_path, 'rb') as sb_file:
            sb_file.seek(offset)
            chunk_data = sb_file.read(size)

            chunk_filename = os.path.join(output_dir, f'compressed_chunk_{chunk_index + 1}_{offset}.bin')
            with open(chunk_filename, 'wb') as chunk_file:
                chunk_file.write(chunk_data)

    messagebox.showinfo("Processo Concluído", f"A extração foi concluída com sucesso. Arquivos salvos em {output_dir}.")

def rebuild_sb_from_chunks(input_dir, sb_path, toc_path):
    try:
        toc_updated = False
        chunks = sorted([f for f in os.listdir(input_dir) if f.startswith('compressed_chunk_')],
                        key=lambda x: int(x.split('_')[2]))

        with open(sb_path, 'wb') as sb_file:
            offsets_and_sizes = []
            for chunk_filename in chunks:
                chunk_path = os.path.join(input_dir, chunk_filename)
                with open(chunk_path, 'rb') as chunk_file:
                    chunk_data = chunk_file.read()

                    offset = sb_file.tell()
                    sb_file.write(chunk_data)
                    chunk_size = len(chunk_data)

                    offsets_and_sizes.append((offset, chunk_size))

            toc_updated = update_toc_with_new_offsets(toc_path, offsets_and_sizes)

        if toc_updated:
            encrypt_decrypt_toc_file(toc_path, decrypt=False)  # Recriptografa o TOC
            messagebox.showinfo("Processo Concluído", f"O arquivo .sb foi reconstruído com sucesso em {sb_path} e o TOC foi atualizado e recriptografado.")
        else:
            messagebox.showwarning("Aviso", "O arquivo .sb foi reconstruído, mas o TOC não pôde ser atualizado.")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao reconstruir o arquivo .sb: {str(e)}")

def update_toc_with_new_offsets(toc_path, offsets_and_sizes):
    try:
        with open(toc_path, 'r+b') as toc_file:
            toc_data = bytearray(toc_file.read())

            position = toc_data.find(b'bundles')
            chunk_index = 0

            while position != -1 and chunk_index < len(offsets_and_sizes):
                position = toc_data.find(b'id', position)
                if position == -1:
                    break

                position = toc_data.find(b'offset', position)
                if position == -1:
                    break

                position += 7
                new_offset = offsets_and_sizes[chunk_index][0]
                toc_data[position:position+4] = new_offset.to_bytes(4, 'little')

                position = toc_data.find(b'size', position)
                if position == -1:
                    break

                position += 5
                new_size = offsets_and_sizes[chunk_index][1]
                toc_data[position:position+4] = new_size.to_bytes(4, 'little')

                chunk_index += 1

            toc_file.seek(0)
            toc_file.write(toc_data)
        return True

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao atualizar o TOC: {str(e)}")
        return False

def select_toc_file():
    toc_path = filedialog.askopenfilename(filetypes=[("TOC Files", "*.toc")])
    if toc_path:
        sb_path = toc_path.replace('.toc', '.sb')
        if os.path.exists(sb_path):
            extract_files_from_sb(toc_path, sb_path)
        else:
            messagebox.showerror("Erro", "O arquivo .sb correspondente não foi encontrado.")

def select_output_dir():
    output_dir = filedialog.askdirectory(title="Selecione a pasta de saída")
    if output_dir:
        sb_path = filedialog.asksaveasfilename(defaultextension=".sb", filetypes=[("SB Files", "*.sb")])
        toc_path = sb_path.replace('.sb', '.toc')
        if sb_path and toc_path:
            rebuild_sb_from_chunks(output_dir, sb_path, toc_path)
            
def select_chunk_file():
    chunk_path = filedialog.askopenfilename(filetypes=[("Chunk Files", "*.bin")])
    if chunk_path:
        decrypt_chunk_file(chunk_path)            
        
def select_chunk_file_for_compression():
    chunk_path = filedialog.askopenfilename(filetypes=[("Chunk Files", "*.bin")])
    if chunk_path:
        compress_chunk_file(chunk_path)

def create_gui():
    root = tk.Tk()
    root.title("SB/TOC Extractor N Rebuilder")
    root.geometry("350x200")
    root.resizable(False, False)

    label = tk.Label(root, text="Escolha uma das opções")
    label.place(x=100, y=20)

    button_extract = tk.Button(root, text="Selecionar .toc(Extrair)", command=select_toc_file)
    button_extract.place(x=30, y=60)

    button_rebuild = tk.Button(root, text="Selecionar pasta(Remontar)", command=select_output_dir)
    button_rebuild.place(x=200, y=60)

    button_decompress = tk.Button(root, text="Descomprimir Chunk", command=select_chunk_file)
    button_decompress.place(x=30, y=100)

    button_compress = tk.Button(root, text="Comprimir Chunk", command=select_chunk_file_for_compression)
    button_compress.place(x=200, y=100)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
