"""
Suppression des annotations YOLO bleues dans une vidéo.

Pipeline :

    Vidéo
       |
       v
    Frame
       |
       v
    Détection du bleu HSV
       |
       v
    Construction du masque
       |
       v
    Dilatation / nettoyage du masque
       |
       v
    Reconstruction avec LaMa
       |
       v
    Frame nettoyée
       |
       v
    Vidéo de sortie

LaMa est initialisé UNE SEULE FOIS et réutilisé pour
toutes les frames.

Important :
    Cette méthode reconstruit les pixels masqués.
    Elle ne peut pas récupérer exactement les pixels
    originaux qui ont été remplacés par le cadre YOLO.
"""

import cv2
import numpy as np

from pathlib import Path
from PIL import Image

from simple_lama_inpainting import SimpleLama

import subprocess
import shutil
import time


# ============================================================
# DOSSIERS
# ============================================================

INPUT_DIR = Path(
    r"F:\Axyris\proj_indiv\detection\donne"
    r"\Real-Time-Fall-Detection-using-YOLO"
    r"\Result videos"
)

OUTPUT_DIR = Path(
    r"F:\Axyris\proj_indiv\detection\app"
    r"\scripts\remove\output"
)

# Extensions acceptées
VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi"
}

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# RECHERCHE DES VIDÉOS
# ============================================================

def get_videos(input_dir):
    """
    Retourne toutes les vidéos .mp4 et .avi
    présentes directement dans le dossier.
    """

    videos = []

    for path in input_dir.iterdir():

        if not path.is_file():
            continue

        if path.suffix.lower() in VIDEO_EXTENSIONS:
            videos.append(path)

    # Tri alphabétique
    videos.sort(
        key=lambda x: x.name.lower()
    )

    return videos


# ============================================================
# DÉTECTION DU BLEU
# ============================================================

# Valeurs volontairement assez permissives afin de détecter :
#
# - bleu pur
# - bleu clair
# - bleu foncé
# - anti-aliasing
# - variations dues à la compression vidéo

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

# Fermeture morphologique
CLOSE_KERNEL_SIZE = 5
CLOSE_ITERATIONS = 2

# Dilatation
DILATE_KERNEL_SIZE = 5
DILATE_ITERATIONS = 2

# Suppression des petites composantes
MIN_COMPONENT_AREA = 10

# Nombre minimum de pixels bleus nécessaire pour
# considérer la frame comme annotée
MIN_BLUE_PIXELS = 100


# ============================================================
# PARAMÈTRES VIDÉO
# ============================================================

# Codec utilisé pour la vidéo temporaire.
#
# mp4v est généralement disponible avec OpenCV.
VIDEO_CODEC = "mp4v"


# ============================================================
# CRÉATION DU DOSSIER
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# DÉTECTION DU BLEU
# ============================================================

def detect_blue_mask(frame):
    """
    Détecte les pixels bleus susceptibles d'appartenir
    aux annotations YOLO.

    Retourne :
        mask
        blue_pixels
    """

    # --------------------------------------------------------
    # BGR -> HSV
    # --------------------------------------------------------

    hsv = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2HSV
    )

    # --------------------------------------------------------
    # Seuil bleu
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

    return mask, blue_pixels


# ============================================================
# CONSTRUCTION DU MASQUE
# ============================================================

def prepare_yolo_mask(
    mask
):
    """
    Nettoie et agrandit le masque.

    Le masque est volontairement légèrement plus grand
    que le cadre bleu afin de supprimer également :

        - anti-aliasing
        - bordures
        - pixels bleus résiduels
        - traces dues à la compression vidéo
    """

    # ========================================================
    # 1. FERMETURE MORPHOLOGIQUE
    # ========================================================

    close_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (
            CLOSE_KERNEL_SIZE,
            CLOSE_KERNEL_SIZE
        )
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        close_kernel,
        iterations=CLOSE_ITERATIONS
    )

    # ========================================================
    # 2. DILATATION
    # ========================================================

    dilate_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (
            DILATE_KERNEL_SIZE,
            DILATE_KERNEL_SIZE
        )
    )

    mask = cv2.dilate(
        mask,
        dilate_kernel,
        iterations=DILATE_ITERATIONS
    )

    # ========================================================
    # 3. SUPPRESSION DES PETITES COMPOSANTES
    # ========================================================

    num_labels, labels, stats, _ = (
        cv2.connectedComponentsWithStats(
            mask,
            connectivity=8
        )
    )

    clean_mask = np.zeros_like(
        mask
    )

    for i in range(
        1,
        num_labels
    ):

        area = stats[
            i,
            cv2.CC_STAT_AREA
        ]

        if area >= MIN_COMPONENT_AREA:

            clean_mask[
                labels == i
            ] = 255

    return clean_mask


