from flask import Flask, request, jsonify
import csv

app = Flask(__name__)
CSV_FILE = 'url.csv'

def remove_empty_lines(file_path):
    with open(file_path, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if line.strip():
                file.write(line)
        file.truncate()

def append_to_csv(data):
    remove_empty_lines(CSV_FILE)
    with open(CSV_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        urls = data.split()
        for url in urls:
            writer.writerow([url])

@app.route('/')
def index():
    return 'Made by God'

@app.route('/addtext', methods=['POST'])
def addtext():
    if 'text' in request.json:
        text = request.json['text']
        append_to_csv(text)
        return jsonify({'message': 'Text added successfully.'}), 200
    else:
        return jsonify({'error': 'Text field is missing.'}), 400
        
@app.route('/removetext', methods=['POST'])
def removetext():
    if 'text' in request.json:
        text = request.json['text']
        with open(CSV_FILE, 'r') as file:
            lines = file.readlines()
        with open(CSV_FILE, 'w') as file:
            for line in lines:
                if text not in line:
                    file.write(line)
        return jsonify({'message': 'Text removed successfully.'}), 200
    else:
        return jsonify({'error': 'Text field is missing.'}), 400

if __name__ == '__main__':
    app.run()