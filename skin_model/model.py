import torch.nn as nn
from torchvision import models

class SkinDiseaseClassifier(nn.Module):
    def __init__(self, num_classes=4, unfreeze_layers=3, dropout_rate=0.7):
        super(SkinDiseaseClassifier, self).__init__()
        self.backbone = models.efficientnet_b0(pretrained=True)

        for param in self.backbone.parameters():
            param.requires_grad = False

        for param in self.backbone.features[-unfreeze_layers:].parameters():
            param.requires_grad = True

        in_features = self.backbone.classifier[1].in_features

        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(p=dropout_rate / 2),
            nn.Linear(256, num_classes)
        )

        self._initialize_weights(self.backbone.classifier)

    def forward(self, x):
        return self.backbone(x)

    def _initialize_weights(self, module):
        for m in module.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)