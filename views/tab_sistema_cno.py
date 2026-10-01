import streamlit as st
import pandas as pd
from project_manager import obtener_val, obtener_df, obtener_ver

def render():
    ver = obtener_ver()
    st.subheader("⚡ Sección 1 y 1.1: Sistema AC (`\\sistemaAC`) y Protecciones Sistémicas CNO 2233")
    st.write("Configura los parámetros de la Tabla 1 (**Sistema AC**) y las tablas normativas de funciones de protección mínimas del Acuerdo CNO 2233.")

    st.markdown("### 1. Comando `\\sistemaAC` (Tabla 1: Sistema AC)")
    plantilla_ac = st.radio(
        "Plantilla rápida de Sistema AC:",
        [
            "Configuración 0,48 kV (Intensidad 1081 A / Protección 1353* A)",
            "Configuración 0,80 kV (Intensidad 775 A / Protección 967,6 A)"
        ],
        index=0,
        horizontal=True,
        key=f"rad_ac_{ver}"
    )

    es_048 = plantilla_ac.startswith("Configuración 0,48")

    c1, c2, c3 = st.columns(3)
    with c1:
        ac_fases = st.text_input("Sistema AC:", value=obtener_val("ac_fases", r"$3~\phi$"), key=f"ac_fases_{ver}")
        ac_etiqueta_pot = st.text_input("Etiqueta fila Potencia:", value=obtener_val("ac_etiqueta_pot", "Potencia" if es_048 else "Potencia [kVA]"), key=f"ac_epot_{ver}")
    with c2:
        ac_tension_kv = st.text_input("Tensión de Línea [kV]:", value=obtener_val("ac_tension_kv", "0,48" if es_048 else "0,8"), key=f"ac_tkv_{ver}")
        ac_corriente_max = st.text_input("Intensidad máxima [A]:", value=obtener_val("ac_corriente_max", "1081" if es_048 else "775"), key=f"ac_imax_{ver}")
    with c3:
        ac_factor_carga = st.text_input("Factor de carga continua:", value=obtener_val("ac_factor_carga", "1,25"), key=f"ac_fc_{ver}")
        ac_proteccion_tablero = st.text_input(
            "Protección en tablero principal (Imax x 1,25) [A]:",
            value=obtener_val("ac_proteccion_tablero", "1353*" if es_048 else "967,6"),
            key=f"ac_ptab_{ver}"
        )

    ac_nota_pie = st.text_input(
        "Nota al pie de la tabla Sistema AC (dejar vacío si no aplica):",
        value=obtener_val("ac_nota_pie", "*Nota: Valor de protección ajustado a 1360 A." if es_048 else ""),
        key=f"ac_nota_{ver}"
    )

    st.markdown("---")
    st.markdown("### 1.1 Subsección: *Protecciones sistémicas a implementar en el proyecto*")

    intro_cno_default = (
        "Todo el sistema de generación basados en inversores y frecuencia variable conectado a los niveles 1, 2 y 3 "
        "deberán disponer de un esquema de protección para proteger la instalación del generador y su punto de conexión "
        "con el sistema de distribución local, los cuales deberán ser selectivos y coordinar con la red existente, "
        "según el acuerdo CNO 2233 de 2026."
    )
    intro_cno_txt = st.text_area("Párrafo introductorio 1.1:", value=obtener_val("intro_cno_txt", intro_cno_default), height=80, key=f"int_cno_{ver}")

    st.markdown("#### Tabla 2: Funciones de protección mínimas (`tab:funciones_proteccion`)")
    df_func_default = pd.DataFrame([
        {"Función de protección": "Baja tensión (ANSI 27)", "PC": "X", "UG": "", "Notas": "m"},
        {"Función de protección": "Sobretensión adelante (ANSI 32)", "PC": "X", "UG": "", "Notas": "k"},
        {"Función de protección": "Sobrecorriente de fases y tierra", "PC": "X", "UG": "", "Notas": "l"},
        {"Función de protección": "Sobretensión (ANSI 59)", "PC": "X", "UG": "", "Notas": "m"},
        {"Función de protección": "Sobretensión de secuencia cero (ANSI 59N)", "PC": "X", "UG": "", "Notas": "n"},
        {"Función de protección": "Frecuencia (ANSI 81U/O)", "PC": "", "UG": "", "Notas": "p"},
        {"Función de protección": "Anti - isla", "PC": "X", "UG": "", "Notas": "q"},
        {"Función de protección": "Verificación de sincronismo", "PC": "X", "UG": "", "Notas": "r"},
    ])
    df_funciones_prot = st.data_editor(
        obtener_df("df_funciones_prot", df_func_default),
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_func_prot_eacp_{ver}"
    )

    st.markdown("#### Observaciones conforme a las notas del acuerdo CNO")
    obs_1_default = (
        "La protección ANSI 32 no aplica, dado que el proyecto es un generador distribuido, y esta función "
        "aplicará solo para autogeneradores con o sin entregar excedentes a la red."
    )
    obs_2_default = (
        "Para la verificación de sincronismo, conforme a la nota “r” del acuerdo se implementará en el PC la función 25 "
        "configurando solamente la condición de Barra viva OR - Línea muerta PV, con un umbral mínimo de tensión de 0.8 p.u "
        "que garantice que el sistema no permitirá energización cuando el sistema del OR se encuentre sin tensión"
    )
    obs_cno_1 = st.text_area("Viñeta 1 (ANSI 32):", value=obtener_val("obs_cno_1", obs_1_default), height=70, key=f"obs1_{ver}")
    obs_cno_2 = st.text_area("Viñeta 2 (Función 25 Sincronismo):", value=obtener_val("obs_cno_2", obs_2_default), height=80, key=f"obs2_{ver}")

    st.markdown("#### Tabla 3: Ajuste de protecciones sistemáticas recomendados CNO 2233 (`tab:AjustesproteccionCNO`)")
    df_cno_default = pd.DataFrame([
        {"Función": "Etapa 1: Baja tensión (ANSI 27)", "Ajustes": r"$\leq$ 0.6 p.u", "Temporización": "Ver nota", "Observaciones": "Actuación segregada por fase o trifásica"},
        {"Función": "Etapa 2: Baja tensión (ANSI 27)", "Ajustes": r"$\leq$ 0.4 p.u", "Temporización": "Ver nota", "Observaciones": "Actuación segregada por fase o trifásica"},
        {"Función": "Etapa 1: Sobretensión (ANSI 59)", "Ajustes": r"$\geq$ 1.22 p.u", "Temporización": r"$\geq$ 2.5 s", "Observaciones": "Actuación trifásica"},
        {"Función": "Etapa 2: Sobretensión (ANSI 59)", "Ajustes": r"$\geq$ 1.25 p.u", "Temporización": r"$\geq$ 0.5 s", "Observaciones": "Actuación trifásica"},
        {"Función": "Bajafrecuencia (ANSI 81U)", "Ajustes": "57 Hz", "Temporización": r"$\geq$ 0.2 s", "Observaciones": "Actuación tensiones F-T"},
        {"Función": "Sobrefrecuencia (ANSI 81O)", "Ajustes": "63 Hz", "Temporización": r"$\geq$ 0.2 s", "Observaciones": "Actuación tensiones F-T"},
    ])
    df_ajustes_cno = st.data_editor(
        obtener_df("df_ajustes_cno", df_cno_default),
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_ajustes_cno_eacp_{ver}"
    )

    datos = {
        "ac_fases": ac_fases,
        "ac_etiqueta_pot": ac_etiqueta_pot,
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
    }
    st.session_state["datos_sistema_cno"] = datos
    return datos
