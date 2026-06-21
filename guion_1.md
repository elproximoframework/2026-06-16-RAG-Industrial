En este vídeo voy a construir el núcleo de un sistema RAG, es decir, un Retrieval-Augmented Generation, pero no uno cualquiera para hacerle preguntas a un PDF de recetas. No. Vamos a intentar crear un RAG Industrial de grado Enterprise en menos de dos horas. Hoy tenemos un reto que, os confieso, me ha quitado un poco el sueño.

¿Por qué industrial? Porque si un chatbot de atención al cliente alucina, te da un código de descuento que no existe y te ríes. Pero si un sistema en una planta de fabricación alucina y le dice a un operario que el límite de presión de una válvula es de 500 bares en lugar de 50, tenemos un accidente grave o una línea de producción reventada. Aquí la precisión tiene que ser absoluta.

Para lograr esto, no estoy solo. Voy a usar nuestra herramienta estrella, nuestro agente de inteligencia artificial: Antigravity IDE. De hecho, la hoja de ruta que vamos a seguir hoy nace de un curso completo y espectacular que nos dio el propio agente de Antigravity sobre arquitecturas Enterprise. Es una guía paso a paso masiva. Por tiempo, en el vídeo de hoy vamos a implementar las tres primeras fases: Ingestión, Metadatos y Recuperación Híbrida. El resto del sistema, los agentes y la generación, lo dejaremos para un vídeo futuro.

El reloj empieza a contar ya. Dos horas. En esta locura me acompaña nuestra herramienta estrella: el agente Antigravity IDE. Pero no os confundáis, aquí el humano sigue al mando. Yo pongo la visión, el concepto y la arquitectura inicial sobre la mesa. A partir de ahí, entramos en una partida de ping-pong con la IA: ella analiza mi propuesta, me sugiere mejoras brutales de diseño, y yo las adapto a la realidad del RAG Industrial. Básicamente, trabajamos codo con codo para construir esto pieza a pieza.

Antes de arrancar de lleno, veamos la arquitectura técnica. Un sistema RAG (Generación Aumentada por Recuperación) consiste en darle a una IA documentos privados para que los lea antes de responder, evitando así que se invente cosas. Pero un RAG de grado industrial requiere una precisión extrema, por lo que el clásico 'cortar texto y buscar palabras' no nos sirve. Nuestra arquitectura se dividirá hoy en tres grandes fases.

En la fase de ingestión, usaremos modelos de visión computacional y OCR profundo con la librería Marker para extraer texto y tablas complejas de manuales técnicos en PDF. Para que lo entendáis, en vez de simplemente intentar 'leer' el texto del PDF, lo que hace el OCR es mirar el PDF como si fuera una imagen, igual que hacemos los humanos, y reconocer dónde hay una tabla, dónde hay un título y dónde hay un pie de página para no mezclar las cosas. Y todo esto lo ejecutaremos acelerado por hardware en nuestra tarjeta gráfica.

A continuación, implementaremos un segmentador jerárquico ('Parent-Child Splitter'). Normalmente los RAGs cortan los documentos a lo bruto cada 500 palabras, partiendo frases por la mitad. Nuestro segmentador inteligente dividirá los documentos manteniendo la cohesión semántica: separará capítulos grandes ('padres') en párrafos lógicos ('hijos') sin perder la relación entre ellos. Almacenaremos estos datos en Qdrant, una base de datos vectorial ultrarrápida. Una base de datos vectorial no guarda el texto letra a letra, sino que lo convierte en coordenadas matemáticas en el espacio. Así, cuando buscamos algo, la IA busca frases que estén matemáticamente cerca, es decir, que signifiquen lo mismo aunque usen palabras distintas.

