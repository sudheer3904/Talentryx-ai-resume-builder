import mysql.connector
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from config import Config

def seed_expanded():
    db = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    cursor = db.cursor()
    
    # 1. New Jobs
    jobs = [
        {
            "role_name": "Product Manager",
            "description": "Drive product vision and strategy. Experience with Agile, JIRA, and Roadmapping.",
            "required_skills": json.dumps(["Agile", "JIRA", "Scrum", "Product Strategy", "User Research", "Communication"])
        },
        {
            "role_name": "Mobile Developer",
            "description": "Build mobile applications for iOS and Android.",
            "required_skills": json.dumps(["Swift", "Kotlin", "React Native", "Flutter", "iOS", "Android"])
        },
        {
            "role_name": "Cybersecurity Analyst",
            "description": "Protect systems from cyber threats. Knowledge of Network Security and Encryption.",
            "required_skills": json.dumps(["Network Security", "Ethical Hacking", "Firewalls", "SIEM", "Encryption", "Python"])
        },
        {
            "role_name": "UI/UX Designer",
            "description": "Design user interfaces and experiences. Proficiency in Figma and Adobe XD.",
            "required_skills": json.dumps(["Figma", "Adobe XD", "Wireframing", "Prototyping", "User Research", "CSS"])
        },
        {
            "role_name": "Cloud Architect",
            "description": "Design and manage cloud infrastructure.",
            "required_skills": json.dumps(["AWS", "Azure", "Google Cloud", "Terraform", "Docker", "Kubernetes"])
        },
        {
             "role_name": "Full Stack Developer",
             "description": "Handle both frontend and backend development.",
             "required_skills": json.dumps(["JavaScript", "React", "Node.js", "Python", "SQL", "Git", "HTML", "CSS"])
        },
        {
             "role_name": "Blockchain Developer",
             "description": "Build decentralized applications and smart contracts.",
             "required_skills": json.dumps(["Solidity", "Ethereum", "Smart Contracts", "Cryptography", "Web3.js"])
        },
        {
             "role_name": "Game Developer",
             "description": "Create video games using engines like Unity or Unreal.",
             "required_skills": json.dumps(["C++", "C#", "Unity", "Unreal Engine", "3D Math", "Physics"])
        }
    ]
    
    print("Seeding Expanded Jobs...")
    for job in jobs:
        try:
            # Check if exists first to avoid error spam
            cursor.execute("SELECT id FROM job_roles WHERE role_name = %s", (job['role_name'],))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO job_roles (role_name, description, required_skills) VALUES (%s, %s, %s)",
                    (job['role_name'], job['description'], job['required_skills'])
                )
                print(f"Added: {job['role_name']}")
            else:
                print(f"Skipping (Exists): {job['role_name']}")
        except mysql.connector.Error as err:
            print(f"Error {job['role_name']}: {err}")

    # 2. New Courses
    courses = [
        {"title": "Product Management Fundamentals", "provider": "Udemy", "link": "https://udemy.com", "skills_covered": json.dumps(["Product Strategy", "Agile", "JIRA"])},
        {"title": "iOS & Swift - The Complete iOS App Development Bootcamp", "provider": "Udemy", "link": "https://udemy.com", "skills_covered": json.dumps(["Swift", "iOS"])},
        {"title": "Android App Development with Kotlin", "provider": "Udacity", "link": "https://udacity.com", "skills_covered": json.dumps(["Kotlin", "Android"])},
        {"title": "Cybersecurity Specialization", "provider": "Coursera", "link": "https://coursera.org", "skills_covered": json.dumps(["Network Security", "Encryption", "SIEM"])},
        {"title": "Google UX Design Professional Certificate", "provider": "Coursera", "link": "https://coursera.org", "skills_covered": json.dumps(["User Research", "Wireframing", "Figma"])},
        {"title": "AWS Certified Solutions Architect", "provider": "A Cloud Guru", "link": "https://acloudguru.com", "skills_covered": json.dumps(["AWS", "Cloud Architecture"])},
        {"title": "Ethereum and Solidity: The Complete Developer's Guide", "provider": "Udemy", "link": "https://udemy.com", "skills_covered": json.dumps(["Solidity", "Ethereum", "Smart Contracts"])},
        {"title": "Unreal Engine 5 C++ Developer", "provider": "Udemy", "link": "https://udemy.com", "skills_covered": json.dumps(["C++", "Unreal Engine"])},
        {"title": "The Complete 2024 Web Development Bootcamp", "provider": "Udemy", "link": "https://udemy.com", "skills_covered": json.dumps(["HTML", "CSS", "JavaScript", "React", "Node.js"])}
    ]
    
    print("Seeding Expanded Courses...")
    for c in courses:
        try:
            cursor.execute("SELECT id FROM courses WHERE title = %s", (c['title'],))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO courses (title, provider, link, skills_covered) VALUES (%s, %s, %s, %s)",
                    (c['title'], c['provider'], c['link'], c['skills_covered'])
                )
                print(f"Added Course: {c['title']}")
            else:
                print(f"Skipping Course: {c['title']}")
        except mysql.connector.Error as err:
            print(f"Error Course {c['title']}: {err}")
            
    db.commit()
    db.close()
    print("Expansion Complete.")

if __name__ == "__main__":
    seed_expanded()
