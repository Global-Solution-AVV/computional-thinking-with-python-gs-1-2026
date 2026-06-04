import csv
import math
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
NORTH_DIR = os.path.join(DATASET_DIR, "north")
SOUTH_DIR = os.path.join(DATASET_DIR, "south")

ANO_MAX = 2025  # 2026 desconsiderado por ser ano incompleto


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


# ── Opcao 2: Variacao percentual entre dois anos ─────────────────────────────

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


# ── Opcao 3: Relatorio de tendencia ──────────────────────────────────────────

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


# ── Regressao linear (auxiliar) ──────────────────────────────────────────────

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



# ── Opcao 4: Comparar Artico vs Antartico ────────────────────────────────────

def comparar_regioes():
    titulo("COMPARAR ARTICO VS ANTARTICO")

    print("  Carregando Artico (N)...")
    dados_n = carregar_dados("N")
    print("  Carregando Antartico (S)...")
    dados_s = carregar_dados("S")

    if not dados_n or not dados_s:
        print("  [!] Dados insuficientes para comparacao.")
        pausar()
        return

    medias_n = calcular_media_anual(dados_n)
    medias_s = calcular_media_anual(dados_s)
    anos_comuns = sorted(set(medias_n.keys()) & set(medias_s.keys()))

    if not anos_comuns:
        print("  [!] Sem anos em comum entre as regioes.")
        pausar()
        return

    primeiro, ultimo = anos_comuns[0], anos_comuns[-1]

    print(f"\n  {'Ano':>6}  {'Artico (M km2)':>16}  {'Antartico (M km2)':>18}  {'Dif. (N-S)':>12}")
    linha()

    for ano in anos_comuns:
        n_val = medias_n[ano]
        s_val = medias_s[ano]
        dif   = n_val - s_val
        print(f"  {ano:>6}  {n_val:>16.2f}  {s_val:>18.2f}  {dif:>+12.2f}")

    linha()

    var_n    = ((medias_n[ultimo] - medias_n[primeiro]) / medias_n[primeiro]) * 100
    var_s    = ((medias_s[ultimo] - medias_s[primeiro]) / medias_s[primeiro]) * 100
    media_n  = sum(medias_n[a] for a in anos_comuns) / len(anos_comuns)
    media_s  = sum(medias_s[a] for a in anos_comuns) / len(anos_comuns)
    min_n    = min(medias_n, key=medias_n.get)
    min_s    = min(medias_s, key=medias_s.get)
    max_n    = max(medias_n, key=medias_n.get)
    max_s    = max(medias_s, key=medias_s.get)

    print(f"  RESUMO COMPARATIVO  ({primeiro} - {ultimo})")
    linha()
    print(f"  {'Indicador':<32}  {'Artico':>10}  {'Antartico':>11}")
    linha("·")
    print(f"  {'Variacao total':.<32}  {var_n:>+9.2f}%  {var_s:>+10.2f}%")
    print(f"  {'Media do periodo (M km2)':.<32}  {media_n:>10.2f}  {media_s:>11.2f}")
    print(f"  {'Menor extensao media: ano':.<32}  {min_n:>10}  {min_s:>11}")
    print(f"  {'Menor extensao media: valor':.<32}  {medias_n[min_n]:>10.2f}  {medias_s[min_s]:>11.2f}")
    print(f"  {'Maior extensao media: ano':.<32}  {max_n:>10}  {max_s:>11}")
    print(f"  {'Maior extensao media: valor':.<32}  {medias_n[max_n]:>10.2f}  {medias_s[max_s]:>11.2f}")
    linha()

    pausar()


# ── Opcao 5: Modelagem Matematica Exponencial (DPS) ───────────────────────────

