import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import os
import numpy as np
from datetime import datetime
import mysql.connector
from utils.queries import *
from utils.user import *
# from workalendar.america import Brazil
# import openpyxl

def handle_login(userName, userPassoword):
    users = st.secrets["users"]

    if userName not in users['emails']:
        st.error("Usuário sem permissão.")
        return
    
    if user_data := login(userName, userPassoword):
        st.session_state["loggedIn"] = True
        st.session_state["user_data"] = user_data
    else:
        st.session_state["loggedIn"] = False
        st.error("Email ou senha inválidos!")

def show_login_page():
    st.markdown(""" 
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
                display: none;
                }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([4,1])
    col1.write("## DashBoard")
    userName = st.text_input(label="", value="", placeholder="Login", label_visibility="collapsed")
    userPassword = st.text_input(label="", value="", placeholder="Senha",type="password", label_visibility="collapsed")
    st.button("login", on_click=handle_login, args=(userName, userPassword))

LOGGER = get_logger(__name__)

def mysql_connection_eshows():
  mysql_config = st.secrets["mysql_eshows"]

  conn_eshows = mysql.connector.connect(
        host=mysql_config['host'],
        port=mysql_config['port'],
        database=mysql_config['database'],
        user=mysql_config['username'],
        password=mysql_config['password']
    )    
  return conn_eshows

def mysql_connection_grupoe():
  mysql_config = st.secrets["mysql_grupoe"]

  conn_grupoe = mysql.connector.connect(
        host=mysql_config['host'],
        port=mysql_config['port'],
        database=mysql_config['database'],
        user=mysql_config['username'],
        password=mysql_config['password']
    )    
  return conn_grupoe

def execute_query(query, conn):
    cursor = conn.cursor()
    cursor.execute(query)

    # Obter nomes das colunas
    column_names = [col[0] for col in cursor.description]
  
    # Obter resultados
    result = cursor.fetchall()
  
    cursor.close()
    return result, column_names

def run():

    ######## Puxando Dados #########
    conn_eshows = mysql_connection_eshows()
    conn_grupoe = mysql_connection_grupoe()


    def view_faturam_eshows():
        result, column_names = execute_query(GET_VIEW_FATURAM_ESHOWS, conn_eshows)
        df_view_faturam_eshows = pd.DataFrame(result, columns=column_names)   

        df_view_faturam_eshows['Data'] = pd.to_datetime(df_view_faturam_eshows['Data'])    

        return df_view_faturam_eshows
    df_view_faturam_eshows = view_faturam_eshows()

    def faturam_fiscal():
        result, column_names = execute_query(GET_FATURAM_FISCAL, conn_eshows)
        df_faturam_fiscal = pd.DataFrame(result, columns=column_names)           
    
        df_faturam_fiscal['Data_Show'] = pd.to_datetime(df_faturam_fiscal['Data_Show'])

        return df_faturam_fiscal
    df_faturam_fiscal = faturam_fiscal()

    def diferencas_faturam_fiscal():
        result, column_names = execute_query(GET_DIFERENCAS_FATURAM_FISCAL, conn_eshows)
        df_diferencas_faturam_fiscal = pd.DataFrame(result, columns=column_names)           
    
        df_diferencas_faturam_fiscal['Data_Show'] = pd.to_datetime(df_diferencas_faturam_fiscal['Data_Show'])

        return df_diferencas_faturam_fiscal
    df_diferencas_faturam_fiscal = diferencas_faturam_fiscal()

    def custos_internos():
        result, column_names = execute_query(GET_CUSTOS_INTERNOS, conn_grupoe)
        df_custos_internos = pd.DataFrame(result, columns=column_names)

        df_custos_internos['Data_Vencimento'] = pd.to_datetime(df_custos_internos['Data_Vencimento'])

        return df_custos_internos
    df_custos_internos = custos_internos()


    ######## Definindo Relatorio ########
    st.write("# Dash Eshows")

    st.markdown(
        """
        Utilize as abas localizadas no lado esquerdo para buscar suas análises.
    """
    ) 

    if "view_faturam_eshows" not in st.session_state:
        st.session_state["view_faturam_eshows"] = df_view_faturam_eshows

    if "faturam_fiscal" not in st.session_state:
        st.session_state["faturam_fiscal"] = df_faturam_fiscal

    if "diferencas_faturam_fiscal" not in st.session_state:
        st.session_state["diferencas_faturam_fiscal"] = df_diferencas_faturam_fiscal        

if __name__ == "__main__":
     ######## Config Pag ##########
    st.set_page_config(
    page_title="Dash_Eshows",
    page_icon="🎵",
    )
    
    with st.sidebar:
        st.button(label="Logout", on_click=logout)

    if "loggedIn" not in st.session_state:
        st.session_state["loggedIn"] = False
        st.session_state["user_date"] = None

    if not st.session_state["loggedIn"]:
        show_login_page()
        st.stop()
    else:
        run()


