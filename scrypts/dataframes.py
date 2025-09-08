#Importes de algunas librerias
import pandas as pd
import numpy as np
from pathlib import Path
#Importe del path donde esta guardado los archivos
from Princiapl import path


#En esta seccion armamos el dataFrame de Bibiliotecas Publicas a partir del archivo brindando por el enunciado

archivo_csv_bibliotecas=f"{path}Tablas Originales/bibliotecas-populares.csv" #Tomamos el archivo de bibliotecas populares
df_csv_biblio= pd.read_csv(archivo_csv_bibliotecas)  #leemos el csv y lo convertimos en un dataFrame


df_bibliotecas= df_csv_biblio[['nro_conabip','nombre','id_provincia','departamento','fecha_fundacion','mail']] #seleccionamos las columnas que nos sirven por el DER

#Hacemos modificaciones en el df para que concuerden los datos con el df de poblacion

#Modificacion en la columna "departamento"
lista_departamentos = df_bibliotecas['departamento'].astype(str)   #Armamos una lista de departamentos para poder modificarlas
lista_departamentos = lista_departamentos.str.replace('á', 'a') \
                                         .str.replace('é', 'e') \
                                         .str.replace('í', 'i') \
                                         .str.replace('ó', 'o') \
                                         .str.replace('ú', 'u') \
                                         
lista_mal=['Gral','Cnel','Cmdte', 'Dr','Sgto','Gob','Almte']                                       #Lista de abreviaciones a cambiar 
lista_bien=['General','Coronel','Comandante','Dr.','Sargento','Gobernador','Almirante']
for i in range(len(lista_mal)):
    lista_departamentos=[x.replace(lista_mal[i], lista_bien[i]) for x in lista_departamentos]        #Cambiamos las abreviaciones

df_bibliotecas['departamento'] = lista_departamentos    #Asignamos la lista modificada a la columna nuevamente


#Mas modificaciones especificas
df_bibliotecas['departamento'] = df_bibliotecas['departamento'].replace({'Villariño': 'Villarino', 'Juan F Ibarra':'Juan Felipe Ibarra','Pte Roque Saenz Peña':'Presidente Roque Saenz Peña','Pte De La Plaza':'Presidencia de la plaza', 'Coronel Felipe Varela':'General Felipe Varela',
                                                                         'Coronel De Marina L Rosales':'Coronel De Marina Leonardo Rosales','Adolfo Gonzalez Chaves':'Adolfo Gonzales Chaves','Leandro N Alem' : 'Leandro N. ALem', 'Lib General San Martin':'Libertador General San Martin',
                                                                        'Cap Sarmiento':'Capitan Sarmiento','Coronel Rosales':'Coronel De Marina Leonardo Rosales', 'Mayor J Luis Fontana':'Mayor Luis J. Fontana','General Angel Peñaloza':'ANGEL VICENTE PEÑALOZA'})

df_bibliotecas['departamento'] = df_bibliotecas['departamento'].astype(str).str.upper()  #Pasamos todos los valores de 'departamento' a mayuscula


#Modificaciones en la columna "fecha_de_fundacion"
#Queremos quedarnos unicamente con los años de fundacion
df_bibliotecas['fecha_fundacion']=df_bibliotecas['fecha_fundacion'].astype(str).str[:-6]    #Me quede con el elemento con los ultimos 6 digitos cortados
df_bibliotecas['fecha_fundacion'] = pd.to_numeric(df_bibliotecas['fecha_fundacion'].astype(str).str.strip(), errors='coerce').fillna(0).astype(int) #Cambiamos los 'Nan' a ceros para evitar problemas


#Modificaciones en la columna "mail"
#Queremos quedarnos unicamente con el dominio de los mails
df_bibliotecas['mail'] = df_bibliotecas['mail'].astype(str).str.strip()                   #Cambiamos todos los mail a tipo string
df_bibliotecas['dominio'] = df_bibliotecas['mail'].str.extract(r'@(.+)$')                 #Creamos una nueva columna "dominio" donde nos quedamos con los elementos que estan luego del arroba
df_bibliotecas['dominio'] = df_bibliotecas['dominio'].str.extract(r'^([^\.]+)')           #Nos quedamos con los elementos anteriores al punto
df_bibliotecas['dominio'] = df_bibliotecas['dominio'].astype(str).str.lower()             #Pasamos todos a minuscula


