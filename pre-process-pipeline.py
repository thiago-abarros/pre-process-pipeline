#!/usr/bin/env python3
"""
PDF Processing and OCR Dataset Creation Tool

This script provides an end-to-end solution for:
1. Converting PDF files to high-quality images
2. Performing OCR on those images using PaddleOCR
3. Creating a Label Studio compatible dataset in JSON format

Usage:
    python pre-process-images.py [pdf_path_or_folder]

    If a folder is provided, all PDF files in that folder will be processed.
    If a single PDF file is provided, only that file will be processed.
    If no argument is provided, a default path will be used.

Dependencies:
    - PyMuPDF (fitz)
    - PaddleOCR
    - PIL
    - numpy
"""

import fitz
import os
import sys
import json
from uuid import uuid4
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
import glob

def convert_pdf_to_images(pdf_path, dpi=300):
    """
    Convert a PDF file to a series of high-resolution images.

    Args:
        pdf_path (str): Path to the PDF file
        dpi (int): Resolution for the output images

    Returns:
        str: Path to the folder containing the generated images
    """

    zoom = dpi/72  # Standard conversion from DPI to zoom factor
    magnify = fitz.Matrix(zoom, zoom)

    # Get the filename without extension for folder naming
    folder_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_folder = f"image/{folder_name}"

    # Create output directory
    os.makedirs(output_folder, exist_ok=True)

    # Open and process the PDF
    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=magnify)
        output_file = f"{output_folder}/page_{page_num}.png"
        pix.save(output_file)
        print(f"Gerado: {output_file}")

    print(f"Convertidas {len(doc)} páginas de {pdf_path} para imagens em {output_folder}")
    return output_folder

def create_image_url(image_path, base_folder="image"):
    """
    Create a URL for an image to be used with Label Studio.

    Label Studio requires image URLs, so this defines the mapping from filesystem to URLs.
    When using local server, the URL format typically includes the folder structure.

    Args:
        image_path (str): Path to the image file (can be relative or absolute)
        base_folder (str): Base folder for relative path construction

    Returns:
        str: URL for the image
    """
    # Extract the relative path from the base_folder
    if os.path.isabs(image_path):
        # If absolute path, extract parts after the base_folder
        parts = image_path.split(base_folder)
        if len(parts) > 1:
            rel_path = parts[1].lstrip(os.sep).replace('\\', '/')

        else:
            # Fallback to just the filename if base_folder not in path
            rel_path = os.path.basename(image_path)

    else:
        # If it's already a relative path (just filename), use as is
        rel_path = image_path.replace('\\', '/')

    # Ensure the path starts with a single /
    rel_path = rel_path.lstrip('/')

    return f'http://localhost:8080/{rel_path}'

