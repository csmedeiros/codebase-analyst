# CLAUDE.md - Contexto do Projeto para Claude Code

> Este arquivo fornece contexto essencial sobre o projeto Codebase Analyst para acelerar o onboarding em novas sessões do Claude Code.

## 📋 Visão Geral do Projeto

**Nome:** Codebase Analyst Agent
**Versão Atual:** 1.2.0
**Tipo:** Ferramenta CLI de análise de codebase com IA
**Stack Principal:** Python 3.9+, LangChain, LangGraph, Rich

## 🎯 Propósito

O Codebase Analyst é um agente de IA que analisa repositórios de código e gera documentação automática de onboarding (`ONBOARDING.md`) para ajudar novos desenvolvedores a entender rapidamente a estrutura e funcionamento de uma codebase.

## 🏗️ Arquitetura

### Componentes Principais

1. **CLI (`src/cli.py`)**: Interface de linha de comando
2. **Agent (`src/agent.py`)**: Configuração do agente LangGraph
3. **Tools (`src/tools.py`)**: Ferramentas do agente (list_dir, read_file, write_file, remove_draft_file)
4. **Prompts (`src/prompts/`)**: System prompts versionados
5. **Summarization (`src/summarization.py`)**: Middleware customizado para gerenciamento de contexto

### Fluxo de Trabalho do Agente

1. **Exploração**: Lista árvore de diretórios, identifica entry points
2. **Análise Profunda**: Lê arquivos-chave, mapeia arquitetura, identifica fluxos
3. **Documentação**: Escreve análise em `DRAFT.md`, depois gera `ONBOARDING.md`

## 🔧 Configurações Importantes

### Versionamento
- **Arquivos de versão:** `setup.py`, `pyproject.toml`, `src/__init__.py`, `src/cli.py`
- **Regra:** Sempre atualizar TODOS os arquivos ao fazer bump de versão
- **Formato:** Semantic Versioning (MAJOR.MINOR.PATCH)

### System Prompts
- **Localização:** `src/prompts/system_prompt_vX.X.X.md`
- **Versão Atual:** `system_prompt_v1.1.5.md`
- **Carregamento:** Dinâmico via `src/prompts.py:132`

### Modelo Padrão
- **Atual:** `anthropic:claude-sonnet-4-5`
- **Motivo:** Melhor performance em análises complexas, contextos maiores

### Observabilidade
- **Tracing:** Langfuse (opcional, via flag `--trace`)
- **Padrão:** Desabilitado para performance
- **Implementação:** Condicional em `cli.py:429-442` e `cli.py:460-461`

## 📁 Estrutura de Arquivos Críticos

```
codebase-analyst/
├── src/
│   ├── __init__.py          # __version__ = "X.X.X"
│   ├── agent.py             # create_codebase_agent()
│   ├── cli.py               # main(), version arg
│   ├── tools.py             # Ferramentas do agente
│   ├── prompts.py           # Carrega system_prompt_vX.X.X.md
│   ├── summarization.py     # SummarizationMiddleware customizado
│   └── prompts/
│       ├── system_prompt_v1.1.2.md
│       └── system_prompt_v1.1.5.md  # ATUAL
├── setup.py                 # version="X.X.X"
├── pyproject.toml           # version = "X.X.X"
├── README.md                # **Versão X.X.X**
├── CHANGELOG.md             # Histórico detalhado
└── requirements.txt         # Dependências
```

## 🚀 Features Recentes (v1.2.0)

### 1. Flag `--trace` para Observabilidade
- Tracing com Langfuse opcional
- Desabilitado por padrão (performance)
- Uso: `codebase-analyst ./projeto --trace`

### 2. Prompts Versionados
- System prompts organizados em `src/prompts/`
- Versionamento claro: `system_prompt_v1.1.5.md`
- Facilita evolução e rollback

### 3. Modelo Padrão Atualizado
- De `gpt-4o-mini` → `anthropic:claude-sonnet-4-5`
- Compatibilidade com 7 provedores mantida

## 📝 Convenções do Projeto

### Documentação
- **README.md**: Documentação principal, sempre atualizada com a versão
- **CHANGELOG.md**: Histórico detalhado de mudanças por versão
- **Seções obrigatórias no CHANGELOG:** Adicionado, Modificado, Corrigido, Técnico, Impacto

### Código
- **Imports:** Sempre usar imports relativos dentro do pacote (`from .agent import ...`)
- **Paths:** Usar `pathlib.Path` para compatibilidade cross-platform
- **Encoding:** UTF-8 em todas as operações de arquivo

### Versionamento
- **Quando fazer bump:**
  - MAJOR: Breaking changes
  - MINOR: Novas features (compatível com versão anterior)
  - PATCH: Bug fixes e melhorias menores

