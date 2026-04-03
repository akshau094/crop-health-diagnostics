import os
import requests
import zipfile

def download_plantvillage_subset():
    """
    Instructions and helper to get the PlantVillage dataset.
    The full dataset is large, so this script provides information 
    on how to access it for training your own models.
    """
    print("=== PlantVillage Dataset Information ===")
    print("The PlantVillage dataset is the gold standard for crop disease classification.")
    print("It contains over 50,000 images across 38 classes.")
    print("\nYou can download it from Kaggle or official sources:")
    print("URL: https://www.kaggle.com/datasets/emmareed/plantvillage-dataset")
    print("\nIn this system, we use a pre-trained ResNet18 model fine-tuned on this dataset.")
    print("To train your own, you would download the dataset, organize it into folders by class,")
    print("and use the PyTorch ImageFolder dataset loader.")

if __name__ == "__main__":
    download_plantvillage_subset()
