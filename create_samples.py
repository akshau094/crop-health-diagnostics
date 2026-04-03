import os
from PIL import Image
import numpy as np

def create_mock_dataset():
    """
    Creates a few mock leaf images for demonstration purposes.
    In a real scenario, the user would upload images from the PlantVillage dataset.
    """
    os.makedirs("backend/samples", exist_ok=True)
    
    classes = {
        "apple_scab": (100, 120, 50),      # Greenish-brown spots
        "potato_early_blight": (80, 60, 20), # Dark brown spots
        "tomato_healthy": (50, 200, 50),     # Bright green
    }
    
    for name, color in classes.items():
        # Create a 256x256 image with a base leaf color
        img_array = np.zeros((256, 256, 3), dtype=np.uint8)
        img_array[:, :] = color
        
        # Add some random "spots" to simulate disease
        if "healthy" not in name:
            for _ in range(20):
                r = np.random.randint(20, 230)
                c = np.random.randint(20, 230)
                size = np.random.randint(5, 15)
                img_array[r:r+size, c:c+size] = (20, 20, 20) # Black/Dark spots
        
        img = Image.fromarray(img_array)
        img.save(f"backend/samples/{name}.jpg")
        print(f"Created sample: backend/samples/{name}.jpg")

if __name__ == "__main__":
    create_mock_dataset()
