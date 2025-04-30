# processing_utils.py

import numpy as np
import cv2 # OpenCV
import logging
import os # Needed for os.getpid() in logging example
from pathlib import Path

# --- Constants used within the functions ---
# These should ideally match the values in your main notebook's configuration cell.
# Alternatively, modify process_parasite_pair to accept these as arguments.
CANCER_THRESHOLD = 0.10
SAVE_FORMAT = ".png"
SAVE_PARAMS_PNG = [cv2.IMWRITE_PNG_COMPRESSION, 9] # Example for PNG

def load_image_as_mask(filepath, threshold_value, invert=False):
    """
    Loads an image using OpenCV and converts it to a boolean mask.
    Assumes grayscale input.
    - For microscope: Pixels <= threshold_value become True (parasite).
    - For dye: Pixels > threshold_value become True (dye).
    If invert=True, the logic is flipped.

    Returns None if loading fails.
    """
    try:
        # Using IMREAD_UNCHANGED might be better if inputs could be 1-bit,
        # but IMREAD_GRAYSCALE is safer if they might be 8-bit grayscale.
        img = cv2.imread(str(filepath), cv2.IMREAD_GRAYSCALE)
        if img is None:
            # Use logger associated with the current process
            # Basic logging might work if root logger configured before pool start
            logging.warning(f"[Worker {os.getpid()}] Could not load image: {filepath}")
            return None

        if invert:
            mask = img > threshold_value
        else:
            mask = img <= threshold_value # e.g., 0 for black parasite

        # Ensure output is boolean numpy array
        return mask.astype(bool)
    except Exception as e:
        logging.error(f"[Worker {os.getpid()}] Error loading/masking file {filepath}: {e}")
        return None


def process_parasite_pair(microscope_path_str, dye_path_str, output_dir_microscope_str, output_dir_dye_cancerous_str):
    """
    Processes a single pair of microscope and dye images.
    Accepts paths/dirs as strings for reliable pickling across processes.
    """
    microscope_path = Path(microscope_path_str)
    dye_path = Path(dye_path_str)
    output_dir_microscope = Path(output_dir_microscope_str)
    output_dir_dye_cancerous = Path(output_dir_dye_cancerous_str)

    parasite_id = microscope_path.stem.replace("_microscope", "") # Assumes naming convention
    # Logging within the worker process
    logging.info(f"[Worker {os.getpid()}] Processing parasite: {parasite_id}")

    # --- Load Images ---
    # Pass appropriate threshold values based on expected image format
    microscope_mask = load_image_as_mask(microscope_path, threshold_value=128, invert=False) # Example: Pixels <= 128 are parasite
    dye_mask = load_image_as_mask(dye_path, threshold_value=128, invert=True) # Example: Pixels > 128 are dye

    if microscope_mask is None or dye_mask is None:
        logging.error(f"[Worker {os.getpid()}] Failed to load masks for {parasite_id}. Skipping.")
        return None # Indicate error

    if microscope_mask.shape != dye_mask.shape:
         logging.error(f"[Worker {os.getpid()}] Shape mismatch for {parasite_id}: Micro={microscope_mask.shape}, Dye={dye_mask.shape}. Skipping.")
         return None # Indicate error

    # --- Calculations ---
    try:
        parasite_area = np.sum(microscope_mask)
        if parasite_area == 0:
            logging.warning(f"[Worker {os.getpid()}] Parasite area is zero for {parasite_id}. Skipping calculation.")
            # Decide how to handle: treat as non-cancerous or error?
            is_cancer = False
        else:
            # Ensure masks are boolean before logical_and
            dye_inside_mask = np.logical_and(microscope_mask, dye_mask)
            dye_inside_area = np.sum(dye_inside_mask)

            dye_ratio = dye_inside_area / parasite_area
            is_cancer = dye_ratio > CANCER_THRESHOLD

            logging.info(f"[Worker {os.getpid()}] {parasite_id}: Parasite Area={parasite_area}, Dye Inside Area={dye_inside_area}, Ratio={dye_ratio:.4f}, Cancer={is_cancer}")

    except Exception as e:
        logging.error(f"[Worker {os.getpid()}] Error during calculation for {parasite_id}: {e}")
        return None # Indicate error

    # --- Storage ---
    try:
        # Re-load original images for saving (avoids saving boolean masks)
        microscope_img_to_save = cv2.imread(str(microscope_path), cv2.IMREAD_UNCHANGED)
        if microscope_img_to_save is None:
             logging.warning(f"[Worker {os.getpid()}] Could not reload microscope image {microscope_path} for saving.")
        else:
            output_microscope_path = output_dir_microscope / f"{parasite_id}{SAVE_FORMAT}"
            # Ensure parent directory exists (important in subprocess)
            output_microscope_path.parent.mkdir(parents=True, exist_ok=True)
            success = cv2.imwrite(str(output_microscope_path), microscope_img_to_save, SAVE_PARAMS_PNG) # Use defined save params
            if not success:
                 logging.warning(f"[Worker {os.getpid()}] Failed to save microscope image to {output_microscope_path}")

        if is_cancer:
            dye_img_to_save = cv2.imread(str(dye_path), cv2.IMREAD_UNCHANGED)
            if dye_img_to_save is None:
                 logging.warning(f"[Worker {os.getpid()}] Could not reload dye image {dye_path} for saving.")
            else:
                output_dye_path = output_dir_dye_cancerous / f"{parasite_id}{SAVE_FORMAT}"
                # Ensure parent directory exists
                output_dye_path.parent.mkdir(parents=True, exist_ok=True)
                success = cv2.imwrite(str(output_dye_path), dye_img_to_save, SAVE_PARAMS_PNG) # Use defined save params
                if not success:
                    logging.warning(f"[Worker {os.getpid()}] Failed to save cancerous dye image to {output_dye_path}")

        return is_cancer # Return status: True if cancer, False otherwise

    except Exception as e:
        # Log the full traceback for saving errors
        logging.error(f"[Worker {os.getpid()}] Error during saving for {parasite_id}: {e}", exc_info=True)
        return None # Indicate error