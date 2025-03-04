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
    """Interpret user's response and categorize it into one of the options or handle invalid responses"""
    options = list(question_node.keys())
    options.remove("question")
    
    prompt = f"""
    Given the user response: "{user_response}"
    And the question: "{question_node['question']}"
    Interpret the response and categorize it into one of the following options: {', '.join(options)}
    If the response doesn't properly address the question, analyze what the user might be trying to say 
    and make your best guess at which option matches their intent. Only return "invalid" if you 
    absolutely cannot determine their intent.
    
    Please return only one option from the list above.
    """
    
    interpreted_response = generate_openai_response(prompt).strip().lower()
    
    # Post-processing to ensure only one option is returned
    if interpreted_response in options:
        return interpreted_response
    elif ',' in interpreted_response:
        # If multiple options are returned, take the first one
        first_option = interpreted_response.split(',')[0].strip()
        return first_option if first_option in options else options[0]  # Default to first option instead of "invalid"
    elif interpreted_response == "invalid":
        # For invalid responses, use OpenAI to determine most likely intent
        followup_prompt = f"""
        The user's response: "{user_response}" to the question: "{question_node['question']}"
        was difficult to classify. Please analyze their message and determine which of these options 
        is most likely what they meant: {', '.join(options)}
        Just return the single most likely option.
        """
        
        fallback_response = generate_openai_response(followup_prompt).strip().lower()
        
        if fallback_response in options:
            return fallback_response
        else:
            # As a last resort, return the first option to keep the conversation flowing
            return options[0]
    
    # If we can't determine the response but it's not "invalid", try to match to an option
    for option in options:
        if option in interpreted_response:
            return option
    
    # If all else fails, return the first option to keep the conversation flowing
    return options[0]

def interpret_demographic_response(user_response, question):
    """Extract demographic information from user response"""
    if "sex" in question["id"]:
        prompt = f"""
        Given the user response: "{user_response}"
        Determine the user's biological sex. Return only one of: male, female, other, or unknown.
        If the response is unclear, return the most likely option.
        """
        
        sex = generate_openai_response(prompt).strip().lower()
        if sex in ["male", "female", "other"]:
            return sex
        return "unknown"
    
    elif "age" in question["id"]:
        prompt = f"""
        Given the user response: "{user_response}"
        Determine the user's age category or exact age.
        If a specific age is given, return that number.
        If a range or category is given, determine if they are: child (0-12), teen (13-19), adult (20-64), or senior (65+).
        Return only the age number or category word.
        """
        
        age = generate_openai_response(prompt).strip().lower()
        
        # Check if the response is a number (specific age)
        if age.isdigit():
            return age
        
        # Otherwise, categorize
        if age in ["child", "teen", "adult", "senior"]:
            return age
        return "adult"  # Default to adult if unclear
    
    elif "height" in question["id"]:
        prompt = f"""
        Given the user response about their height: "{user_response}"
        Extract the height value and unit (inches, centimeters, feet).
        If in feet and inches, convert to inches.
        Return the result as a number followed by unit, e.g., "70 inches" or "175 cm".
        If unclear, make your best estimate.
        """
        
        return generate_openai_response(prompt).strip().lower()
    
    elif "weight" in question["id"]:
        prompt = f"""
        Given the user response about their weight: "{user_response}"
        Extract the weight value and unit (pounds, kilograms).
        Return the result as a number followed by unit, e.g., "160 lbs" or "72 kg".
        If unclear, make your best estimate.
        """
        
        return generate_openai_response(prompt).strip().lower()
    
    elif "medical_history" in question["id"]:
        prompt = f"""
        Given the user response about their medical history: "{user_response}"
        Summarize their medical history concisely.
        If they mention specific conditions, include those.
        If they have no significant medical history, indicate that.
        Keep it brief but informative.
        """
        
        return generate_openai_response(prompt).strip()
    
    return user_response  # Default fallback

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

