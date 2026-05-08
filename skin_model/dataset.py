import os
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms
import random

class BalancedSkinDataset(Dataset):
    def __init__(self, root_dir, mode='train', img_size=224, max_per_class=100, exclude_classes=None):
        """
            root_dir (str): путь к директории с данными
            mode (str): 'train', 'val' или 'test'
            img_size (int): размер изображения
            max_per_class (int): максимум изображений на класс
            exclude_classes (list): список классов для исключения
        """
        self.root_dir = os.path.join(root_dir, mode)
        exclude_classes = exclude_classes or []
        self.classes = sorted([cls for cls in os.listdir(self.root_dir)
                               if cls not in exclude_classes])
        self.class_to_idx = {cls: i for i, cls in enumerate(self.classes)}
        self.images = []
        self.labels = []

        # сбор и балансировка данных
        self._load_and_balance_images(max_per_class)

        # аугментации
        self.transform = self._get_transforms(mode, img_size)

        # статистика
        print(f"Created {mode} dataset with {len(self)} samples")
        for cls, idx in self.class_to_idx.items():
            print(f"Class {cls}: {sum(label == idx for label in self.labels)} samples")

    def _load_and_balance_images(self, max_per_class):
        # сначала собираем все возможные изображения
        class_images = {cls: [] for cls in self.classes}

        for cls in self.classes:
            cls_dir = os.path.join(self.root_dir, cls)
            for img_name in os.listdir(cls_dir):
                if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    class_images[cls].append(os.path.join(cls_dir, img_name))

        # балансировка
        min_samples = min(len(imgs) for imgs in class_images.values()) if max_per_class is None \
            else min(max_per_class, min(len(imgs) for imgs in class_images.values()))

        for cls, img_paths in class_images.items():
            selected_paths = random.sample(img_paths, min(min_samples, len(img_paths)))
            self.images.extend(selected_paths)
            self.labels.extend([self.class_to_idx[cls]] * len(selected_paths))

    def _get_transforms(self, mode, img_size):
        base_transform = [
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]

        if mode == 'train':
            augmentations = [
                transforms.RandomHorizontalFlip(),
                transforms.RandomVerticalFlip(),
                transforms.RandomRotation(30),
                transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
                transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
                transforms.RandomResizedCrop(img_size, scale=(0.8, 1.0)),
            ]
            return transforms.Compose([
                transforms.RandomApply(augmentations, p=0.5),
                *base_transform
            ])
        else:
            return transforms.Compose(base_transform)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        try:
            image = Image.open(self.images[idx]).convert('RGB')
            label = self.labels[idx]
            return self.transform(image), label
        except Exception as e:
            print(f"Error loading {self.images[idx]}: {e}")
            return self[random.randint(0, len(self) - 1)]