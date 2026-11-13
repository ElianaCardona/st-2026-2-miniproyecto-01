# Informe del miniproyecto 1

## 1. La serie

La serie mide las ventas mensuales de electricidad a clientes del sector
residencial de Estados Unidos, expresadas en miles de MWh. Cubre de enero
de 2016 a diciembre de 2025, con frecuencia mensual y 120 observaciones,
verificadas consecutivas y sin vacíos. La fuente (la API oficial de la EIA)
y las condiciones de uso están en la ficha
[datos/README.md](../datos/README.md).

Elegí esta serie porque su patrón anual marcado —con picos y valles que se
repiten cada doce meses— permite evaluar si incorporar la estacionalidad
mejora el pronóstico frente a líneas base que la ignoran.

![La serie](../figuras/serie.png)

Revisé la serie en busca de huecos y de valores atípicos. No hay huecos:
el archivo verificado contiene los 120 meses consecutivos de enero de 2016
a diciembre de 2025, sin fechas duplicadas ni vacíos, y `preparar()` devuelve
la serie sin cambios.

Para los atípicos, comparé cada observación con los otros 9 valores de su
mismo mes calendario (excluyendo la propia) con dos criterios: la valla de
Tukey, que marca lo que cae fuera de
$[Q_1-1{,}5\,\mathrm{IQR},\ Q_3+1{,}5\,\mathrm{IQR}]$ del mes, y el filtro de
Hampel, que marca desviaciones respecto de la mediana del mes mayores que
$3\times 1{,}4826\times \mathrm{MAD}$. Tukey señaló 8 observaciones (abr-2016,
nov-2016, ago-2017, sep-2017, feb-2021, feb-2022, sep-2023 y feb-2025);
Hampel señaló 4 (nov-2016, ago-2017, sep-2017 y ene-2025). Ambos criterios
coincidieron en noviembre de 2016, agosto de 2017 y septiembre de 2017, que
quedan como los candidatos más firmes; abr-2016 y sep-2023 son marginales,
a menos del 0,5 % de su valla.

Conservé las 120 observaciones originales. Las alertas identifican
observaciones inusuales, no necesariamente errores: ningún valor es
imposible —no hay ceros, negativos ni saltos de registro— y al revisar los
señalados no encontré evidencia de errores de registro. Imputarlas o
recortarlas descartaría información útil para pronosticar. Esta es la
columna `decision` de la tabla.

## 2. Componentes

Apliqué una descomposición STL robusta con un periodo de 12 meses a la serie
preparada. La figura muestra los cuatro paneles del ajuste: la serie
observada, la tendencia, la componente estacional y el residuo.

![STL](../figuras/stl.png)

La tendencia sube de 117.873,73 miles de MWh en enero de 2016 a 127.217,74 en
diciembre de 2025, un aumento de 9.344,01 miles de MWh (el 7,9 %) a lo largo
de la década. No es una recta: se mantiene casi plana entre 2016 y 2019
(117.696,65 en junio de 2016 y 119.457,09 en enero de 2018), el ascenso se
concentra entre 2020 y 2022 (121.843,92 en enero de 2020 y 125.742,72 en
junio de 2022) y alrededor de 2023 desciende hasta un mínimo local de
124.446,86 en octubre de 2023; desde ahí vuelve a subir hasta los 127.217,74
de diciembre de 2025.

Los efectos estacionales se expresan respecto a la tendencia: indican, en
promedio, cuánto agrega o resta cada mes sobre el nivel de tendencia. Julio
es el mes con el efecto más alto (+35.449,38 miles de MWh) y agosto le sigue
de cerca (+33.927,15): los meses del verano quedan muy por encima de la
tendencia. En el lado opuesto, abril es el más bajo (-28.185,58) y noviembre
el segundo más bajo (-22.805,84), los meses de ventas más bajas del ciclo
anual. La distancia entre julio y abril, 63.634,96 miles de MWh, da la
escala del ciclo.

El residuo recoge lo que ni la tendencia ni la estacionalidad explican. Su
mayor valor en valor absoluto es positivo y ocurre en enero de 2018:
+17.009,84 miles de MWh, es decir, ese mes las ventas superaron en esa cantidad
a lo que tendencia y estacionalidad explicaban. Destaca sobre el resto: la
desviación típica del residuo es de 4.432,21 miles de MWh y el residuo más
negativo es -14.491,71, en junio de 2023. El tamaño del ciclo anual frente a
un residuo de esa escala anticipa la ventaja del estacional ingenuo sobre
el ingenuo que se cuantifica en la sección 3.

