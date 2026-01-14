"""Tools para o agente de análise de codebase.

Este módulo implementa as ferramentas que o agente usa para interagir
com o sistema de arquivos de forma cross-platform usando pathlib.
"""

from pathlib import Path

from langchain_core.tools import tool


@tool
def list_dir(
    path: str,
    max_entries: int = 200,
    max_depth: int = 5,
    include_hidden: bool = False,
    follow_symlinks: bool = False,
) -> str:
    """
    Lista o conteúdo de um diretório com limites duros de volume e profundidade.

    Esta tool é projetada para evitar respostas gigantes (ToolMessage grande) que
    estouram o contexto do agente/sumarizador. Ela:
      - limita a quantidade total de entradas retornadas (`max_entries`);
      - limita a profundidade de varredura (`max_depth`);
      - opcionalmente ignora arquivos ocultos (nomes iniciados com '.');
      - opcionalmente evita seguir symlinks de diretórios (previne loops).

    Args:
        path: Caminho do diretório a ser listado (relativo ou absoluto).
        max_entries: Máximo de entradas (arquivos/dirs) retornadas no output.
        max_depth: Profundidade máxima de varredura. 1 = apenas o diretório raiz.
        include_hidden: Se True, inclui itens ocultos (prefixo '.').
        follow_symlinks: Se True, permite descer em diretórios que são symlinks.

    Returns:
        String formatada com header e itens listados.
        Pode incluir rodapé com:
          - [TRUNCATED] quando excede `max_entries`;
          - [DENIED] quando algum subdiretório não pôde ser acessado.
    """
    try:
        dir_path = Path(path).resolve()

        if not dir_path.exists():
            return f"Erro: O diretório '{path}' não existe."
        if not dir_path.is_dir():
            return f"Erro: '{path}' não é um diretório."

        max_entries = max(1, int(max_entries))
        max_depth = max(1, int(max_depth))

        lines: list[str] = []
        truncated = False
        denied_count = 0
        entry_count = 0

        def _should_skip(p: Path) -> bool:
            if include_hidden:
                return False
            return p.name.startswith(".")

        def _walk(cur: Path, depth: int) -> None:
            nonlocal truncated, denied_count, entry_count
            if truncated:
                return

            try:
                children = sorted(
                    cur.iterdir(),
                    key=lambda p: (not p.is_dir(), p.name.lower()),
                )
            except PermissionError:
                denied_count += 1
                rel = cur.relative_to(dir_path) if cur != dir_path else Path(".")
                indent = "  " * depth
                lines.append(f"{indent}[DENIED] {rel.as_posix()}/")
                return

            for child in children:
                if truncated:
                    return
                if _should_skip(child):
                    continue

                rel = child.relative_to(dir_path)
                indent = "  " * depth

                is_dir = child.is_dir()
                is_link = child.is_symlink()

                if is_dir:
                    suffix = "/" if not rel.as_posix().endswith("/") else ""
                    tag = "[DIR] "
                    if is_link:
                        tag = "[LNKD]"
                    lines.append(f"{indent}{tag}  {rel.as_posix()}{suffix}")
                else:
                    tag = "[FILE]"
                    if is_link:
                        tag = "[LNK ]"
                    lines.append(f"{indent}{tag} {rel.as_posix()}")

                entry_count += 1
                if entry_count >= max_entries:
                    truncated = True
                    return

                # Descer recursivamente até max_depth
                if is_dir and (depth + 1) < max_depth:
                    # Evitar loops via symlink por padrão
                    if is_link and not follow_symlinks:
                        continue
                    _walk(child, depth + 1)

        _walk(dir_path, 0)

        header = (
            f"Conteúdo de: {dir_path}\n"
            f"Max entries: {max_entries} | Max depth: {max_depth}\n"
            + "-" * 60
            + "\n"
        )

        if not lines:
            return header + f"(vazio) {dir_path}"

        footer_parts = []
        if truncated:
            footer_parts.append(f"[TRUNCATED] exibindo {entry_count} de >= {entry_count + 1} entradas")
        if denied_count:
            footer_parts.append(f"[DENIED] {denied_count} diretório(s) sem permissão")

        footer = ("\n" + "-" * 60 + "\n" + " | ".join(footer_parts)) if footer_parts else ""
        return header + "\n".join(lines) + footer

    except Exception as e:
        return f"Erro ao listar diretório: {e}"


