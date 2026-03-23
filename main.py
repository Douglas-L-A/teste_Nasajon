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

import json

# Converte estatisticas para tipos nativos
def convert_numpy(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(v) for v in obj]
    elif hasattr(obj, "item"):  # numpy scalars
        return obj.item()
    else:
        return obj

estatisticas_json = convert_numpy(estatisticas)


PROJECT_FUNCTION_URL="https://mynxlubykylncinttggu.functions.supabase.co/ibge-submit"
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsImtpZCI6ImR0TG03UVh1SkZPVDJwZEciLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL215bnhsdWJ5a3lsbmNpbnR0Z2d1LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJhZTc2OWU3MC1kNTFjLTQ1ZGMtYTVmMi1kY2I4NWJhZGE0MGUiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzc0MzAwMzk1LCJpYXQiOjE3NzQyOTY3OTUsImVtYWlsIjoiZC5sZW1vc2FyYXVqbzIwMDFAZ21haWwuY29tIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJlbWFpbCIsInByb3ZpZGVycyI6WyJlbWFpbCJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbCI6ImQubGVtb3NhcmF1am8yMDAxQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJub21lIjoiRG91Z2xhcyBMZW1vcyBBcmF1am8iLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6ImFlNzY5ZTcwLWQ1MWMtNDVkYy1hNWYyLWRjYjg1YmFkYTQwZSJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzc0Mjk2Nzk1fV0sInNlc3Npb25faWQiOiI2OWVlMGM5Mi0wMTdjLTRmYjUtYTM1Zi1iZmIzZDgzODBjZDgiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.fqaCTjIE564Qi_MxfsK5nmUre-Hms5byPM5c9b99Or0"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(
    PROJECT_FUNCTION_URL,
    json=estatisticas_json,
    headers=headers
)

print("Status code:", response.status_code)
print("Resposta:", response.text)