# Codebase Analyst Agent

**Versão 1.1.5**

Um agente inteligente de análise de código construído com LangChain e LangGraph. O agente navega em repositórios de código, analisa sua estrutura e gera documentação automaticamente.

Execute de qualquer diretório após instalação!

## Funcionalidades

- **Análise de Codebase**: Explora a estrutura do projeto e fornece um resumo técnico completo
- **Geração de Onboarding**: Cria documentação ONBOARDING.md profissional baseada na análise do código
- **Documentação de Arquitetura**: Documenta a arquitetura do sistema em detalhes
- **Gerenciamento de Contexto**: SummarizationMiddleware para compressão automática de contexto
- **Proteção de Sobrescrita**: Detecta arquivos existentes e solicita confirmação antes de sobrescrever
- **CLI Instalável**: Execute de qualquer pasta após instalação
- **Cross-Platform**: Compatível com Mac, Windows e Linux
- **Multi-Provider**: Suporte a 7 provedores de LLM (OpenAI, Anthropic, Groq, Google, Cohere, Mistral, Together AI)

## Requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)
- Chave de API de pelo menos um provedor LLM suportado (OpenAI, Anthropic, Groq, Google, etc.)

## Instalação Rápida

### Opção 1: Script Automático (Recomendado)

**Mac/Linux:**
```bash
cd codebase-analyst
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
cd codebase-analyst
install.bat
```

### Opção 2: Instalação Manual

**1. Navegue até a pasta do projeto:**
```bash
cd codebase-analyst
```

**2. (Opcional) Crie um ambiente virtual:**
```bash
# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Instale o pacote:**
```bash
pip install -e .
```

## Configuração

### Obter Chaves de API

O agente suporta múltiplos provedores de LLM. Escolha pelo menos um:

**OpenAI:**
1. Acesse [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Crie uma nova chave API
3. Copie a chave (começa com `sk-...`)

**Anthropic (Claude):**
1. Acesse [https://console.anthropic.com/](https://console.anthropic.com/)
2. Crie uma chave API
3. Copie a chave

**Groq:**
1. Acesse [https://console.groq.com/](https://console.groq.com/)
2. Crie uma chave API
3. Copie a chave

**Google (Gemini):**
1. Acesse [https://ai.google.dev/](https://ai.google.dev/)
2. Obtenha uma chave API
3. Copie a chave

### Configurar as Chaves

**Opção 1: Arquivo .env (Recomendado)**
```bash
# Copie o template
cp .env.example .env

# Edite o arquivo .env e adicione as chaves dos provedores que você vai usar:
# OPENAI_API_KEY=sk-sua-chave-aqui
# ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
# GROQ_API_KEY=gsk_sua-chave-aqui
# GOOGLE_API_KEY=sua-chave-aqui
```

**Opção 2: Variáveis de Ambiente**
```bash
# Mac/Linux
export OPENAI_API_KEY=sk-sua-chave-aqui
export ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
export GROQ_API_KEY=gsk_sua-chave-aqui

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-sua-chave-aqui"
$env:ANTHROPIC_API_KEY="sk-ant-sua-chave-aqui"
$env:GROQ_API_KEY="gsk_sua-chave-aqui"

# Windows (CMD)
set OPENAI_API_KEY=sk-sua-chave-aqui
set ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
set GROQ_API_KEY=gsk_sua-chave-aqui
```

## Uso

Após a instalação, o comando `codebase-analyst` estará disponível globalmente:

### Sintaxe Básica

```bash
codebase-analyst [CAMINHO] [OPÇÕES]
```

### Exemplos

**Analisar o diretório atual:**
```bash
codebase-analyst .
```

**Analisar um projeto específico:**
```bash
codebase-analyst ~/projetos/meu-app
```

**Gerar ONBOARDING.md:**
```bash
codebase-analyst ./meu-projeto --task onboarding
```
```

**Usar diferentes modelos e provedores:**
```bash
# OpenAI GPT-4
codebase-analyst ./meu-projeto --model openai:gpt-4o

# Anthropic Claude
codebase-analyst ./meu-projeto --model anthropic:claude-3-5-sonnet-20241022

# Groq Llama
codebase-analyst ./meu-projeto --model groq:llama-3.3-70b-versatile

# Google Gemini
codebase-analyst ./meu-projeto --model google:gemini-2.0-flash-exp

# Modelo sem especificar provedor (usa OpenAI por padrão)
codebase-analyst ./meu-projeto --model gpt-4o
```

**Analisar qualquer pasta de qualquer lugar:**
```bash
cd ~/Documents
codebase-analyst ~/Projects/meu-app --task readme --model anthropic:claude-3-5-sonnet-20241022
```

### Opções Disponíveis

| Opção | Descrição | Padrão |
|-------|-----------|--------|
| `path` | Caminho do repositório a analisar | `.` (diretório atual) |
| `--task` | Tipo de tarefa: `analyze`, `readme`, `architecture` | `analyze` |
| `--model` | Modelo no formato `provider:model` ou apenas `model`<br>Exemplos: `openai:gpt-4o`, `anthropic:claude-3-5-sonnet-20241022`,<br>`groq:llama-3.3-70b-versatile`, `google:gemini-2.0-flash-exp` | `gpt-4o-mini` |
| `--version` | Mostra a versão do programa | - |
| `--help` | Mostra mensagem de ajuda | - |

### Provedores Suportados

