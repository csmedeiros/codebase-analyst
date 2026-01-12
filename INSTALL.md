# Guia de Instalação - Codebase Analyst

Este guia explica como instalar e configurar o **Codebase Analyst Agent** em seu sistema (Mac, Windows ou Linux).

## Requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)
- Chave de API da OpenAI

## Instalação

### Opção 1: Instalação via pip (Modo de Desenvolvimento)

Esta é a forma recomendada se você quiser modificar o código ou contribuir.

#### No Mac/Linux:

```bash
# 1. Clone ou navegue até o diretório do projeto
cd "/seu/diretorio/codebase-analyst"

# 2. (Opcional) Crie e ative um ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instale o pacote em modo desenvolvimento
pip install -e .

# Ou instale diretamente
pip install .
```

### No Windows (PowerShell ou CMD):

```powershell
# Navegue até o diretório
cd "C:\caminho\para\codebase-analyst"

# Crie um ambiente virtual (recomendado)
python -m venv venv
.\venv\Scripts\activate

# Instale o pacote
pip install -e .

# Ou instale diretamente
pip install .
```

### Instalação Global (Sistema)

Se você quiser instalar globalmente (não recomendado, use ambientes virtuais):

```bash
# Mac/Linux
sudo pip install -e .

# Windows (como Administrador)
pip install -e .
```

## 3. Configuração

### 3.1. Obter Chave da API OpenAI

