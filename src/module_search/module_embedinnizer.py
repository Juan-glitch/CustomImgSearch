import torch
import clip
import torch.nn.functional as F

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess_clip = clip.load("ViT-B/32", device=device)

def get_image_embedding(image_tensor):
    with torch.no_grad():
        image_embedding = model.encode_image(image_tensor.to(device))
    return image_embedding / image_embedding.norm(dim=-1, keepdim=True)

def get_text_embedding(text):
    text_input = clip.tokenize([text]).to(device)
    with torch.no_grad():
        text_embedding = model.encode_text(text_input)
    return text_embedding / text_embedding.norm(dim=-1, keepdim=True)

def is_similar(image_tensor, query, threshold=0.8):
    image_emb = get_image_embedding(image_tensor)
    text_emb = get_text_embedding(query)
    similarity = F.cosine_similarity(image_emb, text_emb)
    return similarity.item() >= threshold