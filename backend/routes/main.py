import json
import requests
import google.generativeai as genai
import os
from typing import Dict, Any
from flask import Flask, render_template, request, jsonify





APP_ID = "c3363934-c2c7-4121-94d4-cdab7be4eaa6"
API_KEY = "ww-53Zo0IeITERKRqBJTUWsUMy6lFWYM570bRfgiHNimT1ADGknuw5HJX"




def fetch_profile_data(profile_url: str) -> Dict[str, Any]:
    """Fetch profile data from LinkedIn API."""
    try:
        response = requests.post(
            f"https://app.wordware.ai/api/released-app/{APP_ID}/run",
            json={"inputs": {"profile_url": profile_url}, "version": "^1.0"},
            headers={"Authorization": f"Bearer {API_KEY}"},
            stream=True
        )
        
        if response.status_code != 200:
            return {"error": f"Request failed with status code {response.status_code}"}

        profile_data = None
        for line in response.iter_lines():
            if line:
                try:
                    content = json.loads(line.decode("utf-8"))
                    value = content.get("value", {})
                    
                    if value.get("type") == "outputs":
                        all_values = value.get('values', {})
                        
                        for subflow_key, subflow_data in all_values.items():
                            for output_key, output_value in subflow_data.items():
                                try:
                                    potential_profile = json.loads(output_value.get('output', '{}'))
                                    if isinstance(potential_profile, dict) and 'firstName' in potential_profile:
                                        profile_data = potential_profile
                                        break
                                except (json.JSONDecodeError, AttributeError):
                                    continue
                            
                            if profile_data:
                                break
                except Exception as e:
                    print(f"Error processing response line: {str(e)}")
                    continue

        if not profile_data:
            return {"error": "Could not extract profile data from the response"}

        return profile_data

    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def extract_profile_info(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and structure profile information from raw data."""
    if not profile_data:
        return None
    
    raw_connections = profile_data.get('connections', '0')
    connections_count = int(''.join(filter(str.isdigit, raw_connections))) if raw_connections else 0
    
    profile_info = {
        "name": f"{profile_data.get('firstName', '')} {profile_data.get('lastName', '')}",
        "headline": profile_data.get('headline', 'N/A'),
        "location": profile_data.get('geo', {}).get('full', 'N/A'),
        "profile_picture": profile_data.get('profilePicture', 'N/A'),
        "summary": profile_data.get('summary', 'N/A'),
        "skills": [skill.get('name', 'N/A') for skill in profile_data.get('skills', [])],
        "experience": [],
        "certifications": [],
        "courses": [],
        "followers_count": profile_data.get('followersCount', 0),
        "connections_count": connections_count
    }

    # Extract positions
    positions = profile_data.get('position', [])
    if positions:
        for position in positions:
            start = position.get('start', {})
            end = position.get('end', {})
            
            experience_entry = {
                "title": position.get('title', 'N/A'),
                "company": position.get('companyName', 'N/A'),
                "location": position.get('location', 'N/A'),
                "employment_type": position.get('employmentType', 'N/A'),
                "start_date": f"{start.get('month', 'N/A')}/{start.get('year', 'N/A')}",
                "end_date": f"{end.get('month', 'N/A')}/{end.get('year', 'N/A')}" if end.get('year', 0) != 0 else "Present"
            }
            profile_info["experience"].append(experience_entry)

    # Extract certifications
    for certification in profile_data.get('certifications', []):
        profile_info["certifications"].append({
            "name": certification.get('name', 'N/A'),
            "authority": certification.get('authority', 'N/A'),
            "start_date": f"{certification.get('start', {}).get('month', 'N/A')}/{certification.get('start', {}).get('year', 'N/A')}"
        })

    # Extract courses
    for course in profile_data.get('courses', []):
        profile_info["courses"].append({
            "name": course.get('name', 'N/A')
        })

    return profile_info


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle main page requests."""
    if request.method == 'POST':
        profile_url = request.form.get('profile_url')
        if not profile_url:
            return render_template('index.html', error="Please enter a LinkedIn profile URL.")
        
        profile_data = fetch_profile_data(profile_url)
        if isinstance(profile_data, dict) and "error" in profile_data:
            return render_template('index.html', error=profile_data["error"])
            
        profile_info = extract_profile_info(profile_data)
        return render_template('index.html', profile_info=profile_info, profile_url=profile_url)
    
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)