- **Checklist de bump de versão:**
  1. ✅ `setup.py` - line ~12
  2. ✅ `pyproject.toml` - line ~7
  3. ✅ `src/__init__.py` - line ~6
  4. ✅ `src/cli.py` - `--version` arg (~385)
  5. ✅ `README.md` - Header (~3)
  6. ✅ `CHANGELOG.md` - Nova seção no topo

## 🛠️ Comandos Úteis

```bash
# Instalar em modo desenvolvimento
pip install -e .

# Verificar versão
codebase-analyst --version

# Executar análise com tracing
codebase-analyst ./projeto --trace

# Gerar ONBOARDING.md
codebase-analyst ./projeto --task onboarding
```

## 🔍 Áreas de Atenção

### Middleware de Sumarização
- Implementação customizada em `src/summarization.py`
- Corrige bug do LangChain padrão
- **Parâmetros críticos em `agent.py`:**
  - `trigger=("fraction", 0.5)` - Sumariza quando atinge 50% do contexto máximo
  - `keep=("fraction", 0.2)` - Mantém 20% do contexto após sumarização
  - `trim_tokens_to_summarize=6000` - Sumariza com 6000 tokens de contexto
- **Parâmetro crítico em `_trim_messages_for_summary()` (summarization.py:528):**
  - `start_on=["human", "ai", "tool"]` - Tipos de mensagens incluídos na sumarização
  - **Importante:** Adição de `"ai"` e `"tool"` aos tipos padrão garante que respostas do agente e resultados de ferramentas sejam incluídos
  - Sem esses tipos, apenas mensagens humanas seriam sumarizadas, perdendo contexto crítico

### Multi-Provider Support
- 7 provedores: OpenAI, Anthropic, Groq, Google, Cohere, Mistral, Together AI
- Validação de API key por provedor em `cli.py:validate_api_key()`
- Configuração especial para modelos o1/o3/GPT-5: `reasoning_effort="medium"`

### Proteção de Sobrescrita
- Feature em `cli.py:check_existing_file()`
- Detecta arquivos existentes (ONBOARDING.md)
- Solicita confirmação antes de sobrescrever

## 📚 Referências Rápidas

### Variáveis de Ambiente
- `OPENAI_API_KEY`: Para modelos OpenAI
- `ANTHROPIC_API_KEY`: Para modelos Claude
- `GROQ_API_KEY`: Para modelos Groq
- `GOOGLE_API_KEY`: Para modelos Gemini
- `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY`: Para tracing

### Links Importantes
- Dependências: LangChain >= 0.3.0, LangGraph >= 0.2.0, Rich >= 13.0.0
- Python: >= 3.9

## 💡 Dicas para Claude Code

### ⚠️ REGRA CRÍTICA: Manutenção do CLAUDE.md
**SEMPRE que houver mudanças significativas no projeto, você DEVE atualizar este arquivo (CLAUDE.md).**

Atualizar CLAUDE.md quando:
- ✅ Nova versão do projeto (atualizar "Versão Atual" e "Features Recentes")
- ✅ Mudança de arquitetura ou componentes principais
- ✅ Novas convenções ou práticas adotadas
- ✅ Mudança de modelo padrão, configurações críticas, ou paths importantes
- ✅ Novos objetivos ou funcionalidades planejadas
- ✅ Atualização da "Última atualização" no rodapé

**Este arquivo é a fonte de verdade para futuras sessões. Mantê-lo atualizado economiza tempo de explicações.**

### Ao fazer mudanças:
1. **Sempre** verificar e atualizar a versão em TODOS os 6 arquivos se for bump
2. **Sempre** documentar no CHANGELOG.md com seções estruturadas
3. **Sempre** atualizar README.md se houver mudança de comportamento ou features
4. **Sempre** usar imports relativos dentro do pacote `src/`
5. **Sempre** testar que o versionamento está consistente
6. **Sempre** atualizar CLAUDE.md se a mudança for significativa

### Ao adicionar features:
1. Documentar em README.md com exemplos
2. Adicionar entrada no CHANGELOG.md
3. Considerar impacto em compatibilidade
4. Atualizar versão apropriadamente (MAJOR/MINOR/PATCH)
5. **Atualizar CLAUDE.md** com a nova feature na seção "Features Recentes"

### Ao corrigir bugs:
1. Documentar o problema e a solução no CHANGELOG.md
2. Considerar se é um PATCH ou precisa MINOR/MAJOR
3. Adicionar nota técnica no CHANGELOG se relevante

### Ao fazer bump de versão:
1. Seguir checklist de versionamento (6 arquivos)
2. **Atualizar CLAUDE.md**: versão, data, features recentes
3. Documentar no CHANGELOG.md

## 🎯 Objetivos Futuros

- [ ] Testes automatizados
- [ ] CI/CD pipeline
- [ ] Publicação no PyPI
- [ ] Suporte a mais tipos de documentação
- [ ] Integração com IDEs

---

**Última atualização:** 2026-01-16
**Versão do projeto:** 1.2.0
**Mantido por:** Codebase Analyst Team
