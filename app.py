import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title='Dashboard de Salários na Área de Dados',
    page_icon='📊',
    layout='wide'
)
df = pd.read_csv('https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv')


# Sidebar
st.sidebar.header("🔍 Filtros")

#### Sidebar Filters ####

# Years
available_years = sorted(df['ano'].unique())
selected_years = st.sidebar.multiselect('Ano', available_years, default=available_years)


# Seniority
available_seniority = sorted(df['senioridade'].unique())
selected_seniority = st.sidebar.multiselect('Senioridade', available_seniority, default=available_seniority)


# Contract Type
available_contract_type = sorted(df['contrato'].unique())
selected_contract_type = st.sidebar.multiselect('Tipo de Contrato', available_contract_type, default=available_contract_type)


# Company Size
available_company_size = sorted(df['tamanho_empresa'].unique())
selected_company_size = st.sidebar.multiselect('Tamanho da Empresa', available_company_size, default=available_company_size)

#### Main Content ####

df_filtered = df[
    (df['ano'].isin(selected_years)) &
    (df['senioridade'].isin(selected_seniority)) &
    (df['contrato'].isin(selected_contract_type)) &
    (df['tamanho_empresa'].isin(selected_company_size))
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtered.empty:
    salario_mean = df_filtered['usd'].mean()
    salario_max = df_filtered['usd'].max()
    total_records = df_filtered.shape[0]
    most_common_position = df_filtered["cargo"].mode()[0]
else:
    salario_mean, salario_max, salario_max, total_records, most_common_position = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_mean:,.0f}")
col2.metric("Salário máximo", f"${salario_max:,.0f}")
col3.metric("Total de registros", f"{total_records:,}")
col4.metric("Cargo mais frequente", most_common_position)

st.markdown("---")


# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtered.empty:
        top_positions = df_filtered.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        position_chart = px.bar(
            top_positions,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        position_chart.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(position_chart, width='stretch')
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtered.empty:
        grafico_hist = px.histogram(
            df_filtered,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, width='stretch')
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtered.empty:
        remoto_contagem = df_filtered['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, width='stretch')
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtered.empty:
        df_ds = df_filtered[df_filtered['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        country_chart = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        country_chart.update_layout(title_x=0.1)
        st.plotly_chart(country_chart, width='stretch')
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.") 


# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtered)
