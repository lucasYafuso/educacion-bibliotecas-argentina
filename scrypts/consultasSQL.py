#Importes de algunas librerias
import duckdb 
import pandas as pd
from pathlib import Path
#Importe del path donde esta guardado los archivos
from Princiapl import path



#Crea dataframes usando los archvivos con los datos ya limpios
df_bibliotecas=pd.read_csv(f"{path}TablasModelo/bibliotecas.csv")
df_establecimientos = pd.read_csv(f"{path}TablasModelo/establecimientos.csv")
df_establecimientos_sin_comunas=pd.read_csv(f"{path}TablasModelo/establecimientos_sin_comunas.csv")
df_poblacion = pd.read_csv(f"{path}TablasModelo/poblacion.csv")
df_poblacion_sin_comunas=pd.read_csv(f"{path}TablasModelo/poblacion_sin_comunas.csv")
df_provincias = pd.read_csv(f"{path}TablasModelo/provincias.csv")

#Registramos los dataframes como tablas temporale para poder hacer consultas con SQL 
duckdb.register("df_bibliotecas", df_bibliotecas)
duckdb.register("df_establecimientos", df_establecimientos)
duckdb.register("df_establecimientos_sin_comunas", df_establecimientos_sin_comunas)
duckdb.register("df_poblacion", df_poblacion)
duckdb.register("df_poblacion_sin_comunas", df_poblacion_sin_comunas)
duckdb.register("df_provincias", df_provincias)

#CONSULTA 1

#Para cada departamento informar la provincia, el nombre del departamento, la cantidad de EE de cada nivel educativo, considerando solamente la modalidad 
#común,y la cantidad de habitantes por edad según los niveles educativos. El orden del reporte debe ser alfabético por provincia y dentro de las provincias, 
#descendente por cantidad de escuelas primarias. 

dfConsulta1_SQL = duckdb.query("""SELECT 
  pr.provincia AS provincia,
  e.Departamento       AS departamento,

    SUM(
        CASE 
            WHEN e.Jardin_Mat = 1 THEN 1 
            WHEN e.Jardin_Inf = 1 THEN 1 
            ELSE 0 
        END
    ) AS jardines,
    (p.Cant_0a1 + p.Cant_2a5)  AS poblacion_jardin,
    SUM(CASE WHEN e.Primario  = 1 THEN 1 ELSE 0 END)     AS primarios,
    p.Cant_6a12              AS poblacion_primaria,
    SUM(CASE WHEN e.Secundario = 1 THEN 1 ELSE 0 END)     AS secundarios,                                                                
    p.Cant_13a18          AS poblacion_secundaria

FROM df_establecimientos e
JOIN df_poblacion p
  ON e.id_provincia = p.id_provincia AND e.Departamento = p.departamento
JOIN df_provincias pr
  ON e.id_provincia = pr.id_provincia

GROUP BY pr.provincia, e.Departamento, poblacion_jardin,poblacion_primaria,poblacion_secundaria

ORDER BY pr.provincia ASC, primarios DESC;
 """).df()

dfConsulta1_SQL


#CONSULTA 2

#Para cada departamento informar la provincia, el nombre del departamento y la cantidad de BP fundadas desde 1950. 
#El orden del reporte debe ser alfabético por provincia y dentro de las provincias, descendente por cantidad de BP de dicha capacidad. 

dfConsulta2_SQL = duckdb.query("""SELECT 
  pr.provincia AS provincia,
  b.departamento       AS departamento,
    SUM(CASE WHEN b.fecha_fundacion > 1950 THEN 1 ELSE 0 END) AS CANT_BP_FUNDADAS_DESDE_1950,


FROM df_bibliotecas b
JOIN df_provincias pr
  ON b.id_provincia = pr.id_provincia 


GROUP BY pr.provincia, departamento

ORDER BY pr.provincia ASC,  CANT_BP_FUNDADAS_DESDE_1950 DESC;
 """).df()

dfConsulta2_SQL

#CONSULTA 3

#Para cada departamento, indicar provincia, nombre del departamento, cantidad de BP, cantidad de EE (de modalidad común) y población total. 
#Ordenar por cantidad EE descendente, cantidad BP descendente, nombre de provincia ascendente y nombre de departamento ascendente. 
#No omitir casos sin BP o EE. 

#En esta consulta de SQL utilizamos los dataFrames de establecimientos y poblacion que tienen las comunas agrupadas como un solo departamento para que
#sea compatible con el dataFrame de bibliotecas.

dfConsulta3_SQL = duckdb.query("""SELECT 
  pr.provincia AS provincia,
  p.departamento       AS departamento,
  
    COUNT(DISTINCT b.Nro_Conabip) AS cant_BP,
    COUNT(DISTINCT e.Cueanexo)    AS cant_EE,
  
  p.total as Poblacion


FROM df_poblacion_sin_comunas p
JOIN df_provincias pr
  ON p.id_provincia = pr.id_provincia

LEFT JOIN df_bibliotecas b
  ON p.id_provincia = b.id_provincia AND p.departamento = b.departamento

LEFT JOIN df_establecimientos_sin_comunas e
  ON p.id_provincia = e.id_provincia AND p.departamento = e.Departamento

GROUP BY pr.provincia, p.departamento, p.total

ORDER BY cant_EE DESC,  cant_BP DESC, provincia ASC, departamento ASC;
 """).df()

dfConsulta3_SQL

#CONSULTA 4

#Para cada departamento, indicar provincia, el nombre del departamento y qué dominios de mail se usan más para las BP. 
dfConsulta4_SQL = duckdb.query("""
  WITH contar_dominios AS(
    SELECT 
      pr.provincia,
      b.departamento,
      b.dominio,
      COUNT(*) AS cantidad
    FROM df_bibliotecas b
    JOIN df_provincias pr
      ON b.id_provincia = pr.id_provincia
    WHERE b.dominio IS NOT NULL AND b.dominio != 'nan' AND b.dominio != ''
    GROUP BY pr.provincia, b.departamento, b.dominio
  ),
  dominio_mas_usado AS (
    SELECT 
      provincia,
      departamento,
      MAX(cantidad) AS max_cantidad,
    FROM contar_dominios
    GROUP BY provincia, departamento
  ),
  min_dominio AS (
    SELECT 
      d.provincia,
      d.departamento,
      MIN(d.dominio) AS dominio
    FROM contar_dominios d
    JOIN dominio_mas_usado m
      ON d.provincia = m.provincia
    AND d.departamento = m.departamento
    AND d.cantidad = m.max_cantidad
    GROUP BY d.provincia, d.departamento
  )
  SELECT 
  provincia AS Provincias,
  departamento AS Departamento,
  dominio AS Dominio
  FROM min_dominio
  ORDER BY provincia, departamento;
""").df()

dfConsulta4_SQL

#Estas lineas de codigo descargan los DataFrames que resultan de las consultas como CSV, se encuentran en la carpeta "consultasSQL"
destino = Path("ConsultasSQL")      #nombre carpeta
destino.mkdir(parents=True, exist_ok=True)   # crea la carpeta si no existe

#diccionario de dataframes
dfs = {
    "Consulta1":dfConsulta1_SQL,
    "Consulta2":dfConsulta2_SQL,
    "Consulta3":dfConsulta3_SQL,
    "Consulta4":dfConsulta4_SQL
}

#guarda cada df del diccionario como csv en la carpeta
for nombre, df in dfs.items():
    archivo = destino / f"{nombre}.csv" 
    df.to_csv(archivo, index=False, encoding="utf-8")
    print(f"Guardado {archivo}")







