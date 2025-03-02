# app.py - Main Flask application file
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
import base64
from dotenv import load_dotenv
import requests
import uuid

# Import decision tree
from tree import decisionTree

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "here-ye-health-secret-key")
CORS(app)

# Global variables
predictionState = "root"

# Language mappings for multilingual support with medieval theme
language_mappings = {
   "en": {
       "welcome": "Hark! Welcome to Here Ye Health, realm of healing.",
       "welcome_back": "Good morrow, {}. Welcome back to the healing halls.",
       "didnt_catch": "I prithee, I did not catch thy words. Pray, repeat?",
       "couldnt_understand": "Verily, thy reply confounds me.",
       "consult_professional": "By thy words, thou might suffer from {}. Seek the counsel of a royal physician.",
       "thank_you": "Gratitude for thy time. Fare thee well!",
       "error_processing": "Alas, an error hath befallen. Let us try anew.",
       "error_occurred": "A misfortune hath occurred. Pray, attempt later.",
       "gather_language": "en-US",
   },
   "es": {
       "welcome": "¡Escuchad! Bienvenido a Here Ye Health, reino de la sanación.",
       "welcome_back": "Saludos, {}. Bienvenido de nuevo a los salones de la curación.",
       "didnt_catch": "No he comprendido tus palabras. Por favor, repítelas.",
       "couldnt_understand": "Vuestro mensaje me resulta oscuro.",
       "consult_professional": "Por vuestras respuestas, quizás padezcáis de {}. Consultad a un médico real sin demora.",
       "thank_you": "Gracias por vuestro tiempo. ¡Adiós!",
       "error_processing": "Hubo un error al procesar vuestra respuesta. Intentad de nuevo.",
       "error_occurred": "Ha acontecido un error. Intentad más tarde.",
       "gather_language": "es-ES",
   },
   "it": {
       "welcome": "Ascoltate! Benvenuti a Here Ye Health, il regno della guarigione.",
       "welcome_back": "Salve, {}. Bentornato nei saloni della salute.",
       "didnt_catch": "Non ho colto le vostre parole. Per favore, ripetete.",
       "couldnt_understand": "La vostra risposta mi sfugge.",
       "consult_professional": "Dalle vostre risposte, potreste soffrire di {}. Consultate un medico reale postumo al più presto.",
       "thank_you": "Grazie per il vostro tempo. Addio!",
       "error_processing": "Si è verificato un errore nel processare la vostra risposta. Riprova.",
       "error_occurred": "Si è verificato un errore. Riprova più tardi.",
       "gather_language": "it-IT",
   },
   "pt": {
       "welcome": "Ouvi! Bem-vindo a Here Ye Health, reino da cura.",
       "welcome_back": "Saudações, {}. Bem-vindo de volta aos salões da saúde.",
       "didnt_catch": "Não compreendi vossas palavras. Por favor, repitam.",
       "couldnt_understand": "Vossa resposta me é obscura.",
       "consult_professional": "Pelas vossas respostas, podeis padecer de {}. Consultai um médico real sem demora.",
       "thank_you": "Agradecemos o vosso tempo. Adeus!",
       "error_processing": "Ocorreu um erro ao processar a resposta. Tentai novamente.",
       "error_occurred": "Um erro ocorreu. Tentai mais tarde.",
       "gather_language": "pt-PT",
   },
   "de": {
       "welcome": "Höret! Willkommen zu Here Ye Health, dem Reich der Heilkunst.",
       "welcome_back": "Seid gegrüßt, {}. Willkommen zurück in den Hallen der Genesung.",
       "didnt_catch": "Ich vermag eure Worte nicht zu vernehmen. Wiederholt sie, bitte.",
       "couldnt_understand": "Eure Antwort entzieht sich meinem Verständnis.",
       "consult_professional": "Nach euren Worten leidet ihr vielleicht an {}. Sucht unverzüglich einen königlichen Arzt auf.",
       "thank_you": "Dank für eure Zeit. Lebt wohl!",
       "error_processing": "Ein Fehler ist aufgetreten beim Verarbeiten eurer Antwort. Versucht es erneut.",
       "error_occurred": "Ein Fehler hat sich ereignet. Versucht es später.",
       "gather_language": "de-DE",
   },
   "fr": {
       "welcome": "Écoutez! Bienvenue à Here Ye Health, royaume de la guérison.",
       "welcome_back": "Salutations, {}. Bienvenue de nouveau dans les salles de santé.",
       "didnt_catch": "Je n'ai point saisi vos paroles. Veuillez répéter.",
       "couldnt_understand": "Votre réponse m'est obscure.",
       "consult_professional": "D'après vos réponses, vous pourriez souffrir de {}. Consultez prestement un médecin royal.",
       "thank_you": "Merci de votre temps. Adieu!",
       "error_processing": "Un malheureux défaut est survenu lors du traitement de votre réponse. Veuillez réessayer.",
       "error_occurred": "Un problème est survenu. Veuillez réessayer plus tard.",
       "gather_language": "fr-FR",
   },
}

