import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import json
import os
import httpx

# OpenRouter API Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Full PlantVillage Labels for more accurate detection
LABELS = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
    "Defected_Crop"
]

class PlantDiseaseModel:
    def __init__(self):
        # Using a pre-trained ResNet18 model
        self.model = models.resnet18(pretrained=True)
        # Modify the last layer for our labels
        num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Linear(num_ftrs, len(LABELS))
        self.model.eval()
        
        # Preprocessing transforms
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        # Load dataset info
        self.dataset_info = self._load_dataset_info()

    def _load_dataset_info(self):
        info_path = os.path.join(os.path.dirname(__file__), "..", "dataset", "dataset_info.json")
        if os.path.exists(info_path):
            with open(info_path, "r") as f:
                return json.load(f)
        return {}

    def predict(self, image_bytes, language="English"):
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image = self.transform(image).unsqueeze(0)
        
        with torch.no_grad():
            outputs = self.model(image)
            _, predicted = torch.max(outputs, 1)
            
        prediction = LABELS[predicted.item()]
        
        # Mapping to interventions/information from organized dataset
        info = self.get_detailed_info(prediction)
        ai_analysis = None
        
        # Enhance with AI
        ai_info = self.get_ai_detailed_info(prediction, language)
        if ai_info:
            ai_analysis = {
                "description": str(ai_info.get("description", "")),
                "how_to_fix": ai_info.get("how_to_fix", "")
            }
            
            # Ensure how_to_fix is a string for consistency
            if isinstance(ai_analysis["how_to_fix"], list):
                ai_analysis["how_to_fix"] = ". ".join([str(step).strip().rstrip('.') for step in ai_analysis["how_to_fix"]]) + "."
            
            # Use AI translations for the main fields if available
            info["description"] = ai_analysis["description"]
            info["how_to_fix"] = ai_analysis["how_to_fix"]
        
        return {
            "prediction": prediction,
            "intervention": info["how_to_fix"],
            "status": "Healthy" if "healthy" in prediction.lower() else "Diseased",
            "info": info["description"],
            "ai_analysis": ai_analysis
        }

    def get_ai_detailed_info(self, label, language="English"):
        """Uses OpenRouter API to get a concise, summarized diagnostic report and intervention plan in the requested language"""
        disease_name = label.replace("___", " ").replace("_", " ")
        is_healthy = "healthy" in label.lower()
        
        if is_healthy:
            prompt = (
                f"The plant '{disease_name}' is healthy.\n"
                f"Provide a concise summary and 3 quick tips for maintaining its health in {language}.\n"
                "Format your response as a JSON with two keys:\n"
                "1. 'description': A brief positive summary.\n"
                "2. 'how_to_fix': 3 short bullet points for maintenance.\n"
                "Return ONLY the JSON object."
            )
        else:
            prompt = (
                f"As an expert plant pathologist, provide a CONCISE and SUMMARIZED diagnostic report for: '{disease_name}' in {language}.\n"
                "Do not be overly wordy. Provide the most critical information only.\n"
                "Your response must include:\n"
                "1. Summary: A brief explanation of the cause and primary symptoms (max 3-4 sentences).\n"
                "2. Intervention: A clear, step-by-step plan with the 5 most effective actions (max 5 steps).\n\n"
                "Format your response as a JSON with two keys:\n"
                "1. 'description': The brief summary covering cause and symptoms.\n"
                "2. 'how_to_fix': The 5-step intervention plan.\n"
                f"IMPORTANT: All text must be in {language}.\n"
                "Return ONLY the JSON object."
            )

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    OPENROUTER_URL,
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8006",
                        "X-Title": "Crop Health Diagnostics"
                    },
                    json={
                        "model": "google/gemini-2.0-flash-001",
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"}
                    }
                )
                
                if response.status_code == 200:
                    ai_content = response.json()["choices"][0]["message"]["content"]
                    return json.loads(ai_content)
        except Exception as e:
            print(f"OpenRouter API Error: {str(e)}")
        
        return None

    def get_detailed_info(self, label):
        # First try loading from the organized dataset info
        if label in self.dataset_info:
            return self.dataset_info[label]
        
        # Fallback if not in the JSON file
        return {
            "description": f"The model detected {label.replace('___', ' ')}. This is a common plant health condition.",
            "how_to_fix": "General recommendation: Improve ventilation, prune affected areas, and monitor for changes. Consult an expert if condition persists."
        }

model_instance = PlantDiseaseModel()
