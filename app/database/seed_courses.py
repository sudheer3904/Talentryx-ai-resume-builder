import mysql.connector
import json
import random
from config import Config

def seed_courses():
    db = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    cursor = db.cursor()
    
    print("Clearing existing courses...")
    cursor.execute("DELETE FROM courses")
    
    # 60 tech topics
    tech_topics = {
        "Python": ["Python", "Backend", "Scripting", "Data Science"],
        "Java": ["Java", "Spring Boot", "Enterprise", "Backend"],
        "C++": ["C++", "Systems Programming", "Game Dev"],
        "JavaScript": ["JavaScript", "Frontend", "Web Development"],
        "TypeScript": ["TypeScript", "Frontend", "Web Development"],
        "React": ["React", "JavaScript", "Frontend", "UI"],
        "Angular": ["Angular", "TypeScript", "Frontend"],
        "Vue.js": ["Vue.js", "JavaScript", "Frontend"],
        "Node.js": ["Node.js", "Backend", "JavaScript", "Express"],
        "Django": ["Django", "Python", "Backend", "Web Development"],
        "Flask": ["Flask", "Python", "Backend", "APIs"],
        "Ruby on Rails": ["Ruby", "Rails", "Backend", "Web Development"],
        "PHP": ["PHP", "Backend", "Web Development", "Laravel"],
        "Go": ["Go", "Golang", "Backend", "Microservices"],
        "Rust": ["Rust", "Systems Programming", "WebAssembly"],
        "Swift": ["Swift", "iOS", "Mobile App Development"],
        "Kotlin": ["Kotlin", "Android", "Mobile App Development"],
        "Flutter": ["Flutter", "Dart", "Mobile App Development", "Cross-Platform"],
        "React Native": ["React Native", "Mobile App Development", "JavaScript"],
        "Machine Learning": ["Machine Learning", "AI", "Data Science", "Python"],
        "Deep Learning": ["Deep Learning", "Neural Networks", "AI", "TensorFlow", "PyTorch"],
        "Data Analysis": ["Data Analysis", "Pandas", "Python", "Statistics"],
        "SQL": ["SQL", "Database", "Data Analysis", "PostgreSQL", "MySQL"],
        "NoSQL": ["NoSQL", "MongoDB", "Cassandra", "Database"],
        "Data Engineering": ["Data Engineering", "ETL", "Spark", "Hadoop"],
        "Tableau": ["Tableau", "Data Visualization", "BI"],
        "Power BI": ["Power BI", "Data Visualization", "BI", "Microsoft"],
        "AWS": ["AWS", "Cloud Computing", "DevOps"],
        "Azure": ["Azure", "Cloud Computing", "Microsoft"],
        "GCP": ["GCP", "Google Cloud", "Cloud Computing"],
        "Docker": ["Docker", "Containers", "DevOps"],
        "Kubernetes": ["Kubernetes", "Container Orchestration", "DevOps"],
        "Terraform": ["Terraform", "Infrastructure as Code", "DevOps"],
        "Jenkins": ["Jenkins", "CI/CD", "DevOps", "Automation"],
        "Linux": ["Linux", "Operating Systems", "Bash", "Shell Scripting"],
        "Cybersecurity": ["Cybersecurity", "Network Security", "Information Security"],
        "Ethical Hacking": ["Ethical Hacking", "Penetration Testing", "Security"],
        "Cryptography": ["Cryptography", "Security", "Encryption"],
        "Blockchain": ["Blockchain", "Web3", "Smart Contracts", "Crypto"],
        "Solidity": ["Solidity", "Ethereum", "Smart Contracts", "Blockchain"],
        "UI/UX Design": ["UI Design", "UX Design", "Wireframing", "Figma"],
        "Figma": ["Figma", "UI Design", "Prototyping"],
        "Adobe XD": ["Adobe XD", "UI Design", "Prototyping"],
        "Agile": ["Agile", "Scrum", "Project Management", "Software Development"],
        "Scrum": ["Scrum", "Agile", "Project Management"],
        "Product Management": ["Product Management", "Leadership", "Strategy"],
        "Project Management": ["Project Management", "PMP", "Leadership"],
        "Digital Marketing": ["Digital Marketing", "SEO", "SEM", "Marketing"],
        "SEO": ["SEO", "Search Engine Optimization", "Marketing", "Content"],
        "Content Marketing": ["Content Marketing", "Copywriting", "Marketing"],
        "Social Media Marketing": ["Social Media", "Marketing", "Branding"],
        "Sales": ["Sales", "B2B", "Negotiation", "Business"],
        "Leadership": ["Leadership", "Management", "Soft Skills", "Communication"],
        "Communication": ["Communication", "Soft Skills", "Public Speaking"],
        "Problem Solving": ["Problem Solving", "Critical Thinking", "Soft Skills"],
        "Time Management": ["Time Management", "Productivity", "Soft Skills"],
        "Technical Writing": ["Technical Writing", "Documentation", "Communication"],
        "Git": ["Git", "Version Control", "GitHub", "DevOps"],
        "Software Testing": ["Software Testing", "QA", "Automation Testing", "Selenium"]
    }

    providers_map = {
        "Coursera": "https://coursera.org",
        "Udemy": "https://udemy.com",
        "edX": "https://edx.org",
        "Pluralsight": "https://pluralsight.com",
        "DataCamp": "https://datacamp.com",
        "LinkedIn Learning": "https://linkedin.com/learning",
        "Codecademy": "https://codecademy.com",
        "Udacity": "https://udacity.com",
        "FreeCodeCamp": "https://freecodecamp.org"
    }

    course_formats = [
        "Complete {topic} Bootcamp",
        "Mastering {topic} from Scratch",
        "{topic} for Beginners",
        "Advanced {topic} Patterns",
        "The Ultimate {topic} Guide",
        "{topic} Professional Certification",
        "Learn {topic} in 30 Days",
        "Applied {topic} in the Real World"
    ]

    courses = []
    
    # Generate exactly 300 courses by looping through topics and creating variations
    for _ in range(300):
        topic = random.choice(list(tech_topics.keys()))
        provider = random.choice(list(providers_map.keys()))
        link = providers_map[provider]
        title_format = random.choice(course_formats)
        title = title_format.format(topic=topic)
        skills = tech_topics[topic]
        
        # Add some random additional generic skills occasionally
        if random.random() > 0.7:
            skills = skills + [random.choice(["Career Development", "Tech Skills", "Best Practices"])]
            
        courses.append({
            "title": title,
            "provider": provider,
            "link": link,
            "skills_covered": json.dumps(skills)
        })
        
    # Extra hardcoded specialized ones to ensure variety
    specialized = [
        {"title": "Google Data Analytics Professional Certificate", "provider": "Coursera", "link": "https://coursera.org", "skills_covered": json.dumps(["Data Analytics", "SQL", "R", "Tableau", "Data Science"])},
        {"title": "AWS Certified Solutions Architect - Associate", "provider": "Udemy", "link": "https://udemy.com", "skills_covered": json.dumps(["AWS", "Cloud Computing", "Solutions Architecture"])},
        {"title": "Meta Front-End Developer Professional Certificate", "provider": "Coursera", "link": "https://coursera.org", "skills_covered": json.dumps(["React", "JavaScript", "HTML", "CSS", "Frontend"])},
        {"title": "IBM Data Science Professional Certificate", "provider": "Coursera", "link": "https://coursera.org", "skills_covered": json.dumps(["Python", "SQL", "Machine Learning", "Data Science"])}
    ]
    
    courses.extend(specialized)
    
    print(f"Seeding {len(courses)} Courses...")
    inserted_count = 0
    for c in courses:
        try:
            cursor.execute(
                "INSERT INTO courses (title, provider, link, skills_covered) VALUES (%s, %s, %s, %s)",
                (c['title'], c['provider'], c['link'], c['skills_covered'])
            )
            inserted_count += 1
        except mysql.connector.Error as err:
            print(f"Error seeding '{c['title']}': {err}")
            
    db.commit()
    db.close()
    print(f"{inserted_count} Courses Seeded successfully.")

if __name__ == "__main__":
    seed_courses()
