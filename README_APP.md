# Enriquecedor de Tabelas - CAIXA/VOTO

Aplicação desktop em Python para enriquecimento automático de tabelas de referência com informações de CAIXA e VOTO.

## 🎯 O que faz

Adiciona automaticamente 2 colunas à sua tabela de referência:
- **"Ta na caixa?"** - Indica se o processo está presente na concatenação das 2 planilhas CAIXA
- **"Tem voto?"** - Indica se o processo tem um voto registrado na tabela VOTO

## 📋 Requisitos

- Python 3.9+ (use Python 3.13 com `pandas==2.2.3` ou superior)
- Dependências: `pandas`, `openpyxl`

## 🚀 Como usar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Rodar a aplicação

```bash
python main.py
```

### 3. Usar a interface

1. **Selecionar arquivos CSV:**
   - Clique em "Selecionar" para as tabelas obrigatorias
   - Tabela de Referência
   - Planilha CAIXA 1
   - Planilha CAIXA 2 (opcional)
   - Tabela VOTO

2. **Processar:**
   - Clique em "Processar Tabelas"
   - Aguarde o processamento (o log mostra o progresso)

3. **Salvar resultado:**
   - Clique em "Salvar Resultado (Excel)"
   - Escolha onde salvar o arquivo `.xlsx`

## 📁 Estrutura de arquivos esperados

### Tabela de Referência
Deve conter uma coluna chamada `numeroProcesso` (ou ajuste o código) e outros dados.

```
numeroProcesso, nomeProcesso, partes, status
1001, Processo 1001, João Silva, Ativo
...
```

### Planilhas CAIXA
A Planilha CAIXA 1 e obrigatoria. A Planilha CAIXA 2 e opcional; quando informada, ela e concatenada com a CAIXA 1.

Devem ter pelo menos 3 colunas. A busca é feita na **coluna C (índice 2)**.

```
dados1, dados2, numeroProcesso, dados4
info_a, info_b, 1001, info_x
...
```

### Tabela VOTO
Devem ter pelo menos 3 colunas. A busca é feita na **coluna C (índice 2)**.

```
voto_id, voto_descricao, numeroProcesso, voto_tipo
v001, Voto Sim, 1001, Favorável
...
```

## 🔧 Arquivo de configuração

Se precisar mudar o nome da coluna de busca padrão (`numeroProcesso`), edite [processador.py](processador.py) linha 11:

```python
self.processador = ProcessadorTabelas(coluna_busca="SUA_COLUNA_AQUI")
```

## 📂 Arquivos do projeto

- **main.py** - Interface gráfica (Tkinter)
- **processador.py** - Lógica de processamento de dados
- **requirements.txt** - Dependências Python
- **teste_*.csv** - Arquivos de teste (pode deletar)
- **resultado_teste.xlsx** - Resultado de teste (pode deletar)

## 🧪 Testar

Arquivos de teste estão inclusos para validar o funcionamento:

```bash
python main.py
# Selecione: teste_referencia.csv, teste_caixa1.csv, teste_caixa2.csv, teste_voto.csv
# Clique em "Processar Tabelas"
# Salve como resultado_teste.xlsx
```

## 📝 Notas

- A busca é **case-sensitive**
- Valores vazios ou nulos são considerados como "NÃO encontrado"
- O resultado final contém TODAS as colunas da tabela de referência + 2 colunas novas
- Suporta arquivos grandes (testado com milhares de linhas)

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| "Coluna 'numeroProcesso' não encontrada" | Ajuste o nome da coluna em `main.py` linha que cria o processador |
| Erro ao carregar CSV | Verifique se o arquivo está em UTF-8 ou verifique separadores (,;) |
| Interface não abre | Verifique se `tkinter` está instalado (geralmente já vem com Python) |

## 📧 Suporte

Para problemas ou melhorias, revise o código ou execute com Python em modo debug.

---

**Versão:** 1.0  
**Data:** Maio 2026  
**Autor:** Assistente Copilot