## 3. Líneas base y backtest

Medí todos los modelos con el mismo backtest de orígenes móviles (el de
comun.py, sin modificar). La ventana de prueba son los últimos 24 meses
de la serie, de enero de 2024 a diciembre de 2025, y se recorren 13 orígenes. En cada origen, 
el modelo usa los datos disponibles hasta ese mes, inclusive, y pronostica los 12 meses siguientes,
 de modo que los entrenamientos terminan entre diciembre de 2023 y diciembre de 2024.
La unión de las ventanas de prueba cubre los 24 meses de 2024-01 a
2025-12 y cada mes la pronostican entre 1 y 12 orígenes (enero de 2024
solo uno; en 2025, doce en enero y uno en diciembre). El RMSE, el MAE y
el MAPE finales son el promedio de los 13 orígenes.

Ningún dato posterior al origen entra al modelo: el entrenamiento de
cada origen termina en el origen, y los 12 meses siguientes solo se
usan para comparar el pronóstico con las ventas realmente observadas.
Así la medición imita el uso real de un pronóstico —el futuro no está
disponible cuando se emite— y evita que información del periodo de
prueba contamine el ajuste.

Las dos líneas base ignoran la estructura de la serie de distinta forma.
El ingenuo repite el último valor observado durante los 12 meses del
horizonte; el estacional ingenuo repite los 12 valores del último año
observado, es decir, el mismo mes del año anterior.

| Línea base | RMSE | MAE | MAPE (%) |
|---|---|---|---|
| ingenuo | 30.781,09 | 25.480,90 | 20,30 |
| estacional ingenuo | 6.850,49 | 5.686,72 | 4,49 |

El estacional ingenuo gana con holgura: el RMSE del ingenuo es 4,49
veces el suyo (30.781,09 frente a 6.850,49). Repetir el mismo mes del año
anterior captura el ciclo anual que domina la serie, mientras que
repetir el último valor conserva el nivel de un único mes —de verano o
de invierno— a lo largo de todo el horizonte. Esta es la referencia que
los modelos de las secciones siguientes deben superar.

## 4. Estacionariedad e identificación

Tomé las decisiones con los primeros 96 meses (enero de 2016 a diciembre de
2023) y dejé 2024 y 2025 reservados para el backtest. Apliqué la prueba ADF
a las cuatro versiones; todas con constante y sin tendencia determinista
(especificación `c` de `adfuller`, con el número de rezagos de la prueba ADF seleccionado por AIC):

| Versión | Estadístico | Valor p | Observaciones efectivas de la prueba |
|---|---|---|---|
| Nivel (original) | -1,609 | 0,4793 | 83 |
| Diferencia regular de un mes (d1) | -5,374 | 0,0000 | 83 |
| Diferencia estacional de 12 meses (D12) | -3,252 | 0,0171 | 71 |
| Ambas diferencias (d1 + D12) | -3,542 | 0,0070 | 71 |

El nivel no permite rechazar la raíz unitaria y las tres versiones
diferenciadas sí la rechazan al 5 %. Elegí d=1 y D=1 para los modelos
candidatos. La diferencia estacional sola también rechazó la hipótesis de
raíz unitaria (p = 0,0171) y sigue siendo una alternativa razonable, así
que no me guié por el menor valor p: comparé las dos candidatas sobre los
mismos 96 meses con promedios por tramo y con la ACF, y repetí la ADF con
constante y tendencia como verificación (D12 rechaza más fuerte, -5,542
con p = 0,0000; d1 + D12 queda en el borde, con p = 0,0567).

Los promedios por tramos de 27 a 29 meses separan a las candidatas. En D12
los tres tramos promedian +1.628,89, +828,19 y -1.065,40 miles de MWh: el
cambio anual no se queda junto a una constante, desciende de forma
sostenida a lo largo de la muestra, en línea con el ascenso lento y
episódico de la tendencia de la sección 2. En d1 + D12 los mismos tramos
promedian -122,61, -279,40 y +4,44, sin patrón. Este contraste sugiere,
sin probarlo, que D12 conserva un nivel lento que se desplaza. La ACF
apunta en la misma dirección: en D12 el rezago 1 es positivo y persistente
(+0,403) y la PACF sigue fuera de banda en el rezago 24 (-0,261); en
d1 + D12 el rezago 1 es -0,239 y el 24 no supera la banda (-0,054 en la
ACF, -0,120 en la PACF). Por eso elegí aplicar ambas diferencias antes que
la estacional sola.

