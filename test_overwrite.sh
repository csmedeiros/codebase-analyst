#!/bin/bash
# Script para testar a funcionalidade de detecção de arquivos existentes

echo "========================================"
echo "Teste: Detecção de Arquivos Existentes"
echo "========================================"
echo ""

# Criar diretório de teste
TEST_DIR="/tmp/test-codebase-analyst"
mkdir -p "$TEST_DIR"

# Criar um README.md de teste
echo "# Existing README" > "$TEST_DIR/README.md"
echo "This is an existing README file." >> "$TEST_DIR/README.md"

# Criar um arquivo Python de exemplo
echo "print('Hello World')" > "$TEST_DIR/main.py"

echo "Diretório de teste criado: $TEST_DIR"
echo ""
echo "Conteúdo do diretório:"
ls -lh "$TEST_DIR"
echo ""
echo "========================================"
echo "README.md existente detectado!"
echo "========================================"
echo ""
echo "Ao executar o comando abaixo, você será perguntado se deseja sobrescrever:"
echo ""
echo "  codebase-analyst \"$TEST_DIR\" --task readme"
echo ""
echo "Se responder 'n' (não), o agente NÃO será executado."
echo "Se responder 's' (sim), o arquivo será sobrescrito."
echo ""
echo "Para testar, execute:"
echo "  codebase-analyst \"$TEST_DIR\" --task readme"
echo ""
