"""
Resume upload parsing: extract text from PDF/DOCX and structure into sections.
UTF-8 safe for multi-language; uses pdfminer.six and python-docx.
"""
import re
import os


class ParserService:
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract raw text from PDF (UTF-8 safe via pdfminer)."""
        try:
            from pdfminer.high_level import extract_text
            with open(file_path, 'rb') as f:
                return extract_text(f)
        except Exception as e:
            print(f"ParserService: Error reading PDF: {e}")
            return ""

    @staticmethod
    def extract_text_from_docx(file_path):
        """Extract text from DOCX paragraphs (UTF-8 safe)."""
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            print(f"ParserService: Error reading DOCX: {e}")
            return ""

    @staticmethod
    def parse_resume(file_path, file_ext):
        """
        Parse PDF or DOCX resume and return structured dict for editor.
        Sections: personal, education, experience, projects, skills, certifications.
        """
        text = ""
        if file_ext.lower() == '.pdf':
            text = ParserService.extract_text_from_pdf(file_path)
        elif file_ext.lower() in ('.docx', '.doc'):
            text = ParserService.extract_text_from_docx(file_path)
        if not text or not text.strip():
            return None
        return ParserService.structure_resume_text(text)

    @staticmethod
    def structure_resume_text(text):
        """
        Heuristic section detection (keyword-based). UTF-8 safe.
        Returns dict: personal, education, experience, projects, skills, certifications.
        """
        data = {
            'personal': {},
            'education': [],
            'experience': [],
            'projects': [],
            'skills': {'skills_tech': '', 'skills_soft': '', 'skills_languages': ''},
            'certifications': [],
        }
        # Personal: email, phone, name
        email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email:
            data['personal']['email'] = email.group(0)
        phone = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phone:
            data['personal']['phone'] = phone.group(0)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            data['personal']['full_name'] = lines[0]

        # Section headers (case-insensitive; support multiple languages via common keywords)
        text_lower = text.lower()
        section_keywords = {
            'education': ['education', 'academic', 'qualification', 'formation', 'bildung', 'educación'],
            'experience': ['experience', 'work', 'employment', 'career', 'erfahrung', 'expérience'],
            'projects': ['projects', 'project', 'projets', 'projekte'],
            'skills': ['skills', 'competencies', 'technical', 'compétences', 'fähigkeiten', '技能'],
            'certifications': ['certification', 'certificates', 'licenses', 'certificaciones'],
        }
        section_positions = {}
        for section, keywords in section_keywords.items():
            pos = -1
            for kw in keywords:
                idx = text_lower.find(kw)
                if idx != -1 and (pos == -1 or idx < pos):
                    pos = idx
            if pos != -1:
                section_positions[section] = pos

        sorted_sections = sorted(section_positions.keys(), key=lambda x: section_positions[x])

        for i, section in enumerate(sorted_sections):
            start = section_positions[section]
            end = section_positions[sorted_sections[i + 1]] if i + 1 < len(sorted_sections) else len(text)
            content = text[start:end]
            content_lines = content.split('\n')[1:]
            content_clean = "\n".join(content_lines).strip()

            if section == 'education' and content_clean:
                data['education'].append({
                    'institution': content_clean[:150],
                    'degree': 'Extracted Degree',
                    'year': '20xx',
                    'score': '',
                })
            elif section == 'experience' and content_clean:
                data['experience'].append({
                    'company': 'Extracted Company',
                    'role': 'Extracted Role',
                    'start': 'Jan 20xx',
                    'end': 'Present',
                    'description': content_clean[:500],
                })
            elif section == 'projects' and content_clean:
                data['projects'].append({
                    'title': 'Extracted Project',
                    'tech': '',
                    'description': content_clean[:300],
                })
            elif section == 'skills' and content_clean:
                data['skills']['skills_tech'] = content_clean.replace('\n', ', ')[:500]
            elif section == 'certifications' and content_clean:
                data['certifications'].append({
                    'name': content_clean[:200],
                    'issuer': '',
                    'date': '',
                    'link': '',
                })

        return data
