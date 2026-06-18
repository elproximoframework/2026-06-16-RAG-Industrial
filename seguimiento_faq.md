# Seguimiento y FAQ del Proyecto - RAG Industrial

Este archivo sirve para registrar de forma continua las tareas realizadas, las decisiones de diseno, los problemas encontrados y sus soluciones, asi como las dudas y preguntas del usuario a lo largo del desarrollo.

---

## [2026-06-16] Hito 1: Inicializacion del Repositorio y CI (Sin CD)

### Resumen del Trabajo Realizado
Se ha inicializado la estructura base del proyecto Python y la automatizacion en GitHub.

1. **Estructura base del proyecto Python**:
   - Creacion de los modulos y paquetes base:
     - `app/__init__.py` y `app/main.py` (con estructura de ejecucion vacia).
     - `tests/__init__.py` y `tests/test_main.py` (con un test unitario simple de importacion).
   - Creacion de archivos de dependencias:
     - `requirements.txt` (vacio para dependencias de produccion).
     - `requirements-dev.txt` (con `pytest` y `ruff` para testing y linting).
   - Configuracion de exclusion:
     - `.gitignore` adecuado para proyectos Python.

2. **Integracion Continua (CI)**:
   - Creacion de la accion de GitHub en `.github/workflows/ci.yml`.
   - Se ejecuta en Pull Requests hacia las ramas `main` y `dev`.
   - Pasos del pipeline:
     1. Checkout de codigo.
     2. Configuracion de Python 3.12 (con cache de dependencias pip).
     3. Instalacion de dependencias de desarrollo (`requirements-dev.txt`).
     4. Analisis estatico de codigo con `ruff check`.
     5. Ejecucion de tests unitarios con `pytest`.

3. **Script de Automatizacion de GitHub (`setup_github.py`)**:
   - Creacion y adaptacion del script en Python para:
     - Crear de manera automatica el repositorio remoto en GitHub.
     - Inicializar Git localmente.
     - Subir la rama `main` y la rama `dev`.
     - Crear los **Rulesets de proteccion** (Branch Protection Rulesets) para bloquear force pushes, borrados de ramas y forzar la revision de PRs para `main` y `dev`.
     - Omitir la configuracion de CD (Secrets de AWS, variables de cluster y entorno "production").

---

### FAQ y Problemas Encontrados

#### P1: Error de codificacion de caracteres al ejecutar el script setup_github.py en Windows (UnicodeEncodeError)
* **Sintoma**:
  ```
  UnicodeEncodeError: 'charmap' codec can't encode characters in position 2-61: character maps to <undefined>
  ```
  Ocurria al intentar imprimir lineas decorativas con caracteres UTF-8 como `═` o `✅` en la terminal PowerShell/CMD de Windows.
* **Solucion**: Se modifico todo el output del script `setup_github.py` para utilizar caracteres puramente ASCII (como `-`, `=`, `[OK]` y `[SKIP]`).

#### P2: GitHub bloquea el push debido a politicas de proteccion de secretos (GitHub Push Protection)
* **Sintoma**:
  ```
  remote: error: GH013: Repository rule violations found for refs/heads/main.
  remote: - GITHUB PUSH PROTECTION
  remote:   Push cannot contain secrets
  ```
  GitHub detectaba el token hardcodeado (`ghp_...`) en `setup_github.py` al subir el repositorio inicial, ya que el script se incluia en el commit (`git add .`).
* **Solucion**:
  1. Se agrego `setup_github.py` al `.gitignore` para evitar que vuelva a incluirse en commits futuros.
  2. Se reseteo el repositorio local eliminando la carpeta `.git` para limpiar el historial de commits que contenia la credencial.
  3. Se volvio a ejecutar el setup inicial exitosamente, subiendo el codigo limpio a GitHub.

