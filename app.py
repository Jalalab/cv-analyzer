from flask import Flask, request, jsonify, render_template
import fitz
import os
from groq import Groq

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def analyze_cv(text):
    try:
        prompt = f"""
You are an expert CV reviewer and career coach with 10 years of experience.
Analyze the following CV and provide exactly 5 feedback points.

CV Text:
{text}

Respond in this exact format only:
SCORE: [number between 0-100]
FEEDBACK:
- [feedback point 1]
- [feedback point 2]
- [feedback point 3]
- [feedback point 4]
- [feedback point 5]
"""
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",,
        )

        response = chat_completion.choices[0].message.content
        lines = response.split('\n')
        score = 70
        feedback = []

        for line in lines:
            line = line.strip()
            if line.startswith('SCORE:'):
                try:
                    score = int(''.join(filter(str.isdigit, line.replace('SCORE:', ''))))
                except:
                    score = 70
            elif line.startswith('-'):
                feedback.append(line)

        if not feedback:
            feedback = ["- ✅ CV received and analyzed", "- 💡 Please try uploading again for detailed feedback"]

        return score, feedback

    except Exception as e:
        return 50, [f"- ❌ Error: {str(e)}"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        file = request.files['cv']
        file.save('uploaded_cv.pdf')
        text = extract_text('uploaded_cv.pdf')
        score, feedback = analyze_cv(text)
        return jsonify({'score': score, 'feedback': feedback})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
