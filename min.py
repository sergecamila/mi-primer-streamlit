import streamlit as st
import pandas as pd

st.title("Calculadora de Vigas con Precios")


st.write("👋 Bienvenidos a la calculadora de vigas. Sube un archivo Excel y presiona Calcular.")


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


if archivo is not None:
    st.success("✅ Archivo cargado correctamente")

    precios, proveedores_usados = cargar_mejores_precios(archivo)

    
    largo = st.number_input("Longitud de la viga (m)", min_value=0.1)
    ancho = st.number_input("Ancho de la viga (m)", min_value=0.1)
    altura = st.number_input("Altura de la viga (m)", min_value=0.1)
    cant = st.number_input("Cantidad de vigas", min_value=1, step=1)

    max_dias = st.number_input("Máximo de días permitidos", min_value=1.0)
    max_costo = st.number_input("Máximo de costo permitido ($)", min_value=1.0)

    if st.button("Calcular"):
        st.info("🔄 Botón presionado, calculando...")

        
        volumen_viga = largo * ancho * altura
        volumen_total = volumen_viga * cant

        cant_cem = volumen_total * 8
        cant_are = volumen_total * 0.6
        cant_grav = volumen_total * 0.8
        cant_agua = volumen_total * 175

        costo_m3concreto = (
            (8 * precios["cemento_bolsa"])
            + (0.6 * precios["arena_m3"])
            + (0.8 * precios["grava_m3"])
            + (175 * precios["agua_litro"])
        )
        costo_total = costo_m3concreto * volumen_total
        tiempo_estimado = volumen_total / 300

        
        st.subheader("Resultados principales")
        st.metric("Volumen total", f"{volumen_total:.2f} m³")
        st.metric("Costo total", f"${costo_total:,.2f}")
        st.metric("Tiempo estimado", f"{tiempo_estimado:.2f} días")

        
        if costo_total <= max_costo:
            st.success("✅ El costo está dentro del tope.")
        else:
            st.error("⚠️ El costo supera el máximo permitido.")

        if tiempo_estimado <= max_dias:
            st.success("⏱️ El tiempo está dentro del límite.")
        else:
            st.warning("⚠️ El tiempo supera el máximo permitido.")
else:
    st.warning

    
    materiales = {
        "Cemento (bolsas)": cant_cem,
        "Arena (m³)": cant_are,
        "Grava (m³)": cant_grav,
        "Agua (litros)": cant_agua
    }
    st.subheader("Distribución de materiales")
    st.bar_chart(pd.DataFrame.from_dict(materiales, orient="index", columns=["Cantidad"]))

    # 👉 Aquí colocas el bloque extra
    st.subheader("Comparación de precios por proveedor")
    df_precios = pd.read_excel(archivo, sheet_name="Precios")
    st.dataframe(df_precios)
    st.bar_chart(df_precios.set_index("proveedor")[["precio"]])