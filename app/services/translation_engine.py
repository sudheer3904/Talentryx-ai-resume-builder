import re
import asyncio
from deep_translator import GoogleTranslator  # type: ignore
from concurrent.futures import ThreadPoolExecutor
from typing import Any

class TranslationEngine:
    def __init__(self):
        # In-memory cache: { "lang:text": "translation" }
        self._cache = {}
        # Max workers for async api calls
        self._executor = ThreadPoolExecutor(max_workers=5)

    def _get_lang_code(self, lang_name):
        mapping = {
            'english': 'en',
            'hindi': 'hi',
            'tamil': 'ta',
            'spanish': 'es',
            'french': 'fr',
            'german': 'de',
            'mandarin': 'zh-CN'
        }
        return mapping.get(lang_name.lower(), 'en')

    def translateText(self, text, targetLang):
        if not text or not text.strip():
            return text
            
        lang_code = self._get_lang_code(targetLang)

        cache_key = f"{lang_code}:{text}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            translator = GoogleTranslator(source='auto', target=lang_code)
            translated = translator.translate(text)
            self._cache[cache_key] = translated
            return translated
        except Exception as e:
            print(f"Translation error: {e}")
            return text

    def translateBatch(self, textArray: list[str], targetLang: str) -> list[str]:
        if not textArray:
            return []
            
        lang_code = self._get_lang_code(targetLang)
            
        separator = '\n\n|||\n\n'
        chunks = []
        current_chunk = []
        current_length = 0
        
        for text in textArray:
            text_str = str(text) if text else ""
            if current_chunk and current_length + len(text_str) + len(separator) > 4000:
                chunks.append(current_chunk)
                current_chunk = [text_str]
                current_length = len(text_str)
            else:
                current_chunk.append(text_str)
                current_length += len(text_str) + len(separator)
                
        if current_chunk:
            chunks.append(current_chunk)
            
        translated_results = []
        for chunk in chunks:
            combined_text = separator.join(chunk)
            try:
                translated_combined = self.translateText(combined_text, targetLang)
                split_translated = re.split(r'\s*\|\|\|\s*', translated_combined)
                
                if len(split_translated) == len(chunk):
                    translated_results.extend([t.strip() for t in split_translated])
                else:
                    for original_text in chunk:
                        translated_results.append(self.translateText(original_text, targetLang))
            except Exception as e:
                print(f"Batch translation error: {e}")
                for original_text in chunk:
                    translated_results.append(self.translateText(original_text, targetLang))
                    
        return translated_results

    def _mask_text(self, text, protected_words):
        if not text or not protected_words:
            return text, {}
        
        mask_map = {}
        masked_text = text
        
        # Sort by length descending to mask longer phrases first
        sorted_words = sorted(protected_words, key=len, reverse=True)
        
        for i, word in enumerate(sorted_words):
            if not word.strip(): continue
            # Use regex for word boundaries
            pattern = re.compile(r'\b{}\b'.format(re.escape(word)), re.IGNORECASE)
            
            # Check if this word is in the text
            if pattern.search(masked_text):
                placeholder = f"SKILL_{i}"
                mask_map[placeholder] = word
                masked_text = pattern.sub(placeholder, masked_text)
                
        return masked_text, mask_map

    def _unmask_text(self, translated_text, mask_map):
        if not translated_text or not mask_map:
            return translated_text
            
        unmasked = translated_text
        for placeholder, original_word in mask_map.items():
            # Sometimes translation API might change "**SKILL_1**" to "** SKILL_1 **" etc
            # We'll just replace the placeholder string
            pattern = re.compile(re.escape(placeholder), re.IGNORECASE)
            unmasked = pattern.sub(original_word, unmasked)
            
        return unmasked

    def _extract_protected_words(self, resumeData):
        protected = set()
        
        skills = resumeData.get('skills', {})
        for key in ['skills_tech', 'skills_soft']:
            val = skills.get(key, '')
            if val:
                # Split by commas or newlines
                words = [w.strip() for w in re.split(r'[,;\n]', val) if w.strip()]
                protected.update(words)
                
        # Protect names and emails etc (from personal)
        personal = resumeData.get('personal', {})
        if personal.get('full_name'):
            for name_part in personal.get('full_name').split():
                protected.add(name_part)
        
        if personal.get('email'):
            protected.add(personal.get('email'))
            
        if personal.get('company_name'):
             protected.add(personal.get('company_name')) # Example

        return list(protected)

    def translateResume(self, resumeData, targetLang):
        # Create a deep copy to reconstruct
        import copy
        translated_resume = copy.deepcopy(resumeData)
        protected_words = self._extract_protected_words(resumeData)
        
        # We will collect all texts to translate first, map them to paths
        # Paths: [ ('personal', 'summary'), ('experience', 0, 'description'), ... ]
        paths: list[Any] = []
        texts: list[str] = []
        
        # Summary & Role & Location
        if translated_resume.get('personal', {}).get('summary'):
            paths.append(('personal', 'summary'))
            texts.append(translated_resume['personal']['summary'])
            
        if translated_resume.get('personal', {}).get('role'):
            paths.append(('personal', 'role'))
            texts.append(translated_resume['personal']['role'])

        if translated_resume.get('personal', {}).get('location'):
            paths.append(('personal', 'location'))
            texts.append(translated_resume['personal']['location'])
            
        # Experience (company, role, descriptions)
        for i, exp in enumerate(translated_resume.get('experience', [])):
            if exp.get('company'):
                paths.append(('experience', i, 'company'))
                texts.append(exp['company'])
            if exp.get('role'):
                paths.append(('experience', i, 'role'))
                texts.append(exp['role'])
            if exp.get('description'):
                paths.append(('experience', i, 'description'))
                texts.append(exp['description'])

        # Education (institution, degree)
        for i, edu in enumerate(translated_resume.get('education', [])):
            if edu.get('institution'):
                paths.append(('education', i, 'institution'))
                texts.append(edu['institution'])
            if edu.get('degree'):
                paths.append(('education', i, 'degree'))
                texts.append(edu['degree'])
                
        # Projects (title, descriptions)
        for i, proj in enumerate(translated_resume.get('projects', [])):
            if proj.get('title'):
                paths.append(('projects', i, 'title'))
                texts.append(proj['title'])
            if proj.get('description'):
                paths.append(('projects', i, 'description'))
                texts.append(proj['description'])

        # Certifications (name, issuer)
        for i, cert in enumerate(translated_resume.get('certifications', [])):
            if cert.get('name'):
                paths.append(('certifications', i, 'name'))
                texts.append(cert['name'])
            if cert.get('issuer'):
                paths.append(('certifications', i, 'issuer'))
                texts.append(cert['issuer'])
                
        # Skills
        for skill_key in ['skills_tech', 'skills_soft', 'skills_languages']:
            if translated_resume.get('skills', {}).get(skill_key):
                paths.append(('skills', skill_key))
                texts.append(translated_resume['skills'][skill_key])

        # Hobbies
        if translated_resume.get('hobbies', {}).get('hobbies'):
            paths.append(('hobbies', 'hobbies'))
            texts.append(translated_resume['hobbies']['hobbies'])
            
        # Pre-process masking
        masked_texts = []
        mask_maps = []
        for text in texts:
            masked, m_map = self._mask_text(text, protected_words)
            masked_texts.append(masked)
            mask_maps.append(m_map)
            
        # Batch Translate
        translated_masked_texts = self.translateBatch(masked_texts, targetLang)
        
        # Unmask and Reconstruct
        for idx, path in enumerate(paths):
            unmasked = self._unmask_text(translated_masked_texts[idx], mask_maps[idx])
            
            # Apply back to the tree
            if path[0] == 'personal':
                translated_resume['personal'][path[1]] = unmasked
            elif path[0] == 'experience':
                translated_resume['experience'][path[1]][path[2]] = unmasked
            elif path[0] == 'education':
                translated_resume['education'][path[1]][path[2]] = unmasked
            elif path[0] == 'projects':
                translated_resume['projects'][path[1]][path[2]] = unmasked
            elif path[0] == 'certifications':
                translated_resume['certifications'][path[1]][path[2]] = unmasked
            elif path[0] == 'skills':
                translated_resume['skills'][path[1]] = unmasked
            elif path[0] == 'hobbies':
                translated_resume['hobbies'][path[1]] = unmasked
                
        # Record language
        translated_resume['language'] = targetLang
        return translated_resume

translation_engine = TranslationEngine()
