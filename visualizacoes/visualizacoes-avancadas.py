# Importação das bibliotecas necessárias
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# Carregar os dados tratados
print("Carregando dados tratados...")
dados_completos = pd.read_csv('dados_tratados/dados_completos.csv')
enem_tratado = pd.read_csv('dados_tratados/enem_tratado.csv')
censo_escolar_tratado = pd.read_csv('dados_tratados/censo_escolar_tratado.csv')
municipios_tratado = pd.read_csv('dados_tratados/municipios_tratado.csv')

# 1. Visualização: Mapa de calor da média das notas por UF
print("\nCriando mapa de calor das notas por UF...")

# Agrupar dados por UF
if 'SG_UF_RESIDENCIA' in enem_tratado.columns and 'MEDIA_NOTAS' in enem_tratado.columns:
    media_por_uf = enem_tratado.groupby('SG_UF_RESIDENCIA')['MEDIA_NOTAS'].mean().reset_index()
    
    # Criar mapa
    fig = px.choropleth(
        media_por_uf,
        locations='SG_UF_RESIDENCIA',
        color='MEDIA_NOTAS',
        scope="south america",
        locationmode='ISO-3',
        color_continuous_scale=px.colors.sequential.Plasma,
        labels={'MEDIA_NOTAS': 'Média das Notas', 'SG_UF_RESIDENCIA': 'UF'},
        title='Média das Notas do ENEM por Unidade Federativa'
    )
    
    fig.update_geos(
        fitbounds="locations",
        visible=False
    )
    
    fig.write_html('visualizacoes/mapa_notas_por_uf.html')
    print("Mapa de calor por UF criado com sucesso!")
else:
    print("Colunas necessárias não encontradas para criar o mapa de calor por UF.")

# 2. Visualização: Gráfico de barras de desempenho por tipo de escola
print("\nCriando gráfico de desempenho por tipo de escola...")

if all(col in enem_tratado.columns for col in ['TP_ESCOLA', 'MEDIA_NOTAS']):
    # Mapear códigos para nomes de escolas (ajustar conforme os códigos reais)
    escola_map = {
        1: 'Pública',
        2: 'Privada',
        3: 'Exterior',
    }
    
    # Aplicar mapeamento se necessário
    if 'TP_ESCOLA' in enem_tratado.columns and enem_tratado['TP_ESCOLA'].dtype == 'int64':
        enem_tratado['TIPO_ESCOLA'] = enem_tratado['TP_ESCOLA'].map(escola_map)
    else:
        enem_tratado['TIPO_ESCOLA'] = enem_tratado['TP_ESCOLA']
    
    # Agrupar por tipo de escola
    media_por_escola = enem_tratado.groupby('TIPO_ESCOLA')['MEDIA_NOTAS'].mean().reset_index()
    
    # Criar gráfico de barras
    fig = px.bar(
        media_por_escola,
        x='TIPO_ESCOLA',
        y='MEDIA_NOTAS',
        color='TIPO_ESCOLA',
        labels={'MEDIA_NOTAS': 'Média das Notas', 'TIPO_ESCOLA': 'Tipo de Escola'},
        title='Média das Notas por Tipo de Escola',
        template='plotly_white'
    )
    
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    fig.write_html('visualizacoes/media_por_tipo_escola.html')
    print("Gráfico de desempenho por tipo de escola criado com sucesso!")
else:
    print("Colunas necessárias não encontradas para criar o gráfico por tipo de escola.")

# 3. Visualização: Gráfico de dispersão relacionando infraestrutura e desempenho
print("\nCriando gráfico de dispersão de infraestrutura vs desempenho...")

# Para esse gráfico, precisamos mesclar dados do censo escolar com os do ENEM
if 'dados_completos' in locals() or 'dados_completos' in globals():
    if all(col in dados_completos.columns for col in ['NIVEL_INFRAESTRUTURA', 'MEDIA_NOTAS']):
        fig = px.scatter(
            dados_completos,
            x='NIVEL_INFRAESTRUTURA',
            y='MEDIA_NOTAS',
            color='CATEGORIA_INFRAESTRUTURA' if 'CATEGORIA_INFRAESTRUTURA' in dados_completos.columns else None,
            size='NU_MATRICULAS' if 'NU_MATRICULAS' in dados_completos.columns else None,
            hover_name='NO_ENTIDADE' if 'NO_ENTIDADE' in dados_completos.columns else None,
            labels={
                'NIVEL_INFRAESTRUTURA': 'Nível de Infraestrutura',
                'MEDIA_NOTAS': 'Média das Notas',
                'CATEGORIA_INFRAESTRUTURA': 'Categoria de Infraestrutura'
            },
            title='Relação entre Infraestrutura Escolar e Desempenho no ENEM',
            template='plotly_white'
        )
        
        fig.write_html('visualizacoes/infraestrutura_vs_desempenho.html')
        print("Gráfico de dispersão criado com sucesso!")
    else:
        print("Colunas necessárias não encontradas para criar o gráfico de dispersão.")
else:
    print("DataFrame 'dados_completos' não encontrado.")

# 4. Visualização: Gráfico de linha da evolução de notas por faixa etária e área
print("\nCriando gráfico de linha da evolução de notas por área de conhecimento e faixa etária...")

