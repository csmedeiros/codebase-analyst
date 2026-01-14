# Modificações do System Prompt - ONBOARDING.md

## Resumo
O agente foi modificado para gerar **ONBOARDING.md** em vez de README.md ou ARCHITECTURE.md, com foco em facilitar o onboarding de novos desenvolvedores.

## Arquivos Modificados

### 1. `src/prompts.py` (Principal)

#### Seção `<goal>`
- Alterado objetivo para gerar ONBOARDING.md
- Reforçado: "Permitir que programadores que entram no meio do projeto consigam entender o código de maneira mais fácil e rápida"

#### Seção `<onboarding_requirements>` (Nova)
Adicionadas 13 seções obrigatórias para ONBOARDING.md:

1. **Visão Geral do Projeto** - Descrição concisa, objetivos e tecnologias
2. **Sumário** - Tabela de conteúdos navegável
3. **Estrutura do Projeto** - Árvore ASCII com descrições de cada diretório
4. **Pontos de Entrada** - TODOS os entry points mapeados com diagramas
5. **Arquivos Principais** - Arquivos-chave por categoria (config, entry points, core, integrações, utils)
6. **Fluxos Principais** - Diagramas ASCII dos fluxos mais importantes
7. **Configuração e Variáveis de Ambiente** - Config vars com explicações
8. **Dependências Externas** - Frameworks, bibliotecas, integrações externas
9. **Guia de "Onde Encontrar"** - Q&A prático para tarefas comuns (CRÍTICO)
10. **Como Começar** - Guia de instalação passo a passo
11. **Arquitetura e Padrões** - Padrão arquitetural, camadas, comunicação
12. **Conceitos Importantes** - Terminologia, convenções, padrões de design
13. **Roteiro de Leitura do Código** - Guia estruturado de por onde COMEÇAR (CRÍTICO)

#### Seção 9: "Onde Encontrar" (Where to Find What) - CRÍTICO
Formato de Q&A prático:
- "Onde estão as rotas da API?" → `src/api/routes.py`
- "Onde adicionar um novo endpoint?" → `src/api/routes.py + src/services/`
- "Onde estão as migrations?" → `migrations/` ou `alembic/`
- etc.

#### Seção 13: "Roteiro de Leitura do Código" (Code Reading Roadmap) - CRÍTICO
- Ordem sugerida de leitura em FASES estruturadas
- Para cada arquivo: o que você vai aprender, conceitos que ficarão claros
- Conexões entre componentes (imports, dependências, dependentes)
- Próximo passo lógico após entender cada arquivo
- Estrutura: FASE 1 (Entry Point) → FASE 2 (Rotas) → FASE 3 (Lógica) → FASE 4 (BD) → FASE 5 (Integrações)

#### Seção `<few_shot_execution_examples>` (Nova)
5 exemplos detalhados de ações CORRETAS e INCORRETAS:

1. **LOOP PREVENTION com DRAFT.md**
   - ❌ Reler arquivo já processado
   - ✅ Verificar DRAFT.md e continuar do próximo alvo

2. **CLAIMS COM EVIDÊNCIA**
   - ❌ Especulação sem base
   - ✅ Evidência observada com path + line numbers

3. **NEXT TARGETS DETERMINÍSTICO**
   - ❌ Próximos passos vagos
   - ✅ Específico e priorizado (PRIORITY 1/2/3)

4. **DIAGRAMA ASCII DETALHADO**
   - ❌ Diagrama muito simples
   - ✅ Diagrama com componentes reais e linhas de código

5. **FINALIZAÇÃO CORRETA**
   - ❌ Gerar ONBOARDING.md e esquecer de deletar DRAFT.md
   - ✅ Sequência: gerar → deletar DRAFT.md IMEDIATAMENTE → confirmar

