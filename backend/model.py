import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import json
import os

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
        
        return {
            "prediction": prediction,
            "intervention": info["how_to_fix"],
            "status": "Healthy" if "healthy" in prediction.lower() else "Diseased",
            "info": info["description"],
            "ai_analysis": None
        }

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
