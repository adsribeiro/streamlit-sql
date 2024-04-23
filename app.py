import streamlit as st
import pandas as pd
import re
from streamlit_ace import st_ace, KEYBINDINGS, LANGUAGES, THEMES
from sql_duckdb import *

st.set_page_config(layout="wide")

st.title("SQL Practice App")    
intro, db, tbl, qry = st.tabs(["1 Introdução ao App","2 Criar Base de dados", "3 Upload Dados", "4 Query"])
def run_query():
    try:
        validate_sql(content,conn)
    except Exception as e:
        st.error(e)


def validate_sql(query:str, conn: DuckDBPyConnection):
    sql = conn.sql(query)
    if re.search("create".lower(),query):
         st.success("Tabela criada com sucesso!")
    if re.search("update".lower(),query):   
         st.success("Update realizado com sucesso!")
    if re.search("drop".lower(),query):
         st.success("Drop table com sucesso!")
    else:
        if sql is not None:
            results_df = sql.to_df()
            st.dataframe(results_df, use_container_width=True)
            export = results_df.to_csv()
            st.download_button(label="Download", data=export, file_name='query_results.csv' )

with intro:
    # st.title("Bem-vindo ao Aplicativo de Análise de Dados utilizando SQL")

    st.write("""
    Este aplicativo permite que você crie e gerencie bases de dados utilizando DuckDB.
    Você pode carregar arquivos para preencher a base de dados e realizar consultas diretamente no navegador.
    """)

    st.header("Como Funciona")

    st.write("""
    1. **Criação de Bases de Dados**: Você pode criar novas bases de dados diretamente no aplicativo.

    2. **Carregar Dados**: Faça upload de arquivos CSV, Excel, ou outros formatos suportados para preencher sua base de dados.

    3. **Executar Consultas**: Utilize a linguagem SQL para fazer consultas na sua base de dados. Os resultados serão exibidos diretamente no navegador.

    4. **Visualização de Dados**: Além de consultas SQL, você pode visualizar os dados utilizando gráficos e tabelas interativas.
    """)

    st.header("Benefícios")

    st.write("""
    - **Facilidade de Uso**: Não é necessário instalar nenhum software adicional. Tudo acontece no navegador.

    - **Eficiência**: DuckDB é uma base de dados rápida e eficiente para análise de dados.

    - **Interação em Tempo Real**: Visualize e analise seus dados em tempo real, sem a necessidade de esperar por processamentos demorados.

    - **Flexibilidade**: Carregue diferentes tipos de arquivos e execute consultas complexas conforme necessário.
    """)

with db:
            
    st.markdown("## Criar base de dados")

    st.info("""Informar uma base terminando em .db para criar. Ex: duckdb.db""")

    db_filename = st.text_input("Nome da Base de dados")
    create_db = st.button('Criar Base de dados')

    if create_db and db_filename:
            conn = connect_db(db_filename)
            if conn:
                    st.success("Base de dados criada! Prosegguir para realizar upload do aquivo.")
            else: 
                st.error('A base de dados deve terminar em .db. Por favor infomar valores corretamente.')

with tbl:
    st.markdown("## Inserir Dados")

    # Upload do arquivo
    file = st.file_uploader("Selecione um arquivo CSV, JSON, Parquet ou Excel (XLSX)",)

    if file is not None:
        # Verificar o tipo de arquivo
        file_type = file.name.split('.')[-1].lower()

        if file_type in ['csv', 'json', 'parquet', 'xlsx']:
            try:
                if file_type == 'csv':
                    df = pd.read_csv(file, encoding='latin1')
                elif file_type == 'json':
                    df = pd.read_json(file)
                elif file_type == 'parquet':
                    df = pd.read_parquet(file)
                elif file_type == 'xlsx':
                    df = pd.read_excel(file)
                df = df.rename(columns=lambda x: x.strip().replace(' ', '_'))
                # Visualizar os dados do arquivo
                st.write("Dados do arquivo:")
                st.write(df)
                
                database_list = list_database()
                selected_db = st.selectbox('Selecione uma base de dados:', options=database_list, key="tbl")
                conn = connect_db(selected_db)
                table = st.text_input("Digite o nome da tabela para inserir os dados:")
                # Inserir os dados em uma tabela DuckDB
                if st.button("Inserir dados em DuckDB"):
                    if table:
                        create_table(conn=conn,table=table)
                        st.success(f"Dados inseridos com sucesso na tabela '{table}'.")
                        st.session_state['file'] = None
                    else:
                        st.error("Por favor, forneça um nome válido para a tabela.")
            except Exception as e:
                st.error(f"Erro ao ler o arquivo: {e}")
        else:
            st.error("Tipo de arquivo não suportado. Por favor, selecione um arquivo CSV, JSON, Parquet ou Excel (XLSX).")


with qry:
   
    database_list = list_database()
    col1, col2 =st.columns([2,10])
    with col1:
         
        selected_db = st.selectbox('Selecione uma base de dados:', options=database_list, )
        if selected_db:
            conn = connect_db(selected_db)
            st.write(f'Tabelas na base de dados {selected_db}:')
            tabelas = list_tables(conn=conn,database=selected_db)
            st.dataframe(pd.DataFrame({'Tabelas': tabelas}),hide_index=True,use_container_width=True)
    with col2:
        col3, col4, col5 = st.columns(3)
        content = st_ace(
             value="",
                            placeholder="--Selecione uma base e digite sua SQL Query aqui!",
                            language= "sql",
                            theme=col3.selectbox("Selecionar o tema",options=THEMES),
                            keybinding=col4.selectbox("Selecionar Keybinding",options=KEYBINDINGS),
                            wrap=True,

                            font_size=col5.slider("Tamanho da Fonte", 10, 24, 16),
                            min_lines=15,
                            key="run_query",
                            height=150
                        )
        

        if content:
            run_query()