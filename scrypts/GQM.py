#Importes de algunas librerias
import pandas as pd
import numpy as np
import re
from Princiapl import path

#leemos las tablas originales

#Bibliotecas publicas
df_BP = pd.read_csv(f"{path}TP1/Tablas Originales/bibliotecas-populares.csv")
#Establecimientos educativos
df_EE = pd.read_csv(f"{path}TP1/Tablas Originales/2022_padron_oficial_establecimientos_educativos.xlsx - padron2022.csv",skiprows=6)

#calcula el porcentaje de valores nulos de una columna
def porcentaje_nulos_columnas_incompletas(df):
    total_filas = len(df)
    
    #Calculamos los valores nulos por columna
    faltantes = df.isnull().sum()
    
    #Filtramos solo las columnas con al menos un nulo
    columnas_incompletas = faltantes[faltantes > 0]
    
    #Calculamos el porcentaje de nulos
    porcentaje = (columnas_incompletas / total_filas * 100).round(2)
    
    return porcentaje

#calcula el porcentaje de valores repetidos en una columna
def porcentaje_duplicados(df: pd.DataFrame, columna: str) -> float:
   
    total = df.shape[0]
    if total == 0 or columna not in df.columns:
        return 0.0
    
    #Contamos cuántas veces aparece cada valor
    conteos = df[columna].value_counts(dropna=False)
    #Filtramos los valores que aparecen más de una vez
    duplicados = conteos[conteos > 1].sum()
    porcentaje = duplicados / total * 100
    return round(porcentaje, 2)

#recibe el data frame y un dict con el tipo de dato esperado para cada columna y devuelve el porcentaje de inconsistencia para cada atributo
def porcentaje_tipo_incorrecto(df, tipos_esperados):

    resultados = {}
    for col, tipo in tipos_esperados.items():
        if col not in df.columns:
            resultados[col] = None
            continue
        serie = df[col]
        total = serie.notna().sum()
        if total == 0:
            resultados[col] = None
            continue

        def es_valor_correcto(v):
            if pd.isna(v):
                return True
            try:
                if tipo == 'int':
                    # permite ints o strings de dígitos
                    return isinstance(v, (int, np.integer)) or (isinstance(v, str) and v.isdigit())
                elif tipo == 'float':
                    return isinstance(v, (float, np.floating)) or (isinstance(v, str) and bool(re.fullmatch(r'\d+(\.\d+)?', v)))
                elif tipo == 'numeric':
                    # int o float
                    float(v)
                    return True
                elif tipo == 'str':
                    return isinstance(v, str)
                else:
                    return True
            except:
                return False

        incorrectos = serie.apply(lambda x: not es_valor_correcto(x))
        resultados[col] = round(incorrectos.sum() / total * 100, 2)

    return resultados

#devuelve el porcentaje por columna de la cantidad de valores que no cumplen con estar contenidos en cierta categoría
#y tambien devuelve las filas invalidas
def analisis_consistencia_categorica(df: pd.DataFrame):
    validos = {
        'Sector': ['Privado', 'Estatal', 'Social/cooperativa'],
        'Jurisdicción': [
            'Buenos Aires','Catamarca','Chaco','Chubut','Córdoba','Corrientes',
            'Entre Ríos','Formosa','Jujuy','La Pampa','La Rioja','Mendoza',
            'Misiones','Neuquén','Río Negro','Salta','San Juan','San Luis',
            'Santa Cruz','Santa Fe','Santiago del Estero','Tierra del Fuego',
            'Tucumán','Ciudad de Buenos Aires'
        ],
        'Ámbito': ['Urbano', 'Rural']
    }

    porcentajes = {}
    filas_invalidas = {}

    for col, lista_valida in validos.items():
        if col not in df.columns:
            porcentajes[col] = None
            filas_invalidas[col] = pd.DataFrame()
            continue

        serie = df[col]
        total = serie.notna().sum()
        if total == 0:
            porcentajes[col] = None
            filas_invalidas[col] = pd.DataFrame()
            continue

        mask_invalid = ~serie.isin(lista_valida)
        pct = mask_invalid.sum() / total * 100
        porcentajes[col] = round(pct, 2)
        filas_invalidas[col] = df.loc[mask_invalid, [col]]

    return porcentajes, filas_invalidas


#Calcula el porcentaje de filas donde el código y el nombre no coinciden
#según la relación más frecuente en el DataFrame.
def porcentaje_inconsistencia_codigo_nombre(df: pd.DataFrame, col_codigo: str, col_nombre: str) -> float:
    #Filtramos filas donde ambos valores están presentes
    sub = df[[col_codigo, col_nombre]].dropna()
    total = len(sub)
    if total == 0:
        return 0.0

    #Construimos la relación más frecuente: para cada código, el nombre más común
    modo = (
        sub
        .groupby(col_codigo)[col_nombre]
        .agg(lambda s: s.value_counts().idxmax())
    )

    #Ahora marcamos como inconsistente las filas donde nombre != modo[código]
    #Primero convertimos 'modo' a un dict para lookup rápido
    mapping = modo.to_dict()
    #Aplicamos la verificación
    inconsistentes = sub.apply(
        lambda row: mapping.get(row[col_codigo], None) != row[col_nombre],
        axis=1
    ).sum()

    porcentaje = inconsistentes / total * 100
    return round(porcentaje, 2)

