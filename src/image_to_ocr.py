# Load model directly
from transformers import AutoProcessor, AutoModelForImageTextToText
from transformers.image_utils import load_image
from typing import List
import requests
import torch
from PIL import Image
from io import BytesIO





class OCRModel:
    
    def __init__(self):
        
        self.processor = AutoProcessor.from_pretrained("ds4sd/SmolDocling-256M-preview")
        self.model = AutoModelForImageTextToText.from_pretrained("ds4sd/SmolDocling-256M-preview")


    def load_images(self , image_paths:list[str]) -> list:
        if len(image_paths) <= 3 :        
    
            images = [load_image(image_path) for image_path in image_paths]        
        
            return images
        else:
            raise ValueError(f"only upload num of images <= 3")
        
    def getOCRPrompts(self, num_images: int):
        prompts = []
        for _ in range(num_images):
            message = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "text", "text": "what is written in the image?"},
                    ]
                }
            ]
            prompt = self.processor.apply_chat_template(message, add_generation_prompt=True)
            prompts.append(prompt)
        return prompts
    
    
    def getOCRtext(self, image_paths: List[str]):
        images = self.load_images(image_paths=image_paths)
        prompts = self.getOCRPrompts(num_images=len(images))

        inputs = self.processor(
            text=prompts, 
            images=images, 
            padding=True, 
            return_tensors="pt"
        ).to(self.model.device)

        generated_ids = self.model.generate(**inputs, max_new_tokens=256)
        generated_texts = self.processor.batch_decode(generated_ids, skip_special_tokens=True)

        OCR_texts = [text.split("Assistant")[-1].strip() for text in generated_texts]
        
        
        return OCR_texts , image_paths
        
    
if __name__ == "__main__":
    
    ocr_model = OCRModel()
    
    image_paths = ["20240625_154117.jpg" , "20240625_154117.jpg" ]
    
    ocr_texts , image_paths = ocr_model.getOCRtext(image_paths= image_paths)
    
    print(ocr_texts)