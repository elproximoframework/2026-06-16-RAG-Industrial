Hoy vamos a terminar de crear nuestro sistema RAG Industrial y le vamos a dar un cerebro completo en 3 horas. Si recordáis el último vídeo, hicimos una locura: construimos el núcleo de un sistema RAG Industrial de grado Enterprise en menos de dos horas. Logramos que nuestra IA leyera manuales técnicos súper complejos y los metiera en una base de datos vectorial sin romper las tablas ni perder el contexto. Ya sabéis que en este rincón de internet nuestro objetivo es destripar el presente de la ingeniería para que podamos construir el futuro utilizando Inteligencia Artificial.

Pero seamos sinceros, lo que construimos fue un cerebro metido en un tarro de formol. No se podía hablar con él, no tenía una interfaz web, y si le preguntabas dos veces lo mismo, tardaba una eternidad en responder. Así que hoy vamos a terminar el trabajo.

Nos hemos puesto un reto de 3 horas de reloj para implementar las Fases 4, 5 y 6 de la guía maestra que nos generó nuestro agente de inteligencia artificial. Vamos a darle a este cerebro un enrutador inteligente, lo vamos a envolver en una API profesional con FastAPI, le vamos a meter una caché ultrarrápida, y como traca final, vamos a crear un "Juez de Inteligencia Artificial" usando el método RAGAS para que evalúe si nuestro sistema alucina o es seguro para una planta industrial.

Tres horas. Todo en local. Para lograr esto cuento con un compañero de equipo brutal: el agente Antigravity IDE. Y ojo, que quede claro que aquí la IA no hace el trabajo por mí mientras yo me tomo un café. Yo diseño la arquitectura principal y defino qué queremos conseguir; se lo presento a la IA para que lo analice y proponga optimizaciones, y luego yo me encargo de encajar las piezas y adaptarlas a nuestro entorno. Es un verdadero desarrollo en pareja donde la IA potencia mis ideas.

A nivel arquitectónico, lo que vamos a construir hoy es la capa lógica superior, es decir, el 'cerebro' que convierte a nuestra base de datos en una aplicación autónoma y segura. Empezaremos programando un enrutador inteligente ('Agentic Router'). Imagina este router como una recepcionista en un gran edificio de oficinas: cuando tú haces una pregunta, ella clasifica tu intención y decide a qué departamento enviarte. Si preguntas por el mantenimiento de una máquina, te manda por el flujo de manuales técnicos; si preguntas sobre recursos humanos, te desvía a la base de datos de contratos. Esto evita que la IA busque a lo ciego. Además, le acoplaremos un compresor de contexto. Cuando sacamos documentos de la base de datos, suelen tener mucha 'paja'. Este compresor leerá los documentos antes y recortará toda la información inútil, quedándose solo con los datos puros. Así, cuando le pasemos el texto final a nuestro modelo de IA (Gemini Flash), este no se saturará y nos dará respuestas mucho más directas.

Para que el sistema sea viable en un entorno de producción industrial real, y no solo un experimento de fin de semana, implementaremos una Caché Semántica. ¿Qué es esto? Básicamente es una memoria a corto plazo. Si un operario pregunta '¿Cuál es la presión de la válvula X?', la IA calcula la respuesta y la guarda en memoria. Si diez minutos después otro operario hace la misma pregunta, aunque use otras palabras, la Caché Semántica se da cuenta de que la intención es idéntica y le devuelve la respuesta guardada en milisegundos, ahorrándonos todo el coste computacional y de tiempo de volver a pensar la respuesta desde cero.

También crearemos un 'Ledger Incremental' respaldado por SQLite, que es como un libro de contabilidad automático que vigila nuestra carpeta de manuales. Si metes un PDF nuevo, él sabe que solo tiene que procesar ese archivo, sin tener que tragarse de nuevo los 5.000 PDFs que ya habíamos analizado ayer. Por último, cerraremos el círculo empaquetándolo todo en una API web con FastAPI (la ventanilla para que otras apps se comuniquen con nuestro sistema) e inyectándole un 'Juez IA' basado en el framework RAGAS. Este juez es espectacular: es otra Inteligencia Artificial independiente que se encarga exclusivamente de vigilar a nuestro sistema principal, auditando sistemáticamente sus respuestas para asegurarse de que no se ha inventado nada ('alucinaciones') y evaluando que el contexto entregado al usuario sea veraz.

¡El reloj empieza a contar ya! Vamos al barro.

 Arrancamos con la Fase 4: La Orquestación Agéntica.
