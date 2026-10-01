import streamlit as st
import pandas as pd
from project_manager import obtener_val, obtener_df, obtener_ver

def render():
    ver = obtener_ver()
    st.subheader("🛡️ Sección 1.5: Cálculos de Sobrecorriente (51/50 y 51N/50N)")
    st.write(
        "Configura las tablas de ajustes actuales de los equipos del OR (`\\ParametrosRECOSOR`), "
        "los cálculos de sobrecorriente del proyecto (`\\Ajustessobrecorrienteproyecto`) y, de forma opcional, "
        "las propuestas de cambio de ajustes para cualquier cantidad de equipos del OR."
    )

    # ================= 1. EQUIPOS ACTUALES DEL OR (\ParametrosRECOSOR) =================
    st.markdown("### 1. Ajustes Actuales de Equipos del OR (`\\ParametrosRECOSOR`)")

    col_or1, col_or2 = st.columns(2)
    with col_or1:
        incluir_reco_cabecera = st.checkbox(
            "✅ Incluir tabla Reconectador de Cabecera (`\\recocabecera`)",
            value=bool(obtener_val("incluir_reco_cabecera", True)),
            key=f"chk_inc_reco_cab_{ver}"
        )
    with col_or2:
        incluir_reco_cto = st.checkbox(
            "✅ Incluir tabla Reconectador del Circuito (`\\recoCTO`)",
            value=bool(obtener_val("incluir_reco_cto", False)),
            key=f"chk_inc_reco_cto_{ver}"
        )

    df_cabecera_default = pd.DataFrame([
        {"Parámetro": "ANSI 51", "Pick Up [Aprim]": "250", "DIAL [s]": "0,09", "Curva": "IEC - EI"},
        {"Parámetro": "ANSI 50", "Pick Up [Aprim]": "250", "DIAL [s]": "0,15", "Curva": "DT"},
        {"Parámetro": "ANSI 50-2", "Pick Up [Aprim]": "2400", "DIAL [s]": "0,0", "Curva": "DT"},
        {"Parámetro": "ANSI 51N", "Pick Up [Aprim]": "120", "DIAL [s]": "0,38", "Curva": "IEC - EI"},
        {"Parámetro": "ANSI 50N", "Pick Up [Aprim]": "2400", "DIAL [s]": "0,0", "Curva": "DT"},
    ])
    if incluir_reco_cabecera:
        st.markdown("#### Tabla `tab:ajustesrecoCabecera` (Reconectador `\\recocabecera`)")
        df_reco_cabecera = st.data_editor(
            obtener_df("df_reco_cabecera", df_cabecera_default),
            num_rows="dynamic",
            use_container_width=True,
            key=f"ed_reco_cab_eacp_{ver}"
        )
    else:
        df_reco_cabecera = obtener_df("df_reco_cabecera", df_cabecera_default)

    df_cto_default = pd.DataFrame([
        {"Parámetro": "ANSI 51", "Pick Up [Aprim]": "65", "DIAL [s]": "0,1", "Curva": "IEC - NI"},
        {"Parámetro": "ANSI 50", "Pick Up [Aprim]": "117", "DIAL [s]": "0,05", "Curva": "DT"},
        {"Parámetro": "ANSI 51N", "Pick Up [Aprim]": "22", "DIAL [s]": "0,1", "Curva": "IEC - NI"},
        {"Parámetro": "ANSI 50N", "Pick Up [Aprim]": "63,8", "DIAL [s]": "0,05", "Curva": "DT"},
    ])
    if incluir_reco_cto:
        st.markdown("#### Tabla `tab:ajustesrecoCTO` (Reconectador `\\recoCTO`)")
        df_reco_cto = st.data_editor(
            obtener_df("df_reco_cto", df_cto_default),
            num_rows="dynamic",
            use_container_width=True,
            key=f"ed_reco_cto_eacp_{ver}"
        )
    else:
        df_reco_cto = obtener_df("df_reco_cto", df_cto_default)

    # --- Botones para agregar más equipos actuales del OR ---
    if "num_equipos_or_extra" not in st.session_state:
        st.session_state["num_equipos_or_extra"] = 0

    col_btn_add1, col_btn_rem1, _ = st.columns([1, 1, 2])
    with col_btn_add1:
        if st.button("➕ Agregar otro equipo del OR", key="btn_add_eq_or"):
            st.session_state["num_equipos_or_extra"] += 1
            st.rerun()
    with col_btn_rem1:
        if st.session_state["num_equipos_or_extra"] > 0:
            if st.button("🗑️ Quitar último equipo adicional", key="btn_rem_eq_or"):
                st.session_state["num_equipos_or_extra"] -= 1
                st.rerun()

    lista_guardada_eq_or = obtener_val("equipos_or_extra", [])
    equipos_or_extra = []
    for idx in range(st.session_state["num_equipos_or_extra"]):
        num_eq = idx + 1
        st.markdown(f"#### Equipo Adicional del OR #{num_eq} (`tab:ajustesrecoExtra{num_eq}`)")
        item_prev = lista_guardada_eq_or[idx] if isinstance(lista_guardada_eq_or, list) and idx < len(lista_guardada_eq_or) else {}
        nom_def = item_prev.get("nombre", f"Reconectador Auxiliar {num_eq}") if isinstance(item_prev, dict) else f"Reconectador Auxiliar {num_eq}"
        nombre_eq = st.text_input(
            f"Nombre / Identificador del Equipo Adicional #{num_eq}:",
            value=nom_def,
            key=f"nom_eq_or_extra_{num_eq}_{ver}"
        )
        df_extra_default = pd.DataFrame([
            {"Parámetro": "ANSI 51", "Pick Up [Aprim]": "100", "DIAL [s]": "0,1", "Curva": "IEC - NI"},
            {"Parámetro": "ANSI 50", "Pick Up [Aprim]": "200", "DIAL [s]": "0,05", "Curva": "DT"},
            {"Parámetro": "ANSI 51N", "Pick Up [Aprim]": "40", "DIAL [s]": "0,1", "Curva": "IEC - NI"},
            {"Parámetro": "ANSI 50N", "Pick Up [Aprim]": "120", "DIAL [s]": "0,05", "Curva": "DT"},
        ])
        if isinstance(item_prev, dict) and "df" in item_prev:
            df_extra_init = pd.DataFrame(item_prev["df"]) if isinstance(item_prev["df"], list) else item_prev["df"]
        else:
            df_extra_init = df_extra_default

        df_eq_extra = st.data_editor(
            df_extra_init,
            num_rows="dynamic",
            use_container_width=True,
            key=f"ed_eq_or_extra_{num_eq}_{ver}"
        )
        equipos_or_extra.append({
            "nombre": nombre_eq,
            "label": f"tab:ajustesrecoExtra{num_eq}",
            "df": df_eq_extra
        })

    txt_recierre_or = st.text_input(
        "Nota de esquema de recierre del OR:",
        value=obtener_val("txt_recierre_or", "El equipo cuentan con esquema de recierre de 1+1 ambos recierres con un tiempo muerto de 15 segundos."),
        key=f"txt_rec_or_{ver}"
    )

    # ================= 2. CÁLCULOS Y AJUSTES DEL PROYECTO =================
    st.markdown("---")
    st.markdown("### 2. Fórmulas y Cálculos de Arranque 51P, 51N y 50/50N (`\\Ajustessobrecorrienteproyecto`)")

    c_f1, c_f2, c_f3, c_f4 = st.columns(4)
    with c_f1:
        calc_potencia = st.text_input("Potencia P en fórmula In:", value=obtener_val("calc_potencia", "900kW"), key=f"cpot_{ver}")
        calc_tension = st.text_input("Tensión VL en fórmula In:", value=obtener_val("calc_tension", "13.2kV"), key=f"cten_{ver}")
    with c_f2:
        calc_cosphi = st.text_input("Factor de potencia cos(phi):", value=obtener_val("calc_cosphi", "1"), key=f"cphi_{ver}")
        calc_in_val = st.text_input("Corriente nominal In [A]:", value=obtener_val("calc_in_val", "39.36"), key=f"cin_{ver}")
    with c_f3:
        calc_i51p_exact = st.text_input("I_51P calculada (In * 1.1):", value=obtener_val("calc_i51p_exact", "43.296"), key=f"c51pe_{ver}")
        calc_i51p_aprox = st.text_input("I_51P aproximada [A]:", value=obtener_val("calc_i51p_aprox", "44"), key=f"c51pa_{ver}")
    with c_f4:
        calc_i51n_exact = st.text_input("I_51N calculada (In * 0.4):", value=obtener_val("calc_i51n_exact", "15.744"), key=f"c51ne_{ver}")
        calc_i51n_aprox = st.text_input("I_51N aproximada [A]:", value=obtener_val("calc_i51n_aprox", "16"), key=f"c51na_{ver}")

    parrafo_50_default = (
        r"Ahora, si calculamos la protección ANSI 50 basados en el nivel de corto por un factor del 70\% tendríamos un valor de 2.17kA, "
        r"dado que el reconectador de cabecera cuenta con un esquema de salvar fusible con un disparo rápido a 250A, si programamos la función "
        r"ANSI 50 con el valor del corto estaríamos ocasionandod disparos rápidos en la protección del circuito, por llo que para esta función "
        r"se propone un valor de 200A, que supera el valor de la protección ANSI 51 y está por debajo de la función de disparo rápido del equipo "
        r"de cabecera, la protección ANSI 50N se calculó con el nivel de corto monofásico por un factor de 0.7, dando como resultado un ajuste de "
        r"1.1kA, teninedo en cuenta que para el elemento de tierra el OR no tiene un disparo rápido, este valor coordina adecuadamente con el elemento de protección del OR."
        "\n\\\\\n"
        r"La simulación para los cortos se realizó con el equivalente de red suministrado por el OR para el nivel de tensión \NT\ según los insumos. "
        r"El resumen de los ajustes de protección quedan depositados en las \cref{tab:ajustesrecoProyecto,tab:resumenajustestotales}."
    )
    parrafo_calculo_50 = st.text_area(
        "Párrafo explicativo de ANSI 50 y 50N:",
        value=obtener_val("parrafo_calculo_50", parrafo_50_default),
        height=150,
        key=f"p50_{ver}"
    )

    st.markdown("#### Tabla `tab:ajustesrecoProyecto` (Ajustes de protección para el Reconectador `\\nombreProyecto`)")
    df_proy_default = pd.DataFrame([
        {"Parámetro": "ANSI 51", "Pick Up [Aprim]": "44", "DIAL [s]": "0,05", "Curva": "IEC - EI"},
        {"Parámetro": "ANSI 50", "Pick Up [Aprim]": "200", "DIAL [s]": "0", "Curva": "DT"},
        {"Parámetro": "ANSI 51N", "Pick Up [Aprim]": "16", "DIAL [s]": "0,05", "Curva": "IEC - NI"},
        {"Parámetro": "ANSI 50N", "Pick Up [Aprim]": "1100", "DIAL [s]": "0", "Curva": "DT"},
    ])
    df_ajustes_reco_proy = st.data_editor(
        obtener_df("df_ajustes_reco_proy", df_proy_default),
        num_rows="dynamic",
        use_container_width=True,
        key=f"ed_reco_proy_eacp_{ver}"
    )

    st.markdown("#### Tabla `tab:resumenajustestotales` (Resumen ajuste de protecciones sistemáticas)")
    df_sist_default = pd.DataFrame([
        {"Función": "Etapa 1: Baja tensión (ANSI 27)", "Ajustes": "0.6 p.u", "Temporización": "2 s"},
        {"Función": "Etapa 2: Baja tensión (ANSI 27)", "Ajustes": "0.4 p.u", "Temporización": "1.5 s"},
        {"Función": "Etapa 1: Sobretensión (ANSI 59)", "Ajustes": "1.22 p.u", "Temporización": "2.5 s"},
        {"Función": "Etapa 2: Sobretensión (ANSI 59)", "Ajustes": "1.25 p.u", "Temporización": "0.5 s"},
        {"Función": "Sobretensión de neutro (ANSI 59N)", "Ajustes": "0.3 p.u", "Temporización": "2 s"},
        {"Función": "Bajafrecuencia (ANSI 81U)", "Ajustes": "57 Hz", "Temporización": "0.2 s"},
        {"Función": "Sobrefrecuencia (ANSI 81O)", "Ajustes": "63 Hz", "Temporización": "0.2 s"},
        {"Función": "Anti-isla", "Ajustes": "Lógica compuesta con señales de tensión y frecuencia", "Temporización": "500ms"},
        {"Función": "Verificación de sincronismo", "Ajustes": "Condición barra viva OR - Línea muerta PV umbral de tensión 0.8p.u", "Temporización": "NA"},
    ])
    df_resumen_totales = st.data_editor(
        obtener_df("df_resumen_totales", df_sist_default),
        num_rows="dynamic",
        use_container_width=True,
        key=f"ed_resumen_tot_eacp_{ver}"
    )

    # ================= 3. CONCLUSIÓN Y PROPUESTA OPCIONAL DE CAMBIO DE AJUSTES DEL OR =================
    st.markdown("---")
    st.markdown("### 3. Conclusión y Propuesta de Cambio de Ajustes para el OR (Opcional)")

    es_con_cambio = st.checkbox(
        "🔄 Incluir propuesta de cambio de ajustes para equipos del OR (Activa tablas comparativas Ajuste Actual vs Ajuste Propuesto)",
        value=bool(obtener_val("es_con_cambio", False)),
        key=f"chk_con_cambio_ajustes_or_{ver}"
    )

    incluir_tabla_cambio_cab = False
    incluir_tabla_cambio_cto = False
    df_cambio_cab = pd.DataFrame()
    df_cambio_cto = pd.DataFrame()
    cambios_or_extra = []
    nota_disparo_transferido = ""

    if not es_con_cambio:
        st.info("ℹ️ Modo actual: **Sin cambio de ajustes**. Solo se incluirá el párrafo indicando que las protecciones coordinan adecuadamente con los ajustes actuales del OR.")
        conclusion_sin_cambio_default = (
            r"Al realizar las simulaciones con los ajustes propuestos para el relé del GD \nombreProyecto\ y los ajustes de los equipos "
            r"aguas arriba, suministrados por el OR en \cref{tab:ajustesrecoCabecera} , se observa que no se presenta des coordinación "
            r"con los elementos del circuito, por lo que no se requiere cambio de ajustes."
        )
        conclusion_coord_txt = st.text_area(
            "Párrafo de conclusión (Sin cambio de ajustes):",
            value=obtener_val("conclusion_coord_txt", conclusion_sin_cambio_default),
            height=90,
            key=f"txt_conc_sin_cambio_{ver}"
        )
    else:
        st.success("✅ Modo activo: **Con propuesta de cambio de ajustes del OR**. Selecciona abajo qué equipos llevan tabla de cambio o agrega equipos adicionales.")
        conclusion_con_cambio_default = (
            r"Al realizar las simulaciones con los ajustes propuestos para el relé del GD \nombreProyecto\ y los ajustes los equipos aguas arriba, "
            r"suministrados por el OR en \cref{tab:ajustesrecoCabecera}, se observa que para fallas de 15ohms de impedancia en el nodo de conexión "
            r"se presenta un decalaje muy bajo entre los tiempos de operación de ambos elementos, lo que puede representar una des coordinación con el "
            r"elemento \recoCTO , por lo cual se proponen los ajustes mostrados a continuación para el elemento, el dial propuesto garantiza un decalaje "
            r"de al menos 200ms entre la actuación de los elementos ante diferentes tipos de falla como se demuestra en los anexos, en los que se "
            r"realizaron simulaciones con los ajustes actuales y los propuestos con el objetivo de que el OR pueda verificar la información, dado lo "
            r"anterior se puede concluir que estos ajustes garantizan la correcta coordinación y operación de los elementos del sistema.\\"
            "\n"
            r"También se deja la observación de que en las protecciones de tierra, si bien los ajustes propuestos coordinan correctamente con el "
            r"elemento aguas arriba, se observan descoordinaciones en los elementos del circuito, las cuales no son causadas por el ingreso del "
            r"proyecto en el sistema, se sugiere realizar la corrección de las protecciones para evitar posibles disparos inadecuados de los elementos, "
            r"no solo para fallas en el parque solar si no para fallas en general."
        )
        conclusion_coord_txt = st.text_area(
            "Párrafo de conclusión (Con propuesta de cambio de ajustes):",
            value=obtener_val("conclusion_coord_txt", conclusion_con_cambio_default),
            height=150,
            key=f"txt_conc_con_cambio_{ver}"
        )
        st.caption(
            "💡 Si escribes un asterisco `*` al inicio de cualquier valor en las columnas Propuestas (por ejemplo `*2000` o `*0,12`), "
            "esa celda se resaltará en **amarillo** en el PDF (`\\cellcolor{yellow}`)."
        )

        c_chk_c1, c_chk_c2 = st.columns(2)
        with c_chk_c1:
            incluir_tabla_cambio_cab = st.checkbox(
                "✅ Incluir tabla de cambio de ajustes para Reconectador de Cabecera (`\\recocabecera`)",
                value=bool(obtener_val("incluir_tabla_cambio_cab", True)),
                key=f"chk_cambio_cab_{ver}"
            )
        with c_chk_c2:
            incluir_tabla_cambio_cto = st.checkbox(
                "✅ Incluir tabla de cambio de ajustes para Reconectador del Circuito (`\\recoCTO`)",
                value=bool(obtener_val("incluir_tabla_cambio_cto", True)),
                key=f"chk_cambio_cto_{ver}"
            )

        df_cambio_cab_default = pd.DataFrame([
            {"Parámetro": "ANSI 51", "Pick Up Actual": "150", "Dial Actual": "0,1", "Curva Actual": "IEC - NI", "Pick Up Propuesto": "150", "Dial Propuesto": "0,1", "Curva Propuesta": "IEC - NI"},
            {"Parámetro": "ANSI 50", "Pick Up Actual": "450", "Dial Actual": "0", "Curva Actual": "DT", "Pick Up Propuesto": "*2000", "Dial Propuesto": "0", "Curva Propuesta": "DT"},
            {"Parámetro": "ANSI 51N", "Pick Up Actual": "30", "Dial Actual": "0,1", "Curva Actual": "IEC - NI", "Pick Up Propuesto": "30", "Dial Propuesto": "0,1", "Curva Propuesta": "IEC - NI"},
            {"Parámetro": "ANSI 50N", "Pick Up Actual": "360", "Dial Actual": "0", "Curva Actual": "DT", "Pick Up Propuesto": "*1850", "Dial Propuesto": "0", "Curva Propuesta": "DT"},
        ])
        if incluir_tabla_cambio_cab:
            st.markdown("#### Tabla `tab:cambioAjustescabecera` (Propuesta para Reconectador `\\recocabecera`)")
            df_cambio_cab = st.data_editor(
                obtener_df("df_cambio_cab", df_cambio_cab_default),
                num_rows="dynamic",
                use_container_width=True,
                key=f"ed_cambio_cab_{ver}"
            )

        df_cambio_cto_default = pd.DataFrame([
            {"Parámetro": "ANSI 51", "Pick Up Actual": "200", "Dial Actual": "0,1", "Curva Actual": "IEC - VI", "Pick Up Propuesto": "200", "Dial Propuesto": "*0,12", "Curva Propuesta": "IEC - VI"},
            {"Parámetro": "ANSI 50", "Pick Up Actual": "-", "Dial Actual": "-", "Curva Actual": "DT", "Pick Up Propuesto": "-", "Dial Propuesto": "-", "Curva Propuesta": "DT"},
            {"Parámetro": "ANSI 51N", "Pick Up Actual": "100", "Dial Actual": "0,19", "Curva Actual": "IEC - VI", "Pick Up Propuesto": "100", "Dial Propuesto": "0.19", "Curva Propuesta": "IEC - VI"},
            {"Parámetro": "ANSI 50N", "Pick Up Actual": "-", "Dial Actual": "-", "Curva Actual": "DT", "Pick Up Propuesto": "-", "Dial Propuesto": "-", "Curva Propuesta": "DT"},
        ])
        if incluir_tabla_cambio_cto:
            st.markdown("#### Tabla `tab:cambioAjustes` (Propuesta para Reconectador `\\recoCTO`)")
            df_cambio_cto = st.data_editor(
                obtener_df("df_cambio_cto", df_cambio_cto_default),
                num_rows="dynamic",
                use_container_width=True,
                key=f"ed_cambio_cto_{ver}"
            )

        # --- Botones para agregar más equipos en la propuesta de cambios del OR ---
        if "num_cambios_or_extra" not in st.session_state:
            st.session_state["num_cambios_or_extra"] = 0

        col_btn_add2, col_btn_rem2, _ = st.columns([1, 1, 2])
        with col_btn_add2:
            if st.button("➕ Agregar propuesta de cambio para otro equipo del OR", key="btn_add_cambio_or"):
                st.session_state["num_cambios_or_extra"] += 1
                st.rerun()
        with col_btn_rem2:
            if st.session_state["num_cambios_or_extra"] > 0:
                if st.button("🗑️ Quitar última propuesta adicional", key="btn_rem_cambio_or"):
                    st.session_state["num_cambios_or_extra"] -= 1
                    st.rerun()

        lista_guardada_cambios = obtener_val("cambios_or_extra", [])
        for idx_c in range(st.session_state["num_cambios_or_extra"]):
            num_c = idx_c + 1
            st.markdown(f"#### Propuesta de Cambio Equipo Adicional #{num_c} (`tab:cambioAjustesExtra{num_c}`)")
            item_c_prev = lista_guardada_cambios[idx_c] if isinstance(lista_guardada_cambios, list) and idx_c < len(lista_guardada_cambios) else {}
            nom_c_default = (
                item_c_prev.get("nombre")
                if isinstance(item_c_prev, dict) and item_c_prev.get("nombre")
                else (
                    equipos_or_extra[idx_c]["nombre"]
                    if idx_c < len(equipos_or_extra)
                    else f"Reconectador Auxiliar {num_c}"
                )
            )
            nombre_cambio_eq = st.text_input(
                f"Nombre del Equipo Adicional #{num_c} para propuesta de ajustes:",
                value=nom_c_default,
                key=f"nom_cambio_or_extra_{num_c}_{ver}"
            )
            df_cambio_extra_def = pd.DataFrame([
                {"Parámetro": "ANSI 51", "Pick Up Actual": "100", "Dial Actual": "0,1", "Curva Actual": "IEC - NI", "Pick Up Propuesto": "100", "Dial Propuesto": "*0,15", "Curva Propuesta": "IEC - NI"},
                {"Parámetro": "ANSI 50", "Pick Up Actual": "200", "Dial Actual": "0,05", "Curva Actual": "DT", "Pick Up Propuesto": "*350", "Dial Propuesto": "0,05", "Curva Propuesta": "DT"},
                {"Parámetro": "ANSI 51N", "Pick Up Actual": "40", "Dial Actual": "0,1", "Curva Actual": "IEC - NI", "Pick Up Propuesto": "40", "Dial Propuesto": "*0,15", "Curva Propuesta": "IEC - NI"},
                {"Parámetro": "ANSI 50N", "Pick Up Actual": "120", "Dial Actual": "0,05", "Curva Actual": "DT", "Pick Up Propuesto": "120", "Dial Propuesto": "0,05", "Curva Propuesta": "DT"},
            ])
            if isinstance(item_c_prev, dict) and "df" in item_c_prev:
                df_c_init = pd.DataFrame(item_c_prev["df"]) if isinstance(item_c_prev["df"], list) else item_c_prev["df"]
            else:
                df_c_init = df_cambio_extra_def

            df_cambio_extra = st.data_editor(
                df_c_init,
                num_rows="dynamic",
                use_container_width=True,
                key=f"ed_cambio_or_extra_{num_c}_{ver}"
            )
            cambios_or_extra.append({
                "nombre": nombre_cambio_eq,
                "label": f"tab:cambioAjustesExtra{num_c}",
                "df": df_cambio_extra
            })

        nota_disparo_transferido = st.text_area(
            "Nota adicional opcional (ej. Disparo transferido - dejar vacío si no aplica):",
            value=obtener_val("nota_disparo_transferido", ""),
            height=70,
            key=f"nota_dt_{ver}"
        )

    datos = {
        "incluir_reco_cabecera": incluir_reco_cabecera,
        "incluir_reco_cto": incluir_reco_cto,
        "df_reco_cabecera": df_reco_cabecera,
        "df_reco_cto": df_reco_cto,
        "equipos_or_extra": equipos_or_extra,
        "txt_recierre_or": txt_recierre_or,
        "calc_potencia": calc_potencia,
        "calc_tension": calc_tension,
        "calc_cosphi": calc_cosphi,
        "calc_in_val": calc_in_val,
        "calc_i51p_exact": calc_i51p_exact,
        "calc_i51p_aprox": calc_i51p_aprox,
        "calc_i51n_exact": calc_i51n_exact,
        "calc_i51n_aprox": calc_i51n_aprox,
        "parrafo_calculo_50": parrafo_calculo_50,
        "df_ajustes_reco_proy": df_ajustes_reco_proy,
        "df_resumen_totales": df_resumen_totales,
        "es_con_cambio": es_con_cambio,
        "conclusion_coord_txt": conclusion_coord_txt,
        "incluir_tabla_cambio_cab": incluir_tabla_cambio_cab,
        "incluir_tabla_cambio_cto": incluir_tabla_cambio_cto,
        "df_cambio_cab": df_cambio_cab,
        "df_cambio_cto": df_cambio_cto,
        "cambios_or_extra": cambios_or_extra,
        "nota_disparo_transferido": nota_disparo_transferido,
    }
    st.session_state["datos_sobrecorriente"] = datos
    return datos
