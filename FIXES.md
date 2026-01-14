# Correções para Loop Infinito no Agente de Análise de Codebase

## Problema Identificado

O agente está entrando em loop infinito devido a três problemas principais:

1. **Sumarização muito agressiva**: O middleware de sumarização está configurado para manter apenas 4000 tokens, o que é insuficiente para o agente lembrar o progresso da análise.

2. **Perda de contexto após sumarização**: Após cada sumarização, o agente perde informações cruciais sobre:
   - Quais arquivos já foram analisados
   - Estrutura da codebase descoberta
   - Progresso atual da tarefa

3. **Ausência de mecanismo de estado persistente**: O agente não tem um mecanismo para rastrear progresso fora do histórico de mensagens.

## Análise do Trace Langfuse

### Padrão de Tokens Identificado

```
Generation #1:  Input: 3984 | Cache:    0 | Output:   31  <- Início
Generation #2:  Input:  151 | Cache: 3968 | Output:  463  <- Primeira sumarização
Generation #3:  Input:  135 | Cache: 4480 | Output:  123  <- Segunda sumarização
...
Generation #10: Input: 9112 | Cache:    0 | Output:  249  <- RESET TOTAL
```

**Observações:**
- Cache alto + Input baixo = Contexto perdido após sumarização
- A cada sumarização, apenas ~4000 tokens são mantidos
- Reset completo ocorre periodicamente (cache = 0, input alto)

### Custo Total da Execução

- **32 gerações de LLM**
- **Custo: $0.35**
- **Duração: ~5 minutos**
- **Resultado: Loop infinito sem completar a tarefa**

---

## Soluções Propostas

### Solução 1: Ajustar Configurações de Sumarização (RECOMENDADO)

Modificar `src/agent.py` linhas 58-64:

```python
sum_middleware = SummarizationMiddleware(
    model="openai:gpt-4o",
    trigger=("tokens", 30000),      # ⬆️ Aumentar: sumariza menos frequentemente
    keep=("tokens", 15000),          # ⬆️ Aumentar: mantém mais contexto
    trim_tokens_to_summarize=8000,   # ⬆️ Aumentar: sumariza com mais informação
    summary_prompt=SUMMARIZATION_PROMPT
)
```

**Justificativa:**
- `trigger=30000`: GPT-4o suporta 128k tokens, então 30k é ~23% do limite
- `keep=15000`: Mantém 50% do contexto após sumarização (vs. 20% atual)
- `trim_tokens_to_summarize=8000`: Permite sumarizar com mais informação

### Solução 2: Melhorar o Prompt de Sumarização

Modificar `src/prompts.py` para incluir instruções específicas sobre **o que preservar**:

```python
SUMMARIZATION_PROMPT = """<role>
Context Extraction Assistant for Codebase Analysis
</role>

<primary_objective>
Extract the highest quality/most relevant context from the conversation history,
focusing on codebase analysis progress and discovered structure.
</primary_objective>

<critical_information_to_preserve>
1. **Files already analyzed**: List of files and directories that have been read/analyzed
2. **Codebase structure**: Key directories, modules, and their purposes
3. **Current task progress**: What has been completed and what remains
4. **Important findings**: Key technologies, patterns, dependencies discovered
5. **Current working location**: Which directory/file is being analyzed now
</critical_information_to_preserve>

<instructions>
You are analyzing a codebase to generate documentation. The context you extract will replace
the conversation history, so you must preserve:

- A bulleted list of ALL files and directories analyzed so far
- The overall structure of the codebase discovered
- Your current progress in the analysis (e.g., "Analyzed 5/10 directories")
- Key findings about technologies, frameworks, and patterns used
- The next steps in your analysis plan

DO NOT repeat tool outputs verbatim. Instead, summarize findings in a structured format.
</instructions>

<messages>
Messages to summarize:
{messages}
</messages>

Respond with a structured summary that includes:

## Analyzed Files and Directories
[Bulleted list of what has been analyzed]

## Codebase Structure
[Key directories and their purposes]

## Current Progress
[What's done and what remains]

## Key Findings
[Technologies, patterns, important insights]

## Next Steps
[What needs to be analyzed next]
"""
```

