import cv2
import numpy as np
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os

# Criar a aplicação Flask
app = Flask(__name__)

# Definir a pasta de upload e configuração
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Extensões permitidas para o upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


# Função para verificar se a extensão do arquivo é permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Função para aplicar efeitos na imagem
def apply_effect(image_path, effect):
    image = cv2.imread(image_path)

    if effect == 'gray':
        # Converter para escala de cinza
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif effect == 'blur':
        # Aplicar desfoque simples (Blur)
        return cv2.GaussianBlur(image, (15, 15), 0)
    elif effect == 'median':
        # Aplicar desfoque por mediana
        return cv2.medianBlur(image, 5)
    elif effect == 'binary':
        # Binarizar imagem com threshold
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        return binary
    elif effect == 'erosion':
        # Aplicar erosão
        kernel = np.ones((5, 5), np.uint8)
        return cv2.erode(image, kernel, iterations=1)
    elif effect == 'dilation':
        # Aplicar dilatação
        kernel = np.ones((5, 5), np.uint8)
        return cv2.dilate(image, kernel, iterations=1)
    elif effect == 'opening':
        # Aplicar opening
        kernel = np.ones((5, 5), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    elif effect == 'closing':
        # Aplicar closing
        kernel = np.ones((5, 5), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    else:
        return image


# Rota para o formulário principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Verificar se o arquivo foi enviado
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']

        if file.filename == '':
            return 'No selected file'

        if file and allowed_file(file.filename):
            # Salvar a imagem no servidor
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Obter o efeito desejado
            effect = request.form['effect']
            processed_image = apply_effect(file_path, effect)

            # Salvar a imagem processada
            processed_filename = 'processed_' + filename
            processed_file_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
            cv2.imwrite(processed_file_path, processed_image)

            # Retornar a imagem processada
            return render_template('index.html', filename=processed_filename)

    return render_template('index.html', filename=None)


# Rota para servir a imagem processada
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))


# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True)