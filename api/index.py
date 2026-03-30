import os
from flask import Flask, render_template, request, jsonify, url_for
import cloudinary
import cloudinary.uploader
import cloudinary.api

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# ☁️ Cloudinary Configuration
cloudinary.config( 
  cloud_name = "dcbqs3pek", 
  api_key = "288471857999388", 
  api_secret = "2G6_O45IT4QTAVTmHagS9RUFIUc",
  secure = True
)

# NOTE: We no longer need UPLOAD_FOLDER or os.makedirs!

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/file-product', methods=['GET', 'POST'])
def file_product():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        files = request.files.getlist('images')

        if not product_id or len(files) != 3:
            return render_template('fail.html', error_message="3 images required.")

        try:
            # 🚀 Upload to Cloudinary instead of local folder
            for file in files:
                cloudinary.uploader.upload(file, 
                    public_id = f"{product_id}_{file.filename}",
                    folder = f"artisantrace/{product_id}"
                )

            return render_template('success.html', product_id=product_id)
        except Exception as e:
            return render_template('fail.html', error_message=str(e))

    return render_template('file_product.html')

@app.route('/get-product/<product_id>')
def get_product(product_id):
    try:
        # 1. Direct folder lookup using the Admin API
        # This is more reliable than the Search API for new uploads
        folder_path = f"artisantrace/{product_id}"
        
        result = cloudinary.api.resources(
            type = "upload",
            prefix = folder_path,
            max_results = 10
        )
        
        resources = result.get('resources', [])
        
        if not resources:
            # 2. Log this to Vercel so you can see if the path is wrong
            print(f"DEBUG: No files found in folder {folder_path}")
            return jsonify({"error": "No images found"}), 404

        # 3. Success: Map the secure URLs
        images = [res['secure_url'] for res in resources]
        
        return jsonify({
            "name": "Verified Artisan Product",
            "product_id": product_id,
            "images": images
        }), 200

    except Exception as e:
        # This will show up in your Vercel Logs
        print(f"CLOUDINARY ERROR: {str(e)}")
        return jsonify({"error": "Server connection error"}), 500

app = app