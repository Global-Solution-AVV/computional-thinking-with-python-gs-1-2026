import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
NORTH_DIR = os.path.join(DATASET_DIR, "north")
SOUTH_DIR = os.path.join(DATASET_DIR, "south")

MESES = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}

ANO_MAX = 2025  # 2026 desconsiderado por ser ano incompleto

# ── Parametros de nivel do mar (NOAA STAR altimetria, extraidos em mai/2025) ──
# Fonte: slr_sla_gbl_keep_all_66.csv — NOAA Laboratory for Satellite Altimetry
# Aceleracao calibrada aos cenarios medianos IPCC AR6 Tabela 9.10
_SL = {
    "ano_base":   2025,
    "nivel_base": 82.4,    # mm na escala NOAA STAR (media 1993-2012 = 0)
    "nivel_1993": -19.3,   # mm medio em 1993 na mesma escala
    "taxa":        4.29,   # mm/ano — regressao dos ultimos 8 anos
}
_ACCEL = {
    "Conservador  (SSP1-2.6)": 0.010,
    "Intermediario (SSP2-4.5)": 0.042,
    "Alto          (SSP5-8.5)": 0.148,
}


# ── Carregamento de dados ─────────────────────────────────────────────────────

def carregar_dados(regiao: str) -> list:
    """Carrega todos os CSVs mensais do NSIDC para 'N' (Ártico) ou 'S' (Antártico)."""
    diretorio = NORTH_DIR if regiao == "N" else SOUTH_DIR
    dados = []

    if not os.path.isdir(diretorio):
        print(f"  [ERRO] Diretório não encontrado: {diretorio}")
        return dados

    for nome_arquivo in sorted(os.listdir(diretorio)):
        if not nome_arquivo.endswith(".csv"):
            continue
        caminho = os.path.join(diretorio, nome_arquivo)
        with open(caminho, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            cabecalho = [col.strip() for col in next(reader)]
            for linha in reader:
                if len(linha) < len(cabecalho):
                    continue
                reg = {cabecalho[i]: linha[i].strip() for i in range(len(cabecalho))}
                try:
                    extent = float(reg["extent"])
                    area = float(reg["area"])
                except (ValueError, KeyError):
                    continue
                ano = int(reg["year"])
                if extent == -9999.0 or area == -9999.0 or ano > ANO_MAX:
                    continue
                dados.append({
                    "ano": ano,
                    "mes": int(reg["mo"]),
                    "extent": extent,
                    "area": area,
                })

    dados.sort(key=lambda x: (x["ano"], x["mes"]))
    return dados


def calcular_media_anual(dados: list) -> dict:
    """Retorna dicionário {ano: média_anual_de_extent}."""
    acumulado = {}
    for reg in dados:
        ano = reg["ano"]
        if ano not in acumulado:
            acumulado[ano] = [0.0, 0]
        acumulado[ano][0] += reg["extent"]
        acumulado[ano][1] += 1
    return {ano: soma / cont for ano, (soma, cont) in acumulado.items()}


# ── Utilitários de UI ─────────────────────────────────────────────────────────

def linha(char="─", largura=64):
    print(char * largura)


def titulo(texto: str):
    linha("═")
    print(f"  {texto}")
    linha("═")


def pausar():
    input("\n  [ Pressione ENTER para voltar ao menu ]")


def pedir_regiao() -> str:
    while True:
        r = input("  Regiao [N = Artico | S = Antartico]: ").strip().upper()
        if r in ("N", "S"):
            return r
        print("  [!] Informe N (Artico) ou S (Antartico).")


def pedir_ano(rotulo: str, minimo: int = 1979, maximo: int = ANO_MAX) -> int:
    while True:
        try:
            ano = int(input(f"  {rotulo} ({minimo}-{maximo}): ").strip())
            if minimo <= ano <= maximo:
                return ano
            print(f"  [!] Ano fora do intervalo valido ({minimo}-{maximo}).")
        except ValueError:
            print("  [!] Entrada invalida. Digite um numero inteiro.")


def nome_regiao(regiao: str) -> str:
    if regiao == "N":
        return "Artico (Hemisferio Norte)"
    else:
        return "Antartico (Hemisferio Sul)"


# ── Opcao 1: Sobre o IceTrack ─────────────────────────────────────────────────

def sobre_icetrack():
    titulo("SOBRE O ICETRACK")
    print("  IceTrack e uma plataforma de analise do degelo glacial baseada em dados")
    print("  satelitais do NSIDC (National Snow and Ice Data Center), desde 1979.")
    print("  Processa series historicas de extensao de gelo marinho do Artico e do")
    print("  Antartico, calcula tendencias, identifica recordes e gera relatorios,")
    print("  apoiando pesquisadores e gestores publicos na crise climatica global.")
    pausar()


# ── Opcao 2: Exibir dados por periodo ────────────────────────────────────────

def exibir_dados_por_periodo():
    titulo("EXTENSAO GLACIAL POR PERIODO")
    regiao = pedir_regiao()
    ano_ini = pedir_ano("Ano inicial", 1979, 2024)
    ano_fim = pedir_ano("Ano final  ", ano_ini, ANO_MAX)

    print(f"\n  Carregando {nome_regiao(regiao)}...")
    dados = carregar_dados(regiao)
    filtrados = [r for r in dados if ano_ini <= r["ano"] <= ano_fim]

    if not filtrados:
        print("  [!] Nenhum dado encontrado para o periodo informado.")
        pausar()
        return

    medias_anuais = calcular_media_anual(filtrados)

    print(f"\n  {'Ano':>6}  {'Mes':>4}  {'Extensao (M km2)':>18}  {'Area (M km2)':>14}")
    linha()

    ultimo_ano = None
    for r in filtrados:
        if r["ano"] != ultimo_ano:
            if ultimo_ano is not None:
                media = medias_anuais.get(ultimo_ano, 0.0)
                print(f"  {'':>6}  {'':>4}  {'Media anual  ->':>18}  {media:>14.2f}")
                linha("·")
            ultimo_ano = r["ano"]
        print(f"  {r['ano']:>6}  {MESES[r['mes']]:>4}  {r['extent']:>18.2f}  {r['area']:>14.2f}")

    if ultimo_ano is not None:
        media = medias_anuais.get(ultimo_ano, 0.0)
        print(f"  {'':>6}  {'':>4}  {'Media anual  ->':>18}  {media:>14.2f}")

    pausar()


# ── Opcao 3: Variacao percentual entre dois anos ──────────────────────────────

def calcular_variacao_percentual():
    titulo("VARIACAO PERCENTUAL ENTRE DOIS ANOS")
    regiao = pedir_regiao()
    ano1 = pedir_ano("Ano de referencia (mais antigo) ", 1979, 2024)
    ano2 = pedir_ano("Ano de comparacao (mais recente)", ano1 + 1, ANO_MAX)

    dados = carregar_dados(regiao)
    medias = calcular_media_anual(dados)

    if ano1 not in medias:
        print(f"  [!] Sem dados disponiveis para {ano1}.")
        pausar()
        return
    if ano2 not in medias:
        print(f"  [!] Sem dados disponiveis para {ano2}.")
        pausar()
        return

    m1 = medias[ano1]
    m2 = medias[ano2]
    diferenca = m2 - m1
    variacao = (diferenca / m1) * 100

    linha()
    print(f"  Regiao       : {nome_regiao(regiao)}")
    print(f"  {ano1}         : {m1:.2f} M km2  (media anual)")
    print(f"  {ano2}         : {m2:.2f} M km2  (media anual)")
    linha()
    print(f"  Diferenca    : {diferenca:+.2f} M km2")
    print(f"  Variacao     : {variacao:+.2f}%")
    linha()

    if variacao < -5:
        print(f"  ATENCAO: Reducao expressiva de {abs(variacao):.2f}% da extensao glacial.")
    elif variacao < 0:
        print(f"  Reducao de {abs(variacao):.2f}% da extensao glacial no periodo.")
    else:
        print(f"  Crescimento de {variacao:.2f}% da extensao glacial no periodo.")

    pausar()


# ── Opcao 4: Minima e maxima extensao ────────────────────────────────────────

def identificar_extremos():
    titulo("MINIMA E MAXIMA EXTENSAO REGISTRADA")
    regiao = pedir_regiao()

    dados = carregar_dados(regiao)

    if not dados:
        print("  [!] Sem dados disponiveis.")
        pausar()
        return

    medias = calcular_media_anual(dados)
    anos = sorted(medias.keys())

    ano_min = min(medias, key=medias.get)
    ano_max = max(medias, key=medias.get)
    reg_min = min(dados, key=lambda x: x["extent"])
    reg_max = max(dados, key=lambda x: x["extent"])

    linha()
    print(f"  Regiao  : {nome_regiao(regiao)}")
    print(f"  Periodo : {anos[0]} - {anos[-1]}  ({len(dados)} registros mensais)")
    linha()
    print("  [ MEDIAS ANUAIS ]")
    print(f"    Menor media anual : {ano_min}  ->  {medias[ano_min]:.2f} M km2")
    print(f"    Maior media anual : {ano_max}  ->  {medias[ano_max]:.2f} M km2")
    linha("·")
    print("  [ REGISTROS MENSAIS (valor absoluto) ]")
    print(f"    Menor extensao : {MESES[reg_min['mes']]}/{reg_min['ano']}  ->  {reg_min['extent']:.2f} M km2")
    print(f"    Maior extensao : {MESES[reg_max['mes']]}/{reg_max['ano']}  ->  {reg_max['extent']:.2f} M km2")
    linha()

    if anos[0] in medias and anos[-1] in medias:
        var = ((medias[anos[-1]] - medias[anos[0]]) / medias[anos[0]]) * 100
        print(f"  Variacao total ({anos[0]} -> {anos[-1]}): {var:+.2f}%")

    pausar()


# ── Opcao 5: Relatorio de tendencia ──────────────────────────────────────────

def gerar_relatorio_tendencia():
    titulo("GERAR RELATORIO DE TENDENCIA (.txt)")
    regiao = pedir_regiao()

    dados = carregar_dados(regiao)
    if not dados:
        print("  [!] Sem dados disponiveis.")
        pausar()
        return

    medias = calcular_media_anual(dados)
    anos = sorted(medias.keys())
    primeiro, ultimo = anos[0], anos[-1]

    decadas = {}
    for ano in anos:
        decada = (ano // 10) * 10
        if decada not in decadas:
            decadas[decada] = []
        decadas[decada].append(medias[ano])
    media_decada = {d: sum(v) / len(v) for d, v in decadas.items()}

    var_total = medias[ultimo] - medias[primeiro]
    taxa_anual = var_total / (ultimo - primeiro) if ultimo != primeiro else 0.0

    piores = sorted(medias.items(), key=lambda x: x[1])[:5]
    melhores = sorted(medias.items(), key=lambda x: x[1], reverse=True)[:5]

    sep = "=" * 64
    sep_m = "-" * 64

    linhas_rel = [
        sep,
        "  ICETRACK - RELATORIO DE TENDENCIA GLACIAL",
        sep,
        f"  Regiao       : {nome_regiao(regiao)}",
        f"  Periodo      : {primeiro} - {ultimo}",
        f"  Registros    : {len(dados)} medições no periodo",
        sep,
        "",
        "  MEDIAS POR DECADA (M km2)",
        sep_m,
    ]

    for decada in sorted(media_decada.keys()):
        linhas_rel.append(f"    {decada}s  ->  {media_decada[decada]:.2f} M km2")

    linhas_rel += [
        "",
        "  TENDENCIA GERAL",
        sep_m,
        f"  Extensao em {primeiro}  : {medias[primeiro]:.2f} M km2",
        f"  Extensao em {ultimo}  : {medias[ultimo]:.2f} M km2",
        f"  Variacao total    : {var_total:+.2f} M km2",
        f"  Taxa anual media  : {taxa_anual:+.4f} M km2/ano",
        "",
        "  TOP 5 - ANOS COM MENOR EXTENSAO MEDIA",
        sep_m,
    ]

    for rank, (ano, media) in enumerate(piores, 1):
        linhas_rel.append(f"    {rank}. {ano}  ->  {media:.2f} M km2")

    linhas_rel += [
        "",
        "  TOP 5 - ANOS COM MAIOR EXTENSAO MEDIA",
        sep_m,
    ]

    for rank, (ano, media) in enumerate(melhores, 1):
        linhas_rel.append(f"    {rank}. {ano}  ->  {media:.2f} M km2")

    linhas_rel += [
        "",
        sep,
        "  Fonte: NSIDC Sea Ice Index - nsidc.org/data/g02135",
        "  IceTrack - Global Solution 2026 | FIAP",
        sep,
    ]

    nome_arquivo = f"relatorio_{regiao}_{primeiro}_{ultimo}.txt"
    caminho = os.path.join(BASE_DIR, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_rel))

    print(f"\n  Relatorio gerado com sucesso!")
    print(f"  Arquivo: {nome_arquivo}")
    linha()
    for l in linhas_rel[:22]:
        print(l)
    print("  ...")

    pausar()


# ── Opcao 6: Projecao do nivel do oceano ─────────────────────────────────────

def _regressao_linear(xs: list, ys: list) -> tuple:
    """Retorna (taxa, intercepto) pela regressao linear de minimos quadrados."""
    n = len(xs)
    sx  = sum(xs)
    sy  = sum(ys)
    sxy = sum(xs[i] * ys[i] for i in range(n))
    sxx = sum(xs[i] ** 2    for i in range(n))
    denom = n * sxx - sx ** 2
    if denom == 0:
        return 0.0, sy / n
    taxa = (n * sxy - sx * sy) / denom
    intercepto = (sy - taxa * sx) / n
    return taxa, intercepto


def projetar_nivel_oceano():
    titulo("PROJECAO DO NIVEL DO OCEANO")

    ano_base   = _SL["ano_base"]
    nivel_base = _SL["nivel_base"]
    nivel_1993 = _SL["nivel_1993"]
    taxa       = _SL["taxa"]

    ano_alvo = pedir_ano("Ano alvo da projecao", ano_base + 1, 2100)
    dt = ano_alvo - ano_base

    def projeto(accel: float) -> float:
        return nivel_base + taxa * dt + 0.5 * accel * dt ** 2

    def ano_limiar(limiar_mm: float, accel: float) -> str:
        alvo = nivel_1993 + limiar_mm
        for delta_t in range(1, 300):
            if nivel_base + taxa * delta_t + 0.5 * accel * delta_t ** 2 >= alvo:
                return str(ano_base + delta_t)
        return ">2200"

    linha()
    print(f"  Alta acumulada (1993-{ano_base}): {nivel_base - nivel_1993:.0f} mm  "
          f"({(nivel_base - nivel_1993)/10:.1f} cm)")
    print(f"  Taxa atual                  : {taxa:.2f} mm/ano")
    linha()
    print(f"  PROJECAO PARA {ano_alvo}  (+{dt} anos)")
    linha()
    print(f"  {'Cenario':<30}  {'Alta c/ 1993 (cm)':>18}  {'Adicional (cm)':>16}")
    print(f"  {'':─<30}  {'':─>18}  {'':─>16}")
    for nome, accel in _ACCEL.items():
        sl    = projeto(accel)
        alta  = (sl - nivel_1993) / 10
        delta = (sl - nivel_base) / 10
        print(f"  {nome:<30}  {alta:>18.1f}  {delta:>+16.1f}")
    linha()
    print("  LIMIARES CRITICOS (ano estimado)")
    linha()
    nomes = list(_ACCEL.keys())
    for limiar_mm, label in [(500, "+50 cm"), (1000, "+100 cm")]:
        vals = [ano_limiar(limiar_mm, a) for a in _ACCEL.values()]
        print(f"  {label} acima de 1993:  "
              f"{nomes[0].split()[0]}={vals[0]}  "
              f"{nomes[1].split()[0]}={vals[1]}  "
              f"{nomes[2].split()[0]}={vals[2]}")

    pausar()




# ── Menu principal ────────────────────────────────────────────────────────────

def exibir_menu():
    print()
    linha("═")
    print("  *** ICETRACK - Monitoramento de Geleiras via Dados Satelitais ***")
    linha("═")
    print("  [1]  Sobre o IceTrack")
    print("  [2]  Exibir dados de extensao glacial por periodo")
    print("  [3]  Calcular variacao percentual entre dois anos")
    print("  [4]  Identificar minima e maxima extensao registrada")
    print("  [5]  Gerar relatorio de tendencia (.txt)")
    print("  [6]  Projetar nivel do oceano ate 2100")
    print("  [0]  Sair")
    linha("─")


def main():
    while True:
        exibir_menu()
        opcao = input("  Digite a opcao desejada: ").strip()

        match opcao:
            case "1":
                sobre_icetrack()
            case "2":
                exibir_dados_por_periodo()
            case "3":
                calcular_variacao_percentual()
            case "4":
                identificar_extremos()
            case "5":
                gerar_relatorio_tendencia()
            case "6":
                projetar_nivel_oceano()
            case "0":
                linha("═")
                print("  Encerrando o IceTrack. Ate logo!")
                linha("═")
                break
            case _:
                print("  [!] Opcao invalida. Escolha um numero entre 0 e 6.")


if __name__ == "__main__":
    main()