#### P3: ¿Qué otras opciones de parsing de PDFs o Word (.docx) a Markdown tenemos disponibles para RAG Industrial (Fase 1, 2.1)?
* **Respuesta**:
  Además de LlamaParse y Unstructured.io, se evaluaron las siguientes opciones:
  
  * **Opciones Open-Source y Locales (Privacidad y Cero Costo)**:
    * **IBM Docling**: Muy robusto para tablas complejas y múltiples formatos (PDF, DOCX, PPTX). Utiliza modelos locales livianos.
    * **Marker**: Especializado en PDFs de ingeniería, extrayendo ecuaciones matemáticas (LaTeX) y tablas. Requiere GPU/recursos altos.
    * **PyMuPDF4LLM**: Ultra rápido y de bajo consumo en CPU, convierte tablas nativas y jerarquía visual a Markdown.
    * **Pandoc**: El estándar absoluto para convertir Word (`.docx`) a Markdown estructurado con 100% de fidelidad de manera nativa.
  
  * **Opciones Cloud Enterprise**:
    * **Azure Document Intelligence (Layout API)**: Máxima precisión OCR de la industria para manuales escaneados o planos con tablas densas, con exportación nativa a Markdown.
    * **AWS Textract / Google Cloud Document AI**: Potentes OCRs con capacidad de extracción de tablas (requieren formateo posterior a Markdown).

  ##### Tabla Comparativa de Capacidades:

  | Alternativa | Tipo | Precisión en Tablas | Precisión en Word (.docx) | Requisitos de Cómputo | Costo / Licencia |
  | :--- | :--- | :--- | :--- | :--- | :--- |
  | **Docling (IBM)** | Local / OS | Excelente | Muy buena | Medio (CPU/GPU local) | Libre (Apache 2.0) |
  | **Marker** | Local / OS | Excelente | No soporta | Alto (Requiere GPU) | Libre (GPL-3.0) |
  | **PyMuPDF4LLM** | Local / OS | Buena | No soporta | Muy bajo (CPU ligera) | Comercial / AGPL |
  | **Pandoc** | Local / OS | Excelente | Excelente | Extremadamente bajo | Libre (GPL) |
  | **Azure Document Intelligence** | Cloud API | Excelente | Excelente | Ninguno (SaaS) | Pago por página |

---

## [2026-06-16] Hito 2: Estructura del Modulo de Ingestión en Python

### Resumen del Trabajo Realizado
Se ha estructurado la carpeta `app/ingestion` definiendo clases abstractas, interfaces tipadas, stubs e importaciones seguras para toda la fase de ingesta de datos.

1. **Submódulos y Directorios Creados**:
   - `app/ingestion/parsers/`: Interfaces y adaptadores de parsing.
     - `base.py`: Clase abstracta `BaseParser` para estandarizar métodos de extracción de texto.
     - `pdf_parser.py`: Stubs de parseo para PDF (`DoclingPDFParser` y `LlamaParsePDFParser`).
     - `docx_parser.py`: Stubs de parseo para Word (`PandocDocxParser` y `DoclingDocxParser`).
   - `app/ingestion/chunking/`:
     - `splitter.py`: Contiene `ParentChildSplitter` y esquemas de salida tipo `ChunkPair` para la segmentación jerárquica.
   - `app/ingestion/metadata/`:
     - `extractor.py`: Contiene `MetadataExtractor` y el esquema tipado `IndustrialMetadata` para metadatos industriales (clearance, proyectos, versiones, etc.).
   - `app/ingestion/storage/`:
     - `vector_store.py`: Interfaz `VectorStoreManager` para interactuar con Qdrant.
     - `doc_store.py`: Interfaz `DocStoreManager` para interactuar con el almacén clave-valor de chunks padres.
   - `app/ingestion/sync/`:
     - `ledger.py`: Interfaz `IngestionLedger` para control de hashes SHA-256 e indexación incremental.
   - `app/ingestion/pipeline.py`: Clase central `IngestionPipeline` que actúa como orquestador general de los submódulos.

2. **Validación**:
   - Verificación sintáctica local y de importaciones mediante ruff exitosa (`import app.ingestion.pipeline`).

---

## [2026-06-16] Hito 3: Implementacion de Marker PDF Parser

### Resumen del Trabajo Realizado
Se ha integrado de forma funcional el parser de PDFs utilizando la libreria local `marker-pdf`.

1. **Instalacion de dependencias**:
   - Se instalo exitosamente `marker-pdf` en el entorno local (que instala dependencias clave como `torch`, `transformers`, `surya-ocr` y `pdftext`).