![ACF y PACF](../figuras/acf_pacf.png)

La figura muestra la ACF y la PACF de la serie después de aplicar una diferencia regular y una estacional de 12 meses. La serie transformada tiene 83 observaciones y la PACF se estimó con el método de Yule–Walker. Con una banda de referencia aproximada de ±0,215, en la ACF quedaron fuera de la banda los rezagos 1 (-0,239) y 12 (-0,391). En la PACF quedaron fuera los rezagos 1 (-0,239), 2 (-0,230) y 12 (-0,311). En el rezago 24, tanto la ACF (-0,054) como la PACF (-0,120) quedaron dentro de las bandas mostradas.

Los picos negativos de la ACF en los rezagos 1 y 12 me llevaron a considerar un término de media móvil regular ($q=1$) y uno estacional ($Q=1$), respectivamente. Los rezagos destacados en la PACF también me llevaron a considerar términos autorregresivos. Para elegir el orden SARIMA, comparé por AIC los modelos candidatos (sección 5).

## 5. Modelos clásicos

Con d = 1 y D = 1 fijados en la sección 4, comparé por AIC los 16
candidatos de la rejilla (p, q, P, Q en {0, 1}), todos ajustados sobre
los mismos 96 meses de decisión (2016-01 a 2023-12). Los 16 convergieron
con AIC finito, en un rango de 1.715,36 a 1.736,24. El menor AIC
correspondió a SARIMA(0, 1, 0)(0, 1, 1, 12) con 1.715,36; el segundo
lugar, (0, 1, 0)(1, 1, 0, 12), quedó prácticamente empatado con 1.715,40.
Los cuatro candidatos sin términos estacionales (P = Q = 0) tuvieron los
cuatro AIC más altos (de 1.733,60 a 1.736,24): la ganancia está en el
término estacional, no en la parte autorregresiva.

El modelo elegido, con las dos diferencias ya aplicadas, tiene su
ecuación estimada sobre los 96 meses:

$$
(1 - B)(1 - B^{12})\, y_t = (1 - 0{,}2767\, B^{12})\, \varepsilon_t,
\qquad \hat{\sigma}_\varepsilon = 7.032{,}65 \text{ miles de MWh}.
$$

El único coeficiente dinámico estimado corresponde al término de media móvil estacional. `statsmodels` lo reporta como `ma.S.L12`, con un valor de −0,2767. El ajuste también estima la varianza de las innovaciones. Según la ecuación, el cambio anual de las ventas, $y_t-y_{t-12}$, es igual al cambio anual del mes anterior, más la innovación del mes actual, menos 0,2767 veces la innovación de hace doce meses.
parcialmente al año siguiente.

![Residuos](../figuras/residuos.png)

La figura muestra los residuos del modelo elegido (izquierda) y su ACF
(derecha). En la serie de residuos sobresalen dos valores enormes al
comienzo de la muestra, uno positivo en 2016 y otro negativo a
comienzos de 2017: la doble diferencia deja sin definir los primeros
meses y el ajustador los completa con una inicialización difusa, de
modo que esos dos puntos no son errores de pronóstico reales. Desde
mediados de 2017 los residuos oscilan alrededor de cero sin tendencia
visible y con dispersión parecida a lo largo de la muestra. En la ACF
solo el rezago 12 queda fuera de la banda de confianza (-0,36).

Apliqué la prueba de Ljung–Box para evaluar conjuntamente las autocorrelaciones 
de los residuos hasta los rezagos 12 y 24. Desconté un grado de libertad por el
coeficiente de media móvil estacional estimado, por lo que las pruebas usaron
11 y 23 grados de libertad, respectivamente. Hasta el rezago 12, rechacé la hipótesis 
de autocorrelaciones nulas al nivel del 5 % (estadístico de 23,24 y valor p de 0,0164).
  En la ACF también destaca el rezago 12, lo que sugiere que queda dependencia estacional 
  en los residuos. Hasta el rezago 24, la prueba arrojó un estadístico de 25,77 y 
  un valor p de 0,3120, por lo que no rechacé la hipótesis nula para ese conjunto de rezagos.

Para el SARIMAX agregué como exógena el número de días calendario de
cada mes. Se conoce por completo de antemano: el calendario está fijado
con años de anticipación y no depende de las ventas, así que usarla no
introduce información del futuro en el pronóstico. La construí para los
120 meses de la serie más los 12 meses siguientes, necesarios para
pronosticar todo el horizonte del backtest.

