import requests
import pandas as pd
import unicodedata
import re

# Funções auxiliares
def normalizar(texto):

    # Remove acentos, caracteres especiais e normaliza tamanho
    if not isinstance(texto, str):
        return ""

    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto)
    
    return texto

# Acesso a API
url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    erro_api = False

except:
    erro_api = True

if  not erro_api:
    df = pd.json_normalize(data)

    df = df[[
        "id",
        "nome",
        "microrregiao.mesorregiao.UF.sigla",
        "microrregiao.mesorregiao.UF.regiao.nome"
    ]]

    df.columns = ["id_ibge", "municipio_ibge", "uf", "regiao"]

# Leitura do input.csv
path = "data/input.csv"
municipios_input = pd.read_csv(path)

df['municipio_norm'] = df['municipio_ibge'].apply(normalizar)
municipios_input['municipio_norm'] = municipios_input['municipio'].apply(normalizar)

# Dataframe para output
municipios_output = municipios_input.merge(
    df,
    on='municipio_norm',
    how='left'
)

municipios_output = (
    municipios_output.rename(columns={
        'municipio': 'municipio_input',
        'populacao': 'populacao_input',
    })
    .drop(columns=['municipio_norm'])
)

if not erro_api:
    municipios_output['status'] = 'OK'
else:
    municipios_output['status'] = 'ERRO_API'

municipios_output.loc[municipios_output['municipio_ibge'].duplicated(keep=False), 'status'] = 'AMBIGUO'

municipios_output.loc[
    municipios_output['id_ibge'].isna(),
    'status'
] = 'NAO_ENCONTRADO'

# Definindo estatisticas do output
estatisticas = {
    'stats': {
        'total_municipios': len(municipios_output),
        'total_ok': len(municipios_output[municipios_output['status'] == 'OK']),
        'total_nao_encontrado': len(municipios_output[municipios_output['status'] == 'NAO_ENCONTRADO']),
        'total_erro_api': len(municipios_output[municipios_output['status'] == 'ERRO_API']),
        'pop_total_ok': municipios_output.loc[municipios_output['status'] == 'OK', 'populacao_input'].sum(),
        'medias_por_regiao': (municipios_output.loc[municipios_output['status'] == 'OK']
            .groupby('regiao')['populacao_input']
            .mean()
            .to_dict()
        )
    }
}

municipios_output.to_csv('data/resultados.csv', index=False)

