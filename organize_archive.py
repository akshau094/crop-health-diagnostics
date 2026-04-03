import os
import pandas as pd
import shutil
import json

def organize_archive_dataset():
    archive_path = "c:/Users/aksha/OneDrive/Desktop/crop/archive"
    train_dir = os.path.join(archive_path, "train")
    csv_path = os.path.join(archive_path, "train.csv")
    output_dataset_dir = "c:/Users/aksha/OneDrive/Desktop/crop/organized_archive"
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    # Load CSV
    df = pd.read_csv(csv_path)
    
    # In this specific dataset (Global Wheat Detection or similar), 
    # the task is often object detection (wheat heads).
    # However, since the user wants to categorize and fix defects, 
    # we will treat the presence of bounding boxes as "Defected" 
    # and organize accordingly.
    
    # For this project, let's create a "Defected_Crop" class 
    # and move images there if they have bounding boxes.
    
    os.makedirs(os.path.join(output_dataset_dir, "Defected_Crop"), exist_ok=True)
    os.makedirs(os.path.join(output_dataset_dir, "Healthy_Crop"), exist_ok=True)
    
    # Get unique image IDs that have defects
    defected_images = df['image_id'].unique()
    
    # Limit to a few for demonstration to avoid long processing
    sample_limit = 50
    count = 0
    
    for img_id in defected_images:
        if count >= sample_limit:
            break
            
        src = os.path.join(train_dir, img_id)
        dst = os.path.join(output_dataset_dir, "Defected_Crop", img_id)
        
        if os.path.exists(src):
            shutil.copy(src, dst)
            count += 1
            
    print(f"Organized {count} defected images into {output_dataset_dir}/Defected_Crop")

    # Update dataset_info.json with information about this new class
    info_path = "c:/Users/aksha/OneDrive/Desktop/crop/dataset/dataset_info.json"
    if os.path.exists(info_path):
        with open(info_path, "r") as f:
            data = json.load(f)
    else:
        data = {}
        
    data["Defected_Crop"] = {
        "name": "General Crop Defect",
        "description": "Detected anomalies or defects on the crop/leaf surface. These could be pests, nutrient deficiencies, or physical damage.",
        "how_to_fix": "1. Inspect for pests like aphids or mites. 2. Check soil pH and nutrient levels (Nitrogen, Phosphorus, Potassium). 3. Ensure proper irrigation (not too much, not too little). 4. Remove heavily damaged leaves to prevent spread."
    }
    
    os.makedirs(os.path.dirname(info_path), exist_ok=True)
    with open(info_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Updated {info_path} with Defected_Crop information.")

if __name__ == "__main__":
    organize_archive_dataset()
