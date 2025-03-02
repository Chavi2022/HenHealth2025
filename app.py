# app.py - Main Flask application file
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
import base64
from dotenv import load_dotenv
import requests
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO

# Import decision tree
from tree import decisionTree

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "hen-health-secret-key")
CORS(app)

# Global variables
predictionState = "root"
demographicsCollected = False

# Language mappings for multilingual support with modern medical language and slight medieval flair
language_mappings = {
   "en": {
       "welcome": "Welcome to Hen Health, your medical consultation service.",
       "welcome_back": "Good day, {}. Welcome to your medical consultation.",
       "didnt_catch": "I'm sorry, I didn't quite understand. Could you please clarify?",
       "couldnt_understand": "I'm having trouble understanding your response.",
       "consult_professional": "Based on your symptoms, you may be experiencing {}. We recommend consulting with a healthcare professional for proper evaluation.",
       "thank_you": "Thank you for your time. Take care!",
       "error_processing": "There was an error processing your response. Let's try again.",
       "error_occurred": "An error occurred. Please try again later.",
       "gather_language": "en-US",
   },
   "es": {
       "welcome": "¡Bienvenido a Hen Health, su servicio de consulta médica.",
       "welcome_back": "Buenos días, {}. Bienvenido a su consulta médica.",
       "didnt_catch": "Lo siento, no entendí bien. ¿Podría aclarar?",
       "couldnt_understand": "Tengo dificultades para entender su respuesta.",
       "consult_professional": "Según sus síntomas, puede estar experimentando {}. Le recomendamos consultar con un profesional de la salud para una evaluación adecuada.",
       "thank_you": "Gracias por su tiempo. ¡Cuídese!",
       "error_processing": "Hubo un error al procesar su respuesta. Intentemos de nuevo.",
       "error_occurred": "Ocurrió un error. Por favor, inténtelo de nuevo más tarde.",
       "gather_language": "es-ES",
   },
   "it": {
       "welcome": "Benvenuti a Hen Health, il vostro servizio di consulenza medica.",
       "welcome_back": "Buongiorno, {}. Benvenuto alla tua consulenza medica.",
       "didnt_catch": "Mi dispiace, non ho capito bene. Potresti chiarire?",
       "couldnt_understand": "Ho difficoltà a capire la tua risposta.",
       "consult_professional": "In base ai tuoi sintomi, potresti avere {}. Ti consigliamo di consultare un professionista sanitario per una valutazione appropriata.",
       "thank_you": "Grazie per il tuo tempo. Prenditi cura!",
       "error_processing": "Si è verificato un errore durante l'elaborazione della tua risposta. Riproviamo.",
       "error_occurred": "Si è verificato un errore. Per favore riprova più tardi.",
       "gather_language": "it-IT",
   },
   "pt": {
       "welcome": "Bem-vindo ao Hen Health, seu serviço de consulta médica.",
       "welcome_back": "Bom dia, {}. Bem-vindo à sua consulta médica.",
       "didnt_catch": "Desculpe, não entendi bem. Você poderia esclarecer?",
       "couldnt_understand": "Estou tendo dificuldade em entender sua resposta.",
       "consult_professional": "Com base nos seus sintomas, você pode estar experimentando {}. Recomendamos consultar um profissional de saúde para avaliação adequada.",
       "thank_you": "Obrigado pelo seu tempo. Cuide-se!",
       "error_processing": "Ocorreu um erro ao processar sua resposta. Vamos tentar novamente.",
       "error_occurred": "Ocorreu um erro. Por favor, tente novamente mais tarde.",
       "gather_language": "pt-PT",
   },
   "de": {
       "welcome": "Willkommen bei Hen Health, Ihrem medizinischen Beratungsservice.",
       "welcome_back": "Guten Tag, {}. Willkommen zu Ihrer medizinischen Beratung.",
       "didnt_catch": "Es tut mir leid, ich habe nicht ganz verstanden. Könnten Sie das bitte klären?",
       "couldnt_understand": "Ich habe Schwierigkeiten, Ihre Antwort zu verstehen.",
       "consult_professional": "Basierend auf Ihren Symptomen könnten Sie unter {} leiden. Wir empfehlen Ihnen, einen Arzt für eine richtige Beurteilung zu konsultieren.",
       "thank_you": "Vielen Dank für Ihre Zeit. Passen Sie auf sich auf!",
       "error_processing": "Bei der Verarbeitung Ihrer Antwort ist ein Fehler aufgetreten. Versuchen wir es erneut.",
       "error_occurred": "Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.",
       "gather_language": "de-DE",
   },
   "fr": {
       "welcome": "Bienvenue à Hen Health, votre service de consultation médicale.",
       "welcome_back": "Bonjour, {}. Bienvenue à votre consultation médicale.",
       "didnt_catch": "Je suis désolé, je n'ai pas bien compris. Pourriez-vous préciser?",
       "couldnt_understand": "J'ai du mal à comprendre votre réponse.",
       "consult_professional": "D'après vos symptômes, vous pourriez souffrir de {}. Nous vous recommandons de consulter un professionnel de la santé pour une évaluation appropriée.",
       "thank_you": "Merci de votre temps. Prenez soin de vous!",
       "error_processing": "Une erreur s'est produite lors du traitement de votre réponse. Essayons à nouveau.",
       "error_occurred": "Une erreur s'est produite. Veuillez réessayer plus tard.",
       "gather_language": "fr-FR",
   },
}

