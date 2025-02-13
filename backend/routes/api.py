from flask import Flask, render_template, request, jsonify
from backend.routes.main import fetch_profile_data,extract_profile_info

import google.generativeai as genai
from typing import Dict, Any
import os 

# Configure Gemini API Key
os.environ['GOOGLE_API_KEY'] = "AIzaSyDLvfinLq1GgVzSsUyBZx9J9pvlLpo8E7c"

def get_gemini_model():
    """Initialize and return the Gemini model."""
    try:
        model = genai.GenerativeModel("gemini-pro")
        return model
    except Exception as e:
        print(f"Error initializing Gemini model: {str(e)}")
        return None
    

def generate_headline(user_headline: str) -> Dict[str, Any]:
    """
    Generate an improved LinkedIn headline using Gemini AI.
    
    Args:
        user_headline (str): Current LinkedIn headline
        
    Returns:
        dict: Response containing either updated headline or error message
    """
    if not user_headline:
        return {"error": "Please provide a current headline"}
    
    prompt = f"""As a professional LinkedIn profile optimizer, improve this headline to make it more engaging, 
    impactful, and aligned with LinkedIn best practices. Current headline: '{user_headline}'
    
    Guidelines:
    - Keep it under 120 characters
    - Include relevant keywords
    - Focus on value proposition
    - Make it clear and professional
    - Avoid buzzwords and clichés
    
    Return only the improved headline without any explanations."""
    
    try:
        model = get_gemini_model()
        if not model:
            return {"error": "Unable to initialize AI model"}
        
        response = model.generate_content(prompt)
        improved_headline = response.text.strip()
        
        return {"updated_headline": improved_headline}
    except Exception as e:
        print(f"Error generating headline: {str(e)}")
        return {"error": "Failed to generate headline. Please try again."}

def generate_summary(experience: str, skills: str) -> Dict[str, Any]:
    """
    Generate a professional LinkedIn summary using Gemini AI.
    
    Args:
        experience (str): Professional experience
        skills (str): Current skills
        
    Returns:
        dict: Response containing either updated summary or error message
    """
    if not experience or not skills:
        return {"error": "Please provide both experience and skills"}
    
    prompt = f"""As a professional LinkedIn profile writer, create a compelling summary based on:
    Experience: {experience}
    Skills: {skills}
    
    Guidelines:
    - Start with a strong hook
    - Highlight key achievements
    - Incorporate relevant skills naturally
    - Show personality while maintaining professionalism
    - Keep it between 200-300 words
    - Use first-person narrative
    - Include a call to action
    
    Return only the professional summary without any explanations."""
    
    try:
        model = get_gemini_model()
        if not model:
            return {"error": "Unable to initialize AI model"}
        
        response = model.generate_content(prompt)
        improved_summary = response.text.strip()
        
        return {"updated_summary": improved_summary}
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return {"error": "Failed to generate summary. Please try again."}

def generate_skills(experience: str, current_skills: str) -> Dict[str, Any]:
    """
    Generate suggested skills based on experience using Gemini AI.
    
    Args:
        experience (str): Professional experience
        current_skills (str): Current skills
        
    Returns:
        dict: Response containing either suggested skills or error message
    """
    if not experience or not current_skills:
        return {"error": "Please provide both experience and current skills"}
    
    prompt = f"""As a professional skills analyst, suggest additional relevant skills based on:
    Experience: {experience}
    Current Skills: {current_skills}
    
    Guidelines:
    - Suggest 5-7 highly relevant skills
    - Include both technical and soft skills
    - Focus on in-demand skills
    - Avoid duplicating current skills
    - Consider industry trends
    - List skills in order of relevance
    
    Return only the list of suggested skills, separated by commas."""
    
    try:
        model = get_gemini_model()
        if not model:
            return {"error": "Unable to initialize AI model"}
        
        response = model.generate_content(prompt)
        suggested_skills = response.text.strip()
        
        return {"suggested_skills": suggested_skills}
    except Exception as e:
        print(f"Error generating skills: {str(e)}")
        return {"error": "Failed to generate skills. Please try again."}

app = Flask(__name__)


@app.route('/generate_headline', methods=['POST'])
def generate_headline_route():
    """Handle headline generation requests."""
    user_headline = request.form.get('user_headline')
    if not user_headline:
        return jsonify({'error': 'Please provide a current headline'})
    
    result = generate_headline(user_headline)
    return jsonify(result)

@app.route('/generate_summary', methods=['POST'])
def generate_summary_route():
    """Handle summary generation requests."""
    experience = request.form.get('experience')
    skills = request.form.get('skills')
    
    if not experience or not skills:
        return jsonify({'error': 'Please provide both experience and skills'})
    
    result = generate_summary(experience, skills)
    return jsonify(result)

@app.route('/generate_skills', methods=['POST'])
def generate_skills_route():
    """Handle skills generation requests."""
    experience = request.form.get('experience')
    current_skills = request.form.get('current_skills')
    
    if not experience or not current_skills:
        return jsonify({'error': 'Please provide both experience and current skills'})
    
    result = generate_skills(experience, current_skills)
    return jsonify(result)


