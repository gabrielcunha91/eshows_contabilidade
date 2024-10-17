

GET_VIEW_FATURAM_ESHOWS = """
SELECT
vfe.*,
tgdc.NOME as 'Grupo',
tke.KEYACCOUNT as 'KeyAccount',
to2.NOME as 'Operador'
FROM View_Faturam_Eshows vfe
INNER JOIN T_COMPANIES tc ON (vfe.c_ID = tc.ID)
LEFT JOIN T_GRUPOS_DE_CLIENTES tgdc ON (tc.FK_GRUPO = tgdc.ID)
LEFT JOIN T_KEYACCOUNT_ESTABELECIMENTO tke ON (tc.FK_KEYACCOUNT = tke.ID)
LEFT JOIN T_OPERADORES to2 ON (tc.FK_OPERADOR = to2.ID)
WHERE vfe.`Data` > '2023-01-01 00:00:00'
ORDER BY vfe.`Data`, vfe.Casa  
"""

GET_FATURAM_FISCAL = """
SELECT
tp.ID as 'tp_ID',
tf.ID as 'tf_ID',
tf.DATA_SHOW as 'Data_Show',
DATE_FORMAT(tf.DATA_SHOW, '%m/%Y') as 'Mes_Ano',
tc.NAME as 'Casa',
tc.ID as 'Casa_ID',
tc.NOTA_FISCAL as 'Casa_Exige_NF',
tgdc.GRUPO_CLIENTES as 'Grupo_Cliente',
ta.NOME as 'Artista',
ta.ID as 'Artista_ID',
REGEXP_REPLACE(tab.NUMERO_DOCUMENTO, '[^a-zA-Z0-9]', '') as 'Documento_Artista',
tpf2.ID as 'Boleto_ID',
DATE(tpf2.DATA_VENCIMENTO) as 'Data_Venc_Boleto',
tpf2.STATUS as 'Status_Boleto',
DATE(tpf2.DATA_COMPENSACAO) as 'Data_Pgto_Boleto',
DATE(tp.DATA_PAGAMENTO) as 'Data_Pgto_Artista',
tp.VALOR_BRUTO as 'Valor_Bruto',
tp.VALOR_LIQUIDO as 'Valor_Liquido',
tf.FATURAM_COMISSAO_ARTISTA as 'Faturam_Comissao_Artista',
tf.FATURAM_ADIANT_ARTISTA as 'Faturam_Adiant_Artista',
tf.FATURAM_ADIANT_CONTRATANTE as 'Faturam_Adiant_Contratante',
tf.FATURAM_SAAS_PERCENTUAL as 'Faturam_Saas_Percentual',
tf.FATURAM_SAAS_MENSALIDADE as 'Faturam_Saas_Mensalidade',
tf.FATURAM_CURADORIA as 'Faturam_Curadoria',
tf.NF_FATURAM_PELO_ARTISTA as 'NF_Pelo_Artista',
tf.NF_FATURAM_CONTRA_ARTISTA as 'NF_Contra_Artista',
tf.NF_FATURAM_CONTRA_CONTRATANTE as 'NF_Contra_Contratante',
(tf.FATURAM_COMISSAO_ARTISTA
 + tf.FATURAM_ADIANT_ARTISTA
 + tf.FATURAM_ADIANT_CONTRATANTE
 + tf.FATURAM_SAAS_PERCENTUAL
 + tf.FATURAM_SAAS_MENSALIDADE
 + tf.FATURAM_CURADORIA) as 'Faturamento_Total',
tf.DATA_PROCESSADO_NOTA as 'Data_Processam_NF',
SUBSTRING_INDEX(SUBSTRING_INDEX(tf.NOTA_URL_PDF_PREFEITURA, 'nf=', -1), '&verificacao', 1) AS 'Numero_NF_Eshows',
tf.NOTA_URL_PDF_PREFEITURA as 'Link_NF_Eshows',
tf.NOTA_ERRO as 'Erro_NF',
tf.NOTA_EMAIL_ERRO as 'NOTA_EMAIL_ERRO',
tnf.NUMERO_NOTA_FISCAL as 'Numero_NF_Artista',
ef.FILENAME as 'Link_NF_Artista'
FROM T_FATURAMENTO tf 
INNER JOIN T_PROPOSTAS tp ON (tf.FK_PROPOSTA = tp.ID)
INNER JOIN T_ATRACOES ta ON (tp.FK_CONTRATADO = ta.ID)
INNER JOIN T_COMPANIES tc ON (tp.FK_CONTRANTE = tc.ID)
LEFT JOIN T_ATRACAO_BANCOS tab ON (tp.FK_ATRACAO_BANCO = tab.ID)
LEFT JOIN T_GRUPOS_DE_CLIENTES tgdc ON (tc.FK_GRUPO = tgdc.ID)
JOIN T_PROPOSTAS_FATURA tpf ON (tp.ID = tpf.FK_PROPOSTA)
JOIN T_PARCELAS_FATURA tpf2 ON (tpf.FK_FATURA = tpf2.FK_FATURA)
LEFT JOIN T_NOTAS_FISCAIS tnf ON (tp.FK_NOTA_FISCAL = tnf.ID AND tnf.FK_STATUS_NF = 101)
LEFT JOIN EPM_FILES ef ON (ef.TABLE_NAME = "T_NOTAS_FISCAIS" AND ef.TABLE_ID = tnf.ID)
WHERE tf.DATA_SHOW > '2024-01-01 00:00:00'
ORDER BY tf.ID DESC
"""

