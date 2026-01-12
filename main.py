"""Entry point para o Codebase Analyst Agent.

Este módulo fornece uma interface CLI para análise de codebases
usando um agente LangChain com ferramentas de sistema de arquivos.
"""

from dotenv import load_dotenv

load_dotenv()

import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text
from rich.rule import Rule
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich import box

from src.agent import create_codebase_agent

from langfuse import get_client
from langfuse.langchain import CallbackHandler

# Configuração do console Rich
console = Console()

# Cores do tema (inspirado no Claude Code)
THEME = {
    "primary": "cyan",
    "secondary": "magenta",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "muted": "white",
    "text": "bright_white",
    "agent": "cyan",
    "tool": "yellow",
    "result": "green",
}


def print_header(path: str, task: str, model: str):
    """Imprime o header estilizado do CLI."""
    # Banner
    banner = Text()
    banner.append("◆ ", style="bold cyan")
    banner.append("Codebase Analyst Agent", style="bold white")

    console.print()
    console.print(Panel(banner, box=box.ROUNDED, border_style="cyan", padding=(0, 2)))

    # Info da execução
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Key", style="white")
    info_table.add_column("Value", style="bold white")

    info_table.add_row("📁 Caminho", path)
    info_table.add_row("🎯 Tarefa", task)
    info_table.add_row("🤖 Modelo", model)

    console.print(info_table)
    console.print()


def print_agent_message(content: str):
    """Imprime mensagem do agente com formatação Markdown."""
    if not content:
        return

    console.print()
    console.print(Text("◆ Agente", style=f"bold {THEME['agent']}"))

    # Renderiza como Markdown
    md = Markdown(content)
    console.print(Panel(md, box=box.ROUNDED, border_style=THEME["agent"], padding=(1, 2)))


def print_tool_call(tool_name: str, tool_args: dict):
    """Imprime chamada de ferramenta com destaque."""
    console.print()

    # Header da tool
    tool_header = Text()
    tool_header.append("⚡ ", style=f"bold {THEME['tool']}")
    tool_header.append("Tool: ", style=THEME["tool"])
    tool_header.append(tool_name, style=f"bold {THEME['tool']}")

    console.print(tool_header)

    # Argumentos
    if tool_args:
        args_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
        args_table.add_column("Param", style="cyan")
        args_table.add_column("Value", style="white", overflow="fold")

        for key, value in tool_args.items():
            value_str = str(value)
            # Truncar valores muito longos
            if len(value_str) > 150:
                value_str = value_str[:150] + "..."

            # Se parece ser código ou path, destacar
            if key in ["path", "file_path", "dir_path"]:
                args_table.add_row(f"  {key}", Text(value_str, style="bold blue"))
            elif key == "content" and len(value_str) > 50:
                args_table.add_row(f"  {key}", Text(f"[{len(value)} chars]", style="italic white"))
            else:
                args_table.add_row(f"  {key}", value_str)

        console.print(args_table)


def print_tool_result(content: str, tool_name: str = None, max_lines: int = 20):
    """Imprime resultado de ferramenta."""
    if not content:
        return

    lines = content.split("\n")
    truncated = False

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        truncated = True

    display_content = "\n".join(lines)
    if truncated:
        display_content += f"\n... [+{len(content.split(chr(10))) - max_lines} linhas]"

    # Header do resultado
    result_header = Text()
    result_header.append("✓ ", style=f"bold {THEME['result']}")
    if tool_name:
        result_header.append(f"Resultado de ", style=THEME["result"])
        result_header.append(tool_name, style=f"bold {THEME['result']}")
    else:
        result_header.append("Resultado", style=THEME["result"])

    console.print(result_header)

    # Conteúdo em painel
    console.print(
        Panel(
            Text(display_content, style="white"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 1),
        )
    )


