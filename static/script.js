document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('translate-form');
    const resultDiv = document.getElementById('result');
    const outputText = document.getElementById('output-text');
    const outputAudio = document.getElementById('output-audio');
    const themeToggle = document.getElementById('theme-toggle');

    // Theme Toggle
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        themeToggle.textContent = document.body.classList.contains('dark') ? '☀️' : '🌙';
    });

    // Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        resultDiv.classList.add('hidden');
        outputText.textContent = '';
        outputAudio.classList.add('hidden');

        const formData = new FormData();
        formData.append('input_text', document.getElementById('input-text').value);
        formData.append('file', document.getElementById('file-upload').files[0]);
        formData.append('translation_method', document.getElementById('translation-method').value);
        formData.append('output_format', document.getElementById('output-format').value);
        formData.append('gemini_model', document.getElementById('gemini-model').value);

        try {
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Something went wrong');
            }

            resultDiv.classList.remove('hidden');
            if (data.format === 'text') {
                outputText.textContent = data.result;
            } else {
                const audioBlob = new Blob([new Uint8Array(data.audio)], { type: 'audio/mp3' });
                outputAudio.src = URL.createObjectURL(audioBlob);
                outputAudio.classList.remove('hidden');
            }
        } catch (error) {
            outputText.textContent = `Error: ${error.message}`;
            resultDiv.classList.remove('hidden');
        }
    });
});