GET_CUSTOS_INTERNOS = """
SELECT
	tcie.ID as 'ID_Despesa',
	"T_CUSTOS_INTERNOS" as 'Tabela_Origem',
    tcie.DESCRICAO AS Descricao_da_Despesa,
    tcp.DESCRICAO AS Classificacao_Primaria,
    tcp.ID AS ID_Classificacao_Primaria,
    tcdc.DESCRICAO AS Centro_de_Custo,
    tcdc2.DESCRICAO AS Categoria_de_Custo,
    tcdc2.ID AS ID_Categoria,
    tcie.DATA_COMPETENCIA AS Data_Vencimento,
    tcie.VALOR AS Valor,
    CAST(CONCAT(YEAR(tcie.DATA_COMPETENCIA), '-', MONTH(tcie.DATA_COMPETENCIA), '-', '01') AS DATE) AS Primeiro_Dia_Mes_Vencimento
FROM T_CUSTOS_INTERNOS_ESHOWS tcie
LEFT JOIN T_CENTROS_DE_CUSTOS tcdc ON (tcie.FK_CENTRO_DE_CUSTO = tcdc.ID)
LEFT JOIN T_CLASSIFICACAO_PRIMARIA tcp ON (tcie.FK_CLASSIFICACAO_PRIMARIA = tcp.ID)
LEFT JOIN T_CATEGORIAS_DE_CUSTO tcdc2 ON (tcp.FK_CATEGORIA_CUSTO = tcdc2.ID)
WHERE
    ((tcie.DATA_VENCIMENTO > '2022-12-31 23:59:59')
        AND (tcie.TAG_INVESTIMENTO <> 1)
            AND (tcie.TAG_ESTORNO <> 1))
"""

GET_CUSTOS_COLABORADORES = """
SELECT
	tcce.ID as 'ID_Despesa',
	"T_CUSTOS_COLABORADORES_ESHOWS" as 'Tabela_Origem',
    CONCAT(tcdc.DESCRICAO, ' - ', tcp.DESCRICAO) AS Descricao_da_Despesa,
    tcp.DESCRICAO AS Classificacao_Primaria,
    tcp.ID AS ID_Classificacao_Primaria,
    tcdc.DESCRICAO AS Centro_de_Custo,
    tcdc2.DESCRICAO AS Categoria_de_Custo,
    tcdc2.ID AS ID_Categoria,
    tcce.DATA_VENCIMENTO AS Data_Vencimento,
    tcce.VALOR AS Valor,
    CAST(CONCAT(YEAR(tcce.DATA_VENCIMENTO), '-', MONTH(tcce.DATA_VENCIMENTO), '-', '01') AS DATE) AS Primeiro_Dia_Mes_Vencimento
FROM T_CUSTOS_COLABORADORES_ESHOWS tcce
JOIN T_COLABORADORES_ESHOWS tce ON (tcce.FK_COLABORADOR = tce.ID)
LEFT JOIN T_CENTROS_DE_CUSTOS tcdc ON (tcce.FK_CENTRO_DE_CUSTO = tcdc.ID)
LEFT JOIN T_CLASSIFICACAO_PRIMARIA tcp ON (tcce.FK_CLASSIFICACAO_PRIMARIA = tcp.ID)
LEFT JOIN T_CATEGORIAS_DE_CUSTO tcdc2 ON (tcp.FK_CATEGORIA_CUSTO = tcdc2.ID)
"""

GET_CUSTOS_PESSOAL = """
SELECT
tcpp.ID as 'ID_Despesa',
"T_CUSTOS_PESSOAL" as 'Tabela_Origem',
CONCAT(tcdc.DESCRICAO, ' - ', tcp.DESCRICAO) AS Descricao_da_Despesa,
tcp.DESCRICAO AS Classificacao_Primaria,
tcp.ID AS ID_Classificacao_Primaria,
tcdc.DESCRICAO AS Centro_de_Custo,
tcdc2.DESCRICAO AS Categoria_de_Custo,
tcdc2.ID AS ID_Categoria,
tcpp.DATA_VENCIMENTO AS Data_Vencimento,
tcpp.VALOR AS Valor,
CAST(CONCAT(YEAR(tcpp.DATA_VENCIMENTO), '-', MONTH(tcpp.DATA_VENCIMENTO), '-', '01') AS DATE) AS Primeiro_Dia_Mes_Vencimento
FROM T_CUSTOS_PESSOAL tcpp 
LEFT JOIN T_CENTROS_DE_CUSTOS tcdc ON (tcpp.CENTRO_DE_CUSTO = tcdc.ID)
LEFT JOIN T_CLASSIFICACAO_PRIMARIA tcp ON (tcpp.CLASSIFICACAO_PRIMARIA = tcp.ID)
LEFT JOIN T_CATEGORIAS_DE_CUSTO tcdc2 ON (tcp.FK_CATEGORIA_CUSTO = tcdc2.ID)
"""