1. Acesse [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Crie uma nova chave API
3. Copie a chave (começa com `sk-...`)

### 3.2 Configurar a Chave da API

Você tem duas opções:

**Opção 1: Arquivo .env (Recomendado)**

Crie um arquivo `.env` no diretório do projeto ou na sua pasta home:

```bash
# Mac/Linux
echo "OPENAI_API_KEY=sk-sua-chave-aqui" > ~/.codebase-analyst.env

# Windows (PowerShell)
echo "OPENAI_API_KEY=sk-sua-chave-aqui" > ~\.codebase-analyst.env
```

Ou copie o arquivo de exemplo:
```bash
cp .env.example .env
# Depois edite o arquivo .env com sua chave
```

**Opção 2: Variável de Ambiente**

Mac/Linux:
```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

Windows (CMD):
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

Para tornar permanente, adicione ao seu arquivo de perfil (~/.bashrc, ~/.zshrc, ou variáveis de ambiente do Windows).

## Uso

Após a instalação, você pode executar o `codebase-analyst` de qualquer diretório:

### Sintaxe Básica

```bash
codebase-analyst [CAMINHO] [OPÇÕES]
```

### Exemplos

```bash
# Analisar o diretório atual
codebase-analyst .

# Analisar um projeto específico
codebase-analyst ~/projetos/meu-app --task analyze

# Gerar README.md
codebase-analyst ./meu-projeto --task readme

# Gerar documentação de arquitetura
codebase-analyst ./meu-projeto --task architecture

# Usar um modelo diferente
codebase-analyst ./meu-projeto --task analyze --model gpt-4o

# Analisar qualquer pasta de qualquer lugar
cd ~/Documents
codebase-analyst ~/Projects/meu-app --task readme
```

### Opções Disponíveis

```
codebase-analyst [CAMINHO] [OPÇÕES]

Argumentos:
  path                  Caminho do repositório (default: diretório atual)

Opções:
  --task TASK          Tipo de análise: analyze, readme, architecture (default: analyze)
  --model MODEL        Modelo OpenAI (default: gpt-4o-mini)
  --version            Mostra a versão do programa
  --help               Mostra esta mensagem de ajuda
```

## Tarefas Disponíveis

### 1. analyze (padrão)
Analisa a codebase e fornece um resumo técnico completo.

```bash
codebase-analyst ./meu-projeto --task analyze
```

### 2. readme
Gera um arquivo README.md profissional na raiz do projeto.

```bash
codebase-analyst ./meu-projeto --task readme
```

### 3. architecture
Documenta a arquitetura do sistema em um arquivo ARCHITECTURE.md.

```bash
codebase-analyst ./meu-projeto --task architecture
```

## Exemplos de Uso

### Analisar o diretório atual
```bash
codebase-analyst .
```

### Analisar um projeto específico
```bash
codebase-analyst /caminho/para/seu/projeto
```

### Gerar README.md profissional
```bash
codebase-analyst ./meu-projeto --task readme
```

### Documentar arquitetura do sistema
```bash
codebase-analyst ./meu-projeto --task architecture
```

### Usar modelo GPT-4
```bash
codebase-analyst ./meu-projeto --task analyze --model gpt-4o
```

## Funcionalidades

- Análise completa de codebases
- Geração automática de README.md profissional
- Documentação de arquitetura do sistema
- Interface CLI com output estilizado
- Streaming em tempo real da execução do agente
- Compatível com Mac, Windows e Linux
- Funciona em qualquer diretório após instalação

## Estrutura do Pacote

```
codebase-analyst/
├── src/
│   ├── __init__.py       # Inicialização do pacote
│   ├── cli.py            # Interface CLI (entry point)
│   ├── agent.py          # Criação e configuração do agente
│   ├── tools.py          # Ferramentas do agente (file system)
│   └── prompts.py        # System prompts e instruções
├── setup.py              # Configuração de instalação (setuptools)
├── pyproject.toml        # Configuração moderna de empacotamento
├── requirements.txt      # Dependências
├── MANIFEST.in           # Arquivos adicionais a incluir no pacote
├── .env.example          # Exemplo de configuração de ambiente
└── README.md             # Documentação do projeto
```

## Requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)
- Chave de API da OpenAI
- Conexão com a internet

## Instalação

### Passo 1: Clone ou baixe o projeto

```bash
cd "Code Base Agent/codebase-analyst"
```

### Passo 2: Criar ambiente virtual (recomendado)

#### No Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### No Windows:
```cmd
python -m venv venv
venv\Scripts\activate
```

### Passo 3: Instalar o pacote

Há duas formas de instalar:

#### Opção A: Instalação em modo de desenvolvimento (recomendado para desenvolvimento)
```bash
pip install -e .
```

#### Opção B: Instalação normal
```bash
pip install .
```

### Passo 4: Configurar a API Key da OpenAI

Crie um arquivo `.env` na sua pasta home ou no diretório do projeto:

```bash
# Copiar o template
cp .env.example .env

# Editar e adicionar sua chave
# OPENAI_API_KEY=sk-sua-chave-aqui
```

Ou exporte como variável de ambiente:

**Mac/Linux:**
```bash
export OPENAI_API_KEY=sk-sua-chave-aqui
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-sua-chave-aqui"
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=sk-sua-chave-aqui
```

Para tornar permanente no Windows, adicione às variáveis de ambiente do sistema.

## Uso

Após a instalação, o comando `codebase-analyst` estará disponível globalmente no seu terminal:

### Exemplos básicos:

```bash
# Analisar o diretório atual
codebase-analyst .

# Analisar um projeto específico
codebase-analyst /caminho/para/projeto

# Gerar README.md
codebase-analyst /caminho/para/projeto --task readme

# Documentar arquitetura
codebase-analyst /caminho/para/projeto --task architecture

# Usar um modelo diferente
codebase-analyst . --task analyze --model gpt-4o
```

### Opções disponíveis:

- `path`: Caminho do repositório a analisar (padrão: diretório atual)
- `--task`: Tipo de análise
  - `analyze`: Resumo técnico completo (padrão)
  - `readme`: Gera README.md profissional
  - `architecture`: Documenta a arquitetura em ARCHITECTURE.md
- `--model`: Modelo OpenAI a usar (padrão: `gpt-4o-mini`)
  - Opções: `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`, etc.
- `--version`: Mostra a versão do codebase-analyst
- `--help`: Mostra ajuda completa

## Compatibilidade

- **Python**: 3.9 ou superior
- **Sistemas Operacionais**:
  - macOS (testado)
  - Windows 10/11
  - Linux (todas as distribuições modernas)

O código usa `pathlib` para garantir compatibilidade entre diferentes sistemas operacionais.

## Desinstalação

Para desinstalar o pacote:

```bash
pip uninstall codebase-analyst
```

## Troubleshooting

### Erro: "OPENAI_API_KEY não encontrada"

Certifique-se de que configurou a variável de ambiente corretamente:

1. Verifique se o arquivo `.env` existe e contém a chave
2. Ou exporte a variável no terminal antes de executar
3. No Windows, verifique as variáveis de ambiente do sistema

### Erro: "comando não encontrado: codebase-analyst"

1. Certifique-se de que instalou o pacote: `pip install -e .`
2. Verifique se o diretório de scripts do Python está no PATH
3. Tente usar: `python -m src.cli` como alternativa

### Erro de permissão no Windows

Execute o terminal como Administrador ao instalar o pacote.

### Problemas com caminhos no Windows

O código usa `pathlib.Path` que converte automaticamente entre formatos de caminho. Use barras normais `/` ou duplas barras invertidas `\\` em strings.

## Desenvolvimento

Para contribuir ou modificar o código:

1. Clone o repositório
2. Instale em modo de desenvolvimento: `pip install -e .`
3. Faça suas modificações
4. O comando será atualizado automaticamente (modo editable)

## Suporte

Para problemas ou dúvidas:
- Verifique a documentação no README.md
- Abra uma issue no repositório do projeto
- Consulte a documentação da OpenAI: https://platform.openai.com/docs
