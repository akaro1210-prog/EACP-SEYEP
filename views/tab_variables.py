import streamlit as st
from project_manager import obtener_val, obtener_ver

def render():
    ver = obtener_ver()
    st.subheader("📋 Variables Globales del Proyecto (ANEXO EACP)")
    st.write(
        "Define las variables principales del estudio. Estas variables alimentan automáticamente "
        "la Portada y todos los comandos LaTeX (`\\nombreProyecto`, `\\capacidadMW`, `\\CTO`, `\\NT`, `\\recocabecera`, `\\recoCTO`, etc.)."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        nombre_proyecto = st.text_input("Nombre del Proyecto (\\nombreProyecto):", value=obtener_val("nombreProyecto", "Arboreo"), key=f"v_nom_{ver}")
        capacidad_mw = st.text_input("Capacidad del Proyecto (\\capacidadMW):", value=obtener_val("capacidadMW", "900kW"), key=f"v_cap_{ver}")
        mes_entrega = st.text_input("Mes y Año de Entrega Portada (\\mesentregainformemasyear):", value=obtener_val("mesentregainformemasyear", "Septiembre, 2026"), key=f"v_mes_{ver}")
        operador_red = st.text_input("Operador de Red (\\OR):", value=obtener_val("OR", "EPM"), key=f"v_or_{ver}")
        fecha_entrada = st.text_input("Fecha Entrada en Operación (\\FechaEntrada):", value=obtener_val("FechaEntrada", "marzo del 2027"), key=f"v_fent_{ver}")

    with col2:
        cto = st.text_input("Circuito de Conexión (\\CTO):", value=obtener_val("CTO", "211-11"), key=f"v_cto_{ver}")
        ssee = st.text_input("Subestación (\\SSEE):", value=obtener_val("SSEE", "Doradal_13.2"), key=f"v_ssee_{ver}")
        nt = st.text_input("Nivel de Tensión (\\NT):", value=obtener_val("NT", "13.2kV"), key=f"v_nt_{ver}")
        nodo = st.text_input("Nodo de Conexión (\\nodo):", value=obtener_val("nodo", "906750"), key=f"v_nodo_{ver}")
        ubicacion = st.text_input("Ubicación (\\ubicacion):", value=obtener_val("ubicacion", "En predio del hotel Arboreo, Doradal, Antioquia"), key=f"v_ubi_{ver}")

    with col3:
        reco_cabecera = st.text_input("Reconectador de Cabecera OR (\\recocabecera):", value=obtener_val("recocabecera", "211-11"), key=f"v_rcab_{ver}")
        reco_cto = st.text_input("Protección Aguas Arriba OR (\\recoCTO):", value=obtener_val("recoCTO", "211-11"), key=f"v_rcto_{ver}")
        tipo_proteccion = st.text_input("Tipo de Elemento Protección OR (\\tipoproteccion):", value=obtener_val("tipoproteccion", "Reconectador"), key=f"v_tprot_{ver}")
        year_inicial = st.text_input("Año Inicial de Estudio (\\YearInicial):", value=obtener_val("YearInicial", "2027"), key=f"v_yi_{ver}")
        year_final = st.text_input("Año Final de Estudio (\\YearFinal):", value=obtener_val("YearFinal", "2032"), key=f"v_yf_{ver}")

    with st.expander("⚙️ Otras variables opcionales del encabezado LaTeX"):
        c_o1, c_o2, c_o3 = st.columns(3)
        with c_o1:
            latitud = st.text_input("Latitud (\\Latitud):", value=obtener_val("Latitud", '5°53\'49.8"N'), key=f"v_lat_{ver}")
            longitud = st.text_input("Longitud (\\Longitud):", value=obtener_val("Longitud", '74°45\'12.9"W'), key=f"v_lon_{ver}")
            elemento_proteccion = st.text_input("Elemento Protección (\\elementoProteccion):", value=obtener_val("elementoProteccion", "211-11"), key=f"v_elpr_{ver}")
        with c_o2:
            referencia_panel = st.text_input("Referencia Paneles (\\referenciaPanel):", value=obtener_val("referenciaPanel", "JAM66D45 625 LB"), key=f"v_rpan_{ver}")
            potencia_panel = st.text_input("Potencia Paneles (\\potenciaPanel):", value=obtener_val("potenciaPanel", "625 Wp"), key=f"v_ppan_{ver}")
            cantidad_panel = st.text_input("Cantidad Paneles (\\cantidadPanel):", value=obtener_val("cantidadPanel", "1760"), key=f"v_cpan_{ver}")
        with c_o3:
            ref_inversor_uno = st.text_input("Referencia Inversor 1 (\\refInversoruno):", value=obtener_val("refInversoruno", "Inversor 150 kW On-Grid."), key=f"v_rinv_{ver}")
            inversor_uno = st.text_input("Modelo Inversor 1 (\\Inversoruno):", value=obtener_val("Inversoruno", "Growat MAX 150KTL3-X2MV"), key=f"v_inv_{ver}")
            cantidad_inversor_uno = st.text_input("Cantidad Inversor 1 (\\cantidadInversoruno):", value=obtener_val("cantidadInversoruno", "6 Und."), key=f"v_cinv_{ver}")
            generacion_aprobada = st.text_input("Generación Aprobada (\\generacionaprobada):", value=obtener_val("generacionaprobada", "900kW"), key=f"v_gena_{ver}")

    config_vars = {
        "mesentregainformemasyear": mes_entrega,
        "nombreProyecto": nombre_proyecto,
        "capacidadMW": capacidad_mw,
        "OR": operador_red,
        "FechaEntrada": fecha_entrada,
        "Latitud": latitud,
        "Longitud": longitud,
        "YearInicial": year_inicial,
        "YearFinal": year_final,
        "CTO": cto,
        "SSEE": ssee,
        "NT": nt,
        "nodo": nodo,
        "elementoProteccion": elemento_proteccion,
        "referenciaPanel": referencia_panel,
        "potenciaPanel": potencia_panel,
        "cantidadPanel": cantidad_panel,
        "ubicacion": ubicacion,
        "refInversoruno": ref_inversor_uno,
        "Inversoruno": inversor_uno,
        "cantidadInversoruno": cantidad_inversor_uno,
        "generacionaprobada": generacion_aprobada,
        "recoCTO": reco_cto,
        "tipoproteccion": tipo_proteccion,
        "recocabecera": reco_cabecera,
    }
    st.session_state["config_vars"] = config_vars
    return config_vars
