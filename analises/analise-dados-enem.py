# Importação das bibliotecas necessárias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configurações de visualização
plt.style.use('seaborn-v0_8-whitegrid')
sns.set(font_scale=1.2)
pd.set_option('display.max_columns', None)

# 1. Carregamento dos dados
print("Carregando dados...")

# NOTA: Os caminhos dos arquivos devem ser ajustados conforme sua estrutura de diretórios
# Devido ao tamanho dos arquivos, vamos trabalhar com amostras para demonstração

# Amostra dos dados do ENEM 2022 (substituir pelo caminho real)
enem_df = pd.read_csv('dados/enem_2022_amostra.csv', sep=';', encoding='latin1')

# Amostra do Censo Escolar 2022 (substituir pelo caminho real)
censo_escolar_df = pd.read_csv('dados/censo_escolar_2022_amostra.csv', sep=';', encoding='latin1')

# Indicadores Socioeconômicos por Município (substituir pelo caminho real)
municipios_df = pd.read_csv('dados/indicadores_municipios.csv', sep=';', encoding='latin1')

# 2. Exploração inicial dos dados
print("\n===== Informações sobre o DataFrame do ENEM =====")
print(f"Número de linhas: {enem_df.shape[0]}")
print(f"Número de colunas: {enem_df.shape[1]}")
print("\nPrimeiras linhas:")
print(enem_df.head())
print("\nInformações das colunas:")
print(enem_df.info())
print("\nEstatísticas descritivas:")
print(enem_df.describe())

print("\n\n===== Informações sobre o DataFrame do Censo Escolar =====")
print(f"Número de linhas: {censo_escolar_df.shape[0]}")
print(f"Número de colunas: {censo_escolar_df.shape[1]}")
print("\nPrimeiras linhas:")
print(censo_escolar_df.head())
print("\nInformações das colunas:")
print(censo_escolar_df.info())

print("\n\n===== Informações sobre o DataFrame de Indicadores Municipais =====")
print(f"Número de linhas: {municipios_df.shape[0]}")
print(f"Número de colunas: {municipios_df.shape[1]}")
print("\nPrimeiras linhas:")
print(municipios_df.head())
print("\nInformações das colunas:")
print(municipios_df.info())

# 3. Tratamento e preparação dos dados do ENEM
print("\n===== Tratamento dos dados do ENEM =====")

# Verificar valores nulos
print("\nValores nulos por coluna no ENEM:")
print(enem_df.isnull().sum())

# Vamos focar nas colunas mais importantes para a análise
# Selecionar apenas colunas relevantes
cols_enem = [
    'NU_INSCRICAO', 'TP_SEXO', 'NU_IDADE', 'CO_MUNICIPIO_RESIDENCIA', 
    'NO_MUNICIPIO_RESIDENCIA', 'SG_UF_RESIDENCIA', 'TP_ESCOLA', 
    'TP_ENSINO', 'IN_TREINEIRO', 'CO_ESCOLA', 'NU_NOTA_CN', 
    'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO'
]

# Filtrar apenas as colunas relevantes (ajustar conforme necessário)
if all(col in enem_df.columns for col in cols_enem):
    enem_df = enem_df[cols_enem]
else:
    print("Algumas colunas não foram encontradas. Usando as colunas disponíveis.")
    # Caso algumas colunas não existam, selecione manualmente as disponíveis

# Tratando valores nulos nas notas - substituir por zero os que não fizeram a prova
notas_cols = [col for col in enem_df.columns if 'NOTA' in col]
for col in notas_cols:
    if col in enem_df.columns:
        enem_df[col] = enem_df[col].fillna(0)

