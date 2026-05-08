import os
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from skin_model.model import SkinDiseaseClassifier
from skin_model.dataset import BalancedSkinDataset
from skin_model.train import TrainingConfig


def test_model(config: TrainingConfig, num_samples: int = 4):
    # Настройка устройства
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # Фиксация seed для воспроизводимости
    torch.manual_seed(42)
    np.random.seed(42)

    # Загрузка тестового датасета
    test_dataset = BalancedSkinDataset(config.data_dir, mode='test', img_size=config.img_size)
    test_loader = DataLoader(
        test_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=True
    )

    # Загрузка модели
    model_path = os.path.join(config.save_dir, 'final_model.pth')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")

    model = SkinDiseaseClassifier(
        num_classes=len(test_dataset.classes),
        dropout_rate=config.dropout_rate,
        unfreeze_layers=config.unfreeze_layers
    ).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    all_preds, all_labels, all_probs = [], [], []

    # Предсказания модели
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

    # Метрики
    print_classification_report(test_dataset.classes, all_labels, all_preds)
    plot_confusion_matrix(test_dataset.classes, all_labels, all_preds)
    print_prediction_samples(test_dataset, all_labels, all_preds, all_probs, num_samples)


def print_classification_report(classes, true_labels, pred_labels):
    print("\nClassification Report:")
    report = classification_report(true_labels, pred_labels, target_names=classes, digits=4)
    print(report)

    # Сохраняем отчёт в файл
    with open("classification_report.txt", "w") as f:
        f.write(report)


def plot_confusion_matrix(classes, true_labels, pred_labels):
    cm = confusion_matrix(true_labels, pred_labels)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')
    plt.show()


def print_prediction_samples(dataset, true_labels, pred_labels, probs, num_samples=4):
    print("\nPrediction Samples:")
    for i in range(min(num_samples, len(true_labels))):
        print(f"\nSample {i + 1}:")
        print(f"True label    : {dataset.classes[true_labels[i]]}")
        print(f"Predicted     : {dataset.classes[pred_labels[i]]}")
        print("Probabilities :")
        for cls, prob in zip(dataset.classes, probs[i]):
            print(f"  {cls}: {prob:.4f}")


if __name__ == '__main__':
    config = TrainingConfig()
    test_model(config, num_samples=4)