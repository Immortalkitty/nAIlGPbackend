from torch import nn
from torchvision import models


class ModelInitializer:
    def __init__(self, device, model_name='ResNet50', weights_suffix='DEFAULT'):
        self.device = device
        self.model_name = model_name
        self.weights_suffix = weights_suffix

    def initialize_model(self):
        base_architecture = self.model_name.lower()

        try:
            model_class = getattr(models, base_architecture)
            try:
                weights_enum = getattr(models, f'{self.model_name}_Weights')
                weights_class = getattr(weights_enum, self.weights_suffix)
                model = model_class(weights=weights_class)
            except AttributeError:
                model = model_class()
                print("model initialize without weights")
            if hasattr(model, 'fc'):
              num_features = model.fc.in_features
              model.fc = nn.Sequential(
                  nn.Linear(num_features, 1)
              )
            elif hasattr(model, 'classifier'):
              num_features = model.classifier.in_features if isinstance(model.classifier, nn.Linear) else model.classifier[1].in_features
              model.classifier = nn.Sequential(
                  nn.Linear(num_features, 1)
              )
            if hasattr(model, 'AuxLogits'):
                num_features_aux = model.AuxLogits.fc.in_features
                model.AuxLogits.fc = nn.Sequential(
                    nn.Linear(num_features_aux, 1)
                )
        except AttributeError:
            raise ValueError(f"Unsupported architecture: {self.model_name}.")

        for param in model.parameters():
            param.requires_grad = False

        if hasattr(model, 'fc'):
            for param in model.fc.parameters():
                param.requires_grad = True
        elif hasattr(model, 'classifier'):
            for param in model.classifier.parameters():
                param.requires_grad = True

        if hasattr(model, 'AuxLogits'):
            for param in model.AuxLogits.parameters():
                param.requires_grad = True

        model = model.to(self.device)

        return model