# SB/TOC Extractor N Rebuilder   

## Introdução  
Este programa foi desenvolvido para gerenciar arquivos do tipo `.toc` e `.sb`,  
possibilitando a extração, descompressão, compressão e remontagem de chunks de dados.  
O software também lida com a encriptação e descriptografia de arquivos `.toc`,    
além de oferecer uma interface gráfica amigável para facilitar sua utilização.  

## Requisitos  
- Python 3.7 ou superior  
- Biblioteca `tkinter` (geralmente incluída por padrão no Python)  
- Biblioteca `zlib` (incluída no Python)  

## Funcionalidades Principais  

### 1. Extração de Arquivos do SB  
- Seleciona o arquivo `.toc` correspondente ao `.sb`.  
- Realiza a descriptografia automática do arquivo `.toc`, se necessário.  
- Extrai os chunks do arquivo `.sb` com base nos dados do `.toc` e os salva em uma pasta com o nome do arquivo `.toc`.  

### 2. Remontagem de Arquivos SB  
- Permite selecionar uma pasta contendo chunks extraídos.   
- Reconstrói o arquivo `.sb` a partir dos chunks e atualiza os offsets e tamanhos no arquivo `.toc`.  
- Recriptografa o arquivo `.toc` após a atualização.  

### 3. Descompressão de Chunk  
- Seleciona um arquivo chunk (`.bin`) e descomprime seus dados usando a biblioteca `zlib`.  
- Substitui o arquivo chunk original pelo arquivo descomprimido.  

### 4. Compressão de Chunk  
- Seleciona um arquivo chunk (`.bin`) e comprime seus dados em blocos de 64 KB usando a biblioteca `zlib`.  
- Substitui o arquivo chunk original pelo arquivo comprimido.  

## Como Usar  

### Interface Gráfica  
1. **Inicie o programa**:  
   Execute o script Python. Uma janela será aberta com as opções disponíveis.  

2. **Extração de Arquivos**:  
   - Clique em "Selecionar .toc (Extrair)".  
   - Escolha um arquivo `.toc`. O programa localizará automaticamente o arquivo `.sb` correspondente e realizará a extração dos chunks.  

3. **Remontagem de Arquivos**:  
   - Clique em "Selecionar pasta (Remontar)".  
   - Escolha a pasta contendo os chunks extraídos e, em seguida, selecione o nome e a
   - localização do arquivo `.sb` a ser reconstruído. O arquivo `.toc` será atualizado automaticamente.

4. **Descompressão de Chunk**:  
   - Clique em "Descomprimir Chunk".  
   - Escolha o arquivo chunk (`.bin`) a ser descomprimido.  

5. **Compressão de Chunk**:  
   - Clique em "Comprimir Chunk".  
   - Escolha o arquivo chunk (`.bin`) a ser comprimido.  

### Operações Automáticas  
- **Descriptografia do TOC**:  
   - O programa detecta automaticamente se o arquivo `.toc` está criptografado e realiza a descriptografia antes de extrair os dados.  
- **Atualização do TOC**:  
   - Durante a remontagem, os offsets e tamanhos no `.toc` são atualizados para refletir os novos chunks no `.sb`.  

## Estrutura de Arquivos  

### Formato `.toc`  
- **Bytes Importantes**:  
  - `magic` (4 bytes): Identifica o arquivo `.toc`.   
  - `hash_data` (256 bytes): Dados de hash usados para validação.  
  - `xor_table` (257 bytes): Tabela de XOR para encriptação/descriptografia.  
  - `bundles`: Estrutura que define os offsets e tamanhos dos chunks no arquivo `.sb`.  

### Formato `.sb`  
- Contém os chunks de dados comprimidos.  

## Observações  
1. **Desempenho**:  
   - O programa foi projetado para processar arquivos grandes, mas o tempo de execução  
   - pode variar dependendo do tamanho dos arquivos e da quantidade de chunks.  
2. **Integridade dos Arquivos**:  
   - Faça backups dos arquivos originais antes de usar o programa para evitar perda de dados.  

## Erros Comuns  
- **Erro ao Descomprimir Chunk**:  
  - Certifique-se de que o arquivo chunk foi comprimido usando o mesmo método.  
- **Erro ao Atualizar TOC**:  
  - Verifique se os arquivos chunks estão nomeados corretamente e em ordem.  

## Licença  
Este programa é fornecido "como está", sem garantia de qualquer tipo. O uso é por conta e risco do usuário.  

