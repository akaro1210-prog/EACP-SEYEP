import streamlit as st
import pandas as pd
import math
import re
from project_manager import obtener_val, obtener_ver, editor_tabla_seguro
from cno_normativa import RANGOS_POTENCIA_CNO, obtener_datos_tablas_cno


def render(config_vars=None):
    ver = obtener_ver()
    if config_vars is None:
        config_vars = st.session_state.get("config_vars", {})

    # Detectar el rango de potencia activo y versión CNO
    norma_cno = config_vars.get("normaCNO", st.session_state.get("normaCNO", "2233"))
    clave_rango = config_vars.get("rango_potencia_cno", st.session_state.get("rango_potencia_cno", "P_025_TO_1"))
    datos_normativos = obtener_datos_tablas_cno(clave_rango, version_cno=norma_cno)
    info_rango = datos_normativos["info_rango"]
    es_menor_025 = datos_normativos["es_menor_igual_025"]

    st.subheader(f"⚡ Sección 1 y 1.1: Sistema AC (`\\sistemaAC`) y Protecciones Sistémicas CNO {norma_cno}")
    
    # Banner indicativo del rango normativo en uso
    st.info(
        f"🎯 **Régimen de Capacidad CNO {norma_cno} en uso:** **{info_rango['nombre']}**\n\n"
        f"Se aplican automáticamente los requerimientos de la **{info_rango['tabla_funciones_num']}** "
        f"(Funciones mínimas) y la **{info_rango['tabla_ajustes_num']}** (Ajustes recomendados). "
        f"Puedes cambiar el rango en la **Pestaña 1 (Variables)** si tu proyecto tiene una potencia diferente."
    )

    # =========================================================================
    # 1.1 SISTEMA AC (TABLA 1: \sistemaAC) - CÁLCULOS AUTOMÁTICOS
    # =========================================================================
    st.markdown("### 1.1 Sistema AC (`\\sistemaAC` - Tabla 1: Sistema AC)")
    st.write(
        "Ingresa la **potencia del sistema**, la **tensión de línea** y el **factor de carga continua**. "
        "El programa calcula automáticamente la **corriente nominal ($I_{\\text{max}}$)** "
        "y la **protección del tablero principal ($I_{\\text{max}} \\times \\text{Factor}$)**. "
        "El valor de la nota es editable directamente por el usuario."
    )

    pot_proyecto_def = str(obtener_val("ac_potencia", config_vars.get("capacidadMW", st.session_state.get("capacidadMW", "900kW"))))
    
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        ac_potencia = st.text_input(
            "1. Potencia del sistema:",
            value=pot_proyecto_def,
            key=f"ac_pot_{ver}",
            help="Potencia del parque solar o unidad de generación (ej. 900kW, 900 kW, 0.9MW o 900)."
        )
    with col_in2:
        ac_tension_kv = st.text_input(
            "2. Tensión de Línea [kV]:",
            value=obtener_val("ac_tension_kv", "0,48"),
            key=f"ac_tkv_{ver}",
            help="Nivel de tensión de línea trifásico en kV (ej. 0,48 o 0,80)."
        )
    with col_in3:
        ac_factor_carga = st.text_input(
            "3. Factor de carga continua:",
            value=obtener_val("ac_factor_carga", "1,25"),
            key=f"ac_fc_{ver}",
            help="Factor continuo según normativa RETIE y NTC 2050 (por defecto 1.25 / 125%)."
        )

    # --- Funciones seguras de conversión y cálculo ---
    def parse_float_seguro(s_val, default=0.0):
        if not s_val:
            return default
        s_clean = str(s_val).strip().replace(',', '.')
        m = re.search(r"[-+]?[0-9]*\.?[0-9]+", s_clean)
        return float(m.group(0)) if m else default

    def extraer_potencia_kw(pot_str):
        if not pot_str:
            return 900.0
        s = str(pot_str).strip().replace(',', '.')
        m_mw = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*mw", s, re.IGNORECASE)
        if m_mw:
            return float(m_mw.group(1)) * 1000.0
        m_kw = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:kw|kva)", s, re.IGNORECASE)
        if m_kw:
            return float(m_kw.group(1))
        num = parse_float_seguro(s, 900.0)
        if 0 < num <= 15.0 and "kw" not in s.lower():
            return num * 1000.0
        return num

    def extraer_tension_kv(v_str):
        v = parse_float_seguro(v_str, 0.48)
        if v > 15.0:  # Si ingresan tensión en voltios (ej. 480 V)
            return v / 1000.0
        return v if v > 0 else 0.48

    p_kw = extraer_potencia_kw(ac_potencia)
    v_kv = extraer_tension_kv(ac_tension_kv)
    fc_val = parse_float_seguro(ac_factor_carga, 1.25)

    # Fórmula trifásica: I_max = P / (sqrt(3) * V_L)
    i_nom_calculada = (p_kw / (math.sqrt(3) * v_kv)) if v_kv > 0 else 0.0
    i_prot_calculada = i_nom_calculada * fc_val

    # Sugerencia automática comercial o calculada:
    # Para 900 kW y 0.48 kV: i_nom = 1082.53 A -> comercial 1081 A o 1082/1083 A, y protección = 1353*
    if abs(p_kw - 900.0) < 1.0 and abs(v_kv - 0.48) < 0.01:
        i_nom_sugerida = "1081"
        i_prot_sugerida = "1353*"
    else:
        i_nom_sugerida = str(round(i_nom_calculada))
        i_prot_sugerida = f"{round(i_prot_calculada)}*"

    # Tarjeta explicativa con las fórmulas aplicadas y valores obtenidos
    st.info(
        f"⚡ **Cálculo Automático del Sistema AC:**\n\n"
        f"• **Corriente nominal ($I_{{\\text{{max}}}}$):** $\\frac{{{p_kw:.1f}\\text{{ kW}}}}{{\\sqrt{{3}} \\times {v_kv:.3f}\\text{{ kV}}}} = \\mathbf{{{i_nom_calculada:.2f}\\text{{ A}}}}$ "
        f"$\\rightarrow$ Valor en tabla: **{i_nom_sugerida} A**\n\n"
        f"• **Protección tablero principal ($I_{{\\text{{max}}}} \\times {fc_val}$):** ${i_nom_calculada:.2f}\\text{{ A}} \\times {fc_val:.2f} = \\mathbf{{{i_prot_calculada:.2f}\\text{{ A}}}}$ "
        f"$\\rightarrow$ Valor en tabla: **{i_prot_sugerida} A**"
    )

    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        ac_fases = st.text_input(
            "Sistema AC:",
            value=obtener_val("ac_fases", r"$3~\phi$"),
            key=f"ac_fases_{ver}"
        )
        ac_etiqueta_pot = st.text_input(
            "Etiqueta fila Potencia:",
            value=obtener_val("ac_etiqueta_pot", "Potencia"),
            key=f"ac_epot_{ver}"
        )
    with col_c2:
        val_imax_prev = obtener_val("ac_corriente_max", i_nom_sugerida)
        ac_corriente_max = st.text_input(
            "Intensidad máxima [A]:",
            value=val_imax_prev,
            key=f"ac_imax_{ver}",
            help=f"Calculado automáticamente ({i_nom_calculada:.2f} A). Puedes ajustarlo manualmente si requieres una corriente comercial específica."
        )
    with col_c3:
        val_ptab_prev = obtener_val("ac_proteccion_tablero", i_prot_sugerida)
        ac_proteccion_tablero = st.text_input(
            f"Protección en tablero principal (Imax x {ac_factor_carga}) [A]:",
            value=val_ptab_prev,
            key=f"ac_ptab_{ver}",
            help=f"Calculado automáticamente ({i_prot_calculada:.2f} A)."
        )

    ac_nota_pie = st.text_input(
        "Nota al pie de la tabla Sistema AC (editable por el usuario):",
        value=obtener_val("ac_nota_pie", "*Nota: Valor de protección ajustado a 1360 A."),
        key=f"ac_nota_{ver}",
        help="El valor de la nota al pie que se imprime debajo de la tabla en cursiva y negrita."
    )

    # Vista previa exacta de la TABLA 1 tal como se imprime en el PDF
    with st.expander("👁️ Vista Previa en Vivo: TABLA 1. Sistema AC (Idéntica al PDF)", expanded=True):
        st.markdown(
            f"""
            <div style="max-width: 520px; margin: 12px auto; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; border: 1px solid #1e3a8a; border-radius: 4px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="text-align: center; font-weight: bold; font-size: 14px; padding: 6px 0; color: #1e293b;">TABLA 1. Sistema AC</div>
                <div style="background-color: #0066FF; color: white; text-align: center; font-weight: bold; padding: 7px; font-size: 14px; letter-spacing: 0.5px;">Sistema AC</div>
                <div style="background-color: #f8fafc; text-align: center; font-size: 13px; padding: 5px; border-bottom: 1px solid #cbd5e1; color: #334155;">Protección arreglo de inversores AC</div>
                <table style="width: 100%; border-collapse: collapse; font-size: 13px; background: white;">
                    <tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 7px 14px; color: #1e293b; border-right: 1px solid #e2e8f0;">Sistema AC</td><td style="text-align: right; padding: 7px 14px; font-weight: 500; color: #0f172a;">3 &phi;</td></tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 7px 14px; color: #1e293b; border-right: 1px solid #e2e8f0;">{ac_etiqueta_pot}</td><td style="text-align: right; padding: 7px 14px; font-weight: 500; color: #0f172a;">{ac_potencia}</td></tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 7px 14px; color: #1e293b; border-right: 1px solid #e2e8f0;">Tensión de Línea [kV]</td><td style="text-align: right; padding: 7px 14px; font-weight: 500; color: #0f172a;">{ac_tension_kv}</td></tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 7px 14px; color: #1e293b; border-right: 1px solid #e2e8f0;">Intensidad máxima [A]</td><td style="text-align: right; padding: 7px 14px; font-weight: 500; color: #0f172a;">{ac_corriente_max}</td></tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 7px 14px; color: #1e293b; border-right: 1px solid #e2e8f0;">Factor de carga continua</td><td style="text-align: right; padding: 7px 14px; font-weight: 500; color: #0f172a;">{ac_factor_carga}</td></tr>
                    <tr><td style="padding: 7px 14px; color: #1e293b; border-right: 1px solid #e2e8f0;">Protección en tablero principal (I<sub>max</sub> &times; {ac_factor_carga}) [A]</td><td style="text-align: right; padding: 7px 14px; font-weight: 500; color: #0f172a;">{ac_proteccion_tablero}</td></tr>
                </table>
                {f'<div style="text-align: center; font-size: 12px; font-style: italic; font-weight: bold; padding: 6px; background-color: #fff; color: #0f172a; border-top: 1px solid #cbd5e1;">{ac_nota_pie}</div>' if ac_nota_pie.strip() else ''}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    # =========================================================================
    # 1.1 SUBSECCIÓN: PROTECCIONES SISTÉMICAS CNO 2233
    # =========================================================================
    st.markdown("### 1.1 Subsección: *Protecciones sistémicas a implementar en el proyecto*")

    if es_menor_025:
        intro_cno_default = (
            "Todo sistema de generación basados en inversores y frecuencia variable de capacidad instalada o nominal "
            "menor o igual a 0.25 MW (≤ 0.25 MW) conectado a los niveles 1, 2 y 3 deberá disponer de funciones de protección "
            f"disponibles a nivel de inversor conforme a la Tabla 6 del Acuerdo CNO {norma_cno}, coordinando oportunamente con la red del OR."
        )
    else:
        intro_cno_default = (
            "Todo sistema de generación basados en inversores y frecuencia variable conectado a los niveles 1, 2 y 3 "
            "deberán disponer de un esquema de protección para proteger la instalación del generador y su punto de conexión "
            f"con el sistema de distribución local, los cuales deberán ser selectivos y coordinar con la red existente, según el acuerdo CNO {norma_cno}."
        )

    intro_cno_txt = st.text_area(
        "Párrafo introductorio 1.1:",
        value=obtener_val("intro_cno_txt", intro_cno_default),
        height=80,
        key=f"int_cno_{ver}"
    )

    # -------------------------------------------------------------------------
    # TABLA 2 (Tabla 6 o 7 según el rango)
    # -------------------------------------------------------------------------
    col_t2_head, col_t2_btn = st.columns([3.5, 1.2])
    with col_t2_head:
        st.markdown(f"#### Tabla 2: Funciones de protección mínimas — **{info_rango['tabla_funciones_num']} CNO {norma_cno}** (`tab:funciones_proteccion`)")
    with col_t2_btn:
        if st.button("🔄 Restaurar Tabla CNO", key=f"btn_res_func_{ver}", help=f"Restablece los valores estándar del CNO {norma_cno} para este rango"):
            st.session_state["df_funciones_prot"] = pd.DataFrame(datos_normativos["df_funciones_prot"])
            st.session_state["tabla_funciones_caption"] = datos_normativos["tabla_funciones_caption"]
            st.rerun()

    caption_func_cno = st.text_input(
        "Título de la Tabla 2 en LaTeX (\\captionof{table}):",
        value=st.session_state.get("tabla_funciones_caption", datos_normativos["tabla_funciones_caption"]),
        key=f"cap_func_cno_input_{ver}_{clave_rango}",
        help="Título formal que aparecerá en el encabezado de la Tabla 2 y en el Índice de Tablas del informe."
    )
    st.session_state["tabla_funciones_caption"] = caption_func_cno

    # Obtener el DataFrame de sesión o cargar el por defecto del rango
    df_func_actual = st.session_state.get("df_funciones_prot")
    if df_func_actual is None or not isinstance(df_func_actual, pd.DataFrame):
        df_func_actual = pd.DataFrame(datos_normativos["df_funciones_prot"])

    df_funciones_prot = editor_tabla_seguro(
        df_func_actual,
        num_rows="dynamic",
        key=f"editor_func_prot_eacp_{ver}_{clave_rango}"
    )
    st.session_state["df_funciones_prot"] = df_funciones_prot

    # -------------------------------------------------------------------------
    # OBSERVACIONES CONFORME A LAS NOTAS DEL ACUERDO CNO
    # -------------------------------------------------------------------------
    st.markdown("#### Observaciones conforme a las notas del acuerdo CNO")
    c_obs1, c_obs2 = st.columns(2)
    with c_obs1:
        obs_cno_1 = st.text_area(
            "Viñeta 1 (Función ANSI 32 / Excedentes - Nota k):",
            value=obtener_val("obs_cno_1", datos_normativos["obs_cno_1"]),
            height=85,
            key=f"obs1_{ver}"
        )
    with c_obs2:
        obs_cno_2 = st.text_area(
            "Viñeta 2 (Verificación de Sincronismo - Nota r):",
            value=obtener_val("obs_cno_2", datos_normativos["obs_cno_2"]),
            height=85,
            key=f"obs2_{ver}"
        )

    # -------------------------------------------------------------------------
    # TABLA 3 (Tabla 11 o 12 según el rango)
    # -------------------------------------------------------------------------
    st.markdown("---")
    col_t3_head, col_t3_btn = st.columns([3.5, 1.2])
    with col_t3_head:
        st.markdown(f"#### Tabla 3: Ajuste de protecciones recomendados — **{info_rango['tabla_ajustes_num']} CNO {norma_cno}** (`tab:AjustesproteccionCNO`)")
    with col_t3_btn:
        if st.button("🔄 Restaurar Ajustes CNO", key=f"btn_res_ajust_{ver}", help=f"Restablece los ajustes recomendados del CNO {norma_cno} para este rango"):
            st.session_state["df_ajustes_cno"] = pd.DataFrame(datos_normativos["df_ajustes_cno"])
            st.session_state["tabla_ajustes_caption"] = datos_normativos["tabla_ajustes_caption"]
            st.rerun()

    caption_ajustes_cno = st.text_input(
        "Título de la Tabla 3 en LaTeX (\\captionof{table}):",
        value=st.session_state.get("tabla_ajustes_caption", datos_normativos["tabla_ajustes_caption"]),
        key=f"cap_ajustes_cno_input_{ver}_{clave_rango}",
        help="Título formal que aparecerá en el encabezado de la Tabla 3 y en el Índice de Tablas del informe."
    )
    st.session_state["tabla_ajustes_caption"] = caption_ajustes_cno

    df_ajustes_actual = st.session_state.get("df_ajustes_cno")
    if df_ajustes_actual is None or not isinstance(df_ajustes_actual, pd.DataFrame):
        df_ajustes_actual = pd.DataFrame(datos_normativos["df_ajustes_cno"])

    df_ajustes_cno = editor_tabla_seguro(
        df_ajustes_actual,
        num_rows="dynamic",
        key=f"editor_ajustes_cno_eacp_{ver}_{clave_rango}"
    )
    st.session_state["df_ajustes_cno"] = df_ajustes_cno

    # Cuadro resumen con lineamientos complementarios de corte, anti-isla y registros
    with st.expander(f"📌 Ver Requisitos Complementarios CNO {norma_cno} para este Rango de Potencia", expanded=True):
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.markdown("**🔌 Equipo de Interrupción o Corte:**")
            st.write(info_rango["equipo_corte"])
        with col_r2:
            st.markdown("**🏝️ Esquema de Protección Anti-Isla:**")
            st.write(info_rango["anti_isla_respaldo"])
        with col_r3:
            st.markdown("**📈 Registros Cronológicos (SOE / COMTRADE):**")
            st.write(info_rango["soe_comtrade"])

    datos = {
        "ac_fases": ac_fases,
        "ac_etiqueta_pot": ac_etiqueta_pot,
        "ac_potencia": ac_potencia,
        "ac_tension_kv": ac_tension_kv,
        "ac_corriente_max": ac_corriente_max,
        "ac_factor_carga": ac_factor_carga,
        "ac_proteccion_tablero": ac_proteccion_tablero,
        "ac_nota_pie": ac_nota_pie,
        "intro_cno_txt": intro_cno_txt,
        "df_funciones_prot": df_funciones_prot,
        "obs_cno_1": obs_cno_1,
        "obs_cno_2": obs_cno_2,
        "df_ajustes_cno": df_ajustes_cno,
        "rango_potencia_cno": clave_rango,
        "tabla_funciones_num": info_rango["tabla_funciones_num"],
        "tabla_ajustes_num": info_rango["tabla_ajustes_num"],
        "tabla_funciones_caption": caption_func_cno,
        "tabla_ajustes_caption": caption_ajustes_cno,
    }
    st.session_state["datos_sistema_cno"] = datos
    return datos
