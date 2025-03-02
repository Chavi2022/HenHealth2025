decisionTree = {
    "root": {
        "question": "Good day! What's your primary symptom today?",
        "fever": "fever",
        "cough": "cough",
        "shortness_of_breath": "breathing_difficulty",
        "fatigue": "fatigue",
        "pain": "pain_location",
        "digestive": "digestive_issues",
        "skin": "skin_issues",
        "mental": "mental_health_issues",
        "sleep": "sleep_issues",
        "none": "general_health",
    },
    
    # FEVER BRANCH
    "fever": {
        "question": "Is your fever high (above 101°F/38.3°C) or have you had it for more than 3 days?",
        "yes": "high_fever",
        "no": "low_fever",
    },
    "high_fever": {
        "question": "Do you also have any of these symptoms: rash, severe headache, stiff neck, or extreme fatigue?",
        "yes": "fever_with_serious_symptoms",
        "no": "fever_without_serious_symptoms",
    },
    "low_fever": {
        "question": "Do you have any other cold or flu-like symptoms such as runny nose, sore throat, or body aches?",
        "yes": "mild_viral_infection",
        "no": "low_grade_fever",
    },
    "fever_with_serious_symptoms": {
        "question": "Do you also have confusion, difficulty waking up, or rapid breathing?",
        "yes": "emergency_fever_condition",
        "no": "serious_fever_condition",
    },
    "fever_without_serious_symptoms": {
        "question": "Have you traveled to areas with endemic diseases or been in contact with someone who was ill?",
        "yes": "travel_related_fever",
        "no": "standard_viral_infection",
    },
    
    # COUGH BRANCH
    "cough": {
        "question": "Is your cough persistent (lasting more than a week) or producing colored phlegm?",
        "yes": "persistent_cough",
        "no": "mild_cough",
    },
    "persistent_cough": {
        "question": "Do you also have chest pain, wheezing, or shortness of breath?",
        "yes": "respiratory_condition",
        "no": "chronic_cough",
    },
    "mild_cough": {
        "question": "Is your cough mainly dry, or do you produce clear phlegm?",
        "dry": "dry_cough",
        "phlegm": "productive_cough",
    },
    "respiratory_condition": {
        "question": "Have you recently had a fever or been exposed to someone with a respiratory infection?",
        "yes": "infectious_respiratory_condition",
        "no": "non_infectious_respiratory_condition",
    },
    "chronic_cough": {
        "question": "Do you notice your cough is worse at night, after eating, or when you're in certain environments?",
        "night": "nocturnal_cough",
        "after_eating": "gerd_related_cough",
        "environments": "allergic_cough",
    },
    
    # BREATHING DIFFICULTY BRANCH
    "breathing_difficulty": {
        "question": "Do you experience shortness of breath at rest, or only during physical activity?",
        "rest": "severe_breathing_issue",
        "activity": "mild_breathing_issue",
    },
    "severe_breathing_issue": {
        "question": "Do you have a history of asthma, COPD, or heart problems?",
        "yes": "chronic_respiratory_condition",
        "no": "acute_breathing_issue",
    },
    "mild_breathing_issue": {
        "question": "Does your breathing difficulty worsen in certain environments or during allergy season?",
        "yes": "environmental_breathing_issue",
        "no": "exercise_related_breathing",
    },
    "chronic_respiratory_condition": {
        "question": "Are you currently using prescribed inhalers or other respiratory medications?",
        "yes": "managed_respiratory_condition",
        "no": "unmanaged_respiratory_condition",
    },
    "acute_breathing_issue": {
        "question": "Did the breathing difficulty start suddenly or gradually over days?",
        "suddenly": "emergent_breathing_issue",
        "gradually": "progressive_breathing_issue",
    },
    
    # FATIGUE BRANCH
    "fatigue": {
        "question": "Has your fatigue developed suddenly over days, or gradually over weeks or months?",
        "suddenly": "acute_fatigue",
        "gradually": "chronic_fatigue",
    },
    "acute_fatigue": {
        "question": "Have you recently had an infection, or are you experiencing significant stress?",
        "infection": "post_infectious_fatigue",
        "stress": "stress_related_fatigue",
        "no": "unexplained_acute_fatigue",
    },
    "chronic_fatigue": {
        "question": "Do you wake up feeling rested after a full night's sleep?",
        "yes": "daytime_fatigue",
        "no": "sleep_related_fatigue",
    },
    "sleep_related_fatigue": {
        "question": "Do you snore loudly or has anyone observed you stop breathing during sleep?",
        "yes": "sleep_apnea_suspected",
        "no": "insomnia_suspected",
    },
    "daytime_fatigue": {
        "question": "Do you also experience muscle or joint pain, memory problems, or frequent headaches?",
        "yes": "chronic_fatigue_syndrome_suspected",
        "no": "general_fatigue",
    },
    
    # PAIN BRANCH
    "pain_location": {
        "question": "Where is your pain primarily located?",
        "head": "headache",
        "chest": "chest_pain",
        "abdomen": "abdominal_pain",
        "joints": "joint_pain",
        "back": "back_pain",
        "neck": "neck_pain",
        "extremities": "extremity_pain",
    },
    "headache": {
        "question": "Is your headache severe, sudden, or the worst you've ever experienced?",
        "yes": "severe_headache",
        "no": "mild_headache",
    },
    "chest_pain": {
        "question": "Is your chest pain sharp and worsened by breathing deeply, or is it more of a pressure or squeezing sensation?",
        "sharp": "pleuritic_chest_pain",
        "pressure": "cardiac_chest_pain",
    },
    "abdominal_pain": {
        "question": "Where in your abdomen is the pain located?",
        "upper_right": "upper_right_abdominal_pain",
        "upper_left": "upper_left_abdominal_pain",
        "lower_right": "lower_right_abdominal_pain",
        "lower_left": "lower_left_abdominal_pain",
        "central": "central_abdominal_pain",
    },
    "joint_pain": {
        "question": "Are multiple joints affected, or just one?",
        "multiple": "polyarthralgia",
        "one": "monoarthralgia",
    },
    "back_pain": {
        "question": "Is your back pain in the upper, middle, or lower back?",
        "upper": "upper_back_pain",
        "middle": "middle_back_pain",
        "lower": "lower_back_pain",
    },
    "mild_headache": {
        "question": "Is the pain throbbing, pressure-like, or sharp?",
        "throbbing": "migraine_suspected",
        "pressure": "tension_headache",
        "sharp": "cluster_headache_suspected",
    },
    "severe_headache": {
        "question": "Do you also have vision changes, confusion, or neck stiffness?",
        "yes": "emergency_headache",
        "no": "severe_headache_workup",
    },
    
    # DIGESTIVE ISSUES BRANCH
    "digestive_issues": {
        "question": "What digestive symptom is bothering you most?",
        "nausea": "nausea",
        "vomiting": "vomiting",
        "diarrhea": "diarrhea",
        "constipation": "constipation",
        "heartburn": "heartburn",
        "bloating": "bloating",
    },
    "nausea": {
        "question": "Is your nausea accompanied by vomiting, dizziness, or pain?",
        "vomiting": "nausea_with_vomiting",
        "dizziness": "nausea_with_dizziness",
        "pain": "nausea_with_pain",
        "none": "isolated_nausea",
    },
    "vomiting": {
        "question": "How long have you been vomiting?",
        "hours": "acute_vomiting",
        "days": "persistent_vomiting",
        "weeks": "chronic_vomiting",
    },
    "diarrhea": {
        "question": "Is there blood in your stool, or have you had diarrhea for more than 3 days?",
        "blood": "bloody_diarrhea",
        "duration": "persistent_diarrhea",
        "no": "acute_diarrhea",
    },
    "constipation": {
        "question": "How long have you been experiencing constipation?",
        "days": "recent_constipation",
        "weeks": "persistent_constipation",
        "months": "chronic_constipation",
    },
    
    # SKIN ISSUES BRANCH
    "skin_issues": {
        "question": "What type of skin issue are you experiencing?",
        "rash": "skin_rash",
        "itching": "skin_itching",
        "sores": "skin_sores",
        "discoloration": "skin_discoloration",
    },
    "skin_rash": {
        "question": "Is the rash itchy, painful, or neither?",
        "itchy": "itchy_rash",
        "painful": "painful_rash",
        "neither": "non_symptomatic_rash",
    },
    "itchy_rash": {
        "question": "Did the rash appear suddenly or gradually?",
        "suddenly": "acute_itchy_rash",
        "gradually": "chronic_itchy_rash",
    },
    "skin_itching": {
        "question": "Is the itching localized to one area or all over your body?",
        "localized": "localized_itching",
        "all_over": "generalized_itching",
    },
    
    # MENTAL HEALTH BRANCH
    "mental_health_issues": {
        "question": "What mental health concern would you like to discuss?",
        "anxiety": "anxiety_issues",
        "depression": "depression_issues",
        "stress": "stress_issues",
        "sleep": "sleep_mental_issues",
        "other": "other_mental_issues",
    },
    "anxiety_issues": {
        "question": "Do you experience persistent worry, racing thoughts, or physical symptoms like rapid heartbeat?",
        "worry": "general_anxiety",
        "physical": "panic_symptoms",
        "both": "mixed_anxiety",
    },
    "depression_issues": {
        "question": "Are you experiencing prolonged sadness, lack of interest in activities, or changes in sleep or appetite?",
        "sadness": "depressive_symptoms",
        "interest": "anhedonia",
        "both": "major_depression_suspected",
    },
    
    # SLEEP ISSUES BRANCH
    "sleep_issues": {
        "question": "What sleep problem are you experiencing?",
        "falling_asleep": "insomnia_initial",
        "staying_asleep": "insomnia_middle",
        "early_waking": "insomnia_terminal",
        "excessive_sleep": "hypersomnia",
        "abnormal_behaviors": "parasomnia",
    },
    "insomnia_initial": {
        "question": "How long does it typically take you to fall asleep?",
        "30_minutes": "mild_initial_insomnia",
        "1_hour": "moderate_initial_insomnia",
        "hours": "severe_initial_insomnia",
    },
    "insomnia_middle": {
        "question": "How often do you wake up during the night?",
        "once": "mild_middle_insomnia",
        "few_times": "moderate_middle_insomnia",
        "many_times": "severe_middle_insomnia",
    },
    
    # GENERAL HEALTH BRANCH
    "general_health": {
        "question": "What aspect of your health would you like to discuss?",
        "preventative": "preventative_care",
        "nutrition": "nutrition_advice",
        "exercise": "exercise_advice",
        "mental": "mental_health",
        "chronic": "chronic_disease_management",
    },
    "preventative_care": {
        "question": "What age range do you fall into?",
        "child": "pediatric_preventative",
        "teen": "adolescent_preventative",
        "adult": "adult_preventative",
        "senior": "senior_preventative",
    },
    "nutrition_advice": {
        "question": "Do you have specific dietary concerns or goals?",
        "weight_loss": "weight_loss_nutrition",
        "health_condition": "medical_nutrition",
        "general": "general_nutrition",
        "vegetarian": "plant_based_nutrition",
    },
    "exercise_advice": {
        "question": "What is your current activity level?",
        "sedentary": "sedentary_exercise_plan",
        "light": "light_exercise_plan",
        "moderate": "moderate_exercise_plan",
        "active": "active_exercise_plan",
    },
    
    # DIAGNOSES AND RECOMMENDATIONS
    "emergency_fever_condition": "a potentially serious condition requiring immediate medical attention. Please go to the emergency room or call 911.",
    "serious_fever_condition": "a potentially serious infection requiring prompt medical attention. Please consult with a healthcare provider within 24 hours.",
    "travel_related_fever": "a fever that may be related to travel or exposure. This requires medical evaluation to rule out specific infectious diseases.",
    "standard_viral_infection": "likely a viral infection. Rest, stay hydrated, and take acetaminophen for fever. Consult a doctor if symptoms worsen or persist beyond 5 days.",
    "mild_viral_infection": "a common cold or mild respiratory infection. Rest, stay hydrated, and monitor your symptoms.",
    "low_grade_fever": "a mild inflammation or infection. Monitor your temperature and consult a doctor if it persists beyond 3 days.",
    
    "infectious_respiratory_condition": "a possible respiratory infection such as bronchitis or pneumonia. Please schedule an appointment with a healthcare provider.",
    "non_infectious_respiratory_condition": "a non-infectious respiratory condition such as asthma or COPD. Please consult with a healthcare provider for proper evaluation and treatment.",
    "nocturnal_cough": "a cough that worsens at night, which may be related to post-nasal drip or asthma. Please consult with a healthcare provider for evaluation.",
    "gerd_related_cough": "a cough that may be related to acid reflux. Try avoiding large meals before bedtime and consult with a healthcare provider.",
    "allergic_cough": "a cough that may be triggered by environmental allergies. Consider avoiding triggers and consult with an allergist.",
    "dry_cough": "a viral infection or irritant-related cough. Stay hydrated and consider honey for symptom relief (if over 1 year of age).",
    "productive_cough": "a respiratory infection. Monitor the color of your phlegm and seek medical attention if it turns yellow or green.",
    
    "managed_respiratory_condition": "an exacerbation of your respiratory condition. Continue your prescribed medications and contact your doctor if symptoms don't improve.",
    "unmanaged_respiratory_condition": "a respiratory condition that requires medical management. Please consult with a healthcare provider promptly.",
    "emergent_breathing_issue": "a sudden breathing problem that requires immediate medical attention. Please seek emergency care.",
    "progressive_breathing_issue": "a gradually worsening breathing problem that requires medical evaluation. Please schedule an appointment with a healthcare provider.",
    "environmental_breathing_issue": "likely allergic or environmental asthma. Consider avoiding triggers and consult with a healthcare provider about appropriate medications.",
    "exercise_related_breathing": "possible exercise-induced bronchospasm. A healthcare provider can recommend appropriate pre-exercise treatments.",
    
    "post_infectious_fatigue": "post-infectious fatigue syndrome. Rest appropriately and gradually return to activities as you recover.",
    "stress_related_fatigue": "stress-related fatigue. Consider stress management techniques and ensure adequate sleep.",
    "unexplained_acute_fatigue": "unexplained fatigue that warrants medical evaluation. Please consult with a healthcare provider.",
    "sleep_apnea_suspected": "possible sleep apnea. This condition requires evaluation by a sleep specialist. Please consult with your healthcare provider for a referral.",
    "insomnia_suspected": "possible insomnia. Try improving sleep hygiene and consult with a healthcare provider if it persists.",
    "chronic_fatigue_syndrome_suspected": "symptoms consistent with chronic fatigue syndrome. This requires comprehensive medical evaluation. Please consult with a healthcare provider.",
    "general_fatigue": "general fatigue that may be related to lifestyle factors. Consider your diet, exercise, and stress levels, and ensure adequate sleep.",
    
    "migraine_suspected": "symptoms consistent with migraine headaches. Over-the-counter pain relievers may help, but consider consulting with a healthcare provider for preventive options.",
    "tension_headache": "likely a tension headache. Consider stress management, good posture, and over-the-counter pain relievers if needed.",
    "cluster_headache_suspected": "symptoms consistent with cluster headaches. These can be severe and require medical management. Please consult with a healthcare provider.",
    "emergency_headache": "a potentially serious headache requiring immediate medical attention. Please seek emergency care.",
    "severe_headache_workup": "a severe headache requiring medical evaluation. Please consult with a healthcare provider promptly.",
    
    "pleuritic_chest_pain": "chest pain that may indicate pleurisy or other respiratory issues. Please consult with a healthcare provider.",
    "cardiac_chest_pain": "chest pain that could indicate a cardiac issue. Please seek immediate medical attention.",
    
    "upper_right_abdominal_pain": "possible gallbladder or liver issue. Please consult with a healthcare provider for proper evaluation.",
    "upper_left_abdominal_pain": "possible splenic or gastric issue. Please consult with a healthcare provider for proper evaluation.",
    "lower_right_abdominal_pain": "possible appendicitis or other condition requiring medical attention. Please consult with a healthcare provider promptly.",
    "lower_left_abdominal_pain": "possible diverticulitis or bowel inflammation. Please consult with a healthcare provider for evaluation.",
    "central_abdominal_pain": "possible gastritis, peptic ulcer, or pancreatitis. Please consult with a healthcare provider for evaluation.",
    
    "polyarthralgia": "inflammation affecting multiple joints, which may indicate a systemic condition. Please consult with a healthcare provider.",
    "monoarthralgia": "single joint inflammation, possibly due to injury or localized arthritis. Please consult with a healthcare provider for evaluation.",
    
    "upper_back_pain": "upper back pain which may be related to muscle strain, posture, or stress. Consider gentle stretching and proper ergonomics.",
    "middle_back_pain": "middle back pain which may indicate muscle strain or thoracic spine issues. Please consult with a healthcare provider if persistent.",
    "lower_back_pain": "lower back pain which is commonly due to muscle strain. Rest, gentle stretching, and over-the-counter pain relievers may help.",
    
    "nausea_with_vomiting": "nausea and vomiting which could be due to gastroenteritis, food poisoning, or other conditions. Stay hydrated and seek medical attention if severe or persistent.",
    "nausea_with_dizziness": "nausea with dizziness which may indicate an inner ear problem, low blood pressure, or other conditions. Please consult with a healthcare provider.",
    "nausea_with_pain": "nausea with pain which could indicate various gastrointestinal conditions. Please consult with a healthcare provider for evaluation.",
    "isolated_nausea": "isolated nausea which may be due to dietary factors, medication effects, or stress. Monitor symptoms and consult a healthcare provider if persistent.",
    
    "acute_vomiting": "acute vomiting which may be due to gastroenteritis or food poisoning. Stay hydrated and seek medical attention if severe or persistent.",
    "persistent_vomiting": "persistent vomiting requiring medical evaluation. Please consult with a healthcare provider.",
    "chronic_vomiting": "chronic vomiting requiring comprehensive medical evaluation. Please consult with a healthcare provider promptly.",
    
    "bloody_diarrhea": "diarrhea with blood, which requires immediate medical attention. Please consult with a healthcare provider promptly.",
    "persistent_diarrhea": "persistent diarrhea requiring medical evaluation. Please consult with a healthcare provider.",
    "acute_diarrhea": "acute diarrhea which is commonly due to viral gastroenteritis. Stay well-hydrated and consider over-the-counter anti-diarrheal medication if appropriate.",
    
    "recent_constipation": "recent constipation which may be related to dietary changes or medication. Increase fluid and fiber intake, and consider over-the-counter laxatives if appropriate.",
    "persistent_constipation": "persistent constipation requiring medical evaluation. Please consult with a healthcare provider.",
    "chronic_constipation": "chronic constipation requiring comprehensive evaluation. Please consult with a healthcare provider.",
    
    "acute_itchy_rash": "an acute itchy rash which may be due to an allergic reaction or contact dermatitis. Consider over-the-counter antihistamines and avoid potential triggers.",
    "chronic_itchy_rash": "a chronic itchy rash requiring medical evaluation. Please consult with a healthcare provider or dermatologist.",
    "painful_rash": "a painful rash requiring medical evaluation. Please consult with a healthcare provider promptly.",
    "non_symptomatic_rash": "a non-symptomatic rash which may be monitored. If it persists or changes, please consult with a healthcare provider.",
    
    "localized_itching": "localized itching which may be due to dry skin, contact dermatitis, or insect bites. Consider moisturizers and over-the-counter anti-itch creams.",
    "generalized_itching": "generalized itching which may indicate a systemic condition or allergic reaction. Please consult with a healthcare provider for evaluation.",
    
    "general_anxiety": "symptoms consistent with general anxiety. Consider stress management techniques and consult with a healthcare provider for comprehensive evaluation and treatment options.",
    "panic_symptoms": "symptoms consistent with panic or anxiety. If these are severe or recurrent, please consult with a healthcare provider for evaluation and treatment options.",
    "mixed_anxiety": "significant anxiety symptoms that warrant professional evaluation. Please consult with a healthcare provider or mental health professional.",
    
    "depressive_symptoms": "symptoms that may indicate depression. Please consult with a healthcare provider or mental health professional for evaluation and support.",
    "anhedonia": "loss of interest or pleasure which may indicate depression. Please consult with a healthcare provider or mental health professional.",
    "major_depression_suspected": "symptoms consistent with depression that warrant professional evaluation. Please consult with a healthcare provider or mental health professional promptly.",
    
    "mild_initial_insomnia": "mild difficulty falling asleep. Consider improving sleep hygiene by maintaining a regular sleep schedule and creating a relaxing bedtime routine.",
    "moderate_initial_insomnia": "moderate difficulty falling asleep. Improve sleep hygiene and consider consulting with a healthcare provider if it persists.",
    "severe_initial_insomnia": "severe difficulty falling asleep requiring medical evaluation. Please consult with a healthcare provider.",
    
    "mild_middle_insomnia": "occasional night waking. Consider limiting fluids before bedtime and ensuring a comfortable sleep environment.",
    "moderate_middle_insomnia": "frequent night waking that warrants attention. Improve sleep hygiene and consider consulting with a healthcare provider if it persists.",
    "severe_middle_insomnia": "very disrupted sleep requiring medical evaluation. Please consult with a healthcare provider.",
    
    "pediatric_preventative": "recommended preventative care for children includes regular check-ups, vaccinations, dental care, and vision screening. Please consult with a pediatrician for age-appropriate recommendations.",
    "adolescent_preventative": "recommended preventative care for adolescents includes regular check-ups, vaccinations, sexual health education, and mental health screening. Please consult with a healthcare provider for age-appropriate recommendations.",
    "adult_preventative": "recommended preventative care for adults includes regular check-ups, age-appropriate cancer screenings, vaccinations, and healthy lifestyle practices.",
    "senior_preventative": "recommended preventative care for seniors includes regular check-ups, vaccinations, cancer screenings, fall prevention, and cognitive assessments. Please consult with a healthcare provider for personalized recommendations.",
    
    "weight_loss_nutrition": "effective weight management involves a balanced diet with appropriate portions, regular physical activity, and behavioral strategies. Consider consulting with a registered dietitian for personalized guidance.",
    "medical_nutrition": "nutritional considerations for medical conditions require personalized guidance. Please consult with a registered dietitian who can work with your healthcare provider.",
    "general_nutrition": "a healthy diet includes a variety of fruits, vegetables, whole grains, lean proteins, and healthy fats. Limit processed foods, added sugars, and excessive sodium.",
    "plant_based_nutrition": "plant-based diets can be nutritionally complete when properly planned. Ensure adequate protein, vitamin B12, iron, calcium, and zinc. Consider consulting with a registered dietitian for guidance.",
    
    "sedentary_exercise_plan": "if you're currently inactive, start with light activities like walking for 10-15 minutes daily and gradually increase duration and intensity. Aim for 150 minutes of moderate activity per week as a long-term goal.",
    "light_exercise_plan": "build on your current activity by gradually increasing to 150 minutes of moderate activity per week. Consider adding strength training 2 days per week.",
    "moderate_exercise_plan": "maintain your 150 minutes of moderate activity weekly and ensure you're incorporating strength training 2 days per week. Consider adding flexibility and balance exercises.",
    "active_exercise_plan": "maintain your active lifestyle and ensure proper recovery between workouts. Consider cross-training to prevent overuse injuries and incorporate all components of fitness: cardio, strength, flexibility, and balance.",
}