# Demographic questions
demographic_questions = [
    {"id": "sex", "question": "What is your biological sex?", "options": ["male", "female", "other"]},
    {"id": "age", "question": "What is your age?", "options": ["child", "teen", "adult", "senior"]},
    {"id": "height", "question": "What is your height in inches or centimeters?"},
    {"id": "weight", "question": "What is your weight in pounds or kilograms?"},
    {"id": "medical_history", "question": "Do you have any significant medical history or chronic conditions?"}
]

# OpenAI API functions
def generate_openai_response(prompt, default_response=None):
    """Generate a response using OpenAI's API with improved error handling"""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Validate inputs
    if not prompt or not OPENAI_API_KEY:
        logger.warning("Missing prompt or API key")
        return default_response
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 150  # Limit response length
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10  # Add timeout to prevent hanging
        )
        
        # Log full response for debugging
        logger.info(f"OpenAI API Response Status: {response.status_code}")
        logger.info(f"OpenAI API Response: {response.text}")
        
        if response.status_code == 200:
            response_json = response.json()
            
            # Additional checks for response structure
            if "choices" in response_json and response_json["choices"]:
                content = response_json["choices"][0].get("message", {}).get("content")
                if content:
                    return content.strip()
            
            logger.error("Unexpected OpenAI API response structure")
            return default_response
        else:
            logger.error(f"OpenAI API Error: {response.status_code} - {response.text}")
            return default_response
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error calling OpenAI API: {str(e)}")
        return default_response
    except Exception as e:
        logger.error(f"Unexpected error calling OpenAI API: {str(e)}")
        return default_response

def translate_text(text, target_language):
    """Translate text to the target language using OpenAI API"""
    if target_language == "en":
        return text
    prompt = f"Translate the following text to {target_language}: \"{text}\""
    translated_text = generate_openai_response(prompt, default_response=text)
    return translated_text.strip() if translated_text else text

# Demographic response interpretation (detailed version)
def interpret_demographic_response(user_input, question):
    if "options" in question:
        valid_options = [option.lower() for option in question["options"]]
        response = user_input.strip().lower()
        if response in valid_options:
            return response
        else:
            prompt = (
                f"Interpret the following demographic response: '{user_input}'. "
                f"Return one of the following options: {', '.join(valid_options)}."
            )
            result = generate_openai_response(prompt)
            if result:
                return result.strip().lower()
            else:
                # Fallback if API call fails
                return "invalid"
    else:
        return user_input.strip()

def interpret_response(user_response, question_node):
    """Interpret user's response and categorize it into one of the options."""
    options = list(question_node.keys())
    options.remove("question")
    prompt = f"""
    Given the user response: "{user_response}"
    And the question: "{question_node['question']}"
    Determine which option best fits the response: {', '.join(options)}
    If no suitable option exists, return "invalid".
    """
    return generate_openai_response(prompt).strip().lower() or "invalid"

def modernize_medical_text(medieval_text):
    """Convert medieval-style medical text to modern English while keeping a slight medieval flavor"""
    
    prompt = f"""
    Convert this medical text to modern English while keeping just a hint of medieval flavor:
    "{medieval_text}"
    
    Use standard modern English grammar and vocabulary, but keep a very small amount of medieval flair 
    (like starting with "Good day" or using words like "ailment" occasionally). 
    Use modern medical terminology.
    """
    
    modern_text = generate_openai_response(prompt)
    return modern_text if modern_text else medieval_text

