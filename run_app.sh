#!/usr/bin/env bash

# Vai para a pasta do projeto e executa o app Python
cd "$(dirname "$0")" || exit 1
python main.py

# Pausa para ver mensagens de erro/saída após o app fechar
if [ $? -ne 0 ]; then
  echo "Erro ao executar main.py"
fi
read -n 1 -s -r -p "Pressione qualquer tecla para sair..."