def print_error(message: str):
    """Imprime mensagem de erro."""
    console.print()
    error_text = Text()
    error_text.append("✖ ", style=THEME["error"])
    error_text.append("Erro: ", style=f"bold {THEME['error']}")
    error_text.append(message, style="white")
    console.print(Panel(error_text, box=box.ROUNDED, border_style=THEME["error"]))


def print_success():
    """Imprime mensagem de sucesso ao finalizar."""
    console.print()
    success_text = Text()
    success_text.append("✓ ", style=THEME["success"])
    success_text.append("Análise concluída com sucesso!", style=f"bold {THEME['success']}")
    console.print(Panel(success_text, box=box.ROUNDED, border_style=THEME["success"]))
    console.print()


def print_cancelled():
    """Imprime mensagem de cancelamento."""
    console.print()
    cancel_text = Text()
    cancel_text.append("⚠ ", style=THEME["warning"])
    cancel_text.append("Operação cancelada pelo usuário", style=THEME["warning"])
    console.print(cancel_text)
    console.print()


def main():
    """Função principal do CLI."""
    parser = argparse.ArgumentParser(
        description="Codebase Analyst Agent - Analisa repositórios de código e gera documentação",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py ./meu-projeto --task analyze
  python main.py ./meu-projeto --task readme
  python main.py ./meu-projeto --task architecture --model gpt-4o
        """,
    )
    parser.add_argument("path", help="Caminho do repositório a analisar")
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="Modelo OpenAI a usar (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--task",
        default="analyze",
        choices=["analyze", "readme", "architecture"],
        help="Tipo de tarefa a executar (default: analyze)",
    )
    args = parser.parse_args()

    # Header
    print_header(args.path, args.task, args.model)

    # Criar o agente
    console.print(Rule("Inicializando", style="white"))
    with console.status("[cyan]Criando agente...", spinner="dots"):
        try:
            agent = create_codebase_agent(model_name=args.model)
        except Exception as e:
            print_error(f"Falha ao criar agente: {e}")
            sys.exit(1)

    console.print(Text("  ✓ Agente criado", style="green"))

    # Construir o prompt baseado na tarefa
    task_prompts = {
        "analyze": f"Analise a codebase em '{args.path}' e forneça um resumo técnico completo.",
        "readme": f"Analise a codebase em '{args.path}' e gere um README.md profissional na raiz do projeto.",
        "architecture": f"Analise a codebase em '{args.path}' e documente a arquitetura do sistema em um arquivo ARCHITECTURE.md.",
    }

    user_message = task_prompts[args.task]

    # Mostrar prompt
    console.print()
    console.print(Rule("Executando", style="white"))
    console.print()
    console.print(Text("◇ Prompt", style="cyan"))
    console.print(Text(f"  {user_message}", style="italic white"))

    # Configurar callbacks
    callback = CallbackHandler()
    langfuse = get_client()
    config = {"callbacks": [callback]}

    # Rastrear última tool chamada
    last_tool_name = None

    # Executar com streaming
    try:
        for chunk in agent.stream(
            {"messages": [{"role": "user", "content": user_message}]},
            stream_mode="updates",
            config=config,
        ):
            for step, data in chunk.items():
                if step == "agent":
                    msg = data["messages"][-1]
                    if hasattr(msg, "content") and msg.content:
                        print_agent_message(msg.content)
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            tool_name = tc.get("name", tc.get("type", "unknown"))
                            tool_args = tc.get("args", {})
                            last_tool_name = tool_name  # Armazena para usar no resultado
                            print_tool_call(tool_name, tool_args)
                elif step == "tools":
                    msg = data["messages"][-1]
                    content = str(msg.content) if hasattr(msg, "content") else str(msg)
                    print_tool_result(content, tool_name=last_tool_name)
                langfuse.flush()

    except KeyboardInterrupt:
        print_cancelled()
        sys.exit(0)
    except Exception as e:
        print_error(str(e))
        sys.exit(1)

    # Finalização
    console.print()
    console.print(Rule("Concluído", style="white"))
    print_success()


if __name__ == "__main__":
    main()