def generate_medical_record_pdf(record, title="Hen Health Medical Record", language="en"):
    """Generate a PDF medical record with language support"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    styles.add(ParagraphStyle(name='Title', 
                             parent=styles['Heading1'], 
                             fontSize=16, 
                             spaceAfter=12))
    
    styles.add(ParagraphStyle(name='Subtitle', 
                             parent=styles['Heading2'], 
                             fontSize=14, 
                             spaceAfter=10))
    
    styles.add(ParagraphStyle(name='Section', 
                             parent=styles['Heading3'], 
                             fontSize=12, 
                             spaceAfter=8))
    
    # Translations for PDF text
    translations = {
        'en': {
            'patientInfo': 'Patient Information',
            'name': 'Name:',
            'dob': 'Date of Birth:',
            'sex': 'Sex:',
            'height': 'Height:',
            'weight': 'Weight:',
            'medicalHistory': 'Medical History:',
            'notProvided': 'Not provided',
            'noneReported': 'None reported',
            'consultation': 'Consultation',
            'assessedCondition': 'Assessed Condition:',
            'noDiagnosis': 'No diagnosis provided',
            'recommendations': 'Recommendations for Healthcare Provider:',
            'noRecommendations': 'No recommendations provided',
            'transcript': 'Consultation Transcript:',
            'noConsultations': 'No Consultations Found',
            'noConsultationsDesc': 'This patient has not completed any consultations yet.',
            'disclaimer': 'This document is a record of an AI-assisted medical consultation. Please consult with a healthcare professional for proper diagnosis and treatment.'
        },
        'es': {
            'patientInfo': 'Información del Paciente',
            'name': 'Nombre:',
            'dob': 'Fecha de Nacimiento:',
            'sex': 'Sexo:',
            'height': 'Altura:',
            'weight': 'Peso:',
            'medicalHistory': 'Historial Médico:',
            'notProvided': 'No proporcionado',
            'noneReported': 'Ninguno reportado',
            'consultation': 'Consulta',
            'assessedCondition': 'Condición Evaluada:',
            'noDiagnosis': 'No se proporcionó diagnóstico',
            'recommendations': 'Recomendaciones para el Proveedor de Salud:',
            'noRecommendations': 'No se proporcionaron recomendaciones',
            'transcript': 'Transcripción de la Consulta:',
            'noConsultations': 'No se Encontraron Consultas',
            'noConsultationsDesc': 'Este paciente aún no ha completado ninguna consulta.',
            'disclaimer': 'Este documento es un registro de una consulta médica asistida por IA. Por favor consulte con un profesional de la salud para un diagnóstico y tratamiento adecuados.'
        },
        'fr': {
            'patientInfo': 'Informations du Patient',
            'name': 'Nom:',
            'dob': 'Date de Naissance:',
            'sex': 'Sexe:',
            'height': 'Taille:',
            'weight': 'Poids:',
            'medicalHistory': 'Antécédents Médicaux:',
            'notProvided': 'Non fourni',
            'noneReported': 'Aucun signalé',
            'consultation': 'Consultation',
            'assessedCondition': 'Condition Évaluée:',
            'noDiagnosis': 'Aucun diagnostic fourni',
            'recommendations': 'Recommandations pour le Prestataire de Soins:',
            'noRecommendations': 'Aucune recommandation fournie',
            'transcript': 'Transcription de la Consultation:',
            'noConsultations': 'Aucune Consultation Trouvée',
            'noConsultationsDesc': 'Ce patient n\'a pas encore effectué de consultations.',
            'disclaimer': 'Ce document est un enregistrement d\'une consultation médicale assistée par IA. Veuillez consulter un professionnel de la santé pour un diagnostic et un traitement appropriés.'
        },
        'de': {
            'patientInfo': 'Patienteninformationen',
            'name': 'Name:',
            'dob': 'Geburtsdatum:',
            'sex': 'Geschlecht:',
            'height': 'Größe:',
            'weight': 'Gewicht:',
            'medicalHistory': 'Medizinische Vorgeschichte:',
            'notProvided': 'Nicht angegeben',
            'noneReported': 'Keine angegeben',
            'consultation': 'Beratung',
            'assessedCondition': 'Beurteilter Zustand:',
            'noDiagnosis': 'Keine Diagnose angegeben',
            'recommendations': 'Empfehlungen für den Gesundheitsdienstleister:',
            'noRecommendations': 'Keine Empfehlungen angegeben',
            'transcript': 'Beratungsprotokoll:',
            'noConsultations': 'Keine Beratungen Gefunden',
            'noConsultationsDesc': 'Dieser Patient hat noch keine Beratungen abgeschlossen.',
            'disclaimer': 'Dieses Dokument ist eine Aufzeichnung einer KI-unterstützten medizinischen Beratung. Bitte konsultieren Sie einen Arzt für eine angemessene Diagnose und Behandlung.'
        },
        'it': {
            'patientInfo': 'Informazioni sul Paziente',
            'name': 'Nome:',
            'dob': 'Data di Nascita:',
            'sex': 'Sesso:',
            'height': 'Altezza:',
            'weight': 'Peso:',
            'medicalHistory': 'Storia Medica:',
            'notProvided': 'Non fornito',
            'noneReported': 'Nessuno segnalato',
            'consultation': 'Consultazione',
            'assessedCondition': 'Condizione Valutata:',
            'noDiagnosis': 'Nessuna diagnosi fornita',
            'recommendations': 'Raccomandazioni per il Fornitore di Assistenza Sanitaria:',
            'noRecommendations': 'Nessuna raccomandazione fornita',
            'transcript': 'Trascrizione della Consultazione:',
            'noConsultations': 'Nessuna Consultazione Trovata',
            'noConsultationsDesc': 'Questo paziente non ha ancora completato alcuna consultazione.',
            'disclaimer': 'Questo documento è una registrazione di una consultazione medica assistita da IA. Si prega di consultare un professionista sanitario per una diagnosi e un trattamento adeguati.'
        },
        'pt': {
            'patientInfo': 'Informações do Paciente',
            'name': 'Nome:',
            'dob': 'Data de Nascimento:',
            'sex': 'Sexo:',
            'height': 'Altura:',
            'weight': 'Peso:',
            'medicalHistory': 'Histórico Médico:',
            'notProvided': 'Não fornecido',
            'noneReported': 'Nenhum relatado',
            'consultation': 'Consulta',
            'assessedCondition': 'Condição Avaliada:',
            'noDiagnosis': 'Nenhum diagnóstico fornecido',
            'recommendations': 'Recomendações para o Profissional de Saúde:',
            'noRecommendations': 'Nenhuma recomendação fornecida',
            'transcript': 'Transcrição da Consulta:',
            'noConsultations': 'Nenhuma Consulta Encontrada',
            'noConsultationsDesc': 'Este paciente ainda não completou nenhuma consulta.',
            'disclaimer': 'Este documento é um registro de uma consulta médica assistida por IA. Por favor, consulte um profissional de saúde para diagnóstico e tratamento adequados.'
        }
    }
    
    # Get translations for selected language or fallback to English
    trans = translations.get(language, translations['en'])
    
    # Build the PDF content
    elements = []
    
    # Title
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Patient information
    elements.append(Paragraph(trans['patientInfo'], styles['Subtitle']))
    
    # Create patient info table
    patient_data = [
        [trans['name'], record.get('name', trans['notProvided'])],
        [trans['dob'], record.get('demographics', {}).get('dob', trans['notProvided'])],
        [trans['sex'], record.get('demographics', {}).get('sex', trans['notProvided'])],
        [trans['height'], record.get('demographics', {}).get('height', trans['notProvided'])],
        [trans['weight'], record.get('demographics', {}).get('weight', trans['notProvided'])],
        [trans['medicalHistory'], record.get('demographics', {}).get('medical_history', trans['noneReported'])],
    ]
    
    patient_table = Table(patient_data, colWidths=[1.5*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDINGTOP', (0, 0), (-1, -1), 4),
        ('PADDINGBOTTOM', (0, 0), (-1, -1), 4),
        ('PADDINGLEFT', (0, 0), (-1, -1), 4),
        ('PADDINGRIGHT', (0, 0), (-1, -1), 4),
    ]))
    
    elements.append(patient_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Consultations
    if record.get('entries') and len(record['entries']) > 0:
        for i, entry in enumerate(record['entries']):
            elements.append(Paragraph(f"{trans['consultation']} {i+1} ({entry.get('time', 'Unknown date')})", styles['Subtitle']))
            
            # If entry is in the new format with dates as keys
            if isinstance(entry, dict) and not ('time' in entry or 'diagnosis' in entry):
                for date, details in entry.items():
                    # For the new format, we don't have a diagnosis or recommendations
                    elements.append(Paragraph(f"Date: {date}", styles['Section']))
                    elements.append(Paragraph("Details:", styles['Section']))
                    
                    # Join the bullet points
                    details_text = "\n".join(details)
                    elements.append(Paragraph(details_text, styles['Normal']))
                    elements.append(Spacer(1, 0.1*inch))
            else:
                # For the old format with diagnosis and recommendations
                elements.append(Paragraph(trans['assessedCondition'], styles['Section']))
                elements.append(Paragraph(entry.get('diagnosis', trans['noDiagnosis']), styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))
                
                # Recommendations
                elements.append(Paragraph(trans['recommendations'], styles['Section']))
                elements.append(Paragraph(entry.get('recommendations', trans['noRecommendations']), styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))
                
                # Conversation
                elements.append(Paragraph(trans['transcript'], styles['Section']))
                
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
        elements.append(Paragraph(trans['noConsultations'], styles['Subtitle']))
        elements.append(Paragraph(trans['noConsultationsDesc'], styles['Normal']))
    
    # Disclaimer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(trans['disclaimer'], styles['Italic']))
    
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

# Utility functions for medical records
def read_medical_record(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}

def write_medical_record(data, file_path):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webform')
def webform():
    return render_template('webform.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get name and ailment from form
        user_name = request.form.get('user_name', 'Good Traveler')
        user_ailment = request.form.get('user_ailment', '')
        
        # Set default language to English
        language = request.form.get('language', 'en')
        
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
            session['current_concern'] = user_ailment
        
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

@app.route('/api/set_language', methods=['POST'])
def api_set_language():
    """API endpoint for changing language preference"""
    data = request.get_json()
    language = data.get('language', 'en')
    
    # Store language preference in session
    session['language'] = language
    
    return jsonify({
        'status': 'success',
        'language': language
    })

@app.route("/submit_webform", methods=["POST"])
def submit_webform():
    # Get form data
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    dob = request.form.get("dob")
    gender = request.form.get("gender")
    height = request.form.get("height")
    weight = request.form.get("weight")
    reason = request.form.get("reason")
    language = request.form.get("language", "en")
    
    # Calculate age from DOB
    birth_date = datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.now()
    age = (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )
    
    # Create a unique identifier for this patient
    identifier = str(uuid.uuid4())
    
    # Process reason for visit with GPT
    gpt_prompt = f"Given the following description of a patient's reason for visit, extract and convert it into a concise, organized bulleted list of symptoms and concerns. Do not use 'You' or 'Your' in the response. '{reason}'"
    processed_reason = generate_openai_response(gpt_prompt)
    
    if processed_reason:
        processed_reason = processed_reason.strip().split("\n")
    else:
        processed_reason = [
            f"- {reason}"
        ]  # Fallback to original reason if GPT processing fails
    
    # Construct the JSON file path using the unique identifier
    json_file = f"medical_record_{identifier}.json"
    json_file_path = os.path.join(app.root_path, "static", "user_data", json_file)
    
    # Create user history record
    user_history = {
        "fname": first_name,
        "lname": last_name,
        "age": str(age),
        "dob": dob,
        "gender": gender,
        "height": height,
        "weight": weight,
        "identifier": identifier,
        "language": language,
        "entries": []
    }
    
    # Add new entry
    current_time = datetime.now().strftime("%m/%d/%Y %I:%M%p")
    new_entry = {current_time: ["- Patient filled out webform."] + processed_reason}
    user_history["entries"].append(new_entry)
    
    # Store in session for compatibility with existing code
    session['user_name'] = f"{first_name} {last_name}"
    session['demographics'] = {
        'first_name': first_name,
        'last_name': last_name,
        'age': str(age),
        'sex': gender.lower(),
        'height': height,
        'weight': weight,
        'dob': dob
    }
    
    # Save the medical record to a file
    write_medical_record(user_history, json_file_path)
    
    # Redirect to medical record page
    return redirect(url_for("medical_record", identifier=identifier, language=language))

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
    user_id = data.get('user_id')
    user_name = data.get('user_name', 'Good Traveler')
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
            # Process this demographic answer
            current_question = demographic_questions[current_question_index]
            answer = interpret_demographic_response(user_input, current_question)
            
            # Store the demographic information
            if 'demographics' not in session:
                session['demographics'] = {}
            
            session['demographics'][current_question["id"]] = answer
            
            # Move to the next question
            next_question_index = current_question_index + 1
            session['current_demographic_question'] = next_question_index
            
            # Check if we have more demographic questions
            if next_question_index < len(demographic_questions):
                # Get the next demographic question
                next_question = demographic_questions[next_question_index]
                
                if "options" in next_question:
                    options_text = ", ".join(next_question["options"])
                    question_text = f"{next_question['question']} ({options_text})"
                else:
                    question_text = next_question['question']
                
                # Get audio if needed
                audio_base64 = None
                if data.get('audio_enabled', False):
                    audio_base64 = text_to_speech(question_text, language)
                
                # Add to chat history
                session['current_chat'].append(f"Physician: {question_text}")
                
                return jsonify({
                    'message': question_text,
                    'audio': audio_base64,
                    'is_demographic': True
                })
            else:
                # All demographics collected, start the actual consultation
                session['demographics_collected'] = True
                
                # Get the initial question from the decision tree
                root_question = decisionTree["root"]["question"]
                
                # Create a transition message
                transition = f"Thank you for providing that information. Now, let's discuss your health concerns. {root_question}"
                
                # Add to chat history
                session['current_chat'].append(f"Physician: {transition}")
                
                # Get audio if needed
                audio_base64 = None
                if data.get('audio_enabled', False):
                    audio_base64 = text_to_speech(transition, language)
                
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
        'redirect': f'/medical-form?user_id={user_id}'
    })

@app.route('/medical-form')
def medical_record():
    identifier = request.args.get('identifier')
    user_id = request.args.get('user_id')
    language = request.args.get('language', 'en')
    
    # If an identifier is provided, load from JSON file
    if identifier:
        json_file = f"medical_record_{identifier}.json"
        json_file_path = os.path.join(app.root_path, "static", "user_data", json_file)
        
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                record = json.load(file)
        else:
            # If JSON doesn't exist, create a default structure
            record = {
                'fname': 'Unknown',
                'lname': 'Patient',
                'entries': [],
                'identifier': identifier,
                'language': language
            }
    # If user_id is provided, load from session (legacy method)
    elif user_id:
        # Store the user's chosen language in the session
        if language and language != session.get('language'):
            session['language'] = language
            
        record = {
            'name': session.get('user_name', 'Unknown Patient'),
            'fname': session.get('user_name', '').split()[0] if session.get('user_name', '') else 'Unknown',
            'lname': session.get('user_name', '').split()[-1] if len(session.get('user_name', '').split()) > 1 else 'Patient',
            'demographics': session.get('demographics', {}),
            'entries': session.get('medical_entries', []),
            'language': session.get('language', 'en')
        }
    else:
        return "Patient identifier is required", 400
    
    # Add current date for the record
    current_date = datetime.now().strftime("%B %d, %Y")
    current_year = datetime.now().year
    
    return render_template('medical-form.html', record=record, current_date=current_date, current_year=current_year)

@app.route('/api/export_record', methods=['POST'])
def export_record():
    """API endpoint for exporting medical records as PDF"""
    try:
        identifier = request.form.get('identifier')
        user_id = request.form.get('user_id')
        language = request.form.get('language', 'en')
        export_format = request.form.get('format', 'pdf')
        
        # Determine record source (file or session)
        if identifier:
            json_file = f"medical_record_{identifier}.json"
            json_file_path = os.path.join(app.root_path, "static", "user_data", json_file)
            
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as file:
                    record = json.load(file)
                
                # Add name field for compatibility with PDF generator
                if 'fname' in record and 'lname' in record:
                    record['name'] = f"{record['fname']} {record['lname']}"
                
                # Update demographics format for compatibility with PDF generator
                if 'demographics' not in record:
                    record['demographics'] = {
                        'sex': record.get('gender', '').lower(),
                        'dob': record.get('dob', ''),
                        'height': record.get('height', ''),
                        'weight': record.get('weight', ''),
                        'medical_history': ''
                    }
            else:
                return jsonify({'status': 'error', 'message': 'Medical record not found'}), 404
        elif user_id:
            # Use session data (legacy method)
            record = {
                'name': session.get('user_name', 'Unknown Patient'),
                'demographics': session.get('demographics', {}),
                'entries': session.get('medical_entries', [])
            }
        else:
            return jsonify({'status': 'error', 'message': 'Patient identifier is required'}), 400
        
        # Create a localized PDF title based on language
        pdf_titles = {
            'en': 'Hen Health Medical Record',
            'es': 'Registro Médico de Hen Health',
            'fr': 'Dossier Médical de Hen Health',
            'de': 'Hen Health Krankenakte',
            'it': 'Cartella Clinica di Hen Health',
            'pt': 'Registro Médico de Hen Health'
        }
        
        if export_format == 'pdf':
            # Generate PDF with localized title
            pdf_title = pdf_titles.get(language, pdf_titles['en'])
            pdf_data = generate_medical_record_pdf(record, title=pdf_title, language=language)
            
            # Create a unique filename with language code
            patient_name = record.get('name', 'Unknown_Patient').replace(' ', '_')
            filename = f"medical_record_{patient_name}_{language}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Return the PDF as a download
            response = make_response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            return response
        else:
            # Default to web view if not PDF
            if identifier:
                return jsonify({
                    'status': 'success',
                    'url': f'/medical-form?identifier={identifier}&language={language}'
                })
            else:
                return jsonify({
                    'status': 'success',
                    'url': f'/medical-form?user_id={user_id}&language={language}'
                })
    except Exception as e:
        logger.error(f"Error exporting record: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)