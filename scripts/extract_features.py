import os
import json
import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from tqdm import tqdm


class HawkFeatureExtractor:

    def __init__(self):

        print("Initializing Feature Extraction Pipeline...")

        # ---------------- PATHS ----------------
        self.base_path = os.getcwd()
        self.raw_path = os.path.join(self.base_path, "data", "raw_images")
        self.output_path = os.path.join(self.base_path, "data", "processed_features")

        os.makedirs(self.output_path, exist_ok=True)

        # ---------------- DEVICE ----------------
        self.device = torch.device("cpu")

        # ---------------- MODEL ----------------
        print("Loading ResNet18 backbone...")
        self.model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

        # Remove final classification layer
        self.model = torch.nn.Sequential(*list(self.model.children())[:-1])
        self.model.eval()
        self.model.to(self.device)

        # ---------------- TRANSFORM ----------------
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    # --------------------------------------------------------

    def extract_feature(self, image_path):

        image = Image.open(image_path).convert("RGB")
        image = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            feature = self.model(image)

        feature = feature.squeeze().cpu().numpy()
        return feature

    # --------------------------------------------------------

    def run(self):

        print("Starting feature extraction...")

        image_files = [
            os.path.join(self.raw_path, f)
            for f in os.listdir(self.raw_path)
            if f.endswith(".png")
        ]

        image_files.sort()

        features = []

        for img_path in tqdm(image_files):
            feat = self.extract_feature(img_path)
            features.append(feat)

        features = np.array(features)

        print(f"Extracted feature shape: {features.shape}")

        # ---------------- SAVE FEATURES ----------------
        feature_file = os.path.join(self.output_path, "features.npy")
        np.save(feature_file, features)

        # ---------------- COMPUTE STATS ----------------
        mean_vector = np.mean(features, axis=0)
        std_vector = np.std(features, axis=0)

        stats = {
            "num_images": int(features.shape[0]),
            "feature_dimension": int(features.shape[1]),
            "mean_norm": float(np.linalg.norm(mean_vector)),
            "std_mean": float(np.mean(std_vector))
        }

        stats_file = os.path.join(self.output_path, "feature_stats.json")
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=4)

        # ---------------- DOMAIN SIGNATURE ----------------
        signature_value = float(np.mean(mean_vector))

        signature = {
            "environment_signature": signature_value,
            "description": "Mean embedding signature of environment"
        }

        signature_file = os.path.join(self.output_path, "domain_signature.json")
        with open(signature_file, "w") as f:
            json.dump(signature, f, indent=4)

        print("\nFeature Extraction Complete")
        print(json.dumps(stats, indent=4))
        print("\nDomain Signature:", signature_value)


# ------------------------------------------------------------

if __name__ == "__main__":
    extractor = HawkFeatureExtractor()
    extractor.run()