# ============================================================
# RECONSTRUCTION LAMA
# ============================================================

def reconstruct_with_lama(
    lama,
    frame,
    mask
):
    """
    Reconstruit les zones masquées avec LaMa.
    """

    # --------------------------------------------------------
    # OpenCV BGR -> RGB
    # --------------------------------------------------------

    frame_rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # --------------------------------------------------------
    # NumPy -> PIL
    # --------------------------------------------------------

    image_pil = Image.fromarray(
        frame_rgb
    )

    mask_pil = Image.fromarray(
        mask
    ).convert("L")

    # --------------------------------------------------------
    # Reconstruction
    # --------------------------------------------------------

    result_pil = lama(
        image_pil,
        mask_pil
    )

    # --------------------------------------------------------
    # PIL -> NumPy
    # --------------------------------------------------------

    result_rgb = np.array(
        result_pil
    )

    # --------------------------------------------------------
    # RGB -> BGR
    # --------------------------------------------------------

    result_bgr = cv2.cvtColor(
        result_rgb,
        cv2.COLOR_RGB2BGR
    )

    return result_bgr


# ============================================================
# DÉTECTION DE FFMPEG
# ============================================================

def find_ffmpeg():
    """
    Cherche FFmpeg dans le PATH.
    """

    return shutil.which(
        "ffmpeg"
    )


# ============================================================
# AJOUT DU SON
# ============================================================

def copy_audio(
    original_video,
    silent_video,
    final_video,
    ffmpeg_path
):
    """
    Copie la piste audio de la vidéo originale vers
    la vidéo nettoyée.

    La vidéo nettoyée est réencodée.
    L'audio est simplement copié sans modification.
    """

    command = [
        ffmpeg_path,

        "-y",

        "-i",
        str(silent_video),

        "-i",
        str(original_video),

        "-map",
        "0:v:0",

        "-map",
        "1:a?",

        "-c:v",
        "copy",

        "-c:a",
        "copy",

        "-shortest",

        str(final_video)
    ]

    print()
    print(
        "Ajout de la piste audio..."
    )

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:

        print()
        print(
            "ATTENTION : impossible de copier "
            "la piste audio."
        )

        print(
            result.stderr
        )

        return False

    return True


# ============================================================
# TRAITEMENT DE LA VIDÉO
# ============================================================

