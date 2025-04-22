import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Aseguramos que el módulo modis esté en el path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modis.fetcher import Modis

def main():
    st.set_page_config(page_title="MODIS")
    
    st.title("MODIS Data Fetcher/Aerosol")
    # st.write("Herramienta para obtener datos de MODIS según coordenadas y fechas")
    
    col3, col4 = st.columns(2)
    
    with col3:
        product = st.selectbox(
            "Producto",
            ["MOD04_L2"],
            index=0,
            disabled=True
        )
    
    with col4:
        version = st.selectbox(
            "Versión",
            ["61"],
            index=0,
            disabled=True
        )
    # Crear columnas para formularios
    

    st.subheader("Coordenadas (Peru / Defecto)")
    col1, col2 = st.columns(2)
    lon1 = col1.number_input("Longitud 1", value=-81.35, format="%.2f")
    lat1 = col2.number_input("Latitud 1", value=-0.10, format="%.2f")
    lon2 = col1.number_input("Longitud 2", value=-68.67, format="%.2f")
    lat2 = col2.number_input("Latitud 2", value=-18.34, format="%.2f")


    st.subheader("Fechas")
    today = datetime.today().strftime('%m/%d/%Y')
    default_begin = "03/01/2025"
    default_end = "03/03/2025"
    
    col12, col22 = st.columns(2)
    begin_date = col12.date_input(
        "Fecha de inicio",
        datetime.strptime(default_begin, '%m/%d/%Y'),
        format="MM/DD/YYYY"
    ).strftime('%m/%d/%Y')
    
    end_date = col22.date_input(
        "Fecha de fin",
        datetime.strptime(default_end, '%m/%d/%Y'),
        format="MM/DD/YYYY"
    ).strftime('%m/%d/%Y')
    
    # Opciones adicionales
    # st.subheader("Opciones adicionales")
    
    # Botón para buscar datos
    fetch_button = st.button("Buscar datos MODIS", type="primary")
    
    if fetch_button:
        try:
            with st.spinner("Configurando parámetros de búsqueda..."):
                modis = Modis(lon1=lon1, lat1=lat1, lon2=lon2, lat2=lat2, product=product, version=version)
                modis.dates(begin_date, end_date)
            
            # Calcular cantidad de páginas/días para la barra de progreso
            days_diff = (datetime.strptime(end_date, '%m/%d/%Y') - 
                         datetime.strptime(begin_date, '%m/%d/%Y')).days + 1
            
            # Crear barra de progreso
            progress_bar = st.progress(0)
            progress_status = st.empty()
            
            # Realizar la búsqueda con actualización de progreso
            df_0 = modis.fetch()
            all_data = [df_0]
            
            for page in range(2, modis.pages + 2):
                # Actualizar progreso
                progress = (page - 1) / (modis.pages + 1)
                progress_bar.progress(progress)
                progress_status.text(f"Procesando página/fecha {page - 1} de {modis.pages + 1}...")
                
                # Obtener datos de la página actual
                df_n = modis.fetch(n_page=page)
                all_data.append(df_n)
            
            # Completar la barra de progreso
            progress_bar.progress(1.0)
            progress_status.text("¡Búsqueda completada!")
            
            # Combinar todos los datos
            data = pd.concat(all_data, ignore_index=True)
            
            # Mostrar resumen
            st.subheader("Resumen de resultados")
            st.write(f"Se encontraron {len(data)} registros.")
            
            # Crear botón de descarga antes de mostrar el dataframe
            st.download_button(
                label="Descargar datos como CSV",
                data=data.to_csv(index=False).encode('utf-8'),
                file_name=f"modis_data_{begin_date.replace('/', '')}_to_{end_date.replace('/', '')}.csv",
                mime="text/csv",

                key="download-csv"
            )
            
            # Mostrar dataframe
            st.subheader("Datos obtenidos")
            st.dataframe(data, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error al obtener datos: {str(e)}")
            st.error("Verifique las coordenadas y fechas ingresadas.")

if __name__ == "__main__":
    main()