# Informe del miniproyecto 1

Llene cada sección reemplazando los marcadores `{{...}}`, sin quitar las
secciones. Las cifras salen de lo que imprime `python miniproyecto.py` y las
figuras son las que ese guion deja en `figuras/`. Las fórmulas van en LaTeX
(`$...$` o `$$...$$`).

## 1. La serie

La serie mide las ventas mensuales de electricidad a clientes del sector
residencial de Estados Unidos, expresadas en miles de MWh. Cubre de enero
de 2016 a diciembre de 2025, con frecuencia mensual y 120 observaciones,
verificadas consecutivas y sin vacíos. La fuente (la API oficial de la EIA)
y las condiciones de uso están en la ficha
[datos/README.md](../datos/README.md).

La elegimos porque su patrón anual marcado —con picos y valles que se
repiten cada doce meses— permite evaluar si incorporar la estacionalidad
mejora el pronóstico frente a líneas base que la ignoran.

![La serie](../figuras/serie.png)

La serie se revisó en busca de huecos y de valores atípicos. No hay huecos:
el archivo verificado contiene los 120 meses consecutivos de enero de 2016
a diciembre de 2025, sin fechas duplicadas ni vacíos, y `preparar()` devuelve
la serie sin cambios.

Para los atípicos, cada observación se comparó con los otros 9 valores de su
mismo mes calendario (excluyendo la propia) con dos criterios: la valla de
Tukey, que marca lo que cae fuera de
$[Q_1-1.5\,\mathrm{IQR},\ Q_3+1.5\,\mathrm{IQR}]$ del mes, y el filtro de
Hampel, que marca desviaciones respecto de la mediana del mes mayores que
$3\times 1.4826\times \mathrm{MAD}$. Tukey señaló 8 observaciones (abr-2016,
nov-2016, ago-2017, sep-2017, feb-2021, feb-2022, sep-2023 y feb-2025);
Hampel señaló 4 (nov-2016, ago-2017, sep-2017 y ene-2025). Ambos criterios
coincidieron en noviembre de 2016, agosto de 2017 y septiembre de 2017, que
quedan como los candidatos más firmes; abr-2016 y sep-2023 son marginales,
a menos del 0.5 % de su valla.

Se conservaron las 120 observaciones originales. Las alertas identifican
observaciones inusuales, no necesariamente errores: ningún valor es
imposible —no hay ceros, negativos ni saltos de registro— y la revisión de
los señalados no encontró evidencia de errores de registro. Imputarlas o
recortarlas descartaría información útil para pronosticar. Esta es la
columna `decision` de la tabla.

## 2. Componentes

![STL](../figuras/stl.png)

{{Lectura de la descomposición STL: cómo es la tendencia, qué meses quedan
arriba y abajo en la estacional y con cuánto, y dónde está el residuo más
grande.}}

## 3. Líneas base y backtest

{{Cómo es el backtest: cuántos orígenes, horizonte y qué meses quedan en la
prueba. Por qué ningún dato posterior al origen entra al modelo.}}

{{RMSE, MAE y MAPE del ingenuo y del estacional ingenuo, y cuál gana.}}

## 4. Estacionariedad e identificación

{{Valor p de la prueba ADF para la serie, su diferencia regular, la
estacional y las dos juntas. El d y el D elegidos.}}

![ACF y PACF](../figuras/acf_pacf.png)

{{Qué rezagos salen de las bandas y qué órdenes sugieren.}}

## 5. Modelos clásicos

{{La rejilla de órdenes y su AIC. El modelo elegido, escrito con su
ecuación.}}

![Residuos](../figuras/residuos.png)

{{Diagnóstico de los residuos: Ljung-Box y lo que muestran la gráfica y su
ACF.}}

{{La variable exógena: qué es, por qué se conoce de antemano y si mejora al
SARIMA.}}

## 6. Tabla de métricas

{{Copie aquí `resultados/metricas.csv` como tabla de Markdown, ordenada por
RMSE.}}

| Modelo | Decisión | RMSE | MAE | MAPE (%) |
|---|---|---|---|---|
| {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

## 7. Conclusión

{{El mejor modelo clásico, cuánto mejora a la mejor línea base en cada
métrica y en qué meses o tramos sigue fallando. Es el modelo que el
miniproyecto 2 debe superar.}}
