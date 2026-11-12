# datos

La serie del grupo va en esta carpeta, en CSV. Llene esta ficha y borre la
serie de ejemplo cuando ya no la use.

| Campo | Valor |
|---|---|
| Archivo | [`electricidad_residencial_eeuu.csv`](electricidad_residencial_eeuu.csv) |
| Qué mide | Ventas mensuales de electricidad a clientes del sector residencial de Estados Unidos, expresadas en miles de MWh. |
| Fuente | U.S. Energy Information Administration (EIA), [API de datos abiertos](https://www.eia.gov/opendata/documentation.php). Consulta de ventas minoristas de electricidad con los filtros `stateid=US`, `sectorid=RES` y frecuencia mensual. |
| Licencia | Datos de dominio público. La EIA permite su reutilización y solicita atribución. [Política de reutilización de la EIA](https://www.eia.gov/about/copyrights_reuse.php). |
| Frecuencia | Mensual. |
| Periodo | Enero de 2016 a diciembre de 2025, con 120 observaciones consecutivas. |
| Columna de fecha | `fecha`. Primer día de cada mes, en formato `AAAA-MM-DD`. |
| Columna que se pronostica | `ventas_miles_mwh`. Total mensual de ventas residenciales, en miles de MWh. |


## Serie de ejemplo

`air_passengers.csv`: pasajeros mensuales de una aerolínea entre 1949 y 1960,
la serie clásica de Box y Jenkins, tomada de Kaggle
(`rakannimer/air-passengers`). Solo sirve para comprobar que el guion corre;
el miniproyecto se hace con la serie del grupo.