@tool
def read_file(
    path: str,
    start: int = 1,
    end: int | None = None,
    max_lines: int = 400,
    max_chars: int = 20_000,
    max_line_chars: int = 4_000,
) -> str:
    """
    Lê um arquivo de texto com paginação e limites duros de saída.

    Objetivo: evitar ToolMessage gigantes (ex.: arquivos grandes) que podem quebrar
    o `SummarizationMiddleware`/contexto do agente. A tool:
      - lê apenas um intervalo de linhas [start, end];
      - força um limite de linhas (`max_lines`) mesmo se `end` for maior;
      - força um limite total de caracteres (`max_chars`) no output;
      - corta linhas individuais muito longas (`max_line_chars`).

    Observação de indexação:
      - Entrada `start`/`end` é 1-indexed (mais natural para humanos).
      - Saída é numerada em 0-indexed (estilo VS Code), alinhada à esquerda.

    Args:
        path: Caminho do arquivo a ser lido (relativo ou absoluto).
        start: Linha inicial (1-indexed, inclusiva).
        end: Linha final (1-indexed, inclusiva). Se None, assume start+max_lines-1.
        max_lines: Máximo de linhas retornadas no output.
        max_chars: Máximo aproximado de caracteres retornados no output.
        max_line_chars: Máximo de caracteres por linha antes de truncar.

    Returns:
        String com header (arquivo, intervalo, limites) e linhas numeradas.
        Pode incluir marcadores:
          - …[TRUNCATED_LINE] para linhas individuais truncadas;
          - …[TRUNCATED_OUTPUT_MAX_CHARS] se atingir `max_chars`;
          - [TRUNCATED] se o intervalo foi reduzido por `max_lines`;
          - [MORE] se existir mais conteúdo além do intervalo retornado.

    Raises:
        Nunca propaga exceções para o agente; retorna mensagens de erro em texto.
    """
    try:
        file_path = Path(path).resolve()

        if not file_path.exists():
            return f"Erro: O arquivo '{path}' não existe."
        if not file_path.is_file():
            return f"Erro: '{path}' não é um arquivo."

        start = int(start)
        if start < 1:
            start = 1

        max_lines = max(1, int(max_lines))
        max_chars = max(256, int(max_chars))
        max_line_chars = max(256, int(max_line_chars))

        truncated_by_lines = False
        if end is None:
            end = start + max_lines - 1
        else:
            end = int(end)
            if end < start:
                return f"Erro: Linha inicial ({start}) maior que linha final ({end})."
            if (end - start + 1) > max_lines:
                end = start + max_lines - 1
                truncated_by_lines = True

        selected: list[str] = []
        chars_used = 0
        reached_eof = False
        saw_any = False
        last_line_num_1idx = 0

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for i_1idx, raw in enumerate(f, start=1):
                    last_line_num_1idx = i_1idx
                    if i_1idx < start:
                        continue
                    if i_1idx > end:
                        # Tenta detectar se há mais conteúdo sem ler o resto inteiro.
                        peek = f.readline()
                        reached_eof = (peek == "")
                        break

                    saw_any = True
                    line = raw.rstrip("\n")

                    if len(line) > max_line_chars:
                        line = line[:max_line_chars] + " …[TRUNCATED_LINE]"

                    remaining = max_chars - chars_used
                    if remaining <= 0:
                        selected.append("…[TRUNCATED_OUTPUT_MAX_CHARS]")
                        break

                    if len(line) > remaining:
                        selected.append(line[:remaining] + " …[TRUNCATED_OUTPUT_MAX_CHARS]")
                        break

                    selected.append(line)
                    chars_used += len(line) + 1  # +1 ~ newline

                else:
                    reached_eof = True

        except UnicodeDecodeError:
            return f"Erro: '{path}' parece ser um arquivo binário e não pode ser lido como texto."
        except PermissionError:
            return f"Erro: Sem permissão para ler '{path}'."

        if not saw_any:
            return f"Erro: Linha inicial {start} excede o total de linhas ({last_line_num_1idx})."

        start0 = start - 1
        end0 = end - 1
        line_num_width = len(str(end0))

        numbered_lines = []
        for idx0, line in enumerate(selected, start=start0):
            line_num_str = str(idx0).ljust(line_num_width)
            numbered_lines.append(f"{line_num_str}     {line}")

        total_info = str(last_line_num_1idx) if reached_eof else f"> {end}"
        header = (
            f"Arquivo: {file_path}\n"
            f"Linhas: {start0}-{end0} (0-indexed) | Total: {total_info}\n"
            f"Max_lines: {max_lines} | Max_chars: {max_chars}\n"
            + "-" * 60
            + "\n"
        )

        footer_parts = []
        if truncated_by_lines:
            footer_parts.append("[TRUNCATED] intervalo reduzido por max_lines")
        if not reached_eof:
            footer_parts.append("[MORE] arquivo tem mais conteúdo além do intervalo")

        footer = ("\n" + "-" * 60 + "\n" + " | ".join(footer_parts)) if footer_parts else ""
        return header + "\n".join(numbered_lines) + footer

    except Exception as e:
        return f"Erro ao ler arquivo: {e}"