def create_lmv3_dataset(images_folder_path, output_filename=None, save_to_file=True):
    """
    Create a Label Studio compatible dataset from images using PaddleOCR.

    Args:
        images_folder_path (str): Path to the folder containing images
        output_filename (str, optional): Filename for the output JSON. Default is based on folder name.
        save_to_file (bool): Whether to save the results to a file or just return the data

    Returns:
        tuple: (Path to the generated JSON file or None, list of tasks)
    """
    print(f"Inicializando o motor PaddleOCR...")
    # Initialize the OCR engine
    ocr = PaddleOCR(
        use_angle_cls=False,
        lang='en',
        rec=False
    )

    print(f"Processando imagens em {images_folder_path}...")
    label_studio_task_list = []

    # Process each image in the folder
    for image_name in os.listdir(images_folder_path):
        if not image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        image_path = os.path.join(images_folder_path, image_name)
        print(f"Processando imagem: {image_path}")

        # Prepare the output JSON structure
        output_json = {
            'data': {"ocr": create_image_url(image_path)}
        }
        annotation_result = []

        # Load and process the image
        img = np.asarray(Image.open(image_path))
        image_height, image_width = img.shape[:2]

        # Perform OCR
        result = ocr.ocr(img, cls=False)

        # Process OCR results
        for output in result:
            if output is None:
                continue

            for item in output:
                coords = item[0]  # Bounding box coordinates
                text = item[1][0]  # Detected text

                # Skip empty text
                if not text:
                    continue

                # Calculate normalized bounding box values (as percentages)
                x = coords[0][0]
                y = coords[0][1]
                width = coords[2][0] - coords[0][0]
                height = coords[2][1] - coords[0][1]

                bbox = {
                    'x': 100 * x / image_width,
                    'y': 100 * y / image_height,
                    'width': 100 * width / image_width,
                    'height': 100 * height / image_height,
                    'rotation': 0
                }

                # Generate a unique ID for this detection
                region_id = str(uuid4())[:10]

                # Create annotation entries
                bbox_result = {
                    'id': region_id,
                    'from_name': 'bbox',
                    'to_name': 'image',
                    'type': 'rectangle',
                    'value': bbox
                }

                transcription_result = {
                    'id': region_id,
                    'from_name': 'transcription',
                    'to_name': 'image',
                    'type': 'textarea',
                    'value': dict(text=[text], **bbox),
                    'score': 0.5
                }

                # Add to annotation results
                annotation_result.extend([bbox_result, transcription_result])

        # Add predictions to output
        output_json['predictions'] = [{"result": annotation_result, "score": 0.97}]

        # Add to task list
        label_studio_task_list.append(output_json)

    # Save the results to a JSON file if requested
    if save_to_file:
        # Determine output filename if not provided
        if output_filename is None:
            folder_name = os.path.basename(images_folder_path)
            output_filename = f'{folder_name}_label-studio.json'

        # Save the results to a JSON file
        with open(output_filename, 'w') as f:
            json.dump(label_studio_task_list, f, indent=4)

        print(f"Dataset para Label Studio criado com {len(label_studio_task_list)} imagens em {output_filename}")
        return output_filename, label_studio_task_list
    else:
        print(f"Processadas {len(label_studio_task_list)} imagens de {images_folder_path}")
        return None, label_studio_task_list

def process_all_pdfs_in_folder(folder_path, output_json='label_studio_dataset.json'):
    """
    Process all PDF files in a given folder.

    Args:
        folder_path (str): Path to the folder containing PDF files
        output_json (str): Path for the final combined JSON output

    Returns:
        str: Path to the combined JSON file
    """
    # Find all PDF files in the folder
    pdf_pattern = os.path.join(folder_path, "*.pdf")
    pdf_files = glob.glob(pdf_pattern)

    if not pdf_files:
        print(f"Nenhum arquivo PDF encontrado em {folder_path}")
        return None

    print(f"Encontrados {len(pdf_files)} arquivos PDF para processar")

    # Lists to track processed data
    image_folders = []
    all_tasks = []

    # Process each PDF file
    for pdf_path in pdf_files:
        print(f"\n{'='*50}")
        print(f"Processando PDF: {pdf_path}")
        print(f"{'='*50}")

        # Convert PDF to images
        image_folder = convert_pdf_to_images(pdf_path)
        image_folders.append(image_folder)

        # Create dataset for this PDF without saving individual files
        _, pdf_tasks = create_lmv3_dataset(image_folder, save_to_file=False)
        all_tasks.extend(pdf_tasks)

    # Save all tasks into a single dataset
    print(f"\nSalvando dataset combinado final...")
    with open(output_json, 'w') as f:
        json.dump(all_tasks, f, indent=4)

    print(f"Dataset combinado com {len(all_tasks)} imagens totais salvo em {output_json}")
    return output_json

def main():
    """
    Main function to orchestrate the PDF processing and dataset creation workflow.
    """
    # Get path from command line or use default
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "pdfs/"  # Default to a folder instead of a single file

    # Check if the path is a directory or a file
    if os.path.isdir(path):
        print(f"Processando todos os PDFs na pasta: {path}")
        json_file = process_all_pdfs_in_folder(path)

        if json_file:
            print("\nFluxo de trabalho concluído com sucesso!")
            print(f"Dataset combinado do Label Studio criado: {json_file}")
    else:
        # Process single PDF file
        print(f"Processando PDF único: {path}")
        image_folder = convert_pdf_to_images(path)
        json_file, _ = create_lmv3_dataset(image_folder)

        print("\nFluxo de trabalho concluído com sucesso!")
        print(f"PDF convertido para imagens: {image_folder}")
        print(f"Dataset para Label Studio criado: {json_file}")

    print("\nPara usar este dataset no Label Studio:")
    print("1. Inicie o servidor do Label Studio")
    print("2. Crie um novo projeto ou abra um existente")
    print("3. Importe o arquivo JSON gerado")

if __name__ == "__main__":
    main()