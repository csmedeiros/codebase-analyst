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
        start: Linha inicial (1-indexed para input, padrão: 1)
        end: Linha final (1-indexed para input, inclusive). Se None, lê até o final do arquivo.

    Returns:
        Conteúdo do arquivo com números de linha estilo VS Code (0-indexed, alinhados à esquerda)
        Formato: "N     conteúdo" onde N é o número da linha começando em 0
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

        # Calcular largura necessária para os números de linha
        # Usar o número da última linha para determinar a largura
        max_line_num = end - 1  # 0-indexed
        line_num_width = len(str(max_line_num))

        # Formatar com números de linha estilo VS Code (0-indexed, alinhados à esquerda)
        numbered_lines = []
        for i, line in enumerate(selected_lines, start=start - 1):  # start - 1 para 0-indexed
            line_num_str = str(i).ljust(line_num_width)
            numbered_lines.append(f"{line_num_str}     {line}")

        header = f"Arquivo: {file_path}\n"
        header += f"Linhas: {start - 1}-{end - 1} de {total_lines} (0-indexed)\n"
        header += "-" * 40 + "\n"

        return header + "\n".join(numbered_lines)

    except PermissionError:
        return f"Erro: Sem permissão para ler '{path}'."
    except Exception as e:
        return f"Erro ao ler arquivo: {e}"


@tool
def write_file(path: str, content: str, append: bool = False) -> str:
    """Escreve conteúdo em um arquivo, criando diretórios pai se necessário.

    Args:
        path: Caminho do arquivo a ser criado/sobrescrito
        content: Conteúdo a ser escrito no arquivo
        append: Se True, adiciona o conteúdo ao final do arquivo. Se False, sobrescreve.

    Returns:
        Mensagem de confirmação com o caminho do arquivo criado/atualizado
    """
    try:
        file_path = Path(path).resolve()

        # Criar diretórios pai se não existirem
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Escrever ou adicionar o conteúdo
        if append:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write("\n\n" + content)
            action = " teve conteúdo adicionado"
        else:
            file_path.write_text(content, encoding="utf-8")
            action = "criado/sobrescrito"

        return f"Arquivo {action} com sucesso: {file_path}"

    except PermissionError:
        return f"Erro: Sem permissão para escrever em '{path}'."
    except Exception as e:
        return f"Erro ao escrever arquivo: {e}"
    
import os

@tool
def remove_draft_file(path: str):
    """
    Deleta o arquivo de rascunho DRAFT.md

    Args:
        path: Caminho para o arquivo de rascunho DRAFT.md

    Returns:
        Mensagem de confirmacao ou de erro para a exclusao do arquivo de rascunho
    """

    try:
        os.remove(path)
    except PermissionError:
        return f"Erro: Sem permissão para remover '{path}'."
    except Exception as e:
        return f"Erro ao remover arquivo:\n{e}"
