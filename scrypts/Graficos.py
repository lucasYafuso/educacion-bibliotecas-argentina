#Importes de algunas librerias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from   matplotlib import ticker
import seaborn as sns
import duckdb 
from matplotlib import rcParams
from pathlib import Path
#Importe del path donde esta guardado los archivos
from Princiapl import path

figs={}    #Creamo un diccionario en blanco para almacenar los graficos y luego guardarlos en una carpeta

# Carpeta en la que se van a guardar los graficos
FIG_DIR = Path("Graficos")          
FIG_DIR.mkdir(parents=True, exist_ok=True)

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

#Cantidad de BP por provincia. Mostrarlos ordenados de manera decreciente por dicha cantidad. 

#Consulta de SQL para el Grafico1
dfGrafico1_SQL = duckdb.query("""SELECT 
  pr.provincia AS provincia,                    
  COUNT(DISTINCT b.Nro_Conabip) AS cant_BP

  FROM df_bibliotecas b
  JOIN df_provincias pr
    ON b.id_provincia = pr.id_provincia 

GROUP BY pr.provincia
ORDER BY cant_BP DESC;
 """).df()


#GRAFICO DE BARRAS
fig1, ax = plt.subplots()               #Crea el grafico

ax.bar(data=dfGrafico1_SQL, x='provincia', height='cant_BP')    #Establece los ejes X e Y
       
ax.set_title('Cantidad Bbliotecas Publicas por Provincia')             #Titulo
ax.set_xlabel('Provincias', fontsize='medium')                         #Etiqueta eje X
ax.set_ylabel('cantidad de BP', fontsize='medium')                     #Etiqueta eje Y

ax.set_xticks(range(len(dfGrafico1_SQL)))                       #Rango del eje X
ax.set_xticklabels(dfGrafico1_SQL['provincia'], rotation=90, fontsize=8)        #Rota los labels del eje X 90°     
ax.bar_label(ax.containers[0], fontsize=8)                                             #Pone la etiqueta de cantidad sobre las barras

plt.tight_layout()
figs['grafico1']=fig1                     #Guardamos el grafico en el diccionario

#Graficar la cantidad de EE de los departamentos en función de la población, separando por nivel educativo y su correspondiente grupo etario (identificándolos por colores).

#Consulta de SQL para el Grafico2(primera consulta de SQL del enunciado)
dfGrafico2_SQL = duckdb.query("""
WITH poblacion_por_provincia AS (
    SELECT 
        id_provincia,
        SUM(Cant_0a1 + Cant_2a5) AS poblacion_jardin,
        SUM(Cant_6a12) AS poblacion_primaria,
        SUM(Cant_13a18) AS poblacion_secundaria
    FROM df_poblacion
    GROUP BY id_provincia
)

SELECT 
  pr.provincia AS provincia,

  SUM(
      CASE 
          WHEN e.Jardin_Mat = 1 THEN 1 
          WHEN e.Jardin_Inf = 1 THEN 1 
          ELSE 0 
      END
  ) AS jardines,

  pop.poblacion_jardin,
  SUM(CASE WHEN e.Primario  = 1 THEN 1 ELSE 0 END)     AS primarios,
  pop.poblacion_primaria,
  SUM(CASE WHEN e.Secundario = 1 THEN 1 ELSE 0 END)     AS secundarios,
  pop.poblacion_secundaria

FROM df_establecimientos e
JOIN poblacion_por_provincia pop
  ON e.id_provincia = pop.id_provincia
JOIN df_provincias pr
  ON e.id_provincia = pr.id_provincia

GROUP BY pr.provincia, pop.poblacion_jardin, pop.poblacion_primaria, pop.poblacion_secundaria
ORDER BY pr.provincia ASC;
""").df()




#Vamos a hacer el grafico que representa la cantidad de estudiantes en cada EE dividido en niveles(jardin - primario - secundario) por provincia.

#Hacemos que el dataframe que vamos a usar para grafiar tenga tres columnas extra donde este la cantidad de estudiantes en cada EE dividido en niveles 
dfGrafico2_SQL['proporcion_jardin'] = dfGrafico2_SQL['poblacion_jardin'] / dfGrafico2_SQL['jardines']
dfGrafico2_SQL['proporcion_primaria'] = dfGrafico2_SQL['poblacion_primaria'] / dfGrafico2_SQL['primarios']
dfGrafico2_SQL['proporcion_secundaria'] = dfGrafico2_SQL['poblacion_secundaria'] / dfGrafico2_SQL['secundarios']



provincias = dfGrafico2_SQL['provincia']   # nueva lista de etiquetas
x = np.arange(len(provincias))  # eje X
width = 0.25

fig2, ax = plt.subplots(figsize=(20,8))   # lienzo más razonable para provincias

#Dibujamos las tres barras de cada provincia(jardin - primario - secundario)
ax.bar(x - width, dfGrafico2_SQL['proporcion_jardin'], width, label='Jardin', color='skyblue')
ax.bar(x,          dfGrafico2_SQL['proporcion_primaria'], width, label='Primaria', color='orange')
ax.bar(x + width, dfGrafico2_SQL['proporcion_secundaria'], width, label='Secundaria', color='green')

#Asignamos las etiquetas
ax.set_xticks(range(len(dfGrafico2_SQL)))
ax.set_xticklabels(provincias, rotation=90, fontsize=10)

ax.set_ylabel('Cantidad de estudiantes por EE')                     #Etiqueta del eje y
ax.set_title('Proporción de EE por nivel educativo y provincia')    #Titulo del grafico
ax.legend()                                                         #Mustra a que hace referencia cada barra
ax.grid(axis='y', linestyle='--', alpha=0.5)                        

