from flask import Flask, request, jsonify, render_template
import fitz  # PyMuPDF
import re

app = Flask(__name__)

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def analyze_cv(text):
    score = 0
    feedback = []

    # Check name
    if len(text.split('\n')[0]) > 2:
        score += 10
    else:
        feedback.append("❌ Add your full name at the top")

    # Check email
    if re.search(r'[\w.-]+@[\w.-]+\.\w+', text):
        score += 10
    else:
        feedback.append("❌ No email found — add your email")

    # Check phone
    if re.search(r'[\+\d][\d\s\-]{8,}', text):
        score += 10
    else:
        feedback.append("❌ No phone number found")

    # Check LinkedIn
    if 'linkedin' in text.lower():
        score += 10
    else:
        feedback.append("❌ Add your LinkedIn profile link")

    # Check GitHub
    if 'github' in text.lower():
        score += 10
    else:
        feedback.append("❌ Add your GitHub profile link")

    # Check education
    if any(word in text.lower() for word in ['education', 'university', 'bachelor', 'master']):
        score += 10
    else:
        feedback.append("❌ Add an Education section")

    # Check experience
    if any(word in text.lower() for word in ['experience', 'internship', 'worked', 'job']):
        score += 10
    else:
        feedback.append("❌ Add Work Experience or Internship section")

    # Check skills
    if 'skills' in text.lower():
        score += 10
    else:
        feedback.append("❌ Add a Skills section")

    # Check projects
    if 'project' in text.lower():
        score += 10
    else:
        feedback.append("❌ Add a Projects section")

    # Check length
    if len(text.split()) > 200:
        score += 10
    else:
        feedback.append("❌ CV is too short — add more details")

    if not feedback:
        feedback.append("✅ Great CV! All key sections found.")

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