Finalmente, montaremos un sistema de recuperación híbrido. Imagina que es como pescar con dos redes distintas a la vez: por un lado hacemos una búsqueda vectorial para encontrar conceptos e ideas similares (pesca semántica), y por el otro cruzamos eso con un motor BM25 en memoria RAM, que es un algoritmo clásico y rapidísimo para buscar palabras clave exactas (por si estamos buscando el código exacto del número de serie de una válvula). Los resultados de ambos motores se fusionarán y pasarán por un último filtro llamado Cross-Encoder, que es como un revisor humano súper estricto: leerá los documentos encontrados y los reordenará uno a uno, para asegurar que solo le pasamos a nuestra IA el contexto absolutamente más relevante y descartamos la basura.

Vamos al lío.

Lo primero es lo primero. Minuto uno. Le pido a Antigravity IDE que me monte la base del proyecto en Python. Quiero un repositorio con su estructura, sus tests, y una integración continua en GitHub Actions usando Ruff y Pytest. Y, por supuesto, un script automático para crear el repositorio en GitHub y subir las ramas.

Esto que estáis viendo en pantalla es pura magia. En cuestión de segundos, la IA me escupe toda la estructura de carpetas y un script llamado setup_github.py. Yo me froto las manos, le doy a ejecutar en mi terminal de Windows y... ¡PUM! Primer en la frente.

La consola me escupe un error gigante: "UnicodeEncodeError". Resulta que a la IA le pareció muy bonito poner emojis y caracteres especiales en los logs del script, y la consola de Windows ha dicho que esos dibujitos no los procesa. Vale, se lo digo a Antigravity, me lo cambia a formato texto aburrido ASCII, y vuelvo a ejecutar.

Parece que va bien, inicializa Git, hace el commit, intenta subirlo a GitHub y... ¡PUM otra vez! GitHub me bloquea el push con una alerta roja de "Push Protection". ¿Qué ha pasado? Pues que mi queridísima y avanzadísima IA, en su infinita sabiduría, había puesto mi token secreto de GitHub directamente escrito dentro del código del script. Y claro, al intentar subir ese archivo al repositorio público, GitHub me ha cortado el grifo por seguridad.

A veces la inteligencia artificial tiene tela, os lo digo de verdad. Así que me toca meterme al barro. Borro la carpeta oculta de Git a mano para destruir el historial, meto el script en el archivo gitignore para que no se suba nunca, y repito el proceso. Ahora sí, repositorio creado, reglas de protección activadas y CI funcionando. Llevamos veinte minutos y ya hemos sudado.

Entramos en el "Grind", el desarrollo real. Fase 1: Ingestión de datos.
Tenemos un PDF de 91 páginas, el datasheet de un conversor analógico-digital, lleno de tablas de ingeniería, tolerancias y fórmulas. Le pregunto a Antigravity qué usamos para extraer esto, porque un lector de PDF normal te destroza las tablas y te las convierte en una sopa de letras inservible.

La IA me hace un análisis brutal en pantalla. Me compara Docling de IBM, PyMuPDF y Marker. Me recomienda usar Marker, porque utiliza modelos de visión artificial y OCR basados en redes neuronales para entender el "layout" de la página y reconstruir las tablas perfectamente en formato Markdown. Le digo que adelante.

Y aquí viene un concepto clave que quiero que penséis un poco. ¿Cómo divides un manual técnico de 100 páginas para meterlo en una base de datos vectorial sin romper una tabla por la mitad o dejar una advertencia de peligro separada de su contexto?

La IA me explica que usar LangChain con su cortador de texto por defecto es un error en la industria, porque corta por número de caracteres y no entiende la estructura. En su lugar, Antigravity me programa desde cero un "Parent-Child Splitter", un segmentador jerárquico. Primero, lee los títulos H1, H2 y H3 del Markdown. Cada sección completa es un "Padre", un bloque grande de texto. Luego, divide ese padre en trocitos pequeños llamados "Hijos". Los hijos van a la base de datos vectorial para que la búsqueda sea ultra precisa, pero cuando encontramos un hijo, el sistema recupera al Padre completo para que el modelo de lenguaje tenga todo el contexto técnico. Es una genialidad.

