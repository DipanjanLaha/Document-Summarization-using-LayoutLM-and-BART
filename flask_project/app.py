from flask import Flask, render_template, request, redirect, url_for
import os
import json
import subprocess
from logic import run_layoutlm_on_pdf
#from logic2 import summarize
#from models.summarization_model import load_summarization_model, summarize_text

app = Flask(__name__)
RESULT_FOLDER = 'static/outputs'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['OUTPUT_FOLDER'] = 'static/outputs/'
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# layoutlm_model, layoutlm_tokenizer = load_layoutlm_model()
# summarizer = load_summarization_model()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['pdf']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            output_image_paths = run_layoutlm_on_pdf(filepath, app.config['RESULT_FOLDER'])
            result = subprocess.run(["C:/Users/dipan/anaconda3/python.exe", './logic2.py', '--pdf', filepath], capture_output=True, text=True)
            if result.returncode == 0:
                try:
                    print(json.loads(result.stdout))
                except json.JSONDecodeError:
                    print({"error": "Failed to parse output"})
                else:
                    print({"error": result.stderr.strip()})

            data = json.loads(result.stdout)
            ops = []
            for item in data:
                ops.append(item["summary"])





            # # Pass through LayoutLM
            # layoutlm_output_path = predict_layoutlm(filepath, layoutlm_model, layoutlm_tokenizer)

            # # (Optional) Extract text from layout model if needed
            # extracted_text = "text extracted from layoutlm output"  # placeholder

            # # Pass through Summarization
            # summary = summarize_text(extracted_text, summarizer)

            # return render_template('index.html',
            #                        layoutlm_image=layoutlm_output_path,
            #                        summary_text=summary)
            return render_template('results.html', images=output_image_paths, summaries=ops)
        
    return render_template('uploads.html')


@app.route('/results')
def results():
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True)
