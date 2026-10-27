import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Selector de Tuberías y Accesorios", page_icon="🔧", layout="wide")

# Este prototipo distingue datos tomados del PDF de reglas heurísticas no validadas.
CASES = {
    "Caso 1 · Solución de nitrato de plata": {
        "fluid": "Solución acuosa de nitrato de plata",
        "flow": 6.3, "temp": 30.0, "pressure": 2.0, "length": 15.0,
        "elbows": 3, "valves": 2, "filter": False, "solids": 0.0,
        "notes": "Síntesis verde de AgNPs; reducir contaminación metálica y mantener flujo estable.",
        "chemistry": "Sal acuosa; la concentración de AgNO₃ y otros componentes no está especificada en el PDF."
    },
    "Caso 2 · Suspensión acuosa de SiO₂": {
        "fluid": "Suspensión acuosa de nanopartículas de sílice",
        "flow": 9.8, "temp": 43.0, "pressure": 2.0, "length": 21.0,
        "elbows": 4, "valves": 1, "filter": True, "solids": 6.0,
        "notes": "Reducir sedimentación, aglomeración, obstrucciones y pérdidas de carga.",
        "chemistry": "Suspensión con 6 % en masa de sólidos; viscosidad, tamaño de partícula y pH no especificados."
    },
    "Caso 3 · Mezcla ácida del método de Hummers": {
        "fluid": "H₂SO₄ + KMnO₄ + partículas de grafito oxidado",
        "flow": None, "temp": 48.0, "pressure": 2.5, "length": 17.0,
        "elbows": 5, "valves": 1, "filter": False, "solids": None,
        "notes": "Evitar corrosión, fugas y acumulación de sólidos/residuos.",
        "chemistry": "Medio ácido y oxidante. Concentraciones, proporciones, composición exacta y caudal no especificados."
    }
}

# Compatibilidad preliminar deliberadamente conservadora. No sustituye tablas de fabricantes.
MATERIALS = {
    "Acero al carbono": {"tmax": 400, "p_note": "Depende de cédula, diámetro, unión y norma", "acid": "No recomendado sin evaluación", "oxidizer": "No recomendado sin evaluación", "salts": "Evaluar corrosión", "solids": "Puede erosionarse/contaminar"},
    "Acero inoxidable 316/316L": {"tmax": 500, "p_note": "Depende de cédula, diámetro, unión y norma", "acid": "No asumir compatible", "oxidizer": "No asumir compatible", "salts": "Riesgo de picadura con cloruros", "solids": "Resistencia mecánica; evaluar desgaste"},
    "PVC-U / CPVC": {"tmax": 60, "p_note": "Presión admisible cae con temperatura; revisar fabricante", "acid": "Depende de concentración y temperatura", "oxidizer": "Verificar compatibilidad específica", "salts": "Generalmente buena resistencia; verificar", "solids": "Evaluar abrasión y diseño"},
    "HDPE": {"tmax": 60, "p_note": "Presión admisible cae con temperatura; revisar fabricante", "acid": "Depende de concentración y temperatura", "oxidizer": "Verificar compatibilidad específica", "salts": "Generalmente buena resistencia; verificar", "solids": "Puede ayudar frente a abrasión; verificar"},
    "Polipropileno (PP)": {"tmax": 90, "p_note": "Presión admisible cae con temperatura; revisar fabricante", "acid": "Depende de concentración y temperatura", "oxidizer": "Verificar compatibilidad específica", "salts": "Generalmente buena resistencia; verificar", "solids": "Evaluar abrasión y diseño"},
    "PTFE (revestimiento/liner)": {"tmax": 200, "p_note": "Depende del diseño del sistema revestido", "acid": "Amplia resistencia, confirmar mezcla/condiciones", "oxidizer": "Confirmar condiciones de proceso y fabricante", "salts": "Buena resistencia química general", "solids": "Evaluar liner, velocidad y diseño"}
}