def clean_video(
    input_video,
    temporary_output,
    lama
):

    # ========================================================
    # OUVERTURE
    # ========================================================

    cap = cv2.VideoCapture(
        str(input_video)
    )

    if not cap.isOpened():

        raise RuntimeError(
            f"Impossible d'ouvrir la vidéo : "
            f"{input_video}"
        )

    # ========================================================
    # INFORMATIONS
    # ========================================================

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    width = int(
        cap.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        cap.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    duration = (
        total_frames / fps
        if fps > 0
        else 0
    )

    print()
    print("=" * 70)
    print("INFORMATIONS VIDÉO")
    print("=" * 70)

    print(
        f"Résolution       : "
        f"{width} x {height}"
    )

    print(
        f"FPS              : "
        f"{fps:.3f}"
    )

    print(
        f"Frames           : "
        f"{total_frames}"
    )

    print(
        f"Durée            : "
        f"{duration:.2f} secondes"
    )

    print()

    # ========================================================
    # VIDÉO TEMPORAIRE
    # ========================================================

    temp_video = temporary_output

    # ========================================================
    # WRITER
    # ========================================================

    fourcc = cv2.VideoWriter_fourcc(
        *VIDEO_CODEC
    )

    writer = cv2.VideoWriter(
        str(temp_video),
        fourcc,
        fps,
        (
            width,
            height
        )
    )

    if not writer.isOpened():

        cap.release()

        raise RuntimeError(
            "Impossible de créer "
            "la vidéo de sortie."
        )

    # ========================================================
    # STATISTIQUES
    # ========================================================

    processed_frames = 0

    frames_with_blue = 0

    frames_without_blue = 0

    errors = 0

    start_time = time.time()

    # ========================================================
    # TRAITEMENT
    # ========================================================

    print("=" * 70)
    print("TRAITEMENT DE LA VIDÉO")
    print("=" * 70)
    print()

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        processed_frames += 1

        try:

            # =================================================
            # DÉTECTION BLEU
            # =================================================

            raw_mask, blue_pixels = (
                detect_blue_mask(
                    frame
                )
            )

            # =================================================
            # AUCUNE ANNOTATION
            # =================================================

            if blue_pixels < MIN_BLUE_PIXELS:

                frames_without_blue += 1

                writer.write(
                    frame
                )

            # =================================================
            # ANNOTATION DÉTECTÉE
            # =================================================

            else:

                frames_with_blue += 1

                # ---------------------------------------------
                # Préparation du masque
                # ---------------------------------------------

                mask = prepare_yolo_mask(
                    raw_mask
                )

                # ---------------------------------------------
                # Reconstruction
                # ---------------------------------------------

                cleaned_frame = (
                    reconstruct_with_lama(
                        lama,
                        frame,
                        mask
                    )
                )

                # ---------------------------------------------
                # Écriture
                # ---------------------------------------------

                writer.write(
                    cleaned_frame
                )

        except Exception as e:

            errors += 1

            print()
            print(
                f"Erreur frame "
                f"{processed_frames} : "
                f"{e}"
            )

            # En cas d'erreur, conserver
            # la frame originale plutôt
            # que perdre une frame.
            writer.write(
                frame
            )

        # =====================================================
        # PROGRESSION
        # =====================================================

        if (
            processed_frames % 10 == 0
            or processed_frames == total_frames
        ):

            elapsed = (
                time.time()
                - start_time
            )

            if elapsed > 0:

                speed = (
                    processed_frames
                    / elapsed
                )

            else:

                speed = 0

            if total_frames > 0:

                percent = (
                    processed_frames
                    / total_frames
                ) * 100

            else:

                percent = 0

            remaining_frames = (
                total_frames
                - processed_frames
            )

            if speed > 0:

                remaining_seconds = (
                    remaining_frames
                    / speed
                )

            else:

                remaining_seconds = 0

            print(
                f"\r"
                f"Progression : "
                f"{percent:6.2f}% | "
                f"Frame : "
                f"{processed_frames}/"
                f"{total_frames} | "
                f"Vitesse : "
                f"{speed:.2f} FPS | "
                f"ETA : "
                f"{remaining_seconds:.0f}s",
                end="",
                flush=True
            )

    print()

    # ========================================================
    # FERMETURE
    # ========================================================

    cap.release()

    writer.release()

    elapsed = (
        time.time()
        - start_time
    )

    # ========================================================
    # STATISTIQUES
    # ========================================================

    print()
    print("=" * 70)
    print("TRAITEMENT TERMINÉ")
    print("=" * 70)

    print(
        f"Frames traitées       : "
        f"{processed_frames}"
    )

    print(
        f"Frames avec cadre     : "
        f"{frames_with_blue}"
    )

    print(
        f"Frames sans cadre     : "
        f"{frames_without_blue}"
    )

    print(
        f"Erreurs               : "
        f"{errors}"
    )

    print(
        f"Temps                 : "
        f"{elapsed:.2f} secondes"
    )

    if elapsed > 0:

        print(
            f"Vitesse moyenne      : "
            f"{processed_frames / elapsed:.2f} FPS"
        )

    print()

    return temp_video


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

def main():

    global_start = time.time()

    print("=" * 70)
    print("SUPPRESSION DES CADRES YOLO - TRAITEMENT BATCH")
    print("RECONSTRUCTION AVEC LAMA")
    print("=" * 70)

    print()

    # ========================================================
    # RÉCUPÉRATION DES VIDÉOS
    # ========================================================

    videos = get_videos(INPUT_DIR)

    if not videos:

        print(
            "Aucune vidéo trouvée dans :"
        )

        print(
            INPUT_DIR
        )

        return

    print(
        f"Vidéos trouvées : "
        f"{len(videos)}"
    )

    print()

    # ========================================================
    # INITIALISATION DE LAMA
    # ========================================================

    print("=" * 70)
    print("INITIALISATION DE LAMA")
    print("=" * 70)
    print()

    lama = SimpleLama()

    print(
        "LaMa prêt."
    )

    print()

    # ========================================================
    # DÉTECTION FFMPEG
    # ========================================================

    ffmpeg = find_ffmpeg()

    if ffmpeg is None:

        print()
        print(
            "FFmpeg non trouvé."
        )

        print(
            "Les vidéos seront conservées "
            "sans piste audio."
        )

        print()

    # ========================================================
    # TRAITEMENT DES VIDÉOS
    # ========================================================

    print("=" * 70)
    print("TRAITEMENT DES VIDÉOS")
    print("=" * 70)
    print()

    processed = 0
    skipped = 0
    failed = 0

    for i, input_video in enumerate(videos, 1):

        print()
        print("=" * 70)
        print(
            f"VIDÉO {i}/{len(videos)}"
        )
        print("=" * 70)

        print(
            f"Fichier : "
            f"{input_video.name}"
        )

        print()

        # --------------------------------------------------------
        # Nom de sortie
        # --------------------------------------------------------

        output_video = (
            OUTPUT_DIR
            / f"{input_video.stem}_clean.mp4"
        )

        # --------------------------------------------------------
        # Vérifier si déjà traitée
        # --------------------------------------------------------

        if output_video.exists():

            print(
                "Déjà traitée (sortie existe)."
            )

            skipped += 1

            # Supprimer l'original si la sortie existe
            print()
            print(
                "Suppression de la vidéo originale..."
            )

            try:

                input_video.unlink()

                print(
                    "Original supprimé."
                )

                processed += 1

            except Exception as e:

                print(
                    "ATTENTION : impossible "
                    "de supprimer l'original :"
                )

                print(e)

                # La vidéo a quand même été traitée.
                processed += 1

            continue

        # --------------------------------------------------------
        # Traitement
        # --------------------------------------------------------

        try:

            temp_video = OUTPUT_DIR / f"{input_video.stem}_temp.mp4"

            clean_video(
                input_video,
                temp_video,
                lama
            )

        except Exception as e:

            print()
            print(
                "ERREUR FATALE :"
            )

            print(e)

            failed += 1
            continue

        # --------------------------------------------------------
        # AUDIO
        # --------------------------------------------------------

        if ffmpeg is not None:

            success = copy_audio(
                input_video,
                temp_video,
                output_video,
                ffmpeg
            )

            if success:

                try:

                    temp_video.unlink()

                except Exception:
                    pass

            else:

                output_video = temp_video

        else:

            output_video = temp_video

        # --------------------------------------------------------
        # Vérification et suppression de l'original
        # --------------------------------------------------------

        if output_video.exists():

            print()
            print(
                "Suppression de la vidéo originale..."
            )

            try:

                input_video.unlink()

                print(
                    "Original supprimé."
                )

                processed += 1

            except Exception as e:

                print(
                    "ATTENTION : impossible "
                    "de supprimer l'original :"
                )

                print(e)

                # La vidéo a quand même été traitée.
                processed += 1

        else:

            print()
            print(
                "ATTENTION : la vidéo de sortie "
                "n'a pas été créée."
            )

            failed += 1

        print()
        print(
            "Vidéo nettoyée :"
        )

        print(
            output_video
        )

    # ========================================================
    # RÉSUMÉ
    # ========================================================

    total_time = (
        time.time()
        - global_start
    )

    print()
    print()
    print("=" * 70)
    print("TRAITEMENT GLOBAL TERMINÉ")
    print("=" * 70)

    print()

    print(
        f"Vidéos trouvées       : "
        f"{len(videos)}"
    )

    print(
        f"Vidéos traitées       : "
        f"{processed}"
    )

    print(
        f"Déjà traitées         : "
        f"{skipped}"
    )

    print(
        f"Échecs                : "
        f"{failed}"
    )

    print(
        f"Temps total           : "
        f"{total_time:.2f} secondes"
    )

    print()

    print(
        "Dossier des résultats :"
    )

    print(
        OUTPUT_DIR
    )

    print()


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":

    main()