#df_bibliotecas  #Devolvemos el df

#En esta seccion armamos el dataFrame de Establecimientos Educativos a partir del archivo brindando por el enunciado

archivo_csv_establecimientos=f"{path}Tablas Originales/2022_padron_oficial_establecimientos_educativos.xlsx - padron2022.csv" #Tomamos el archivo de establecimientos educativos
df_csv_establ= pd.read_csv(archivo_csv_establecimientos,skiprows=5)         #Leemos el csv y lo convertimos en dataFrame
col_inicial_drop  = "Artística"                                             #Queremos eliminar todas las columnas posteriores a la modalidad "comun"
idx = df_csv_establ.columns.get_loc(col_inicial_drop)                       #Agarramos todas las columnas desde la elegido 
df_csv_establ.drop(columns=df_csv_establ.columns[idx:], inplace=True)       #Eliminamos todas las columnas seleccionadas anteriormente
df=df_csv_establ.iloc[0:]                                                   #Creamos un df con lo que quedo
df.columns= df.iloc[0]                                                      #Asignamos la primera fila como los headers
df= df[df['Común']=='1']                                                    #Eliminamos todos los elementos que no sean de modalidad "comun"


#Creamos el df de establecimientos con las columnas que queremos conservar por el DER
df_establecimientos=df[['Cueanexo','Código de localidad','Departamento','Nivel inicial - Jardín maternal', 'Nivel inicial - Jardín de infantes',
                        'Primario', 'Secundario']]


#Modificaciones en el df para que concuerden con otros df

#Modificaciones en la columna "Codigo de Localidad"
#Queremos modificar la columna "Cueanexo" para conservar solo los primeros dos digitos y conseguir el id de cada provincia
n = 7               #Número de dígitos que queremos sacar
df_establecimientos['Código de localidad'] = df_establecimientos['Cueanexo'].astype(str).str[:-n] #Sacamos la cantidad de digitos de atras para adelanete
df_establecimientos=df_establecimientos.rename(columns={'Código de localidad':'id_provincia'})     #Reenombramos la columna por id_provincia
df_establecimientos=df_establecimientos.rename(columns={'Nivel inicial - Jardín maternal':'Jardin_Mat'})     #Simplificamos los nombres de los jardines
df_establecimientos=df_establecimientos.rename(columns={'Nivel inicial - Jardín de infantes':'Jardin_Inf'})
 #Cambiamos el nombre de la columna
df_establecimientos['id_provincia'] = df_establecimientos['id_provincia'].replace({'06': '6', '02': '2'}).astype(int) #Reemplazamos los codigos que inician con cero para que coincida con el df de provincias


#Modificaciones en la columna "Departamento"
df_establecimientos['Departamento'] = df_establecimientos['Departamento'].astype(str).str.upper()     #Pasamos la columna a mayuscula 

#hacemos modificaciones mas especificas
df_establecimientos['Departamento']=df_establecimientos['Departamento'].replace({'CORONEL FELIPE VARELA':'GENERAL FELIPE VARELA', 'GENERAL JUAN F QUIROGA':'GENERAL JUAN FACUNDO QUIROGA','GENERAL JUAN MARTIN DE PUEYRREDON':'JUAN MARTIN DE PUEYRREDON','GENERAL GUEMES':'GENERAL GÜEMES','1§ DE MAYO':'1º DE MAYO',
                                                                                 'GENERAL OCAMPO':'GENERAL ORTIZ DE OCAMPO','MAYOR LUIS J FONTANA':'MAYOR LUIS J. FONTANA','GENERAL ANGEL V PEÑALOZA':'ANGEL VICENTE PEÑALOZA','DOCTOR MANUEL BELGRANO':'DR. MANUEL BELGRANO','CORONEL DE MARINA L ROSALES':'CORONEL DE MARINA LEONARDO ROSALES',
                                                                                'JUAN B ALBERDI':'JUAN BAUTISTA ALBERDI','GUER AIKE':'GÜER AIKE','MALARGUE':'MALARGÜE','JUAN F IBARRA':'JUAN FELIPE IBARRA','LIBERTADOR GRL SAN MARTIN':'LIBERTADOR GENERAL SAN MARTIN'})


