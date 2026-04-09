import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np


class FeatureExtractor:

    def __init__(self):

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        weights = models.ResNet18_Weights.DEFAULT

        model = models.resnet18(weights=weights)

        self.model = torch.nn.Sequential(*list(model.children())[:-1])

        self.model.eval()
        self.model.to(self.device)

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def extract(self, image_path):

        img = Image.open(image_path).convert("RGB")

        img = self.transform(img).unsqueeze(0).to(self.device)

        with torch.no_grad():

            feature = self.model(img)

        feature = feature.cpu().numpy().flatten()

        return feature

    def extract_from_array(self, frame):
        """
        Extract features directly from numpy array (NO DISK I/O)
        """

        from PIL import Image

        # Ensure uint8
        frame = frame.astype(np.uint8)

        # Convert to PIL
        img = Image.fromarray(frame).convert("RGB")

        img = self.transform(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            feature = self.model(img)

        feature = feature.cpu().numpy().flatten()

        return feature