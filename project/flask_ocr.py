from flask import Flask, render_template, request, send_from_directory

# Initialize Flask app
app = Flask(__name__)

# Global list objects
ocr_texts = []
image_filenames = []

# Calculate the number of strings
def get_string_count(text):
    return len(text.split())

# Calculate the number of characters
def get_char_count(text):
    return len(text.replace('\n', '').replace(' ', ''))

# Reference filename from the /img directory 
@app.route('/img/<filename>')
def ref_image(filename):
    return send_from_directory('img', filename)

# Stores OCR data in item object for display via render_template
@app.route('/', methods=['GET', 'POST'])
def index():
    global ocr_texts, image_filenames
    items = []
    string_count = 0
    char_count = 0
    
    # Append OCR text and image name
    if request.method == 'POST':
        data = request.get_json()
        ocr_text = data.get('ocr_text')
        image_filename = data.get('image_filename')
        if ocr_text:
            ocr_texts.append(ocr_text)
            image_filenames.append(image_filename)
    
    # Parse and calculate OCR text for count metadata
    for text, image_filename in zip(ocr_texts, image_filenames):
        string_count = get_string_count(text)
        char_count = get_char_count(text)
        # Prepare data in template
        items.append({'ocr_text': text, 'image_filename': image_filename, 'string_count': string_count, 'char_count': char_count})
            
    print("OCR: ", ocr_texts)
    return render_template('index.html', items=items)

# Reset data values
@app.route('/reset', methods=['POST'])
def reset():
    global ocr_texts, image_filenames
    ocr_texts = []
    image_files = []
    return render_template('index.html', items=[])

# Run Flask app when executed
if __name__ == '__main__':
    app.run(debug=True)

