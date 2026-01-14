"""Entry point para o Codebase Analyst Agent CLI.

Este módulo fornece uma interface CLI para análise de codebases
usando um agente LangChain com ferramentas de sistema de arquivos.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.rule import Rule
from rich.table import Table
from rich import box

from .agent import create_codebase_agent

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


def validate_api_key(model_name: str):
    """Valida se a chave de API necessária está configurada.

    Args:
        model_name: Nome do modelo no formato 'provider:model' ou apenas 'model'

    Returns:
        True se a chave de API está configurada, False caso contrário
    """
    # Parse do provider
    if ":" in model_name:
        provider, _ = model_name.split(":", 1)
    else:
        # Default para OpenAI
        provider = "openai"

    # Mapeamento de providers para variáveis de ambiente
    provider_env_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "groq": "GROQ_API_KEY",
        "google": "GOOGLE_API_KEY",
        "cohere": "COHERE_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "together": "TOGETHER_API_KEY",
    }

    env_var = provider_env_map.get(provider.lower())

    if not env_var:
        # Provider desconhecido, mas vamos deixar o init_chat_model lidar com isso
        return True

    if not os.getenv(env_var):
        print_error(
            f"{env_var} não encontrada!\n\n"
            f"Por favor, configure sua chave de API do {provider.capitalize()}:\n"
            f"  • Crie um arquivo .env na sua pasta home ou no diretório do projeto\n"
            f"  • Adicione a linha: {env_var}=sua-chave-aqui\n"
            f"  • Ou exporte como variável de ambiente: export {env_var}=sua-chave-aqui"
        )
        return False
    return True


def validate_path(path: str):
    """Valida se o caminho existe."""
    path_obj = Path(path).resolve()
    if not path_obj.exists():
        print_error(f"O caminho '{path}' não existe!")
        return False
    if not path_obj.is_dir():
        print_error(f"O caminho '{path}' não é um diretório!")
        return False
    return True


def print_warning(message: str):
    """Imprime mensagem de aviso."""
    console.print()
    warning_text = Text()
    warning_text.append("⚠ ", style=THEME["warning"])
    warning_text.append("Aviso: ", style=f"bold {THEME['warning']}")
    warning_text.append(message, style="white")
    console.print(Panel(warning_text, box=box.ROUNDED, border_style=THEME["warning"]))


def check_existing_file(target_path: Path, task: str) -> bool:
    """Verifica se arquivo já existe e pergunta ao usuário se pode sobrescrever.

    Args:
        target_path: Caminho do diretório alvo
        task: Tipo de tarefa (onboarding)

    Returns:
        True se pode continuar, False se usuário cancelou
    """
    file_mapping = {
        "onboarding": "ONBOARDING.md"
    }

    if task not in file_mapping:
        return True  # Tarefa 'analyze' não cria arquivos

    filename = file_mapping[task]
    file_path = target_path / filename

    if not file_path.exists():
        return True  # Arquivo não existe, pode continuar

    # Arquivo existe, mostrar aviso
    console.print()
    print_warning(f"O arquivo '{filename}' já existe no diretório!")

    # Mostrar informações do arquivo existente
    file_size = file_path.stat().st_size
    file_modified = file_path.stat().st_mtime
    from datetime import datetime
    modified_date = datetime.fromtimestamp(file_modified).strftime("%Y-%m-%d %H:%M:%S")

    info_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    info_table.add_column("Key", style="cyan")
    info_table.add_column("Value", style="white")

    info_table.add_row("Arquivo", str(file_path))
    info_table.add_row("Tamanho", f"{file_size} bytes")
    info_table.add_row("Modificado", modified_date)

    console.print(info_table)
    console.print()

    # Perguntar ao usuário
    warning_msg = Text()
    warning_msg.append("Este arquivo será ", style="white")
    warning_msg.append("SOBRESCRITO", style="bold red")
    warning_msg.append(" se você continuar.", style="white")
    console.print(warning_msg)
    console.print()

    # Prompt de confirmação
    try:
        response = input("Deseja continuar e sobrescrever o arquivo? [s/N]: ").strip().lower()

        if response in ['s', 'sim', 'y', 'yes']:
            # Deletar o arquivo existente
            try:
                file_path.unlink()
                console.print()
                console.print(Text(f"  ✓ Arquivo '{filename}' deletado e será recriado", style="yellow"))
                return True
            except Exception as e:
                console.print()
                print_error(f"Erro ao deletar arquivo '{filename}': {e}")
                return False
        else:
            console.print()
            console.print(Text(f"  ✗ Operação cancelada - arquivo '{filename}' preservado", style="green"))
            return False

    except (KeyboardInterrupt, EOFError):
        console.print()
        print_cancelled()
        return False


def main():
    """Função principal do CLI."""
    parser = argparse.ArgumentParser(
        description="Codebase Analyst Agent - Gera documentação de onboarding detalhada para codebases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  codebase-analyst ./meu-projeto
  codebase-analyst ./meu-projeto --task onboarding
  codebase-analyst ./meu-projeto --task onboarding --model openai:gpt-4o
  codebase-analyst . --model anthropic:claude-3-5-sonnet-20241022
  codebase-analyst . --task analyze --model groq:llama-3.3-70b-versatile

Tarefas disponíveis:
  • analyze     : Análise rápida da codebase (sem gerar documentação)
  • onboarding  : Gera ONBOARDING.md completo para novos desenvolvedores (default)

Notas:
  • Suporta múltiplos provedores: OpenAI, Anthropic, Groq, Google, etc.
  • Requer chaves de API configuradas (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
  • Compatível com Mac, Windows e Linux
  • Usa caminhos absolutos internamente para funcionar em qualquer diretório
  • O ONBOARDING.md inclui: estrutura, entry points, fluxos, roadmap de leitura e muito mais
        """,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Caminho do repositório a analisar (default: diretório atual)",
    )
    parser.add_argument(
        "--model",
        default="anthropic:claude-sonnet-4-5",
        help=(
            "Modelo a usar no formato 'provider:model' ou apenas 'model' (default: gpt-4o-mini). "
            "Exemplos: openai:gpt-4o, anthropic:claude-3-5-sonnet-20241022, "
            "groq:llama-3.3-70b-versatile, google:gemini-2.0-flash-exp"
        ),
    )
    parser.add_argument(
        "--task",
        default="onboarding",
        choices=["analyze", "onboarding"],
        help="Tipo de tarefa a executar (default: onboarding)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="codebase-analyst 1.1.0",
    )

    args = parser.parse_args()

    # Validações
    if not validate_api_key(args.model):
        sys.exit(1)

    # Resolve path para absoluto (cross-platform)
    target_path = Path(args.path).resolve()

    if not validate_path(str(target_path)):
        sys.exit(1)

    # Verificar se arquivo já existe (para tarefas readme e architecture)
    if not check_existing_file(target_path, args.task):
        sys.exit(0)  # Usuário cancelou, saída limpa

    # Header
    print_header(str(target_path), args.task, args.model)

    # Criar o agente
    console.print(Rule("Inicializando", style="white"))
    with console.status("[cyan]Criando agente...", spinner="dots"):
        try:
            agent = create_codebase_agent(model_name=args.model)
        except Exception as e:
            print_error(f"Falha ao criar agente: {e}")
            sys.exit(1)

    console.print(Text("  ✓ Agente instanciado", style="green"))

    # Construir o prompt baseado na tarefa
    task_prompts = {
        "analyze": f"Analise a codebase em '{target_path}' e forneça um resumo técnico completo.",
        "onboarding": f"Analise a codebase em '{target_path}' e gere um arquivo ONBOARDING.md completo e detalhado na raiz do projeto. Este arquivo deve facilitar o entendimento do código para novos desenvolvedores, incluindo: estrutura do projeto, entry points, arquivos principais, fluxos de execução, configurações, dependências e um roadmap de leitura do código.",
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
    config = {"callbacks": [callback], "recursion_limit": 1000}

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

    # Renderizar markdown conforme a tarefa
    if args.task == "onboarding":
        onboarding_path = target_path / "ONBOARDING.md"
        if onboarding_path.exists():
            console.print()
            console.print(Rule("Visualizando ONBOARDING.md", style="cyan"))
            console.print()
            try:
                with open(onboarding_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    md = Markdown(content)
                    console.print(md)
                console.print()
                console.print(Text(f"✓ Arquivo completo salvo em: {onboarding_path}", style="green"))
            except Exception as e:
                print_error(f"Erro ao renderizar ONBOARDING.md: {e}")
    elif args.task == "analyze":
        # Para análise, tentar renderizar qualquer markdown gerado ou mensagem final do agente
        console.print()
        console.print(Rule("Análise Completa", style="cyan"))
        console.print()
        console.print(Text("✓ Análise técnica da codebase concluída com sucesso!", style="green"))


if __name__ == "__main__":
    main()
