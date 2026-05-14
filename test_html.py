from app import create_app
from app.services.pdf_service import generate_pdf, render_template

def generate_html(resume_data, sections, theme='corporate', translations=None, format_type=None):
    design_dict = resume_data.get('design', {})
    import typing
    design_dict = typing.cast(typing.Dict[str, typing.Any], design_dict)
    if format_type:
        fmt = format_type.lower()
        if fmt in {'corporate':1}:
            pass
    layout_color = design_dict.get('color') or '#2c3e50'
    main_color = layout_color
    font_family = design_dict.get('font') or "'Helvetica', 'Arial', sans-serif"
    line_height = design_dict.get('spacing') or 1.4
    font_size = design_dict.get('fontSize') or 10.5
    custom_css = f"""
    <style>
    body {{
        font-family: {font_family} !important;
        line-height: {line_height} !important;
        font-size: {font_size}pt !important;
    }}
    h1, h2, h3, .section-title {{
        color: {main_color} !important;
    }}
    h2.section-title {{
        border-bottom: 2.5px solid {main_color} !important;
    }}
    .layout-modern_flow .header-container,
    .theme-creative .header-container {{
        background-color: {layout_color} !important;
    }}
    .layout-modern_flow h2.section-title::after,
    .theme-creative h2.section-title::after {{
        background: {layout_color} !important;
    }}
    </style>
    """
    html_content = render_template(
        'resume/pdf_template.html',
        resume=resume_data,
        sections=sections,
        theme=theme,
        qr_codes={},
        photo_path=None,
        design=design_dict,
        custom_css=custom_css,
        t=translations or {},
    )
    return html_content

app = create_app()
with app.app_context():
    html = generate_html({'design': {'color': '#ff0000', 'layout': 'modern_flow'}}, {'personal': {'full_name': 'Test User'}})
    with open('c:/Resume_Builder4/test.html', 'w', encoding='utf-8') as f:
        f.write(html)