fig2.tight_layout()
fig2.canvas.draw()                                  #fuerza renderizado
fig2.savefig("graficos/grafico2.jpg", dpi=300)      #Guarda la imagen de otra forma que las demas para que sea legible
plt.close(fig2)                                     #Cierra el grafico


#Realizar un boxplot por cada provincia, de la cantidad de EE por cada departamento de la provincia. 
#Mostrar todos los boxplots en una misma figura, ordenados por la mediana de cada provincia. 

#Consulta del SQL para el grafico3
dfGrafico3_SQL = duckdb.query("""SELECT 
  pr.provincia AS provincia,
  e.Departamento       AS departamento,
  
    COUNT(*)    AS cant_EE

                              
FROM df_establecimientos e
JOIN df_provincias pr
  ON e.id_provincia = pr.id_provincia

GROUP BY pr.provincia, e.Departamento

ORDER BY provincia ASC, cant_EE ASC;
 """).df()


#GRAFICO BOXPLOT
fig3=ax.boxplot(dfGrafico3_SQL['cant_EE'])          #Genera el grafico


fig, ax = plt.subplots()                                              #Creamos figura y un sistema de ejes
positions = np.arange(len(dfGrafico3_SQL['provincia'])) * 1.5         #Tomamos una lista con la provincias y los separamos con un interlineado de 1,5 para que no se superpongan los boxplots
 

#Establecemos eje X e Y
dfGrafico3_SQL.boxplot(by='provincia', column=['cant_EE'], 
             ax=ax, grid=False, showmeans=True, rot=90,)



fig.suptitle('')
ax.set_title('Cantidad Establecimientos Educativos por provincia')               #Titulo
ax.set_xlabel('Provincias')                                                      #Etiqueta eje X
ax.set_ylabel('Cantidad de Establecimientos Educativos')                         #Etiqueta eje Y

figs['grafico3'] = fig   #Guardamos el grafico en el diccionario


#Relación entre la cantidad de BP cada mil habitantes y de EE cada mil habitantes por departamento. 
#Consulta SQL grafico4
dfGrafico4_SQL = duckdb.query("""SELECT 
  pr.provincia AS provincia,
  p.departamento       AS departamento,
  
    COUNT(DISTINCT b.Nro_Conabip) AS cant_BP,
    COUNT(DISTINCT e.Cueanexo)    AS cant_EE,
  
  p.total as Poblacion


FROM df_poblacion p
JOIN df_provincias pr
  ON p.id_provincia = pr.id_provincia

LEFT JOIN df_bibliotecas b
  ON p.id_provincia = b.id_provincia AND p.departamento = b.departamento

LEFT JOIN df_establecimientos e
  ON p.id_provincia = e.id_provincia AND p.departamento = e.Departamento

GROUP BY pr.provincia, p.departamento, p.total

ORDER BY provincia ASC, departamento ASC, cant_EE DESC,  cant_BP DESC  ;
 """).df()


#Vamos a hacer la proporcion de cantidad de EE/BP por cada mil habitantes agrgandole una columna extra al datafre con esa informacion
dfGrafico4_SQL['ee_cada_1000_hab'] = dfGrafico4_SQL['cant_EE']*1000/ dfGrafico4_SQL['Poblacion']
dfGrafico4_SQL['bp_cada_1000_hab'] = dfGrafico4_SQL['cant_BP']*1000/ dfGrafico4_SQL['Poblacion']


#Usamos una datafre nuevo en el cual estas columnas creadas anteriormente no son ceros
df_plot = dfGrafico4_SQL[(dfGrafico4_SQL["bp_cada_1000_hab"] > 0) &
                         (dfGrafico4_SQL["ee_cada_1000_hab"]  > 0)].copy()

#Generamos un scatter plot
fig4=plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df_plot,
    x="ee_cada_1000_hab",
    y="bp_cada_1000_hab",
    hue="provincia",
    palette="tab20",
    edgecolor="black",
    linewidth=0.3,
    alpha=0.8
)


# Escalas logarítmicas
plt.xscale("log")
plt.yscale("log")

plt.xlabel("Escuelas cada 1000 habitantes (log)")                                           #Etiqueta del eje x
plt.ylabel("Bibliotecas cada 1000 habitantes (log)")                                        #Etiqueta del eje y
plt.title("EE vs BP por departamento (escala log–log)")                                     #Titulo del grafico
plt.legend(title="Provincia", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)       #Muestra a que provincia hace referencia cada punto   
plt.tight_layout()

figs['grafico4']=fig4       #Guardamos el grafico en el diccionario
 
#Creamos una funcion para que guarde los grafico del diccionario en la carpeta creada en el inicio del codigo
for nombre, fig in figs.items():
    ruta = FIG_DIR / f"{nombre}.jpg"      
    fig.savefig(ruta, dpi=800, bbox_inches="tight")
    fig.tight_layout()
    fig.canvas.draw()                     # asegura renderizado
    plt.close(fig)                        # libera memoria


#Estas lineas de codigo descargan los DataFrames que resultan de las consultas hechas para cada grafico como CSV, se encuentran en la carpeta "consultasSQL"
destino = Path("ConsultasSQL")      #nombre carpeta
destino.mkdir(parents=True, exist_ok=True)   # crea la carpeta si no existe

#diccionario de dataframes
dfs = {
    "ConsultaGrafico1":dfGrafico1_SQL,
    "ConsultaGrafico2":dfGrafico2_SQL,
    "ConsultaGrafico3":dfGrafico3_SQL,
    "ConsultaGrafico4":dfGrafico4_SQL
}

#guarda cada df del diccionario como csv en la carpeta
for nombre, df in dfs.items():
    archivo = destino / f"{nombre}.csv" 
    df.to_csv(archivo, index=False, encoding="utf-8")
