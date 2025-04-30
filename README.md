# Parasite Cancer Detection Image Processing Pipeline

## Project Overview

This project implements a Python-based pipeline to process paired microscope and dye sensor images of parasitic microorganisms. The goal is to identify parasites potentially exhibiting cancerous traits based on the concentration of luminescent dye within their bodies, according to criteria provided by researchers.

The pipeline handles large image files (tested with 500x500 simulations, designed for 100,000x100,000), calculates relevant areas, applies the cancer detection logic (>10% internal dye coverage), and implements an efficient storage strategy (saving all microscope images compressed, but only saving dye images for cancerous cases).

This solution was developed as part of a coding challenge evaluating practical software engineering skills, including the use of common libraries and tools.

## Features

* Loads paired microscope and dye images.
* Calculates parasite area and internal dye area using NumPy and OpenCV.
* Applies a configurable threshold (default: 10%) to detect potential cancer.
* Uses multiprocessing (`concurrent.futures.ProcessPoolExecutor`) for parallel processing of image pairs to improve performance.
* Saves all microscope images using lossless PNG compression.
* Selectively saves dye images only for detected cancerous parasites, also using lossless PNG compression.
* Generates dummy data for testing purposes.
* Logs processing steps and summary statistics.

## File Structure

.├── input_images/        # Directory for input images (created by script if needed)│   ├── microscope/      # Input microscope images (e.g., parasite_0000_microscope.png)│   └── dye/             # Input dye sensor images (e.g., parasite_0000_dye.png)├── output_images/       # Directory for output images (created by script)│   ├── microscope_all/  # Output directory for ALL processed microscope images (compressed)│   └── dye_cancerous/   # Output directory for ONLY cancerous dye images (compressed)├── parasite_processing.ipynb # Jupyter Notebook: Main script execution, configuration, dummy data generation├── processing_utils.py  # Python Module: Contains core processing functions used by multiprocessing workers├── processing_log.txt   # Log file generated during processing├── requirements.txt     # Python dependencies└── README.md            # This file
## Dependencies

* Python 3.7+
* NumPy
* OpenCV for Python (`opencv-python`)

## Setup

1.  **Clone the repository (if applicable).**
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1.  **Ensure `processing_utils.py` is in the same directory as the notebook.**
2.  **Launch Jupyter Notebook or Jupyter Lab:**
    ```bash
    jupyter notebook
    # or
    jupyter lab
    ```
3.  **Open `parasite_processing.ipynb`.**
4.  **Run the cells sequentially:**
    * The "Configuration" cell sets up paths and parameters.
    * The "Generate Dummy Data" cell creates sample input images in the `input_images/` directory (optional, if you don't have your own input).
    * The "Main Execution Loop" cell performs the core processing using multiprocessing.

## Output

* Processed microscope images will be saved in `output_images/microscope_all/`.
* Dye images for parasites identified as cancerous will be saved in `output_images/dye_cancerous/`.
* A detailed log of the processing run will be saved to `processing_log.txt`.
* Summary statistics (counts, time taken) will be printed in the notebook and logged.

## Notes

* The image dimensions for testing are set to 500x500 in the notebook configuration for practical reasons. The code structure is intended for the target 100,000x100,000 images, but memory usage should be monitored closely for full-scale runs.
* The parallel processing uses `ProcessPoolExecutor`. The number of workers can be adjusted in the notebook configuration (`MAX_WORKERS`).
* Error handling is included, and errors during processing are logged.