#Modificaciones en las columnas de niveles educativos
#Cambiamos los 'Nan' de los niveles educativos por ceros para las consultas de SQL
cols_niveles = ['Jardin_Mat', 'Jardin_Inf', 'Primario', 'Secundario']
for col in cols_niveles:
    df_establecimientos[col] = pd.to_numeric(df_establecimientos[col].astype(str).str.strip(), errors='coerce').fillna(0).astype(int)


#df_establecimientos  #Devolvemos el df

#DataFrame de establecimientos educativos compatible con dataFrame de bibliotecas publicas
#Como el df de bibliotecas no estaba dividido por comunas, decidimos unificar todos los establecimientos publicos de CABA

#Copiamos el df de establecimientos educativos, y modificamos el departamento de aquellas filas que tienen id_provincia=2
df_establecimientos_sin_comunas=df_establecimientos.copy()
df_establecimientos_sin_comunas.loc[df_establecimientos_sin_comunas['id_provincia'] == 2, 'Departamento'] = 'CIUDAD AUTONOMA DE BUENOS AIRES'    

#df_establecimientos_sin_comunas

#Vamos a crear un nuevo csv a partir de la modificacion del archivo del poblacion dado por el enunciado, ya que este es muy dificil de manipular. 
archivo_csv_poblacion=f"{path}Tablas Originales/padron_poblacion.xlsX - Output.csv" 

df_csv_poblac = pd.read_csv(archivo_csv_poblacion, header=None,nrows=56597)  #Leemos el archivo y lo convertimos a un df sin el encabezado

#Detectamos filas con "AREA #" y extraermos el índice, el cod_area y el departamento
area_info = [
    (idx, str(row[1]).strip(), str(row[2]).strip() if pd.notna(row[2]) else "desconocido")
    for idx, row in df_csv_poblac.iterrows()
    if isinstance(row[1], str) and "AREA #" in row[1]
]

horizontalizados = []  #Lista donde se van a acumular resultados

#Procesamos cada Area del csv por separado
for i in range(len(area_info)):
    idx, cod_area, departamento = area_info[i]
    start = idx + 3
    end = area_info[i + 1][0] if i + 1 < len(area_info) else df_csv_poblac.shape[0]

    # Leer bloque de datos
    df = df_csv_poblac.iloc[start:end].copy()      #Generamos una copia del df original
    df.columns = ['col0', 'Edad', 'Casos', '%', 'Acumulado %']  #Le establecemos las columnas que tiene el df original
    df = df[['Edad', 'Casos']]   #Establecemos solo las columnas que queremos conservar por el DER
    df = df[df['Edad'].astype(str).str.isnumeric()]   #Se queda solo donde los valores de edad son un numero
    df['Edad'] = df['Edad'].astype(int)               #Los convierte a enteros
    df['Casos'] = df['Casos'].astype(str).str.replace(' ', '').str.replace('.', '').astype(int) #Convierte la columna a string, elimina espacios y puntos, y los convierte en enteros


    #Armamos las categorias correspondientes a los niveles educativos 
    resumen = {
        'cod_area': cod_area,

        'departamento': departamento,

        'cant_0a1': df[df['Edad'].between(0, 1)]['Casos'].sum(),

        'cant_2a5': df[df['Edad'].between(2, 5)]['Casos'].sum(),

        'cant_6a12': df[df['Edad'].between(6, 12)]['Casos'].sum(),

        'cant_13a18': df[df['Edad'].between(13, 18)]['Casos'].sum(),

        'cant_mas18': df[df['Edad'] > 18]['Casos'].sum(),

        'total': df['Casos'].sum()
    }

    horizontalizados.append(resumen)  #Apendeamos la lista al acumulado de resultados


df_tabla_poblacion = pd.DataFrame(horizontalizados)   #Creamos el DataFrame final a partir de la lista



