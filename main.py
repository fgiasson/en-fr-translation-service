from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def get_model(model_path):
    """Load a Hugging Face model and tokenizer from the specified directory"""
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    return model, tokenizer

# Load the models and tokenizers for each supported language
en_fr_model, en_fr_tokenizer = get_model('models/en_fr/')
fr_en_model, fr_en_tokenizer = get_model('models/fr_en/')

app = Flask(__name__)

def is_translation_supported(from_lang, to_lang):
    """Check if the specified translation is supported"""
    supported_translations = ['en_fr', 'fr_en']
    return f'{from_lang}_{to_lang}' in supported_translations

@app.route('/translate/<from_lang>/<to_lang>/', methods=['POST'])
def translate_endpoint(from_lang, to_lang):
    """Translate text from one language to another. This function is 
    called when a POST request is sent to /translate/<from_lang>/<to_lang>/"""
    if not is_translation_supported(from_lang, to_lang):
        return jsonify({'error': 'Translation not supported'}), 400

    data = request.get_json()
    from_text = data.get(f'{from_lang}_text', '')

    if from_text:
        model = None
        tokenizer = None

        match from_lang:
            case 'en':        
                model = en_fr_model
                tokenizer = en_fr_tokenizer
            case 'fr':
                model = fr_en_model
                tokenizer = fr_en_tokenizer

        to_text = tokenizer.decode(model.generate(tokenizer.encode(from_text, return_tensors='pt')).squeeze(), skip_special_tokens=True)

        return jsonify({f'{to_lang}_text': to_text})
    else:
        return jsonify({'error': 'Text to translate not provided'}), 400
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)


