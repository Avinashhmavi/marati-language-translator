from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
import docx
import google.generativeai as genai
from groq import Groq
import gtts
from io import BytesIO
import re

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB file limit

# Configure API keys
GROQ_API_KEY = "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"
GEMINI_API_KEY = "AIzaSyDchVYHSsulr4izilpCPlYR-NNp8ipitrc"

genai.configure(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        # Get form data
        input_text = request.form.get('input_text', '').strip()
        file = request.files.get('file')
        translation_method = request.form.get('translation_method')
        output_format = request.form.get('output_format')
        gemini_model = request.form.get('gemini_model', 'gemini-1.5-pro')

        # Input validation
        if not any([input_text, file]):
            return jsonify(error="Please provide text or upload a file"), 400

        # Get text content
        if file:
            if file.filename.endswith('.pdf'):
                pdf_reader = PdfReader(file)
                text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
            elif file.filename.endswith('.docx'):
                doc = docx.Document(file)
                text = "\n".join(para.text for para in doc.paragraphs)
            else:
                return jsonify(error="Unsupported file type. Only PDF/DOCX allowed"), 400
        else:
            text = input_text

        if not text.strip():
            return jsonify(error="No text found to translate"), 400

        # Translation with improved accuracy
        if translation_method == 'groq':
            # Optimized prompt for exact translation
            prompt = (
                "Translate the following English text to Marathi accurately and literally. "
                "Do not paraphrase, summarize, or alter the meaning. Preserve all details and context:\n\n"
                f"{text}"
            )
            response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.1,  # Low temperature for precision
                max_tokens=2000   # Adjust based on input length
            )
            marathi_text = response.choices[0].message.content.strip()
        else:
            # Use Gemini with a precise instruction
            model = genai.GenerativeModel(gemini_model)
            prompt = (
                "Translate the following English text to Marathi with exact accuracy. "
                "Do not change the meaning, add interpretations, or omit details. "
                "Provide a literal and faithful translation:\n\n"
                f"{text}"
            )
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.1}  # Low temperature for precision
            )
            marathi_text = response.text.strip()

        # Basic validation: Check if output is empty or nonsensical
        if not marathi_text or re.match(r'^[a-zA-Z0-9\s]*$', marathi_text):
            return jsonify(error="Translation failed: Output is invalid or not in Marathi"), 500

        # Prepare response
        if output_format == 'text':
            return jsonify({
                'result': marathi_text,
                'format': 'text'
            })
        else:
            tts = gtts.gTTS(text=marathi_text, lang='mr')
            audio_io = BytesIO()
            tts.write_to_fp(audio_io)
            audio_io.seek(0)
            return jsonify({
                'audio': list(audio_io.getvalue()),
                'format': 'audio'
            })

    except Exception as e:
        return jsonify(error=f"Server error: {str(e)}"), 500

if __name__ == '__main__':
    app.run(debug=True)