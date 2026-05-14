import json
import re

def expand_questions():
    with open('C:/Resume_Builder 5/app/data/interview_questions.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    tech_templates = [
        "What are the most critical tools or frameworks you use as a {role}, and why?",
        "How do you stay updated with the latest trends and updates in {role}?",
        "Walk me through your process for troubleshooting a complex issue in your {role} work.",
        "How do you ensure quality and maintainability in your {role} deliverables?",
        "Describe a time when you had to optimize performance or efficiency in a {role} project.",
        "What are the common antipatterns or mistakes you see junior {role}s make?",
        "Explain how you handle dependency management or system integrations in your {role} tasks.",
        "Can you describe how you approach testing and validation within a {role} context?",
        "What metrics or indicators do you use to measure the success of a {role} implementation?",
        "How do you handle security or compliance requirements in your {role} projects?",
        "Describe your approach to documenting your {role} work for other team members.",
        "How do you balance technical debt with the need to deliver {role} features quickly?",
        "What is the most challenging technical constraint you've faced as a {role}?",
        "Explain a time when you had to evaluate and choose between two different technologies for a {role} project.",
        "How do you approach refactoring or improving existing systems in your {role} capacity?",
        "What role does automation play in your daily tasks as a {role}?",
        "Describe how you would design a scalable solution for a typical {role} problem.",
        "How do you handle edge cases and unexpected inputs in your {role} work?",
        "What is your strategy for monitoring and logging in production {role} environments?",
        "Explain how you collaborate with cross-functional technical teams to achieve {role} objectives."
    ]

    behav_templates = [
        "Tell me about a time you had a disagreement with a team member regarding a {role} decision. How was it resolved?",
        "Describe a high-pressure situation in your {role} career and how you handled it.",
        "Provide an example of a time when you had to learn a new tool or technology quickly for a {role} project.",
        "Tell me about a {role} project that failed or did not meet expectations. What did you learn?",
        "Describe how you manage your time and prioritize tasks when juggling multiple {role} deadlines.",
        "Give an example of a time you went above and beyond your standard {role} responsibilities.",
        "Tell me about a time you received constructive criticism on your {role} work and how you responded.",
        "Describe your experience mentoring or onboarding junior team members in a {role} capacity.",
        "Tell me about a time you had to adapt your {role} approach due to changing project requirements.",
        "Describe a situation where you had to communicate complex {role} concepts to a non-technical audience."
    ]

    for key, content in data.items():
        role_name = key.replace('_', ' ').title()
        
        tech = content.get('technical', [])
        behav = content.get('behavioral', [])
        
        # Add tech questions
        idx = 0
        while len(tech) < 20:
            template = tech_templates[idx % len(tech_templates)]
            q = template.format(role=role_name)
            if q not in tech:
                tech.append(q)
            idx += 1
            
        # Ensure it's exactly 20
        content['technical'] = tech[:20]
        
        # Add behavioral questions
        idx = 0
        while len(behav) < 10:
            template = behav_templates[idx % len(behav_templates)]
            q = template.format(role=role_name)
            if q not in behav:
                behav.append(q)
            idx += 1
            
        # Ensure it's exactly 10
        content['behavioral'] = behav[:10]

    with open('C:/Resume_Builder 5/app/data/interview_questions.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')

if __name__ == '__main__':
    expand_questions()
