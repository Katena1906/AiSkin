import os
import torch
import torch.optim as optim
from torch.utils.data import DataLoader, WeightedRandomSampler
from tqdm import tqdm
import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict, List
import time
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

from skin_model.model import SkinDiseaseClassifier
from skin_model.dataset import BalancedSkinDataset


def plot_training_history(history: Dict[str, List[float]], save_dir: Optional[str] = None) -> None:
    plt.figure(figsize=(16, 6))

    # Loss
    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    # Accuracy
    plt.subplot(1, 2, 2)
    plt.plot(history['train_acc'], label='Train Accuracy')
    plt.plot(history['val_acc'], label='Validation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.legend()

    plt.tight_layout()

    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        plt.savefig(os.path.join(save_dir, 'training_metrics.png'), bbox_inches='tight', dpi=300)
        plt.close()
    else:
        plt.show()


@dataclass
class TrainingConfig:
    data_dir: str = 'data'
    save_dir: str = 'saved_models'
    batch_size: int = 32
    num_epochs: int = 30
    learning_rate: float = 0.0001
    img_size: int = 224
    num_workers: int = 4
    patience: int = 5
    weight_decay: float = 1e-4
    dropout_rate: float = 0.5
    unfreeze_layers: int = 5


def train_model(config: TrainingConfig) -> tuple:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    train_dataset = BalancedSkinDataset(config.data_dir, mode='train', img_size=config.img_size)
    val_dataset = BalancedSkinDataset(config.data_dir, mode='val', img_size=config.img_size)

    class_counts = np.bincount(train_dataset.labels)
    class_weights = 1. / torch.tensor(class_counts, dtype=torch.float)
    sample_weights = class_weights[train_dataset.labels]
    sampler = WeightedRandomSampler(sample_weights, len(sample_weights), replacement=True)

    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        sampler=sampler,
        num_workers=config.num_workers,
        pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=True
    )

    model = SkinDiseaseClassifier(
        num_classes=len(train_dataset.classes),
        dropout_rate=config.dropout_rate,
        unfreeze_layers=config.unfreeze_layers
    ).to(device)

    # функция потерь
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay
    )
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', patience=3, factor=0.5
    )

    # Training variables
    best_acc = 0.0
    epochs_without_improvement = 0
    history = {
        'train_loss': [],
        'val_loss': [],
        'train_acc': [],
        'val_acc': [],
        'lr': []
    }

    # цикл обучения
    for epoch in range(config.num_epochs):
        start_time = time.time()
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch + 1}/{config.num_epochs}")

        for images, labels in progress_bar:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad(set_to_none=True)
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs.data, 1)
            total_train += labels.size(0)
            correct_train += (predicted == labels).sum().item()

            progress_bar.set_postfix({
                'loss': f"{loss.item():.4f}",
                'acc': f"{100 * correct_train / total_train:.2f}%"
            })

        # Calculate training metrics
        avg_train_loss = running_loss / len(train_loader.dataset)
        train_acc = 100. * correct_train / total_train

        # Validation phase
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)

        # Update learning rate
        scheduler.step(val_acc)

        # Update history
        history['train_loss'].append(avg_train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        history['lr'].append(optimizer.param_groups[0]['lr'])

        epoch_time = time.time() - start_time
        print(f"Epoch {epoch + 1}/{config.num_epochs} - {epoch_time:.1f}s")
        print(f"Train Loss: {avg_train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")

        if val_acc > best_acc:
            best_acc = val_acc
            epochs_without_improvement = 0
            save_path = os.path.join(config.save_dir, 'best_model.pth')
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'config': vars(config),
                'class_to_idx': train_dataset.class_to_idx
            }, save_path)
            print(f"Model saved to {save_path} with val_acc: {val_acc:.2f}%")
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= config.patience:
                print(f"Early stopping after {epoch + 1} epochs")
                break

    # сохранение лучшей модели
    final_save_path = os.path.join(config.save_dir, 'final_model.pth')
    torch.save(model.state_dict(), final_save_path)
    print(f"Final model saved to {final_save_path}")

    # график истории обучения
    plot_training_history(history, config.save_dir)

    generate_classification_report(model, val_loader, device, train_dataset.class_to_idx, config.save_dir)

    return model, history


def evaluate(model: torch.nn.Module,
             data_loader: DataLoader,
             criterion: torch.nn.Module,
             device: torch.device) -> tuple:
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in data_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    avg_loss = running_loss / len(data_loader.dataset)
    accuracy = 100. * correct / total if total > 0 else 0.0
    return avg_loss, accuracy


def generate_classification_report(model: torch.nn.Module,
                                   data_loader: DataLoader,
                                   device: torch.device,
                                   class_to_idx: dict,
                                   save_dir: Optional[str] = None) -> None:

    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in data_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            _, preds = torch.max(outputs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    idx_to_class = {v: k for k, v in class_to_idx.items()}
    class_names = [idx_to_class[i] for i in sorted(idx_to_class.keys())]

    # сlassification report
    report = classification_report(
        all_labels, all_preds,
        target_names=class_names,
        output_dict=True
    )

    # матрица ошибок
    plt.figure(figsize=(10, 8))
    cm = confusion_matrix(all_labels, all_preds)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)

    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        # Save report as JSON
        import json
        with open(os.path.join(save_dir, 'classification_report.json'), 'w') as f:
            json.dump(report, f, indent=4)

        # Save confusion matrix
        plt.savefig(os.path.join(save_dir, 'confusion_matrix.png'),
                    bbox_inches='tight', dpi=300)
        plt.close()
    else:
        plt.show()


if __name__ == '__main__':
    config = TrainingConfig(
        data_dir='data',
        save_dir='saved_models',
        batch_size=32,
        num_epochs=50,
        learning_rate=0.0001,
        img_size=224,
        num_workers=4,
        patience=7,
        weight_decay=1e-4,
        dropout_rate=0.5,
        unfreeze_layers=5
    )

    os.makedirs(config.save_dir, exist_ok=True)

    model, history = train_model(config)