La exógena mejora al SARIMA, aunque poco: el RMSE baja de 8.395,83 a
8.300,63 (-95,20), el MAE de 7.120,84 a 6.904,44 (-216,40) y el MAPE de
5,72 % a 5,47 % (-0,25 puntos porcentuales). Aun así el SARIMAX queda
por encima del estacional ingenuo (RMSE 6.850,49): la longitud del mes
aporta algo de señal, pero no es el factor que explica la brecha con la
línea base.

## 6. Tabla de métricas

La tabla copia las cuatro filas de `resultados/metricas.csv`, ordenadas
por RMSE. La columna `decision` es la misma para los cuatro modelos
porque todos pronostican la misma serie conservada:

| Modelo | Decisión | RMSE | MAE | MAPE (%) |
|---|---|---|---|---|
| estacional ingenuo | Serie sin huecos. Se conservaron las 120 observaciones originales. La revisión por mes calendario señaló valores inusuales, sin evidencia de errores de registro. | 6.850,49 | 5.686,72 | 4,49 |
| SARIMAX(0, 1, 0)(0, 1, 1, 12) + exógenas | Serie sin huecos. Se conservaron las 120 observaciones originales. La revisión por mes calendario señaló valores inusuales, sin evidencia de errores de registro. | 8.300,63 | 6.904,44 | 5,47 |
| SARIMA(0, 1, 0)(0, 1, 1, 12) | Serie sin huecos. Se conservaron las 120 observaciones originales. La revisión por mes calendario señaló valores inusuales, sin evidencia de errores de registro. | 8.395,83 | 7.120,84 | 5,72 |
| ingenuo | Serie sin huecos. Se conservaron las 120 observaciones originales. La revisión por mes calendario señaló valores inusuales, sin evidencia de errores de registro. | 30.781,09 | 25.480,90 | 20,30 |

## 7. Conclusión

Entre los modelos ajustados, el mejor fue el SARIMAX(0, 1, 0)(0, 1, 1, 12)
con los días del mes como exógena: RMSE 8.300,63, MAE 6.904,44 y MAPE
5,47 %, por debajo del SARIMA sin exógenas (8.395,83, 7.120,84 y 5,72 %)
en las tres métricas. El menor error global lo obtuvo el estacional
ingenuo: RMSE 6.850,49, MAE 5.686,72 y MAPE 4,49 %. En este backtest
ningún modelo ajustado logró superar esa línea base.

Las diferencias del SARIMAX frente a cada referencia:

- Frente al estacional ingenuo —el SARIMAX comete más error—: RMSE
  +1.450,14 (+21,2 %), MAE +1.217,72 (+21,4 %) y MAPE +0,98 puntos
  porcentuales.
- Frente al ingenuo —el SARIMAX queda mejor—: RMSE un 73,0 % menor
  (8.300,63 frente a 30.781,09), MAE un 72,9 % menor y MAPE un 73,1 %
  menor.

Para señalar los meses difíciles definí el error con signo como el
pronóstico menos el valor observado. Como cada mes de la ventana de
prueba lo pronostican entre 1 y 12 orígenes, resumí cada mes a partir de
los orígenes que lo incluyen y ordené los meses por su error absoluto
medio, el promedio de los valores absolutos del error; para cada uno
reporto también el error medio con signo. Los meses con mayor error
absoluto medio fueron enero de 2024 (error medio con signo de -16.455,54,
con un solo origen), enero de 2025 (-13.535,10, con doce), junio de 2024
(-13.511,29, con seis) y febrero de 2025 (-12.066,75, con once); en los
cuatro el pronóstico quedó por debajo de las ventas reales y todos sus
orígenes erraron en esa misma dirección, de modo que el error absoluto
medio coincide con el valor absoluto del error medio con signo. Los
errores grandes se concentran en el arranque de cada año y en junio de
2024, y 2024 fue el año más difícil: MAE promedio de 7.255,13 frente a
6.553,75 en 2025. El sesgo promedio del SARIMAX en toda la ventana es
-2.754,27 miles de MWh: tiende a subestimar las ventas.

Con estas cifras, la referencia principal del miniproyecto 2 es el
estacional ingenuo (RMSE 6.850,49), porque obtuvo el menor error global
del backtest. Por separado, el mejor modelo entre los ajustados fue el
SARIMAX (RMSE 8.300,63): un modelo nuevo deberá quedar por debajo de ese
umbral para superar a los modelos clásicos, y por debajo de la marca del
estacional ingenuo para que el resultado tenga valor frente a lo simple.
