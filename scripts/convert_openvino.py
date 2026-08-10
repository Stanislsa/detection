"""
Script de conversion de modèle YOLO vers OpenVINO.

Optimisation pour CPU Intel (ThinkPad i5).
Divise par 2-3 le temps d'inférence.

Usage:
    python scripts/convert_openvino.py --model yolo11n.pt
    python scripts/convert_openvino.py --model yolo11s.pt --output ./models
"""

import argparse
from pathlib import Path
from ultralytics import YOLO


def convert_to_openvino(
    model_path: str,
    dynamic: bool = True,
    half: bool = True
):
    """
    Convertit un modèle YOLO vers OpenVINO.
    
    Args:
        model_path: Chemin du modèle YOLO (.pt)
        dynamic: Forme dynamique des tenseurs
        half: Précision FP16 (plus rapide)
    """
    print(f"Conversion de {model_path} vers OpenVINO...")
    print(f"Configuration: dynamic={dynamic}, half={half}")
    
    # Charger le modèle
    print("Chargement du modèle...")
    model = YOLO(model_path)
    
    # Exporter vers OpenVINO
    print("Exportation vers OpenVINO...")
    output_path = model.export(
        format="openvino",
        dynamic=dynamic,
        half=half
    )
    
    print(f"\n✓ Conversion réussie!")
    print(f"Modèle OpenVINO créé: {output_path}")
    print(f"\nUtilisation:")
    print(f"  model = YOLO('{output_path}')")
    print(f"  results = model('video.mp4', device='cpu')")
    
    return output_path


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Convertir YOLO vers OpenVINO pour optimisation CPU Intel"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="yolo11n.pt",
        help="Modèle YOLO à convertir (défaut: yolo11n.pt)"
    )
    
    parser.add_argument(
        "--static",
        action="store_true",
        help="Utiliser forme statique au lieu de dynamique"
    )
    
    parser.add_argument(
        "--fp32",
        action="store_true",
        help="Utiliser FP32 au lieu de FP16"
    )
    
    args = parser.parse_args()
    
    # Vérifier que le modèle existe
    model_path = Path(args.model)
    if not model_path.exists():
        print(f"Erreur: Le modèle {args.model} n'existe pas")
        print("Téléchargement automatique...")
    
    # Convertir
    convert_to_openvino(
        model_path=str(model_path),
        dynamic=not args.static,
        half=not args.fp32
    )


if __name__ == "__main__":
    main()
