from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import numpy as np
from PIL import Image
import io
import base64
import tensorflow as tf

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
app.config['MODEL_PATH'] = 'small_cnn_brain_tumor_final.keras'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load the model once at startup
print("Loading model...")
try:
    model = tf.keras.models.load_model(app.config['MODEL_PATH'])
    print(f"Model loaded successfully from {app.config['MODEL_PATH']}")
    # Get the expected input shape from the model
    if model.input_shape:
        expected_shape = model.input_shape[1:3]  # Get (height, width) excluding batch and channel
        print(f"Model expects input shape: {model.input_shape}")
        print(f"Using image size: {expected_shape}")
    else:
        expected_shape = (200, 200)  # Default fallback
        print(f"Could not determine input shape, using default: {expected_shape}")
except Exception as e:
    print(f"Error loading model: {e}")
    print("Please make sure the model file 'small_cnn_brain_tumor_final.keras' is in the project directory")
    model = None
    expected_shape = (224, 224)  # Default fallback

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_image(image):
    """Preprocess the image for model prediction"""
    # Get the expected input size from the model (or use default)
    if model is not None and model.input_shape:
        target_size = model.input_shape[1:3]  # (height, width)
    else:
        target_size = expected_shape if 'expected_shape' in globals() else (200, 200)
    
    # Resize to the model's expected input size
    image = image.resize(target_size)
    # Convert to grayscale (L mode) - model expects 1 channel
    if image.mode != 'L':
        image = image.convert('L')
    # Convert to numpy array and normalize
    img_array = np.array(image) / 255.0
    # Add channel dimension for grayscale (height, width) -> (height, width, 1)
    img_array = np.expand_dims(img_array, axis=-1)
    # Add batch dimension: (height, width, 1) -> (1, height, width, 1)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_tumor(image, original_image=None):
    """
    Predict brain tumor using the loaded TensorFlow model.
    
    Expected return format:
    {
        'has_tumor': bool,
        'confidence': float (0-1),
        'message': str
    }
    """
    if model is None:
        raise Exception("Model not loaded. Please check if the model file exists.")
    
    # Try prediction with current image size
    try:
        prediction = model.predict(image, verbose=0)
    except Exception as e:
        # If prediction fails, try common alternative sizes
        if original_image is not None:
            common_sizes = [(200, 200), (180, 180), (150, 150), (256, 256)]
            for size in common_sizes:
                try:
                    # Re-preprocess with different size
                    resized = original_image.resize(size)
                    if resized.mode != 'L':
                        resized = resized.convert('L')
                    img_array = np.array(resized) / 255.0
                    img_array = np.expand_dims(img_array, axis=-1)
                    img_array = np.expand_dims(img_array, axis=0)
                    prediction = model.predict(img_array, verbose=0)
                    print(f"Successfully predicted with size: {size}")
                    break
                except:
                    continue
            else:
                raise Exception(f"Could not find compatible input size. Original error: {str(e)}")
        else:
            raise e
    
    # Handle different output formats
    # If model outputs probability for tumor class (single value or binary)
    if len(prediction[0]) == 1:
        # Binary classification: output is probability of tumor
        tumor_probability = float(prediction[0][0])
        has_tumor = tumor_probability > 0.5
        confidence = tumor_probability if has_tumor else (1 - tumor_probability)
    else:
        # Multi-class: assume index 1 is tumor class, index 0 is no tumor
        # Adjust these indices based on your model's output
        no_tumor_prob = float(prediction[0][0])
        tumor_prob = float(prediction[0][1])
        has_tumor = tumor_prob > no_tumor_prob
        confidence = tumor_prob if has_tumor else no_tumor_prob
    
    return {
        'has_tumor': has_tumor,
        'confidence': confidence,
        'message': 'Tumor Detected' if has_tumor else 'No Tumor Detected'
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an image file.'}), 400
        
        # Read and process the image
        image = Image.open(io.BytesIO(file.read()))
        
        # Preprocess for model
        preprocessed = preprocess_image(image)
        
        # Get prediction (pass original image for fallback)
        result = predict_tumor(preprocessed, original_image=image)
        
        # Convert image to base64 for display
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'prediction': result,
            'image': img_str
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

