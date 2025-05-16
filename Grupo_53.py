import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Configuración inicial
st.set_page_config(page_title="Análisis de Supermercado - Myanmar", layout="wide")
sns.set_style("whitegrid")
custom_palette = ["#114B5F", "#235789", "#4C243B", "#6C4B5E", "#6B8F71", "#51291E"]
sns.set_palette(custom_palette)

st.title("🛍️ Análisis de Datos de una Cadena de Supermercados en Myanmar")

# Estilo de las métricas
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}
[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}
[data-testid="stMetric"] {
    background-color: #B6BABE;
    text-align: center;
    padding: 15px 0;
}
[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}
            </style>
""", unsafe_allow_html=True)

# Cargar datos con caché para mejorar rendimiento
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data.csv")
    return df
# Cargar datos
df = cargar_datos()

df['Date'] = pd.to_datetime(df['Date'])

# Diccionario de traducción (inglés -> español)
traducciones = {
    "Health and beauty": "Salud y belleza",
    "Electronic accessories": "Accesorios electrónicos",
    "Home and lifestyle": "Hogar y estilo de vida",
    "Sports and travel": "Deportes y viajes",
    "Food and beverages": "Comida y bebidas",
    "Fashion accessories": "Accesorios de moda"
}

# Aplicar la traducción a la columna 'Product line'
df['Product line'] = df['Product line'].map(traducciones) 

# Diccionario de traducción (inglés -> español)
traducciones = {
    "Member": "Miembro",
    "Normal": "Normal"
}

# Aplicar la traducción a la columna 'Customer type'
df['Customer type'] = df['Customer type'].map(traducciones)

# Diccionario de traducción (inglés -> español)
traducciones = {
    "Ewallet": "Billetera electrónica",
    "Cash": "Efectivo",
    "Credit card": "Tarjeta de crédito"
}

# Aplicar la traducción a la columna 'Payment'
df['Payment'] = df['Payment'].map(traducciones)

st.sidebar.header("Filtros")
# Obtener fechas mínima y máxima del DataFrame
min_date = df['Date'].min()
max_date = df['Date'].max()
# Selector de rango de fechas
fecha_inicio, fecha_fin = st.sidebar.date_input(
    "Selecciona un rango de fechas:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
# Filtrar el DataFrame según el rango de fechas
df_filtered = df[(df['Date'] >= pd.to_datetime(fecha_inicio)) & (df['Date'] <= pd.to_datetime(fecha_fin))]

selected_branch = st.sidebar.multiselect("Selecciona sucursal:", df["Branch"].unique(), default=df["Branch"].unique())
selected_product_lines = st.sidebar.multiselect("Selecciona línea de producto:", df["Product line"].unique(), default=df["Product line"].unique())

df_filtered = df[(df["Branch"].isin(selected_branch)) & (df["Product line"].isin(selected_product_lines))]

# SECCIÓN DE MÉTRICAS (Primera fila)
# Generación de métricas
df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
df['gross income'] = pd.to_numeric(df['gross income'], errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')

# Calcular métricas
ventas_totales = df['Total'].sum()
total_unidades = df['Quantity'].sum()
ganancia_bruta = df['gross income'].sum()
calificacion_promedio = df['Rating'].mean()

# Mostrar métricas en columnas
st.subheader("Resumen de Métricas")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Ventas Totales", f"${ventas_totales:,.2f}")
col2.metric("Unidades Vendidas", f"{total_unidades:,}")
col3.metric("Ganancia Bruta", f"${ganancia_bruta:,.2f}")
col4.metric("Calificación Promedio", f"{calificacion_promedio:.2f} / 10")

# SECCIÓN DE GRÁFICOS 
col1, col2 = st.columns(2)
with col1:
    st.subheader("Evolución de las Ventas Totales")
    ventas_diarias = df_filtered.groupby("Date")["Total"].sum().reset_index()
    fig1, ax1 = plt.subplots()
    sns.lineplot(x="Date", y="Total", data=ventas_diarias, ax=ax1)
    ax1.set_title("Ventas Totales a lo Largo del Tiempo")
    ax1.set_ylabel('Total $')
    ax1.set_xlabel('Fecha')
    ax1.tick_params("x", rotation=90)
    fig1.patch.set_facecolor('none') # Fondo transparente de la figura
    ax1.set_facecolor('none')  # Fondo transparente del área del gráfico
    st.pyplot(fig1)
    st.write("*El gráfico muestra...*")

with col2:
    st.subheader("Ingresos por Línea de Producto")
    ingresos_linea = df_filtered.groupby("Product line")["Total"].sum().reset_index()
    # Crear gráfico de barras
    fig2 = px.bar(
        ingresos_linea,
        x="Product line",
        y="Total",
        color="Product line",
        title="Ingresos Totales por Línea de Producto",
        color_discrete_sequence=custom_palette
        )
    # Personalizar los ejes
    fig2.update_layout(
        xaxis_title="Línea de Producto",
        yaxis_title="Ingresos Totales"
    )
    # Mostrar en Streamlit
    st.plotly_chart(fig2)
    st.write("*El gráfico muestra...*")

col3, col4 = st.columns(2)
with col3:
    st.subheader("Distribución de Calificaciones de Clientes")
    fig3, ax3 = plt.subplots()
    sns.histplot(df_filtered["Rating"], bins=10, kde=True, ax=ax3)
    ax3.set_title("Distribución de Calificaciones")
    ax3.set_ylabel("Frecuencia")
    ax3.set_xlabel("Calificación de Clientes")
    fig3.patch.set_facecolor('none') # Fondo transparente de la figura
    ax3.set_facecolor('none')  # Fondo transparente del área del gráfico
    st.pyplot(fig3)
    st.write("*El gráfico muestra...*")

with col4:
    st.subheader("Comparación del Gasto por Tipo de Cliente")
    fig4, ax4 = plt.subplots()
    sns.boxplot(x="Customer type", y="Total", data=df_filtered, ax=ax4)
    ax4.set_ylabel("Gasto Total")
    ax4.set_xlabel("Tipo de Cliente")
    fig4.patch.set_facecolor('none') # Fondo transparente de la figura
    ax4.set_facecolor('none')  # Fondo transparente del área del gráfico
    st.pyplot(fig4)
    st.write("*El gráfico muestra...*")

col5, col6 = st.columns(2)
with col5:
    st.subheader("Relación entre Costo y Ganancia Bruta")
    fig5 = px.scatter(
        df_filtered,
        x="cogs",
        y="gross income",
        color="Product line",
        title="Costo vs Ganancia Bruta",
        color_discrete_sequence=custom_palette
        )
    # Personalizar los ejes
    fig5.update_layout(
        xaxis_title="Costo",
        yaxis_title="Ganancia Bruta"
    )
    # Mostrar en Streamlit
    st.plotly_chart(fig5)
    st.write("*El gráfico muestra...*")

with col6:
    st.subheader("Relación entre Costo, Ganancia Bruta y Precio Unitario")
    fig10 = plt.figure()
    ax10 = fig10.add_subplot(111, projection='3d')
    scatter = ax10.scatter(df_filtered["cogs"], df_filtered["gross income"], df_filtered["Unit price"],
                           c=df_filtered["Rating"], cmap="Blues")
    ax10.set_xlabel("Costo")
    ax10.set_ylabel("Ganancia Bruta")
    ax10.set_zlabel("Precio Unitario")
    ax10.set_title("Visualización 3D: Costo vs Ganancia vs Precio")
    fig10.patch.set_facecolor('none') # Fondo transparente de la figura
    ax10.set_facecolor('none')  # Fondo transparente del área del gráfico
    st.pyplot(fig10)
    st.write("*El gráfico muestra...*")

col7, col8 = st.columns(2)
with col7:
    st.subheader("Métodos de Pago Preferidos")
    fig6 = px.histogram(
        df_filtered, 
        x="Payment", 
        color="Payment", 
        title="Frecuencia de Métodos de Pago",
        color_discrete_sequence=custom_palette
        )
    # Personalizar los ejes
    fig6.update_layout(
        xaxis_title="Métodos de Pago",
        yaxis_title="Frecuencia"
    )
    # Mostrar en Streamlit
    st.plotly_chart(fig6)
    st.write("*El gráfico muestra...*")

with col8:
    st.subheader("Análisis de Correlación Numérica")
    variables = ["Unit price", "Quantity", "Tax 5%", "Total", "cogs", "gross income", "Rating"]
    corr = df_filtered[variables].corr()
    fig7, ax7 = plt.subplots()
    sns.heatmap(corr, annot=True, cmap="Blues", ax=ax7)
    fig7.patch.set_facecolor('none') # Fondo transparente de la figura
    ax7.set_facecolor('none')  # Fondo transparente del área del gráfico
    st.pyplot(fig7)
    st.write("*El gráfico muestra...*")

st.subheader("Visualización Multivariada")
st.write("Matriz de correlaciones")
fig9 = sns.pairplot(df_filtered[variables], corner=True)
st.pyplot(fig9)
st.write("*El gráfico muestra...*")

st.subheader("Ingreso Bruto por Sucursal y Línea de Producto")
sunburst_df = df_filtered.groupby(['Branch', 'Product line'])['gross income'].sum().reset_index()
fig8 = px.sunburst(sunburst_df, path=['Branch', 'Product line'], values='gross income', title="Ingreso Bruto por Sucursal y Línea de Producto", color_discrete_sequence=custom_palette)
# Ajustar tamaño de la figura
fig8.update_layout(width=800, height=800)  
# Mostrar en Streamlit
st.plotly_chart(fig8)
st.write("*El gráfico muestra...*")


# Pie de página
st.markdown("---")
st.caption("Análisis de Datos de una Cadena de Supermercados | Datos: data.csv")

