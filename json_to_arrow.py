import json
from datasets import Dataset

# Mapeamento de labels para IDs
LABEL_TO_ID = {
    "ano_calendario": 0,
    "dependentes": 1,
    "exercicio_e_ano": 2,
    "nome_contribuinte": 3,
    "protegida_por_sigilo": 4,
    "rodape_pagina": 5,
    "texto_ignorado": 6,
    "tipo_declaracao": 7,
    "valor_total_bens": 8
}

def convert_label_studio_to_hf(json_path):
    """
    Lê o JSON exportado do Label Studio, ignorando o campo "bbox".
    Pega as informações de bounding box e label diretamente de "label".
    Converte para um Dataset do Hugging Face.
    """

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_ids = []
    all_images = []
    all_tokens = []
    all_bboxes = []
    all_ner_tags = []

    for item in data:
        # ID do exemplo
        sample_id = item["id"]

        # Caminho ou URL da imagem (campo 'ocr')
        sample_image = item["ocr"]

        # Lista de "tokens" (assumindo que cada item da 'transcription'
        # corresponde a um item de 'label')
        tokens = item["transcription"]

        # As bounding boxes e as tags, agora extraídas SÓ do campo "label"
        bboxes = []
        ner_tags = []

        # Verifique se a quantidade de "label" é a mesma de "transcription".
        # Se não for, você pode usar zip() ou min(len(), len()).
        # Aqui, vamos usar zip() para tratar a menor das duas:
        for label_info, token_text in zip(item["label"], tokens):
            # Pegamos os campos de bbox diretamente do label_info
            x = label_info["x"]
            y = label_info["y"]
            w = label_info["width"]
            h = label_info["height"]

            # Monta a lista [x, y, width, height] - ou qualquer formato
            bboxes.append([x, y, w, h])

            # label_info["labels"] normalmente é uma lista de classes
            # Se há só uma classe por bounding box, pegamos a primeira

            # Label (primeira da lista) convertida para ID numérico
            label_name = label_info["labels"][0]
            label_id = LABEL_TO_ID.get(label_name, -1)  # -1 para rótulos não mapeados
            ner_tags.append(label_id)
            # class_id = label_info["labels"][0]
            # ner_tags.append(class_id)

        all_ids.append(sample_id)
        all_images.append(sample_image)
        all_tokens.append(tokens)
        all_bboxes.append(bboxes)
        all_ner_tags.append(ner_tags)

    # Monta o dicionário no formato aceito pelo Hugging Face
    hf_dict = {
        "id": all_ids,
        "image": all_images,
        "tokens": all_tokens,
        "bboxes": all_bboxes,
        "ner_tags": all_ner_tags,
    }

    hf_dataset = Dataset.from_dict(hf_dict)
    return hf_dataset

if __name__ == "__main__":
    # Exemplo de uso:
    json_file = "original.json"
    hf_dataset = convert_label_studio_to_hf(json_file)

    print(hf_dataset)
    # Salvar no formato Arrow, se quiser
    hf_dataset.save_to_disk("arrow_dataset")