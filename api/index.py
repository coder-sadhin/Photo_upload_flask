from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from livereload import Server
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'fudskjt438r79873rhdkjhf87982378rfd@kjdsp'  # Change this!

# Configuration for image uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024  # 30MB max

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ====================== ROUTES ======================

@app.route('/')
def index():
    """Home page - Requirements & Dashboard"""
    return render_template('index.html')


@app.route('/file-product', methods=['GET', 'POST'])
def file_product():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        files = request.files.getlist('images')

        # Basic Validation
        if not product_id or len(files) != 3:
            return render_template('fail.html', error_message="You must provide a Product ID and exactly 3 images.")

        try:
            # Create folder
            product_path = os.path.join(app.config['UPLOAD_FOLDER'], product_id)
            os.makedirs(product_path, exist_ok=True)

            # Save Files
            for file in files:
                if file.filename:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(product_path, filename))

            # ✅ SHOW SUCCESS PAGE
            return render_template('success.html', product_id=product_id)

        except Exception as e:
            return render_template('fail.html', error_message=str(e))

    return render_template('file_product.html')

# 🔍 THE FIX: This route finds the specific folder you just created
@app.route('/get-product/<product_id>')
def get_product(product_id):
    # Construct the path to the folder
    product_dir = os.path.join(app.config['UPLOAD_FOLDER'], product_id)
    
    if os.path.exists(product_dir):
        # Gather all images in that specific folder
        images = []
        for f in os.listdir(product_dir):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                # Generate correct URL for the frontend
                img_url = url_for('static', filename=f'uploads/{product_id}/{f}')
                images.append(img_url)
        
        return jsonify({
            "name": "Verified Artisan Item",
            "product_id": product_id,
            "images": images
        }), 200
    
    # If folder doesn't exist, search fails
    return jsonify({"error": "Product not found"}), 404

#if __name__ == '__main__':
    #app.run(debug=True)
    # server = Server(app.wsgi_app)
    
    # Watch templates and static files
    # server.watch('app/templates/')
    # server.watch('app/static/')
    # server.serve(port=5000, debug=True)

    # app.run(debug=True)
