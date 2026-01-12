"""Tools para o agente de análise de codebase.

Este módulo implementa as ferramentas que o agente usa para interagir
com o sistema de arquivos de forma cross-platform usando pathlib.
"""

from pathlib import Path

from langchain_core.tools import tool


@tool
def list_dir(path: str) -> str:
    """Lista o conteúdo de um diretório, mostrando arquivos e subdiretórios.

    Args:
        path: Caminho do diretório a ser listado (relativo ou absoluto)

    Returns:
        String formatada com a lista de arquivos e diretórios
    """
    try:
        dir_path = Path(path).resolve()

        if not dir_path.exists():
            return f"Erro: O diretório '{path}' não existe."

        if not dir_path.is_dir():
            return f"Erro: '{path}' não é um diretório."

        items = []
        for item in sorted(dir_path.iterdir()):
            if item.is_dir():
                items.append(f"[DIR]  {item.name}/")
            else:
                items.append(f"[FILE] {item.name}")

        if not items:
            return f"O diretório '{path}' está vazio."

        header = f"Conteúdo de: {dir_path}\n" + "-" * 40 + "\n"
        return header + "\n".join(items)

    except PermissionError:
        return f"Erro: Sem permissão para acessar '{path}'."
    except Exception as e:
        return f"Erro ao listar diretório: {e}"


@tool
def read_file(path: str, start: int = 1, end: int | None = None) -> str:
    """Lê o conteúdo de um arquivo de texto, opcionalmente apenas um intervalo de linhas.

    Args:
        path: Caminho do arquivo a ser lido
        start: Linha inicial (1-indexed, padrão: 1)
        end: Linha final (1-indexed, inclusive). Se None, lê até o final do arquivo.

    Returns:
        Conteúdo do arquivo com números de linha no formato "N: conteúdo"
    """
    try:
        file_path = Path(path).resolve()

        if not file_path.exists():
            return f"Erro: O arquivo '{path}' não existe."

        if not file_path.is_file():
            return f"Erro: '{path}' não é um arquivo."

        # Verificar se é um arquivo binário (heurística simples)
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return f"Erro: '{path}' parece ser um arquivo binário e não pode ser lido como texto."

        lines = content.splitlines()
        total_lines = len(lines)

        # Validar índices
        if start < 1:
            start = 1
        if end is None or end > total_lines:
            end = total_lines
        if start > total_lines:
            return f"Erro: Linha inicial {start} excede o total de linhas ({total_lines})."
        if start > end:
            return f"Erro: Linha inicial ({start}) maior que linha final ({end})."

        # Extrair o intervalo (converter para 0-indexed)
        selected_lines = lines[start - 1 : end]

        # Formatar com números de linha
        numbered_lines = [
            f"{i}: {line}" for i, line in enumerate(selected_lines, start=start)
        ]

        header = f"Arquivo: {file_path}\n"
        header += f"Linhas: {start}-{end} de {total_lines}\n"
        header += "-" * 40 + "\n"

        return header + "\n".join(numbered_lines)

    except PermissionError:
        return f"Erro: Sem permissão para ler '{path}'."
    except Exception as e:
        return f"Erro ao ler arquivo: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Escreve conteúdo em um arquivo, criando diretórios pai se necessário.

    Args:
        path: Caminho do arquivo a ser criado/sobrescrito
        content: Conteúdo a ser escrito no arquivo

    Returns:
        Mensagem de confirmação com o caminho do arquivo criado
    """
    try:
        file_path = Path(path).resolve()

        # Criar diretórios pai se não existirem
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Escrever o conteúdo
        file_path.write_text(content, encoding="utf-8")

        return f"Arquivo criado/atualizado com sucesso: {file_path}"

    except PermissionError:
        return f"Erro: Sem permissão para escrever em '{path}'."
    except Exception as e:
        return f"Erro ao escrever arquivo: {e}"
