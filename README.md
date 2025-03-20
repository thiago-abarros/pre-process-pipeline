# pre-process-pipeline

O PDF Processing Pipeline é uma ferramenta abrangente para processamento de documentos PDF com OCR (Reconhecimento Óptico de Caracteres). Este pipeline oferece uma solução completa para:

1. **Conversão de PDF para Imagens**: Transforma documentos PDF em imagens de alta qualidade.
2. **OCR Automatizado**: Utiliza PaddleOCR para detectar e reconhecer texto nas imagens.
3. **Criação de Dataset**: Gera datasets no formato compatível com o Label Studio para revisão, correção ou anotação manual.
4. **Integração com Label Studio**: Configuração automática de um ambiente para visualizar e editar os resultados do OCR.

## Contexto e Propósito

Este repositório foi desenvolvido especificamente para auxiliar na criação de dados para treinamento de modelos de reconhecimento de layout de documentos (Document Layout Recognition - DLR) e na geração de datasets rotulados para sistemas de extração de informações textuais.

Ao transformar documentos em imagens anotadas com coordenadas precisas de cada elemento textual, este pipeline facilita:

- **Treinamento de modelos DLR**: Criação de datasets estruturados para ensinar modelos a reconhecerem a organização espacial de documentos, incluindo tabelas, parágrafos, cabeçalhos e rodapés.
- **Extração de informações**: Identificação e rotulagem de campos específicos em documentos (como datas, nomes, valores) para treinamento de modelos de extração de informações.
- **Aprimoramento de algoritmos OCR**: Geração de dados de referência para avaliar e melhorar algoritmos de OCR em diferentes tipos de documentos.

Este repositório é ideal para qualquer projeto que necessite extrair texto estruturado de documentos digitalizados ou PDFs.

## Guia de Instalação

### Pré-requisitos

- Python 3.12 ou superior
- Pip (gerenciador de pacotes Python)
- Git

### Passos de Instalação

1. **Clone o repositório**

   ```bash
   git clone https://github.com/yourusername/pre-process-pipeline.git
   cd pre-process-pipeline
   ```

