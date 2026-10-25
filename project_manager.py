import json
import os
import base64
import pandas as pd
import streamlit as st

IMAGENES_PROYECTO = [
    "Logo_Cliente.png",
    "Proteccion27-59.png",
    "ICC 1F GCP.png",
    "ICC 1F GSP.png",
    "ICC 3F GCP.png",
    "ICC 3F GSP.png",
    "Protecciones falla lado alta proyecto.png",
    "Protecciones falla 1F franca lado alta proyecto.png",
    "Protecciones falla 1F 5ohms lado alta proyecto.png",
    "Protecciones falla 1F 15ohms lado alta proyecto.png",
    "Protecciones falla 1F 30ohms lado alta proyecto.png",
    "Protecciones falla 3F franca lado alta proyecto.png",
    "Protecciones falla 3F 5ohms lado alta proyecto.png",
    "Protecciones falla 3F 15ohms lado alta proyecto.png",
    "Protecciones falla 3F 30ohms lado alta proyecto.png",
    "Protecciones falla lado baja proyecto.png",
    "Protecciones falla 1F franca lado baja proyecto.png",
    "Protecciones falla 3F franca lado baja proyecto.png",
    "Protecciones falla nodo conexión proyecto.png",
    "Protecciones falla 1F franca nodo conexión proyecto.png",
    "Protecciones falla 1F 5ohms nodo conexión proyecto.png",
    "Protecciones falla 1F 15ohms nodo conexión proyecto.png",
    "Protecciones falla 1F 30ohms nodo conexión proyecto.png",
    "Protecciones falla 3F franca nodo conexión proyecto.png",
    "Protecciones falla 3F 5ohms nodo conexión proyecto.png",
    "Protecciones falla 3F 15ohms nodo conexión proyecto.png",
    "Protecciones falla 3F 30ohms nodo conexión proyecto.png",
]

def obtener_ver():
    return st.session_state.get("ver_import", 0)

def obtener_val(clave, default):
    """Obtiene el valor guardado de un proyecto importado o devuelve el valor por defecto."""
    proy = st.session_state.get("proyecto_cargado", {})
    if isinstance(proy, dict) and clave in proy and proy[clave] is not None:
        return proy[clave]
    return default

def obtener_df(clave, df_default):
    """Obtiene un DataFrame guardado de un proyecto importado o devuelve el DataFrame por defecto."""
    proy = st.session_state.get("proyecto_cargado", {})
    if isinstance(proy, dict) and clave in proy:
        val = proy[clave]
        if isinstance(val, list):
            return pd.DataFrame(val)
        if isinstance(val, pd.DataFrame):
            return val
    return df_default

def serializar_objeto(obj):
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    if isinstance(obj, list):
        nueva_lista = []
        for item in obj:
            if isinstance(item, dict):
                nuevo_item = {}
                for k, v in item.items():
                    nuevo_item[k] = serializar_objeto(v)
                nueva_lista.append(nuevo_item)
            else:
                nueva_lista.append(item)
        return nueva_lista
    return obj

def exportar_proyecto_json(params_totales):
    """Empaqueta todas las variables, tablas, equipos adicionales del OR e imágenes en un JSON."""
    paquete = {
        "formato": "SEYEP_EACP_V1",
        "datos": {},
        "imagenes_b64": {}
    }

    for k, v in params_totales.items():
        paquete["datos"][k] = serializar_objeto(v)

    paquete["datos"]["num_equipos_or_extra"] = st.session_state.get("num_equipos_or_extra", 0)
    paquete["datos"]["num_cambios_or_extra"] = st.session_state.get("num_cambios_or_extra", 0)

    for img_name in IMAGENES_PROYECTO:
        if os.path.exists(img_name):
            try:
                with open(img_name, "rb") as f_img:
                    paquete["imagenes_b64"][img_name] = base64.b64encode(f_img.read()).decode("utf-8")
            except Exception:
                pass

    return json.dumps(paquete, ensure_ascii=False, indent=2).encode("utf-8")

def importar_proyecto_json(uploaded_json_file):
    """Restaura todas las variables, tablas e imágenes desde un archivo JSON de proyecto."""
    contenido = json.loads(uploaded_json_file.getvalue().decode("utf-8"))
    datos = contenido.get("datos", contenido)
    imagenes_b64 = contenido.get("imagenes_b64", {})

    st.session_state["proyecto_cargado"] = datos
    st.session_state["num_equipos_or_extra"] = int(datos.get("num_equipos_or_extra", len(datos.get("equipos_or_extra", []))))
    st.session_state["num_cambios_or_extra"] = int(datos.get("num_cambios_or_extra", len(datos.get("cambios_or_extra", []))))

    # Restaurar imágenes adjuntas en el archivo del proyecto
    for img_name, b64_str in imagenes_b64.items():
        if img_name in IMAGENES_PROYECTO and b64_str:
            try:
                with open(img_name, "wb") as f_out:
                    f_out.write(base64.b64decode(b64_str))
            except Exception:
                pass

    st.session_state["ver_import"] = st.session_state.get("ver_import", 0) + 1