def generate_doctor_recommendations(diagnosis, demographics):
    """Generate recommendations for healthcare providers based on diagnosis and demographics"""
    
    prompt = f"""
    Generate concise recommendations for a healthcare provider based on the following:
    
    Patient Demographics:
    - Sex: {demographics.get('sex', 'Not provided')}
    - Age: {demographics.get('age', 'Not provided')}
    - Height: {demographics.get('height', 'Not provided')}
    - Weight: {demographics.get('weight', 'Not provided')}
    - Medical History: {demographics.get('medical_history', 'None reported')}
    
    Preliminary Diagnosis: {diagnosis}
    
    Provide 3-4 focused recommendations for the healthcare provider to consider during follow-up.
    Include any relevant tests, evaluations, or considerations based on the demographics and diagnosis.
    Format as a bulleted list and keep it professional and concise.
    """
    
    recommendations = generate_openai_response(prompt)
    return recommendations if recommendations else "No specific recommendations available."

def generate_medical_record_pdf(record):
    """Generate a PDF medical record"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    custom_title_style = ParagraphStyle(name='HenHealthTitle', 
                             parent=styles['Heading1'], 
                             fontSize=16, 
                             spaceAfter=12)
    
    custom_subtitle_style = ParagraphStyle(name='HenHealthSubtitle', 
                             parent=styles['Heading2'], 
                             fontSize=14, 
                             spaceAfter=10)
    
    custom_section_style = ParagraphStyle(name='HenHealthSection', 
                             parent=styles['Heading3'], 
                             fontSize=12, 
                             spaceAfter=8)
    
    # Build the PDF content
    elements = []
    
    # Title
    elements.append(Paragraph("Hen Health Medical Record", custom_title_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Consultations
    if record.get('entries') and len(record['entries']) > 0:
        for i, entry in enumerate(record['entries']):
            elements.append(Paragraph(f"Consultation {i+1} ({entry.get('time', 'Unknown date')})", custom_subtitle_style))
            
            # Diagnosis
            elements.append(Paragraph("Assessed Condition:", custom_section_style))
            elements.append(Paragraph(entry.get('diagnosis', 'No diagnosis provided'), styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Recommendations
            elements.append(Paragraph("Recommendations for Healthcare Provider:", custom_section_style))
            elements.append(Paragraph(entry.get('recommendations', 'No recommendations provided'), styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Conversation
            elements.append(Paragraph("Consultation Transcript:", custom_section_style))
            
            conversation_data = []
            for line in entry.get('conversation', []):
                if line.startswith('Physician:'):
                    conversation_data.append([line, ''])
                else:
                    conversation_data.append(['', line])
            
            if conversation_data:
                conversation_table = Table(conversation_data, colWidths=[3*inch, 3*inch])
                conversation_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                    ('PADDINGTOP', (0, 0), (-1, -1), 4),
                    ('PADDINGBOTTOM', (0, 0), (-1, -1), 4),
                    ('PADDINGLEFT', (0, 0), (-1, -1), 4),
                    ('PADDINGRIGHT', (0, 0), (-1, -1), 4),
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ]))
                
                elements.append(conversation_table)
            
            elements.append(Spacer(1, 0.25*inch))
    else:
        elements.append(Paragraph("No Consultations Found", custom_subtitle_style))
        elements.append(Paragraph("This patient has not completed any consultations yet.", styles['Normal']))
    
    # Disclaimer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("This document is a record of an AI-assisted medical consultation. Please consult with a healthcare professional for proper diagnosis and treatment.", styles['Italic']))
    
    # Build the document
    doc.build(elements)
    
    # Get the PDF content
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf

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
        
        # Initialize demographics
        session['demographics'] = {}
        session['demographics_collected'] = False
        session['current_demographic_question'] = 0
        
        return redirect(url_for('chat', user_name=user_name, user_id=user_id))
    
    # Use the existing login.html template
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
    
    # Get the demographics
    demographics = session.get('demographics', {})
    first_name = demographics.get('first_name', user_name.split()[0] if ' ' in user_name else user_name)
    
    # Get the root question
    root_question = decisionTree["root"]["question"]
    
    # Check if there's a current concern
    current_concern = session.get('current_concern', '')
    
    # Craft a personalized greeting that acknowledges demographics and current concern
    if current_concern:
        prompt = f"""
        Create a warm, personalized greeting for a patient with the following details:
        - Name: {first_name}
        - Sex: {demographics.get('sex', 'Not specified')}
        - Age: {demographics.get('age', 'Not specified')}
        - Current concern: "{current_concern}"
        
        The greeting should:
        1. Address them by their first name
        2. Have a very slight medieval flavor (like starting with "Good day" but otherwise use modern English)
        3. Acknowledge their concern
        4. Lead into this first diagnostic question: "{root_question}"
        
        Keep it warm, professional, and concise.
        """
        
        greeting = generate_openai_response(prompt)
        if not greeting:
            greeting = f"Good day, {first_name}. I understand you're experiencing {current_concern}. Let's start by determining your primary symptom. {root_question}"
        
        # Clear the current concern after using it
        session.pop('current_concern', None)
    else:
        prompt = f"""
        Create a warm, personalized greeting for a new patient named {first_name}.
        It should have a very slight medieval flavor (like starting with "Good day" but otherwise use modern English),
        be professionally friendly, and transition into asking this medical question: "{root_question}"
        """
        
        greeting = generate_openai_response(prompt)
        if not greeting:
            greeting = f"Good day, {first_name}. Welcome to your medical consultation. {root_question}"
    
    # Store in chat history
    session['current_chat'].append(f"Physician: {greeting}")
    
    # Get audio if needed
    audio_base64 = None
    if data.get('audio_enabled', False):
        audio_base64 = text_to_speech(greeting, language)
    
    return jsonify({
        'message': greeting,
        'audio': audio_base64
    })

@app.route('/api/chat', methods=['POST'])
def process_chat():
    global predictionState
    data = request.get_json()
    user_input = data.get('message')
    language = data.get('language', 'en')
    
    # Initialize chat history if not already
    if 'current_chat' not in session:
        session['current_chat'] = []
    
    # Add the user's message to chat history
    session['current_chat'].append(f"Patient: {user_input}")
    
    # Check if we're still collecting demographics
    if not session.get('demographics_collected', False):
        current_question_index = session.get('current_demographic_question', 0)
        if current_question_index < len(demographic_questions):
            current_question = demographic_questions[current_question_index]
            answer = interpret_demographic_response(user_input, current_question)
            # Store the demographic answer...
            session['demographics'][current_question["id"]] = answer
            
            # Move to the next question
            next_question_index = current_question_index + 1
            session['current_demographic_question'] = next_question_index
            
            if next_question_index < len(demographic_questions):
                next_question = demographic_questions[next_question_index]
                if "options" in next_question:
                    options_text = ", ".join(next_question["options"])
                    question_text = f"{next_question['question']} ({options_text})"
                else:
                    question_text = next_question['question']
                
                # Translate the question text
                question_text = translate_text(question_text, language)
                
                audio_base64 = text_to_speech(question_text, language) if data.get('audio_enabled', False) else None
                session['current_chat'].append(f"Physician: {question_text}")
                return jsonify({
                    'message': question_text,
                    'audio': audio_base64,
                    'is_demographic': True
                })
            else:
                session['demographics_collected'] = True
                root_question = decisionTree["root"]["question"]
                translated_root_question = translate_text(root_question, language)
                transition = f"Thank you for providing that information. Now, let's discuss your health concerns. {translated_root_question}"
                session['current_chat'].append(f"Physician: {transition}")
                audio_base64 = text_to_speech(transition, language) if data.get('audio_enabled', False) else None
                return jsonify({
                    'message': transition,
                    'audio': audio_base64,
                    'is_demographic': False
                })
    
    # If we're here, we're processing the actual consultation
    try:
        # First, check if we've already reached a diagnosis (predictionState is a string, not a node in the tree)
        if predictionState not in decisionTree:
            # Already at a diagnosis, so just return it again
            diagnosis = predictionState
            ai_response = language_mappings[language]['consult_professional'].format(diagnosis)
            
            # Add AI response to chat history
            session['current_chat'].append(f"Physician: {ai_response}")
            
            # Get audio if needed
            audio_base64 = None
            if data.get('audio_enabled', False):
                audio_base64 = text_to_speech(ai_response, language)
            
            return jsonify({
                'message': ai_response,
                'audio': audio_base64,
                'is_diagnosis': True,
                'is_demographic': False
            })
        
        # Otherwise, continue with the decision tree logic
        current_node = decisionTree[predictionState]
        current_question = current_node["question"]
        
        # Create a safe copy of options for interpret_response
        interpreted_response = interpret_response(user_input, current_node)
        
        # This is the case when response is invalid
        if interpreted_response == "invalid":
            ai_response = f"{language_mappings[language]['didnt_catch']} {current_question}"
            
            # Add AI response to chat history
            session['current_chat'].append(f"Physician: {ai_response}")
            
            # Get audio if needed
            audio_base64 = None
            if data.get('audio_enabled', False):
                audio_base64 = text_to_speech(ai_response, language)
            
            return jsonify({
                'message': ai_response,
                'audio': audio_base64,
                'is_diagnosis': False,
                'is_demographic': False
            })
        
        # Response is valid, update state
        if interpreted_response in current_node:
            next_state = current_node[interpreted_response]
            predictionState = next_state
            
            # Check if we've reached a diagnosis (leaf node)
            if next_state not in decisionTree:
                diagnosis = next_state
                ai_response = language_mappings[language]['consult_professional'].format(diagnosis)
                is_diagnosis = True
            else:
                # We're still in the decision tree
                next_question = decisionTree[next_state]["question"]
                
                # Add a hint of medieval flair to the response
                prompt = f'''
                Rephrase this medical question in a friendly, professional tone with just a hint of medieval flair: 
                "{next_question}"
                Use modern English and medical terminology, but maintain a slight old-fashioned warmth in the greeting.
                '''
                
                modern_question = generate_openai_response(prompt)
                ai_response = modern_question or next_question
                is_diagnosis = False
        else:
            # Couldn't understand but we have a valid response
            ai_response = f"{language_mappings[language]['couldnt_understand']} {current_question}"
            is_diagnosis = False
            if language != "en":
                ai_response = translate_text(ai_response, language)
        
        # Add AI response to chat history
        session['current_chat'].append(f"Physician: {ai_response}")
        
        # Get audio if needed
        audio_base64 = None
        if data.get('audio_enabled', False):
            audio_base64 = text_to_speech(ai_response, language)
        
        return jsonify({
            'message': ai_response,
            'audio': audio_base64,
            'is_diagnosis': is_diagnosis,
            'is_demographic': False
        })
    
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({
            'message': language_mappings[language]['error_occurred'],
            'error': str(e)
        }), 500

@app.route('/api/text_to_speech', methods=['POST'])
def api_text_to_speech():
    """API endpoint for sentence-level text-to-speech"""
    data = request.get_json()
    text = data.get('text', '')
    language = data.get('language', 'en')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    audio_base64 = text_to_speech(text, language)
    
    if audio_base64:
        return jsonify({'audio': audio_base64})
    else:
        return jsonify({'error': 'Failed to generate speech'}), 500

@app.route('/api/end_chat', methods=['POST'])
def end_chat():
    global predictionState
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    # In a full implementation, you would save this to a database
    # For this demo, we'll use session storage
    if 'medical_entries' not in session:
        session['medical_entries'] = []
    
    # Add a new entry for this consultation
    if predictionState not in decisionTree:
        current_date = datetime.now()
        formatted_date = current_date.strftime("%B %d, %Y")
        
        # Generate doctor recommendations
        demographics = session.get('demographics', {})
        recommendations = generate_doctor_recommendations(predictionState, demographics)
        
        session['medical_entries'].append({
            'time': formatted_date,
            'diagnosis': predictionState,
            'conversation': session.get('current_chat', []),
            'recommendations': recommendations
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
    
    # Prepare record data
    record = {
        'name': session.get('user_name', 'Unknown Patient'),
        'demographics': session.get('demographics', {}),
        'entries': session.get('medical_entries', [])
    }
    
    # Add current date for the record
    current_date = datetime.now().strftime("%B %d, %Y")
    current_year = datetime.now().year
    
    return render_template('medical-record.html', record=record, current_date=current_date, current_year=current_year)

@app.route('/api/export_record', methods=['POST'])
def export_record():
    """API endpoint for exporting medical records as PDF"""
    try:
        user_id = request.form.get('user_id')
        export_format = request.form.get('format', 'pdf')
        
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User identifier is required'}), 400
        
        # Prepare record data
        record = {
            'name': session.get('user_name', 'Unknown Patient'),
            'demographics': session.get('demographics', {}),
            'entries': session.get('medical_entries', [])
        }
        
        if export_format == 'pdf':
            # Generate PDF
            pdf_data = generate_medical_record_pdf(record)
            
            # Create a unique filename
            filename = f"medical_record_{record['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # In a real application, you would save this file and provide a download link
            # For this example, we'll use a direct response approach
            response = make_response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            return response
        else:
            # Default to web view if not PDF
            return jsonify({
                'status': 'success',
                'url': f'/medical-record?user_id={user_id}'
            })
    except Exception as e:
        logger.error(f"Error exporting record: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