Pero claro, la teoría es preciosa hasta que chocas con la realidad del hardware. Entramos en la crisis mental del reto. Queda una hora y cuarto.

Marker necesita ejecutarse en mi tarjeta gráfica, una RTX 3060 Ti, para ir rápido. Le digo a la IA que instale las dependencias. Lo hace, ejecuto el test y veo que va a pedales. El procesador está al cien por cien y la gráfica durmiendo. Antigravity instaló la versión de PyTorch para CPU.

No pasa nada, respiro hondo. Le digo: "Instala la versión de CUDA 12.1 para usar la GPU". Lo hace. Vuelvo a ejecutar. Ahora me salta un error de C++ diciendo que "torchvision" no es compatible. Resulta que las versiones chocan. La IA lo arregla forzando la reinstalación.

Vuelvo a ejecutar. Otro error. Ahora la librería Pydantic se queja de un módulo llamado "typing-extensions". La IA lo actualiza.

Vuelvo a ejecutar. Y aquí el infierno. Un error de seguridad brutal. Resulta que la librería "transformers" ha metido un bloqueo hace unos días por una vulnerabilidad de seguridad que exige tener PyTorch 2.6. ¡Pero la versión de CUDA que necesitamos usa PyTorch 2.5.1!

Yo no sé vosotros, pero ver a la IA pelearse contra un infierno de dependencias de Python es fascinante y desesperante a partes iguales. Antigravity intenta hacer un downgrade de la librería. Falla. Intenta forzar el uso de un formato llamado "safetensors". Falla, porque Windows necesita que actives el "Modo Desarrollador" para crear enlaces simbólicos en el disco duro y descargar el modelo BAAI/bge-m3.

El reloj sigue bajando. Quedan 45 minutos y mi cabeza está a punto de explotar. Le digo a la IA: "Busca una alternativa, sácame de este barro". Y Antigravity, en un destello de brillantez, me dice: "Vale, dejamos el modelo pesado para producción. Para que puedas desarrollar ahora mismo, te voy a inyectar un modelo de embeddings mucho más ligero, el all-MiniLM-L6-v2, que ya está en formato nativo seguro y no da error de symlinks en Windows".

Cambia dos líneas de código, ejecuto el script y... silencio. La consola empieza a escupir barras de progreso. La GPU se pone a zumbar. ¡Funciona! El chute de dopamina que te da cuando el código compila después de una hora de peleas no está pagado. En 40 segundos, Marker se lee las 91 páginas, entiende las tablas y me genera un Markdown perfecto.

Superada la crisis, entramos en la recta final. Quedan 30 minutos. Fase 2 y Fase 3. El Despliegue de la lógica.

Le pido a Antigravity que me monte la base de datos vectorial usando Qdrant en local y que guarde los "Chunks Padres" en archivos JSON en mi disco duro. Además, le pido que extraiga metadatos: de qué proyecto es el documento, qué nivel de confidencialidad tiene, en qué idioma está. Todo esto es vital para que un ingeniero no vea documentos de un proyecto secreto al que no tiene acceso.

Ejecutamos el test completo de la Fase 2 y noto que tarda muchísimo, casi cinco minutos. Miro los logs con la IA y nos damos cuenta de dos cuellos de botella absurdos. Primero, Qdrant estaba guardando en el disco duro de Windows fragmento por fragmento, haciendo 26 escrituras separadas. Segundo, la librería de detección de idioma estaba analizando si el texto era español o inglés... ¡casi dos mil veces!, una vez por cada trocito de texto.

Le digo a Antigravity: "Optimiza esto, soy un mandao pero no tengo todo el día". La IA reescribe el código para hacer un "Bulk Upsert", es decir, subir todos los vectores de golpe a la base de datos en una sola operación, y cambia la lógica para detectar el idioma una sola vez al principio del documento. Volvemos a ejecutar y el tiempo cae en picado. Eficiencia pura.