Hasta ahora teníamos un buscador muy bueno, pero necesitábamos que el sistema pensara antes de buscar. Le pido a Antigravity que me programe un "Agentic Router", que básicamente es un guardia de tráfico. Si un operario pregunta por una alarma, el router manda la consulta por un carril rápido. Si un ingeniero pregunta por patentes, lo manda por un carril de análisis profundo.

 Además, la IA me implementa un "Compresor de Contexto". Esto es vital, porque si le metes a un modelo de lenguaje 50 páginas de golpe, se le olvida lo que hay en el medio. Este compresor coge el texto, lo lee, y recorta toda la paja dejando solo las oraciones que responden a la pregunta. Todo esto conectado a Gemini 1.5 Flash, configurado con temperatura cero absoluta para que no se invente ni una sola coma.

Todo pinta espectacular en la pantalla. Le digo a la IA: "Ejecuta el test, vamos a preguntarle por la funcionalidad de los pines B4 y B5 de nuestro datasheet". Le doy al play y... ¡PUM! Pantallazo de error en la consola.

Mirad lo que me escupe esto: OSError 1455: El archivo de paginación es demasiado pequeño. Y justo debajo: CUDA out of memory.

Resulta que mi ordenador ha colapsado. La IA intentó cargar el modelo de compresión en la memoria RAM, pero yo, en mi infinita sabiduría, había dejado corriendo en segundo plano unos contenedores Docker entrenando un modelo de visión artificial YOLOv10 del proyecto anterior. El sistema operativo ha dicho "hasta aquí hemos llegado, chaval" y ha matado el proceso. Soy un mandao, sí, pero a veces el mandao tiene la culpa.

Respiro hondo. Cierro todos los Dockers, limpio la memoria de la tarjeta gráfica, y vuelvo a lanzar la consulta. Silencio en la consola... y de repente, ¡bum! Aparece la respuesta perfecta: "Los pines B4 y B5 corresponden a las señales DCO y su funcionalidad es salida de reloj". Y lo mejor, al final de la frase, me pone la cita exacta del documento y la página. El subidón de dopamina que te da ver esto funcionar no tiene precio.

Llevamos una hora. Entramos en el "Grind", el trabajo duro. Fase 5: Despliegue y Caché.

No podemos tener este sistema corriendo en scripts sueltos, así que le pido a Antigravity que envuelva todo en FastAPI. Para los que no estéis metidos en backend, FastAPI es como construirle una ventanilla de atención al cliente a nuestro código. Pero aquí viene la magia que me propone la IA: en lugar de cargar los pesados modelos de IA cada vez que alguien pregunta algo, los cargamos una sola vez al arrancar el servidor.

Y ahora quiero que penséis un poco... En una fábrica, si una máquina falla, tres operarios distintos van a preguntar lo mismo en el chat a lo largo del día. ¿Tiene sentido gastar tiempo y dinero en que la IA procese la misma pregunta tres veces? No.

Así que Antigravity me programa una Caché Semántica. Si la pregunta tiene un 95% de similitud con algo que ya se ha preguntado, el sistema ni siquiera despierta a Gemini; te escupe la respuesta guardada. Hacemos la prueba en pantalla: la primera consulta tarda 23 segundos. Hago la misma consulta otra vez y... ¡16 milisegundos! Ha pasado de tardar medio minuto a ser instantáneo. Magia pura.

 Pero claro, la alegría dura poco. Queda una hora y media y entramos en la crisis mental del vídeo.

 Le pido a la IA que me monte el "Ledger Incremental". Esto es una base de datos SQLite que vigila la carpeta de manuales. Si metes un PDF nuevo, lo procesa. Si no ha cambiado, lo ignora. Así no reindexamos miles de páginas a lo tonto.

Le meto un PDF nuevo de prueba, el AD9446. El sistema detecta el archivo, llama a la librería Marker para leer el PDF usando la tarjeta gráfica y... ¡OTRA VEZ EL ERROR! WinError 1455.

Me quiero arrancar los pelos. Resulta que la librería Marker intenta cargar una librería de PyTorch que pesa 3.5 Gigabytes de golpe. Mi Windows, que ya tiene FastAPI y Qdrant abiertos, no tiene suficiente memoria virtual en el disco duro y aborta el programa violentamente.

Me pongo a investigar con Antigravity. Intentamos limitar los "workers", intentamos aislar el proceso, la IA me escribe scripts de diagnóstico súper complejos... y nada. Windows no me deja. El reloj sigue bajando. Quedan 45 minutos.

Antigravity, viendo mi desesperación, me da dos opciones: o reinicio el ordenador, entro a la BIOS, reconfiguro la paginación de Windows y pierdo media hora... o usamos un "atajo de desarrollo" que consiste en pre-parsear el documento a texto plano para engañar al sistema y que no cargue PyTorch. Como el tiempo apremia, tomamos el atajo. El test pasa en 10 segundos. Hemos sobrevivido, pero me apunto arreglar esto de la RAM para el futuro.

