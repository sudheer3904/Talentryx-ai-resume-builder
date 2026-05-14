import mysql.connector
import json
import random
from config import Config

def seed_smart_jobs():
    db = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    cursor = db.cursor()
    
    # Drop if exists and create tables
    print("Dropping and re-creating jobs and job_sources tables...")
    cursor.execute("DROP TABLE IF EXISTS job_sources")
    cursor.execute("DROP TABLE IF EXISTS jobs")
    
    cursor.execute("""
    CREATE TABLE jobs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        job_title VARCHAR(150),
        category VARCHAR(100),
        required_skills JSON,
        optional_skills JSON,
        demand_level ENUM('High', 'Medium', 'Low')
    )
    """)
    
    cursor.execute("""
    CREATE TABLE job_sources (
        id INT AUTO_INCREMENT PRIMARY KEY,
        job_id INT,
        platform_name VARCHAR(100),
        job_link VARCHAR(255),
        company_name VARCHAR(150),
        location VARCHAR(100),
        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
    )
    """)
    
    # Data pools for generating 150 jobs
    categories = {
        "Software Development": {
            "titles": ["Backend Developer", "Frontend Developer", "Full Stack Developer", "Mobile App Developer", "Java Developer", "Software Engineer", "C++ Developer", "Python Developer", "React Developer", "Node.js Developer"],
            "req_skills": ["Python", "Java", "JavaScript", "C++", "C#", "SQL", "React", "Node.js", "Django", "Flask", "Spring Boot", "Git", "REST APIs"],
            "opt_skills": ["Docker", "Kubernetes", "AWS", "GraphQL", "TypeScript", "Redis", "MongoDB", "Linux"]
        },
        "Data Science / AI": {
            "titles": ["Data Scientist", "Machine Learning Engineer", "Data Analyst", "AI Researcher", "Data Engineer", "Deep Learning Engineer", "Computer Vision Specialist", "NLP Engineer"],
            "req_skills": ["Python", "R", "SQL", "Machine Learning", "Deep Learning", "Pandas", "NumPy", "TensorFlow", "PyTorch", "Tableau", "PowerBI", "Statistics"],
            "opt_skills": ["Hadoop", "Spark", "AWS", "Azure ML", "C++", "Java", "Scikit-Learn", "Data Visualization"]
        },
        "Web Development": {
            "titles": ["Web Developer", "UI Developer", "Web Designer", "PHP Developer", "Ruby on Rails Developer", "Frontend Engineer", "CMS Specialist"],
            "req_skills": ["HTML", "CSS", "JavaScript", "React", "Vue.js", "Angular", "PHP", "Ruby", "TypeScript", "Bootstrap", "Tailwind CSS"],
            "opt_skills": ["Node.js", "WordPress", "Figma", "SASS", "Webpack", "Jest", "SEO"]
        },
        "Cybersecurity": {
            "titles": ["Cybersecurity Analyst", "Penetration Tester", "Information Security Manager", "Security Engineer", "Ethical Hacker", "SOC Analyst"],
            "req_skills": ["Network Security", "Linux", "Python", "Ethical Hacking", "Cryptography", "Risk Assessment", "Firewalls", "Security+", "Wireshark"],
            "opt_skills": ["CISSP", "CEH", "Bash", "C++", "Cloud Security", "SIEM", "Reverse Engineering"]
        },
        "Cloud / DevOps": {
            "titles": ["Cloud Architect", "DevOps Engineer", "Site Reliability Engineer", "AWS Specialist", "Azure Developer", "Cloud Security Engineer"],
            "req_skills": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Linux", "CI/CD", "Terraform", "Jenkins", "Python", "Bash"],
            "opt_skills": ["Ansible", "Prometheus", "Grafana", "GitOps", "Golang", "Networking", "Agile"]
        },
        "UI/UX Design": {
            "titles": ["UX Researcher", "UI Designer", "Product Designer", "Interaction Designer", "Visual Designer", "UX/UI Lead"],
            "req_skills": ["Figma", "Adobe XD", "User Research", "Wireframing", "Prototyping", "Sketch", "Interaction Design", "Usability Testing"],
            "opt_skills": ["HTML", "CSS", "Adobe Illustrator", "Photoshop", "Agile", "InVision", "Motion Design"]
        },
        "Business / Management": {
            "titles": ["Product Manager", "Project Manager", "Business Analyst", "Scrum Master", "Operations Manager", "Strategy Consultant", "Technical Program Manager"],
            "req_skills": ["Agile", "Scrum", "Project Management", "Leadership", "Communication", "Jira", "Risk Management", "Stakeholder Management", "Data Analysis"],
            "opt_skills": ["SQL", "Tableau", "Confluence", "Python", "Six Sigma", "PMP", "Budgeting"]
        }
    }
    
    platforms = ["LinkedIn", "Naukri", "Glassdoor", "Indeed", "Internshala", "Freshersworld"]
    company_prefixes = ["Tech", "Global", "Nova", "Apex", "Nexus", "Quantum", "Cyber", "Data", "Cloud", "Future"]
    company_suffixes = ["Solutions", "Corp", "Inc", "Technologies", "Systems", "Innovations", "Labs", "Studios", "AI", "Networks"]
    locations = ["Remote", "New York, NY", "San Francisco, CA", "London, UK", "Berlin, Germany", "Bangalore, India", "Toronto, Canada", "Sydney, Australia", "Austin, TX", "Seattle, WA"]
    
    total_jobs = 0
    for i in range(150):
        # Choose random category
        cat_name = random.choice(list(categories.keys()))
        cat_data = categories[cat_name]
        
        job_title = random.choice(cat_data["titles"])
        if random.random() > 0.6:
            level = random.choice(["Senior ", "Junior ", "Lead ", "Principal "])
            job_title = level + job_title
            
        req_skills = random.sample(cat_data["req_skills"], min(len(cat_data["req_skills"]), random.randint(5, 8)))
        opt_skills = random.sample(cat_data["opt_skills"], min(len(cat_data["opt_skills"]), random.randint(2, 4)))
        demand = random.choice(["High", "Medium", "Low"])
        
        # Insert job
        cursor.execute(
            "INSERT INTO jobs (job_title, category, required_skills, optional_skills, demand_level) VALUES (%s, %s, %s, %s, %s)",
            (job_title, cat_name, json.dumps(req_skills), json.dumps(opt_skills), demand)
        )
        job_id = cursor.lastrowid
        total_jobs += 1
        
        # Insert 2-3 links
        num_links = random.randint(2, 3)
        plats_chosen = random.sample(platforms, num_links)
        for platform in plats_chosen:
            company = f"{random.choice(company_prefixes)} {random.choice(company_suffixes)}"
            loc = random.choice(locations)
            # Create a realistic slug
            slug = job_title.lower().replace(" ", "-") + "-" + str(random.randint(1000,9999))
            
            if platform == "LinkedIn":
                link = f"https://www.linkedin.com/jobs/view/{slug}"
            elif platform == "Naukri":
                link = f"https://www.naukri.com/job-listings-{slug}"
            elif platform == "Glassdoor":
                link = f"https://www.glassdoor.com/job-listing/{slug}"
            elif platform == "Indeed":
                link = f"https://www.indeed.com/viewjob?jk={slug}"
            elif platform == "Internshala":
                link = f"https://internshala.com/job/detail/{slug}"
            else:
                link = f"https://www.freshersworld.com/jobs/{slug}"
                
            cursor.execute(
                "INSERT INTO job_sources (job_id, platform_name, job_link, company_name, location) VALUES (%s, %s, %s, %s, %s)",
                (job_id, platform, link, company, loc)
            )
            
    db.commit()
    print(f"Successfully seeded {total_jobs} advanced jobs with multiple platform sources.")
    cursor.close()
    db.close()

if __name__ == "__main__":
    seed_smart_jobs()
