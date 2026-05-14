from flask import Blueprint, request, jsonify, current_app, render_template_string
import os
import requests
import sqlite3
from datetime import datetime
from openai import OpenAI
from flask_mail import Message
from app import mail

bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# Initialize OpenAI client
client = OpenAI()

DEMO_MODE = True
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

def smart_fallback(action, text=None, user_input=None):
    """SMART FALLBACK ENGINE"""
    
    # 1. Action-based responses
    if action == 'improve':
        return f"<ul>\n<li>Enhanced tone and clarity for professional presentation</li>\n<li>Restructured phrasing to improve readability and impact</li>\n</ul>"
    elif action == 'rewrite':
        return f"<ul>\n<li>Restructured professionally using industry-standard formatting</li>\n<li>Replaced passive voice with strong active action verbs</li>\n</ul>"
    elif action == 'generate':
        return f"<ul>\n<li>Created comprehensive bullet points based on your background</li>\n<li>Demonstrated clear impact through structured achievements</li>\n</ul>"
    elif action == 'optimize':
        return f"<ul>\n<li>Added strong action verbs to highlight accomplishments</li>\n<li>Optimized keywords to better align with target industry standards</li>\n</ul>"
    elif action == 'ats':
        return f"<ul>\n<li><b>ATS Score: 80/100</b></li>\n<li>Improvement: Quantify your achievements with metrics and percentages</li>\n<li>Strengthen your keyword match against the job description</li>\n</ul>"
    
    # 2. Intent Detection Engine based on user_input
    if user_input:
        user_input_lower = user_input.lower()
        
        # Dynamic content example
        if "website" in user_input_lower:
            return "<ul>\n<li>Developed a responsive website improving user experience</li>\n<li>Implemented modern UI techniques</li>\n</ul>"
            
        elif any(kw in user_input_lower for kw in ["professional summary", "summary", "about me"]):
            return "<ul>\n<li>Results-driven [Job Title] with [X years] of experience in [industry]</li>\n<li>Skilled in [key skills] with proven success in [achievement]</li>\n<li>Strong expertise in [tools/technologies]</li>\n<li>Seeking to contribute to [company/role]</li>\n</ul>"
            
        elif any(kw in user_input_lower for kw in ["objective", "career objective"]):
            return "<ul>\n<li>Motivated individual seeking a role as [Job Title]</li>\n<li>Passionate about applying skills in [domain]</li>\n<li>Committed to contributing to organizational growth</li>\n</ul>"
            
        elif any(kw in user_input_lower for kw in ["experience", "work", "job"]):
            return "<ul>\n<li>Led key initiatives improving efficiency and productivity</li>\n<li>Collaborated with cross-functional teams</li>\n<li>Delivered measurable results within deadlines</li>\n</ul>"
            
        elif "project" in user_input_lower:
            return "<ul>\n<li>Developed a project using [technologies]</li>\n<li>Implemented solutions to real-world problems</li>\n<li>Achieved performance improvements and scalability</li>\n</ul>"
            
        elif "skills" in user_input_lower:
            return "<ul>\n<li><b>Technical Skills:</b> Python, JavaScript, SQL</li>\n<li><b>Soft Skills:</b> Communication, Leadership, Problem-solving</li>\n</ul>"
            
        elif "education" in user_input_lower:
            return "<ul>\n<li>Bachelor’s Degree in [Field] – [University]</li>\n<li>Year: [YYYY]</li>\n</ul>"
            
        else:
            return f"<p>I am your AI career assistant. Regarding '{user_input}', I recommend tailoring your terminology to the specific job description and utilizing strong action verbs.</p>"

    return "<p>How can I assist you with your resume today?</p>"

