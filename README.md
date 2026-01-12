# Codebase Analyst Agent

Um agente inteligente de análise de código construído com LangChain e LangGraph. O agente navega em repositórios de código, analisa sua estrutura e gera documentação automaticamente.

Execute de qualquer diretório após instalação!

## Funcionalidades

- **Análise de Codebase**: Explora a estrutura do projeto e fornece um resumo técnico completo
- **Geração de README**: Cria um README.md profissional baseado na análise do código
- **Documentação de Arquitetura**: Documenta a arquitetura do sistema em detalhes
- **Proteção de Sobrescrita**: Detecta arquivos existentes e solicita confirmação antes de sobrescrever
- **CLI Instalável**: Execute de qualquer pasta após instalação
- **Cross-Platform**: Compatível com Mac, Windows e Linux

## Requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)
- Chave de API da OpenAI

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

### Obter Chave da API OpenAI

1. Acesse [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Adicione saldo na API
3. Crie uma nova chave API
4. Copie a chave (começa com `sk-...`)

### Configurar a Chave

**Opção 1: Arquivo .env (Recomendado)**
```bash
# Copie o template
cp .env.example .env

# Edite o arquivo .env e adicione:
# OPENAI_API_KEY=sk-sua-chave-aqui
```

**Opção 2: Variável de Ambiente**
```bash
# Mac/Linux
export OPENAI_API_KEY=sk-sua-chave-aqui

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-sua-chave-aqui"

# Windows (CMD)
set OPENAI_API_KEY=sk-sua-chave-aqui
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

**Gerar README.md:**
```bash
codebase-analyst ./meu-projeto --task readme
```

**Documentar arquitetura:**
```bash
codebase-analyst ./meu-projeto --task architecture
```

**Usar modelo GPT-4:**
```bash
codebase-analyst ./meu-projeto --model gpt-4o
```

**Analisar qualquer pasta de qualquer lugar:**
```bash
cd ~/Documents
codebase-analyst ~/Projects/meu-app --task readme
```

### Opções Disponíveis

| Opção | Descrição | Padrão |
|-------|-----------|--------|
| `path` | Caminho do repositório a analisar | `.` (diretório atual) |
| `--task` | Tipo de tarefa: `analyze`, `readme`, `architecture` | `analyze` |
| `--model` | Modelo OpenAI a usar | `gpt-4o-mini` |
| `--version` | Mostra a versão do programa | - |
| `--help` | Mostra mensagem de ajuda | - |

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
│   ├── __init__.py       # Inicialização do pacote
│   ├── agent.py          # Configuração do agente LangGraph
│   ├── tools.py          # Ferramentas do agente (list_dir, read_file, write_file)
│   └── prompts.py        # System prompt do agente
├── main.py               # Entry point com CLI
├── requirements.txt      # Dependências do projeto
└── README.md             # Este arquivo
```

## Ferramentas do Agente

O agente possui três ferramentas para interagir com o sistema de arquivos:

### `list_dir(path)`
Lista o conteúdo de um diretório, mostrando arquivos e subdiretórios com prefixos `[FILE]` e `[DIR]`.

### `read_file(path, start, end)`
Lê o conteúdo de um arquivo de texto, opcionalmente apenas um intervalo de linhas.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `path` | str | Caminho do arquivo a ser lido |
| `start` | int | Linha inicial (1-indexed, padrão: 1) |
| `end` | int \| None | Linha final (1-indexed, inclusive). Se omitido, lê até o final |

O retorno inclui números de linha no formato `N: conteúdo` e um header com o total de linhas do arquivo.

**Exemplo de uso pelo agente:**
```python
# Ler primeiras 50 linhas
read_file("src/main.py", start=1, end=50)

# Ler linhas 100-200
read_file("src/main.py", start=100, end=200)

# Ler arquivo inteiro
read_file("README.md")
```

### `write_file(path, content)`
Cria ou sobrescreve arquivos, criando diretórios pai automaticamente se necessário.

## Arquitetura

O projeto utiliza:

- **LangChain**: Framework para construção de aplicações com LLMs
- **LangGraph**: Biblioteca para criação de agentes com grafos de estado
- **OpenAI API**: Modelos de linguagem para análise e geração de texto
- **pathlib**: Manipulação cross-platform de caminhos de arquivo

## Notas Técnicas

- Todas as operações de arquivo usam `pathlib` para compatibilidade cross-platform
- Encoding UTF-8 é usado em todas as operações de leitura/escrita
- O agente usa temperatura baixa (0.1) para outputs mais consistentes
- Streaming está habilitado para visualizar o progresso em tempo real