# Criar coluna de média das notas (primeira coluna derivada)
if all(col in enem_df.columns for col in ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT']):
    enem_df['MEDIA_NOTAS'] = enem_df[['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT']].mean(axis=1)

# Criar coluna de faixa etária (segunda coluna derivada)
if 'NU_IDADE' in enem_df.columns:
    bins = [0, 17, 20, 25, 30, 100]
    labels = ['Até 17 anos', '18 a 20 anos', '21 a 25 anos', '26 a 30 anos', 'Acima de 30 anos']
    enem_df['FAIXA_ETARIA'] = pd.cut(enem_df['NU_IDADE'], bins=bins, labels=labels)

# 4. Tratamento e preparação dos dados do Censo Escolar
print("\n===== Tratamento dos dados do Censo Escolar =====")

# Verificar valores nulos
print("\nValores nulos por coluna no Censo Escolar:")
print(censo_escolar_df.isnull().sum())

# Filtrar apenas escolas de Ensino Médio (ajustar conforme necessidade)
if 'IN_ENSINO_MEDIO' in censo_escolar_df.columns:
    censo_escolar_df = censo_escolar_df[censo_escolar_df['IN_ENSINO_MEDIO'] == 1]

# Criar coluna com indicador de infraestrutura (terceira coluna derivada)
# Esse é apenas um exemplo - ajuste conforme as colunas disponíveis
infra_cols = [
    'IN_BIBLIOTECA', 'IN_LABORATORIO_INFORMATICA', 'IN_LABORATORIO_CIENCIAS',
    'IN_QUADRA_ESPORTES', 'IN_SALA_ATENDIMENTO_ESPECIAL', 'IN_INTERNET'
]

# Verifica se as colunas existem no DataFrame
if all(col in censo_escolar_df.columns for col in infra_cols):
    censo_escolar_df['NIVEL_INFRAESTRUTURA'] = censo_escolar_df[infra_cols].sum(axis=1)
    
    # Categorizar o nível de infraestrutura
    censo_escolar_df['CATEGORIA_INFRAESTRUTURA'] = pd.cut(
        censo_escolar_df['NIVEL_INFRAESTRUTURA'], 
        bins=[0, 2, 4, 6], 
        labels=['Básica', 'Intermediária', 'Avançada']
    )

# 5. Tratamento e preparação dos dados de Indicadores Municipais
print("\n===== Tratamento dos dados de Indicadores Municipais =====")

# Verificar valores nulos
print("\nValores nulos por coluna nos Indicadores Municipais:")
print(municipios_df.isnull().sum())

# Vamos criar uma coluna de categorização do IDH (quarta coluna derivada)
if 'IDH' in municipios_df.columns:
    bins_idh = [0, 0.5, 0.6, 0.7, 0.8, 1.0]
    labels_idh = ['Muito baixo', 'Baixo', 'Médio', 'Alto', 'Muito alto']
    municipios_df['CATEGORIA_IDH'] = pd.cut(municipios_df['IDH'], bins=bins_idh, labels=labels_idh)

# 6. Mesclando os DataFrames para análises
print("\n===== Mesclando os DataFrames =====")

# Preparar para a mesclagem - garantir que as colunas de chave existam
# Mesclar ENEM com dados municipais
if 'CO_MUNICIPIO_RESIDENCIA' in enem_df.columns and 'CODIGO_IBGE' in municipios_df.columns:
    print("\nMesclando ENEM com Indicadores Municipais...")
    enem_municipios_df = pd.merge(
        enem_df, 
        municipios_df,
        left_on='CO_MUNICIPIO_RESIDENCIA',
        right_on='CODIGO_IBGE',
        how='left'
    )
    print(f"DataFrame resultante tem {enem_municipios_df.shape[0]} linhas e {enem_municipios_df.shape[1]} colunas")
else:
    print("Não foi possível mesclar ENEM com Indicadores Municipais devido à ausência de colunas de chave.")
    enem_municipios_df = enem_df.copy()

# Mesclar com dados do Censo Escolar
if 'CO_ESCOLA' in enem_df.columns and 'CO_ENTIDADE' in censo_escolar_df.columns:
    print("\nMesclando com Censo Escolar...")
    dados_completos_df = pd.merge(
        enem_municipios_df,
        censo_escolar_df,
        left_on='CO_ESCOLA',
        right_on='CO_ENTIDADE',
        how='left'
    )
    print(f"DataFrame final tem {dados_completos_df.shape[0]} linhas e {dados_completos_df.shape[1]} colunas")
else:
    print("Não foi possível mesclar com o Censo Escolar devido à ausência de colunas de chave.")
    dados_completos_df = enem_municipios_df.copy()

# 7. Salvando os DataFrames tratados
print("\n===== Salvando os DataFrames tratados =====")
enem_df.to_csv('dados_tratados/enem_tratado.csv', index=False)
censo_escolar_df.to_csv('dados_tratados/censo_escolar_tratado.csv', index=False)
municipios_df.to_csv('dados_tratados/municipios_tratado.csv', index=False)
if 'dados_completos_df' in locals():
    dados_completos_df.to_csv('dados_tratados/dados_completos.csv', index=False)

print("\nProcesso de tratamento de dados concluído!")

# 8. Análises Exploratórias

# Análise 1: Distribuição das notas
print("\n===== Análise 1: Distribuição das notas do ENEM =====")
plt.figure(figsize=(15, 10))

for i, col in enumerate(notas_cols, 1):
    if col in enem_df.columns:
        plt.subplot(2, 3, i)
        sns.histplot(enem_df[col].dropna(), kde=True)
        plt.title(f'Distribuição de {col}')
        plt.xlabel('Nota')
        plt.ylabel('Frequência')

if 'MEDIA_NOTAS' in enem_df.columns:
    plt.subplot(2, 3, len(notas_cols) + 1)
    sns.histplot(enem_df['MEDIA_NOTAS'].dropna(), kde=True)
    plt.title('Distribuição da Média das Notas')
    plt.xlabel('Média')
    plt.ylabel('Frequência')

plt.tight_layout()
plt.savefig('analises/distribuicao_notas.png')

# Análise 2: Comparação de médias por gênero
print("\n===== Análise 2: Comparação de notas por gênero =====")
if all(col in enem_df.columns for col in ['TP_SEXO', 'MEDIA_NOTAS']):
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='TP_SEXO', y='MEDIA_NOTAS', data=enem_df)
    plt.title('Distribuição da Média das Notas por Gênero')
    plt.xlabel('Gênero')
    plt.ylabel('Média das Notas')
    plt.savefig('analises/notas_por_genero.png')

