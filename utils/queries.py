

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
WITH propostas_faturamento AS (
    SELECT
        tp.ID AS proposta_ID,
        tf.ID AS fatura_ID,
        MAX(tpf2.DATA_VENCIMENTO) AS vencimento_ultima_parcela,
        COUNT(tpf2.ID) AS numero_parcelas,
        COUNT(CASE WHEN tpf2.STATUS = 'Received' THEN tpf2.ID END) AS numero_parcelas_pagas,
        CASE
            WHEN COUNT(CASE WHEN tpf2.STATUS = 'Received' THEN tpf2.ID END) = COUNT(tpf2.ID)
                THEN 'QUITADO'
            WHEN COUNT(CASE WHEN tpf2.STATUS = 'Received' THEN tpf2.ID END) = 0 AND MAX(tpf2.DATA_VENCIMENTO) > CURDATE() 
                THEN 'PENDENTE'
            WHEN COUNT(CASE WHEN tpf2.STATUS = 'Received' THEN tpf2.ID END) < COUNT(tpf2.ID) AND MAX(tpf2.DATA_VENCIMENTO) < CURDATE() 
                THEN 'ATRASADO'
            ELSE 'PARCIAL'
        END AS 'Status_Recebimento'
    FROM T_PROPOSTAS tp
    LEFT JOIN T_PROPOSTAS_FATURA tpf ON (tp.ID = tpf.FK_PROPOSTA)
    LEFT JOIN T_FATURAS tf ON (tpf.FK_FATURA = tf.ID)
    LEFT JOIN T_PARCELAS_FATURA tpf2 ON (tf.ID = tpf2.FK_FATURA)
    WHERE tpf2.CANCELADO = 0 
    GROUP BY tp.ID
)
SELECT 
    tp.ID AS 'tp_ID',
    tf.ID AS 'tf_ID',
    tf.DATA_SHOW AS 'Data_Show',
    DATE_FORMAT(tf.DATA_SHOW, '%m/%Y') AS 'Mes_Ano',
    tc.NAME AS 'Casa',
    tc.ID AS 'Casa_ID',
    tc.NOTA_FISCAL AS 'Casa_Exige_NF',
    tgdc.GRUPO_CLIENTES AS 'Grupo_Cliente',
    ta.NOME AS 'Artista',
    ta.ID AS 'Artista_ID',
    REGEXP_REPLACE(tab.NUMERO_DOCUMENTO, '[^a-zA-Z0-9]', '') AS 'Documento_Artista',
    pf.fatura_ID AS 'Fatura_ID',
    pf.vencimento_ultima_parcela AS 'Vencimento_Ultima_Parcela',
    pf.numero_parcelas AS 'Numero_Parcelas',
    pf.numero_parcelas_pagas AS 'Numero_Parcelas_Pagas',
    pf.Status_Recebimento AS 'Status_Recebimento',
    MAX(DATE(tp.DATA_PAGAMENTO)) AS 'Data_Pgto_Artista',
    MAX(tp.VALOR_BRUTO) AS 'Valor_Bruto',
    MAX(tp.VALOR_LIQUIDO) AS 'Valor_Liquido',
    MAX(tf.FATURAM_COMISSAO_ARTISTA) AS 'Faturam_Comissao_Artista',
    MAX(tf.FATURAM_ADIANT_ARTISTA) AS 'Faturam_Adiant_Artista',
    MAX(tf.FATURAM_ADIANT_CONTRATANTE) AS 'Faturam_Adiant_Contratante',
    MAX(tf.FATURAM_SAAS_PERCENTUAL) AS 'Faturam_Saas_Percentual',
    MAX(tf.FATURAM_SAAS_MENSALIDADE) AS 'Faturam_Saas_Mensalidade',
    MAX(tf.FATURAM_CURADORIA) AS 'Faturam_Curadoria',
    MAX(tf.NF_FATURAM_PELO_ARTISTA) AS 'NF_Pelo_Artista',
    MAX(tf.NF_FATURAM_CONTRA_ARTISTA) AS 'NF_Contra_Artista',
    MAX(tf.NF_FATURAM_CONTRA_CONTRATANTE) AS 'NF_Contra_Contratante',
    (MAX(tf.FATURAM_COMISSAO_ARTISTA)
     + MAX(tf.FATURAM_ADIANT_ARTISTA)
     + MAX(tf.FATURAM_ADIANT_CONTRATANTE)
     + MAX(tf.FATURAM_SAAS_PERCENTUAL)
     + MAX(tf.FATURAM_SAAS_MENSALIDADE)
     + MAX(tf.FATURAM_CURADORIA)) AS 'Faturamento_Total',
    MAX(tf.DATA_PROCESSADO_NOTA) AS 'Data_Processam_NF',
    MAX(SUBSTRING_INDEX(SUBSTRING_INDEX(tf.NOTA_URL_PDF_PREFEITURA, 'nf=', -1), '&verificacao', 1)) AS 'Numero_NF_Eshows',
    MAX(tf.NOTA_URL_PDF_PREFEITURA) AS 'Link_NF_Eshows',
    MAX(tf.NOTA_ERRO) AS 'Erro_NF',
    MAX(tf.NOTA_EMAIL_ERRO) AS 'NOTA_EMAIL_ERRO',
    MAX(tnf.NUMERO_NOTA_FISCAL) AS 'Numero_NF_Artista',
    MAX(ef.FILENAME) AS 'Link_NF_Artista'
FROM T_FATURAMENTO tf 
INNER JOIN T_PROPOSTAS tp ON (tf.FK_PROPOSTA = tp.ID)
INNER JOIN T_ATRACOES ta ON (tp.FK_CONTRATADO = ta.ID)
INNER JOIN T_COMPANIES tc ON (tp.FK_CONTRANTE = tc.ID)
LEFT JOIN T_ATRACAO_BANCOS tab ON (tp.FK_ATRACAO_BANCO = tab.ID)
LEFT JOIN T_GRUPOS_DE_CLIENTES tgdc ON (tc.FK_GRUPO = tgdc.ID)
LEFT JOIN propostas_faturamento pf ON (tp.ID = pf.proposta_ID)
LEFT JOIN T_NOTAS_FISCAIS tnf ON (tp.FK_NOTA_FISCAL = tnf.ID AND tnf.FK_STATUS_NF = 101)
LEFT JOIN EPM_FILES ef ON (ef.TABLE_NAME = "T_NOTAS_FISCAIS" AND ef.TABLE_ID = tnf.ID)
WHERE tp.FK_STATUS_PROPOSTA NOT IN (102)
AND tc.ID NOT IN (102, 196, 633)
AND tf.DATA_SHOW > '2024-01-01 00:00:00'
GROUP BY tp.ID
ORDER BY tf.ID
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