Nos quedan 15 minutos. Fase 3. La recuperación avanzada o Retrieval Híbrido.
En la industria, si buscas "válvula de presión", la búsqueda semántica vectorial es genial. Pero si buscas el código de error exacto "ERR-404", los vectores a veces fallan porque no entienden bien los números de serie. Necesitamos búsqueda léxica tradicional, palabras clave exactas.

Le pido a Antigravity que me integre BM25, el algoritmo clásico. Pero para evitar que Windows me vuelva a dar errores pidiendo compiladores de C++, la IA me programa un motor BM25 desde cero, en Python puro, que se carga en la memoria RAM en menos de diez milisegundos. Es una locura ver cómo te escribe un motor de búsqueda matemático de la nada.

Ahora tenemos dos listas de resultados: los de Qdrant y los de BM25. La IA me implementa un algoritmo llamado Reciprocal Rank Fusion para fusionar ambas listas y quedarse con lo mejor de los dos mundos.

Y para rematar, la guinda del pastel: El Re-ranking. Tomamos los mejores resultados y se los pasamos a un modelo llamado Cross-Encoder. Es un modelo pequeñito, de solo 90 megas, que analiza palabra por palabra si la pregunta del usuario realmente tiene sentido con el texto encontrado.

Quedan tres minutos en el reloj. Le doy al botón de ejecutar el test final, el "test_retrieval.py".

La consola se ilumina. Veo cómo genera las variantes de la pregunta, cómo Qdrant busca los vectores, cómo el BM25 puro en Python busca las palabras clave, cómo se fusionan los resultados, y cómo el Cross-Encoder reordena todo. Y ahí está. En pantalla. El sistema me devuelve exactamente el ID del "Chunk Padre" que contiene la sección "Theory of Operation" con las especificaciones de ruido del ADC AD4086. Con sus metadatos, sus citas y su contexto completo.

¡Tiempo! Paramos el reloj.

Mirad lo que se ha visto hoy. Quiero que reflexionéis sobre esto. Hace tan solo un año, montar un segmentador jerárquico personalizado, escribir un motor BM25 desde cero para esquivar errores de Windows, lidiar con el infierno de dependencias de CUDA y PyTorch, y montar un pipeline de búsqueda híbrida con fusión de rankings y re-evaluación por Cross-Encoder... esto habría sido el trabajo de un equipo de ingenieros durante semanas enteras.

Hoy, gracias a tener un agente como Antigravity IDE trabajando codo con codo conmigo, ha sido una sesión intensa de "pair-programming" de menos de dos horas. Sí, ha habido bugs, frustración y momentos de querer tirar el ordenador por la ventana. Pero esa es la realidad del desarrollo. La IA no hace magia pulsando un botón, la IA es una herramienta bestial que, si sabes guiarla y entiendes la arquitectura que quieres montar, te da superpoderes.

El núcleo de nuestro RAG Industrial está vivo y es ultra preciso. Pero nos falta la mitad del cerebro. En el próximo vídeo abordaremos la Fase 4: vamos a meter agentes enrutadores, compresión de contexto y la generación final con modelos de lenguaje estrictos que no alucinen y que citen sus fuentes.

¿Queréis ver cómo conectamos este motor de búsqueda a un LLM para que responda como un ingeniero jefe? Dejádmelo en los comentarios. Y ya sabéis, si os ha gustado meteros en el barro técnico conmigo hoy, reventad el botón de like, suscribíos para no perderos la segunda parte de este reto, y nos vemos en el próximo vídeo construyendo el futuro. ¡Hasta la próxima!

...
(Silencio breve, cambio de plano más informal)
Oye, por cierto... acabo de darme cuenta de que el ordenador suena como un avión a punto de despegar. Resulta que el script de pruebas terminó, pero la IA no programó que se liberara la memoria VRAM de la gráfica, y tengo el modelo de 2 gigas ahí tostándose a fuego lento por puro TOC. Voy a matar el proceso antes de que salga ardiendo. Ahora sí, ¡chao!
