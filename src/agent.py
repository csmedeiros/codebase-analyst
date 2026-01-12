"""Configuração do agente de análise de codebase.

Este módulo cria e configura o agente usando LangGraph, que é a API
atual e recomendada do ecossistema LangChain para criação de agentes.
"""

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from src.prompts import SYSTEM_PROMPT
from src.tools import list_dir, read_file, write_file


def create_codebase_agent(model_name: str = "gpt-4o-mini"):
    """Cria e retorna o agente de análise de codebase.

    Args:
        model_name: Nome do modelo OpenAI a ser usado

    Returns:
        Agente configurado pronto para uso
    """
    # Inicializar o modelo
    model = ChatOpenAI(
        model=model_name,
        temperature=0.1,  # Baixa temperatura para outputs consistentes
    )

    # Lista de tools
    tools = [list_dir, read_file, write_file]

    from langchain.agents.middleware import TodoListMiddleware, SummarizationMiddleware

    # Criar o agente usando create_react_agent do langgraph
    # Esta é a API atual e recomendada para criação de agentes
    agent = create_agent(
        model=model,
        middleware=[TodoListMiddleware(), SummarizationMiddleware(model="openai:gpt-4o-mini", trigger=("tokens", 5000), keep=("tokens", 10000))],
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent
