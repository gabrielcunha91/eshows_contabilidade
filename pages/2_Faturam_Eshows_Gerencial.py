import streamlit as st
import pandas as pd
import datetime
import calendar
from utils.functions.general_functions import *

st.set_page_config(
    page_title="Faturam_Eshows_Gerencial",
    page_icon="🎵",
    layout="wide"
)


### Puxando Dados ###
df_view_faturam_eshows = st.session_state["view_faturam_eshows"]

df_view_faturam_eshows["Grupo"] = df_view_faturam_eshows["Grupo"].fillna("Outros")

colunas_para_somar_faturam = ["Comissao_Eshows_B2B", "Comissao_Eshows_B2C", "SAAS_Mensalidade", "SAAS_Percentual", "Curadoria",
                              "Taxa_Adiantamento", "Taxa_Emissao_NF"]

df_view_faturam_eshows["Faturam_Total"] = df_view_faturam_eshows[colunas_para_somar_faturam].sum(axis=1)

### Agrupamentos ###
df_view_faturam_ajustado = df_view_faturam_eshows[["Primeiro_Dia_Mes", "p_ID", "Casa", "Valor_Total", "Comissao_Eshows_B2B",
                                                    "Comissao_Eshows_B2C", "SAAS_Mensalidade", "SAAS_Percentual", "Curadoria",
                                                      "Taxa_Adiantamento", "Taxa_Emissao_NF", "Grupo", "Faturam_Total"]]


df_view_faturam_por_mes = df_view_faturam_ajustado.groupby("Primeiro_Dia_Mes").agg(
    {"Casa": "nunique", "p_ID": "nunique", "Valor_Total": "sum", "Comissao_Eshows_B2B": "sum", "Comissao_Eshows_B2C": "sum",
     "SAAS_Mensalidade": "sum", "SAAS_Percentual": "sum", "Curadoria": "sum", "Taxa_Adiantamento": "sum", "Taxa_Emissao_NF": "sum", "Faturam_Total": "sum"})

df_view_faturam_por_mes["Perc_Comissao"] = df_view_faturam_por_mes["Comissao_Eshows_B2B"]/df_view_faturam_por_mes["Valor_Total"]

# colunas_para_somar_faturam = ["Comissao_Eshows_B2B", "Comissao_Eshows_B2C", "SAAS_Mensalidade", "SAAS_Percentual", "Curadoria",
#                               "Taxa_Adiantamento", "Taxa_Emissao_NF"]

# df_view_faturam_por_mes["Faturam_Total"] = df_view_faturam_por_mes[colunas_para_somar_faturam].sum(axis=1)

df_view_faturam_por_mes["Prog_Faturam_Total"] = df_view_faturam_por_mes["Faturam_Total"]

## Faturamento por mes consolidado geral
df_view_faturam_por_mes_formatado = format_columns_brazilian(df_view_faturam_por_mes, ["Valor_Total","Comissao_Eshows_B2B", "Comissao_Eshows_B2C", "SAAS_Mensalidade", "SAAS_Percentual", "Curadoria",
                              "Taxa_Adiantamento", "Taxa_Emissao_NF", "Faturam_Total"])


df_view_faturam_por_mes_formatado = format_columns_percentage(df_view_faturam_por_mes_formatado, ["Perc_Comissao"])

# Convertendo as coluna Casa e Num_Shows para numérico, tratando erros
df_view_faturam_por_mes_formatado['Casa'] = pd.to_numeric(df_view_faturam_por_mes_formatado['Casa'], errors='coerce')
df_view_faturam_por_mes_formatado['p_ID'] = pd.to_numeric(df_view_faturam_por_mes_formatado['p_ID'], errors='coerce')
df_view_faturam_por_mes_formatado['Prog_Faturam_Total'] = pd.to_numeric(df_view_faturam_por_mes_formatado['Prog_Faturam_Total'], errors='coerce')

# Remover nulos antes de calcular max
df_view_faturam_por_mes_formatado.dropna(subset=['Casa'], inplace=True)
df_view_faturam_por_mes_formatado.dropna(subset=['p_ID'], inplace=True)
df_view_faturam_por_mes_formatado.dropna(subset=['Prog_Faturam_Total'], inplace=True)

# Calcular o valor máximo
max_valor_casas = df_view_faturam_por_mes_formatado["Casa"].max()
max_valor_casas = int(max_valor_casas)  # Converter para int para evitar problemas

max_valor_shows = df_view_faturam_por_mes_formatado["p_ID"].max()
max_valor_shows = int(max_valor_shows)  # Converter para int para evitar problemas

max_valor_faturam = df_view_faturam_por_mes_formatado["Prog_Faturam_Total"].max()
max_valor_faturam = int(max_valor_faturam)  # Converter para int para evitar problemas

# Contando o número de linhas
num_linhas = df_view_faturam_por_mes_formatado.shape[0]  # ou df_view_faturam_por_mes_formatado.count()
# Calcular altura necessária (por exemplo, 40 pixels por linha)
altura_por_linha = 40
altura_total = num_linhas * altura_por_linha - 80  

st.data_editor(
    df_view_faturam_por_mes_formatado,
    column_config={
        "Primeiro_Dia_Mes": st.column_config.DatetimeColumn(
            "Mes_Ano",
            format="MM/YYYY" 
        ),
        "Casa": st.column_config.ProgressColumn(
            "Num_de_Casas",
            format="%.0f",
            min_value=0,
            max_value=max_valor_casas
        ),
        "p_ID": st.column_config.ProgressColumn(
            "Num_de_Shows",
            format="%.0f",
            min_value=0,
            max_value=max_valor_shows
        ),
        "Prog_Faturam_Total": st.column_config.ProgressColumn(
            "Prog_Faturam",
            format="%.2f",
            min_value=0,
            max_value=max_valor_faturam,
        )
    },
    height=altura_total  # Defina a altura da tabela, ajuste conforme necessário
)



# Filtando grupos
grupos = sorted(df_view_faturam_ajustado["Grupo"].unique())
grupo_padrao = grupos

# Criando colunas para organizar os elementos lado a lado
col1, col2 = st.columns([1, 4])  # Ajuste as proporções conforme necessário

# Checkbox para selecionar ou desmarcar todos os grupos
with col1:
    selecionar_todos = st.checkbox("Selecionar todos os grupos")

# Campo multiselect
with col2:
    if selecionar_todos:
        grupo = st.multiselect("Grupos", grupos, grupos)  # Todos os grupos pré-selecionados
    else:
        grupo = st.multiselect("Grupos", grupos)  # Nenhum grupo pré-selecionado

df_view_faturam_por_grupo = df_view_faturam_ajustado[df_view_faturam_ajustado["Grupo"].isin(grupo)]

# Filtrando casas
casas = sorted(df_view_faturam_por_grupo["Casa"].unique())
casas_padrao = casas
casa = st.multiselect("Casas", casas, default=casas_padrao)

df_view_faturam_por_casa = df_view_faturam_ajustado[df_view_faturam_ajustado["Casa"].isin(casa)]

# Filtrando Data
today = datetime.datetime.now()
last_year = today.year - 1
jan_last_year = datetime.datetime(last_year, 1, 1)
jan_this_year = datetime.datetime(today.year, 1, 1)
last_day_of_month = calendar.monthrange(today.year, today.month)[1]
this_month_this_year = datetime.datetime(today.year, today.month, last_day_of_month)

dec_this_year = datetime.datetime(today.year, 12, 31)

date_input = st.date_input("Período",
                           (jan_this_year, this_month_this_year),
                           jan_last_year,
                           dec_this_year,
                           format="DD/MM/YYYY"
                           )


mask = (df_view_faturam_por_casa["Primeiro_Dia_Mes"] >= date_input[0]) & (df_view_faturam_por_casa["Primeiro_Dia_Mes"] <= date_input[1])
df_view_faturam_por_casa_data = df_view_faturam_por_casa[mask]

## Faturamento por mes por grupo
df_view_faturam_por_casa_data = df_view_faturam_por_casa_data.groupby("Primeiro_Dia_Mes").agg(
    {"Casa": "nunique", "p_ID": "nunique", "Valor_Total": "sum", "Comissao_Eshows_B2B": "sum", "Comissao_Eshows_B2C": "sum",
     "SAAS_Mensalidade": "sum", "SAAS_Percentual": "sum", "Curadoria": "sum", "Taxa_Adiantamento": "sum", "Taxa_Emissao_NF": "sum", "Faturam_Total": "sum"})


df_view_faturam_por_casa_data_formatado = format_columns_brazilian(df_view_faturam_por_casa_data, ["Valor_Total", "Comissao_Eshows_B2B", "Comissao_Eshows_B2C",
                                                                                                   "SAAS_Mensalidade", "SAAS_Percentual", "Curadoria", "Taxa_Adiantamento", "Taxa_Emissao_NF", "Faturam_Total"])


st.data_editor(
    df_view_faturam_por_casa_data,
    column_config={
        "Primeiro_Dia_Mes": st.column_config.DatetimeColumn(
            "Mes_Ano",
            format="MM/YYYY" 
        ),
        "Casa": st.column_config.NumberColumn(
            "Num_de_Casas",
            format="%.0f",
            min_value=0,
            step=1
        ),
        "p_ID": st.column_config.NumberColumn(
            "Num_de_Shows",
            min_value=0,
            step=1,
            format="%.0f"
        )
    }
)


# ## Abrindo as propostas
st.markdown("Abertura por propostas:") 
# df_view_faturam_eshows
df_view_faturam_proposta = df_view_faturam_eshows[["p_ID", "Casa", "UF", "Cidade", "Data", "Artista", "Grupo", "Valor_Bruto", "Valor_Total",
                                                   "Valor_Liquido", "Comissao_Eshows_B2B", "Comissao_Eshows_B2C", "Taxa_Adiantamento",
                                                   "Curadoria", "SAAS_Percentual", "SAAS_Mensalidade", "Taxa_Emissao_NF", "Faturam_Total" ,"KeyAccount"]]

df_view_faturam_proposta = df_view_faturam_proposta[df_view_faturam_proposta["Casa"].isin(casa)]

df_view_faturam_proposta = df_view_faturam_proposta[mask]

#st.dataframe(df_view_faturam_proposta, use_container_width=True)

df_view_faturam_proposta['Valor_Bruto'] = pd.to_numeric(df_view_faturam_proposta['Valor_Bruto'], errors='coerce')
max_valor_bruto = df_view_faturam_proposta['Valor_Bruto'].max()

df_view_faturam_proposta_formatado = df_view_faturam_proposta.copy()
df_view_faturam_proposta_formatado = format_columns_brazilian(df_view_faturam_proposta_formatado, ['Valor_Bruto', 'Valor_Total', 'Valor_Liquido', 'Comissao_Eshows_B2B', 'Comissao_Eshows_B2C',
                                                                                                    'Taxa_Adiantamento', 'Curadoria', 'SAAS_Percentual', 'SAAS_Mensalidade', 'Taxa_Emissao_NF', 'Faturam_Total'])

df_view_faturam_proposta_formatado

excel_filename = 'faturamento_gerencial.xlsx'

if st.button('Atualizar Planilha Excel'):
    sheet_name = 'df_faturam_gerencial'
    export_to_excel(df_view_faturam_proposta, sheet_name, excel_filename)

    st.success('Arquivo atualizado com sucesso!')

if st.button('Baixar Excel'):
  if os.path.exists(excel_filename):
    with open(excel_filename, "rb") as file:
      file_content = file.read()
    st.download_button(
      label="Clique para baixar o arquivo Excel",
      data=file_content,
      file_name="faturamento_gerencial.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )    

