"""Regenera una presentacion PowerPoint de 27 diapositivas, 16:9 y en español.

python -m pip install python-pptx
python build_slides.py

Usa animaciones compatibles: fundidos/deslizamientos entre diapositivas y
revelacion por etapas de las explicaciones (sin VBA ni macros).
"""
from pathlib import Path
from zipfile import ZipFile
from tempfile import NamedTemporaryFile
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

OUT = Path(__file__).with_name("presentacion_intro_ia.pptx")
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
DARK, PANEL, WHITE, MUTED = "091327", "152840", "F5F9FF", "B5C7DC"
CYAN, BLUE, LILAC, GOLD = "58E1D0", "80ACFF", "C3A4FF", "FFB870"
PALETTE = (CYAN, BLUE, LILAC, GOLD)

def rgb(c):
    return RGBColor.from_string(c)

def txt(slide, value, x, y, w, h, sz=20, color=WHITE, bold=False):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = shape.text_frame
    frame.clear(); frame.word_wrap = True
    for i, sentence in enumerate(str(value).split("\n")):
        p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        p.text = sentence
        for r in p.runs:
            r.font.name = "Aptos"
            r.font.size = Pt(sz)
            r.font.bold = bold
            r.font.color.rgb = rgb(color)
    return shape

def block(slide, x, y, w, h, heading, body, accent=CYAN):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = rgb(PANEL); sh.line.fill.background()
    txt(slide, heading, x+.20, y+.20, w-.4, .66, 19, accent, True)
    txt(slide, body, x+.20, y+.92, w-.4, h-.98, 16, WHITE)