def editor_tabla_seguro(df, key, num_rows="dynamic", disabled_cols=None):
    """
    Renderizador resiliente de tablas para Streamlit.
    - Modo Interactivo: Utiliza st.data_editor nativo.
    - Modo Compatible: Si el navegador presenta problemas para descargar los módulos
      dinámicos de JavaScript (TypeError: Failed to fetch dynamically imported module DataFrame.js),
      permite ver y editar directamente cada celda mediante campos de texto nativos de Streamlit.
    """
    if df is None:
        return None
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    ss_key = f"df_state_{key}"
    if ss_key not in st.session_state:
        st.session_state[ss_key] = df.copy()

    df_actual = st.session_state[ss_key]
    toggle_key = f"toggle_compat_{key}"
    modo_global_compatible = st.session_state.get("modo_tablas_compatible", False)
    modo_local_compatible = st.session_state.get(toggle_key, False)
    usar_modo_compatible = modo_global_compatible or modo_local_compatible

    c_info, c_btn = st.columns([4, 1.3])
    with c_btn:
        if usar_modo_compatible:
            if st.button("📊 Modo Interactivo", key=f"btn_m_inter_{key}", help="Volver a la cuadrícula interactiva st.data_editor"):
                st.session_state[toggle_key] = False
                st.session_state["modo_tablas_compatible"] = False
                st.rerun()
        else:
            if st.button("📝 Editar por Campos", key=f"btn_m_comp_{key}", help="Usa este modo si la cuadrícula muestra recuadro rojo 'TypeError: Failed to fetch dynamically imported module'"):
                st.session_state[toggle_key] = True
                st.rerun()

    if not usar_modo_compatible:
        try:
            df_editado = st.data_editor(
                df_actual,
                num_rows=num_rows,
                use_container_width=True,
                key=key
            )
            st.session_state[ss_key] = df_editado
            return df_editado
        except Exception:
            usar_modo_compatible = True

    if usar_modo_compatible:
        st.info("💡 **Modo Compatible:** Editando celdas mediante campos de texto directos (100% inmune a errores de red o caché en el navegador).")
        columnas = list(df_actual.columns)
        registros = df_actual.to_dict(orient="records")
        nuevos_registros = []
        fila_a_eliminar = None

        for idx, row in enumerate(registros):
            with st.container(border=True):
                c_lbl, c_del = st.columns([5, 1])
                with c_lbl:
                    st.caption(f"**Fila {idx + 1}**")
                with c_del:
                    if num_rows == "dynamic" and len(registros) > 1:
                        if st.button("🗑️", key=f"del_{key}_{idx}", help=f"Eliminar fila {idx + 1}"):
                            fila_a_eliminar = idx

                cols_inputs = st.columns(len(columnas))
                fila_editada = {}
                for col_idx, col_name in enumerate(columnas):
                    with cols_inputs[col_idx]:
                        val_prev = str(row.get(col_name, ""))
                        if val_prev in ("nan", "None"):
                            val_prev = ""
                        es_deshabilitada = bool(disabled_cols and col_name in disabled_cols)
                        nuevo_val = st.text_input(
                            f"{col_name}:",
                            value=val_prev,
                            disabled=es_deshabilitada,
                            key=f"inp_{key}_{idx}_{col_name}"
                        )
                        fila_editada[col_name] = nuevo_val
                nuevos_registros.append(fila_editada)

        if fila_a_eliminar is not None:
            nuevos_registros.pop(fila_a_eliminar)
            st.session_state[ss_key] = pd.DataFrame(nuevos_registros, columns=columnas)
            st.rerun()

        if num_rows == "dynamic":
            if st.button("➕ Agregar fila", key=f"add_row_{key}", type="secondary"):
                fila_vacia = {col: "" for col in columnas}
                nuevos_registros.append(fila_vacia)
                st.session_state[ss_key] = pd.DataFrame(nuevos_registros, columns=columnas)
                st.rerun()

        df_resultado = pd.DataFrame(nuevos_registros, columns=columnas)
        st.session_state[ss_key] = df_resultado
        return df_resultado