#devuelve el porcentaje de inconsistencia entre jurisdiccion, cod de departamento y cod de localidad
#usando la logica del mapeo mas frecuente
def porcentaje_incoherencia_codigo(
    df: pd.DataFrame,
    cod_dep_col: str = 'Código de departamento',
    jur_col:     str = 'Jurisdicción',
    cod_loc_col: str = 'Código de localidad',
    dep_col:     str = 'Departamento'
) -> dict:
 
    #Filtramos filas completas
    sub = df.dropna(subset=[cod_dep_col, jur_col, cod_loc_col, dep_col])
    total = len(sub)
    if total == 0:
        return {'dep->jur': 0.0, 'loc->dep': 0.0}

    #Inferimos mapeos usando la moda
    mapa_dep_jur = (
        sub.groupby(cod_dep_col)[jur_col]
           .agg(lambda s: s.value_counts().idxmax())
           .to_dict()
    )
    mapa_loc_dep = (
        sub.groupby(cod_loc_col)[dep_col]
           .agg(lambda s: s.value_counts().idxmax())
           .to_dict()
    )

    #Máscaras de inconsistencia
    mask_dep_jur = sub.apply(lambda r: mapa_dep_jur.get(r[cod_dep_col]) != r[jur_col], axis=1)
    mask_loc_dep = sub.apply(lambda r: mapa_loc_dep.get(r[cod_loc_col]) != r[dep_col], axis=1)

    #Calculamos el porcentajes
    return {
        'dep->jur': round(mask_dep_jur.sum() / total * 100, 2),
        'loc->dep': round(mask_loc_dep.sum() / total * 100, 2)
    }

##RESULTADO DEL ANALISIS

#completitud de BP y EE

print("completitud de BP:\n",porcentaje_nulos_columnas_incompletas(df_BP))
#la tabla EE genera muchos null y es un poco ruidosa, vemos su completitud como un detalle extra, porque de EE analizamos 
#principalmente la consistencia de datos
#print(porcentaje_nulos_columnas_incompletas(df_EE))

#inconsistencia por cuanexos duplicados en EE 
print("porcentaje de cuanexos duplicados en EE:",porcentaje_duplicados(df_EE, 'Cueanexo'))

#inconsistencia por tipo de dato erroneo en las columnas de EE

#los tipos de datos de los atributos que queremos analizar
tipos = {
    'Jurisdicción': 'str',
    'Sector': 'str',
    'Ámbito': 'str',
    'Departamento': 'str',
    'Código de departamento': 'int',
    'Localidad': 'str',
    'Código de localidad': 'int',
    'Cueanexo': 'int',
    'Nombre': 'str',
    'Domicilio': 'str',
    'C. P.': 'str',
    'Teléfono': 'str',
    'Mail': 'str',
    
}
print("porcentaje de inconsistencia del tipo de dato:\n",porcentaje_tipo_incorrecto(df_EE, tipos))

#inconsistencia de atributos con valares categoricos en EE
pct, invalidos = analisis_consistencia_categorica(df_EE)
print("Porcentajes de inconsistencia categorica:\n", pct)
#print("Filas inválidas para 'Ámbito':\n", invalidos['Ámbito'])

#inconsistencia de Nombres que no coinciden con su Código de indentificación en EE

#nombre de los pares de columnas codidgo-nombre a comparar
#cod_dep = 'Código de departamento'
#nom_dep = 'Departamento'
cod_loc = 'Código de localidad'
nom_loc = 'Localidad'

#pct_dep = porcentaje_inconsistencia_codigo_nombre(df_EE, cod_dep, nom_dep)
pct_loc = porcentaje_inconsistencia_codigo_nombre(df_EE, cod_loc, nom_loc)

#print(f"incoherencia Departamento-codigo: {pct_dep}%")
print(f"incoherencia Localidad-cogido:   {pct_loc}%")

#inconsistencia entre Jurisdiccion-localidad-departamento incoherentes
resultados = porcentaje_incoherencia_codigo(df_EE,
    cod_dep_col='Código de departamento',
    jur_col='Jurisdicción',
    cod_loc_col='Código de localidad',
    dep_col='Departamento'
)

print("Dep→Jur inconsistente:", resultados['dep->jur'], "%")
print("Loc→Dep inconsistente:", resultados['loc->dep'], "%")