#### Reforço do DRAFT.md
- Claramente reforçado como "fonte única de verdade"
- Cleanup obrigatório: `remove_draft_file("DRAFT.md")` IMEDIATAMENTE após gerar ONBOARDING.md
- DRAFT.md deve ser deletado e NÃO permanecer no repositório do usuário

#### 10 Princípios Críticos (Resumo)
1. SEMPRE ler DRAFT.md antes de qualquer ação
2. NUNCA reler arquivos em "Files Read (Index)"
3. SEMPRE ler arquivos em blocos (end parameter obrigatório)
4. SEMPRE registrar evidências com path + line numbers
5. SEMPRE atualizar DRAFT.md após cada ação significativa
6. SEMPRE gerar ONBOARDING.md completo (13 seções)
7. SEMPRE deletar DRAFT.md imediatamente após gerar ONBOARDING.md
8. NUNCA especular sem observação direta
9. NUNCA explorar diretórios irrelevantes (node_modules, .git, venv, etc.)
10. SEMPRE usar diagramas ASCII detalhados

### 2. `src/cli.py` (Atualizado)

#### Mudanças na função `main()`
- **--task choices**: `["analyze", "readme", "architecture"]` → `["analyze", "onboarding"]`
- **--task default**: `"analyze"` → `"onboarding"`
- **Descrição**: Atualizada para focar em onboarding de novos desenvolvedores
- **Exemplos**: Atualizados com novo fluxo

#### Mudanças em `check_existing_file()`
- **file_mapping**: Alterado para `{"onboarding": "ONBOARDING.md"}`
- Apenas ONBOARDING.md é verificado/sobrescrito

#### task_prompts
- Removido: `"readme"`, `"architecture"`
- Adicionado: `"onboarding"` com prompt detalhado explicando o objetivo do arquivo

#### Exemplos de uso
```bash
codebase-analyst ./meu-projeto                    # Gera ONBOARDING.md
codebase-analyst . --task onboarding --model gpt-4o
codebase-analyst ./repo --task analyze            # Apenas análise
```

## Benefícios das Modificações

### Para Novos Desenvolvedores
- ✅ Guia de por onde começar a ler o código (Seção 13)
- ✅ Q&A prático "Onde encontrar o quê" (Seção 9)
- ✅ Diagramas ASCII claros de fluxos e arquitetura
- ✅ Roteiro estruturado em fases
- ✅ Explicações de o que aprender em cada etapa

### Para o Agente
- ✅ Maior precisão com few-shot examples
- ✅ Loop prevention garantido via DRAFT.md
- ✅ Cleanup obrigatório de artefatos temporários
- ✅ 13 seções bem-definidas e estruturadas
- ✅ Critérios claros de sucesso

## Uso

### Comando Default (recomendado)
```bash
codebase-analyst ./path/to/project
```
Gera ONBOARDING.md completo na raiz do projeto.

### Análise sem documentação
```bash
codebase-analyst ./path/to/project --task analyze
```
Apenas análise, sem gerar arquivo.

### Especificar modelo
```bash
codebase-analyst ./path/to/project --model anthropic:claude-3-5-sonnet-20241022
```

## Estrutura Final do ONBOARDING.md

O arquivo gerado terá estrutura clara e hierárquica:

```
# ONBOARDING - [Nome do Projeto]

## 1. Visão Geral do Projeto
## 2. Sumário
## 3. Estrutura do Projeto
## 4. Pontos de Entrada
## 5. Arquivos Principais
## 6. Fluxos Principais
## 7. Configuração e Variáveis de Ambiente
## 8. Dependências Externas
## 9. Guia de "Onde Encontrar"
## 10. Como Começar
## 11. Arquitetura e Padrões
## 12. Conceitos Importantes
## 13. Roteiro de Leitura do Código
```

## Compatibilidade
- ✅ Totalmente compatível com contexto sumarizado
- ✅ DRAFT.md garante recuperação após sumarização
- ✅ Sem perda de progresso entre sessões

---
**Data**: 2026-01-12
**Status**: ✅ Implementado e testado
