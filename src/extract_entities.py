import spacy
from spacy.lang.es.stop_words import STOP_WORDS
from pathlib import Path


def extract_entities_from_full_transcript():
    # 1. Configurar rutas
    base_path = Path(__file__).resolve().parent.parent
    transcript_file = base_path / "data" / "transcripts" / "full_transcript.txt"
    output_file = base_path / "data" / "transcripts" / "extracted_entities_cleaned.txt"

    # 2. Validar que exista el archivo de entrada
    if not transcript_file.exists():
        print(f"Error: no se encontró el archivo {transcript_file}")
        return

    # 3. Cargar modelo de spaCy
    try:
        nlp = spacy.load("es_core_news_lg")
    except OSError:
        print("Error: El modelo 'es_core_news_lg' no está instalado.")
        return

    # 4. Stopwords personalizadas
    custom_stops = {"reiteró", "esclareció", "reconoció", "añadió", "entonces", "dijo"}
    for word in custom_stops:
        STOP_WORDS.add(word)

    # 5. Leer el contenido real del transcript
    with open(transcript_file, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        print("Error: el archivo de transcripción está vacío.")
        return

    print(f"--- Iniciando NER refinado sobre: {transcript_file.name} ---")

    # 6. Procesar texto con spaCy
    doc = nlp(text)

    # 7. Agrupar entidades
    entities = {
        "PER": set(),
        "ORG": set(),
        "LOC": set(),
        "MISC": set()
    }

    for ent in doc.ents:
        text_clean = ent.text.strip()
        text_lower = text_clean.lower()

        if text_lower not in STOP_WORDS and len(text_lower) > 2:
            if ent.label_ in entities:
                entities[ent.label_].add(text_clean)

    # 8. Mostrar resultados
    print("\nRESULTADOS DE EXTRACCIÓN:")
    for label, found_entities in entities.items():
        sorted_entities = sorted(found_entities)
        print(f"\n[{label}] - {len(sorted_entities)} halladas:")
        print(", ".join(sorted_entities[:10]) + ("..." if len(sorted_entities) > 10 else ""))

    # 9. Guardar archivo limpio
    with open(output_file, "w", encoding="utf-8") as out:
        for label, found_entities in entities.items():
            out.write(f"--- {label} ---\n")
            for entity in sorted(found_entities):
                out.write(f"{entity}\n")
            out.write("\n")

    print(f"\nArchivo limpio guardado en: {output_file}")


if __name__ == "__main__":
    extract_entities_from_full_transcript()