2. **Configure o ambiente virtual e instale as dependências**

   Você pode escolher entre dois métodos para configurar seu ambiente:

   #### Método 1: Usando virtualenv tradicional (venv)

   ```bash
   # No Windows
   python -m venv venv
   venv\Scripts\activate
   pip install -e .

   # No Linux/macOS
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

   #### Método 2: Usando UV (mais rápido)

   O [UV](https://github.com/astral-sh/uv) é uma alternativa moderna e mais rápida para gerenciamento de ambientes Python, escrita em Rust.

   ```bash
   # Instale o UV, se ainda não tiver instalado
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # No Windows (PowerShell)
   # Baixe e instale UV a partir de https://github.com/astral-sh/uv/releases

   # Crie o ambiente virtual e instale as dependências em um único comando
   uv venv
   
   # Ative o ambiente (Windows)
   .venv\Scripts\activate
   
   # Ative o ambiente (Linux/macOS)
   source .venv/bin/activate
   
   # Instale as dependências
   uv pip install -e .
   ```

   Com UV, a instalação das dependências será significativamente mais rápida que com pip tradicional.

   Ambos os métodos instalarão todas as dependências listadas no arquivo `pyproject.toml`, incluindo:
   - PyMuPDF (fitz)
   - PaddleOCR e suas dependências
   - Label Studio
   - Outras bibliotecas necessárias

## Guia de Utilização

### Parte 1: Processamento de PDFs

O script `pre-process-pipeline.py` realiza a conversão de PDFs para imagens e executa OCR para detecção de texto.

1. **Estrutura de diretórios recomendada**

   Crie uma pasta `pdfs` no diretório raiz do projeto para armazenar os arquivos PDF que deseja processar:

   ```bash
   mkdir -p pdfs
   ```

2. **Copie seus arquivos PDF para a pasta**

   Coloque os arquivos PDF que deseja processar na pasta `pdfs/`.

3. **Execute o script de processamento**

   Para processar todos os PDFs na pasta:

   ```bash
   python pre-process-pipeline.py pdfs/
   ```

   Para processar um único arquivo PDF:

   ```bash
   python pre-process-pipeline.py pdfs/seu-arquivo.pdf
   ```

4. **Resultados do processamento**

   O script criará:
   - Uma pasta `image/` contendo as imagens extraídas de cada página dos PDFs
   - Um arquivo JSON com os resultados do OCR no formato compatível com Label Studio

### Parte 2: Visualização e Edição no Label Studio

Para visualizar e editar os resultados do OCR, você pode usar o script `start_services.py`, que inicia um servidor HTTP para hospedar as imagens e o Label Studio.

1. **Execute o script de serviços**

   ```bash
   python start_services.py
   ```

   Este comando iniciará:
   - Um servidor HTTP na porta 8080 para servir as imagens
   - O Label Studio na porta 8081

2. **Acesse o Label Studio**

   Abra seu navegador e acesse:

   ```
   http://localhost:8081
   ```

3. **Configure um novo projeto no Label Studio**

   - Clique em "Create Project"
   - Dê um nome ao seu projeto (ex: "OCR Review")
   - Em "Labeling Setup", escolha a opção "Optical Character Recognition"
   - Clique em "Save"

4. **Importe o dataset gerado**

   - No seu projeto, vá para a aba "Import"
   - Selecione "Upload Files"
   - Escolha o arquivo JSON gerado (normalmente tem o nome `[nome-da-pasta]_label-studio.json` ou `label_studio_dataset.json`)
   - Clique em "Import"

5. **Revise e edite o texto reconhecido**

   - As imagens das páginas dos PDFs serão exibidas com caixas de texto delimitando o texto reconhecido
   - Você pode editar o texto reconhecido, mover as caixas ou adicionar novas anotações
   - Ao terminar de revisar cada imagem, clique em "Submit" para salvar as alterações

6. **Exporte os resultados finais**

   - Vá para a aba "Export"
   - Escolha o formato desejado (JSON, CSV, etc.)
   - Clique em "Export" para baixar os resultados finais

7. **Encerre os serviços**

   Para encerrar os serviços, pressione CTRL+C no terminal onde o script `start_services.py` está em execução.

## Dicas e Troubleshooting

- **Qualidade do OCR**: A qualidade dos resultados do OCR depende da qualidade dos PDFs originais. PDFs com texto nítido e bem formatado tendem a ter melhores resultados.

- **DPI das imagens**: Por padrão, as imagens são extraídas com 300 DPI. Você pode alterar este valor editando o parâmetro `dpi` na chamada da função `convert_pdf_to_images` no script.

- **Problemas de conexão**: Se estiver tendo problemas para acessar as imagens no Label Studio, verifique se os dois serviços (HTTP server e Label Studio) estão rodando corretamente.

- **Erros de OCR**: O PaddleOCR pode enfrentar dificuldades com certas fontes ou layouts complexos. Nestes casos, a revisão manual no Label Studio é essencial.

- **Pasta de imagens**: As imagens geradas são armazenadas na pasta `image/` com subdiretórios correspondentes aos nomes dos arquivos PDF.

## Conclusão

Este pipeline oferece uma solução completa para processamento de PDFs com OCR e revisão dos resultados. Com a integração do Label Studio, você pode facilmente corrigir erros do OCR e exportar os resultados para uso em aplicações subsequentes.

Os datasets gerados são particularmente valiosos para:
- Treinar modelos personalizados de reconhecimento de layout de documentos
- Desenvolver sistemas de extração de informação específicos para seus tipos de documentos
- Criar datasets de referência para avaliar e comparar diferentes modelos de OCR e extração de texto

Ao combinar a automação do processo de OCR com ferramentas intuitivas para revisão manual, este pipeline reduz significativamente o tempo e esforço necessários para construir datasets de alta qualidade para tarefas de processamento de documentos.
