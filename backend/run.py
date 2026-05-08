# C:\AiSkin\run.py
import os
import sys
import webbrowser
import time
import threading

def check_model():
    model_path = "saved_models/final_model.pth"
    if os.path.exists(model_path):
        print(f"Модель найдена: {model_path}")
        return True
    else:
        print(f"Модель не найдена: {model_path}")
        print("Сначала обучите модель: python train.py")
        return False

def check_dependencies():
    try:
        import fastapi
        import uvicorn
        import torch
        print("Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"Отсутствует зависимость: {e}")
        print("\nУстановите зависимости:")
        print("pip install fastapi uvicorn python-multipart pillow aiohttp beautifulsoup4")
        return False

def open_browser():
    time.sleep(2)
    webbrowser.open("http://localhost:8000")

def main():
    print("="*60)
    print("AI Skin Disease Classifier - Веб-приложение")
    print("="*60)
    print(f"Рабочая директория: {os.getcwd()}")
    print(f"Модель: saved_models/final_model.pth")
    print("="*60)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_model():
        response = input("\nПродолжить без модели? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("\nЗапуск веб-сервера на http://localhost:8000")
    print("Откройте браузер для использования приложения")
    print("Нажмите Ctrl+C для остановки\n")
    
    os.system("python -m uvicorn app.web_app:app --host 0.0.0.0 --port 8000 --reload")

if __name__ == "__main__":
    main()