from flask import Flask, render_template, request, send_file, render_template_string, url_for
import pdfkit
import uuid
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/preview', methods=['POST'])
def preview():
    content = request.form.get('content', '')
    image = request.files.get('image')

    image_tag = ''
    if image and image.filename:
        filename = f"{uuid.uuid4().hex}_{image.filename}"
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(img_path)
        image_url = url_for('uploaded_file', filename=filename)

        if image.filename.endswith('.svg'):
            image_tag = f'<object data="{image_url}" type="image/svg+xml" width="300"></object><br>'
        else:
            image_tag = f'<img src="{image_url}" alt="Uploaded Image" width="300"><br>'

    return render_template('report_template.html', content=content, image_tag=image_tag)
    

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/', methods=['POST'])
def generate_pdf():
    content = request.form.get('content', '')
    image = request.files.get('image')

    image_tag = ''
    if image and image.filename:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(img_path)
        image_tag = f'<img src="{img_path}" width="300"><br>'

    html = render_template('report_template.html', content=content, image_tag=image_tag)
    filename = f"{uuid.uuid4().hex}.pdf"
    pdfkit.from_string(html, filename, configuration=config)
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
