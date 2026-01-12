# Proteção de Sobrescrita de Arquivos

## Visão Geral

O Codebase Analyst agora inclui um mecanismo de proteção que detecta arquivos existentes antes de executar tarefas que geram documentação. Isso previne a perda acidental de conteúdo.

## Como Funciona

### Detecção Automática

Quando você executa uma tarefa que gera arquivos (`--task readme` ou `--task architecture`), o CLI:

1. **Verifica** se o arquivo de destino já existe no diretório
2. **Exibe informações** sobre o arquivo existente (caminho, tamanho, data de modificação)
3. **Solicita confirmação** antes de continuar
4. **Cancela a operação** se você não confirmar

### Arquivos Protegidos

| Tarefa | Arquivo Protegido |
|--------|-------------------|
| `--task readme` | `README.md` |
| `--task architecture` | `ARCHITECTURE.md` |
| `--task analyze` | Nenhum (não cria arquivos) |

## Fluxo de Uso

### Cenário 1: Arquivo Não Existe

```bash
$ codebase-analyst ./meu-projeto --task readme

# Executa normalmente, cria README.md
```

### Cenário 2: Arquivo Existe - Usuário Confirma

```bash
$ codebase-analyst ./meu-projeto --task readme

⚠ Aviso: O arquivo 'README.md' já existe no diretório!

Arquivo:     /caminho/para/meu-projeto/README.md
Tamanho:     2048 bytes
Modificado:  2026-01-12 08:30:45

Este arquivo será SOBRESCRITO se você continuar.

Deseja continuar e sobrescrever o arquivo? [s/N]: s

✓ Arquivo 'README.md' será sobrescrito

# Agente é executado e README.md é sobrescrito
```

### Cenário 3: Arquivo Existe - Usuário Cancela

```bash
$ codebase-analyst ./meu-projeto --task readme

⚠ Aviso: O arquivo 'README.md' já existe no diretório!

Arquivo:     /caminho/para/meu-projeto/README.md
Tamanho:     2048 bytes
Modificado:  2026-01-12 08:30:45

Este arquivo será SOBRESCRITO se você continuar.

Deseja continuar e sobrescrever o arquivo? [s/N]: n

✗ Operação cancelada - arquivo 'README.md' preservado

# Agente NÃO é executado, arquivo original preservado
```

## Opções de Resposta

O prompt aceita as seguintes respostas:

**Para continuar (sobrescrever):**
- `s`, `S` (sim)
- `sim`, `SIM`
- `y`, `Y` (yes)
- `yes`, `YES`

**Para cancelar (padrão):**
- `n`, `N` (não)
- `nao`, `não`, `NAO`, `NÃO`
- Qualquer outra resposta
- Enter (vazio) - **padrão é NÃO**
- Ctrl+C (KeyboardInterrupt)

## Informações Exibidas

Quando um arquivo existente é detectado, o CLI mostra:

1. **⚠ Aviso** em destaque amarelo
2. **Informações do arquivo:**
   - Caminho completo
   - Tamanho em bytes
   - Data e hora da última modificação
3. **Aviso de sobrescrita** com texto "SOBRESCRITO" em vermelho
4. **Prompt de confirmação** com padrão [N]

## Segurança

### Proteção Padrão

O comportamento padrão é **NÃO sobrescrever**. Isso significa:
- Se você pressionar Enter sem digitar nada, o arquivo é preservado
- Você precisa explicitamente confirmar com `s` ou `sim` para sobrescrever
- Interrupção (Ctrl+C) também cancela a operação

### Sem Opção --force

Propositalmente **não há opção `--force`** ou `--overwrite` para bypass automático. Isso garante que:
- Você sempre será perguntado quando um arquivo existe
- Scripts automatizados não podem sobrescrever acidentalmente
- É necessário confirmação manual do usuário

## Casos de Uso

### Desenvolvimento Iterativo

Durante o desenvolvimento, você pode gerar documentação múltiplas vezes:

```bash
# Primeira vez - cria README.md
codebase-analyst . --task readme

# Você faz mudanças no código...

# Segunda vez - pergunta antes de sobrescrever
codebase-analyst . --task readme
# Responda 's' para atualizar a documentação
```

### Preservar Documentação Manual

Se você editou manualmente a documentação gerada:

```bash
# Você já editou README.md manualmente
# Tenta gerar novamente

codebase-analyst . --task readme
# Responda 'n' para preservar suas edições
```

### Backup Antes de Sobrescrever

Fluxo recomendado para não perder conteúdo:

```bash
# 1. Fazer backup do arquivo existente
cp README.md README.md.backup

# 2. Executar o gerador
codebase-analyst . --task readme
# Responda 's' para sobrescrever

# 3. Comparar versões
diff README.md README.md.backup

# 4. Mesclar conteúdo se necessário
```

## Implementação Técnica

### Função de Verificação

```python
def check_existing_file(target_path: Path, task: str) -> bool:
    """Verifica se arquivo já existe e pergunta ao usuário."""
    # Retorna True se pode continuar
    # Retorna False se usuário cancelou
```

### Integração no Fluxo

A verificação ocorre **após** as validações iniciais mas **antes** de criar o agente:

1. Validar API key
2. Validar caminho do diretório
3. **→ Verificar arquivo existente** ←
4. Criar agente
5. Executar tarefa

Isso economiza recursos ao não criar o agente se o usuário vai cancelar.

## Testes

### Script de Teste

Um script de teste está disponível:

```bash
./test_overwrite.sh
```

Este script:
1. Cria um diretório de teste
2. Gera um README.md de exemplo
3. Fornece instruções para testar a funcionalidade

### Teste Manual

```bash
# 1. Criar diretório de teste
mkdir /tmp/test-project
echo "# Old README" > /tmp/test-project/README.md

# 2. Tentar gerar README
codebase-analyst /tmp/test-project --task readme

# 3. Verificar que foi perguntado sobre sobrescrita
# 4. Testar ambos os cenários (sim/não)
```

## Compatibilidade

Esta funcionalidade é compatível com:

- ✅ Mac (testado)
- ✅ Windows (suportado via input())
- ✅ Linux (suportado)
- ✅ Ambientes não-interativos (usa sys.exit(0) em caso de EOF)

## Limitações Conhecidas

1. **Tarefa 'analyze'**: Não cria arquivos, então não há verificação
2. **Arquivos em subdiretórios**: Apenas verifica na raiz do projeto
3. **Backup automático**: Não faz backup, recomenda-se fazer manualmente
4. **Histórico Git**: Não verifica se arquivo está versionado

## Melhorias Futuras

Possíveis melhorias:

- [ ] Opção para criar backup automático (.bak)
- [ ] Detectar se arquivo está em controle de versão (git status)
- [ ] Preview das diferenças antes de sobrescrever
- [ ] Modo --interactive para sempre perguntar
- [ ] Modo --quiet para ambientes CI/CD (com erro se arquivo existe)

## Referências

- Código: [src/cli.py](src/cli.py) - função `check_existing_file()`
- Testes: [test_overwrite.sh](test_overwrite.sh)
