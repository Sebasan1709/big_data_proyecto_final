import spacy
from spacy.lang.es.stop_words import STOP_WORDS
from pathlib import Path

def extract_entities_from_chunks():
    # 1. Configurar rutas relativas (desde /src hacia /data)
    base_path = Path(__file__).parent.parent
    data_dir = base_path / "data" / "transcripts" / "chunks"

    
    # 2. Cargar modelo de spaCy (Large para mejor precisión)
    try:
        nlp = spacy.load("es_core_news_lg")
    except OSError:
        print("Error: El modelo 'es_core_news_lg' no está instalado.")
        return
    
    # 2.1. Añadimos palabras que vimos en tu resultado anterior que no son entidades
    custom_stops = {"reiteró", "esclareció", "reconoció", "añadió", "entonces", "dijo"}
    for word in custom_stops:
        STOP_WORDS.add(word)

    # 3. Procesar el texto con el modelo NER
    print(f"--- Iniciando NER refinado en {len("data\\transcripts\\chunks")} archivos ---")
    doc = nlp("data\\transcripts\\full_transcript.txt")

    # 4. Organizar y mostrar resultados con filtros
    # Filtramos por categorías relevantes para grafos
    entities = {
        "PER": set(),   # Personas
        "ORG": set(),   # Organizaciones
        "LOC": set(),   # Ubicaciones
        "MISC": set()   # Misceláneos (Algoritmos, leyes, etc.)
    }

    for ent in doc.ents:
        # FILTRO 1: ¿Es una stopword o es muy corta (menos de 3 letras)?
        # FILTRO 2: ¿La palabra en minúsculas está en nuestra lista de bloqueo?
        text_lower = ent.text.lower().strip()
        
        if text_lower not in STOP_WORDS and len(text_lower) > 2:
            if ent.label_ in entities:
                entities[ent.label_].add(ent.text.strip())

    # 5. Imprimir reporte rápido
    print("\nRESULTADOS DE EXTRACCIÓN:")
    for label, found_entities in entities.items():
        print(f"\n[{label}] - {len(found_entities)} halladas:")
        print(", ".join(list(found_entities)[:10]) + ("..." if len(found_entities) > 10 else ""))

    # Opcional: Guardar para el siguiente paso de Neo4j
    output_file = base_path / "data" / "transcripts" / "extracted_entities_cleaned.txt"
    with open(output_file, "w", encoding="utf-8") as out:
        for label, found_entities in entities.items():
            out.write(f"--- {label} ---\n")
            out.write("\n".join(found_entities) + "\n\n")
    
    # print(f"\nArchivo guardado en: {output_file}")
    print(f"\nArchivo limpio guardado en: {output_file}")


# Punto de entrada, Evita ejecuciones accidentales (Importación)
if __name__ == "__main__":
    extract_entities_from_chunks()
