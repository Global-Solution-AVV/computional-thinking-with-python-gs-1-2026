# IceTrack - Monitoramento de Geleiras via Dados Satelitais

Projeto desenvolvido para a Global Solution 2026 da disciplina **Computational Thinking with Python**.

O IceTrack é uma solução em Python para análise da extensão de gelo marinho no Ártico e na Antártida, utilizando dados satelitais históricos do NSIDC. O sistema executa pelo terminal e permite ao usuário consultar informações, calcular variações percentuais, gerar relatórios, comparar regiões e executar uma modelagem matemática exponencial relacionada ao comportamento da extensão glacial ao longo do tempo.

## Integrantes

| Nome | RM |
| --- | --- |
| Artur Fabi Brandi | 570258 |
| Victor Bertacchini De Godoy | 571452 |
| Victor Lula Heineken Rodrigues | 570782 |

## Objetivo

O objetivo do projeto é transformar dados ambientais obtidos por sensoriamento remoto em informações compreensíveis para análise climática. A solução ajuda a observar tendências de redução ou aumento da extensão glacial, comparar o comportamento entre hemisférios e interpretar os impactos por meio de cálculos, relatórios e modelagem matemática.

## Funcionalidades

O menu principal possui cinco opções:

1. **Sobre o IceTrack**
   Apresenta uma descrição textual da solução e do problema abordado.

2. **Calcular variação percentual entre dois anos**
   Solicita a região, o ano de referência e o ano de comparação. Em seguida, calcula a diferença em milhões de km² e a variação percentual da extensão glacial média anual.

3. **Gerar relatório de tendência**
   Cria um arquivo `.txt` com médias por década, tendência geral, taxa anual média e ranking dos anos com maior e menor extensão média.

4. **Comparar Ártico vs Antártico**
   Compara os dados anuais das duas regiões e exibe um resumo consolidado com variação total, médias e extremos históricos.

5. **Modelagem matemática exponencial**
   Ajusta uma função exponencial aos dados históricos, calcula domínio, imagem, monotonia, derivada, integral acumulada, meia-vida glacial e projeções futuras. Quando `numpy` e `matplotlib` estão instalados, também gera um gráfico `.png`.

## Conceitos de Python aplicados

- Estruturas de decisão: `if`, `elif`, `else` e `match-case`.
- Estruturas de repetição: `while` e `for`.
- Sequências: listas e strings.
- Funções e procedimentos com `def`.
- Passagem de parâmetros e retorno de função.
- Leitura de arquivos CSV.
- Escrita de arquivos `.txt`.
- Validação de entradas do usuário.
- Geração de gráficos com `matplotlib`.

## Estrutura do projeto

```txt
computional-thinking-with-python-gs-1-2026/
├── main.py
├── README.md
├── requirements.txt
└── dataset/
    ├── sea_level_noaa.csv
    ├── north/
    │   ├── N_01_extent_v4.0 (1).csv
    │   ├── N_02_extent_v4.0 (1).csv
    │   └── ...
    └── south/
        ├── S_01_extent_v4.0.csv
        ├── S_02_extent_v4.0.csv
        └── ...
```

Arquivos gerados durante a execução:

```txt
relatorio_N_1978_2025.txt
relatorio_S_1978_2025.txt
modelagem_dps_N_1978_2025.png
modelagem_dps_S_1978_2025.png
```

Os arquivos `.txt` são gerados pela opção de relatório. Os arquivos `.png` são gerados pela opção de modelagem matemática quando as dependências de gráfico estão instaladas.

## Requisitos

- Python 3.10 ou superior.
- Bibliotecas listadas em `requirements.txt`.

As principais bibliotecas externas usadas para a modelagem com gráficos são:

- `numpy`
- `matplotlib`

## Como instalar

Clone o repositório ou acesse a pasta do projeto:

```bash
cd /Users/vheineken/workspace/computional-thinking-with-python-gs-1-2026
```

Crie um ambiente virtual, se desejar:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como executar

Execute o arquivo principal pelo terminal:

```bash
python3 main.py
```

O sistema exibirá o menu:

```txt
[1]  Sobre o IceTrack
[2]  Calcular variacao percentual entre dois anos
[3]  Gerar relatorio de tendencia (.txt)
[4]  Comparar Artico vs Antartico
[5]  Modelagem matematica exponencial  [DPS]
[0]  Sair
```

## Exemplos de teste

### Descrição do projeto

```txt
Opção: 1
```

### Variação percentual do Ártico

```txt
Opção: 2
Região: N
Ano de referência: 1979
Ano de comparação: 2025
```

Resultado esperado:

```txt
Regiao       : Artico (Hemisferio Norte)
1979         : 12.35 M km2  (media anual)
2025         : 10.15 M km2  (media anual)
Diferenca    : -2.20 M km2
Variacao     : -17.81%
```

### Variação percentual da Antártida

```txt
Opção: 2
Região: S
Ano de referência: 1979
Ano de comparação: 2025
```

### Gerar relatório de tendência

```txt
Opção: 3
Região: N
```

Arquivo gerado:

```txt
relatorio_N_1978_2025.txt
```

### Comparar Ártico e Antártico

```txt
Opção: 4
```

### Modelagem matemática

```txt
Opção: 5
Região: N
```

Arquivo de gráfico gerado, caso as dependências estejam instaladas:

```txt
modelagem_dps_N_1978_2025.png
```

## Validações implementadas

O sistema valida entradas incorretas para melhorar a usabilidade:

- região inválida;
- ano fora do intervalo permitido;
- entrada não numérica em campos de ano;
- opção inexistente no menu.

Exemplo:

```txt
Regiao [N = Artico | S = Antartico]: F
[!] Informe N (Artico) ou S (Antartico).

Ano de referencia (mais antigo) (1979-2024): 1900
[!] Ano fora do intervalo valido (1979-2024).

Digite a opcao desejada: 10
[!] Opcao invalida. Escolha um numero entre 0 e 5.
```

## Fonte dos dados

Os dados de extensão de gelo marinho foram organizados a partir de arquivos CSV do **NSIDC Sea Ice Index**.

Fonte indicada no relatório gerado pelo sistema:

```txt
NSIDC Sea Ice Index - nsidc.org/data/g02135
```

O projeto também inclui o arquivo `dataset/sea_level_noaa.csv`, com dados de nível médio do mar da NOAA, mantido como base complementar para análises ambientais.

## Observações

- O ano de 2026 é desconsiderado no código por ser um ano incompleto.
- As unidades de extensão glacial são apresentadas em milhões de km².
- A opção de modelagem matemática funciona sem gráficos caso `numpy` e `matplotlib` não estejam instalados, mas exibe um aviso informando como instalar as bibliotecas.
- Os gráficos `.png` são salvos na raiz do projeto.
