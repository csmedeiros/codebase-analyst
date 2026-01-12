# Changelog

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
