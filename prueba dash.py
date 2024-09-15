# app.py

import streamlit as st
import pandas as pd
from datetime import datetime

# Diccionario para almacenar proyectos y sus tareas
proyectos = {}

# Lista para almacenar el historial de cambios
historial_cambios = []

# Función para agregar un nuevo proyecto
def agregar_proyecto(nombre_proyecto):
    if nombre_proyecto in proyectos:
        st.warning(f"El proyecto '{nombre_proyecto}' ya existe.")
    else:
        proyectos[nombre_proyecto] = pd.DataFrame(columns=['ID de Tarea', 'Descripción', 'Prioridad', 'Responsable', 'Fecha de Compromiso', 'Estado', 'Historial'])
        st.success(f"Proyecto '{nombre_proyecto}' creado exitosamente.")

# Función para agregar una tarea a un proyecto
def agregar_tarea(nombre_proyecto, descripcion, prioridad, responsable, fecha_compromiso):
    if nombre_proyecto not in proyectos:
        st.warning(f"El proyecto '{nombre_proyecto}' no existe.")
        return
    df = proyectos[nombre_proyecto]
    nuevo_id = len(df) + 1
    nueva_tarea = pd.DataFrame({
        'ID de Tarea': [nuevo_id],
        'Descripción': [descripcion],
        'Prioridad': [prioridad],
        'Responsable': [responsable],
        'Fecha de Compromiso': [fecha_compromiso],
        'Estado': ['Pendiente'],
        'Historial': [f"Creada el {datetime.now()}"]
    })
    proyectos[nombre_proyecto] = pd.concat([df, nueva_tarea], ignore_index=True)
    st.success(f"Tarea '{descripcion}' agregada al proyecto '{nombre_proyecto}'.")

# Función para actualizar el estado de una tarea
def actualizar_estado(nombre_proyecto, id_tarea, nuevo_estado):
    if nombre_proyecto not in proyectos:
        st.warning(f"El proyecto '{nombre_proyecto}' no existe.")
        return
    df = proyectos[nombre_proyecto]
    if id_tarea not in df['ID de Tarea'].values:
        st.warning(f"La tarea con ID {id_tarea} no existe en el proyecto '{nombre_proyecto}'.")
        return
    indice = df.index[df['ID de Tarea'] == id_tarea][0]
    estado_anterior = df.at[indice, 'Estado']
    if estado_anterior != nuevo_estado:
        df.at[indice, 'Estado'] = nuevo_estado
        cambio = f"{datetime.now()} - Estado cambiado de '{estado_anterior}' a '{nuevo_estado}'"
        df.at[indice, 'Historial'] += "\n" + cambio
        historial_cambios.append({
            'Proyecto': nombre_proyecto,
            'ID de Tarea': id_tarea,
            'Cambio': cambio
        })
        st.success(f"Estado de la tarea ID {id_tarea} actualizado a '{nuevo_estado}'.")
    else:
        st.info(f"La tarea ya está en estado '{nuevo_estado}'.")

# Función para mostrar el dashboard
def mostrar_dashboard():
    st.header("Dashboard de Proyectos")
    resumen = []
    for proyecto, df in proyectos.items():
        tareas_pendientes = df[df['Estado'] != 'Completada']
        resumen.append({
            'Proyecto': proyecto,
            'Tareas Pendientes': len(tareas_pendientes)
        })
    df_resumen = pd.DataFrame(resumen)
    st.table(df_resumen)

    st.header("Tareas Vencidas o Próximas a Vencer")
    hoy = datetime.now()
    proximas_tareas = []
    for proyecto, df in proyectos.items():
        for _, row in df.iterrows():
            fecha_compromiso = pd.to_datetime(row['Fecha de Compromiso'])
            if fecha_compromiso <= hoy and row['Estado'] != 'Completada':
                proximas_tareas.append({
                    'Proyecto': proyecto,
                    'Descripción': row['Descripción'],
                    'Fecha de Compromiso': fecha_compromiso.date()
                })
    df_proximas = pd.DataFrame(proximas_tareas)
    st.table(df_proximas)

# Función para exportar los datos a Excel
def exportar_a_excel():
    with pd.ExcelWriter('Tablero_de_Tareas.xlsx') as writer:
        # Exportar cada proyecto
        for proyecto, df in proyectos.items():
            df.to_excel(writer, sheet_name=proyecto, index=False)
        # Crear y exportar el Dashboard
        resumen = []
        for proyecto, df in proyectos.items():
            tareas_pendientes = df[df['Estado'] != 'Completada']
            resumen.append({
                'Proyecto': proyecto,
                'Tareas Pendientes': len(tareas_pendientes)
            })
        df_resumen = pd.DataFrame(resumen)
        df_resumen.to_excel(writer, sheet_name='Dashboard', index=False)
    st.success("Datos exportados a 'Tablero_de_Tareas.xlsx'.")

# Interfaz de la aplicación
def main():
    st.title("Tablero de Seguimiento de Tareas")

    menu = ["Agregar Proyecto", "Agregar Tarea", "Actualizar Estado", "Ver Dashboard", "Exportar Datos"]
    choice = st.sidebar.selectbox("Menú", menu)

    if choice == "Agregar Proyecto":
        st.subheader("Agregar Nuevo Proyecto")
        nombre_proyecto = st.text_input("Nombre del Proyecto")
        if st.button("Agregar Proyecto"):
            if nombre_proyecto:
                agregar_proyecto(nombre_proyecto)
            else:
                st.warning("Por favor, ingresa un nombre para el proyecto.")

    elif choice == "Agregar Tarea":
        st.subheader("Agregar Nueva Tarea")
        if proyectos:
            nombre_proyecto = st.selectbox("Selecciona el Proyecto", list(proyectos.keys()))
            descripcion = st.text_input("Descripción de la Tarea")
            prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
            responsable = st.text_input("Responsable")
            fecha_compromiso = st.date_input("Fecha de Compromiso")
            if st.button("Agregar Tarea"):
                if descripcion and responsable:
                    agregar_tarea(nombre_proyecto, descripcion, prioridad, responsable, fecha_compromiso)
                else:
                    st.warning("Por favor, completa todos los campos.")
        else:
            st.warning("No hay proyectos disponibles. Agrega un proyecto primero.")

    elif choice == "Actualizar Estado":
        st.subheader("Actualizar Estado de una Tarea")
        if proyectos:
            nombre_proyecto = st.selectbox("Selecciona el Proyecto", list(proyectos.keys()))
            df = proyectos[nombre_proyecto]
            if not df.empty:
                id_tarea = st.number_input("ID de la Tarea", min_value=1, step=1)
                nuevo_estado = st.selectbox("Nuevo Estado", ["Pendiente", "En Proceso", "Completada"])
                if st.button("Actualizar Estado"):
                    actualizar_estado(nombre_proyecto, id_tarea, nuevo_estado)
            else:
                st.warning("El proyecto seleccionado no tiene tareas.")
        else:
            st.warning("No hay proyectos disponibles.")

    elif choice == "Ver Dashboard":
        mostrar_dashboard()

    elif choice == "Exportar Datos":
        if st.button("Exportar a Excel"):
            exportar_a_excel()
            with open('Tablero_de_Tareas.xlsx', 'rb') as f:
                st.download_button('Descargar Excel', f, file_name='Tablero_de_Tareas.xlsx')

    st.sidebar.markdown("---")
    st.sidebar.info("Aplicación desarrollada con Streamlit")

if __name__ == '__main__':
    main()
