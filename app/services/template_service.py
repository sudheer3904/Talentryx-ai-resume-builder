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

def get_template_name(template_id: str) -> str:
    words = template_id.split('_')
    return ' '.join(word.capitalize() for word in words)

def get_template_layout_and_theme(name: str):
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
        
    return layout, theme
