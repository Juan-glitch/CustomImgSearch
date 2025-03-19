# Version: 0.0.1 | Updated: 2025-03-17 15:06:32 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
import os

def process_folder(input_dir, base_output_dir, embeddings,
                    embeddingTranslator, researcher):
    """
    Description:
         process_folder function.
    Args:
        input_dir: The first parameter.
        base_output_dir: The second parameter.
        embeddings: The third parameter.
        embeddingTranslator: The fourth parameter.
        researcher: The fifth parameter.
    Returns:
        None
    """
    processed_images = []
    for file in os.listdir(input_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_path = os.path.join(input_dir, file)
            processed = process_image(image_path, embeddings, embeddingTranslator, researcher, base_output_dir)
            processed_images.append(processed)
    return processed_images