@tool
def write_file(
    path: str,
    content: str,
    append: bool = False,
    max_content_chars: int = 200_000,
) -> str:
    """
    Escreve conteúdo em um arquivo com limite duro no tamanho do input.

    Motivo do limite: se o agente tentar escrever blobs muito grandes (por exemplo,
    um arquivo inteiro “na raça”), isso pode estourar o contexto e também gerar
    logs/traços enormes.

    Args:
        path: Caminho do arquivo a ser criado/sobrescrito (relativo ou absoluto).
        content: Conteúdo textual a ser escrito.
        append: Se True, adiciona ao final do arquivo; se False, sobrescreve.
        max_content_chars: Máximo de caracteres aceitos em `content`. Se exceder,
            o conteúdo é truncado e um marcador é adicionado.

    Returns:
        Mensagem de confirmação com o caminho resolvido do arquivo.
        Se truncar, adiciona o marcador: ...[TRUNCATED_INPUT_MAX_CHARS]

    Raises:
        Nunca propaga exceções para o agente; retorna mensagens de erro em texto.
    """
    try:
        file_path = Path(path).resolve()
        file_path.parent.mkdir(parents=True, exist_ok=True)

        max_content_chars = max(1_000, int(max_content_chars))
        if content is None:
            content = ""
        if len(content) > max_content_chars:
            content = content[:max_content_chars] + "\n...[TRUNCATED_INPUT_MAX_CHARS]"

        if append:
            with open(file_path, "a", encoding="utf-8") as f:
                if f.tell() > 0:
                    f.write("\n\n")
                f.write(content)
            action = "teve conteúdo adicionado"
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
def remove_draft_file(path: str) -> str:
    """
    Remove (delete) um arquivo chamado exatamente 'DRAFT.md'.

    Esta tool é propositalmente restrita para reduzir risco operacional:
    ela só permite apagar um arquivo com nome 'DRAFT.md'. Qualquer outro
    nome é recusado.

    Args:
        path: Caminho para o arquivo 'DRAFT.md' (relativo ou absoluto).

    Returns:
        Mensagem de confirmação ao remover, ou mensagem de erro se:
          - o arquivo não existir;
          - não for um arquivo regular;
          - não tiver permissão;
          - o nome não for exatamente 'DRAFT.md'.
    """
    try:
        p = Path(path).resolve()
        
        if not p.exists():
            return f"Erro: O arquivo '{p}' não existe."
        if not p.is_file():
            return f"Erro: '{p}' não é um arquivo."
        
        os.remove(p)
        
        return f"Arquivo removido com sucesso: {p}"

    except PermissionError:
        return f"Erro: Sem permissão para remover '{path}'."
    except Exception as e:
        return f"Erro ao remover arquivo:\n{e}"