| Provedor | Formato | Variável de Ambiente | Exemplo de Modelo |
|----------|---------|---------------------|-------------------|
| OpenAI | `openai:model` | `OPENAI_API_KEY` | `openai:gpt-4o` |
| Anthropic | `anthropic:model` | `ANTHROPIC_API_KEY` | `anthropic:claude-3-5-sonnet-20241022` |
| Groq | `groq:model` | `GROQ_API_KEY` | `groq:llama-3.3-70b-versatile` |
| Google | `google:model` | `GOOGLE_API_KEY` | `google:gemini-2.0-flash-exp` |
| Cohere | `cohere:model` | `COHERE_API_KEY` | `cohere:command-r-plus` |
| Mistral | `mistral:model` | `MISTRAL_API_KEY` | `mistral:mistral-large-latest` |
| Together AI | `together:model` | `TOGETHER_API_KEY` | `together:meta-llama/Llama-3-70b-chat-hf` |

## Proteção de Sobrescrita

O Codebase Analyst protege seus arquivos existentes! 🛡️

Quando você executa tarefas que geram arquivos (`--task readme` ou `--task architecture`), o CLI automaticamente:

1. **Detecta** se o arquivo já existe no diretório
2. **Mostra informações** sobre o arquivo existente (caminho, tamanho, data de modificação)
3. **Solicita confirmação** antes de continuar
4. **Preserva o arquivo** se você não confirmar

### Exemplo

```bash
$ codebase-analyst ./meu-projeto --task readme

⚠ Aviso: O arquivo 'README.md' já existe no diretório!

Arquivo:     /caminho/para/meu-projeto/README.md
Tamanho:     2048 bytes
Modificado:  2026-01-12 08:30:45

Este arquivo será SOBRESCRITO se você continuar.

Deseja continuar e sobrescrever o arquivo? [s/N]:
```

**Opções de resposta:**
- Digite `s`, `sim`, `y` ou `yes` para sobrescrever
- Digite `n`, `não` ou pressione Enter para **cancelar** (padrão)
- Pressione Ctrl+C para cancelar

### Arquivos Protegidos

| Tarefa | Arquivo Protegido |
|--------|-------------------|
| `--task readme` | `README.md` |
| `--task architecture` | `ARCHITECTURE.md` |
| `--task analyze` | Nenhum (não cria arquivos) |

> 📖 **Documentação completa**: Veja [FEATURE_OVERWRITE_PROTECTION.md](FEATURE_OVERWRITE_PROTECTION.md) para mais detalhes

## Estrutura do Projeto

```
codebase-analyst/
├── src/
│   ├── __init__.py          # Inicialização do pacote (v1.1.5)
│   ├── agent.py             # Configuração do agente LangGraph
│   ├── cli.py               # Entry point CLI principal
│   ├── tools.py             # Ferramentas do agente (list_dir, read_file, write_file, remove_draft_file)
│   ├── prompts.py           # Prompts do agente
│   ├── summarization.py     # SummarizationMiddleware para gerenciamento de contexto
│   └── system_prompt.md     # System prompt detalhado do agente
├── main.py                  # Entry point alternativo
├── pyproject.toml           # Configuração moderna do pacote Python
├── setup.py                 # Configuração de instalação
├── requirements.txt         # Dependências do projeto
├── install.sh / install.bat # Scripts de instalação automática
└── README.md                # Este arquivo
```

## Ferramentas do Agente

O agente possui quatro ferramentas para interagir com o sistema de arquivos:

### `list_dir(path)`
Lista o conteúdo de um diretório, mostrando arquivos e subdiretórios com prefixos `[FILE]` e `[DIR]`.

### `read_file(path, start, end)`
Lê o conteúdo de um arquivo de texto, opcionalmente apenas um intervalo de linhas.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `path` | str | Caminho do arquivo a ser lido |
| `start` | int | Linha inicial (1-indexed para input, padrão: 1) |
| `end` | int \| None | Linha final (1-indexed para input, inclusive). Se omitido, lê até o final |

O retorno inclui números de linha estilo VS Code (0-indexed, alinhados à esquerda) no formato `N     conteúdo` e um header com o total de linhas do arquivo.

**Exemplo de uso pelo agente:**
```python
# Ler primeiras 50 linhas
read_file("src/main.py", start=1, end=50)

# Ler linhas 100-200
read_file("src/main.py", start=100, end=200)

# Ler arquivo inteiro
read_file("DRAFT.md")
```

### `write_file(path, content)`
Cria ou sobrescreve arquivos, criando diretórios pai automaticamente se necessário.

### `remove_draft_file(path)`
Remove o arquivo DRAFT.md (usado internamente pelo agente para memória de trabalho).

## Arquitetura

O projeto utiliza:

- **LangChain**: Framework para construção de aplicações com LLMs
- **LangGraph**: Biblioteca para criação de agentes com grafos de estado
- **Multi-Provider LLM**: Suporte a OpenAI, Anthropic, Groq, Google, Cohere, Mistral e Together AI
- **Rich**: Interface de terminal com formatação rica
- **SummarizationMiddleware**: Gerenciamento inteligente de contexto para evitar overflow de tokens
- **pathlib**: Manipulação cross-platform de caminhos de arquivo

## Notas Técnicas

- Todas as operações de arquivo usam `pathlib` para compatibilidade cross-platform
- Encoding UTF-8 é usado em todas as operações de leitura/escrita
- O agente usa temperatura baixa (0.1) para outputs mais consistentes
- Streaming está habilitado para visualizar o progresso em tempo real
- SummarizationMiddleware comprime contexto antigo quando próximo do limite de tokens
- Fluxo de trabalho em duas fases: exploração + análise profunda

## Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para histórico completo de versões.

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.