def material_assessment(case_name, data):
    rows = []
    for material, m in MATERIALS.items():
        score, warnings = 0, []
        # Temperatura: solo alerta de cribado, no certifica diseño.
        if data["temp"] > m["tmax"]:
            warnings.append(f"Temperatura supera el umbral de cribado ({m['tmax']} °C); descartar salvo ficha técnica que demuestre lo contrario.")
            score -= 4
        else:
            score += 1
        if "Hummers" in case_name:
            warnings.append(m["acid"] + "; " + m["oxidizer"] + ". Se requiere confirmación escrita del fabricante para la mezcla real.")
            if material in ["Acero al carbono", "Acero inoxidable 316/316L"]:
                score -= 3
            if material in ["PTFE (revestimiento/liner)", "PVC-U / CPVC", "HDPE", "Polipropileno (PP)"]:
                score += 1
        elif "SiO₂" in case_name:
            warnings.append("Verificar abrasión, sedimentación, diámetro, velocidad y compatibilidad con el dispersante.")
            if material in ["HDPE", "Polipropileno (PP)", "PVC-U / CPVC"]:
                score += 1
        else:
            warnings.append("Confirmar compatibilidad con la concentración real de AgNO₃ y extracto vegetal; revisar riesgo de contaminación.")
            if material in ["PVC-U / CPVC", "HDPE", "Polipropileno (PP)", "PTFE (revestimiento/liner)"]:
                score += 1
        rows.append({"Material candidato": material, "Cribado preliminar": "Revisar" if warnings else "Pendiente", "Puntos de cribado (no validación)": score, "Advertencias": " ".join(warnings)})
    return pd.DataFrame(rows).sort_values("Puntos de cribado (no validación)", ascending=False)

st.title("🔧 Selector Interactivo de Tuberías y Accesorios")
st.caption("Operaciones Unitarias · Prototipo educativo basado en la presentación del equipo")
st.warning("Uso educativo y de preselección. Las puntuaciones son heurísticas del prototipo, no cálculos certificados ni una aprobación de compatibilidad. No usar para diseñar o operar una instalación real sin revisión de ingeniería, fichas técnicas y evaluación de riesgos.")

with st.sidebar:
    st.header("Navegación")
    section = st.radio("Ir a", ["Selector", "Propiedades del fluido", "Compatibilidad química", "Accesorios y riesgos", "Casos de estudio", "Datos y límites"])
    st.divider()
    st.markdown("**Clave de evidencia**")
    st.markdown("🔵 **Del PDF:** datos y objetivos explícitos de los casos.")
    st.markdown("🟠 **Supuesto/regla preliminar:** criterio de demostración que requiere validación.")

if section == "Selector":
    st.subheader("1 · Condiciones del proceso")
    case_name = st.selectbox("Cargar un caso de la presentación", list(CASES.keys()))
    case = CASES[case_name]
    st.info("Los valores cargados se transcriben del PDF. Si un dato no aparece allí, se muestra como no especificado y no se inventa.")
    c1, c2, c3 = st.columns(3)
    with c1:
        fluid = st.text_input("Fluido / mezcla", value=case["fluid"])
        temp = st.number_input("Temperatura (°C)", min_value=-50.0, max_value=500.0, value=float(case["temp"]), step=1.0)
        pressure = st.number_input("Presión de operación (bar)", min_value=0.0, max_value=1000.0, value=float(case["pressure"]), step=0.1)
    with c2:
        flow_default = case["flow"] if case["flow"] is not None else 0.0
        flow = st.number_input("Caudal (L/min) · 0 = no especificado", min_value=0.0, max_value=100000.0, value=float(flow_default), step=0.1)
        length = st.number_input("Longitud de recorrido (m)", min_value=0.0, max_value=100000.0, value=float(case["length"]), step=1.0)
        solids_default = case["solids"] if case["solids"] is not None else 0.0
        solids = st.number_input("Sólidos (% masa) · 0 = no especificado", min_value=0.0, max_value=100.0, value=float(solids_default), step=0.5)
    with c3:
        elbows = st.number_input("Número de codos", min_value=0, max_value=1000, value=int(case["elbows"]), step=1)
        valves = st.number_input("Número de válvulas", min_value=0, max_value=1000, value=int(case["valves"]), step=1)
        has_filter = st.checkbox("Incluye filtro", value=bool(case["filter"]))
        fluid_type = st.selectbox("Clasificación preliminar", ["Acuoso / solución", "Suspensión con sólidos", "Ácido", "Oxidante", "Ácido + oxidante", "Otro"])
    st.markdown("**Objetivo del caso (del PDF)**")
    st.write(case["notes"])
    st.markdown("**Datos químicos faltantes (del PDF)**")
    st.write(case["chemistry"])
    if st.button("Evaluar candidatos", type="primary", use_container_width=True):
        st.session_state["evaluated"] = True
        st.session_state["selected_case"] = case_name
        st.session_state["eval_data"] = {"temp": temp, "pressure": pressure, "flow": flow, "length": length, "solids": solids, "elbows": elbows, "valves": valves, "filter": has_filter, "fluid": fluid, "fluid_type": fluid_type}
    if st.session_state.get("evaluated", False):
        d = st.session_state["eval_data"]
        st.subheader("2 · Resultado del cribado")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Temperatura", f"{d['temp']:.1f} °C")
        m2.metric("Presión", f"{d['pressure']:.1f} bar")
        m3.metric("Caudal", f"{d['flow']:.1f} L/min" if d["flow"] > 0 else "No especificado")
        m4.metric("Accesorios", f"{d['elbows']} codos · {d['valves']} válvulas")
        results = material_assessment(st.session_state["selected_case"], d)
        st.dataframe(results, use_container_width=True, hide_index=True)
        st.error("El orden de la tabla es una ayuda heurística para organizar la revisión; NO significa que el primer material sea seguro o compatible. No se ha calculado diámetro, velocidad, Reynolds, pérdidas de carga, NPSHa/NPSHr ni golpe de ariete porque faltan datos.")
        st.download_button("Descargar resultados CSV", results.to_csv(index=False).encode("utf-8-sig"), file_name="cribado_materiales.csv", mime="text/csv")

