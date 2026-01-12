"""Configuração do agente de análise de codebase.

Este módulo cria e configura o agente usando LangGraph, que é a API
atual e recomendada do ecossistema LangChain para criação de agentes.
"""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from .prompts import SYSTEM_PROMPT
from .tools import list_dir, read_file, write_file


def create_codebase_agent(model_name: str = "gpt-5-mini"):
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
    if provider == "openai" and (model.startswith("o") or model.startswith("gpt-5")):
        model_kwargs["reasoning_effort"] = "medium"

    # Inicializar o modelo usando init_chat_model
    model = init_chat_model(
        model=model,
        model_provider=provider,
        **model_kwargs
    )

    # Lista de tools
    tools = [list_dir, read_file, write_file]

    from langchain.agents.middleware import TodoListMiddleware, SummarizationMiddleware

    # Criar o agente usando create_react_agent do langgraph
    # Esta é a API atual e recomendada para criação de agentes
    sum_middleware = SummarizationMiddleware(
        model="openai:gpt-4o",
        trigger=("messages", 20),
        keep=("messages", 10),
        trim_tokens_to_summarize=8000
    )
    todo_middlware = TodoListMiddleware()
    agent = create_agent(
        model=model,
        middleware=[sum_middleware, todo_middlware],
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent
