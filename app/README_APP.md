# SCT Clinical App

This is a Streamlit-based web application that integrates functionalities from the **Spinal Cord Toolbox (SCT)** for clinical use.

## Features

-   **Segmentation**: Run deep learning-based segmentation on spinal cord MRI images (NIfTI format).
    -   Supports various tasks like spinal cord, gray matter, and lesion segmentation.
    -   Visualizes the input image and the resulting segmentation overlay.
    -   Allows downloading the segmentation mask.
-   **Analysis**: (Future work) Calculate metrics like Cross-Sectional Area (CSA).

## Prerequisites

-   Python 3.8+
-   Spinal Cord Toolbox (SCT) installed or available in `PYTHONPATH`.
-   Streamlit

## Installation

1.  Ensure you are in the root of the workspace.
2.  Install dependencies:
    ```bash
    pip install -r app/requirements_app.txt
    ```
    *Note: Installing `ivadomed` and `torch` might take some time and require significant disk space.*

## Usage

1.  Run the Streamlit app:
    ```bash
    streamlit run app/main.py
    ```
2.  Open the provided URL in your browser.
3.  Navigate to the **Segmentation** tab.
4.  Select a task (e.g., `spinalcord` for contrast-agnostic segmentation).
5.  Upload a `.nii.gz` file.
6.  Click **Run Segmentation**.

## Notes

-   The app expects the `spinalcordtoolbox` package to be importable.
-   Deep learning models are downloaded automatically on the first run.
-   If running in a constrained environment, ensure `ivadomed` and its dependencies (especially `torch`) are correctly installed.
