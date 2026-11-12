"""Miniproyecto 1: la serie del grupo, de las líneas base al mejor modelo clásico.

Se corre de principio a fin con

    python miniproyecto.py

y deja las figuras en figuras/ y la tabla en resultados/metricas.csv. Las
partes marcadas con TODO las completa el grupo; mientras falten, el guion las
reporta como pendientes y sigue. El informe, docs/informe.md, cita las cifras
y las figuras que produce este guion.
"""
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf  # noqa: E402
from statsmodels.tsa.seasonal import STL  # noqa: E402
from statsmodels.tsa.stattools import acf, adfuller, pacf  # noqa: E402

from comun import (RAIZ, backtest, cargar_serie, estacional_ingenuo,  # noqa: E402
                   fechas_siguientes, ingenuo)

warnings.filterwarnings("ignore")
FIGURAS = RAIZ / "figuras"
RESULTADOS = RAIZ / "resultados"
FIGURAS.mkdir(exist_ok=True)
RESULTADOS.mkdir(exist_ok=True)

# ============================================================
# 1. La serie
# ============================================================
# Cambie estos cuatro datos por los de la serie del grupo y documente la
# fuente en datos/README.md. La serie de ejemplo solo sirve para probar que
# el guion corre.
ARCHIVO = "datos/electricidad_residencial_eeuu.csv"
FECHA = "fecha"
VALOR = "ventas_miles_mwh"
PERIODO = 12

# Lo que se hizo con los huecos y con los datos atípicos, en una línea. Va
# a la columna `decision` de la tabla de métricas.
DECISION = ("Serie sin huecos. Se conservaron las 120 observaciones originales. "
            "La revisión por mes calendario señaló valores inusuales, sin "
            "evidencia de errores de registro.")


def preparar(serie):
    """Decisión del grupo: conservar la serie tal como llega, sin cambios.

    El CSV verificado trae los 120 meses consecutivos de 2016-01 a 2025-12
    sin vacíos, así que no hay huecos que rellenar. La revisión por mes
    calendario (valla de Tukey contra los otros 9 años del mismo mes, con
    el filtro de Hampel como contraste) señaló observaciones inusuales
    (8 con Tukey, 4 con Hampel; ambos coincidieron en nov-2016, ago-2017 y
    sep-2017). Las alertas identifican observaciones inusuales y la
    revisión no encontró evidencia de errores de registro, así que se
    conservan los 120 valores originales: se devuelve la serie sin
    modificaciones.
    """
    return serie


def graficar_serie(serie):
    figura, eje = plt.subplots(figsize=(9, 3.4))
    eje.plot(serie.index, serie.to_numpy())
    eje.set_title(f"{VALOR}: serie mensual")
    eje.set_ylabel(VALOR)
    figura.tight_layout()
    figura.savefig(FIGURAS / "serie.png", dpi=120)
    plt.close(figura)


# ============================================================
# 2. Descomposición
# ============================================================
MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre")


def descomponer(serie):
    """STL robusta con el periodo de la serie; guarda figuras/stl.png.

    Ajusta STL(serie, period=PERIODO, robust=True) a la serie preparada y
    dibuja los cuatro paneles: observado, tendencia, estacional y residuo.
    Imprime la tendencia en los extremos, el mes con el efecto estacional
    promedio más alto y el más bajo, y el residuo de mayor valor absoluto.
    """
    stl = STL(serie, period=PERIODO, robust=True).fit()
    paneles = [("Observado", stl.observed), ("Tendencia", stl.trend),
               ("Estacional", stl.seasonal), ("Residuo", stl.resid)]
    figura, ejes = plt.subplots(4, 1, figsize=(9, 8), sharex=True)
    for eje, (nombre, datos) in zip(ejes, paneles):
        eje.plot(datos.index, datos.to_numpy())
        eje.set_ylabel(nombre)
    ejes[0].set_title(f"{VALOR}: descomposición STL robusta (periodo {PERIODO})")
    figura.tight_layout()
    figura.savefig(FIGURAS / "stl.png", dpi=120)
    plt.close(figura)

    print(f"Tendencia: {serie.index[0]:%Y-%m}: {stl.trend.iloc[0]:.2f} -> "
          f"{serie.index[-1]:%Y-%m}: {stl.trend.iloc[-1]:.2f}")

    promedio = stl.seasonal.groupby(stl.seasonal.index.month).mean()
    alto, bajo = promedio.idxmax(), promedio.idxmin()
    print(f"Efecto estacional promedio: más alto en {MESES[alto - 1]} "
          f"({promedio[alto]:+.2f}), más bajo en {MESES[bajo - 1]} "
          f"({promedio[bajo]:+.2f}), en miles de MWh")

    fecha = stl.resid.abs().idxmax()
    print(f"Mayor residuo en valor absoluto: {fecha:%Y-%m}, "
          f"valor = {stl.resid[fecha]:+.2f} miles de MWh")


