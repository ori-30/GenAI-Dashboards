from snowflake.snowpark import Session
import json
import streamlit as st

def snowpark_basic_auth() -> Session:
    with open('cred.json', 'r') as config_file:
        try:
            config = json.load(config_file)
        except json.JSONDecodeError:
            raise ValueError("Error al cargar el archivo JSON. Asegúrate de que el archivo no esté vacío y tenga un formato JSON válido.")


    account = config['Snowflake']['account']
    user = config['Snowflake']['user']
    password = config['Snowflake']['password']

    connection_parameters = {
        "ACCOUNT": account,
        "USER": user,
        "PASSWORD": password
    }
    return Session.builder.configs(connection_parameters).create()
#snowflake conn for streamlit
def snowpark_auth(account,user,password) -> Session:
    connection_parameters = {
        "ACCOUNT": account,
        "USER": user,
        "PASSWORD": password
    }
    return Session.builder.configs(connection_parameters).create()
def snowpark_basic_auth_toml() -> Session:
    account = st.secrets["SNOWFLAKE_ACCOUNT"]
    user = st.secrets["SNOWFLAKE_USER"]
    password = st.secrets["SNOWFLAKE_PASSWORD"]
    connection_parameters = {
        "ACCOUNT": account,
        "USER": user,
        "PASSWORD": password
    }
    return Session.builder.configs(connection_parameters).create()
def execute_query_and_fetch_dataframe(session,db):
    session.sql("use role accountadmin").collect()
    query = """
    SELECT DISTINCT
        TABLES.TABLE_NAME,
        TABLES.COMMENT AS TABLE_DESC,
        COLUMNS.COLUMN_NAME,
        COLUMNS.COMMENT AS COLUMN_DESC,
        COLUMNS.DATA_TYPE
    FROM 
        {}.INFORMATION_SCHEMA.COLUMNS AS COLUMNS
    JOIN
        {}.INFORMATION_SCHEMA.TABLES AS TABLES
    ON
        COLUMNS.TABLE_NAME = TABLES.TABLE_NAME
        AND TABLES.TABLE_SCHEMA != 'INFORMATION_SCHEMA'
    ORDER BY
        TABLES.TABLE_NAME, COLUMNS.COLUMN_NAME;
    """
    query=query.format(db,db)
    result = session.sql(query).collect()

    result_json = {}
    for row in result:
        table_name = row['TABLE_NAME']
        table_comment = row['TABLE_DESC']
        column_name = row['COLUMN_NAME']
        column_comment = row['COLUMN_DESC']
        column_type = row["DATA_TYPE"]

        # Add table and column info to the result_json
        if table_name not in result_json:
            result_json[table_name] = {
                'table': table_name,
                'comment': table_comment,
                'columns': []
            }

        result_json[table_name]['columns'].append({
            'column': column_name,
            'type': column_type,
            'comment': column_comment
        })

    return list(result_json.values())

def divide_list(result_json, max_size):
    json_str = json.dumps(result_json, ensure_ascii=False)
    
    # Verifica si el JSON ya es suficientemente pequeño
    if len(json_str) <= max_size:
        return [result_json]

    # Divide el JSON en fragmentos más pequeños
    fragments = []
    current_fragment = []

    for item in result_json:
        current_fragment.append(item)
        current_size = len(json.dumps(current_fragment, ensure_ascii=False))
        
        if current_size > max_size:
            fragments.append(current_fragment[:-1])
            current_fragment = [item]

    # Agrega el último fragmento si es necesario
    if current_fragment:
        fragments.append(current_fragment)

    return fragments

def save_fragments_to_json(fragments, output_prefix="parte"):
    for idx, fragment in enumerate(fragments):
        output_file = f"{output_prefix}_{idx + 1}.json"
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(fragment, file, ensure_ascii=False, indent=2)
        print(f"Fragment {idx + 1} saved to {output_file}")

def get_metadata(account,user,password,db):
    conn=snowpark_auth(account,user,password)
    GEN_SQL = """
Vas a actuar como un experto data architect de Snowflake llamado Yorkis.
Tu objetivo es aplicar inteligencia al proceso de segmentación por dominios en la capa Golden.

La respuesta esperada es un listado con los dominios recomendados por la IA, así como un listado de las tablas que deberían pertenecer a esos dominios.

Para ello debes ayudarte de una descripción de la empresa, sus áreas de negocio y los metadatos de las tablas.
Estos metadatos incluyen el nombre de la tabla, su descripción, el nombre de las columnas, su tipo y su descripción. Los metadataos tienen este formato:

Table: table1
Description: description1
Columns:
Column: column1
Description: column1 description


Tambien tienes que generar las queries SQL necesarias para generar los dominios y las tablas que has propuesto.
Esto lo haras usando la capa golden como base de datos, los dominios como esquemas y las tablas como tablas, te dejo un ejemplo de como deberia ser la query SQL:
CREATE DATABASE IF NOT EXISTS <database>;
CREATE SCHEMA IF NOT EXISTS <database>.<domain_name>;
CREATE TABLE IF NOT EXISTS <database>.<domain_name>.<table_name> AS SELECT * FROM <table_name>;

Te dejo un serie de normas que debes cumplir para poder hacer el ejercicio:
1. Necesitas 3 componentes para generar los dominios. La description, las areas y los metadatos)
2. Debes revisar que tienes todos antes de preguntar.
3. Si te falta un componente despues de revisarlo pidelo.
5. Cuando hayas procesado todos los componenetes, debes generar los dominios y las tablas y añadir una explicación de por qué has elegido esos dominios y tablas.
6. Es primordial que una tabla no puede estar en varios dominios.

Para recapitular te indico los pasos que debes seguir siempre de manera inequivoca:
1. Da una bienvenida y explica lo que haces
2. Revisa que tienes los 3 componentes. Si no es asi, pidelos.
3. Procesa la descripción de la empresa y las áreas de negocio y los metadatos de las tablas para generar los dominios y las tablas. Recuerda que una tabla no puede estar en varios dominios.
4. Pide confirmacion antes de generar las queries

A continuación te dejo los metadatos de las tablas:

"""
    Metadata_prompt = ""
    Metadatat = execute_query_and_fetch_dataframe(conn,db)
    
    for i in Metadatat:
        table_value = i.get('table', '')
        comment_value = i.get('comment', '')
        
        Metadata_prompt += f"Table: {table_value}\nDescription: {comment_value}\nColumns:\n"
        
        for j in i.get('columns', []):
            column_value = j.get('column', '')
            comment_column_value = j.get('comment', '')
            
            Metadata_prompt += f"Column: {column_value}\nDescription: {comment_column_value}\n"
    
    prompt = GEN_SQL + Metadata_prompt
    return prompt
if __name__ == '__main__':
    #conn=snowpark_basic_auth()
    prompt=get_metadata("DEMO")
    #with open('prompt.txt', 'w') as f:
    #    f.write(prompt)
    print(prompt)
    #session_with_pwd=snowpark_basic_auth()

    #result_json = execute_query_and_fetch_dataframe(session_with_pwd)
    #print(result_json)
    #result_fragments = divide_list(result_json, 10000)
    #save_fragments_to_json(result_fragments)
    #print(json.dumps(result_fragments[1], ensure_ascii=False, indent=2))
    