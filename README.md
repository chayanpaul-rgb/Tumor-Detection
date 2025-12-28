# Brain Tumor Detection Web Application

A simple and attractive web application for detecting brain tumors in MRI images using machine learning.

## Features

- 🎨 Modern, attractive UI with gradient design
- 📤 Drag-and-drop image upload
- 🤖 AI-powered tumor detection
- 📊 Confidence score display
- 📱 Responsive design for all devices

## Setup Instructions

### 1. Download Your Model from Google Colab

Download your model file `small_cnn_brain_tumor_final.keras` from Google Colab:

**Option A: Direct Download from Colab**
```python
# In Google Colab, run this to download the model
from google.colab import files
files.download('/content/drive/MyDrive/small_cnn_brain_tumor_final.keras')
```

**Option B: Using Google Drive**
1. Open Google Drive in your browser
2. Navigate to the file: `small_cnn_brain_tumor_final.keras`
3. Right-click and download
4. Place it in the project root directory (same folder as `app.py`)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
.
├── app.py                              # Flask backend application
├── requirements.txt                    # Python dependencies
├── small_cnn_brain_tumor_final.keras   # Your trained model (download from Colab)
├── templates/
│   └── index.html                      # Main HTML template
├── static/
│   ├── style.css                       # Styling
│   └── script.js                       # Frontend JavaScript
└── uploads/                            # Uploaded images (created automatically)
```

## Usage

1. Open the web application in your browser
2. Upload an MRI image by clicking or dragging and dropping
3. Click "Analyze Image" to get the prediction
4. View the results with confidence score

## Important Notes

⚠️ **This tool is for research purposes only. Always consult medical professionals for diagnosis.**

## Model Integration

The model is already integrated! The app will automatically load `small_cnn_brain_tumor_final.keras` when it starts.

**Note**: If your model has a different output format (e.g., different class indices), you may need to adjust the `predict_tumor()` function in `app.py` to match your model's output structure.

## Customization

- **Model Path**: Change `app.config['MODEL_PATH']` in `app.py` if your model has a different name or location
- **Image Preprocessing**: Adjust the `preprocess_image()` function if your model expects different input dimensions or normalization
- **Styling**: Modify `static/style.css` to change colors, fonts, and layout

## Supported Image Formats

- PNG
- JPG/JPEG
- GIF
- BMP
- TIFF

## License

This project is open source and available for educational purposes.