# ============================================================
# 3. Estacionariedad e identificación
# ============================================================

def estacionariedad(serie):
    """ADF en el nivel, la diferencia regular, la estacional y ambas; elige (d, D).

    Decide con los primeros 96 meses (2016-01 a 2023-12); 2024 y 2025
    quedan reservados para el backtest. Imprime el estadístico, el valor p
    y el número de observaciones de cada versión, elige d y D con la
    prueba y los picos de la ACF en 12 y 24, guarda la ACF y la PACF de la
    versión elegida en figuras/acf_pacf.png y devuelve (d, D).
    """
    entrenamiento = serie.iloc[:96]  # 2016-01 a 2023-12; 2024-2025 para el backtest

    versiones = [
        ("original", entrenamiento),
        ("d1 regular", entrenamiento.diff().dropna()),
        ("D12 estacional", entrenamiento.diff(PERIODO).dropna()),
        ("d1 + D12 ambas", entrenamiento.diff().diff(PERIODO).dropna()),
    ]

    print(f"Prueba ADF, {len(entrenamiento)} meses "
          f"({entrenamiento.index[0]:%Y-%m} a {entrenamiento.index[-1]:%Y-%m}):")
    print("  versión             estadístico    valor p   nobs")
    valor_p = {}
    for nombre, datos in versiones:
        estadistico, p, _, nobs, *_ = adfuller(datos)
        valor_p[nombre] = p
        print(f"  {nombre:16s}  {estadistico:12.3f}  {p:8.4f}  {nobs:5d}")

    d = 0 if valor_p["original"] < 0.05 else 1

    # ¿Sobrevive el ciclo anual a la diferencia regular? ACF de d1 en 12 y 24.
    d1 = versiones[1][1]
    banda_d1 = 1.96 / (len(d1) ** 0.5)
    acf_d1 = acf(d1, nlags=24)
    picos = abs(acf_d1[12]) > banda_d1 or abs(acf_d1[24]) > banda_d1
    if d:
        D = 1 if (valor_p["D12 estacional"] >= 0.05 or picos) else 0
    else:
        D = 1 if valor_p["D12 estacional"] >= 0.05 else 0

    elegida = entrenamiento
    if d:
        elegida = elegida.diff()
    if D:
        elegida = elegida.diff(PERIODO)
    elegida = elegida.dropna()

    print()
    print(f"Decisión: d = {d}, D = {D}; versión elegida: "
          f"{'d1 + D12' if d and D else 'd1' if d else 'D12' if D else 'nivel'}")
    if d:
        print(f"  El nivel no es estacionario (p = {valor_p['original']:.4f}): "
              "la diferencia regular es necesaria.")
    else:
        print(f"  El nivel ya es estacionario (p = {valor_p['original']:.4f}).")
    if valor_p["D12 estacional"] >= 0.05:
        print(f"  La diferencia estacional sola no alcanza estacionariedad "
              f"(p = {valor_p['D12 estacional']:.4f}): queda el ascenso lento "
              "del nivel, no basta con ella.")
    else:
        print(f"  La diferencia estacional sola sí es estacionaria "
              f"(p = {valor_p['D12 estacional']:.4f}).")
    if d and picos:
        print(f"  Tras la diferencia regular el ciclo anual persiste "
              f"(ACF en 12: {acf_d1[12]:+.3f}, en 24: {acf_d1[24]:+.3f}, "
              f"banda ±{banda_d1:.3f}): hace falta la diferencia estacional.")
    print(f"  Con ambas diferencias la ADF rechaza "
          f"(p = {valor_p['d1 + D12 ambas']:.4f}).")

    banda = 1.96 / (len(elegida) ** 0.5)
    acf_elegida = acf(elegida, nlags=24)
    pacf_elegida = pacf(elegida, nlags=24, method="ywm")
    print()
    print(f"ACF y PACF de la versión elegida (n = {len(elegida)}, "
          f"banda ±{banda:.3f}):")
    print("  rezago     ACF    PACF")
    for k in (1, 2, 3, 12, 13, 24):
        marca = "  <-" if (abs(acf_elegida[k]) > banda
                           or abs(pacf_elegida[k]) > banda) else ""
        print(f"  {k:6d}  {acf_elegida[k]:+.3f}  {pacf_elegida[k]:+.3f}{marca}")

    figura, ejes = plt.subplots(1, 2, figsize=(9.6, 3.6))
    plot_acf(elegida, lags=36, zero=False, ax=ejes[0], title="ACF")
    plot_pacf(elegida, lags=36, zero=False, ax=ejes[1], method="ywm",
              title="PACF")
    figura.suptitle(f"{VALOR}: d = {d}, D = {D} (2016-01 a 2023-12)")
    figura.tight_layout()
    figura.savefig(FIGURAS / "acf_pacf.png", dpi=120)
    plt.close(figura)

    return d, D


