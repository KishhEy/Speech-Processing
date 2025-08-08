document.addEventListener('DOMContentLoaded', () => {
    const mediaUpload = document.getElementById('media-upload');
    const analyzeBtn = document.getElementById('analyze-btn');
    const statusEl = document.getElementById('status');
    const fileNameEl = document.getElementById('file-name');
    const resultContainer = document.getElementById('result-container');
    const resultEmotionEl = document.getElementById('result-emotion');

    let selectedFile = null;

    mediaUpload.addEventListener('change', (event) => {
        selectedFile = event.target.files[0];
        if (selectedFile) {
            fileNameEl.textContent = selectedFile.name;
            analyzeBtn.disabled = false;
            resultContainer.classList.add('hidden');
            statusEl.textContent = '';
        }
    });

    analyzeBtn.addEventListener('click', async () => {
        if (!selectedFile) {
            statusEl.textContent = 'Please select a file first.';
            return;
        }

        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = `<div class="flex items-center justify-center"><div class="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-6 w-6 mr-3"></div><span>Analyzing...</span></div>`;
        resultContainer.classList.add('hidden');
        statusEl.textContent = 'Uploading and processing file...';

        const formData = new FormData();
        formData.append('audio_file', selectedFile);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.error) {
                throw new Error(result.error);
            }

            resultEmotionEl.textContent = result.emotion;
            resultContainer.classList.remove('hidden');
            statusEl.textContent = 'Analysis complete!';

        } catch (error) {
            console.error('An error occurred during analysis:', error);
            statusEl.textContent = `Error: ${error.message}`;
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = 'Analyze Emotion';
        }
    });

    // Initial state
    analyzeBtn.disabled = true;
});