if 'FAIXA_ETARIA' in enem_tratado.columns:
    # Preparar dados
    areas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT']
    areas_presentes = [area for area in areas if area in enem_tratado.columns]
    
    if areas_presentes:
        # Criar um DataFrame melhor para visualização
        notas_por_faixa = enem_tratado.groupby('FAIXA_ETARIA')[areas_presentes].mean().reset_index()
        
        # Criar gráfico
        fig = go.Figure()
        
        for area in areas_presentes:
            nome_area = {
                'NU_NOTA_CN': 'Ciências da Natureza',
                'NU_NOTA_CH': 'Ciências Humanas',
                'NU_NOTA_LC': 'Linguagens e Códigos',
                'NU_NOTA_MT': 'Matemática'
            }.get(area, area)
            
            fig.add_trace(go.Scatter(
                x=notas_por_faixa['FAIXA_ETARIA'],
                y=notas_por_faixa[area],
                mode='lines+markers',
                name=nome_area
            ))
        
        fig.update_layout(
            title='Média das Notas por Área de Conhecimento e Faixa Etária',
            xaxis_title='Faixa Etária',
            yaxis_title='Média das Notas',
            template='plotly_white',
            legend_title='Área de Conhecimento'
        )
        
        fig.write_html('visualizacoes/notas_por_area_e_idade.html')
        print("Gráfico de linha criado com sucesso!")
    else:
        print("Colunas de notas por área não encontradas.")
else:
    print("Coluna 'FAIXA_ETARIA' não encontrada.")

# 5. Visualização: Gráfico de pizza da distribuição de escolas por infraestrutura
print("\nCriando gráfico de pizza da distribuição de escolas por infraestrutura...")

if 'CATEGORIA_INFRAESTRUTURA' in censo_escolar_tratado.columns:
    # Contagem de escolas por categoria
    contagem_infra = censo_escolar_tratado['CATEGORIA_INFRAESTRUTURA'].value_counts().reset_index()
    contagem_infra.columns = ['Categoria', 'Quantidade']
    
    # Criar gráfico de pizza
    fig = px.pie(
        contagem_infra,
        values='Quantidade',
        names='Categoria',
        title='Distribuição das Escolas por Nível de Infraestrutura',
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.write_html('visualizacoes/distribuicao_infraestrutura_pizza.html')
    print("Gráfico de pizza criado com sucesso!")
else:
    print("Coluna 'CATEGORIA_INFRAESTRUTURA' não encontrada.")

# 6. Visualização: Gráfico de radar comparando desempenho por área de conhecimento e tipo de escola
print("\nCriando gráfico de radar comparando desempenho por área e tipo de escola...")

if all(col in enem_tratado.columns for col in ['TIPO_ESCOLA']):
    # Verificar quais colunas de notas estão disponíveis
    notas_cols = [col for col in ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO'] if col in enem_tratado.columns]
    
    if notas_cols:
        # Calcular médias por tipo de escola
        radar_data = enem_tratado.groupby('TIPO_ESCOLA')[notas_cols].mean().reset_index()
        
        # Criar figura
        fig = go.Figure()
        
        for i, row in radar_data.iterrows():
            tipo_escola = row['TIPO_ESCOLA']
            valores = row[notas_cols].tolist()
            rotulos = [
                'Ciências da Natureza',
                'Ciências Humanas',
                'Linguagens e Códigos',
                'Matemática',
                'Redação'
            ][:len(notas_cols)]  # Ajustar para o número de colunas presentes
            
            fig.add_trace(go.Scatterpolar(
                r=valores,
                theta=rotulos,
                fill='toself',
                name=tipo_escola
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1000]  # Ajustar conforme a escala das notas
                )
            ),
            title='Comparação de Desempenho por Área de Conhecimento e Tipo de Escola',
            template='plotly_white'
        )
        
        fig.write_html('visualizacoes/radar_notas_tipo_escola.html')
        print("Gráfico de radar criado com sucesso!")
    else:
        print("Colunas de notas não encontradas.")
else:
    print("Coluna 'TIPO_ESCOLA' não encontrada.")

# 7. Preparar dados para o Looker Studio
print("\nPreparando dados para o Looker Studio...")

# Criar um arquivo consolidado com os dados mais importantes para o dashboard
if 'dados_completos' in locals() or 'dados_completos' in globals():
    # Selecionar colunas relevantes para o dashboard
    colunas_dashboard = [
        # Dados do estudante
        'NU_INSCRICAO', 'TP_SEXO', 'NU_IDADE', 'FAIXA_ETARIA',
        # Localização
        'SG_UF_RESIDENCIA', 'NO_MUNICIPIO_RESIDENCIA',
        # Escola
        'TP_ESCOLA', 'TIPO_ESCOLA', 'CO_ESCOLA',
        # Notas
        'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO', 'MEDIA_NOTAS',
        # Infraestrutura
        'NIVEL_INFRAESTRUTURA', 'CATEGORIA_INFRAESTRUTURA',
        # Dados do município
        'IDH', 'CATEGORIA_IDH', 'PIB_PER_CAPITA'
    ]
    
    # Filtrar apenas colunas que existem
    colunas_existentes = [col for col in colunas_dashboard if col in dados_completos.columns]
    
    # Criar um DataFrame para o dashboard
    dashboard_df = dados_completos[colunas_existentes].copy()
    
    # Salvar para o Looker Studio
    dashboard_df.to_csv('dados_para_dashboard/dados_dashboard.csv', index=False)
    print("Dados para dashboard preparados com sucesso!")
else:
    print("DataFrame 'dados_completos' não encontrado para preparar dados do dashboard.")

print("\nTodas as visualizações foram criadas com sucesso!")
