# IBGE Municípios - Normalização e Envio de Estatísticas

Este projeto realiza a leitura de um arquivo de municípios com população, faz **normalização e correção de nomes**, compara com os dados oficiais do **IBGE**, gera um CSV de saída e envia estatísticas agregadas para uma função do **Supabase**.

---

## 🚀 Funcionalidades

1. **Leitura do CSV de entrada**  
   - Exemplo de arquivo: `input.csv`  
   - Colunas obrigatórias: `municipio`, `populacao`

2. **Normalização de dados**  
   - Remove espaços, acentos e caracteres inconsistentes  
   - Converte nomes para minúsculo/capitalização uniforme  

3. **Consulta e mapeamento com IBGE**  
   - Utiliza a API pública do IBGE para obter informações oficiais  
   - Campos extraídos:  
     - `municipio_ibge` (nome oficial)  
     - `uf` (sigla da unidade federativa)  
     - `regiao` (Norte, Nordeste, Centro-Oeste, Sudeste, Sul)  
     - `id_ibge` (código IBGE)

4. **Geração do CSV de saída (`resultado.csv`)**  
   - Colunas:  
     ```
     municipio_input,populacao_input,municipio_ibge,uf,regiao,id_ibge,status
     ```
   - Status possíveis:  
     - `OK` → match correto  
     - `NAO_ENCONTRADO` → não há correspondência  
     - `AMBIGUO` → múltiplos matches encontrados  
     - `ERRO_API` → falha na consulta à API

5. **Cálculo de estatísticas**  
   - Total de municípios processados  
   - Total de correspondências corretas (`OK`)  
   - Total de não encontrados (`NAO_ENCONTRADO`)  
   - Total de erros de API (`ERRO_API`)  
   - Soma da população dos municípios `OK`  
   - Média de população por região


---

## ⚙️ Como rodar

1. **Instalar dependências**

```bash
pip install -r requirements.txt
```

2. **Executar o script**

```bash
python main.py
```

### ⚠️ Observações sobre correspondência de municípios

- Municípios que estão com **escrita incorreta ou divergente no `input.csv`** podem não ser encontrados na base oficial do IBGE.  
- Esses casos são marcados no CSV de saída como `NAO_ENCONTRADO`.  
- Para aumentar a chance de match correto, o script realiza **normalização básica** (remoção de espaços extras, capitalização uniforme e remoção de acentos).  
- Nomes com erros mais complexos ou muito diferentes do padrão oficial **não serão corrigidos automaticamente**.
- Para municípios de UF distintos, mas com mesmo nome, o status é considerado "Ambíguo".
