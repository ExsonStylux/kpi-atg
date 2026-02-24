import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración de página
st.set_page_config(page_title="Dashboard Facturación", layout="wide")

# Conexión a tu Google Sheet personal (Privada)
# La URL de tu hoja se configura en los 'Secrets' de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# --- BOTÓN DE PÁNICO ---
if st.sidebar.button("🧨 BORRAR RASTRO Y CERRAR"):
    st.cache_data.clear()
    st.sidebar.error("Datos borrados de la memoria temporal.")
    st.stop()

st.title("📊 Indicadores de Facturación ERP")

# 1. Leer históricos de Google Sheets
try:
    df_historico = conn.read()
    # Convertir fecha a formato correcto
    df_historico['f.factura'] = pd.to_datetime(df_historico['f.factura'])
except:
    df_historico = pd.DataFrame()
    st.warning("Conecta tu Google Sheet para ver históricos.")

# 2. Carga de nuevo archivo Excel
with st.sidebar.expander("⬆️ Cargar Datos del Mes"):
    archivo = st.file_uploader("Sube el Excel del ERP", type=["xlsx"])
    if archivo:
        nuevo_df = pd.read_excel(archivo)
        if st.button("Guardar y Actualizar Dashboard"):
            # Combinar y limpiar
            df_final = pd.concat([df_historico, nuevo_df], ignore_index=True)
            conn.update(data=df_final)
            st.success("¡Datos sincronizados con tu Google Sheet!")
            st.rerun()

# 3. Visualización de KPIs
if not df_historico.empty:
    # Lógica de Sucursal: letras en el folio
    df_historico['Sucursal'] = df_historico['folioint'].str.extract('([a-zA-Z]+)')
    
    # Métricas principales
    total_facturado = df_historico['total'].sum()
    total_viajes = df_historico['folioint'].nunique()
    
    col1, col2 = st.columns(2)
    col1.metric("Facturación Acumulada", f"${total_facturado:,.2f}")
    col2.metric("Total de Viajes", f"{total_viajes}")

    # Gráficos
    st.subheader("Facturación por Unidad")
    st.bar_chart(df_historico.groupby('unidad')['total'].sum())
    
    st.subheader("Comparativo por Sucursal (Serie)")
    st.line_chart(df_historico.groupby(['f.factura', 'Sucursal'])['total'].sum().unstack())
else:
    st.info("Por favor, sube un archivo Excel para generar el reporte.")
