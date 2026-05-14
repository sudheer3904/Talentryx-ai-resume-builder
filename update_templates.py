import os
import glob

# Paths
template_dir = r"c:\Resume_Builder 5\app\templates\resume_templates"
files = glob.glob(os.path.join(template_dir, "*.html"))

target_qr_block = """        {% if qr_codes and (qr_codes.linkedin or qr_codes.github) %}
        <div class="qr-top-right">
            {% if qr_codes.linkedin %}
            <div class="qr-item">
                <img src="data:image/png;base64,{{ qr_codes.linkedin }}" alt="LinkedIn">
                <div class="qr-label">LinkedIn</div>
            </div>
            {% endif %}
            {% if qr_codes.github %}
            <div class="qr-item">
                <img src="data:image/png;base64,{{ qr_codes.github }}" alt="GitHub">
                <div class="qr-label">GitHub</div>
            </div>
            {% endif %}
        </div>
        {% endif %}"""

replacement_qr_block = """        {% if qr_codes and (qr_codes.linkedin or qr_codes.github or qr_codes.portfolio) %}
        <div class="qr-top-right">
            {% if qr_codes.linkedin %}
            <div class="qr-item">
                <img src="data:image/png;base64,{{ qr_codes.linkedin }}" alt="LinkedIn">
                <div class="qr-label">LinkedIn</div>
            </div>
            {% endif %}
            {% if qr_codes.github %}
            <div class="qr-item">
                <img src="data:image/png;base64,{{ qr_codes.github }}" alt="GitHub">
                <div class="qr-label">GitHub</div>
            </div>
            {% endif %}
            {% if qr_codes.portfolio %}
            <div class="qr-item">
                <img src="data:image/png;base64,{{ qr_codes.portfolio }}" alt="Portfolio">
                <div class="qr-label">Portfolio</div>
            </div>
            {% endif %}
        </div>
        {% endif %}"""

target_contact_block = """            <br>
            {% if sections.personal.linkedin %}{{ sections.personal.linkedin | replace('https://', '') | replace('www.',
            '') }}{% endif %}
            {% if sections.personal.github %}{% if sections.personal.linkedin %} | {% endif %}{{
            sections.personal.github | replace('https://', '') | replace('www.', '') }}{% endif %}
        </div>"""

replacement_contact_block = """            <br>
            {% if sections.personal.linkedin %}{{ sections.personal.linkedin | replace('https://', '') | replace('www.', '') }}{% endif %}
            {% if sections.personal.github %}{% if sections.personal.linkedin %} | {% endif %}{{ sections.personal.github | replace('https://', '') | replace('www.', '') }}{% endif %}
            {% if sections.personal.portfolio %}{% if sections.personal.linkedin or sections.personal.github %} | {% endif %}{{ sections.personal.portfolio | replace('https://', '') | replace('www.', '') }}{% endif %}
        </div>"""

count = 0
for fpath in files:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = content
    if target_qr_block in new_content:
        new_content = new_content.replace(target_qr_block, replacement_qr_block)
    
    if target_contact_block in new_content:
        new_content = new_content.replace(target_contact_block, replacement_contact_block)
        
    if new_content != content:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)
        count += 1
        
print(f"Updated {count} template files.")