def add(label, heading, subtitle, cards=(), bottom="", accent=CYAN, hero=False):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = rgb(DARK)
    txt(slide, "CURSO DE SISTEMAS MULTIAGENTES  /  MÓDULO 0", .60, 7.12, 8, .25, 10, MUTED, True)
    txt(slide, f"{len(prs.slides):02}", 12.1, 7.09, .8, .29, 11, MUTED)
    if hero:
        txt(slide, label.upper(), .65, .68, 11, .42, 15, accent, True)
        txt(slide, heading, .65, 1.45, 11.9, 3.2, 43, WHITE, True)
        txt(slide, subtitle, .71, 5.35, 10.8, .95, 23, MUTED)
        return
    txt(slide, label.upper(), .65, .46, 11.3, .35, 12, accent, True)
    txt(slide, heading, .65, .96, 11.8, .83, 31, WHITE, True)
    txt(slide, subtitle, .66, 1.80, 11.8, .58, 17, MUTED)
    n = len(cards)
    if n:
        cols = 2 if n in (2,4) else (3 if n in (3,6) else min(n,4))
        rows = (n + cols - 1) // cols
        width = (11.82-(cols-1)*.25)/cols
        height = 3.4/rows - .19
        for i,(name,explain) in enumerate(cards):
            x = .69+(i%cols)*(width+.25); y=2.66+(i//cols)*(height+.30)
            block(slide,x,y,width,height,name,explain,PALETTE[i%4])
    if bottom: txt(slide,bottom,.79,6.36,11.8,.5,16,accent)

add("Introducción a la inteligencia artificial", "¿Y SI EL\nSOFTWARE\nPUDIERA APRENDER?",
    "De reglas programadas a modelos, lenguaje y agentes", hero=True)
add("Punto de partida","Una pregunta que cambia la forma de programar",
    "¿Cómo decide un programa a qué equipo enviar un mensaje?",
    [("EL MENSAJE","«Mi cuenta no me deja entrar y tengo que pagar hoy»")],
    "El mismo problema, cuatro posibles tecnologías.")
add("El reto","Clasificar mensajes en cuatro equipos",
    "Una entrada libre en español debe convertirse en una categoría.",
    [("ACCESO","Cuenta, contraseña, credenciales"),
     ("FACTURACIÓN","Cobros, pagos y recibos"),
     ("SOPORTE TÉCNICO","Errores y fallas en la aplicación"),
     ("ENVÍOS","Entregas y paquetes")])
add("Actividad · 15 minutos","Antes de IA: diseñen un algoritmo",
    "En parejas: pseudocódigo o Python con if/else.",
    [("CREAR REGLAS","Buscar palabras o patrones, establecer prioridades."),
     ("PROBAR EXCEPCIONES","«Me debitaron dos veces»; «La web se congela».")],
    "Anoten los fallos antes de modificar las reglas.")
add("Método 1: reglas","Primero: instrucciones explícitas","Una persona programa condiciones conocidas.",
    [("IF / ELSE", "Si contiene «contraseña» → ACCESO\nSi contiene «cobro» → FACTURACIÓN\nSi contiene «error» → SOPORTE TÉCNICO\nSi no coincide nada → REVISIÓN")],
    "Control y trazabilidad, pero mantenimiento de excepciones.")
add("Prueba de estrés","¿Y si la persona usa otras palabras?",
    "Un mensaje nuevo puede expresar el mismo concepto.",
    [("CASO 1","«No puedo acceder con mis credenciales»"),
     ("CASO 2","«La web queda inmóvil»"),
     ("CASO 3","«Me debitaron dos veces»")],
    "Las reglas no son malas; tienen un dominio de aplicación.")
add("Cambio conceptual","¿Y si enseñamos mediante ejemplos?",
    "Todo modelo ejecuta algoritmos; cambia la forma de obtener sus parámetros.",
    [("REGLAS","Una persona escribe las condiciones y el programa las ejecuta."),
     ("ML SUPERVISADO","Una persona aporta ejemplos; el entrenamiento aprende parámetros.")],
    "Reglas diseñadas vs. patrones aprendidos.")
add("Aprendizaje supervisado 1/3","Un modelo aprende a partir de datos",
    "Primero presentamos ejemplos etiquetados.",
    [("DATOS DE ENTRENAMIENTO","«Olvidé mi contraseña» → acceso\n«Me cobraron dos veces» → facturación\n«Mi paquete se retrasó» → envíos")])
add("Aprendizaje supervisado 2/3","Un modelo aprende a partir de datos",
    "Segundo: los algoritmos ajustan parámetros durante el entrenamiento.",
    [("DATOS","Textos y etiquetas"),("ENTRENAMIENTO","TF-IDF + regresión logística")])
add("Aprendizaje supervisado 3/3","Un modelo aprende a partir de datos",
    "Tercero: el modelo infiere la categoría de un mensaje nuevo.",
    [("ENTRENAR","Ejemplos etiquetados"),("MODELO","Parámetros aprendidos"),
     ("INFERIR","Un mensaje nuevo"),("SALIDA","Categoría predicha")],
    "Una predicción no garantiza verdad.")
add("Mapa conceptual","IA es un campo amplio, no una sola tecnología",
    "Las categorías se solapan; deep learning forma parte de machine learning.",
    [("IA SIMBÓLICA","Reglas, búsqueda y representación explícita"),
     ("MACHINE LEARNING","Patrones aprendidos de datos"),
     ("DEEP LEARNING","Redes neuronales profundas"),
     ("IA GENERATIVA","Generación de texto, imágenes, código y audio")])
add("Método 3 · embeddings","Representar significado con vectores",
    "Un modelo multilingüe preentrenado sitúa frases parecidas cerca.",
    [("CLÚSTER: ACCESO","«clave de ingreso»\n«mi contraseña»"),
     ("CLÚSTER: COBROS","«error de pago»\n«cargo duplicado»"),
     ("CLÚSTER: ENVÍOS","«pedido perdido»\n«paquete retrasado»")],
    "Similitud semántica no equivale a verdad.")
add("Método 4 · LLM","La instrucción se expresa en lenguaje natural",
    "El modelo puede clasificar sin escribir una regla por sinónimo.",
    [("PROMPT","«Clasifica en acceso, facturación, soporte técnico o envíos. Responde JSON.»")],
    "Los LLM pueden producir respuestas convincentes e incorrectas.")
add("Detrás del modelo","Cómo un LLM transforma texto en respuesta",
    "Diagrama simplificado, no una explicación de conciencia o intención.",
    [("TEXTO","Mensaje e instrucciones"),("TOKENS","Unidades numéricas"),
     ("TRANSFORMER","Predicción contextual"),("SALIDA","Secuencia generada")])
add("Decisión de ingeniería","¿Cuál gana? Depende de lo que valoremos.",
    "Comparar exactitud, latencia, costo, privacidad y mantenimiento.",
    [("REGLAS","Predecibles, pero frágiles a variaciones."),
     ("ML","Rápido y entrenable; necesita ejemplos."),
     ("EMBEDDINGS","Similitud, pero puede fallar el contexto."),
     ("LLM","Flexible, pero costoso y no infalible.")],
    "No elijas por una demo espectacular.")
add("Experimento reproducible","¡Ejecutemos la misma prueba!",
    "Mismos mensajes, categorías y métricas para todos los métodos.",
    [("EN TERMINAL","python comparar.py --metodos reglas ml")],
    "16 mensajes sintéticos no validan un sistema de producción.")
add("Límites","La IA también se equivoca",
    "La potencia no elimina la necesidad de ingeniería.",
    [("ALUCINACIONES","Respuestas plausibles, pero falsas."),
     ("SESGOS","Patrones indeseables de datos."),
     ("PRIVACIDAD","Datos y permisos deben protegerse.")],
    "Evaluación, seguridad y supervisión humana.")
add("Un nuevo nivel","Clasificar no es lo mismo que actuar",
    "Un modelo produce salidas; una arquitectura de agente usa políticas y herramientas.",
    [("MODELO","Entrada → predicción o texto"),
     ("AGENTE","Observa → decide → valida → actúa")])
add("Agente · paso 1/3","Del mensaje a la decisión",
    "Primero: percibir un mensaje.",
    [("OBSERVAR","«No puedo entrar»")])
add("Agente · paso 2/3","Del mensaje a la decisión",
    "Segundo: proponer una clasificación y validarla.",
    [("OBSERVAR","Mensaje"),("DECIDIR","Categoría: acceso"),("VALIDAR","¿Está autorizado?")])
add("Agente · paso 3/3","Del mensaje a una acción controlada",
    "Tercero: ejecutar una herramienta solo si está autorizado.",
    [("OBSERVAR","Mensaje"),("DECIDIR","Modelo o reglas"),
     ("VALIDAR","Aprobación"),("ACTUAR","Ticket simulado")],
    "La práctica NO crea tickets reales.")
add("Sistemas multiagentes","La colaboración requiere coordinación",
    "Varios modelos no crean automáticamente un sistema multiagente.",
    [("COORDINADOR","Asigna tareas"),("ESPECIALISTA","Analiza"),
     ("VERIFICADOR","Comprueba"),("HERRAMIENTA","Actúa con permisos")],
    "Necesitamos roles, comunicación, control y evaluación.")
add("La revolución","¿Por qué la IA cambia el trabajo?",
    "Disminuye el costo de procesar lenguaje y datos no estructurados.",
    [("CREAR","Borradores, ideas y código"),("ANALIZAR","Documentos y señales"),
     ("PERSONALIZAR","Servicios adaptados"),("AUTOMATIZAR","Acciones con controles")],
    "Potencial no significa impacto garantizado.")
add("Criterio profesional","La pregunta no es «¿dónde pongo IA?»",
    "¿Qué solución resuelve el problema con riesgos aceptables?",
    [("USAR REGLAS","Cuando hay condiciones claras y verificables."),
     ("USAR MODELOS","Cuando existen patrones complejos o lenguaje flexible.")],
    "Muchas soluciones robustas combinan ambas.")
add("Trabajo en equipos","Defiende una decisión técnica",
    "Prepara una recomendación para la empresa ficticia.",
    [("01","¿Qué errores observaste?"),("02","¿Qué método elegirías?"),
     ("03","¿Qué no automatizarías?"),("04","¿Cómo lo evaluarías?")],
    "Entregable: reglas, fallos, comparación y recomendación.")
add("Ruta de aprendizaje","De una predicción a un sistema multiagente",
    "Esta clase prepara las siguientes cuatro unidades.",
    [("MÓDULO 1","Agentes y LLM"),("MÓDULO 2","Tools, RAG y memoria"),
     ("MÓDULO 3","Control y evaluación"),("MÓDULO 4","Sistemas multiagentes")],
    "El modelo predice. El agente actúa. El sistema multiagente coordina.")
add("La idea clave","EL FUTURO NO ES\nSOLO ESCRIBIR\nMÁS REGLAS.",
    "Es saber cuándo combinar algoritmos, modelos y agentes.",hero=True)

prs.save(OUT)
NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
with ZipFile(OUT) as z:
    members=[(f,z.read(f.filename)) for f in z.infolist()]
with NamedTemporaryFile(dir=OUT.parent, suffix=".pptx",delete=False) as f:
    temp=Path(f.name)
with ZipFile(temp,"w") as z:
    for info,data in members:
        if info.filename.startswith("ppt/slides/slide") and info.filename.endswith(".xml"):
            root=etree.fromstring(data)
            node=etree.Element("{%s}transition"%NS,spd="med",advClick="1")
            etree.SubElement(node,"{%s}fade"%NS)
            ovr=root.find("{%s}clrMapOvr"%NS)
            root.insert(root.index(ovr)+1,node) if ovr is not None else root.append(node)
            data=etree.tostring(root,encoding="UTF-8",xml_declaration=True)
        z.writestr(info,data)
temp.replace(OUT)
print("Generadas",len(prs.slides),"diapositivas en",OUT)
