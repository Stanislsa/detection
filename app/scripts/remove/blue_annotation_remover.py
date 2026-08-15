"""
Suppression des annotations YOLO bleues avec LaMa.

Étapes :
    1. Détection des pixels bleus dans HSV
    2. Construction du masque
    3. Agrandissement très léger du masque
    4. Reconstruction avec LaMa
    5. Sauvegarde de l'image reconstruite

LaMa est utilisé à la place de cv2.inpaint()
pour obtenir une reconstruction plus détaillée.
"""

import cv2
import numpy as np

from pathlib import Path
from PIL import Image

import time


# ============================================================
# IMPORT LAMA
# ============================================================

from simple_lama_inpainting import SimpleLama


# ============================================================
# CONFIGURATION
# ============================================================

TEST_IMAGE = Path(
    r"F:\Axyris\proj_indiv\detection\donne"
    r"\Real-Time-Fall-Detection-using-YOLO"
    r"\Annotated Frames"
    r"\A-20099_jpg.rf.c46f490b45d47a0e8c2c641749a53a00.jpg"
)

OUTPUT_DIR = Path(
    r"F:\Axyris\proj_indiv\detection\app\scripts\remove\output"
)


# ============================================================
# DÉTECTION DU BLEU
# ============================================================

# Paramètres ajustés selon recommandations
# Plus permissifs pour capturer les variations de bleu dues à la compression JPEG
LOWER_BLUE = np.array(
    [85, 50, 30],
    dtype=np.uint8
)

UPPER_BLUE = np.array(
    [145, 255, 255],
    dtype=np.uint8
)


# ============================================================
# PARAMÈTRES DU MASQUE
# ============================================================

# ATTENTION :
# Plus cette valeur est élevée, plus on supprime de pixels
# autour du cadre.
#
# Pour ton cas, commencer avec 1 ou 2 est préférable.
DILATE_SIZE = 3

DILATE_ITERATIONS = 1

MIN_BLUE_PIXELS = 100


# ============================================================
# CRÉATION DU DOSSIER
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# INITIALISATION LAMA
# ============================================================

print()
print("=" * 60)
print("INITIALISATION DE LAMA")
print("=" * 60)
print()

lama = SimpleLama()

print("LaMa prêt.")
print()


# ============================================================
# DÉTECTION DES ANNOTATIONS BLEUES
# ============================================================

def detect_blue_annotation(image):

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    # --------------------------------------------------------
    # Détection du bleu
    # --------------------------------------------------------

    mask = cv2.inRange(
        hsv,
        LOWER_BLUE,
        UPPER_BLUE
    )

    # --------------------------------------------------------
    # Nombre de pixels bleus
    # --------------------------------------------------------

    blue_pixels = cv2.countNonZero(
        mask
    )

    if blue_pixels < MIN_BLUE_PIXELS:

        return (
            mask,
            False,
            None
        )

    # --------------------------------------------------------
    # Recherche des contours
    # --------------------------------------------------------

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:

        return (
            mask,
            False,
            None
        )

    # --------------------------------------------------------
    # Bounding box globale
    # --------------------------------------------------------

    height, width = image.shape[:2]

    x_min = width
    y_min = height

    x_max = 0
    y_max = 0

    valid_contours = 0

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        if area < 2:
            continue

        x, y, w, h = cv2.boundingRect(
            contour
        )

        x_min = min(
            x_min,
            x
        )

        y_min = min(
            y_min,
            y
        )

        x_max = max(
            x_max,
            x + w
        )

        y_max = max(
            y_max,
            y + h
        )

        valid_contours += 1

    if valid_contours == 0:

        return (
            mask,
            False,
            None
        )

    bbox = (
        x_min,
        y_min,
        x_max,
        y_max
    )

    return (
        mask,
        True,
        bbox
    )


# ============================================================
# CONSTRUCTION DU MASQUE (VERSION AMÉLIORÉE)
# ============================================================

def prepare_mask(mask):

    # ========================================================
    # 1. FERMETURE DES PETITES INTERRUPTIONS
    # ========================================================

    close_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (5, 5)
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        close_kernel,
        iterations=2
    )

    # ========================================================
    # 2. DILATATION
    # ========================================================

    # On élargit suffisamment pour supprimer aussi
    # les pixels bleus résiduels et l'anti-aliasing.

    dilate_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (5, 5)
    )

    mask = cv2.dilate(
        mask,
        dilate_kernel,
        iterations=2
    )

    # ========================================================
    # 3. PETITE DILATATION SUPPLÉMENTAIRE
    # ========================================================

    dilate_kernel_2 = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    mask = cv2.dilate(
        mask,
        dilate_kernel_2,
        iterations=1
    )

    return mask


# ============================================================
# PRÉPARATION DU MASQUE YOLO (VERSION SPÉCIFIQUE)
# ============================================================

def prepare_yolo_mask(image):

    # ========================================================
    # CONVERSION HSV
    # ========================================================

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    # ========================================================
    # MASQUE BLEU
    # ========================================================

    lower_blue = np.array(
        [85, 50, 30],
        dtype=np.uint8
    )

    upper_blue = np.array(
        [145, 255, 255],
        dtype=np.uint8
    )

    mask = cv2.inRange(
        hsv,
        lower_blue,
        upper_blue
    )

    # ========================================================
    # FERMETURE
    # ========================================================

    kernel_close = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (5, 5)
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel_close,
        iterations=2
    )

    # ========================================================
    # DILATATION
    # ========================================================

    kernel_dilate = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (5, 5)
    )

    mask = cv2.dilate(
        mask,
        kernel_dilate,
        iterations=2
    )

    # ========================================================
    # SUPPRESSION DES PETITS BRUITS
    # ========================================================

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        mask,
        connectivity=8
    )

    clean_mask = np.zeros_like(mask)

    for i in range(1, num_labels):

        area = stats[i, cv2.CC_STAT_AREA]

        if area >= 10:

            clean_mask[
                labels == i
            ] = 255

    return clean_mask


