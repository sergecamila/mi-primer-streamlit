if st.button("Calcular"):
    # Cálculos
    volumen_viga = largo * ancho * altura
    volumen_total = volumen_viga * cant

    cant_cem = volumen_total * 8
    cant_are = volumen_total * 0.6
    cant_grav = volumen_total * 0.8
    cant_agua = volumen_total * 175

    # Gráfico de materiales
    materiales = {
        "Cemento (bolsas)": cant_cem,
        "Arena (m³)": cant_are,
        "Grava (m³)": cant_grav,
        "Agua (litros)": cant_agua
    }
    st.subheader("Distribución de materiales")
    st.bar_chart(pd.DataFrame.from_dict(materiales, orient="index", columns=["Cantidad"]))

    # Bloque extra: comparación de precios
    st.subheader("Comparación de precios por proveedor")
    df_precios = pd.read_excel(archivo, sheet_name="Precios")
    st.dataframe(df_precios)
    st.bar_chart(df_precios.set_index("proveedor")[["precio"]])
