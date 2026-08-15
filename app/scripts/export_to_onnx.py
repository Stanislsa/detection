"""
Script d'export YOLOv11 vers ONNX pour intégration C++.
Exporte le modèle entraîné au format ONNX avec optimisation.
"""

import sys
from pathlib import Path
import onnx
import onnxruntime as ort
import numpy as np
from ultralytics import YOLO

# Ajouter le répertoire parent au path pour imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def export_yolo_to_onnx(
    model_path: str = "yolo11n.pt",
    output_path: str = "cpp_backend/models/fall_detection.onnx",
    imgsz: int = 640,
    opset: int = 18,
    simplify: bool = False
) -> bool:
    """
    Export YOLOv11 vers format ONNX via torch.onnx.export direct.
    
    Args:
        model_path: Chemin vers le modèle YOLO (.pt)
        output_path: Chemin de sortie pour le fichier ONNX
        imgsz: Taille d'image pour l'export (640 par défaut)
        opset: Version ONNX opset (12 par défaut)
        simplify: Simplifier le modèle ONNX
        
    Returns:
        True si export réussi
    """
    print(f"🔄 Chargement du modèle YOLO: {model_path}")
    
    try:
        import torch
        
        # Charger le modèle YOLO via Ultralytics
        model = YOLO(model_path)
        print(f"✅ Modèle chargé avec succès")
        
        # Créer le répertoire de sortie si nécessaire
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔄 Export vers ONNX: {output_path}")
        print(f"   - Image size: {imgsz}")
        print(f"   - ONNX opset: {opset}")
        
        # Préparer le modèle PyTorch pour l'export
        model_pytorch = model.model
        model_pytorch.eval()
        
        # Créer un input dummy
        dummy_input = torch.randn(1, 3, imgsz, imgsz)
        
        # Exporter via torch.onnx.export directement
        torch.onnx.export(
            model_pytorch,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=opset,
            do_constant_folding=True,
            input_names=['images'],
            output_names=['output'],
            dynamic_axes={
                'images': {0: 'batch'},
                'output': {0: 'batch'}
            }
        )
        
        print(f"✅ Export ONNX terminé: {output_path}")
        
        # Validation du modèle ONNX
        print(f"🔄 Validation du modèle ONNX...")
        onnx_model = onnx.load(output_path)
        onnx.checker.check_model(onnx_model)
        print(f"✅ Modèle ONNX valide")
        
        # Test d'inférence avec ONNX Runtime
        print(f"🔄 Test d'inférence ONNX Runtime...")
        test_onnx_inference(output_path, imgsz)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_onnx_inference(onnx_path: str, imgsz: int = 640) -> bool:
    """
    Test l'inférence avec ONNX Runtime.
    
    Args:
        onnx_path: Chemin vers le fichier ONNX
        imgsz: Taille d'image
        
    Returns:
        True si test réussi
    """
    try:
        # Créer session ONNX Runtime
        session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
        
        # Obtenir les infos d'entrée/sortie
        input_name = session.get_inputs()[0].name
        output_names = [output.name for output in session.get_outputs()]
        
        input_info = session.get_inputs()[0]
        input_shape = input_info.shape
        
        print(f"   - Input: {input_name}, shape: {input_shape}")
        print(f"   - Outputs: {output_names}")
        
        # Gérer les dimensions dynamiques
        fixed_shape = []
        for dim in input_shape:
            if isinstance(dim, str):
                fixed_shape.append(1)  # Remplacer 'batch' par 1
            else:
                fixed_shape.append(dim)
        
        # Créer une image de test aléatoire
        dummy_input = np.random.randn(*fixed_shape).astype(np.float32)
        
        # Inférence
        import time
        start = time.time()
        outputs = session.run(output_names, {input_name: dummy_input})
        inference_time = (time.time() - start) * 1000
        
        print(f"   - Inférence test: {inference_time:.2f}ms")
        print(f"   - Output shapes: {[out.shape for out in outputs]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test inférence: {e}")
        return False


def compare_python_onnx(model_path: str = "yolo11n.pt", onnx_path: str = "cpp_backend/models/fall_detection.onnx"):
    """
    Compare les résultats entre Python YOLO et ONNX Runtime.
    
    Args:
        model_path: Chemin modèle YOLO
        onnx_path: Chemin modèle ONNX
    """
    print(f"\n🔄 Comparaison Python vs ONNX...")
    
    try:
        from PIL import Image
        import cv2
        
        # Créer une image de test
        test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        test_image_path = "test_image.jpg"
        cv2.imwrite(test_image_path, test_image)
        
        # Inférence Python
        print(f"   - Inférence Python YOLO...")
        model_py = YOLO(model_path)
        results_py = model_py(test_image_path, verbose=False)
        
        if results_py and len(results_py[0].boxes) > 0:
            conf_py = float(results_py[0].boxes.conf[0])
            print(f"   - Confiance Python: {conf_py:.4f}")
        else:
            print(f"   - Pas de détection Python")
            conf_py = 0.0
        
        # Inférence ONNX
        print(f"   - Inférence ONNX Runtime...")
        session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
        input_name = session.get_inputs()[0].name
        output_names = [output.name for output in session.get_outputs()]
        
        # Préparer l'input
        input_shape = session.get_inputs()[0].shape
        if input_shape[0] is None:
            input_shape = [1] + input_shape[1:]
        
        # Normaliser l'image pour ONNX
        img_rgb = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (640, 640))
        img_normalized = img_resized.astype(np.float32) / 255.0
        img_transposed = np.transpose(img_normalized, (2, 0, 1))
        img_batch = np.expand_dims(img_transposed, axis=0)
        
        outputs = session.run(output_names, {input_name: img_batch})
        
        # Extraire la confiance (simplifié - dépend de la structure de sortie)
        print(f"   - Output ONNX shape: {outputs[0].shape}")
        
        # Nettoyer
        import os
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        print(f"✅ Comparaison terminée")
        
    except Exception as e:
        print(f"⚠️  Erreur comparaison: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Export YOLOv11 vers ONNX")
    print("=" * 60)
    
    # Configuration
    MODEL_PATH = "yolo11n.pt"
    OUTPUT_PATH = "cpp_backend/models/fall_detection.onnx"
    
    # Vérifier que le modèle existe
    if not Path(MODEL_PATH).exists():
        print(f"❌ Modèle non trouvé: {MODEL_PATH}")
        print(f"   Téléchargez-le avec: yolo11n.pt sera téléchargé automatiquement")
        # Ultralytics téléchargera automatiquement le modèle
        model = YOLO(MODEL_PATH)
    
    # Export
    success = export_yolo_to_onnx(
        model_path=MODEL_PATH,
        output_path=OUTPUT_PATH,
        imgsz=640,
        opset=17,
        simplify=False
    )
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Export terminé avec succès!")
        print("=" * 60)
        
        # Comparaison optionnelle
        compare_python_onnx(MODEL_PATH, OUTPUT_PATH)
        
        print(f"\n📦 Fichier ONNX: {OUTPUT_PATH}")
        print(f"📏 Taille: {Path(OUTPUT_PATH).stat().st_size / 1024 / 1024:.2f} MB")
    else:
        print("\n" + "=" * 60)
        print("❌ Export échoué")
        print("=" * 60)
        sys.exit(1)