elif section == "Propiedades del fluido":
    st.subheader("Propiedades físicas y variables faltantes")
    st.markdown("**Del PDF:** viscosidad, densidad, temperatura, presión de vapor y sólidos suspendidos afectan bombeo, pérdidas de carga, presión hidrostática y riesgo de cavitación.")
    st.dataframe(pd.DataFrame([
        ["Viscosidad", "No proporcionada en los tres casos", "Afecta pérdidas de carga y capacidad de bombeo"],
        ["Densidad", "No proporcionada en los tres casos", "Afecta presión hidrostática y caudal másico"],
        ["Temperatura", "Casos 1–3: 30, 43 y 48 °C", "Dato del PDF"],
        ["Presión de vapor", "No proporcionada", "Necesaria para evaluar margen de vaporización/cavitación"],
        ["Sólidos suspendidos", "Caso 2: 6 % masa; caso 3 contiene grafito oxidado", "Faltan tamaño de partícula, distribución y tendencia a aglomeración"],
        ["pH / concentración química", "No especificados en detalle", "Necesarios para verificar compatibilidad química"],
    ], columns=["Parámetro", "Estado de datos", "Importancia"]))
    st.info("No se estiman valores de viscosidad o densidad a partir del nombre del fluido: la formulación, concentración y temperatura pueden cambiar las propiedades.")
    st.subheader("Cálculos que se habilitarían con datos suficientes")
    st.markdown("- Velocidad media: requiere caudal volumétrico y diámetro interno.\n- Reynolds: requiere densidad, viscosidad, velocidad y diámetro.\n- Pérdida de carga: requiere diámetro, rugosidad, longitud, accesorios y propiedades.\n- Cavitación: requiere presión de vapor, elevaciones, pérdidas de succión y datos de bomba para comparar NPSHa con NPSHr.")

elif section == "Compatibilidad química":
    st.subheader("Matriz de compatibilidad química")
    st.warning("El PDF incluye categorías de materiales y agentes, pero no aporta resultados completos verificados para cada celda. La matriz siguiente no marca materiales como “inertes” sin datos específicos.")
    rows = [
        ["Acero al carbono", "Requiere evaluación", "Requiere evaluación", "Riesgo de corrosión", "No asumir compatible", "Revisar pares y aislamiento"],
        ["Acero inoxidable 316/316L", "Depende de ácido y concentración", "Depende de agente", "Riesgo de picadura/crevice", "No asumir compatible", "Revisar contacto con otros metales"],
        ["PVC-U / CPVC", "Depende de concentración/temperatura", "Depende de formulación", "Verificar ficha", "Verificar ficha", "Considerar uniones y temperatura"],
        ["Cobre / bronce", "No asumir compatible", "Depende de agente", "Verificar corrosión", "No asumir compatible", "Posible par galvánico"],
        ["HDPE", "Depende de concentración/temperatura", "Verificar agente", "Generalmente resistente, confirmar", "Verificar agente", "Aislar metales si corresponde"],
        ["Polipropileno (PP)", "Depende de concentración/temperatura", "Verificar agente", "Generalmente resistente, confirmar", "Verificar agente", "Aislar metales si corresponde"],
        ["PTFE (liner/junta)", "Amplia resistencia, confirmar mezcla", "Confirmar", "Buena resistencia general", "Confirmar condiciones", "No aplica como tubería metálica"],
    ]
    st.dataframe(pd.DataFrame(rows, columns=["Material", "Ácidos fuertes", "Bases fuertes", "Cloruros", "Oxidantes", "Apareamiento galvánico"]), use_container_width=True, hide_index=True)
    st.caption("Las frases de esta tabla son orientación general del prototipo, no certificaciones. Para selección final se necesita identidad química, concentración, temperatura, presión, tiempo de contacto, permeación, tipo de unión y aprobación del fabricante.")
    st.markdown("**Estados previstos para una futura matriz validada:** Inerte · Tolerante con límites · No recomendado · Sin datos.")