def call_ai_api(action, text, custom_prompt=None):
    if DEMO_MODE:
        return smart_fallback(action, text, custom_prompt)

    api_key = os.environ.get('OPENAI_API_KEY')
    hf_token = os.environ.get('HF_API_TOKEN')

    if not api_key and not hf_token:
        return smart_fallback(action, text, custom_prompt)

    try:
        if api_key:
            prompt_map = {
                'improve': f"Improve the following resume text professionally:\n{text}",
                'rewrite': f"Rewrite the following resume content with strong achievements:\n{text}",
                'generate': f"Generate 3 strong resume bullet points:\n{text}",
                'optimize': f"Optimize the text with keywords and action verbs:\n{text}",
                'ats': f"Give ATS feedback with improvements:\n{text}"
            }

            if action == 'custom':
                prompt = f"Act as an expert resume writer.\nRequest: {custom_prompt}\nContext: {text}"
            else:
                prompt = prompt_map.get(action, f"Analyze:\n{text}")

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional resume writer and ATS expert. Give concise, impactful responses. Use HTML formatting with <ul><li> for bullet points. Never mention mock responses."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )

            return response.choices[0].message.content

        elif hf_token:
            headers = {"Authorization": f"Bearer {hf_token}"}
            prompt = f"<s>[INST] You are a professional resume writer. Task: {action}. Context: {text} [/INST]"
            payload = {"inputs": prompt, "parameters": {"max_new_tokens": 250, "temperature": 0.7}}
            hf_res = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
            if hf_res.status_code == 200:
                result = hf_res.json()
                return result[0].get('generated_text', '').split('[/INST]')[-1].strip()
            else:
                raise Exception("HF API failed")

    except Exception as e:
        current_app.logger.error(f"AI API Error: {e}")
        return smart_fallback(action, text, custom_prompt)

# =======================
# NEW ROUTES
# =======================
def handle_route(action):
    data = request.get_json() or {}
    text = data.get('text', '')
    custom_prompt = data.get('custom_prompt', '')
    
    suggestion = call_ai_api(action, text, custom_prompt)
    
    return jsonify({
        "status": "success",
        "suggestion": suggestion
    })

@bp.route('/improve', methods=['POST'])
def ai_improve(): return handle_route('improve')

@bp.route('/rewrite', methods=['POST'])
def ai_rewrite(): return handle_route('rewrite')

@bp.route('/generate', methods=['POST'])
def ai_generate(): return handle_route('generate')

@bp.route('/optimize', methods=['POST'])
def ai_optimize(): return handle_route('optimize')

@bp.route('/ats', methods=['POST'])
def ai_ats(): return handle_route('ats')

@bp.route('/custom', methods=['POST'])
def ai_custom(): return handle_route('custom')

# =======================
# CHAT ROUTE
# =======================
@bp.route('/chat', methods=['POST'])
def ai_chat():
    data = request.get_json() or {}
    messages = data.get('messages', [])
    context = data.get('context', '')
    
    # Extract last user message
    last_message = ""
    if messages and len(messages) > 0:
        last_message = messages[-1].get('content', '')

    if DEMO_MODE:
        return jsonify({
            "status": "success",
            "suggestion": smart_fallback('custom', context, last_message)
        })

    api_key = os.environ.get('OPENAI_API_KEY')
    hf_token = os.environ.get('HF_API_TOKEN')

    if not api_key and not hf_token:
        return jsonify({
            "status": "success",
            "suggestion": smart_fallback('custom', context, last_message)
        })

    try:
        user_skills = data.get('userSkills', {})
        target_role = data.get('targetRole', '')
        
        if api_key:
            system_msg = "You are an expert resume writer and career coach. Provide professional, concise, and ATS-optimized responses. Use HTML tags for formatting."
            
            # Inject context
            context_string = ""
            if target_role:
                context_string += f"Target Role: {target_role}\n"
            if user_skills:
                context_string += f"Skills: {user_skills}\n"
            if context:
                context_string += f"Selected Text:\n{context}\n"

            if context_string:
                system_msg += f"\n\nContext:\n{context_string}"

            formatted_messages = [{"role": "system", "content": system_msg}]

            for msg in messages:
                if msg.get('role') in ['user', 'assistant']:
                    formatted_messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=formatted_messages,
                max_tokens=1000,
                temperature=0.7
            )

            return jsonify({
                "status": "success",
                "suggestion": response.choices[0].message.content
            })
            
        elif hf_token:
            # Fallback to HuggingFace
            headers = {"Authorization": f"Bearer {hf_token}"}
            last_msg = messages[-1]['content'] if messages else "Help me with my resume."
            prompt = f"<s>[INST] You are a career coach. Context: {context}. Target Role: {target_role}. Question: {last_msg} [/INST]"
            payload = {"inputs": prompt, "parameters": {"max_new_tokens": 250, "temperature": 0.7}}
            hf_res = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
            if hf_res.status_code == 200:
                result = hf_res.json()
                suggestion = result[0].get('generated_text', '').split('[/INST]')[-1].strip()
            else:
                raise Exception("HF API failed")
                
            return jsonify({
                "status": "success",
                "suggestion": suggestion
            })

    except Exception as e:
        current_app.logger.error(f"OpenAI API Error: {e}")
        return jsonify({
            "status": "success",
            "suggestion": smart_fallback('custom', context, last_message)
        })