Nos quedan 30 minutos. La batalla final. Fase 6: El Framework RAGAS.

No puedes llevar un sistema de Inteligencia Artificial a una fábrica sin pasar una auditoría. Para eso existe RAGAS, una librería que usa a un modelo de lenguaje (en este caso Gemini) para actuar como un juez implacable y evaluar a nuestro propio sistema.

Preparamos un "Golden Dataset", un archivo con 10 preguntas trampa súper difíciles y sus respuestas correctas. Le damos al play para que el juez evalúe y... ¡Error de Python!

La librería RAGAS tiene un bug interno con los embeddings de Google. Fijaos en la consola, dice que el objeto no tiene el atributo embed_query. La IA de Antigravity se pone el traje de hacker y hace lo que en programación se llama un "monkeypatch", básicamente ponerle cinta americana digital al código de la librería de terceros para forzarla a funcionar.

Volvemos a ejecutar. ¡Otro error! Ahora RAGAS no sabe leer sus propios resultados y da un fallo con los DataFrames de Pandas. Antigravity vuelve a meterse al barro, reescribe la forma en la que extraemos las métricas y cruzamos los dedos.

Quedan 5 minutos. La consola empieza a escupir barras de progreso. El Juez IA está evaluando las respuestas. Evalúa la Fidelidad, la Relevancia, la Precisión del Contexto...

¡Tiempo! El test termina. Y aquí tenéis los resultados en pantalla.

¿Hemos aprobado? Pues... la consola nos ha escupido una alerta roja gigante: CRITICAL WARNING: Despliegue abortado.

El sistema exigía un 95% de fidelidad (cero alucinaciones) y hemos sacado un 70%. Hemos suspendido. Pero, y aquí viene lo interesante, ¿por qué hemos suspendido?

Analizando el CSV de resultados con la IA, nos damos cuenta de algo fascinante. Yo le había puesto preguntas trampa sobre máquinas que NO estaban en los documentos. Nuestro sistema RAG hizo exactamente lo que le programamos: respondió "INFORMACIÓN NO DISPONIBLE EN EL CORPUS DE SEGURIDAD". Prefirió callar antes que inventar. ¡Eso es perfecto para la industria! Pero el Juez de RAGAS, al ver que la respuesta no se basaba en el texto recuperado (porque no había texto), le cascó un cero en fidelidad a esas preguntas, hundiendo la nota media.

Además, vimos que la "Precisión del Contexto" fue baja, lo que significa que a veces nuestro buscador no lograba encontrar las tablas de especificaciones en la primera página de resultados.

Y mirad, quiero que reflexionéis sobre esto. Hace un año, montar un servidor FastAPI asíncrono, con caché semántica en Qdrant, un sistema de sincronización incremental en SQLite y un pipeline de evaluación automatizada con LLMs como jueces... habría sido el trabajo de un mes para un equipo entero de backend. Hoy, con un agente como Antigravity IDE, lo hemos levantado en 3 horas.

Sí, hemos tenido que pelearnos con la memoria de Windows, hemos tenido que parchear librerías rotas, y al final, nuestro propio sistema de seguridad nos ha bloqueado el paso a producción porque somos demasiado estrictos. Pero así es la ingeniería real. No es un camino de rosas, es iterar, fallar, medir y mejorar.

El código está ahí y funciona maravillosamente, pero ahora sabemos exactamente dónde están sus puntos débiles. En el próximo vídeo, vamos a arreglar estos defectos de búsqueda, y vamos a meter todo este monstruo dentro de contenedores Docker para desplegarlo en producción con integración continua en GitHub Actions.

¿Queréis ver cómo llevamos este proyecto al siguiente nivel y lo subimos a la nube? Dejádmelo en los comentarios. Y ya sabéis, si os ha gustado sufrir conmigo hoy en las trincheras del código, reventad el botón de like, suscribíos para no perderos la puesta en producción, y nos vemos en el próximo vídeo construyendo el futuro. ¡Hasta la próxima!

(Cambio de plano, cámara en mano, un poco a oscuras)

Oye, una cosa rápida... ¿Os acordáis de que os dije que Antigravity era un genio? Pues resulta que en uno de los scripts automáticos para subir el código a GitHub, me dejó mi API Key de Google y mi token personal escritos en texto plano. He tenido que hacer un git reset de emergencia y reescribir el historial a mano antes de que algún bot me robara la cuenta. Si es que... mucha inteligencia artificial, pero al final el que tiene que fregar los platos siempre soy yo. ¡Chao!