#En esta seccion creamos el dataFrame de Poblacion a partir del archivo modificado en la seccion anterior
df_poblacion=df_tabla_poblacion.copy()                                      #lo convertimos en un nuevo dataFrame

#Modificaciones en la columna "cod_area"
#Necesitamos modificar el codigo de area para que sea igual al codigo de provincia
df_poblacion['cod_area'] = df_poblacion['cod_area'].astype(str).str[7:]          #Seleccionamos los primeros 7 digitos               
df_poblacion['cod_area'] = df_poblacion['cod_area'].astype(str).str[:-3]         #Seleccionamos los ultimos 3
df_poblacion['cod_area'] = df_poblacion['cod_area'].replace({'06': int('6'), '02': int('2')}).astype(int) #Modificamos los que tienen cero para que sean como los del df de provincia 
df_poblacion=df_poblacion.rename(columns={'cod_area':'id_provincia'})                    #Renombramos la columna para que sea acorde a lo que queremos


#Modificaciones en la columna "Departamento"
lista_departamentos = df_poblacion['departamento'].astype(str)            #Arma una lista de departamentos para poder modificarles las letras con tildes
lista_departamentos = lista_departamentos.str.replace('á', 'a') \
                                         .str.replace('é', 'e') \
                                         .str.replace('í', 'i') \
                                         .str.replace('ó', 'o') \
                                         .str.replace('ú', 'u') \
                                         .str.replace('Á', 'A') 

df_poblacion['departamento'] = lista_departamentos                              #Volvemos a asignar la lista a la columna 
df_poblacion['departamento'] = df_poblacion['departamento'].astype(str).str.upper()    #Pasamos todos los elementos de la columna a mayuscula


#df_poblacion

#DataFrame de establecimientos educativos compatible con dataFrame de bibliotecas publicas
#Como el df de bibliotecas no estaba dividido por comunas, decidimos unificarlas como CABA

#Copiamos el df de poblacion, y modificamos el departamento de aquellas filas que tienen id_provincia=2
df_poblacion_sin_comunas=df_poblacion.copy()
df_caba = (df_poblacion_sin_comunas[df_poblacion_sin_comunas['id_provincia'] == 2].groupby(['id_provincia'], as_index=False).sum(numeric_only=True))  # suma columnas numéricas
df_filtrado = df_poblacion_sin_comunas[df_poblacion_sin_comunas['id_provincia'] != 2] 
df_poblacion_sin_comunas = pd.concat([df_filtrado, df_caba], ignore_index=True)
df_poblacion_sin_comunas.loc[df_poblacion_sin_comunas['id_provincia'] == 2, 'departamento'] = 'CIUDAD AUTONOMA DE BUENOS AIRES'

#df_poblacion_sin_comunas

##En esta seccion armamos el dataFrame de Codigos Provinciales a partir del archivo de Bibliotecas Populares

df_codigo_provincias=df_csv_biblio[['id_provincia','provincia']]  #Creamos el df de provincia a partid del df original de bibliotecas
df_codigo_provincias=df_codigo_provincias.drop_duplicates(subset='id_provincia', keep='first') #Eliminamos los repetidos quedandonos con la primera apricion de cada provincia
#df_codigo_provincias   #Devolvemos el df de provincias



#Estas lineas de codigo descargan los DataFrames como CSV, se encuentran en la carpeta "dataframes_to_csv"
destino = Path("TablasModelo")      #nombre carpeta
destino.mkdir(parents=True, exist_ok=True)   # crea la carpeta si no existe

#diccionario de dataframes
dfs = {
    "establecimientos": df_establecimientos,
    "bibliotecas": df_bibliotecas,
    "poblacion": df_poblacion,
    "provincias":df_codigo_provincias,
    "poblacion_por_rango":df_tabla_poblacion,
    "poblacion_sin_comunas":df_poblacion_sin_comunas,
    "establecimientos_sin_comunas":df_establecimientos_sin_comunas
}

#guarda cada df del diccionario como csv en la carpeta
for nombre, df in dfs.items():
    archivo = destino / f"{nombre}.csv" 
    df.to_csv(archivo, index=False, encoding="utf-8")
    print(f"Guardado {archivo}")