# =======================
# FEEDBACK ROUTE
# =======================
def get_feedback_db():
    db_path = os.path.join(current_app.root_path, 'data', 'feedback.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # create table if not exists
    conn.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating INTEGER,
            category TEXT,
            message TEXT,
            email TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

@bp.route('/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json() or {}
    rating = data.get('rating')
    category = data.get('category')
    message = data.get('message')
    email = data.get('email', '')
    
    if not rating or not category or not message:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
    try:
        conn = get_feedback_db()
        cursor = conn.cursor()
        created_at = datetime.now()
        cursor.execute(
            'INSERT INTO feedback (rating, category, message, email, created_at) VALUES (?, ?, ?, ?, ?)',
            (rating, category, message, email, created_at)
        )
        conn.commit()
        conn.close()
        
        # --- Email Notification Logic ---
        try:
            admin_email = current_app.config.get('MAIL_USERNAME')
            if admin_email:
                # 1. Admin Notification
                admin_msg = Message(
                    subject="New Feedback Received – Talentryx",
                    recipients=[admin_email]
                )
                
                try:
                    rating_val = int(rating)
                    stars = '★' * rating_val + '☆' * (5 - rating_val)
                except:
                    stars = str(rating)
                
                # HTML template for admin email
                admin_html = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
                    <h2 style="color: #4A90E2; text-align: center;">Talentryx Feedback</h2>
                    <hr style="border: 0; border-top: 1px solid #eee;">
                    <p><strong>Rating:</strong> <span style="color: #ff9800; font-size: 18px;">{stars}</span> ({rating}/5)</p>
                    <p><strong>Category:</strong> {category}</p>
                    <p><strong>Message:</strong></p>
                    <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #4A90E2; font-style: italic;">
                        {message}
                    </div>
                    <p><strong>User Email:</strong> {email if email else 'Not provided'}</p>
                    <p><strong>Timestamp:</strong> {created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <hr style="border: 0; border-top: 1px solid #eee;">
                    <p style="font-size: 12px; color: #888; text-align: center;">This is an automated message from Talentryx AI Resume Builder.</p>
                </div>
                """
                admin_msg.html = admin_html
                mail.send(admin_msg)
                
                # 2. User Confirmation Email (Optional)
                if email:
                    user_msg = Message(
                        subject="Thank You for Your Feedback – Talentryx",
                        recipients=[email]
                    )
                    user_msg.body = f"Hi there,\n\nThank you for submitting your feedback ({category}) to Talentryx. We value your input and will use it to improve our service!\n\nBest Regards,\nThe Talentryx Team"
                    mail.send(user_msg)
                    
        except Exception as email_err:
            current_app.logger.error(f"Email Sending Error: {email_err}")
            # Do NOT break the API if email fails
        
        return jsonify({
            "status": "success",
            "message": "Feedback submitted successfully"
        })
    except Exception as e:
        current_app.logger.error(f"Feedback DB Error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

@bp.route('/feedback/list', methods=['GET'])
def list_feedback():
    try:
        conn = get_feedback_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC")
        rows = cursor.fetchall()
        feedback_list = [dict(row) for row in rows]
        conn.close()
        return jsonify({"status": "success", "data": feedback_list})
    except Exception as e:
        current_app.logger.error(f"Feedback List Error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

@bp.route('/feedback/stats', methods=['GET'])
def stats_feedback():
    try:
        conn = get_feedback_db()
        cursor = conn.cursor()
        
        # Average rating
        cursor.execute("SELECT AVG(rating) as avg_rating, COUNT(id) as total_count FROM feedback")
        row = cursor.fetchone()
        avg_rating = row['avg_rating'] or 0
        total_count = row['total_count'] or 0
        
        # Category breakdown
        cursor.execute("SELECT category, COUNT(id) as count FROM feedback GROUP BY category")
        cat_rows = cursor.fetchall()
        categories = {cat['category']: cat['count'] for cat in cat_rows}
        
        conn.close()
        
        return jsonify({
            "status": "success",
            "data": {
                "average_rating": round(avg_rating, 1),
                "total_count": total_count,
                "categories": categories
            }
        })
    except Exception as e:
        current_app.logger.error(f"Feedback Stats Error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500
