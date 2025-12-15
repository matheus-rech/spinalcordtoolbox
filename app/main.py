import streamlit as st
import os
import sys
import tempfile
import subprocess
import matplotlib.pyplot as plt
from nilearn import plotting

try:
    from spinalcordtoolbox.deepseg.models import TASKS
except ImportError:
    st.error("Could not import spinalcordtoolbox. Please ensure the environment is set up correctly.")
    TASKS = {}

# Check for ivadomed
try:
    import ivadomed
except ImportError:
    st.warning("`ivadomed` is not installed. Deep learning models might fail to run. Please install it using `pip install ivadomed`.")

st.set_page_config(
    page_title="SCT Clinical App",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Spinal Cord Toolbox - Clinical Integration")

st.markdown("""
This application demonstrates how **Spinal Cord Toolbox (SCT)** can be integrated into a clinical workflow.
It provides an easy-to-use interface for spinal cord segmentation and analysis.
""")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Segmentation", "Analysis"])

def save_uploaded_file(uploaded_file, temp_dir):
    try:
        path = os.path.join(temp_dir, os.path.basename(uploaded_file.name))
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return path
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def run_command(cmd_list):
    process = subprocess.Popen(
        cmd_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr

if page == "Home":
    st.header("Welcome to the SCT Clinical App")
    st.info("Select a module from the sidebar to get started.")
    
    st.subheader("Available Features")
    st.markdown("""
    - **Segmentation**: Automatically segment spinal cord and pathologies using Deep Learning models.
    - **Analysis**: (Coming Soon) Extract metrics like Cross-Sectional Area (CSA).
    """)

elif page == "Segmentation":
    st.header("Spinal Cord Segmentation")
    
    # Task Selection
    task_options = list(TASKS.keys())
    if not task_options:
        st.warning("No segmentation tasks available. Please ensure spinalcordtoolbox is correctly installed and configured.")
        st.stop()

    # Sort tasks to put 'spinalcord' (contrast agnostic) first as it is the most general
    if 'spinalcord' in task_options:
        task_options.remove('spinalcord')
        task_options.insert(0, 'spinalcord')
        
    selected_task = st.selectbox("Select Segmentation Task", task_options, 
                                 format_func=lambda x: f"{x} - {TASKS[x]['description']}")
    
    st.info(f"**Task Description**: {TASKS[selected_task]['long_description']}")
    
    # File Upload
    uploaded_file = st.file_uploader("Upload MRI Image (NIfTI)", type=["nii", "nii.gz"])
    
    if uploaded_file is not None:
        # Create temp dir for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = save_uploaded_file(uploaded_file, temp_dir)
            
            if input_path:
                st.subheader("Input Image")
                # Visualize Input
                # We use a static plot for now
                fig, ax = plt.subplots(1, 1, figsize=(10, 5))
                plotting.plot_anat(input_path, axes=ax, title="Input Image")
                st.pyplot(fig)
                
                if st.button("Run Segmentation"):
                    st.write("Processing... This may take a while if models need to be downloaded.")
                    
                    # Define output filename
                    output_filename = f"{os.path.splitext(uploaded_file.name)[0]}_seg.nii.gz"
                    output_path = os.path.join(temp_dir, output_filename)
                    
                    # Construct command
                    # We rely on 'sct_deepseg' being available in the path (installed via pip)
                    # or accessible via 'python -m spinalcordtoolbox.scripts.sct_deepseg' if needed.
                    # Assuming sct_deepseg is an entry point.
                    cmd_list = ["sct_deepseg", selected_task, "-i", input_path, "-o", output_path]
                    
                    # For some tasks we might need extra arguments, but let's stick to defaults for now
                    
                    with st.spinner("Running Deep Learning Model..."):
                        retcode, stdout, stderr = run_command(cmd_list)
                    
                    if retcode == 0:
                        st.success("Segmentation Complete!")
                        
                        # Find the actual output file (sometimes SCT adds suffixes)
                        # We look for files in temp_dir that end with .nii.gz and are not the input
                        generated_files = [f for f in os.listdir(temp_dir) if f.endswith(".nii.gz") and os.path.join(temp_dir, f) != input_path]
                        
                        if generated_files:
                            # Pick the most likely result (usually the one we asked for, or one with a suffix)
                            # If we passed -o, sct_deepseg usually honors it or appends to it.
                            # Let's check if our expected output path exists
                            final_output_path = None
                            if os.path.exists(output_path):
                                final_output_path = output_path
                            elif len(generated_files) > 0:
                                final_output_path = os.path.join(temp_dir, generated_files[0])
                            
                            if final_output_path:
                                st.subheader("Segmentation Result")
                                fig2, ax2 = plt.subplots(1, 1, figsize=(10, 5))
                                plotting.plot_roi(final_output_path, bg_img=input_path, axes=ax2, title="Segmentation Overlay", alpha=0.5)
                                st.pyplot(fig2)
                                
                                # Download Button
                                with open(final_output_path, "rb") as f:
                                    st.download_button(
                                        label="Download Segmentation",
                                        data=f,
                                        file_name=os.path.basename(final_output_path),
                                        mime="application/gzip"
                                    )
                            else:
                                st.error("Could not find output file.")
                                st.write("Generated files in temp:", generated_files)
                        else:
                            st.error("No output files generated.")
                    else:
                        st.error("Segmentation Failed.")
                        st.text_area("Error Log", stderr)
                        st.text_area("Output Log", stdout)

elif page == "Analysis":
    st.header("Analysis")
    st.warning("This module is under construction. It will feature CSA calculation and other metrics.")