# Análise 3: Correlação entre as notas
print("\n===== Análise 3: Correlação entre as notas =====")
if all(col in enem_df.columns for col in notas_cols):
    plt.figure(figsize=(10, 8))
    correlation_matrix = enem_df[notas_cols].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
    plt.title('Matriz de Correlação das Notas')
    plt.tight_layout()
    plt.savefig('analises/correlacao_notas.png')

# Análise 4: Média por faixa etária
print("\n===== Análise 4: Média por faixa etária =====")
if all(col in enem_df.columns for col in ['FAIXA_ETARIA', 'MEDIA_NOTAS']):
    plt.figure(figsize=(12, 6))
    sns.barplot(x='FAIXA_ETARIA', y='MEDIA_NOTAS', data=enem_df)
    plt.title('Média das Notas por Faixa Etária')
    plt.xlabel('Faixa Etária')
    plt.ylabel('Média das Notas')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('analises/media_por_faixa_etaria.png')

# Análise 5: Distribuição das escolas por nível de infraestrutura
print("\n===== Análise 5: Distribuição das escolas por nível de infraestrutura =====")
if 'CATEGORIA_INFRAESTRUTURA' in censo_escolar_df.columns:
    plt.figure(figsize=(10, 6))
    sns.countplot(x='CATEGORIA_INFRAESTRUTURA', data=censo_escolar_df)
    plt.title('Distribuição das Escolas por Nível de Infraestrutura')
    plt.xlabel('Nível de Infraestrutura')
    plt.ylabel('Quantidade de Escolas')
    plt.tight_layout()
    plt.savefig('analises/distribuicao_infraestrutura.png')

# Análise 6: Relação entre IDH do município e média das notas
print("\n===== Análise 6: Relação entre IDH e média das notas =====")
if all(col in dados_completos_df.columns for col in ['IDH', 'MEDIA_NOTAS']):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='IDH', y='MEDIA_NOTAS', data=dados_completos_df)
    plt.title('Relação entre IDH Municipal e Média das Notas')
    plt.xlabel('IDH')
    plt.ylabel('Média das Notas')
    plt.tight_layout()
    plt.savefig('analises/idh_vs_media.png')

print("\nTodas as análises foram concluídas e salvas!")
