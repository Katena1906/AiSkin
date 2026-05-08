import torch
import sys
from pathlib import Path
from PIL import Image
from torchvision import transforms
import numpy as np
import os
import cv2
from torch.nn import functional as F

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skin_model.model import SkinDiseaseClassifier

class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        self._register_hooks()
    
    def _register_hooks(self):
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]
        
        def forward_hook(module, input, output):
            self.activations = output
        
        self.target_layer.register_backward_hook(backward_hook)
        self.target_layer.register_forward_hook(forward_hook)
    
    def generate(self, input_tensor, target_class=None):
        self.model.zero_grad()
        output = self.model(input_tensor)
        
        if target_class is None:
            target_class = torch.argmax(output, dim=1).item()
        
        self.model.zero_grad()
        output[0, target_class].backward()
        
        gradients = self.gradients.detach().cpu().numpy()[0]
        activations = self.activations.detach().cpu().numpy()[0]
        
        weights = np.mean(gradients, axis=(1, 2))
        cam = np.zeros(activations.shape[1:], dtype=np.float32)
        
        for i, w in enumerate(weights):
            cam += w * activations[i]
        
        cam = np.maximum(cam, 0)
        cam = cv2.resize(cam, (224, 224))
        cam = (cam - np.min(cam)) / (np.max(cam) - np.min(cam) + 1e-8)
        
        return cam

class SkinAnalyzer:
    def __init__(self, model_path="saved_models/final_model.pth", data_dir="data"):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.data_dir = data_dir
        
        self.classes = ['acne', 'actinic_keratosis', 'basal_cell_carcinoma', 'rosacea']
        self.num_classes = 4
        
        self.model = SkinDiseaseClassifier(num_classes=self.num_classes)
        
        base_path = Path(__file__).parent.parent.parent
        full_model_path = os.path.join(str(base_path), model_path)
        checkpoint = torch.load(full_model_path, map_location=self.device)
        
        from collections import OrderedDict
        new_state_dict = OrderedDict()
        for k, v in checkpoint.items():
            name = k[7:] if k.startswith('module.') else k
            new_state_dict[name] = v
        
        self.model.load_state_dict(new_state_dict)
        self.model.to(self.device)
        self.model.eval()
        
        target_layer = self.model.backbone.features[-1]
        self.grad_cam = GradCAM(self.model, target_layer)
        
        print(f"Model loaded on {self.device}")
        print(f"Classes: {self.classes}")
    
    def _get_bounding_boxes_from_cam(self, cam, original_size, threshold=0.5):
        cam_resized = cv2.resize(cam, original_size)
        
        cam_normalized = (cam_resized - np.min(cam_resized)) / (np.max(cam_resized) - np.min(cam_resized) + 1e-8)
        
        binary_mask = (cam_normalized > threshold).astype(np.uint8)
        
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w * h > 1000:
                boxes.append({
                    'x': int(x / original_size[0] * 100),
                    'y': int(y / original_size[1] * 100),
                    'width': int(w / original_size[0] * 100),
                    'height': int(h / original_size[1] * 100),
                    'confidence': float(np.max(cam_normalized[y:y+h, x:x+w]))
                })
        
        return boxes[:3]
    
    def _create_heatmap_image(self, cam, original_image, alpha=0.5):
        cam_resized = cv2.resize(cam, original_image.size)
        cam_colored = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
        
        original_np = np.array(original_image)
        heatmap = cv2.addWeighted(original_np, 1 - alpha, cam_colored, alpha, 0)
        
        return Image.fromarray(heatmap)
    
    def analyze_image(self, image_bytes):
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        original_image = Image.open(image_bytes).convert('RGB')
        original_size = original_image.size
        
        image_tensor = transform(original_image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1).cpu().numpy()[0]
            max_confidence = np.max(probabilities)
            predicted_class_idx = np.argmax(probabilities)
            
            if max_confidence < 0.5:
                predicted_class = 'healthy'
                confidence = 1.0 - max_confidence
            else:
                predicted_class = self.classes[predicted_class_idx]
                confidence = float(probabilities[predicted_class_idx])
        
        all_probabilities = {
            'acne': float(probabilities[0]),
            'actinic_keratosis': float(probabilities[1]),
            'basal_cell_carcinoma': float(probabilities[2]),
            'rosacea': float(probabilities[3]),
            'healthy': 1.0 - max_confidence if max_confidence < 0.5 else 0.0
        }
        
        cam = None
        heatmap_base64 = None
        bounding_boxes = []
        
        if max_confidence >= 0.5:
            try:
                cam = self.grad_cam.generate(image_tensor, predicted_class_idx)
                
                heatmap_image = self._create_heatmap_image(cam, original_image, alpha=0.5)
                import base64
                import io
                buffer = io.BytesIO()
                heatmap_image.save(buffer, format='PNG')
                heatmap_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                bounding_boxes = self._get_bounding_boxes_from_cam(cam, original_size, threshold=0.5)
                for box in bounding_boxes:
                    box['label'] = predicted_class
                    box['disease_name'] = predicted_class
            except Exception as e:
                print(f"GradCAM error: {e}")
        
        return {
            'disease': predicted_class,
            'confidence': confidence,
            'all_probabilities': all_probabilities,
            'needs_doctor': predicted_class in ['basal_cell_carcinoma', 'actinic_keratosis'] and confidence > 0.7,
            'heatmap': f"data:image/png;base64,{heatmap_base64}" if heatmap_base64 else None,
            'bounding_boxes': bounding_boxes
        }

skin_analyzer = SkinAnalyzer()