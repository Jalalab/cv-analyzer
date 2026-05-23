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
    prompt = f"""
You are an expert CV reviewer and career coach.
Analyze the following CV and provide:
1. A score out of 100
2. A list of specific improvements needed
3. What is done well

CV Text:
{text}

Respond in this exact format:
SCORE: [number]
FEEDBACK:
- [feedback point 1]
- [feedback point 2]
- [feedback point 3]
- [feedback point 4]
- [feedback point 5]
"""
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    
    response = chat_completion.choices[0].message.content
    
    # Parse score
    lines = response.split('\n')
    score = 50
    feedback = []
    
    for line in lines:
        if line.startswith('SCORE:'):
            try:
                score = int(line.replace('SCORE:', '').strip())
            except:
                score = 50
        elif line.strip().startswith('-'):
            feedback.append(line.strip())
    
    if not feedback:
        feedback = ["Please try again"]
    
    return score, feedback

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['cv']
    file.save('uploaded_cv.pdf')
    text = extract_text('uploaded_cv.pdf')
    score, feedback = analyze_cv(text)
    return jsonify({'score': score, 'feedback': feedback})

if __name__ == '__main__':
    app.run(debug=True)