2. **Implementacion del Parser**:
   - [pdf_parser.py](file:///d:/PropuestaCanalYoutube/2026-06-16-RAG-Industrial/app/ingestion/parsers/pdf_parser.py): Se agrego la clase `MarkerPDFParser` heredando de `BaseParser`.
   - **Inicializacion Perezosa (Lazy Initialization)**: Para evitar retardos masivos en el arranque del sistema (debido a la importacion de librerias de Deep Learning como PyTorch), la inicializacion del convertidor `PdfConverter` y la carga en memoria de sus modelos neuronales (`create_model_dict`) se realiza de manera diferida unicamente cuando se invoca el metodo `parse` por primera vez.

3. **Configuracion del Pipeline**:
   - [pipeline.py](file:///d:/PropuestaCanalYoutube/2026-06-16-RAG-Industrial/app/ingestion/pipeline.py): Se configuro `IngestionPipeline` para usar `MarkerPDFParser` de manera predeterminada para el parseo de PDFs (`self.pdf_parser = MarkerPDFParser()`).

4. **Validacion**:
   - Verificacion de sintaxis e importacion ejecutada sin errores.

---

## [2026-06-16] Hito 4: Reinstalacion de PyTorch (GPU CUDA) y Prueba de Ingesta con Datasheet PDF

### Resumen del Trabajo Realizado
Se ha habilitado la aceleracion por hardware (GPU) para el procesamiento local de documentos de ingenieria mediante Marker y se valido su funcionamiento con un datasheet de 91 paginas.

1. **Inspeccion de Hardware y Verificacion de GPU**:
   - Se corroboro que el entorno de desarrollo cuenta con una tarjeta **NVIDIA GeForce RTX 3060 Ti** con **8 GB de VRAM** (de los cuales mas de 7 GB estaban libres).
   - Se detecto que la instalacion inicial de PyTorch era la compilada para CPU (`torch.cuda.is_available()` = `False`).

2. **Resolucion de Dependencias y Reinstalacion para CUDA**:
   - **PyTorch (CUDA 12.1)**: Se reinstalo `torch-2.5.1+cu121` utilizando la bandera `--no-deps` para actualizar unicamente la biblioteca de calculo numerico y evitar bloqueos por permisos en dependencias del sistema en uso (como `MarkupSafe`).
   - **Pydantic / typing-extensions**: Se actualizo `typing-extensions` a la version `4.15.0` para solucionar un error de importacion de la clase `Sentinel` por parte de Pydantic.
   - **Torchvision (CUDA 12.1)**: Se detecto un error al ejecutar Marker debido a que la version pre-existente de torchvision no coincidia con la nueva version de PyTorch (`RuntimeError: operator torchvision::nms does not exist`). Se soluciono instalando de forma limpia `torchvision-0.20.1+cu121` desde el indice de PyTorch de CUDA 12.1.
   - **Resultado**: La prueba de verificacion confirmo que CUDA paso a estar activo: `CUDA available: True` (NVIDIA GeForce RTX 3060 Ti).

3. **Prueba de Ingesta y Correccion de la API**:
   - Se creo el script de automatizacion [test_parse_pdf.py](file:///d:/PropuestaCanalYoutube/2026-06-16-RAG-Industrial/test_parse_pdf.py).
   - Durante las primeras corridas se detecto una discrepancia con el metodo de llamada de Marker (el convertidor no tiene el metodo `.convert()`). Se modifico la clase `MarkerPDFParser` en `pdf_parser.py` para invocar al convertidor directamente a traves de su metodo `__call__` (`converter(file_path)`).
   - El script ejecuto exitosamente la ingesta del datasheet de 91 paginas `data/AD4086_Datasheet.pdf` en aproximadamente 40 segundos.
   - Se genero con exito el archivo Markdown estructurado [AD4086_Datasheet.md](file:///d:/PropuestaCanalYoutube/2026-06-16-RAG-Industrial/data/AD4086_Datasheet.md) con 3101 lineas, preservando encabezados y las tablas de especificaciones tecnicas perfectamente ordenadas.

4. **Reorganizacion de Pruebas (Playground)**:
   - Se creo la carpeta [playground/](file:///d:/PropuestaCanalYoutube/2026-06-16-RAG-Industrial/playground) para alojar todos los scripts de prueba manuales.
   - Se movio el script de prueba a [playground/test_parse_pdf.py](file:///d:/PropuestaCanalYoutube/2026-06-16-RAG-Industrial/playground/test_parse_pdf.py) y se adapto su ruta de importacion (`sys.path.append`).
   - Se mejoro el script para manejar fallos de codificacion en consolas Windows mediante reemplazos seguros en caracteres no ASCII (como `►`).
   - Se valido su ejecucion en su nueva ubicacion con exito.

#### P4: ¿Cómo funciona Marker respecto al OCR y cuáles son las alternativas tradicionales sin IA ni OCR?
* **Respuesta**:
  
  ##### 1. ¿Usa OCR Marker?
  Sí, Marker es una solución híbrida orientada por Inteligencia Artificial que incluye OCR. Su pipeline funciona así:
  - **Detección de Layout (IA)**: Utiliza modelos de segmentación visual (Surya/YOLO) para identificar columnas, párrafos, tablas e imágenes.
  - **Extracción de Texto**: Si el PDF es digital, utiliza su librería `pdftext` para extraer el texto nativo por coordenadas. Si es escaneado, activa Surya OCR para digitalizar las imágenes.
  - **Reconocimiento de Fórmulas y Tablas (IA)**: Utiliza modelos de deep learning para traducir ecuaciones a LaTeX y reconstruir celdas de tablas.
  Requiere una instalación de ~2.5 GB de modelos locales y PyTorch con soporte de GPU (CUDA) para ser eficiente.

  ##### 2. Alternativas tradicionales sin IA ni OCR (CPU-only, muy ligeras):
  Si los PDFs de la planta son puramente digitales (no escaneados), se pueden usar librerías tradicionales que leen directamente el flujo de dibujo vectorial del PDF. Se ejecutan en milisegundos y no requieren GPU:
  - **pymupdf4llm**: Excelente para RAG. Convierte directamente el texto digital a Markdown respetando títulos, negritas y tablas sencillas sin usar IA. Pesa menos de 15 MB.
  - **pdfplumber**: El estándar heurístico para extraer tablas basándose en el análisis de intersección de líneas visuales de manera determinista.
  - **PyPDF**: Librería básica en Python para extraer texto crudo sin formato ni estructura de columnas.

#### P5: Consulta del usuario sobre las diferentes estrategias de chunking y su aplicabilidad al RAG Industrial
* **Respuesta**:
  A petición del usuario, se analizaron las principales estrategias de segmentación de texto (chunking) aplicadas al diseño de un RAG Industrial Enterprise:

  ##### 1. Fixed-Size Chunking (Por tamaño fijo de caracteres o tokens)
  - **Descripción**: Divide el texto en fragmentos de longitud fija (ej. 500 caracteres) con un solapamiento fijo (ej. 50 caracteres).
  - **Pros**: Muy simple de implementar y computacionalmente instantáneo.
  - **Contras**: Rompe oraciones a la mitad, destruye tablas de datos, y descontextualiza totalmente términos críticos en especificaciones técnicas de planta.

  ##### 2. Recursive Character Chunking (Por caracteres recursivos)
  - **Descripción**: Segmenta el texto usando una jerarquía de separadores (típicamente `\n\n`, `\n`, ` `, `""`) intentando mantener párrafos y oraciones completas unidas.
  - **Pros**: Respeta mejor la estructura de lectura del texto que el método fijo.
  - **Contras**: Sigue corriendo el riesgo de dividir tablas complejas o secciones técnicas indivisibles en el manual.

  ##### 3. Structural / Semantic Chunking (Por estructura del documento o semántica)
  - **Descripción**: Utiliza la sintaxis del parser (ej. etiquetas `#`, `##` de Markdown) para separar físicamente el documento en sus secciones y subsecciones lógicas, o usa modelos de embedding para detectar saltos semánticos entre oraciones.
  - **Pros**: Mantiene agrupada toda la información relacionada con un mismo título o tópico técnico.
  - **Contras**: Genera chunks de tamaño muy irregular (algunos demasiado largos, diluyendo el embedding, y otros de una sola línea).

  ##### 4. Hierarchical Chunking (Parent-Child / Desacoplado)
  - **Descripción**: Combina lo mejor de dos mundos:
    - Se segmenta el documento en fragmentos lógicos grandes (**Parents**: 1024-2048 tokens) para mantener el contexto completo.
    - Cada fragmento padre se divide en sub-fragmentos más pequeños (**Children**: 128-256 tokens) con overlap.
    - Se vectorizan e indexan únicamente los fragmentos hijos (para una búsqueda semántica de alta precisión en la Vector DB).
    - Al momento del Retrieval, si un hijo es seleccionado, se recupera e inyecta su chunk padre completo en el LLM desde un almacenamiento clave-valor persistente.
  - **Pros**: **El estándar Enterprise para RAG**. Evita diluir los embeddings de búsqueda sin privar al LLM del contexto completo y de advertencias técnicas circundantes.
  - **Contras**: Requiere gestionar dos bases de datos (Vector DB para hijos y Document Store para padres).

  ##### 5. Sentence Window Retrieval (Ventana de oraciones)
  - **Descripción**: Se indexan oraciones individuales. Al recuperar, se inyectan las oraciones seleccionadas expandiendo su contexto con $N$ oraciones anteriores y posteriores.
  - **Pros**: Gran precisión de búsqueda.
  - **Contras**: Dificulta la reconstrucción cuando la respuesta ideal reside en datos tabulares extensos.

  ##### Conclusión para nuestro RAG Industrial:
  Implementaremos la estrategia **Hierarchical (Parent-Child)** en combinación con segmentación **estructural de Markdown** (usando los encabezados identificados por Marker/LlamaParse) para garantizar la máxima fidelidad en el retrieval y evitar alucinaciones.

---

## [2026-06-16] Hito 5: Implementación del ParentChildSplitter (Chunking Jerárquico)

### Resumen del Trabajo Realizado
Se ha implementado y validado el núcleo del módulo de chunking jerárquico con la estrategia Parent-Child sobre el Markdown real del datasheet `AD4086_Datasheet.md` (91 páginas, 368.653 caracteres).

1. **Implementación de `ParentChildSplitter`** ([splitter.py](file:///d:/PropuestaCanalYoutube/2026-06-16-RAG-Industrial/app/ingestion/chunking/splitter.py)):
   - **Segmentación estructural por encabezados Markdown (H1-H3)**: El documento se divide primero por sus encabezados lógicos. Cada bloque de texto bajo un encabezado se convierte en un **Chunk Padre**, preservando la cabecera como contexto y metadato.
   - **Sliding Window para Chunks Padre demasiado largos**: Si una sección supera el `parent_size` (1500 chars por defecto), se subdivide a su vez en sub-padres con solapamiento (`parent_overlap=150`), sin perder continuidad de lectura.
   - **Sliding Window por respeto de palabras para Chunks Hijos**: Sobre cada Chunk Padre se aplica una ventana deslizante de `child_size=300` chars con `child_overlap=50`, ajustando los cortes al último espacio en blanco para no romper palabras.
   - **Enlazado mediante `parent_id`**: Cada Chunk Hijo lleva en sus metadatos el `id` del Chunk Padre del que proviene, habilitando la recuperación del contexto completo en el momento del Retrieval.
   - **Propagación de metadatos**: Tanto padres como hijos heredan los metadatos base del documento (`source`, `document_name`, `file_type`) y añaden metadatos propios (`chunk_type`, `section_heading`, `heading_level`, `parent_index`, `child_index`).

2. **Tipos de datos definidos** (dataclasses):
   - `ParentChunk`: Representa una sección lógica grande del documento con su encabezado.
   - `ChildChunk`: Fragmento indexable pequeño con puntero al padre.
   - `ChunkPair`: Agrupación de un padre con su lista de hijos.

3. **Script de test** ([playground/test_chunking.py](file:///d:/PropuestaCanalYoutube/2026-06-16-RAG-Industrial/playground/test_chunking.py)):
   - Carga el Markdown real del datasheet.
   - Instancia el splitter con los parámetros de producción.
   - Ejecuta el split y muestra estadísticas.
   - Valida la integridad de los chunks (padres no vacíos, hijos con `parent_id` válido, metadatos completos).

### Resultados de la Ejecución de Test (Documento: AD4086_Datasheet.md)

| Métrica | Valor |
| :--- | :--- |
| Caracteres totales del documento | 368.653 |
| Líneas totales | 3.100 |
| **Chunks PADRE generados** | **358** |
| **Chunks HIJO generados** | **1.622** |
| Longitud promedio de padre | 1.071 chars |
| Longitud promedio de hijo | 227 chars |
| Errores de validación | **0** |

### Parámetros de Producción Usados

| Parámetro | Valor | Descripción |
| :--- | :--- | :--- |
| `parent_size` | 1500 chars | Tamaño máximo del chunk padre |
| `parent_overlap` | 150 chars | Solapamiento entre padres consecutivos |
| `child_size` | 300 chars | Tamaño máximo del chunk hijo (indexado en VectorDB) |
| `child_overlap` | 50 chars | Solapamiento entre hijos consecutivos |
| `split_by_headings` | `True` | Segmentación estructural por encabezados Markdown H1-H3 |

---

#### P6: Análisis comparativo — Implementación con LangChain (Guía punto 2.3) vs. nuestra implementación propia

> *Pregunta planteada por el usuario al revisar el punto 2.3 de `Guia_Paso_a_Paso_RAG_Industrial.md`, que propone usar `MultiVectorRetriever` de LangChain como base del pipeline de ingestión.*

##### Código propuesto en la guía (LangChain)

```python
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
child_splitter  = RecursiveCharacterTextSplitter(chunk_size=200,  chunk_overlap=30)
retriever = MultiVectorRetriever(vectorstore=..., byte_store=..., id_key="parent_id")
```

##### ✅ Ventajas del enfoque LangChain

| Aspecto | Detalle |
| :--- | :--- |
| **Velocidad de prototipado** | `MultiVectorRetriever` + `LocalFileStore` encapsulan en ~20 líneas lo que nosotros hicimos manualmente. Ideal para una prueba de concepto rápida. |
| **Integración ecosistémica** | El `retriever` de LangChain encaja directamente con `ContextualCompressionRetriever` (reranker), `ConversationalRetrievalChain` y RAGAS sin adaptadores adicionales. |
| **DocStore abstraído** | El `ByteStore` serializa/deserializa los chunks padre automáticamente. En nuestro código, `DocStoreManager` aún tiene ese bloque pendiente de implementar. |
| **Stack de inferencia unificado** | `ChatOpenAI`, prompts, parsers de output y retrieval en el mismo ecosistema, sin necesidad de código puente. |

##### ❌ Desventajas de LangChain para nuestro caso de uso industrial

| Aspecto | Detalle |
| :--- | :--- |
| **Sin segmentación estructural** | `RecursiveCharacterTextSplitter` **no sabe nada de Markdown**. Cortará en el carácter N aunque esté a mitad de una fila de tabla o a mitad de un encabezado. Nuestro splitter primero segmenta por H1/H2/H3 y **luego** aplica sliding window dentro de cada sección. |
| **Acoplamiento fuerte al proveedor** | La guía usa `OpenAIEmbeddings` y `LocalFileStore`. Cambiar a embeddings locales (`BAAI/bge-m3`) o a Redis/PostgreSQL como DocStore requiere aprender la abstracción específica de LangChain para cada backend. |
| **Metadatos como caja negra** | La guía propaga `source`, `project`, `doc_type` manualmente campo a campo. Cualquier campo nuevo requiere editar la función. Nuestras `dataclasses` (`ParentChunk`, `ChildChunk`) definen el esquema de forma explícita y estáticamente tipada. |
| **Vendor lock-in indirecto** | `langchain_openai`, `langchain_cohere`, `langchain_community` son paquetes separados con versiones que rompen compatibilidad entre sí con frecuencia (problema similar al que ya vivimos con `torch` / `torchvision`). |
| **Sin conciencia de sección** | Los chunks padre de LangChain no saben a qué encabezado pertenecen. El `parent_id` es solo un UUID opaco. En nuestro código, el padre lleva `heading`, `heading_level` y `section_heading` — metadatos críticos para el pre-filtrado por sección técnica de la Fase 2. |
| **Testing difícil** | Un `MultiVectorRetriever` requiere instanciar VectorStore + ByteStore para cualquier test. Nuestro `ParentChildSplitter.split_document()` es una función pura: entra texto, salen dataclasses. Testeable sin infraestructura. |

##### ⚖️ Diferencia arquitectónica clave

```
Guía (LangChain):   Text ──► RecursiveCharacterTextSplitter ──► LangChain Document ──► MultiVectorRetriever
Nuestro enfoque:    Text ──► _split_by_headings() ──► _sliding_window() ──► ParentChunk/ChildChunk ──► VectorStore/DocStore
```

La diferencia fundamental es que `RecursiveCharacterTextSplitter` aplica la ventana deslizante sobre el **texto completo sin estructura**. Nosotros la aplicamos **dentro de cada sección ya delimitada por encabezados**. Esto garantiza que una tabla de especificaciones de la Sección 4.2 nunca se mezcle con texto de la Sección 4.3 en un mismo chunk padre.

##### 🔄 Patrones de LangChain que sí adoptamos

La guía valida dos decisiones de diseño que ya tenemos implementadas:

1. **El patrón `(parent_id → bytes)` del ByteStore**: Es exactamente lo que `DocStoreManager` debe implementar. LangChain usa `LocalFileStore` como PoC; nosotros usaremos Redis o PostgreSQL en producción, pero el contrato es el mismo.
2. **El `id_key` como enlace entre VectorStore y DocStore**: La forma en que LangChain enlaza hijos (en el VectorStore) con padres (en el ByteStore) mediante un campo de metadatos `parent_id` es idéntica a lo que ya implementamos en `ChildChunk.metadata["parent_id"]`. Esto valida que nuestro diseño es el correcto.

##### Conclusión

LangChain es superior para llegar rápido a una demo. Nuestra implementación propia es superior para producción industrial porque el splitter es consciente de la estructura del documento (Markdown H1-H3), los tipos de datos son explícitos y verificables en tiempo de desarrollo, y el sistema es totalmente testeable sin necesidad de infraestructura activa (Qdrant, Redis, etc.). El siguiente paso lógico es que nuestro `DocStoreManager` implemente el patrón `ByteStore` que la guía describe.

---

## [2026-06-16] Hito 6: Fase 2 — Metadatos, VectorStore (Qdrant) y Pipeline End-to-End

### Resumen del Trabajo Realizado

Se ha completado la Fase 2 del pipeline de ingesta conectando los `ChunkPair` jerárquicos con almacenamiento real: metadatos estructurados, persistencia de chunks padre en disco y vectorización + indexación de chunks hijo en Qdrant.

### Dependencias instaladas

```bash
pip install qdrant-client sentence-transformers langdetect
```

| Paquete | Versión | Uso |
| :--- | :--- | :--- |
| `qdrant-client` | 1.18.0 | Cliente Qdrant (modo embebido local + servidor remoto) |
| `sentence-transformers` | 5.5.1 | Modelo BAAI/bge-m3 para embeddings multilingüe |
| `langdetect` | 1.0.9 | Detección automática de idioma en modo heurístico |

### Bloque 1: MetadataExtractor ([extractor.py](file:///d:/PropuestaCanalYoutube/2026-06-16-RAG-Industrial/app/ingestion/metadata/extractor.py))

**Esquema `IndustrialMetadata`** — TypedDict con todos los campos requeridos:

| Campo | Tipo | Fuente | Descripción |
| :--- | :--- | :--- | :--- |
| `project_id` | `str` | `base_metadata` | Identificador del proyecto de I+D (RBAC) |
| `product_line` | `str` | `base_metadata` | Línea de producto o maquinaria |
| `doc_type` | `Literal` | **Heurístico** | Inferido del nombre del fichero (PRD, SOP, DATASHEET…) |
| `confidentiality` | `Literal` | `base_metadata` | Nivel de acceso (PUBLIC/INTERNAL/RESTRICTED/TOP_SECRET) |
| `version` | `str` | `base_metadata` | Versión del documento |
| `creation_timestamp` | `int` | auto | Unix epoch del momento de ingesta |
| `language` | `str` | **`langdetect`** | Idioma detectado automáticamente del texto |
| `source` | `str` | fichero | Ruta absoluta del origen |
| `document_name` | `str` | fichero | Nombre sin extensión |
| `section_heading` | `str\|None` | `ChunkPair` | Título de la sección Markdown |
| `heading_level` | `int\|None` | `ChunkPair` | Nivel H1/H2/H3 |
| `chunk_type` | `Literal` | `ChunkPair` | "parent" o "child" |
| `parent_id` | `str\|None` | `ChunkPair` | ID del padre (solo en hijos) |
| `parent_index` | `int` | `ChunkPair` | Posición del padre en el documento |
| `child_index` | `int\|None` | `ChunkPair` | Posición del hijo dentro de su padre |

**Modo heurístico** (`use_llm=False`, por defecto):
- `doc_type` → regex sobre el nombre del fichero (`"AD4086_Datasheet.pdf"` → `DATASHEET`).
- `language` → `langdetect` sobre los primeros 500 chars del chunk.
- Resto de campos → heredados de `base_metadata` o valores por defecto seguros.

**Modo LLM** (`use_llm=True`) → `NotImplementedError`, reservado para Fase 2 avanzada.

### Bloque 2: DocStoreManager ([doc_store.py](file:///d:/PropuestaCanalYoutube/2026-06-16-RAG-Industrial/app/ingestion/storage/doc_store.py))

**JSON File Store** local para chunks padre:

- Cada `ParentChunk` → fichero `storage_path/parents/{parent_id}.json`.
- Lookup O(1) por `parent_id` (nombre de fichero = ID).
- API: `save_parents()`, `get_parent()`, `exists()`, `delete_parent()`, `list_all_ids()`, `count()`.
- **Upgrade path a Redis**: sustituir operaciones de fichero por `redis.set()` / `redis.get()` sin cambiar la interfaz.

### Bloque 3: VectorStoreManager ([vector_store.py](file:///d:/PropuestaCanalYoutube/2026-06-16-RAG-Industrial/app/ingestion/storage/vector_store.py))

**Qdrant en modo embebido local** + embeddings **BAAI/bge-m3**:

| Parámetro | Valor | Justificación |
| :--- | :--- | :--- |
| Distancia | `COSINE` | Estándar para embeddings de texto normalizados |
| Dimensiones | `1024` | Dimensión nativa del modelo BAAI/bge-m3 |
| HNSW `m` | `16` | Equilibrio calidad/memoria para colecciones de miles de chunks |
| HNSW `ef_construct` | `100` | Alta exploración en construcción — mayor recall |
| Payload indexes | `project_id`, `doc_type`, `confidentiality` | Pre-filtrado RBAC sin escaneo total |

- Modelo **BAAI/bge-m3**: multilingüe ES+EN, 1024d, gratuito, ~2.2 GB (caché HuggingFace).
- Lazy init: el modelo se carga solo cuando se necesita por primera vez.
- Vectorización en **batches de 64** con `normalize_embeddings=True`.
- Upsert idempotente: re-indexar el mismo chunk no crea duplicados.
- **Upgrade path a producción**: `QdrantClient(url="http://qdrant:6333")` sin cambiar ningún otro código.

### Bloque 4: IngestionPipeline ([pipeline.py](file:///d:/PropuestaCanalYoutube/2026-06-16-RAG-Industrial/app/ingestion/pipeline.py))

`process_file()` implementado con el flujo de orquestación completo:

```
process_file(file_path, base_metadata)
  ├─ [1] PARSE    → Detecta extensión → MarkerPDFParser / PandocDocxParser
  ├─ [2] SPLIT    → ParentChildSplitter → List[ChunkPair]
  ├─ [3] ENRICH   → MetadataExtractor.enrich_chunk() sobre cada padre e hijo
  ├─ [4] STORE    → DocStoreManager.save_parents() → JSON files en disco
  ├─ [5] INDEX    → VectorStoreManager.add_child_chunks() → upsert en Qdrant
  └─ [6] REPORT   → Dict {n_parents, n_children, duration_seconds, status}
```

### Bloque 5: Test End-to-End ([playground/test_phase2.py](file:///d:/PropuestaCanalYoutube/2026-06-16-RAG-Industrial/playground/test_phase2.py))

6 checkpoints de validación:

| Checkpoint | Validación |
| :--- | :--- |
| `[1/6]` | Dependencias disponibles + PDF existe |
| `[2/6]` | `process_file()` retorna `status="ok"` con `n_parents > 0` y `n_children > 0` |
| `[3/6]` | DocStore tiene cobertura ≥ 95% de chunks padre |
| `[4/6]` | 3 búsquedas semánticas devuelven hits con `score > 0.3` |
| `[5/6]` | `parent_id` del mejor hit existe en DocStore y se recupera |
| `[6/6]` | Todos los payloads de Qdrant tienen los campos de metadatos obligatorios |

### Resultados del Test End-to-End (`test_phase2.py`)

El test se ejecutó con éxito utilizando el modelo de desarrollo local `all-MiniLM-L6-v2` (384 dimensiones) y la base de datos Qdrant embebida local. Todas las validaciones pasaron satisfactoriamente:

- **Fichero procesado**: `AD4086_Datasheet.pdf` (3.3 MB)
- **Chunks PADRE generados y guardados**: `358` (100% persistidos en `DocStoreManager`)
- **Chunks HIJO vectorizados e indexados**: `1622` (en Qdrant local)
- **Tiempo total optimizado**: `278.88 segundos` (incluyendo OCR completo y parseo de tablas de 91 páginas)
- **Mejor Score obtenido**: `0.6747` para la consulta `"ADC resolution noise performance"`
- **Búsqueda semántica e hidratación**: Recuperación exitosa del chunk padre `P-4e170c5e` de la sección `THEORY OF OPERATION` desde el ID enlazado en el payload del hit de Qdrant.
- **Integridad de metadatos**: Confirmado que el 100% de los resultados contienen los campos obligatorios del esquema `IndustrialMetadata`.

#### Optimizaciones de rendimiento aplicadas durante esta sesión:
1. **Bulk Upsert**: Modificación del método `add_child_chunks()` en `vector_store.py` para acumular todos los `PointStruct` en memoria y realizar una única llamada de inserción masiva a Qdrant en lugar de 26 llamadas (lotes de 64). Esto redujo a un solo commit de E/S en disco, previniendo bloqueos en sistemas de archivos locales Windows.
2. **Detección Única de Idioma**: Modificación de `pipeline.py` y `extractor.py` para invocar a `langdetect` una sola vez a nivel de documento completo (`raw_text`) en vez de 1.980 llamadas individuales por chunk. Esto eliminó el cuello de botella en CPU que tomaba más de 3 minutos de procesamiento inútil.

---

## [2026-06-16] Hito 7: Propuesta de Diseño para la Fase 3 (Retrieval Avanzado)

A petición del usuario, se ha elaborado y guardado el **Plan de Implementación** para la Fase 3 de la guía en [implementation_plan.md](file:///C:/Users/Francisco/.gemini/antigravity-ide/brain/a9e5d1c5-e9ff-45f2-8e90-d4aa43f2e490/implementation_plan.md). Este plan detalla la arquitectura para implementar búsqueda híbrida, fusión de rankings (RRF), re-ranking local (ms-marco-MiniLM) y query transformation (HyDE/Multi-query) de manera desacoplada y modular.





