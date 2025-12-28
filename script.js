const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const previewSection = document.getElementById('previewSection');
const previewImage = document.getElementById('previewImage');
const removeBtn = document.getElementById('removeBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultSection = document.getElementById('resultSection');
const uploadContent = document.querySelector('.upload-content');

// Store the current file
let currentFile = null;

// Drag and drop functionality
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// Handle click on upload area (but not on the browse button)
uploadArea.addEventListener('click', (e) => {
    // Don't trigger if clicking on the browse button
    if (e.target.closest('.browse-btn')) {
        return;
    }
    fileInput.click();
});

// Handle browse button click separately
const browseBtn = document.querySelector('.browse-btn');
if (browseBtn) {
    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent triggering upload area click
        fileInput.click();
    });
}

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please upload an image file.');
        return;
    }

    // Store the file for later use
    currentFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewSection.style.display = 'block';
        uploadArea.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

removeBtn.addEventListener('click', () => {
    resetPreview();
});

function resetPreview() {
    previewSection.style.display = 'none';
    uploadArea.style.display = 'block';
    // Reset file input to allow selecting the same file again
    fileInput.value = '';
    currentFile = null;
    resultSection.style.display = 'none';
}

analyzeBtn.addEventListener('click', async () => {
    // Use stored file (from drag-drop) or file input (from browse)
    const file = currentFile || fileInput.files[0];
    if (!file) {
        alert('Please select an image first.');
        return;
    }

    // Show loading state
    analyzeBtn.disabled = true;
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');
    btnText.textContent = 'Analyzing...';
    btnLoader.style.display = 'inline-block';

    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to analyze image');
        }

        // Display results
        displayResults(data);

    } catch (error) {
        alert('Error: ' + error.message);
        console.error('Error:', error);
    } finally {
        // Reset button state
        analyzeBtn.disabled = false;
        btnText.textContent = 'Analyze Image';
        btnLoader.style.display = 'none';
    }
});

function displayResults(data) {
    const { prediction, image } = data;
    const { has_tumor, confidence, message } = prediction;

    // Update preview image if provided
    if (image) {
        previewImage.src = 'data:image/png;base64,' + image;
    }

    // Set result icon and styling
    const resultIcon = document.getElementById('resultIcon');
    const resultTitle = document.getElementById('resultTitle');
    const resultMessage = document.getElementById('resultMessage');
    const confidenceValue = document.getElementById('confidenceValue');
    const progressFill = document.getElementById('progressFill');

    if (has_tumor) {
        resultIcon.className = 'result-icon danger';
        resultIcon.textContent = '⚠️';
        resultTitle.textContent = 'Tumor Detected';
        resultTitle.style.color = 'var(--danger-color)';
        resultMessage.textContent = 'The analysis indicates the presence of a brain tumor. Please consult with a medical professional immediately.';
    } else {
        resultIcon.className = 'result-icon success';
        resultIcon.textContent = '✓';
        resultTitle.textContent = 'No Tumor Detected';
        resultTitle.style.color = 'var(--success-color)';
        resultMessage.textContent = 'The analysis shows no signs of a brain tumor. However, this is not a substitute for professional medical diagnosis.';
    }

    // Update confidence
    const confidencePercent = Math.round(confidence * 100);
    confidenceValue.textContent = `${confidencePercent}%`;
    progressFill.style.width = `${confidencePercent}%`;

    // Show result section
    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function resetAnalysis() {
    resetPreview();
    resultSection.style.display = 'none';
}

