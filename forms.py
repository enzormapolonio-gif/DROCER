import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Configuração da página
st.set_page_config(page_title="Dashboard de Entrevistas", layout="wide")

# Funções de limpeza
def clean_languages(text):
    if pd.isna(text): return ""
    text = str(text).lower().replace("acho q tudo", "").replace("tudo", "")
    parts = re.split(r',|\se\s|\.', text)
    cleaned_parts = []
    for p in parts:
        p = p.strip()
        if not p: continue
        if p == 'japones': p = 'japonês'
        if p == 'coreano': p = 'coreano'
        cleaned_parts.append(p.capitalize())
    return ", ".join(set(cleaned_parts))

def clean_genres(text):
    if pd.isna(text): return ""
    text = str(text).lower().replace("tudo", "")
    text = text.replace("metaaaaaaaall", "metal")
    text = text.replace("trap é músicas underground", "trap, underground")
    text = text.replace("punk e indie", "punk, indie")
    text = text.replace("jpop e bossa nova", "jpop, bossa nova")
    text = text.replace("/", ",")
    
    parts = re.split(r',|\se\s|\.', text)
    cleaned_parts = []
    for p in parts:
        p = p.strip().title()
        if not p: continue
        if p == 'Kpop': p = 'K-Pop'
        if p == 'Jpop': p = 'J-Pop'
        if p == 'Mpb': p = 'MPB'
        if p == 'Rnb': p = 'R&B'
        cleaned_parts.append(p)
    return ", ".join(set(cleaned_parts))

# Carregamento e cache dos dados
@st.cache_data
def load_data():
    # Substitua pelo caminho correto do seu arquivo se necessário
    file_path = "DROCER_ Vira o Disco (respostas) - Respostas ao formulário 1.csv"
    df = pd.read_csv(file_path)
    
    df['Idiomas (Limpos)'] = df['Qual é o idioma das músicas que você escuta?'].apply(clean_languages)
    df['Estilos (Limpos)'] = df['Quais são seus estilos favoritos?'].apply(clean_genres)
    
    # Filtrar apenas quem aceitou a entrevista
    df_interview = df[df['Gostaria de participar de uma entrevista com a nossa equipe?'].str.strip().str.lower() == 'sim'].copy()
    return df, df_interview

df_full, df_interview = load_data()

# Título e Métricas
st.title("🎧 Dashboard - Candidatos para Entrevista")
st.markdown("Visualização interativa focada nos candidatos que **aceitaram** participar da entrevista.")

col1, col2, col3 = st.columns(3)
col1.metric("Total de Respostas", len(df_full))
col2.metric("Aceitaram a Entrevista", len(df_interview))
col3.metric("Taxa de Conversão", f"{(len(df_interview)/len(df_full))*100:.1f}%")

st.divider()

# Layout em duas colunas para os gráficos
c1, c2 = st.columns(2)

with c1:
    # 1. Frequência de Audição
    st.subheader("Frequência que Ouvem Música")
    freq_counts = df_interview['Você costuma ouvir música com que frequência?'].value_counts().reset_index()
    freq_counts.columns = ['Frequência', 'Contagem']
    fig_freq = px.bar(freq_counts, x='Frequência', y='Contagem', color='Frequência', text_auto=True)
    st.plotly_chart(fig_freq, use_container_width=True)

    # 3. Idiomas Mais Escutados
    st.subheader("Top Idiomas Escutados")
    all_languages = []
    for langs in df_interview['Idiomas (Limpos)']:
        all_languages.extend([l.strip() for l in langs.split(',') if l.strip()])
    lang_counts = pd.Series(all_languages).value_counts().head(8).reset_index()
    lang_counts.columns = ['Idioma', 'Menções']
    fig_langs = px.bar(lang_counts, x='Menções', y='Idioma', orientation='h', color='Idioma', text_auto=True)
    fig_langs.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_langs, use_container_width=True)

with c2:
    # 2. Preferência Nacional x Internacional
    st.subheader("Música Nacional vs Internacional")
    pref_counts = df_interview['Você prefere músicas nacionais ou internacionais?'].value_counts().reset_index()
    pref_counts.columns = ['Preferência', 'Contagem']
    fig_pref = px.pie(pref_counts, values='Contagem', names='Preferência', hole=0.4)
    fig_pref.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pref, use_container_width=True)

    # 4. Estilos Mais Escutados
    st.subheader("Top 10 Estilos Musicais")
    all_genres = []
    for genres in df_interview['Estilos (Limpos)']:
        all_genres.extend([g.strip() for g in genres.split(',') if g.strip()])
    genre_counts = pd.Series(all_genres).value_counts().head(10).reset_index()
    genre_counts.columns = ['Estilo', 'Menções']
    fig_genres = px.bar(genre_counts, x='Menções', y='Estilo', orientation='h', color='Estilo', text_auto=True)
    fig_genres.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_genres, use_container_width=True)

st.divider()

# Tabela interativa com os contatos e perfis
# Tabela interativa com os contatos e perfis
st.subheader("📋 Lista de Candidatos para Entrevista")

# Definir as colunas exatas que vêm do CSV
colunas_tabela = [
    'Qual é o seu nome?', 
    'Qual é o seu curso?\nEX: 2CDD02\n\n*Se não for estudante no Senac, escreva: Não sou estudante do Senac.',
    'Endereço de e-mail', 
    'Estilos (Limpos)', 
    'Você produz música?'
]

# Criar a tabela e renomear os cabeçalhos para ficar mais bonito no Dashboard
df_exibicao = df_interview[colunas_tabela].copy()
df_exibicao.columns = ['Nome', 'Turma/Curso', 'E-mail', 'Estilos Musicais', 'Produz Música?']

# Exibir a tabela
st.dataframe(df_exibicao, use_container_width=True)