elif section == "Accesorios y riesgos":
    st.subheader("Accesorios y fenómenos críticos")
    st.dataframe(pd.DataFrame([
        ["Codos", "Pérdida de presión; desgaste en suspensiones", "Reducir cambios innecesarios de dirección; revisar radio y diámetro"],
        ["Válvulas", "Restricción, fuga, bloqueo; cierre rápido", "Seleccionar tipo/material y tiempo de cierre según proceso"],
        ["Filtro", "Obstrucción por aglomerados o sólidos", "Definir tamaño de retención, diferencial de presión y plan de limpieza"],
        ["Reducciones / tees", "Zonas de recirculación y acumulación", "Evitar geometrías que favorezcan sedimentación"],
        ["Cavitación", "Presión local bajo presión de vapor", "Comparar NPSHa con NPSHr; faltan datos para calcularlo"],
        ["Golpe de ariete", "Sobrepresión por cambios bruscos de velocidad", "Evaluar transitorios, cierre de válvulas y necesidad de alivio/amortiguación"],
        ["Juntas / sellos", "Fuga, hinchamiento, degradación", "Confirmar PTFE, EPDM, NBR o FKM con fabricante para el fluido real"],
    ], columns=["Elemento/fenómeno", "Riesgo", "Acción de revisión"]), use_container_width=True, hide_index=True)
    st.warning("El PDF describe mitigaciones generales, pero no contiene datos suficientes para dimensionar válvulas, filtros, sellos o dispositivos de protección.")

elif section == "Casos de estudio":
    st.subheader("Casos de la presentación")
    for name, c in CASES.items():
        with st.expander(name, expanded=False):
            a, b = st.columns(2)
            with a:
                st.markdown("**Datos transcritos del PDF**")
                st.write(f"Fluido: {c['fluid']}")
                st.write(f"Temperatura: {c['temp']} °C · Presión: {c['pressure']} bar")
                st.write(f"Longitud: {c['length']} m · Codos: {c['elbows']} · Válvulas: {c['valves']}")
                st.write(f"Caudal: {c['flow']} L/min" if c["flow"] is not None else "Caudal: no especificado")
                st.write(f"Sólidos: {c['solids']} % masa" if c["solids"] is not None else "Sólidos: presentes, concentración no especificada")
            with b:
                st.markdown("**Objetivo / información pendiente**")
                st.write(c["notes"])
                st.write(c["chemistry"])
    st.markdown("### Lista de comprobación para validar cada caso")
    checks = [
        "Concentración y composición química completas",
        "Temperatura y presión de diseño, no solo operación",
        "Caudal, viscosidad y densidad medidos o documentados",
        "Diámetro interno, material y clase de presión",
        "Compatibilidad confirmada por tabla/ficha del fabricante",
        "Compatibilidad de juntas, adhesivos y uniones",
        "Revisión de pérdidas de carga, transitorios y riesgos",
        "Procedimiento de operación, contención y respuesta a derrames"
    ]
    for item in checks:
        st.checkbox(item, key="check_" + item)

elif section == "Datos y límites":
    st.subheader("Trazabilidad: verificado frente a supuesto")
    st.markdown("**Verificado en el PDF adjunto**")
    st.write("- Casos 1–3 y sus caudales/temperaturas/presiones/longitudes/accesorios cuando están indicados.\n- Objetivos de cada caso y fenómenos a considerar.\n- Familias de materiales mencionadas y necesidad de revisar compatibilidad física y química.")
    st.markdown("**Supuestos o elementos no validados del prototipo**")
    st.write("- Umbrales de temperatura usados para alertas iniciales: solo cribado; no equivalen a ratings de producto.\n- Puntuaciones y orden de materiales: heurística para organizar la revisión, no recomendación final.\n- No se ha verificado compatibilidad exacta de AgNO₃, mezcla Hummers ni suspensiones con ningún producto comercial.")
    st.markdown("**Datos requeridos antes de recomendar una línea real**")
    st.write("- Fichas de seguridad (SDS), concentraciones, impurezas, pH, oxidantes y tiempo de contacto.\n- Caudal completo, diámetro, rugosidad, trazado/elevaciones, propiedades reológicas y curva de bomba.\n- Clase de presión a la temperatura real, método de unión, juntas y requisitos de limpieza.")
    st.caption("El contenido de esta aplicación se basa en el PDF aportado por el equipo y añade una capa de organización/cribado marcada explícitamente como no validada. No sustituye normas aplicables ni revisión de un profesional competente.")

st.divider()
st.caption("Prototipo académico · Selector Interactivo de Tuberías y Accesorios · Universidad Politécnica de Sinaloa")
