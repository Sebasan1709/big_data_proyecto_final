# Extracción Inteligente de Conocimiento en Audiencias Legales: Dashboard de Storytelling y Análisis de Grafos

> Proyecto final para la materia de **Big Data** — **Maestría en Inteligencia de Negocios**, Universidad Externado de Colombia.

---

## Tabla de Contenido

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Arquitectura y Pipeline de Datos](#arquitectura-y-pipeline-de-datos)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Retos y Aprendizajes](#retos-y-aprendizajes)
5. [Instalación y Configuración](#instalación-y-configuración)
6. [Cómo utilizar el Proyecto](#cómo-utilizar-el-proyecto)
7. [Créditos](#créditos)

---

## Descripción del Proyecto

La aplicación procesa la audiencia del **Tribunal Superior de Bogotá** (Radicado: `110016721202000054`) sobre un caso de acceso carnal violento agravado. El sistema convierte el lenguaje natural hablado en una estructura de red que permite **reducir el tiempo de revisión manual de videos por parte de abogados en más de un 80%**.

El objetivo principal es transformar una audiencia judicial en video (de larga duración) en un ecosistema de datos accionables, culminando en un dashboard interactivo que narra los hechos, actores y la sentencia del caso mediante técnicas avanzadas de NLP y bases de datos de grafos.

---

## Arquitectura y Pipeline de Datos

El flujo de trabajo se divide en **8 etapas críticas** contenidas en los scripts del repositorio:

| # | Script | Descripción |
|---|--------|-------------|
| 1 | `extract_audio.py` | Conversión del video original a formato `.wav` optimizado. |
| 2 | `split_audio.py` | Partición del audio en bloques de 3 minutos para evitar colapsos de memoria. |
| 3 | `transcribe_chunks_medium.py` | Transcripción automática con WhisperModel (Medium). |
| 4 | `merge_transcripts.py` | Unión de los fragmentos transcritos en un único documento. |
| 5 | `extract_entities.py` | NER complementario: identificación de Personas, Lugares, Organizaciones y Delitos → `.txt`. |
| 6 | `extract_relations.py` | Generación de vínculos entre entidades (quién hizo qué a quién) → `.csv`. |
| 7 | *(Neo4j)* | Carga en base de datos de grafos: nodos y relaciones del caso penal. |
| 8 | `dashboard.py` | Interfaz Streamlit con narrativa por capítulos (Actores, Hechos, Investigación, Sentencia). |
| 9 | `api.py` | Servicio FastAPI para consultas programáticas a la base de datos de grafos. |

---

## Tecnologías Utilizadas

| Tecnología | Uso |
|---|---|
| **Python 3.11+** | Lenguaje base, gestión de dependencias con Poetry |
| **Faster-Whisper (Medium)** | Transcripción de audio de alta precisión |
| **spaCy (`es_core_news_lg`)** | Procesamiento de lenguaje natural y NER |
| **Neo4j** | Almacenamiento y consulta de grafos complejos |
| **Streamlit** | Visualización y storytelling de datos |
| **FastAPI** | Exposición de endpoints para integración |
| **Claude** | Refinamiento de las relaciones |
| **FFmpeg** | Procesamiento multimedia |

---

## Retos y Aprendizajes

- **Gestión de Memoria:** Incluso con 32 GB de RAM, el procesamiento de audios largos generaba errores. Se implementó una fragmentación estricta de archivos `.wav` y `.txt` para garantizar la estabilidad.

- **Procesamiento por Lotes (Batching):** Se ejecutó el pipeline en lotes controlados para probar nuevas funcionalidades sin comprometer el flujo completo de datos.

- **Especialización Legal:** Los modelos base de spaCy presentaban dificultades con verbos jurídicos complejos. Se requirió refinamiento con LLMs (vía API y finalmente GPT) para obtener precisión en las relaciones extraídas.

- **Selección del Modelo Whisper:** Las versiones *Base* y *Small* generaban baja calidad gramatical. El modelo **Medium** mejoró los resultados, con un tiempo de procesamiento aproximado de 2 horas, pero no se integró como insumo final para la base de Grafos.

---

## Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/Sebasan1709/big_data_proyecto_final.git
cd big_data_proyecto_final
```

### 2. Instalar Poetry

Si aún no lo tienes instalado, sigue las [instrucciones oficiales de Poetry](https://python-poetry.org/docs/#installation).

### 3. Instalar las dependencias del proyecto

Desde la raíz del repositorio (donde se encuentra `pyproject.toml`), ejecuta:

```bash
poetry install
```

### 4. Descargar el modelo de lenguaje de spaCy

```bash
python -m spacy download es_core_news_lg
```

> **Nota:** El modelo `lg` (Large) es indispensable por su precisión en términos legales y nombres propios.

### 5. Instalar FFmpeg

- **Windows:** Descarga desde [FFmpeg Official Builds](https://ffmpeg.org/download.html), descomprime y añade la carpeta `/bin` a las variables de entorno (`PATH`).
- **Linux:** `sudo apt install ffmpeg`
- **Mac:** `brew install ffmpeg`

---

## Cómo utilizar el Proyecto

### Acceso a los Datos Crudos

Por motivos de peso y administración, el video original no se encuentra en el repositorio.

1. **Descargar video:** Solicita acceso en este [Enlace de Google Drive](https://drive.google.com/file/d/1hVNq3TAgvUMTLz0lBVPf-xSkAT6mlkP6/view?usp=sharing).
2. **Ubicación:** Una vez descargado, colócalo en: `data/raw_videos/video_audiencia.mp4`.

### Ejecución del Pipeline

Ejecuta los scripts **en el siguiente orden**:

```bash
# 1. Extraer audio del video
python extract_audio.py

# 2. Partir el audio en chunks de 3 minutos
python split_audio.py

# 3. Transcripción con modelo Medium
python transcribe_chunks_medium.py

# 4. Unir los fragmentos transcritos
python merge_transcripts.py

# 5. Extracción de entidades (ejecutar ambos) → guardado en TXT
python extract_entities.py

# 6. Extracción de relaciones → guardado en CSV
python extract_relations.py
```

### Lanzar el Dashboard

```bash
streamlit run dashboard.py
```

### Lanzar la API

```bash
python api.py
```

---

## Créditos

Proyecto desarrollado como trabajo final para la materia de **Big Data** de la **Maestría en Inteligencia de Negocios** en la **Universidad Externado de Colombia**.

| Integrante | GitHub |
|---|---|
| Cristina Berrío | [@Crisberry](https://github.com/Crisberry) |
| Juan Sebastián Ángel | [@Sebasan1709](https://github.com/Sebasan1709) |
| Julián Echeverry | [@julianecheverry](https://github.com/julianecheverry) |
