import spacy
import csv
from pathlib import Path


def get_main_relation(sent):
    """
    Intenta obtener el verbo principal de la oración.
    Si no encuentra uno claro, devuelve RELATED_TO.
    """
    for token in sent:
        if token.dep_ == "ROOT" and token.pos_ in {"VERB", "AUX"}:
            return token.lemma_.upper().replace(" ", "_")
    return "RELATED_TO"


def extract_relations():
    # 1. Rutas
    base_path = Path(__file__).resolve().parent.parent
    transcript_file = base_path / "data" / "transcripts" / "full_transcript.txt"
    output_file = base_path / "data" / "transcripts" / "extracted_relations.csv"

    # 2. Validar archivo
    if not transcript_file.exists():
        print(f"Error: no se encontró el archivo {transcript_file}")
        return

    # 3. Cargar modelo spaCy
    try:
        nlp = spacy.load("es_core_news_lg")
    except OSError:
        print("Error: El modelo 'es_core_news_lg' no está instalado.")
        return

    # 4. Leer transcript
    with open(transcript_file, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        print("Error: el transcript está vacío.")
        return

    print(f"Procesando relaciones desde: {transcript_file.name}")

    # 5. Procesar texto
    doc = nlp(text)

    relations = []
    sentence_id = 1

    # Etiquetas que sí queremos considerar
    valid_labels = {"PER", "ORG", "LOC", "MISC"}

    for sent in doc.sents:
        sentence_text = sent.text.strip()

        if not sentence_text:
            continue

        sent_entities = []
        for ent in sent.ents:
            if ent.label_ in valid_labels and len(ent.text.strip()) > 2:
                sent_entities.append({
                    "entity_text": ent.text.strip(),
                    "entity_label": ent.label_
                })

        # Solo nos interesan oraciones con al menos 2 entidades
        if len(sent_entities) >= 2:
            relation_name = get_main_relation(sent)

            # Crear relaciones entre pares consecutivos
            for i in range(len(sent_entities) - 1):
                source = sent_entities[i]
                target = sent_entities[i + 1]

                relations.append({
                    "sentence_id": sentence_id,
                    "sentence_text": sentence_text,
                    "source_entity": source["entity_text"],
                    "source_type": source["entity_label"],
                    "relation": relation_name,
                    "target_entity": target["entity_text"],
                    "target_type": target["entity_label"]
                })

        sentence_id += 1

    # 6. Guardar CSV
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "sentence_id",
            "sentence_text",
            "source_entity",
            "source_type",
            "relation",
            "target_entity",
            "target_type"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(relations)

    print(f"Relaciones extraídas: {len(relations)}")
    print(f"Archivo guardado en: {output_file}")


if __name__ == "__main__":
    extract_relations()