# ============================================================
# RECONSTRUCTION LAMA
# ============================================================

def reconstruct_with_lama(
    image_bgr,
    mask
):

    # --------------------------------------------------------
    # OpenCV BGR -> RGB
    # --------------------------------------------------------

    image_rgb = cv2.cvtColor(
        image_bgr,
        cv2.COLOR_BGR2RGB
    )

    # --------------------------------------------------------
    # Conversion en PIL
    # --------------------------------------------------------

    image_pil = Image.fromarray(
        image_rgb
    )

    mask_pil = Image.fromarray(
        mask
    ).convert("L")

    # --------------------------------------------------------
    # LaMa
    # --------------------------------------------------------

    result_pil = lama(
        image_pil,
        mask_pil
    )

    # --------------------------------------------------------
    # PIL -> OpenCV
    # --------------------------------------------------------

    result_rgb = np.array(
        result_pil
    )

    result_bgr = cv2.cvtColor(
        result_rgb,
        cv2.COLOR_RGB2BGR
    )

    return result_bgr


# ============================================================
# TRAITEMENT IMAGE
# ============================================================

def clean_image(
    input_path,
    output_path
):

    try:

        # ----------------------------------------------------
        # Lecture
        # ----------------------------------------------------

        image = cv2.imread(
            str(input_path),
            cv2.IMREAD_COLOR
        )

        if image is None:

            return {
                "status": "ERROR",
                "detected": False,
                "bbox": None,
                "message": (
                    "Impossible de lire l'image"
                )
            }

        # ----------------------------------------------------
        # Détection
        # ----------------------------------------------------

        mask, detected, bbox = (
            detect_blue_annotation(
                image
            )
        )

        # ----------------------------------------------------
        # Aucun cadre
        # ----------------------------------------------------

        if not detected:

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            success = cv2.imwrite(
                str(output_path),
                image
            )

            if not success:

                return {
                    "status": "ERROR",
                    "detected": False,
                    "bbox": None,
                    "message": (
                        "Erreur d'écriture"
                    )
                }

            return {
                "status": "OK",
                "detected": False,
                "bbox": None,
                "message": (
                    "Aucun cadre bleu"
                )
            }

        # ----------------------------------------------------
        # Préparation masque YOLO (version spécifique)
        # ----------------------------------------------------

        mask = prepare_yolo_mask(
            image
        )

        # ----------------------------------------------------
        # Reconstruction LaMa
        # ----------------------------------------------------

        print(
            "Reconstruction LaMa..."
        )

        cleaned = reconstruct_with_lama(
            image,
            mask
        )

        # ----------------------------------------------------
        # Sauvegarde
        # ----------------------------------------------------

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        success = cv2.imwrite(
            str(output_path),
            cleaned
        )

        if not success:

            return {
                "status": "ERROR",
                "detected": True,
                "bbox": bbox,
                "message": (
                    "Erreur d'écriture"
                )
            }

        return {
            "status": "OK",
            "detected": True,
            "bbox": bbox,
            "message": (
                "Cadre supprimé avec LaMa"
            )
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "detected": False,
            "bbox": None,
            "message": str(e)
        }


# ============================================================
# MAIN
# ============================================================

def main():

    start_time = time.time()

    print("=" * 60)
    print("SUPPRESSION DU CADRE YOLO")
    print("RECONSTRUCTION AVEC LAMA")
    print("=" * 60)

    print()
    print(
        "Image source :"
    )

    print(
        TEST_IMAGE
    )

    print()

    print(
        "Dossier sortie :"
    )

    print(
        OUTPUT_DIR
    )

    print()

    # --------------------------------------------------------
    # Vérification
    # --------------------------------------------------------

    if not TEST_IMAGE.exists():

        print(
            "ERREUR : image introuvable."
        )

        return

    # --------------------------------------------------------
    # Sortie
    # --------------------------------------------------------

    output_path = (
        OUTPUT_DIR
        / f"{TEST_IMAGE.stem}_clean"
        f"{TEST_IMAGE.suffix}"
    )

    # --------------------------------------------------------
    # Traitement
    # --------------------------------------------------------

    result = clean_image(
        TEST_IMAGE,
        output_path
    )

    # --------------------------------------------------------
    # Résultat
    # --------------------------------------------------------

    elapsed = (
        time.time()
        - start_time
    )

    print()
    print("=" * 60)
    print("TRAITEMENT TERMINÉ")
    print("=" * 60)

    print(
        f"Statut        : "
        f"{result['status']}"
    )

    print(
        f"Cadre détecté : "
        f"{result['detected']}"
    )

    print(
        f"Bounding box  : "
        f"{result['bbox']}"
    )

    print(
        f"Message       : "
        f"{result['message']}"
    )

    print(
        f"Temps         : "
        f"{elapsed:.2f} secondes"
    )

    print()

    print(
        "Image générée :"
    )

    print(
        output_path
    )


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":

    main()