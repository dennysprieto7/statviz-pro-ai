# StatViz Pro AI — Dashboard independiente

Dashboard web exploratorio para bases clínicas en Excel/CSV.

## Publicar sin instalar Python localmente
1. Descarga y descomprime `StatViz_Dashboard.zip`.
2. Inicia sesión en GitHub y crea un repositorio nuevo llamado `statviz-pro-ai`.
3. Sube los archivos `app.py`, `requirements.txt` y `README.md` a la raíz del repositorio.
4. Entra en https://share.streamlit.io/ e inicia sesión con GitHub.
5. Selecciona **Create app**, el repositorio `statviz-pro-ai`, rama `main` y archivo principal `app.py`.
6. Pulsa **Deploy**. Streamlit generará una URL pública para tu dashboard.

## Funciones incluidas
- Carga de Excel/CSV y selección de hoja de Excel.
- Resumen de registros, variables, datos ausentes y duplicados.
- Exploración de variables numéricas y categóricas con gráficos interactivos.
- Auditoría de datos ausentes.
- Distribución descriptiva de categorías de escalas de riesgo.
- Filtros categóricos, tabla filtrada y exportación CSV.
- Diccionario de variables exportable.
- Datos demostrativos para probar la interfaz.

## Nota de privacidad
No cargues información identificable de pacientes en una instancia pública sin autorización, controles de acceso y revisión de los requisitos legales aplicables. La aplicación no está diseñada como sistema clínico validado ni como herramienta diagnóstica.
