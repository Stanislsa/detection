"""
Script de démarrage de l'entraînement YOLO via TrainingService.
"""

import sys
import os
from pathlib import Path

# Activer KMP_DUPLICATE_LIB_OK
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.training_service import get_training_service, TrainingConfig

def main():
    service = get_training_service()
    
    data_yaml = Path("f:/Axyris/proj_indiv/detection/data/dataset/data.yaml")
    dataset_path = Path("f:/Axyris/proj_indiv/detection/data/dataset")
    
    if not data_yaml.exists():
        print(f"Erreur: {data_yaml} introuvable.")
        return
        
    validation = service.validate_dataset(str(dataset_path))
    print("Résultat de validation du dataset:", validation)
    
    config = TrainingConfig(
        dataset_path=str(dataset_path),
        data_yaml=str(data_yaml),
        model_name="yolo11n.pt",
        epochs=5,
        imgsz=640,
        batch=8,
        optimizer="Adam",
        lr0=0.001,
        patience=5,
        device="cpu",
        project="models",
        name="trained_model",
        save=True,
        verbose=True
    )
    
    def log_cb(msg):
        print(f"[TRAINING LOG] {msg}")
        
    def progress_cb(current, total):
        print(f"[PROGRESS] Epoch {current}/{total}")

    service.set_callbacks(
        progress_callback=progress_cb,
        log_callback=log_cb
    )
    
    print("\n--- DÉMARRAGE DE L'ENTRAÎNEMENT YOLO ---")
    started = service.start_training(config)
    if started:
        print("Entraînement démarré en arrière-plan. Attente de la fin...")
        if service._training_thread:
            service._training_thread.join()
        print("--- ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS ---")
    else:
        print("Échec du démarrage de l'entraînement.")

if __name__ == "__main__":
    main()
