from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os
import PyPDF2
from transformers import pipeline

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Initialize GPT-2 locally using transformers
llm = pipeline("text-generation", model="gpt2")

# Home page route
@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    chat_response = None
    if request.method == 'POST':
        if 'file' in request.files:
            # Handle PDF upload
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Read PDF and generate summary
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    pdf_text = " ".join([page.extract_text() for page in pdf_reader.pages])

                # Generate summary using GPT-2
                summary_prompt = "Summarize the following text: " + pdf_text[:1000]  # Limit input size for GPT-2
                summary = llm(summary_prompt, max_new_tokens=150, num_return_sequences=1)[0]['generated_text']

                # Store the PDF text in the session for chatbot access
                app.config['PDF_TEXT'] = pdf_text  # Store in app config

        elif 'question' in request.form:
            # Handle chatbot question
            question = request.form['question']
            pdf_text = app.config.get('PDF_TEXT', '')  # Retrieve PDF text
            if pdf_text:
                prompt = f"Question: {question}\nDocument Text: {pdf_text[:1000]}"  # Limit input size for GPT-2
                chat_response = llm(prompt, max_new_tokens=100, num_return_sequences=1)[0]['generated_text']
    
    return render_template('index1.html', summary=summary, chat_response=chat_response)

if __name__ == '__main__':
    if not os.path.exists('uploads/'):
        os.makedirs('uploads/')
    app.run(debug=True)
