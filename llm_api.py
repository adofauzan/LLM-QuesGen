from flask import Flask, request, jsonify
from llm_handler import LLMHandler
from chromaDB import Chroma_DB
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

gpu_llm = LLMHandler()
vector_db = Chroma_DB()
UPLOAD_FOLDER = './data/sources'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.before_request
def check_initialize():
    if not gpu_llm.is_initialized:
        gpu_llm.initialize()

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(file):
    if file.filename == '':
        return {"error": "No selected file"}, 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        try:
            vector_db.initialize()
            return {"file_path": file_path}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    return {"error": "File type not allowed"}, 400

def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            vector_db.delete_langchain_db()
            print(f"Deleted {file_path}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")

@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_message = request.json['query']
        response = gpu_llm.chat(user_message)
        return jsonify({"response": response})
    except KeyError:
        return jsonify({"error": "Query not provided"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask_rag', methods=['POST'])
def ask_rag():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    upload_result, status_code = upload_file(file)

    if status_code != 200:
        return jsonify(upload_result), status_code

    file_path = upload_result['file_path']

    if not vector_db.is_initialized:
        return jsonify({"error": "Please Wait, DB not initialized"}), 400
    try:
        extra = request.json['extra_instruction']
        q_type = request.json['question_type']
        subject = request.json['subject']
        diff = request.json['difficulty']
        lang = request.json['language']
        query_collection= vector_db.langchain_chroma
        response = gpu_llm.chat_rag(extra, q_type, subject, diff, lang, query_collection)
        delete_file(file_path)
        return jsonify({"response": response})
    except KeyError:
        return jsonify({"error": "Query not provided"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route('/upload_file', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part in the request"}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(file_path)
#         try:
#             vector_db.update_collection()
#             return jsonify({"file_path": file_path})
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500

#     return jsonify({"error": "File type not allowed"}), 400

@app.route('/<string:name>')
def hello(name):
    return "Hello " + name

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=666)
