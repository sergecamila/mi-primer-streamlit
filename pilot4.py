import streamlit as st
import pandas as pd
from pathlib import Path
from fpdf import FPDF
from datetime import datetime

cem_m3 = 8
are_m3 = 0.6
grav_m3 = 0.8
agua_m3 = 175
cant_concretoxdia = 300

st.title("Calculadora de Vigas con Precios")

archivo = st.file_uploader("Sube el archivo de precios (.xlsx)", type="xlsx")

def cargar_mejores_precios(ruta_excel):
    df = pd.read_excel(ruta_excel, sheet_name="Precios")
    df["material"] = df["material"].astype(str).str.strip()
    df["proveedor"] = df["proveedor"].astype(str).str.strip()
    df = df.sort_values(["material", "precio"])
    mejores = df.groupby("material", as_index=False).first()
    precios = dict(zip(mejores["material"], mejores["precio"]))
    proveedores = dict(zip(mejores["material"], mejores["proveedor"]))
    return precios, proveedores

def generar_recibo(costo_total, tiempo_estimado, materiales, proveedores_df):
    pdf = FPDF()
    pdf.add_page()

    pdf.image("logo.png", x=10, y=8, w=30)

    
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 102, 204)  
    pdf.cell(200, 10, "Recibo de Concreto", ln=True, align="C")
    pdf.ln(15)

    
    pdf.set_draw_color(0, 102, 204)  
    pdf.set_line_width(1)
    pdf.line(10, 28, 200, 28)  

    
    pdf.set_text_color(0, 0, 0)  
    pdf.set_font("Arial", size=12)
    fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    pdf.cell(200, 10, f"Fecha de emisión: {fecha_emision}", ln=True)
    pdf.ln(5)

    
    pdf.cell(200, 10, f"Costo total: ${costo_total:,.0f}", ln=True)
    pdf.cell(200, 10, f"Tiempo estimado: {int(tiempo_estimado)} días", ln=True)
    pdf.ln(10)

    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Materiales:", ln=True)
    pdf.set_font("Arial", size=12)
    for mat, cant in materiales.items():
        pdf.cell(200, 10, f"{mat}: {cant:.0f}", ln=True)
    pdf.ln(10)

    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Proveedores seleccionados:", ln=True)
    pdf.set_font("Arial", size=12)
    for i, row in proveedores_df.iterrows():
        pdf.cell(200, 10, f"{row['Material']}: {row['Proveedor']}", ln=True)

    ruta = "recibo.pdf"
    pdf.output(ruta)
    return ruta

if archivo is not None:
    precios, proveedores_usados = cargar_mejores_precios(archivo)

    largo = st.number_input("Longitud de la viga (m)", min_value=0.1)
    ancho = st.number_input("Ancho de la viga (m)", min_value=0.1)
    altura = st.number_input("Altura de la viga (m)", min_value=0.1)
    cant = st.number_input("Cantidad de vigas", min_value=1, step=1)

    max_dias = st.number_input("Máximo de días permitidos", min_value=1.0)
    max_costo = st.number_input("Máximo de costo permitido ($)", min_value=1.0)

    if st.button("Calcular"):
        volumen_viga = largo * ancho * altura
        volumen_total = volumen_viga * cant

        cant_cem = volumen_total * cem_m3
        cant_are = volumen_total * are_m3
        cant_grav = volumen_total * grav_m3
        cant_agua = volumen_total * agua_m3

        precio_bc = precios["cemento_bolsa"]
        precio_m3are = precios["arena_m3"]
        precio_m3grav = precios["grava_m3"]
        precio_lagua = precios["agua_litro"]

        costo_m3concreto = (
            (cem_m3 * precio_bc)
            + (are_m3 * precio_m3are)
            + (grav_m3 * precio_m3grav)
            + (agua_m3 * precio_lagua)
        )
        costo_total = costo_m3concreto * volumen_total
        tiempo_estimado = volumen_total / cant_concretoxdia

        st.subheader("Resultados principales")
        col1, col2 = st.columns(2)
        col1.metric("Volumen por viga", f"{volumen_viga:.2f} m³")
        col1.metric("Volumen total", f"{volumen_total:.2f} m³")
        col2.metric("Costo total del concreto", f"${costo_total:,.2f}")
        col2.metric("Tiempo estimado", f"{int(tiempo_estimado)} días")  

        if costo_total <= max_costo:
            st.success("✅ El costo total está dentro del tope.")
        else:
            st.error("⚠️ El costo total supera el máximo permitido. Ajusta la cantidad de vigas o los días.")

        if tiempo_estimado <= max_dias:
            st.success("⏱️ El tiempo estimado está dentro del límite.")
        else:
            st.warning("⚠️ El tiempo estimado supera el máximo permitido. Considera aumentar la capacidad diaria.")

        materiales = {
            "Cemento (bolsas)": cant_cem,
            "Arena (m³)": cant_are,
            "Grava (m³)": cant_grav,
            "Agua (litros)": cant_agua
        }
        st.subheader("Distribución de materiales")
        st.bar_chart(pd.DataFrame.from_dict(materiales, orient="index", columns=["Cantidad"]))

        st.subheader("Mejores proveedores seleccionados")
        proveedores_df = pd.DataFrame({
            "Material": list(proveedores_usados.keys()),
            "Proveedor": list(proveedores_usados.values())
        })
        st.dataframe(proveedores_df)

        
        ruta_pdf = generar_recibo(costo_total, tiempo_estimado, materiales, proveedores_df)
        with open(ruta_pdf, "rb") as f:
            st.download_button("Descargar recibo en PDF", f, file_name="recibo.pdf")