### Solução 3: Implementar State Tracking com LangGraph Checkpoints

Adicionar um checkpoint system para persistir estado fora do histórico de mensagens:

```python
# src/agent.py

from langgraph.checkpoint.memory import MemorySaver

def create_codebase_agent(model_name: str = "gpt-5-mini"):
    # ... código existente ...

    # Adicionar checkpointer para persistir estado
    memory = MemorySaver()

    agent = create_agent(
        model=model,
        middleware=[sum_middleware, ctx_edit],
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=memory,  # <- ADICIONAR ISSO
    )

    return agent
```

### Solução 4: Adicionar Tool de State Management

Criar uma tool específica para o agente registrar progresso:

```python
# src/tools.py

from langchain_core.tools import tool

@tool
def update_progress(
    analyzed_files: list[str],
    current_directory: str,
    progress_notes: str
) -> str:
    """Registra o progresso da análise da codebase.

    Use esta tool para registrar:
    - Arquivos/diretórios já analisados
    - Localização atual na análise
    - Notas sobre progresso e descobertas

    Isso garante que o progresso seja mantido mesmo após sumarizações.
    """
    # Persistir em um arquivo ou estado do grafo
    progress = {
        "analyzed_files": analyzed_files,
        "current_directory": current_directory,
        "notes": progress_notes
    }

    # Retornar confirmação
    return f"Progress updated: {len(analyzed_files)} files analyzed, currently at {current_directory}"
```

E adicionar no system prompt:

```python
SYSTEM_PROMPT = """...

IMPORTANTE: Para evitar retrabalho, use a tool `update_progress` regularmente para registrar:
- Arquivos e diretórios já analisados
- Sua localização atual na análise
- Descobertas importantes

Antes de analisar um arquivo, sempre verifique se ele já foi analisado anteriormente.
"""
```

---

## Recomendação de Implementação

### Fase 1 (Imediato):
1. ✅ Aplicar **Solução 1**: Ajustar configurações de sumarização
2. ✅ Aplicar **Solução 2**: Melhorar prompt de sumarização

### Fase 2 (Opcional, se o problema persistir):
3. ⚠️ Implementar **Solução 3**: State tracking com checkpoints
4. ⚠️ Implementar **Solução 4**: Tool de progress tracking

---

## Código Completo para Aplicar

### 1. Atualizar `src/agent.py`

```python
# Linha 58-64
sum_middleware = SummarizationMiddleware(
    model="openai:gpt-4o",
    trigger=("tokens", 30000),       # Aumentado de 20000
    keep=("tokens", 15000),           # Aumentado de 4000
    trim_tokens_to_summarize=8000,    # Aumentado de 4000
    summary_prompt=SUMMARIZATION_PROMPT
)
```

### 2. Criar novo arquivo `src/prompts_fixed.py`

Com o `SUMMARIZATION_PROMPT` melhorado (veja Solução 2).

### 3. Atualizar import em `src/agent.py`

```python
from .prompts_fixed import SYSTEM_PROMPT, SUMMARIZATION_PROMPT
```

---

## Monitoramento

Após aplicar as correções, monitore no Langfuse:

1. **Token usage**: `keep` deveria manter ~15k tokens após sumarização
2. **Cache reads**: Deveria ser menor (~3-5k) vs. input tokens maior (~10-15k)
3. **Número de sumarizações**: Deveria ser reduzido significativamente
4. **Progresso da tarefa**: O agente deveria completar a análise sem loops

---

## Evidências do Problema Original

### Configuração Problemática
```python
trigger=("tokens", 20000),  # Sumariza cedo demais
keep=("tokens", 4000),      # Mantém pouco contexto (20% do trigger)
trim_tokens_to_summarize=4000,
```

### Resultado no Trace
- 32 generations em 5 minutos
- Múltiplas sumarizações (todas com cache alto, input baixo)
- 2 resets completos de contexto
- Task nunca completada
- Custo: $0.35 sem resultado útil