def modelagem_matematica():
    titulo("MODELAGEM MATEMATICA EXPONENCIAL  [DPS]")

    try:
        import numpy as np
        import matplotlib.pyplot as plt
        tem_libs = True
    except ImportError:
        tem_libs = False

    regiao = pedir_regiao()
    print(f"\n  Carregando {nome_regiao(regiao)}...")
    dados  = carregar_dados(regiao)
    medias = calcular_media_anual(dados)
    anos   = sorted(medias.keys())

    if len(anos) < 5:
        print("  [!] Dados insuficientes para modelagem.")
        pausar()
        return

    ano_base = anos[0]
    t_vals   = [float(a - ano_base) for a in anos]
    a_vals   = [medias[a]           for a in anos]

    # Fit exponencial: A(t) = A0 * e^(-k*t)
    # Linearizacao: ln(A) = ln(A0) - k*t  →  regressao linear de (t, ln(A))
    log_a      = [math.log(a) for a in a_vals]
    slope, intercept = _regressao_linear(t_vals, log_a)
    k          = -slope                # taxa positiva = decrescente
    A0         = math.exp(intercept)   # extensao inicial estimada

    T     = t_vals[-1]
    dA_t0 = -k * A0                              # A'(0)
    dA_tT = -k * A0 * math.exp(-k * T)          # A'(T)

    # Meia-vida: A(t) = A0/2  =>  t = ln(2)/k
    if k > 0:
        t_half   = math.log(2) / k
        ano_half = ano_base + t_half
    else:
        t_half = ano_half = None

    # Integral acumulada no periodo: integral(0..T) de A(t)dt = A0/k*(1-e^(-kT))
    area_acum = (A0 / k) * (1.0 - math.exp(-k * T)) if k != 0 else A0 * T

    # Coeficiente nivel do mar: 0.073 mm por 1000 km2 = 73 mm por M km2
    C_MM = 73.0

    linha()
    print("  MODELO PRINCIPAL: A(t) = A0 * e^(-k*t)")
    print("  A(t) = extensao glacial no ano t  [M km2]")
    print("  A0   = extensao inicial estimada  [M km2]")
    print("  k    = taxa de degelo calibrada aos dados NSIDC  [1/ano]")
    print(f"  t    = anos desde {ano_base}  (t=0 em {ano_base})")
    linha()
    print("  PARAMETROS AJUSTADOS (regressao log-linear sobre dados reais):")
    print(f"    A0 = {A0:.4f} M km2")
    print(f"    k  = {k:.6f} ao ano  ({'decrescente' if k > 0 else 'crescente'})")
    linha()
    print("  ANALISE MATEMATICA DA FUNCAO:")
    print(f"    Dominio  :  t in [0, +inf)  =>  anos [{ano_base}, +inf)")
    if k > 0:
        print(f"    Imagem   :  (0, {A0:.2f}]  M km2")
        print( "    Monotonia:  estritamente decrescente  |  A'(t) < 0 para todo t")
        print( "    Concavidade: convexa (A''(t) = k^2*A0*e^(-kt) > 0)")
    else:
        print(f"    Imagem   :  [{A0:.2f}, +inf)  M km2")
        print( "    Monotonia:  estritamente crescente  |  A'(t) > 0 para todo t")
    linha()
    print("  DERIVADA: A'(t) = -k * A0 * e^(-k*t)")
    print(f"    A'(0)  = {dA_t0:+.4f} M km2/ano  (taxa em {ano_base})")
    print(f"    A'({T:.0f}) = {dA_tT:+.4f} M km2/ano  (taxa em {anos[-1]})")
    linha()
    if t_half is not None:
        print("  MEIA-VIDA GLACIAL:")
        print(f"    A(t) = A0/2  quando  t = ln(2)/k = {t_half:.1f} anos")
        print(f"    Estimativa: ano {ano_half:.0f}  (extensao cai para {A0/2:.2f} M km2)")
        linha()
    print(f"  INTEGRAL acumulada ({ano_base}-{anos[-1]}):")
    print(f"    integral(0..{T:.0f}) A(t) dt = A0/k * (1 - e^(-k*T)) = {area_acum:.1f} M km2*ano")
    linha()
    print(f"  2a FUNCAO — IMPACTO NO NIVEL DO MAR: N(t) = C * (A0 - A(t))")
    print(f"    C = {C_MM:.0f} mm por M km2 perdido  |  N(0) = 0 (referencia {ano_base})")
    print(f"    {'Ano':>6}  {'A(t) (M km2)':>14}  {'Perda acum. (M km2)':>22}  {'N(t) (mm)':>12}")
    linha("·")
    for ano_alvo in [1979, 1990, 2000, 2010, 2020, 2025, 2050, 2075, 2100]:
        if ano_alvo < ano_base:
            continue
        t_alvo = float(ano_alvo - ano_base)
        at = A0 * math.exp(-k * t_alvo)
        nt = C_MM * (A0 - at)
        print(f"    {ano_alvo:>6}  {at:>14.3f}  {A0 - at:>22.3f}  {nt:>12.1f}")
    linha()

    if not tem_libs:
        print("  [AVISO] matplotlib/numpy nao encontrados — graficos indisponiveis.")
        print("          Instale com:  pip install matplotlib numpy")
        pausar()
        return

    # ── Graficos com matplotlib ───────────────────────────────────────────────
    import numpy as np
    import matplotlib.pyplot as plt

    t_mod    = np.linspace(0, 121, 500)
    anos_mod = ano_base + t_mod
    A_mod    = A0 * np.exp(-k * t_mod)
    dA_mod   = -k * A0 * np.exp(-k * t_mod)
    N_mod    = C_MM * (A0 - A_mod)

    fig, axs = plt.subplots(3, 1, figsize=(12, 11), sharex=True)
    fig.suptitle(
        f"IceTrack — Modelagem Matematica Exponencial\n"
        f"{nome_regiao(regiao)}  |  A(t) = {A0:.2f} * e^(-{k:.5f}*t)  |  {ano_base}–2100",
        fontsize=12, fontweight="bold",
    )

    # Subplot 1: A(t) — modelo vs dados reais
    ax1 = axs[0]
    ax1.plot(anos_mod, A_mod, "b-", linewidth=2,
             label=f"Modelo: A(t) = {A0:.2f}*e^(-{k:.5f}*t)")
    ax1.scatter(anos, a_vals, color="navy", s=18, alpha=0.7,
                label="Dados reais NSIDC", zorder=5)
    ax1.axhline(y=A0 / 2, color="red", linestyle="--", alpha=0.7,
                label=f"Meia-vida: {A0/2:.2f} M km²")
    if t_half is not None:
        ax1.axvline(x=ano_half, color="red", linestyle=":", alpha=0.6)
        ax1.annotate(f"~{ano_half:.0f}", xy=(ano_half, A0 / 2),
                     xytext=(ano_half + 3, A0 / 2 + 0.4), fontsize=9, color="red")
    ax1.set_ylabel("Extensao (M km²)")
    ax1.set_title("A(t) — Extensao Glacial Modelada vs Dados Reais")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Subplot 2: A'(t) — taxa instantanea
    ax2 = axs[1]
    ax2.plot(anos_mod, dA_mod, "g-", linewidth=2,
             label="A'(t) = -k * A0 * e^(-k*t)")
    ax2.axhline(y=0, color="black", linewidth=0.8)
    ax2.fill_between(anos_mod, dA_mod, 0, alpha=0.2, color="green")
    ax2.set_ylabel("Taxa (M km²/ano)")
    ax2.set_title("A'(t) — Taxa Instantanea de Degelo (Derivada)")
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    # Subplot 3: N(t) — impacto no nivel do mar
    ax3 = axs[2]
    ax3.plot(anos_mod, N_mod, "r-", linewidth=2,
             label=f"N(t) = {C_MM:.0f} * (A0 - A(t))")
    ax3.fill_between(anos_mod, N_mod, alpha=0.15, color="red")
    ax3.set_ylabel("Elevacao estimada (mm)")
    ax3.set_xlabel("Ano")
    ax3.set_title("N(t) — Impacto Estimado no Nivel do Mar")
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()

    nome_plot    = f"modelagem_dps_{regiao}_{ano_base}_{anos[-1]}.png"
    caminho_plot = os.path.join(BASE_DIR, nome_plot)
    plt.savefig(caminho_plot, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"\n  Grafico salvo: {nome_plot}")
    pausar()


# ── Menu principal ────────────────────────────────────────────────────────────

def exibir_menu():
    print()
    linha("═")
    print("  *** ICETRACK - Monitoramento de Geleiras via Dados Satelitais ***")
    linha("═")
    print("  [1]  Sobre o IceTrack")
    print("  [2]  Calcular variacao percentual entre dois anos")
    print("  [3]  Gerar relatorio de tendencia (.txt)")
    print("  [4]  Comparar Artico vs Antartico")
    print("  [5]  Modelagem matematica exponencial  [DPS]")
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
                calcular_variacao_percentual()
            case "3":
                gerar_relatorio_tendencia()
            case "4":
                comparar_regioes()
            case "5":
                modelagem_matematica()
            case "0":
                linha("═")
                print("  Encerrando o IceTrack. Ate logo!")
                linha("═")
                break
            case _:
                print("  [!] Opcao invalida. Escolha um numero entre 0 e 5.")


if __name__ == "__main__":
    main()
