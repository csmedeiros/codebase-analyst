# Changelog

## [1.2.0] - 2026-01-16

### Adicionado
- **Flag `--trace` para Observabilidade**: Nova flag opcional para habilitar tracing com Langfuse
  - Por padrão, o tracing está **desabilitado** para melhor performance
  - Quando habilitado com `--trace`, permite observabilidade completa via Langfuse
  - Feedback visual no CLI indicando status do tracing (habilitado/desabilitado)
  - Flush do Langfuse condicionado à flag para evitar overhead desnecessário
  - Documentação completa no README.md com exemplos de uso

### Modificado
- **Organização de Prompts**: System prompts agora organizados em versões
  - Prompts movidos para diretório `src/prompts/`
  - System prompt atual: `system_prompt_v1.1.5.md`
  - Arquivo `prompts.py` carrega dinamicamente o prompt versionado
  - Facilita manutenção e tracking de mudanças nos prompts ao longo do tempo
- **Modelo Padrão**: Alterado de `gpt-4o-mini` para `anthropic:claude-sonnet-4-5`
  - Melhor desempenho em análises de codebase complexas
  - Suporte a contextos maiores
  - Mantida compatibilidade com todos os 7 provedores
- **README.md**: Atualizado com documentação da flag `--trace` e novos defaults

