from torch import nn
from torchvision import models


class ModelInitializer:
    def __init__(self, device, model_name='EfficientNet_V2_S', weights_suffix='DEFAULT'): # weights_suffix='IMAGENET1K_V1'
        self.device = device
        self.model_name = model_name
        self.weights_suffix = weights_suffix

    def initialize_model(self):
        base_architecture = self.model_name.lower()

        try:
            model_class = getattr(models, base_architecture)
        except AttributeError:
            raise ValueError(f"Unsupported architecture: {self.model_name}")

        try:
            weights_enum = getattr(models, f'{self.model_name}_Weights')
            weights_class = getattr(weights_enum, self.weights_suffix)
        except AttributeError:
            raise ValueError(f"Unsupported weights: {self.model_name}_Weights.{self.weights_suffix}")

        model = model_class(weights=weights_class)


        if hasattr(model, 'fc'):
            num_features = model.fc.in_features
            model.fc = nn.Sequential(
                nn.Linear(num_features, 1),
                nn.Sigmoid()
            )
        elif hasattr(model, 'classifier'):
            num_features = model.classifier[1].in_features
            model.classifier = nn.Sequential(
                nn.Dropout(p=0.2, inplace=False),
                nn.SELU(),
                nn.Linear(num_features, 1)
            )
        else:
            raise ValueError(f"Model {self.model_name} architecture requires custom handling.")

        model = model.to(self.device)
        return model