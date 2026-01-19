"""Configuração do agente de análise de codebase.

Este módulo cria e configura o agente usando LangGraph, que é a API
atual e recomendada do ecossistema LangChain para criação de agentes.
"""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from .prompts import SYSTEM_PROMPT, SUMMARIZATION_PROMPT
from .tools import list_dir, read_file, write_file, remove_draft_file


def create_codebase_agent(model_name: str = "anthropic:claude-sonnet-4-5"):
    """Cria e retorna o agente de análise de codebase.

    Args:
        model_name: Nome do modelo no formato 'provider:model' ou apenas 'model'.
                   Exemplos:
                   - 'openai:gpt-4o-mini' ou 'gpt-4o-mini' (OpenAI)
                   - 'anthropic:claude-3-5-sonnet-20241022' (Anthropic)
                   - 'groq:llama-3.3-70b-versatile' (Groq)
                   - 'google:gemini-2.0-flash-exp' (Google)

    Returns:
        Agente configurado pronto para uso
    """
    # Parse do provider e model name
    if ":" in model_name:
        provider, model = model_name.split(":", 1)
    else:
        # Default para OpenAI se não especificado
        provider = "openai"
        model = model_name

    # Configurações base do modelo
    model_kwargs = {
        "temperature": 0.3,  # Baixa temperatura para outputs consistentes
    }

    # Adicionar reasoning_effort para modelos OpenAI o1/o3
    if provider == "openai":
        model_kwargs["frequency_penalty"] = 0.0
        model_kwargs["presence_penalty"] = 0.0
        if (model.startswith("o") or model.startswith("gpt-5")):
            model_kwargs["reasoning_effort"] = "medium"


    # Inicializar o modelo usando init_chat_model
    model = init_chat_model(
        model=model,
        model_provider=provider,
        **model_kwargs
    )

    # Lista de tools
    tools = [list_dir, read_file, write_file, remove_draft_file]

    from langchain.agents.middleware import TodoListMiddleware, ClearToolUsesEdit, ContextEditingMiddleware, ToolRetryMiddleware
    from .summarization import SummarizationMiddleware

    # Criar o agente usando create_react_agent do langgraph
    # Esta é a API atual e recomendada para criação de agentes
    sum_middleware = SummarizationMiddleware(
        model=model,
        trigger=("fraction", 0.5),       # Aumentado: sumariza menos frequentemente
        keep=("fraction", 0.2),          # Aumentado: mantém 50% do contexto após sumarização
        trim_tokens_to_summarize=6000,   # Aumentado: sumariza com mais informação de contexto
        summary_prompt=SUMMARIZATION_PROMPT,
    )

    ctx_edit = ContextEditingMiddleware(
        edits=[
            ClearToolUsesEdit(
                trigger=2000,          # ajuste conforme teu modelo/uso
                keep=3,                  # mantém os 3 tool results mais recentes
                clear_tool_inputs=False, # normalmente você quer manter os args do tool call
            )
        ],
        token_count_method="approximate",
    )

    tool_retry = ToolRetryMiddleware(tools=tools, retry_on=Exception)
    todo_middlware = TodoListMiddleware()

    agent = create_agent(
        model=model,
        middleware=[sum_middleware, todo_middlware, tool_retry],
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent