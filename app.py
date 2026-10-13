import io
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='StatViz Pro AI | Dashboard', page_icon='📊', layout='wide')

NAVY = '#17365D'
TEAL = '#159D9A'

st.markdown(f"""
<style>
.block-container {{padding-top: 1.2rem; padding-bottom: 2rem;}}
[data-testid='stMetric'] {{border: 1px solid #dce3ea; padding: 14px; border-radius: 10px; background: rgba(245,248,251,.65);}}
h1, h2, h3 {{color: {NAVY};}}
</style>
""", unsafe_allow_html=True)

st.title('📊 StatViz Pro AI')
st.caption('Dashboard bioestadístico interactivo · datos clínicos y cardiovasculares')

@st.cache_data(show_spinner=False)
def load_file(file_bytes, filename, sheet_name=None):
    bio = io.BytesIO(file_bytes)
    if filename.lower().endswith(('.xlsx', '.xls')):
        xls = pd.ExcelFile(bio)
        chosen = sheet_name if sheet_name in xls.sheet_names else xls.sheet_names[0]
        return pd.read_excel(bio, sheet_name=chosen), xls.sheet_names
    return pd.read_csv(bio), []

with st.sidebar:
    st.header('1. Cargar datos')
    uploaded = st.file_uploader('Selecciona un archivo Excel o CSV', type=['xlsx','xls','csv'])
    st.caption('Los datos se procesan durante la sesión de esta aplicación.')

    if uploaded:
        raw = uploaded.getvalue()
        sheets = []
        if uploaded.name.lower().endswith(('.xlsx','.xls')):
            try:
                sheets = pd.ExcelFile(io.BytesIO(raw)).sheet_names
            except Exception as e:
                st.error(f'No se pudieron leer las hojas: {e}')
        sheet = st.selectbox('Hoja de Excel', sheets) if sheets else None
        try:
            df, _ = load_file(raw, uploaded.name, sheet)
        except Exception as e:
            st.error(f'Error al leer el archivo: {e}')
            st.stop()
    else:
        st.info('Carga tu base para comenzar. Puedes probar con datos de demostración.')
        demo = st.button('Abrir datos de demostración', use_container_width=True)
        if demo:
            st.session_state['demo'] = True
        if not st.session_state.get('demo', False):
            st.stop()
        df = pd.DataFrame({
            'EDAD':[52,61,67,73,58,80,45,69,63,56],
            'SEXO':['F','M','F','F','M','F','M','F','M','F'],
            'TAS':[118,142,135,151,126,147,119,139,132,124],
            'TAD':[72,86,78,91,75,82,69,84,77,74],
            'PREVENT_categoria':['Bajo','Intermedio','Alto','Alto','Bajo','Alto','Bajo','Intermedio','Intermedio','Bajo'],
            'SCORE2_LAC_categoria':['Bajo','Intermedio','Alto','Alto','Bajo','Alto','Bajo','Alto','Intermedio','Bajo']
        })

if df.empty:
    st.warning('El archivo no contiene filas. Revisa la hoja seleccionada.')
    st.stop()

# Normalize display only; original column names are preserved.
df = df.copy()
num_cols = df.select_dtypes(include='number').columns.tolist()
cat_cols = [c for c in df.columns if c not in num_cols]
missing_total = int(df.isna().sum().sum())
missing_pct = 100 * missing_total / max(1, df.shape[0] * df.shape[1])

st.subheader('Resumen de la base')
a,b,c,d,e = st.columns(5)
a.metric('Pacientes / registros', f'{len(df):,}')
b.metric('Variables', f'{df.shape[1]:,}')
c.metric('Celdas ausentes', f'{missing_total:,}')
d.metric('Ausencia global', f'{missing_pct:.2f}%')
e.metric('Filas duplicadas', f'{int(df.duplicated().sum()):,}')

with st.expander('Vista previa de los datos', expanded=False):
    st.dataframe(df.head(100), use_container_width=True, height=320)
    st.download_button('Descargar base cargada como CSV', df.to_csv(index=False).encode('utf-8-sig'), 'base_datos.csv', 'text/csv')

st.divider()
tab1, tab2, tab3, tab4, tab5 = st.tabs(['📈 Exploración','🧩 Datos ausentes','⚖️ Escalas de riesgo','🔎 Filtros y tabla','📋 Diccionario'])

with tab1:
    st.subheader('Exploración interactiva')
    if num_cols:
        col1,col2 = st.columns([1,2])
        with col1:
            variable = st.selectbox('Variable numérica', num_cols)
            tipo = st.radio('Visualización', ['Histograma','Caja y bigotes','Densidad'], horizontal=False)
            series = df[variable].dropna()
            if len(series):
                st.write('**Estadísticos descriptivos**')
                stats = series.describe().rename({'count':'n','mean':'Media','std':'Desv. estándar','min':'Mínimo','25%':'P25','50%':'Mediana','75%':'P75','max':'Máximo'})
                st.dataframe(stats.to_frame('Valor').round(3), use_container_width=True)
        with col2:
            plotdata = df[[variable]].dropna()
            if tipo == 'Histograma':
                fig = px.histogram(plotdata, x=variable, marginal='box', title=f'Distribución de {variable}', template='plotly_white')
            elif tipo == 'Caja y bigotes':
                fig = px.box(plotdata, y=variable, points='outliers', title=f'Distribución de {variable}', template='plotly_white')
            else:
                fig = px.violin(plotdata, y=variable, box=True, points='outliers', title=f'Densidad de {variable}', template='plotly_white')
            fig.update_traces(marker_color=TEAL, marker_line_color=NAVY)
            fig.update_layout(title_x=.02, height=440)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('No se detectaron variables numéricas.')
    if cat_cols:
        st.subheader('Distribución de variables categóricas')
        catvar = st.selectbox('Variable categórica', cat_cols, key='cat_distribution')
        counts = df[catvar].fillna('(Ausente)').astype(str).value_counts().rename_axis('Categoría').reset_index(name='n')
        counts['%'] = 100 * counts['n'] / len(df)
        fig = px.bar(counts.sort_values('n'), x='n', y='Categoría', orientation='h', text='n', title=f'Frecuencias: {catvar}', template='plotly_white')
        fig.update_traces(marker_color=TEAL, textposition='outside')
        fig.update_layout(height=max(350, 32*len(counts)), title_x=.02)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(counts.sort_values('n', ascending=False), use_container_width=True, hide_index=True)

with tab2:
    st.subheader('Auditoría de datos ausentes')
    miss = pd.DataFrame({'Variable':df.columns, 'Ausentes':df.isna().sum().values})
    miss['% ausente'] = 100*miss['Ausentes']/len(df)
    miss = miss.sort_values('Ausentes', ascending=False)
    fig = px.bar(miss[miss['Ausentes']>0].sort_values('% ausente'), x='% ausente', y='Variable', orientation='h', text=miss[miss['Ausentes']>0].sort_values('% ausente')['% ausente'].map(lambda x:f'{x:.1f}%'), title='Porcentaje de datos ausentes por variable', template='plotly_white')
    fig.update_traces(marker_color=TEAL, textposition='outside')
    fig.update_layout(height=max(350, 26*max(1,(miss['Ausentes']>0).sum())), title_x=.02)
    if (miss['Ausentes']>0).any(): st.plotly_chart(fig, use_container_width=True)
    else: st.success('No hay datos ausentes en la base.')
    st.dataframe(miss, use_container_width=True, hide_index=True)
    st.download_button('Descargar auditoría de ausentes', miss.to_csv(index=False).encode('utf-8-sig'), 'auditoria_ausentes.csv', 'text/csv')

with tab3:
    st.subheader('Comparación descriptiva de escalas de riesgo')
    scale_candidates = [c for c in df.columns if any(k in str(c).lower() for k in ['prevent','score2','ascvd','heart','ops','riesgo','categoria'])]
    if scale_candidates:
        selected = st.multiselect('Selecciona las variables categóricas de escala', scale_candidates, default=scale_candidates[:min(4,len(scale_candidates))])
        if selected:
            rows=[]
            for col in selected:
                vals = df[col].fillna('No disponible').astype(str).value_counts(dropna=False)
                for category, n in vals.items(): rows.append({'Escala':col, 'Categoría':category, 'n':int(n), '% de la cohorte':100*n/len(df)})
            dist = pd.DataFrame(rows)
            fig = px.bar(dist, x='Escala', y='n', color='Categoría', barmode='stack', text_auto=True, title='Distribución por categorías disponibles', template='plotly_white')
            fig.update_layout(title_x=.02)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(dist, use_container_width=True, hide_index=True)
            st.download_button('Descargar tabla de escalas', dist.to_csv(index=False).encode('utf-8-sig'), 'distribucion_escalas.csv', 'text/csv')
            st.caption('Las categorías se muestran tal como aparecen en la base. No se asume que las escalas sean clínicamente equivalentes ni se calcula reclasificación validada automáticamente.')
    else:
        st.info('No se identificaron automáticamente columnas de escalas. Revisa los nombres de las variables en la pestaña Diccionario.')

with tab4:
    st.subheader('Filtrar y revisar registros')
    filters = st.multiselect('Columnas categóricas para filtrar', cat_cols, help='Elige una o más variables; luego selecciona las categorías permitidas.')
    filtered = df.copy()
    for col in filters:
        options = sorted(filtered[col].dropna().astype(str).unique().tolist())
        chosen = st.multiselect(f'Valores de {col}', options, default=options, key=f'filter_{col}')
        filtered = filtered[filtered[col].astype(str).isin(chosen)]
    st.metric('Registros tras filtros', f'{len(filtered):,}', delta=f'{len(filtered)-len(df):,} respecto a la base completa')
    st.dataframe(filtered, use_container_width=True, height=440)
    st.download_button('Exportar registros filtrados (CSV)', filtered.to_csv(index=False).encode('utf-8-sig'), 'registros_filtrados.csv', 'text/csv')

with tab5:
    st.subheader('Diccionario de variables')
    dictionary = pd.DataFrame({'Variable':df.columns, 'Tipo detectado':['Numérica' if c in num_cols else 'Categórica/texto' for c in df.columns], 'No ausentes':df.notna().sum().values, 'Ausentes':df.isna().sum().values, 'Valores únicos':[df[c].nunique(dropna=True) for c in df.columns]})
    st.dataframe(dictionary, use_container_width=True, hide_index=True)
    st.download_button('Descargar diccionario', dictionary.to_csv(index=False).encode('utf-8-sig'), 'diccionario_variables.csv', 'text/csv')

st.divider()
st.caption('StatViz Pro AI · Herramienta exploratoria. Verifica definiciones, unidades, criterios clínicos y supuestos estadísticos antes de usar resultados en publicaciones o decisiones clínicas.')
