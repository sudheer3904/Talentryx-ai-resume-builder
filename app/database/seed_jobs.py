import mysql.connector
import json
from config import Config

def seed_jobs():
    db = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    cursor = db.cursor()
    
    # Clear existing jobs to prevent duplicates during re-seeding
    print("Clearing existing job roles...")
    cursor.execute("DELETE FROM job_roles")
    
    jobs = [
        {
            "role_name": "Software Engineer",
            "description": "Develop and maintain software applications. Experience with Python, SQL, and Flask.",
            "required_skills": json.dumps(["Python", "SQL", "Flask", "REST API", "Git"])
        },
        {
            "role_name": "Data Scientist",
            "description": "Analyze large datasets and build predictive models. Proficiency in Python, Pandas, and Scikit-learn.",
            "required_skills": json.dumps(["Python", "Pandas", "NumPy", "Scikit-learn", "Machine Learning"])
        },
        {
            "role_name": "Frontend Developer",
            "description": "Build responsive web interfaces specialized in HTML, CSS, JavaScript, and React.",
            "required_skills": json.dumps(["HTML", "CSS", "JavaScript", "React", "Bootstrap", "Tailwind CSS"])
        },
        {
            "role_name": "DevOps Engineer",
            "description": "Manage infrastructure and deployment pipelines. Experience with Docker, Kubernetes, and AWS.",
            "required_skills": json.dumps(["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Terraform"])
        },
        {
            "role_name": "Full Stack Developer",
            "description": "Work on both frontend and backend components of web applications.",
            "required_skills": json.dumps(["JavaScript", "Node.js", "React", "SQL", "HTML", "CSS"])
        },
        {
            "role_name": "Mobile App Developer",
            "description": "Design and build applications for mobile platforms like iOS and Android.",
            "required_skills": json.dumps(["Flutter", "Dart", "Swift", "Kotlin", "React Native"])
        },
        {
            "role_name": "AI/ML Engineer",
            "description": "Develop advanced AI models and implement machine learning algorithms.",
            "required_skills": json.dumps(["Python", "TensorFlow", "PyTorch", "NLP", "Deep Learning"])
        },
        {
            "role_name": "Cybersecurity Analyst",
            "description": "Protect systems and networks from digital attacks and ensure data security.",
            "required_skills": json.dumps(["Security+", "Ethical Hacking", "Network Security", "Linux"])
        },
        {
            "role_name": "Cloud Architect",
            "description": "Design and manage scalable cloud-based infrastructure and services.",
            "required_skills": json.dumps(["AWS", "Azure", "Cloud Computing", "Infrastructure as Code"])
        },
        {
            "role_name": "Project Manager",
            "description": "Lead projects from inception to completion, ensuring goals and deadlines are met.",
            "required_skills": json.dumps(["Agile", "Scrum", "Risk Management", "Leadership"])
        },
        {
            "role_name": "UI/UX Designer",
            "description": "Create intuitive and visually appealing user interfaces and experiences.",
            "required_skills": json.dumps(["Figma", "Adobe XD", "User Research", "Prototyping"])
        },
        {
            "role_name": "QA Automation Engineer",
            "description": "Develop automated testing scripts to ensure software quality and reliability.",
            "required_skills": json.dumps(["Selenium", "Test Automation", "Java", "Python", "JUnit"])
        },
        {
            "role_name": "Data Engineer",
            "description": "Design and maintain data pipelines and architectures for large-scale data processing.",
            "required_skills": json.dumps(["SQL", "Spark", "Hadoop", "ETL", "Python"])
        },
        {
            "role_name": "Marketing Specialist",
            "description": "Develop and execute marketing campaigns to drive brand awareness and growth.",
            "required_skills": json.dumps(["SEO", "Digital Marketing", "Content Strategy", "Social Media"])
        },
        {
            "role_name": "HR Manager",
            "description": "Oversee recruitment, employee relations, and organizational development.",
            "required_skills": json.dumps(["Recruitment", "Conflict Resolution", "Communication"])
        }
    ]
    
    print(f"Seeding {len(jobs)} Job Roles...")
    for job in jobs:
        try:
            cursor.execute(
                "INSERT INTO job_roles (role_name, description, required_skills) VALUES (%s, %s, %s)",
                (job['role_name'], job['description'], job['required_skills'])
            )
        except mysql.connector.Error as err:
            print(f"Error seeding '{job['role_name']}': {err}")
            
    db.commit()
    db.close()
    print("Jobs Seeded successfully.")

if __name__ == "__main__":
    seed_jobs()
