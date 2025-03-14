def process_folder(input_dir, base_output_dir, embeddings, embeddingTranslator, researcher):
    """
    Procesa todas las imágenes del directorio input_dir.
    """
    processed_images = []
    for file in os.listdir(input_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_path = os.path.join(input_dir, file)
            processed = process_image(image_path, embeddings, embeddingTranslator, researcher, base_output_dir)
            processed_images.append(processed)
    return processed_images

