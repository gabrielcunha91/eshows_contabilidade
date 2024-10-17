import streamlit as st
import pandas as pd
import datetime
import calendar


st.set_page_config(
    page_title="Faturam_Eshows_Gerencial",
    page_icon="🎵",
    layout="wide"
)


### Puxando Dados ###
df_view_faturam_eshows = st.session_state["view_faturam_eshows"]


### Agrupamentos ###
df_view_faturam_ajustado = df_view_faturam_eshows[["Primeiro_Dia_Mes", "p_ID", "Casa", "Valor_Total", "Comissao_Eshows_B2B",
                                                    "Comissao_Eshows_B2C", "SAAS_Mensalidade", "SAAS_Percentual", "Curadoria",
                                                      "Taxa_Adiantamento", "Taxa_Emissao_NF", "Grupo"]]


df_view_faturam_por_mes = df_view_faturam_ajustado.groupby("Primeiro_Dia_Mes").agg(
    {"Casa": "nunique", "p_ID": "nunique", "Valor_Total": "sum", "Comissao_Eshows_B2B": "sum", "Comissao_Eshows_B2C": "sum",
     "SAAS_Mensalidade": "sum", "SAAS_Percentual": "sum", "Curadoria": "sum", "Taxa_Adiantamento": "sum", "Taxa_Emissao_NF": "sum"})

df_view_faturam_por_mes["Perc_Comissao"] = df_view_faturam_por_mes["Comissao_Eshows_B2B"]/df_view_faturam_por_mes["Valor_Total"]
colunas_para_somar_faturam = ["Comissao_Eshows_B2B", "Comissao_Eshows_B2C", "SAAS_Mensalidade", "SAAS_Percentual", "Curadoria",
                              "Taxa_Adiantamento", "Taxa_Emissao_NF"]

df_view_faturam_por_mes["Faturam_Total"] = df_view_faturam_por_mes[colunas_para_somar_faturam].sum(axis=1)


## Faturamento por mes consolidado geral
df_view_faturam_por_mes

# Filtando grupos
grupos = df_view_faturam_ajustado["Grupo"].unique()
grupo_padrao = "Coco Bambu"  # Defina o grupo padrão aqui
grupo = st.selectbox("Grupo", grupos, index=grupos.tolist().index(grupo_padrao))

df_view_faturam_por_grupo =  df_view_faturam_ajustado[df_view_faturam_ajustado["Grupo"] == grupo]

# Filtrando Data
today = datetime.datetime.now()
last_year = today.year - 1
jan_last_year = datetime.datetime(last_year, 1, 1)
last_day_of_month = calendar.monthrange(today.year, today.month)[1]
this_month_this_year = datetime.datetime(today.year, today.month, last_day_of_month)

dec_this_year = datetime.datetime(today.year, 12, 31)

date_input = st.date_input("Período",
                           (jan_last_year, this_month_this_year),
                           jan_last_year,
                           dec_this_year,
                           format="DD/MM/YYYY"
                           )


mask = (df_view_faturam_por_grupo["Primeiro_Dia_Mes"] >= date_input[0]) & (df_view_faturam_por_grupo["Primeiro_Dia_Mes"] <= date_input[1])
df_view_faturam_por_grupo_data = df_view_faturam_por_grupo[mask]

## Faturamento por mes por grupo
df_view_faturam_por_grupo_data = df_view_faturam_por_grupo_data.groupby("Primeiro_Dia_Mes").agg(
    {"Casa": "nunique", "p_ID": "nunique", "Valor_Total": "sum", "Comissao_Eshows_B2B": "sum", "Comissao_Eshows_B2C": "sum",
     "SAAS_Mensalidade": "sum", "SAAS_Percentual": "sum", "Curadoria": "sum", "Taxa_Adiantamento": "sum", "Taxa_Emissao_NF": "sum"})


df_view_faturam_por_grupo_data

# ## Abrindo as propostas
# st.markdown("Abertura por propostas:") 
# df_view_faturam_eshows