# ============================================================
# 4. Modelos clásicos
# ============================================================
# Cada modelo es una función modelo(entrenamiento, h) que devuelve h
# pronósticos y solo usa `entrenamiento`. Así entra al backtest común.

def elegir_sarima(serie, d, D):
    """TODO: rejilla pequeña de órdenes (p, q, P, Q) comparada por AIC.

    Ajuste con toda la serie preparada, imprima la tabla de AIC, revise los
    residuos del elegido con Ljung-Box y guarde figuras/residuos.png.
    Devuelva el orden y el orden estacional elegidos.
    """
    raise NotImplementedError("selección del SARIMA")


def modelo_sarima(orden, orden_estacional):
    """TODO: devuelva la función modelo(entrenamiento, h) del SARIMA elegido."""
    raise NotImplementedError("SARIMA en el backtest")


def exogenas(serie):
    """TODO: DataFrame de variables conocidas de antemano, con el índice de la serie.

    Por ejemplo, el número de festivos o de días hábiles de cada mes. Debe
    cubrir también los 12 meses que siguen al final de la serie.
    """
    raise NotImplementedError("variables exógenas")


def modelo_sarimax(orden, orden_estacional, x):
    """TODO: devuelva modelo(entrenamiento, h) de un SARIMAX con exógenas x.

    Use x.loc[entrenamiento.index] para ajustar y
    x.loc[fechas_siguientes(entrenamiento, h)] para pronosticar.
    """
    raise NotImplementedError("SARIMAX en el backtest")


# ============================================================
# 5. La tabla de métricas
# ============================================================

def fila(nombre, serie, modelo):
    _, promedio = backtest(serie, modelo)
    return {"modelo": nombre, "decision": DECISION,
            "RMSE": round(promedio["RMSE"], 2), "MAE": round(promedio["MAE"], 2),
            "MAPE": round(promedio["MAPE"], 2)}


def pendiente(parte, error):
    print(f"  pendiente: {parte} ({error})")


def main():
    cruda = cargar_serie(ARCHIVO, FECHA, VALOR)
    print(f"Serie: {len(cruda)} meses, de {cruda.index[0]:%Y-%m} a "
          f"{cruda.index[-1]:%Y-%m}, {cruda.isna().sum()} vacíos")
    serie = preparar(cruda)
    graficar_serie(serie)

    filas = [fila("ingenuo", serie, ingenuo),
             fila("estacional ingenuo", serie,
                  lambda t, h: estacional_ingenuo(t, h, PERIODO))]

    try:
        descomponer(serie)
    except NotImplementedError as error:
        pendiente("parte 2", error)

    try:
        d, D = estacionariedad(serie)
    except NotImplementedError as error:
        pendiente("parte 3", error)
        d = D = None

    if d is not None:
        try:
            orden, estacional = elegir_sarima(serie, d, D)
            filas.append(fila(f"SARIMA{orden}{estacional}", serie,
                              modelo_sarima(orden, estacional)))
            x = exogenas(serie)
            filas.append(fila(f"SARIMAX{orden}{estacional} + exógenas", serie,
                              modelo_sarimax(orden, estacional, x)))
        except NotImplementedError as error:
            pendiente("parte 4", error)

    tabla = pd.DataFrame(filas).sort_values("RMSE")
    tabla.to_csv(RESULTADOS / "metricas.csv", index=False)
    print(tabla.drop(columns="decision").to_string(index=False))
    print("Mejor modelo por RMSE:", tabla.iloc[0]["modelo"])


if __name__ == "__main__":
    main()
