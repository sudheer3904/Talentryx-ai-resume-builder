import os
from PIL import Image, ImageDraw

def create_dirs():
    os.makedirs('app/templates/resume_templates', exist_ok=True)
    os.makedirs('app/static/template_previews', exist_ok=True)

CATEGORIES = {
    'Professional': ['classic_professional', 'corporate_executive', 'business_standard', 'formal_ats', 'corporate_blue', 'professional_modern', 'professional_sidebar', 'professional_compact'],
    'Minimal': ['minimal_clean', 'minimal_elegant', 'minimal_ats', 'minimal_serif', 'minimal_grid', 'minimal_academic'],
    'Modern': ['modern_tech', 'modern_gradient', 'modern_split_layout', 'modern_sidebar', 'modern_blocks', 'modern_cards'],
    'Creative': ['creative_designer', 'creative_portfolio', 'creative_bold', 'creative_grid', 'creative_magazine'],
    'Technical': ['software_developer', 'engineering_resume', 'devops_professional', 'data_scientist', 'ai_engineer'],
    'Student': ['student_basic', 'graduate_entry', 'internship_resume', 'campus_placement'],
    'Executive': ['executive_leadership', 'management_resume', 'consulting_resume'],
    'Portfolio': ['designer_portfolio', 'creative_portfolio_v2'],
    'Compact': ['one_page_compact', 'dense_tech_resume'],
    'Generic': ['modern_elegant', 'classic_minimal', 'tech_startup', 'financial_analyst', 'marketing_pro', 'sales_executive', 'healthcare_professional', 'teacher_resume', 'legal_resume']
}

def generate_image(name, cat_name):
    img = Image.new('RGB', (300, 400), color=(245, 245, 250))
    d = ImageDraw.Draw(img)
    # Draw simple lines to look like a resume layout
    d.rectangle([(20, 20), (280, 50)], fill=(70, 70, 100))
    for i in range(5):
        d.rectangle([(20, 70 + i*40), (280, 70 + i*40 + 15)], fill=(180, 180, 190))
    img.save(f'app/static/template_previews/{name}.png')

def generate_html(name, cat_name):
    # Depending on category we can set some specific template code.
    # The simplest is just copying pdf_template and modifying layout/theme implicitly!
    # Wait, instead of copying 50 times, we can include the `resume/pdf_template.html` 
    # but wait, Jinja2 doesn't have a way to include something and change its root variables 
    # unless we pass it to `render_template` or `include` with context.
    
    # We will literally copy `app/templates/resume/pdf_template.html` 
    # and replace `layout-{{ design.layout|default('one_column') }}` with specific layouts
    # and add a custom chunk of CSS.
    
    with open('app/templates/resume/pdf_template.html', 'r', encoding='utf-8') as f:
        content = f.read()

    layout = 'one_column'
    theme = 'corporate'
    
    if 'sidebar' in name or 'split' in name or name in ['devops_professional', 'data_scientist']:
        layout = 'two_column'
    elif 'compact' in name or 'ats' in name or 'dense' in name:
        layout = 'compact'
    elif 'creative' in name or 'modern' in name or 'designer' in name:
        layout = 'modern_flow'
        theme = 'creative'
    elif 'minimal' in name or 'basic' in name:
        layout = 'minimal_layout'
        theme = 'minimal'
    elif 'academic' in name:
        theme = 'academic'
        
    # Replace the class
    content = content.replace(
        '''layout-{{ design.layout|default('one_column') }} theme-{{ theme|default('corporate') }}''',
        f'''layout-{layout} theme-{theme} template-{name}'''
    )

    # Let's insert a small bit of custom CSS per template
    # Instead of replacing, we can do it after <style>
    custom_css = f"""
        /* Custom CSS for {name} */
        body.template-{name} {{
            /* Specific overrides can go here */
        }}
    """
    content = content.replace('</style>', custom_css + '</style>')

    with open(f'app/templates/resume_templates/{name}.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    create_dirs()
    total = 0
    for cat, templates in CATEGORIES.items():
        for t in templates:
            generate_image(t, cat)
            generate_html(t, cat)
            total += 1
    print(f"Generated {{total}} files")
