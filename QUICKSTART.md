# Quick Start Guide

Comece a usar o Codebase Analyst em menos de 5 minutos!

## 1. Pré-requisitos (2 minutos)

### Instalar Python
- **Mac**: Já vem instalado ou use `brew install python3`
- **Windows**: Baixe em [python.org](https://python.org)
- **Linux**: `sudo apt install python3 python3-pip` (Debian/Ubuntu)

### Obter Chave da OpenAI
1. Acesse: https://platform.openai.com/api-keys
2. Clique em "Create new secret key"
3. Copie a chave (começa com `sk-...`)

## 2. Instalação (2 minutos)

### Mac/Linux

```bash
# Entre na pasta
cd "Code Base Agent/codebase-analyst"

# Execute o instalador
chmod +x install.sh
./install.sh

# Configure a API key
export OPENAI_API_KEY=sk-sua-chave-aqui
```

### Windows

```cmd
REM Entre na pasta
cd "Code Base Agent\codebase-analyst"

REM Execute o instalador
install.bat

REM Configure a API key
set OPENAI_API_KEY=sk-sua-chave-aqui
```

## 3. Primeiro Uso (1 minuto)

### Testar o comando

```bash
codebase-analyst --help
```

### Analisar um projeto

```bash
# Analisar o diretório atual
codebase-analyst .

# Analisar outro projeto
codebase-analyst /caminho/do/projeto
```

## Exemplos Práticos

### Gerar README.md Profissional

```bash
codebase-analyst ~/meu-projeto --task readme
```

Isso vai:
1. Verificar se README.md já existe (e pedir confirmação se existir) 🛡️
2. Analisar toda a estrutura do código
3. Identificar tecnologias e padrões
4. Criar um README.md na raiz do projeto

**Nota**: Se README.md já existir, você será perguntado se deseja sobrescrever!

### Documentar Arquitetura

```bash
codebase-analyst ~/meu-projeto --task architecture
```

Gera um arquivo `ARCHITECTURE.md` com:
- Estrutura do sistema
- Fluxo de dados
- Componentes principais
- Diagramas ASCII

### Análise Completa

```bash
codebase-analyst ~/meu-projeto --task analyze
```

Fornece um resumo técnico completo no terminal.

## Dicas

### Usar Modelo Mais Potente

```bash
codebase-analyst . --task readme --model gpt-4o
```

### Analisar de Qualquer Lugar

Após instalação, funciona de qualquer diretório:

```bash
cd ~/Documents
codebase-analyst ~/Projects/app --task analyze
```

### Tornar a API Key Permanente

**Mac/Linux** - Adicione ao `~/.bashrc` ou `~/.zshrc`:
```bash
export OPENAI_API_KEY=sk-sua-chave-aqui
```

**Windows** - Adicione às variáveis de ambiente:
1. Pesquise "variáveis de ambiente" no menu Iniciar
2. Clique em "Variáveis de Ambiente"
3. Adicione `OPENAI_API_KEY` com sua chave

## Troubleshooting Rápido

### "comando não encontrado: codebase-analyst"

```bash
# Reinstale o pacote
pip install -e .
```

### "OPENAI_API_KEY não encontrada"

```bash
# Verifique se está definida
echo $OPENAI_API_KEY  # Mac/Linux
echo %OPENAI_API_KEY%  # Windows

# Se vazia, configure novamente
export OPENAI_API_KEY=sk-sua-chave-aqui
```

### Erro de permissão (Windows)

Execute o CMD ou PowerShell como Administrador.

## Próximos Passos

- Leia o [README.md](README.md) completo
- Veja o [INSTALL.md](INSTALL.md) para instalação avançada
- Explore as opções com `codebase-analyst --help`

---

**Pronto!** Você está apto a analisar qualquer codebase! 🚀