# OpenAI API functions
def generate_openai_response(prompt):
    """Generate a response using OpenAI's API"""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            logger.error(f"OpenAI API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        return None

def interpret_response(user_response, question_node):
    """Interpret user's response and categorize it into one of the options"""
    options = list(question_node.keys())
    options.remove("question")
    
    prompt = f"""
    Given the user response: "{user_response}"
    And the question: "{question_node['question']}"
    Interpret the response and categorize it into one of the following options: {', '.join(options)}
    If the response doesn't properly address the question, return "invalid".
    
    Please return only one option from the list above, not multiple options.
    """
    
    interpreted_response = generate_openai_response(prompt).strip().lower()
    
    # Post-processing to ensure only one option is returned
    if interpreted_response in options:
        return interpreted_response
    elif ',' in interpreted_response:
        # If multiple options are returned, take the first one
        first_option = interpreted_response.split(',')[0].strip()
        return first_option if first_option in options else "invalid"
    
    return "invalid"

# Eleven Labs TTS integration
def text_to_speech(text, language="en"):
    """Convert text to speech using Eleven Labs API and return a base64 encoded audio"""
    
    ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
    
    # Language voice mapping with medieval voices
    language_voice_map = {
        "en": {"voice_id": "XjLkpWUlnhS8i7gGz3lZ", "language": "English"},
        "es": {"voice_id": "gD1IexrzCvsXPHUuT0s3", "language": "Spanish"},
        "it": {"voice_id": "pwvkOXKI34DbjtR6yUk5", "language": "Italian"},
        "pt": {"voice_id": "cyD08lEy76q03ER1jZ7y", "language": "Portuguese"},
        "de": {"voice_id": "f2yUVfK5jdm78zlpcZ8C", "language": "German"},
        "fr": {"voice_id": "Qrl71rx6Yg8RvyPYRGCQ", "language": "French"},
    }
    
    # Translate text if not in English
    if language != "en" and language in language_voice_map:
        prompt = f"Translate the following text to {language_voice_map.get(language)['language']}:\n\n{text}\n\nTranslation:"
        translated_text = generate_openai_response(prompt)
        if translated_text:
            text = translated_text.strip()
    
    voice_info = language_voice_map.get(language, language_voice_map["en"])
    voice_id = voice_info["voice_id"]
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.7,
            "similarity_boost": 0.8
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Convert audio response to base64 for embedding in HTML
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            return audio_base64
        else:
            logger.error(f"Eleven Labs API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error in text_to_speech: {str(e)}")
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get name and ailment from form
        user_name = request.form.get('user_name', 'Good Traveler')
        user_ailment = request.form.get('user_ailment', '')
        
        # Set default language to English
        language = 'en'
        
        # Store in session
        session['user_name'] = user_name
        session['user_ailment'] = user_ailment
        session['language'] = language
        
        # Generate a unique user ID 
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id
        
        # Initialize medical record if not exists
        if 'medical_entries' not in session:
            session['medical_entries'] = []
        
        # Add initial ailment to medical record
        if user_ailment:
            session['initial_ailment'] = user_ailment
        
        return redirect(url_for('chat', user_name=user_name, user_id=user_id))
    
    return render_template('login.html')

@app.route('/set_language', methods=['POST'])
def set_language():
    language = request.form.get('language')
    session['language'] = language
    return jsonify({'status': 'success'})

@app.route('/chat')
def chat():
    user_name = session.get('user_name')
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    return render_template('chat.html', user_name=user_name, user_id=user_id)

@app.route('/api/start_chat', methods=['POST'])
def start_chat():
    global predictionState
    
    data = request.get_json()
    user_id = data.get('user_id')
    user_name = data.get('user_name', 'Good Traveler')
    language = data.get('language', 'en')
    
    # Initialize chat history in session
    if 'current_chat' not in session:
        session['current_chat'] = []
    
    # Reset prediction state
    predictionState = "root"
    
    # Get initial question with medieval flair
    root_question = decisionTree["root"]["question"]
    
    # Add medieval flair to the question and include initial ailment if provided
    initial_greeting = language_mappings[language]['welcome_back'].format(user_name)
    
    if 'initial_ailment' in session and session['initial_ailment']:
        prompt = f"""
        A patient named {user_name} has described their ailment as: "{session['initial_ailment']}"
        Based on this, create a personalized medieval court physician greeting that acknowledges 
        their concern, then ask this medical question: "{root_question}"
        Use thee, thou, and similar medieval English. Keep it somewhat concise.
        """
        medieval_question = generate_openai_response(prompt) or f"{initial_greeting} I understand thou art troubled by {session['initial_ailment']}. {root_question}"
        # Clear the initial ailment after using it
        session.pop('initial_ailment', None)
    else:
        prompt = f"""
        Rephrase this medical question in a medieval court physician style, 
        but maintain the medical meaning: "{root_question}"
        Use thee, thou, and similar medieval English. Keep it concise.
        """
        medieval_question = generate_openai_response(prompt) or f"{initial_greeting} {root_question}"
    
    # Store in chat history
    session['current_chat'].append(f"Physician: {medieval_question}")
    
    # Get audio if needed
    audio_base64 = None
    if data.get('audio_enabled', False):
        audio_base64 = text_to_speech(medieval_question, language)
    
    return jsonify({
        'message': medieval_question,
        'audio': audio_base64
    })

@app.route('/api/chat', methods=['POST'])
def process_chat():
    global predictionState
    
    data = request.get_json()
    user_input = data.get('message')
    user_id = data.get('user_id')
    user_name = data.get('user_name', 'Good Traveler')
    language = data.get('language', 'en')
    
    # Initialize chat history if not already
    if 'current_chat' not in session:
        session['current_chat'] = []
    
    # Add the user's message to chat history
    session['current_chat'].append(f"Patient: {user_input}")
    
    try:
        current_node = decisionTree[predictionState]
        current_question = current_node["question"]
        interpreted_response = interpret_response(user_input, current_node)
        
        if interpreted_response == "invalid":
            # Give a medieval-flavored response for invalid input
            ai_response = f"{language_mappings[language]['didnt_catch']} {current_question}"
        else:
            if interpreted_response in current_node:
                predictionState = current_node[interpreted_response]
            else:
                ai_response = f"{language_mappings[language]['couldnt_understand']} {current_question}"
            
            if predictionState not in decisionTree:
                # End of decision tree - medieval diagnosis
                ai_response = language_mappings[language]['consult_professional'].format(predictionState)
            else:
                next_question = decisionTree[predictionState]["question"]
                
                # Add a medieval flair to the response
                prompt = f"""
                Rephrase this medical question in a medieval court physician style, 
                but maintain the medical meaning: "{next_question}"
                Use thee, thou, and similar medieval English. Keep it concise.
                """
                
                medieval_question = generate_openai_response(prompt)
                ai_response = medieval_question or next_question
        
        # Add AI response to chat history
        session['current_chat'].append(f"Physician: {ai_response}")
        
        # Get audio if needed
        audio_base64 = None
        if data.get('audio_enabled', False):
            audio_base64 = text_to_speech(ai_response, language)
        
        return jsonify({
            'message': ai_response,
            'audio': audio_base64,
            'is_diagnosis': predictionState not in decisionTree
        })
    
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({
            'message': language_mappings[language]['error_occurred'],
            'error': str(e)
        }), 500

@app.route('/api/end_chat', methods=['POST'])
def end_chat():
    data = request.get_json()
    user_id = data.get('user_id')
    
    # In a full implementation, you would save this to a database
    # For this demo, we'll use session storage
    if 'medical_entries' not in session:
        session['medical_entries'] = []
    
    # Add a new entry for this consultation
    if predictionState not in decisionTree:
        session['medical_entries'].append({
            'time': f"Day {datetime.now().day} of {['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][datetime.now().month-1]}, Year of Our Lord {datetime.now().year}",
            'diagnosis': predictionState,
            'conversation': session.get('current_chat', [])
        })
    
    # Clear current chat
    session['current_chat'] = []
    
    return jsonify({
        'status': 'success',
        'redirect': f'/medical-record?user_id={user_id}'
    })

@app.route('/medical-record')
def medical_record():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return "User identifier is required", 400
    
    # In medieval theme, we'll use a simplified approach with session storage
    record = {
        'name': session.get('user_name', 'Unknown Traveler'),
        'entries': session.get('medical_entries', [])
    }
    
    return render_template('medical-record.html', record=record)

if __name__ == '__main__':
    app.run(debug=True)