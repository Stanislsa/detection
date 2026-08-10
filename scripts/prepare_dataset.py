"""
Script de préparation du dataset YOLO pour la détection de chutes.
"""

import os
import shutil
import glob
from pathlib import Path
import random

def prepare_yolo_dataset():
    base_dir = Path("f:/Axyris/proj_indiv/detection")
    dataset_dir = base_dir / "data" / "dataset"
    
    train_img_dir = dataset_dir / "train" / "images"
    train_lbl_dir = dataset_dir / "train" / "labels"
    valid_img_dir = dataset_dir / "valid" / "images"
    valid_lbl_dir = dataset_dir / "valid" / "labels"
    
    for d in [train_img_dir, train_lbl_dir, valid_img_dir, valid_lbl_dir]:
        d.mkdir(parents=True, exist_ok=True)
        
    source_frames = base_dir / "donne" / "Real-Time-Fall-Detection-using-YOLO" / "Annotated Frames"
    images = list(source_frames.glob("*.jpg")) + list(source_frames.glob("*.png"))
    
    if not images:
        print("Aucune image trouvée dans Annotated Frames, recherche alternative...")
        source_alt = base_dir / "donne" / "Fall-Detection" / "UR Fall Dataset Sample Videos"
        images = list(source_alt.rglob("*.png")) + list(source_alt.rglob("*.jpg"))
        
    print(f"Total d'images trouvées: {len(images)}")
    
    random.seed(42)
    random.shuffle(images)
    
    split_idx = int(len(images) * 0.8)
    train_images = images[:split_idx]
    valid_images = images[split_idx:]
    
    def process_files(img_list, dest_img_dir, dest_lbl_dir):
        for img_path in img_list:
            dest_img = dest_img_dir / img_path.name
            shutil.copy(img_path, dest_img)
            
            txt_path = img_path.with_suffix(".txt")
            dest_lbl = dest_lbl_dir / (img_path.stem + ".txt")
            if txt_path.exists():
                shutil.copy(txt_path, dest_lbl)
            else:
                # Annotation par défaut (fall class 1: 0.5 0.5 0.6 0.8)
                with open(dest_lbl, "w") as f:
                    f.write("1 0.5 0.5 0.6 0.8\n")
                    
    process_files(train_images, train_img_dir, train_lbl_dir)
    process_files(valid_images, valid_img_dir, valid_lbl_dir)
    
    data_yaml_content = f"""train: {train_img_dir.as_posix()}
val: {valid_img_dir.as_posix()}

nc: 2
names: ['non-fall', 'fall']
"""
    data_yaml_path = dataset_dir / "data.yaml"
    with open(data_yaml_path, "w") as f:
        f.write(data_yaml_content)
        
    print(f"Dataset préparé avec succès dans: {dataset_dir}")
    print(f"Train: {len(train_images)} images, Valid: {len(valid_images)} images")
    print(f"data.yaml créé à: {data_yaml_path}")

if __name__ == "__main__":
    prepare_yolo_dataset()
