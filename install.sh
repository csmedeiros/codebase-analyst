#!/bin/bash
# Script de instalação para Mac/Linux

set -e

echo "================================================"
echo "   Codebase Analyst - Script de Instalação"
echo "================================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "Por favor, instale Python 3.9 ou superior."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
echo "✓ Python encontrado: $(python3 --version)"

# Verificar pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip não encontrado!"
    echo "Por favor, instale pip."
    exit 1
fi

echo "✓ pip encontrado"
echo ""

# Perguntar sobre ambiente virtual
read -p "Deseja criar um ambiente virtual? (recomendado) [S/n]: " CREATE_VENV
CREATE_VENV=${CREATE_VENV:-S}

if [[ $CREATE_VENV =~ ^[Ss]$ ]]; then
    echo ""
    echo "Criando ambiente virtual..."
    python3 -m venv venv

    echo "✓ Ambiente virtual criado"
    echo ""
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
    echo "✓ Ambiente virtual ativado"
fi

echo ""
echo "Instalando pacote..."
pip install -e .

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "   ✓ Instalação concluída com sucesso!"
    echo "================================================"
    echo ""
    echo "Próximos passos:"
    echo ""
    echo "1. Configure sua OPENAI_API_KEY:"
    echo "   export OPENAI_API_KEY=sk-sua-chave-aqui"
    echo ""
    echo "   Ou crie um arquivo .env:"
    echo "   cp .env.example .env"
    echo "   # Edite o arquivo .env com sua chave"
    echo ""
    echo "2. Execute o comando:"
    echo "   codebase-analyst --help"
    echo ""
    echo "3. Analise um projeto:"
    echo "   codebase-analyst ./meu-projeto"
    echo ""

    if [[ $CREATE_VENV =~ ^[Ss]$ ]]; then
        echo "Nota: Para usar o comando novamente, ative o ambiente virtual:"
        echo "   source venv/bin/activate"
        echo ""
    fi
else
    echo ""
    echo "❌ Erro na instalação!"
    exit 1
fi