### Técnico
- Inicialização condicional do `CallbackHandler` do Langfuse em [cli.py:429-442](src/cli.py#L429-L442)
- Flush condicional do Langfuse client em [cli.py:460-461](src/cli.py#L460-L461)
- Carregamento dinâmico de prompts em [prompts.py:132](src/prompts.py#L132)
- Estrutura de versionamento de prompts em `src/prompts/`

### Impacto
- ✅ Melhor performance quando tracing não é necessário (padrão)
- ✅ Observabilidade completa disponível sob demanda
- ✅ Facilita debugging e análise de execuções com Langfuse
- ✅ Organização clara de prompts permite evolução controlada
- ✅ Mantém compatibilidade total com versões anteriores

## [1.1.8] - 2026-01-15

### Corrigido
- **Middleware de Sumarização Corrigido**: Corrigido bug crítico no middleware de resumo que impedia o contexto de ser gerido corretamente
  - Implementada classe `SummarizationMiddleware` customizada que substitui a implementação padrão do LangChain
  - Corrigida invocação do modelo durante a sumarização: adicionado suporte correto ao atributo `.text` do response
  - Ajustados parâmetros de trigger e keep para garantir sumarização eficiente:
    - `trigger=("fraction", 0.5)` - Sumariza quando atinge 50% do contexto máximo
    - `keep=("fraction", 0.2)` - Mantém 20% do contexto mais recente após sumarização
    - `trim_tokens_to_summarize=6000` - Sumariza com 6000 tokens de contexto
  - Sistema agora particiona corretamente mensagens entre as que devem ser sumarizadas e as que devem ser preservadas
  - Implementado tratamento correto de pares AI/Tool messages para evitar quebra de contexto

### Melhorado
- **Compatibilidade Multi-Modelo**: O agente agora funciona corretamente com múltiplos provedores de LLM, não apenas Claude Sonnet 4.5
  - Suporte completo para modelos OpenAI (GPT-4o, GPT-4o-mini, o1, o3, GPT-5)
  - Suporte para modelos Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
  - Suporte para modelos Groq (Llama 3.3 70B e outros)
  - Suporte para modelos Google (Gemini 2.0 Flash)
  - Ajuste automático de `chars_per_token` para modelos Anthropic (3.3) para contagem precisa de tokens
  - Adicionado parâmetro `reasoning_effort="medium"` para modelos OpenAI o1/o3/GPT-5

### Técnico
- Middleware `SummarizationMiddleware` implementado em [src/summarization.py](src/summarization.py)
  - Métodos síncronos (`before_model`) e assíncronos (`abefore_model`) implementados
  - Sistema de particionamento de mensagens com binary search para eficiência
  - Trimming inteligente de mensagens para sumarização com estratégia "last"
  - Validação robusta de configurações de `ContextSize` (fraction, tokens, messages)
  - Geração de IDs únicos para mensagens quando necessário
- Sistema de contagem de tokens otimizado por tipo de modelo
- Prompt de sumarização customizado focado em extração de contexto relevante

### Impacto
- ✅ Agente agora mantém contexto de longo prazo corretamente em todas as execuções
- ✅ Redução significativa no uso de tokens através de sumarização eficiente
- ✅ Compatibilidade com qualquer modelo de LLM que suporte function calling
- ✅ Performance melhorada em análises de codebases grandes (10k+ arquivos)
- ✅ Custos reduzidos através de gerenciamento inteligente de contexto

## [1.1.5] - 2026-01-14

### Modificado
- Bump de versão para 1.1.5
- Consolidação de correções e melhorias das versões 1.1.1 a 1.1.4

## [1.1.0] - 2026-01-12

### Adicionado
- **Proteção de Sobrescrita de Arquivos**: O CLI agora detecta automaticamente se README.md ou ARCHITECTURE.md já existem antes de executar
  - Exibe informações do arquivo existente (caminho, tamanho, data de modificação)
  - Solicita confirmação do usuário antes de sobrescrever
  - Cancela a operação se o usuário não confirmar (preserva o arquivo original)
  - Comportamento padrão é NÃO sobrescrever (enter vazio = cancelar)
  - Suporta respostas em português e inglês (s/sim/y/yes para confirmar)
  - Tratamento de Ctrl+C para cancelamento limpo
- Função `check_existing_file()` em src/cli.py
- Função `print_warning()` para mensagens de aviso formatadas
- Documentação completa em FEATURE_OVERWRITE_PROTECTION.md
- Script de teste test_overwrite.sh

### Modificado
- README.md atualizado com seção sobre Proteção de Sobrescrita
- Fluxo de execução do CLI: verificação de arquivo acontece após validações mas antes de criar o agente

### Corrigido
- **Bug Fix**: Erro `ModuleNotFoundError: No module named 'src'` ao executar de outros diretórios
  - Corrigido imports em src/cli.py: `from src.agent` → `from .agent`
  - Corrigido imports em src/agent.py: `from src.prompts` → `from .prompts` e `from src.tools` → `from .tools`
  - Atualizado src/__init__.py com exports adequados e `__version__`
  - Agora funciona perfeitamente de qualquer diretório após instalação via pip
- Documentação completa da correção em BUGFIX_v1.1.1.md

## [1.0.0] - 2026-01-12

### Adicionado
- Instalação via pip como pacote Python
- Comando CLI global `codebase-analyst` disponível em qualquer diretório
- Scripts de instalação automática para Mac/Linux (install.sh) e Windows (install.bat)
- Arquivo de configuração pyproject.toml para empacotamento moderno
- Arquivo setup.py para compatibilidade com pip
- MANIFEST.in para incluir arquivos não-Python no pacote
- .env.example com template de configuração
- INSTALL.md com guia completo de instalação
- Validação de OPENAI_API_KEY no início da execução
- Validação de caminhos antes de executar o agente
- Suporte para caminho padrão (diretório atual) quando não especificado
- Tratamento de erros melhorado com mensagens claras

### Modificado
- Estruturado o projeto como pacote Python instalável
- Entry point movido de main.py para src/cli.py
- Melhorado uso de pathlib.Path para garantir compatibilidade cross-platform
- Atualizado README.md com instruções de instalação e uso do CLI
- Requisitos de Python alterados de 3.13+ para 3.9+ (maior compatibilidade)

### Características
- **Cross-Platform**: Funciona nativamente em Mac, Windows e Linux
- **Instalável**: Pode ser instalado via pip e usado de qualquer lugar
- **Portátil**: Resolve caminhos automaticamente para funcionar em qualquer diretório
- **Configurável**: Suporta .env e variáveis de ambiente
- **Profissional**: Interface CLI com Rich para output estilizado

### Arquivos Criados
- `setup.py` - Configuração de instalação setuptools
- `pyproject.toml` - Configuração moderna de empacotamento Python
- `src/cli.py` - Entry point CLI do pacote
- `install.sh` - Script de instalação para Mac/Linux
- `install.bat` - Script de instalação para Windows
- `.env.example` - Template de configuração de ambiente
- `MANIFEST.in` - Manifesto de arquivos do pacote
- `INSTALL.md` - Guia detalhado de instalação
- `CHANGELOG.md` - Este arquivo

### Como Usar

Após instalação:
```bash
# De qualquer diretório
codebase-analyst ~/meu-projeto --task analyze
codebase-analyst . --task readme
codebase-analyst /caminho/completo/projeto --task architecture
```

### Upgrade Path

Se você estava usando a versão anterior:

**Antes:**
```bash
cd codebase-analyst
python main.py ./meu-projeto --task analyze
```

**Agora:**
```bash
# De qualquer lugar!
codebase-analyst ./meu-projeto --task analyze
```
