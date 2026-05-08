import torch
from torchvision import transforms
from PIL import Image
import os

from skin_model.model import SkinDiseaseClassifier
from skin_model.dataset import BalancedSkinDataset


def load_model(config, class_names):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = SkinDiseaseClassifier(num_classes=len(class_names)).to(device)

    state_dict = torch.load(os.path.join(config.save_dir, 'final_model.pth'), map_location=device)
    # если модель была сохранена с DataParallel, убираем префикс 'module.'
    from collections import OrderedDict
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = k[7:] if k.startswith('module.') else k
        new_state_dict[name] = v
    model.load_state_dict(new_state_dict)

    model.eval()
    return model, device


def get_transform(img_size=224):
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])


def predict_image(image_path, config):
    dummy_dataset = BalancedSkinDataset(config.data_dir, mode='val', img_size=config.img_size)
    class_names = dummy_dataset.classes

    model, device = load_model(config, class_names)

    image = Image.open(image_path).convert('RGB')
    transform = get_transform(img_size=config.img_size)
    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.softmax(outputs, dim=1).cpu().numpy()[0]
        predicted_class_idx = torch.argmax(outputs, dim=1).item()
        predicted_class = class_names[predicted_class_idx]

    print(f"\nПредсказание для изображения: {os.path.basename(image_path)}")
    print(f"Класс: {predicted_class} ({predicted_class_idx})")
    print("Вероятности по классам:")
    for cls, prob in zip(class_names, probs):
        print(f"{cls}: {prob:.4f}")

    return predicted_class, probs