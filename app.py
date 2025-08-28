from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Import views after app creation
from views.chatbotLegalv2 import process_input, create_new_chat, get_chat_list, load_chat
from views.judgmentPred import extract_text_from_file, predict_verdict
from views.docGen import generate_legal_document

@app.route('/')
def index():
    try:
        raw_chat_names = get_chat_list()
        chat_list = []

        for name in raw_chat_names:
            chat_data = load_chat(name)
            first_q = chat_data["past"][0] if chat_data["past"] else "New chat"
            truncated_q = first_q[:30] + '...' if len(first_q) > 30 else first_q
            chat_list.append({
                "name": name,
                "title": truncated_q
            })

        chat_name = chat_list[0]["name"] if chat_list else create_new_chat()
        chat_data = load_chat(chat_name) if chat_list else {"past": [], "generated": []}

        return render_template('index.html', 
                             chat_name=chat_name, 
                             chat_list=list(reversed(chat_list)), 
                             chat_data=chat_data)
    except Exception as e:
        print(f"Error in index: {e}")
        # Create default chat if error
        chat_name = create_new_chat()
        return render_template('index.html', 
                             chat_name=chat_name, 
                             chat_list=[], 
                             chat_data={"past": [], "generated": []})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('user_input', '')
        chat_name = data.get('chat_name', '')

        if not user_input or not chat_name:
            return jsonify({"error": "Missing input or chat name"}), 400

        response = process_input(chat_name, user_input)
        return jsonify({"response": response})
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/new_chat', methods=['POST'])
def new_chat():
    try:
        chat_name = create_new_chat()
        return jsonify({"chat_name": chat_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/load_chat', methods=['POST'])
def load_existing_chat():
    try:
        data = request.json
        chat_name = data.get('chat_name')
        if not chat_name:
            return jsonify({"error": "Chat name required"}), 400

        chat_data = load_chat(chat_name)
        return jsonify({"chat_data": chat_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict', methods=['GET', 'POST'])
def predict_judgment():
    if request.method == 'GET':
        try:
            raw_chat_names = get_chat_list()
            chat_list = []
            for name in raw_chat_names:
                chat_data = load_chat(name)
                first_q = chat_data["past"][0] if chat_data["past"] else "New chat"
                truncated_q = first_q[:30] + '...' if len(first_q) > 30 else first_q
                chat_list.append({
                    "name": name,
                    "title": truncated_q
                })
            return render_template('predict.html', chat_list=chat_list)
        except:
            return render_template('predict.html', chat_list=[])

    # POST request
    try:
        file = request.files.get('file')
        file_type = request.form.get('file_type')

        if not file or not file_type:
            return jsonify({"error": "File and file type required."}), 400

        temp_dir = os.path.join(os.getcwd(), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)

        text = extract_text_from_file(temp_path, file_type)
        result = predict_verdict(text)
        
        # Clean up
        try:
            os.remove(temp_path)
        except:
            pass
            
        return jsonify({
            "text": text,
            "result": result
        })
    except Exception as e:
        print(f"Predict error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate', methods=['GET'])
def generate():
    try:
        raw_chat_names = get_chat_list()
        chat_list = []
        for name in raw_chat_names:
            chat_data = load_chat(name)
            first_q = chat_data["past"][0] if chat_data["past"] else "New chat"
            truncated_q = first_q[:30] + '...' if len(first_q) > 30 else first_q
            chat_list.append({
                "name": name,
                "title": truncated_q
            })
        return render_template('generate.html', chat_list=chat_list)
    except:
        return render_template('generate.html', chat_list=[])

@app.route('/generate_document', methods=['POST'])
def generate_document():
    try:
        data = request.json
        prompt = data.get('doc_prompt', '')
        if not prompt:
            return jsonify({'error': 'Prompt required'}), 400

        file_path, file_name = generate_legal_document(prompt)
        return jsonify({
            'download_url': f'/download/{file_name}',
            'file_name': file_name
        })
    except Exception as e:
        print(f"Generate error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('static/generated_docs', filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)