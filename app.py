from flask import Flask, render_template, request, jsonify
import os
import markdown
from werkzeug.utils import secure_filename
from pypdf import PdfReader
from openai import OpenAI
import json
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Function to check if the file has allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to read PDF
def pdfreader(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()
    return text

# Function to get job role using OpenAI
def get_job_role(text):
    client = OpenAI(api_key="sk-60852459c0af4bd18f26c21b8d01c11d", base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are job role recommendor system suggest jobs in precise format and advice to achieve them"},
            {"role": "user", "content": f"I'd like to leverage this data \n {text} \n  to identify the ideal job role for user and advice on how to pursue it and proivde me output into json format , the json object will contain the following keys first is 'ideal_job_role' an array of string , other is 'user' which is the string , and 'advice',it should not return any other job role only so that i can easily jsonify it."},
        ],
        max_tokens=1024,
        temperature=0.5,
        stream=False
    )
    output = response.choices[0].message.content
    print("the output is from the open ai is ", output)

    pattern = re.compile(r'{(.*)}', re.DOTALL)
    match = pattern.search(output)

    if match:
        result = json.loads("{" + match.group(1) + "}")
    else:
        return ""
    
    return jsonify(result)
    


    # try:
    #     # Remove leading/trailing whitespace and remove the 'json' code block syntax
    #     output = output.strip().replace('```json', '').replace('```', '')
        
    #     # Parse the JSON-formatted string into a Python dictionary
    #     json_data = json.loads(output)
        
    #     return json_data
    # except json.JSONDecodeError as e:
    #     print("Error decoding JSON:", e)
    #     return None


    # return jsonify(output)
    # return  markdown.markdown(output)

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        
        file = request.files['file']

        if file.filename == '':
            return render_template('index.html', error='No selected file')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            text = pdfreader(file_path)
            job_role = get_job_role(text)

            # return render_template('index.html', job_role=job_role)
    

    return job_role
    # return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

