// Editor State
let resumeData = {
    personal: {},
    education: [],
    experience: [],
    skills: {},
    projects: [],
    certifications: [],
    design: {},
    hobbies: {},
    photo_path: null
};

// Debounce Utility
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

const autoSave = debounce(() => {
    saveResume(true); // true = silent mode
}, 2000); // 2 seconds debounce

// Item Templates (using global TRANSLATIONS)
const t = typeof TRANSLATIONS !== 'undefined' ? TRANSLATIONS : {
    labels: {
        institution: 'University/School', degree: 'Degree', year: 'Year', score: 'Score/CGPA',
        company: 'Company Name', role: 'Role/Title', start: 'Start Date', end: 'End Date',
        description: 'Description', project_title: 'Project Title', tech_stack: 'Tech Stack'
    }
};

const templates = {
    education: `
        <div class="item-card mb-3 p-2 border rounded">
            <input type="text" class="form-control mb-1" placeholder="${t.labels.institution}" oninput="updateData('education', index, 'institution', this.value)">
            <input type="text" class="form-control mb-1" placeholder="${t.labels.degree}" oninput="updateData('education', index, 'degree', this.value)">
            <div class="row">
                <div class="col-6"><input type="text" class="form-control mb-1" placeholder="${t.labels.year}" oninput="updateData('education', index, 'year', this.value)"></div>
                <div class="col-6"><input type="text" class="form-control mb-1" placeholder="${t.labels.score}" oninput="updateData('education', index, 'score', this.value)"></div>
            </div>
            <button class="btn btn-sm btn-danger mt-1" onclick="removeItem('education', index)">Remove</button>
        </div>
    `,
    experience: `
         <div class="item-card mb-3 p-2 border rounded">
            <input type="text" class="form-control mb-1" placeholder="${t.labels.company}" oninput="updateData('experience', index, 'company', this.value)">
            <input type="text" class="form-control mb-1" placeholder="${t.labels.role}" oninput="updateData('experience', index, 'role', this.value)">
             <div class="row">
                <div class="col-6"><input type="text" class="form-control mb-1" placeholder="${t.labels.start}" oninput="updateData('experience', index, 'start', this.value)"></div>
                <div class="col-6"><input type="text" class="form-control mb-1" placeholder="${t.labels.end}" oninput="updateData('experience', index, 'end', this.value)"></div>
            </div>
            <!-- Rich Text -->
            <div class="quill-editor frosted-glass bg-white mb-2" style="height: 150px; border-radius: 8px;" id="quill-experience-index"></div>
            <button class="btn btn-sm btn-danger mt-1" onclick="removeItem('experience', index)">Remove</button>
        </div>
    `,
    projects: `
        <div class="item-card mb-3 p-2 border rounded">
            <input type="text" class="form-control mb-1" placeholder="${t.labels.project_title}" oninput="updateData('projects', index, 'title', this.value)">
            <div class="quill-editor frosted-glass bg-white mb-2" style="height: 150px; border-radius: 8px;" id="quill-projects-index"></div>
            <input type="text" class="form-control mb-1" placeholder="${t.labels.tech_stack}" oninput="updateData('projects', index, 'tech', this.value)">
            <button class="btn btn-sm btn-danger mt-1" onclick="removeItem('projects', index)">Remove</button>
        </div>
    `,
    certifications: `
        <div class="item-card mb-3 p-2 border rounded">
            <input type="text" class="form-control mb-1" placeholder="Certification name" oninput="updateData('certifications', index, 'name', this.value)">
            <input type="text" class="form-control mb-1" placeholder="Issuer" oninput="updateData('certifications', index, 'issuer', this.value)">
            <input type="text" class="form-control mb-1" placeholder="Date / Link" oninput="updateData('certifications', index, 'link', this.value)">
            <button class="btn btn-sm btn-danger mt-1" onclick="removeItem('certifications', index)">Remove</button>
        </div>
    `
};

document.addEventListener('DOMContentLoaded', () => {
    // Initialize listeners for static inputs
    document.querySelectorAll('#form-personal input, #form-personal textarea').forEach(input => {
        if (input.type === 'file') return; // Skip file input here
        input.addEventListener('input', (e) => {
            resumeData.personal[e.target.name] = e.target.value;
            renderPreview();
            autoSave();
        });
    });

    setTimeout(() => {
        initSingleQuill('quill-summary', 'personal', 'summary', typeof t !== 'undefined' && t.placeholders ? t.placeholders.summary : 'Professional summary...');
        initSingleQuill('quill-skills_tech', 'skills', 'skills_tech', typeof t !== 'undefined' && t.placeholders ? t.placeholders.tech_skills : 'Technical Skills');
        initSingleQuill('quill-skills_soft', 'skills', 'skills_soft', typeof t !== 'undefined' && t.placeholders ? t.placeholders.soft_skills : 'Soft Skills');
        initSingleQuill('quill-skills_languages', 'skills', 'skills_languages', 'English, Hindi...');
        initSingleQuill('quill-hobbies', 'hobbies', 'hobbies', 'Reading, Traveling...');
    }, 100);

    // Design Listeners
    document.querySelectorAll('#form-design input, #form-design select').forEach(input => {
        input.addEventListener('input', (e) => {
            resumeData.design[e.target.name] = e.target.value;
            renderPreview();
            autoSave();
        });
    });

    // Photo Upload Listener
    const photoInput = document.getElementById('photo-input');
    if (photoInput) {
        photoInput.addEventListener('change', uploadPhoto);
    }

    // Language Selector Listener
    const langSelector = document.getElementById('resume-language-selector');
    if (langSelector) {
        langSelector.addEventListener('change', async (e) => {
            const newLang = e.target.value;
            const oldLang = resumeData.language;

            // Save current state to translations object before switching
            if (!resumeData.translations) resumeData.translations = {};
            resumeData.translations[oldLang] = JSON.parse(JSON.stringify({
                personal: resumeData.personal,
                experience: resumeData.experience,
                education: resumeData.education,
                projects: resumeData.projects,
                skills: resumeData.skills,
                hobbies: resumeData.hobbies,
                certifications: resumeData.certifications
            }));

            resumeData.language = newLang;
            await updateTranslations(newLang);

            // If we already have translated content for this language, load it
            if (resumeData.translations[newLang]) {
                if (confirm(`Cached translation for ${newLang} found.\nClick OK to load your previous ${newLang} content.\nClick Cancel to forcefully re-translate the current content into ${newLang}.`)) {
                    const tl = resumeData.translations[newLang];
                    resumeData.personal = tl.personal;
                    resumeData.experience = tl.experience;
                    resumeData.education = tl.education;
                    resumeData.projects = tl.projects;
                    resumeData.skills = tl.skills;
                    resumeData.hobbies = tl.hobbies;
                    resumeData.certifications = tl.certifications;
                    updateEditorInputs();
                    renderPreview();
                    autoSave();
                } else {
                    renderPreview();
                    await translateResumeContent(newLang);
                }
            } else {
                renderPreview(); // This will use updated headers

                // Ask for content translation
                if (confirm(`Language changed to ${newLang}. Do you want to translate your resume content as well?`)) {
                    await translateResumeContent(newLang);
                } else {
                    autoSave();
                }
            }
        });
    }

    // Styling Checkboxes Listener
    document.querySelectorAll('#form-design input[type="checkbox"]').forEach(input => {
        input.addEventListener('change', (e) => {
            resumeData.design[e.target.name] = e.target.checked;
            renderPreview();
            autoSave();
        });
    });

    // Load initial data (if any)
    if (typeof INITIAL_SECTIONS !== 'undefined' && INITIAL_SECTIONS.length > 0) {
        loadInitialData();
    } else {
        // Init design if empty
        if (typeof INITIAL_DESIGN !== 'undefined') {
            resumeData.design = INITIAL_DESIGN;
            // Trigger design population
            populateDesignForm();
        }
    }

    if (typeof INITIAL_PHOTO !== 'undefined' && INITIAL_PHOTO) {
        resumeData.photo_path = INITIAL_PHOTO;
        updatePhotoPreview(INITIAL_PHOTO);
    }

    // Initialize Sortable for Section Reordering
    const sectionContainer = document.getElementById('resumeSections');
    new Sortable(sectionContainer, {
        animation: 150,
        handle: '.section-header', // Drag via header
        ghostClass: 'sortable-ghost'
    });

    // Initial Preview Render
    renderPreview();
});

function toggleSection(id) {
    const el = document.getElementById(`sec-${id}`);
    el.classList.toggle('active');
}

function addItem(section, event) {
    if (event) event.stopPropagation();
    resumeData[section].push({});
    renderFormList(section);
}

function removeItem(section, index) {
    resumeData[section].splice(index, 1);
    renderFormList(section);
    renderPreview();
}

function updateData(section, index, field, value) {
    resumeData[section][index][field] = value;
    renderPreview();
    autoSave();
}

function renderFormList(section) {
    const container = document.getElementById(`list-${section}`);
    if (!container) return;
    container.innerHTML = '';
    resumeData[section].forEach((item, index) => {
        const tmpl = templates[section];
        if (!tmpl) return;
        let html = tmpl.replace(/index/g, index);
        // Inject values
        container.insertAdjacentHTML('beforeend', html);

        // Populate inputs
        const inserted = container.lastElementChild;
        // Simple value binding (manual for this demo)
        if (section === 'education') {
            if (item.institution) inserted.querySelector('input[placeholder="University/School"]').value = item.institution;
            if (item.degree) inserted.querySelector('input[placeholder="Degree"]').value = item.degree;
            if (item.year) inserted.querySelector('input[placeholder="Year"]').value = item.year;
            if (item.score) inserted.querySelector('input[placeholder="Score/CGPA"]').value = item.score;
        } else if (section === 'experience') {
            if (item.company) inserted.querySelector('input[placeholder="Company Name"]').value = item.company;
            if (item.role) inserted.querySelector('input[placeholder="Role/Title"]').value = item.role;
            if (item.start) inserted.querySelector('input[placeholder="Start Date"]').value = item.start;
            if (item.end) inserted.querySelector('input[placeholder="End Date"]').value = item.end;
            // Init Quill
            initQuill(`quill-experience-${index}`, 'experience', index, 'description');
        } else if (section === 'projects') {
            if (item.title) inserted.querySelector('input[placeholder="Project Title"]').value = item.title;
            if (item.tech) inserted.querySelector('input[placeholder="Tech Stack"]').value = item.tech;
            // Init Quill
            initQuill(`quill-projects-${index}`, 'projects', index, 'description');
        } else if (section === 'certifications') {
            if (item.name) inserted.querySelector('input[placeholder="Certification name"]').value = item.name;
            if (item.issuer) inserted.querySelector('input[placeholder="Issuer"]').value = item.issuer;
            if (item.link) inserted.querySelector('input[placeholder="Date / Link"]').value = item.link;
        }
    });
}

function renderPreview() {
    const p = resumeData.personal;
    document.getElementById('prev-name').innerText = p.full_name || 'YOUR NAME';

    // Construct contact line
    let contactInfo = [];
    document.getElementById('prev-content').innerHTML = '';

    // Handle Modern Flow Contact Rendering
    if (resumeData.design.layout === 'modern_flow') {
        let contactHtml = '<div class="row w-100 g-0" style="margin-top:10px;">';
        if (p.email) contactHtml += `<div class="col-6"><i class="fas fa-envelope"></i> ${p.email}</div>`;
        if (p.phone) contactHtml += `<div class="col-6"><i class="fas fa-phone"></i> ${p.phone}</div>`;
        if (p.location) contactHtml += `<div class="col-6"><i class="fas fa-location-dot"></i> ${p.location}</div>`;
        if (p.linkedin) contactHtml += `<div class="col-6"><i class="fab fa-linkedin"></i> ${p.linkedin.replace('https://', '').replace('www.', '')}</div>`;
        if (p.github) contactHtml += `<div class="col-6"><i class="fab fa-github"></i> ${p.github.replace('https://', '').replace('www.', '')}</div>`;
        contactHtml += '</div>';
        document.getElementById('prev-contact').innerHTML = contactHtml;
    } else {
        const contactEl = document.getElementById('prev-contact');
        contactEl.innerHTML = '';

        // Line 1: Email, Phone, Location (bold)
        const contactLine = [];
        if (p.email) contactLine.push(p.email);
        if (p.phone) contactLine.push(p.phone);
        if (p.location) contactLine.push(p.location);
        if (contactLine.length) {
            const line1 = document.createElement('div');
            line1.style.fontWeight = 'bold';
            line1.style.fontSize = '10pt';
            line1.innerText = contactLine.join(' | ');
            contactEl.appendChild(line1);
        }

        // Line 2: LinkedIn, GitHub, Portfolio (bold)
        const links = [];
        if (p.linkedin) links.push(p.linkedin);
        if (p.github) links.push(p.github);
        if (p.portfolio) links.push(p.portfolio);
        if (links.length) {
            const line2 = document.createElement('div');
            line2.style.fontWeight = 'bold';
            line2.style.fontSize = '10pt';
            line2.style.marginTop = '2px';
            line2.innerText = links.join(' | ');
            contactEl.appendChild(line2);
        }
    }

    // 2. Summary
    const summaryHtml = p.summary ? `<div class="preview-item-desc">${p.summary}</div>` : null;

    // Build sections objects
    const previewSections = {};

    if (summaryHtml) previewSections['summary'] = { title: TRANSLATIONS.headers.summary, html: summaryHtml };

    // 3. Education
    if (resumeData.education.length) {
        let html = resumeData.education.map(e => `
            <div class="preview-item">
                <div class="preview-item-date">${e.year || ''}</div>
                <div class="preview-item-title">${e.institution || ''}</div>
                <div class="preview-item-subtitle">${e.degree || ''} ${e.score ? '- ' + e.score : ''}</div>
            </div>
        `).join('');
        previewSections['education'] = { title: TRANSLATIONS.headers.education, html: html };
    }

    // 4. Skills
    if (resumeData.skills.skills_tech || resumeData.skills.skills_soft || resumeData.skills.skills_languages) {
        let html = '';
        if (resumeData.skills.skills_tech) html += `<div><strong>${TRANSLATIONS.labels.tech_skills}:</strong> ${resumeData.skills.skills_tech}</div>`;
        if (resumeData.skills.skills_soft) html += `<div><strong>${TRANSLATIONS.labels.soft_skills}:</strong> ${resumeData.skills.skills_soft}</div>`;
        if (resumeData.skills.skills_languages) html += `<div><strong>${TRANSLATIONS.labels.languages}:</strong> ${resumeData.skills.skills_languages}</div>`;
        previewSections['skills'] = { title: TRANSLATIONS.headers.skills, html: html };
    }

    // 5. Experience
    if (resumeData.experience.length) {
        let html = resumeData.experience.map((e, idx) => {
            let desc = e.description || '';
            return `
            <div class="preview-item">
                <div class="preview-item-date">${e.start || ''} - ${e.end || ''}</div>
                <div class="preview-item-title">${e.company || ''}</div>
                <div class="preview-item-subtitle ${resumeData.design.italicSubs ? 'fst-italic' : ''}">${e.role || ''}</div>
                <div class="preview-item-desc">${desc}</div>
            </div>`;
        }).join('');
        previewSections['experience'] = { title: TRANSLATIONS.headers.experience, html: html };
    }

    // 6. Projects
    if (resumeData.projects.length) {
        let html = resumeData.projects.map((p, idx) => {
            let desc = p.description || '';
            return `
            <div class="preview-item">
                <div class="preview-item-title">${p.title || ''}</div>
                <div class="preview-item-subtitle ${resumeData.design.italicSubs ? 'fst-italic' : ''}">${p.tech || ''}</div>
                <div class="preview-item-desc">${desc}</div>
            </div>`;
        }).join('');
        previewSections['projects'] = { title: TRANSLATIONS.headers.projects, html: html };
    }

    // 7. Certifications
    if (resumeData.certifications && resumeData.certifications.length) {
        let html = resumeData.certifications.map(c => `
            <div class="preview-item">
                <div class="preview-item-title">${c.name || ''}</div>
                <div class="preview-item-subtitle">${c.issuer || ''} ${c.link ? ' · ' + c.link : ''}</div>
            </div>`).join('');
        previewSections['certifications'] = { title: TRANSLATIONS.headers.certifications || 'Certifications', html: html };
    }

    // 8. Hobbies
    if (resumeData.hobbies && resumeData.hobbies.hobbies) {
        previewSections['hobbies'] = { title: TRANSLATIONS.headers.hobbies, html: `<div class="preview-item-desc">${resumeData.hobbies.hobbies}</div>` };
    }

    // Distribute sections based on layout
    const layout = resumeData.design.layout || 'one_column';
    const contentArea = document.getElementById('prev-content');

    if (layout === 'two_column' || layout === 'mixed_column') {
        contentArea.innerHTML = `
            <div class="preview-layout-columns" style="display: grid; grid-template-columns: 30% 70%; gap: 20px;">
                <div class="preview-sidebar"></div>
                <div class="preview-main"></div>
            </div>
        `;
        const sidebar = contentArea.querySelector('.preview-sidebar');
        const main = contentArea.querySelector('.preview-main');

        const sidebarItems = ['skills', 'certifications', 'hobbies'];
        const mainItems = ['summary', 'experience', 'education', 'projects'];

        if (layout === 'mixed_column') {
            // In mixed, summary and experience are top full-width, others are columns
            contentArea.innerHTML = `
                <div class="preview-top"></div>
                <div class="preview-layout-columns" style="display: grid; grid-template-columns: 50% 50%; gap: 20px; margin-top:15px;">
                    <div class="preview-left"></div>
                    <div class="preview-right"></div>
                </div>
            `;
            const top = contentArea.querySelector('.preview-top');
            const left = contentArea.querySelector('.preview-left');
            const right = contentArea.querySelector('.preview-right');

            ['summary', 'experience'].forEach(key => { if (previewSections[key]) addPreviewSectionTo(previewSections[key].title, previewSections[key].html, top); });
            ['education'].forEach(key => { if (previewSections[key]) addPreviewSectionTo(previewSections[key].title, previewSections[key].html, left); });
            ['skills', 'projects', 'certifications', 'hobbies'].forEach(key => { if (previewSections[key]) addPreviewSectionTo(previewSections[key].title, previewSections[key].html, right); });
        } else {
            sidebarItems.forEach(key => { if (previewSections[key]) addPreviewSectionTo(previewSections[key].title, previewSections[key].html, sidebar); });
            mainItems.forEach(key => { if (previewSections[key]) addPreviewSectionTo(previewSections[key].title, previewSections[key].html, main); });
        }
    } else {
        const order = ['summary', 'experience', 'education', 'skills', 'projects', 'certifications', 'hobbies'];
        order.forEach(key => {
            if (previewSections[key]) {
                addPreviewSection(previewSections[key].title, previewSections[key].html);
            }
        });
    }

    // Apply Design
    applyDesign();

    // Render Photo
    renderPhoto();
}

function addPreviewSectionTo(title, content, container) {
    const div = document.createElement('div');
    div.className = 'preview-section';
    div.innerHTML = `<div class="preview-section-title" style="font-weight:bold; font-size:1.2em; margin-bottom:10px; border-bottom: 2px solid #eee;">${title}</div>${content}`;
    container.appendChild(div);
}

function applyDesign() {
    const preview = document.getElementById('resume-preview');
    const d = resumeData.design || {};

    preview.style.fontFamily = d.font || "'Helvetica', 'Arial', sans-serif";
    preview.style.lineHeight = d.spacing || 1.5;
    preview.style.fontSize = (d.fontSize || 11) + 'pt';

    // Apply Colors
    const color = d.color || '#2c3e50';
    // We can use CSS variables or direct manipulation
    preview.querySelectorAll('.preview-section-title').forEach(el => {
        el.style.color = color;
        el.style.fontWeight = d.boldHeadings ? '900' : 'bold';
        if (d.textShadow) {
            el.style.textShadow = `1px 1px 2px ${color}44`;
        } else {
            el.style.textShadow = 'none';
        }
    });

    preview.querySelectorAll('.preview-item-title').forEach(el => {
        el.style.color = '#333';
        el.style.fontWeight = d.boldHeadings ? '800' : 'bold';
    });

    preview.querySelectorAll('.preview-item-desc').forEach(el => {
        el.style.fontWeight = d.boldHeadings ? 'bold' : 'normal';
    });

    // Header specific
    const nameEl = document.getElementById('prev-name');
    nameEl.style.color = color;
    nameEl.style.fontWeight = d.boldHeadings ? '900' : 'bold';

    // Layout Specific Preview Adjustments
    const header = document.querySelector('.preview-header');
    const previewContainer = document.getElementById('prev-content');

    // Clear layout classes
    preview.className = 'resume-paper';
    preview.classList.add('layout-' + (d.layout || 'one_column'));
    if (d.template) {
        preview.classList.add('template-' + d.template);
    }

    if (d.layout === 'modern_flow') {
        header.style.backgroundColor = color;
        header.style.color = 'white';
        header.style.padding = '20px';
        header.style.borderRadius = '5px';
        nameEl.style.color = 'white';
        document.getElementById('prev-contact').style.color = 'white';

        // Add "Role" to preview if exists
        let roleEl = document.getElementById('prev-role');
        if (!roleEl) {
            roleEl = document.createElement('div');
            roleEl.id = 'prev-role';
            roleEl.style.fontStyle = 'italic';
            roleEl.style.fontSize = '1.1em';
            roleEl.style.marginTop = '5px';
            header.insertBefore(roleEl, document.getElementById('prev-contact'));
        }
        roleEl.innerText = resumeData.personal.role || '';
        roleEl.style.display = resumeData.personal.role ? 'block' : 'none';

        preview.querySelectorAll('.preview-section-title').forEach(el => {
            el.style.textAlign = 'center';
            el.style.borderBottom = 'none';
            el.style.position = 'relative';
            el.classList.add('centered-line-title');
            if (!el.querySelector('span')) {
                const text = el.innerText;
                el.innerHTML = `<span style="background:white; padding:0 10px; position:relative; z-index:1;">${text}</span>`;
            }
        });
    } else if (d.layout === 'minimal_layout') {
        header.style.backgroundColor = 'transparent';
        header.style.color = 'inherit';
        header.style.padding = '0';
        document.getElementById('prev-contact').style.color = 'inherit';
        nameEl.style.color = '#444';

        preview.querySelectorAll('.preview-section-title').forEach(el => {
            el.style.textAlign = 'left';
            el.style.borderBottom = '1px solid #ddd';
            el.style.textTransform = 'capitalize';
            el.classList.remove('centered-line-title');
            if (el.querySelector('span')) {
                el.innerText = el.querySelector('span').innerText;
            }
        });
    } else {
        header.style.backgroundColor = 'transparent';
        header.style.color = 'inherit';
        header.style.padding = '0';
        document.getElementById('prev-contact').style.color = 'inherit';
        if (document.getElementById('prev-role')) document.getElementById('prev-role').style.display = 'none';

        preview.querySelectorAll('.preview-section-title').forEach(el => {
            el.style.textAlign = 'left';
            el.style.borderBottom = `2.5px solid ${color}`;
            el.classList.remove('centered-line-title');
            if (el.querySelector('span')) {
                el.innerText = el.querySelector('span').innerText;
            }
        });
    }

    // Handle column layouts in preview if possible
    if (d.layout === 'two_column' || d.layout === 'mixed_column') {
        // Handled in renderPreview for DOM structure
    } else {
        previewContainer.style.display = 'block';
    }
}

function renderPhoto() {
    // Check if photo container exists in preview, if not add it
    let photoContainer = document.getElementById('prev-photo-container');
    if (!photoContainer) {
        photoContainer = document.createElement('div');
        photoContainer.id = 'prev-photo-container';
        photoContainer.style.width = '200px';
        photoContainer.style.height = '200px';
        photoContainer.style.borderRadius = '50%';
        photoContainer.style.overflow = 'hidden';
        photoContainer.style.margin = '0 auto 10px auto';
        photoContainer.style.display = 'none'; // hidden by default

        // Insert before name
        const header = document.querySelector('.preview-header');
        header.insertBefore(photoContainer, header.firstChild);
    }

    if (resumeData.photo_path) {
        photoContainer.style.display = 'block';
        photoContainer.innerHTML = `<img src="${resumeData.photo_path}" style="width:100%; height:100%; object-fit:cover;">`;
    } else {
        photoContainer.style.display = 'none';
        photoContainer.innerHTML = '';
    }
}

function addPreviewSection(title, content) {
    const div = document.createElement('div');
    div.className = 'preview-section';
    div.innerHTML = `<div class="preview-section-title" style="font-weight:bold; font-size:1.2em; margin-bottom:10px; border-bottom: 2px solid #eee;">${title}</div>${content}`;
    document.getElementById('prev-content').appendChild(div);
}

async function saveResume(silent = false) {
    const statusEl = document.getElementById('save-status');
    if (silent) {
        statusEl.innerText = 'Saving...';
    }

    // Determine section order from DOM
    const sectionsOrder = [];
    document.querySelectorAll('.section-card').forEach(card => {
        const body = card.querySelector('.section-body');
        if (body) {
            const id = body.id.replace('sec-', '');
            // 'design' is special; 'evidence' is API; 'summary' is stored inside personal
            if (id !== 'design' && id !== 'evidence' && id !== 'summary' && resumeData[id]) {
                sectionsOrder.push({
                    name: id,
                    content: resumeData[id]
                });
            }
        }
    });

    const data = {
        title: document.querySelector('h5').innerText,
        language: resumeData.language || 'English',
        target_role: 'General',
        design: {
            ...resumeData.design,
            translations: resumeData.translations || {}
        },
        sections: sectionsOrder
    };

    try {
        const res = await fetch(`/resume/${RESUME_ID}/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();

        if (silent) {
            statusEl.innerText = 'Saved';
            setTimeout(() => { statusEl.innerText = ''; }, 2000);
        } else {
            alert(result.message);
        }
    } catch (e) {
        console.error(e);
        if (silent) statusEl.innerText = 'Error saving';
        else alert('Error saving resume');
    }
}

function updateEditorInputs() {
    const p = resumeData.personal;
    const s = resumeData.skills || {};
    const h = resumeData.hobbies || {};

    if (document.querySelector('input[name="full_name"]')) document.querySelector('input[name="full_name"]').value = p.full_name || '';
    if (document.querySelector('input[name="email"]')) document.querySelector('input[name="email"]').value = p.email || '';
    if (document.querySelector('input[name="phone"]')) document.querySelector('input[name="phone"]').value = p.phone || '';
    if (document.querySelector('input[name="location"]')) document.querySelector('input[name="location"]').value = p.location || '';
    if (document.querySelector('input[name="portfolio"]')) document.querySelector('input[name="portfolio"]').value = p.portfolio || '';
    if (document.querySelector('input[name="linkedin"]')) document.querySelector('input[name="linkedin"]').value = p.linkedin || '';
    if (document.querySelector('input[name="github"]')) document.querySelector('input[name="github"]').value = p.github || '';
    if (quills['quill-summary']) quills['quill-summary'].root.innerHTML = p.summary || '';

    if (quills['quill-skills_tech']) quills['quill-skills_tech'].root.innerHTML = s.skills_tech || '';
    if (quills['quill-skills_soft']) quills['quill-skills_soft'].root.innerHTML = s.skills_soft || '';
    if (quills['quill-skills_languages']) quills['quill-skills_languages'].root.innerHTML = s.skills_languages || '';

    if (quills['quill-hobbies']) quills['quill-hobbies'].root.innerHTML = h.hobbies || '';

    renderFormList('education');
    renderFormList('experience');
    renderFormList('projects');
    renderFormList('certifications');
}

async function translateResumeContent(targetLang) {
    const statusEl = document.getElementById('save-status');
    statusEl.innerText = 'Translating content...';

    // Add spinner overlay
    const overlay = document.createElement('div');
    overlay.id = 'translation-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = '0'; overlay.style.left = '0';
    overlay.style.width = '100vw'; overlay.style.height = '100vh';
    overlay.style.backgroundColor = 'rgba(255,255,255,0.7)';
    overlay.style.zIndex = '9999';
    overlay.style.display = 'flex';
    overlay.style.flexDirection = 'column';
    overlay.style.justifyContent = 'center';
    overlay.style.alignItems = 'center';
    overlay.innerHTML = '<div class="spinner-border text-primary" role="status"></div><h4 class="mt-3">Translating...</h4><p class="text-muted">Optimizing via batch translation</p>';
    document.body.appendChild(overlay);

    try {
        const res = await fetch('/api/resume/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                resumeData: resumeData,
                targetLang: targetLang
            })
        });
        const result = await res.json();
        if (result.status === 'success') {
            resumeData = result.translatedData;

            // Re-render editor inputs
            updateEditorInputs();
            renderPreview();

            statusEl.innerText = 'Translation Complete!';
            setTimeout(() => { statusEl.innerText = ''; }, 3000);

            // autoSave translated data
            autoSave();
        } else {
            console.error(result.message);
            statusEl.innerText = 'Translation error';
            alert('Failed to translate content: ' + result.message);
        }
    } catch (e) {
        console.error(e);
        statusEl.innerText = 'Translation error';
        alert('An error occurred during translation.');
    } finally {
        const ov = document.getElementById('translation-overlay');
        if (ov) ov.remove();
    }
}

function loadInitialData() {
    INITIAL_SECTIONS.forEach(sec => {
        if (sec.section_name && resumeData.hasOwnProperty(sec.section_name)) {
            resumeData[sec.section_name] = sec.section_content;
        }
    });

    if (typeof INITIAL_DESIGN !== 'undefined') {
        resumeData.design = INITIAL_DESIGN;
        if (resumeData.design.translations) {
            resumeData.translations = resumeData.design.translations;
        }
        populateDesignForm();
    }

    // Initialize the tracked language from the DOM if present
    const langSelect = document.getElementById('resume-language-selector');
    if (langSelect) {
        resumeData.language = langSelect.value;
    } else {
        resumeData.language = 'English';
    }

    // Populate Forms
    // Personal
    const p = resumeData.personal;
    if (p.full_name) document.querySelector('input[name="full_name"]').value = p.full_name;
    if (p.email) document.querySelector('input[name="email"]').value = p.email;
    if (p.phone) document.querySelector('input[name="phone"]').value = p.phone;
    if (p.location) document.querySelector('input[name="location"]').value = p.location;
    // New fields
    if (p.portfolio) document.querySelector('input[name="portfolio"]').value = p.portfolio;
    if (p.linkedin) document.querySelector('input[name="linkedin"]').value = p.linkedin;
    if (p.github) document.querySelector('input[name="github"]').value = p.github;

    if (p.summary && quills['quill-summary']) quills['quill-summary'].root.innerHTML = p.summary;

    // Skills
    const s = resumeData.skills;
    if (s.skills_tech && quills['quill-skills_tech']) quills['quill-skills_tech'].root.innerHTML = s.skills_tech;
    if (s.skills_soft && quills['quill-skills_soft']) quills['quill-skills_soft'].root.innerHTML = s.skills_soft;
    if (s.skills_languages && quills['quill-skills_languages']) quills['quill-skills_languages'].root.innerHTML = s.skills_languages;

    // Hobbies
    const h = resumeData.hobbies;
    if (h.hobbies && quills['quill-hobbies']) quills['quill-hobbies'].root.innerHTML = h.hobbies;

    // Lists
    renderFormList('education');
    renderFormList('experience');
    renderFormList('projects');
    renderFormList('certifications');

    // Preview
    renderPreview();
}



function populateDesignForm() {
    const d = resumeData.design || {};
    if (d.font) document.querySelector('select[name="font"]').value = d.font;
    if (d.layout) document.querySelector('select[name="layout"]').value = d.layout;
    if (d.template) {
        const tmplSelect = document.querySelector('select[name="template"]');
        if (tmplSelect) tmplSelect.value = d.template;
    }
    if (d.color) document.querySelector('input[name="color"]').value = d.color;
    if (d.fontSize) document.querySelector('input[name="fontSize"]').value = d.fontSize;
    if (d.spacing) document.querySelector('input[name="spacing"]').value = d.spacing;

    // Checkboxes
    if (d.boldHeadings) document.getElementById('boldHeadings').checked = true;
    if (d.italicSubs) document.getElementById('italicSubs').checked = true;
    if (d.textShadow) document.getElementById('textShadow').checked = true;
}

async function updateTranslations(lang) {
    try {
        const res = await fetch(`/resume/translations/${lang}`);
        const data = await res.json();
        // Update global TRANSLATIONS properties
        Object.assign(TRANSLATIONS, data);

        // Re-calculate headers in the editor sidebar if needed?
        // For now, let's just update the headers visible in the sidebar manually or wait for refresh
        // Actually, the sidebar headers are server-side rendered. 
        // We might need to refresh them if we want full consistency.
    } catch (err) {
        console.error('Failed to update translations', err);
    }
}

async function uploadPhoto(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('photo', file);

    try {
        const res = await fetch(`/resume/${RESUME_ID}/upload_photo`, {
            method: 'POST',
            body: formData
        });
        const result = await res.json();
        if (result.status === 'success') {
            resumeData.photo_path = result.photo_path;
            updatePhotoPreview(result.photo_path);
            renderPreview();
        } else {
            alert('Photo upload failed');
        }
    } catch (err) {
        console.error(err);
        alert('Error uploading photo');
    }
}

function updatePhotoPreview(path) {
    const box = document.getElementById('photo-preview');
    box.innerHTML = `<img src="${path}" style="width:100%; height:100%; object-fit:cover;">`;
}

async function downloadPDF() {
    await saveResume(true); // Force a save first so all the latest design configs exist on server
    const format = document.getElementById('download-format') ? document.getElementById('download-format').value : 'pdf';
    const style = document.getElementById('download-style') ? document.getElementById('download-style').value : '';
    let url = `/resume/${RESUME_ID}/download/${format}?t=${Date.now()}`;
    if (style) url += '&format_style=' + encodeURIComponent(style);
    window.location.href = url;

    // Auto-open feedback modal 3 seconds after download starts
    if (window.TalentryxFeedback) {
        window.TalentryxFeedback.promptAfterAction(3000);
    }
}

async function analyzeResume() {
    const modal = new bootstrap.Modal(document.getElementById('analysisModal'));
    modal.show();

    document.getElementById('analysis-loading').style.display = 'block';
    document.getElementById('analysis-content').style.display = 'none';

    try {
        const res = await fetch(`/analysis/${RESUME_ID}/analyze`);
        const data = await res.json();

        if (data.status === 'success') {
            // Populate ATS Score
            if (data.ats_score) {
                const score = data.ats_score.score;
                document.getElementById('ats-score-text').innerText = score;
                document.getElementById('ats-circle').setAttribute('stroke-dasharray', `${score}, 100`);

                // Color coding
                const circle = document.getElementById('ats-circle');
                if (score >= 80) circle.setAttribute('stroke', '#2ecc71');
                else if (score >= 60) circle.setAttribute('stroke', '#f1c40f');
                else circle.setAttribute('stroke', '#e74c3c');

                const checksContainer = document.getElementById('ats-checks');
                checksContainer.innerHTML = '';
                data.ats_score.checks.forEach(check => {
                    let icon = check.status === 'pass' ? '<i class="fas fa-check-circle text-success me-2"></i>' :
                        (check.status === 'warn' ? '<i class="fas fa-exclamation-circle text-warning me-2"></i>' :
                            '<i class="fas fa-times-circle text-danger me-2"></i>');
                    checksContainer.innerHTML += `<li class="list-group-item px-0 py-1 border-0">${icon} <strong>${check.name}:</strong> ${check.msg}</li>`;
                });
            }

            // Populate Job Recommendations
            const jobContainer = document.getElementById('job-recommendations');
            jobContainer.innerHTML = '';
            if (data.recommendations && data.recommendations.length > 0) {
                jobContainer.style.display = 'block';
                // Take top 3
                data.recommendations.slice(0, 3).forEach(job => {
                    jobContainer.innerHTML += `
                        <div class="card mb-2">
                            <div class="card-body py-2">
                                <h6 class="card-title mb-1">${job.role}</h6>
                                <div class="progress" style="height: 5px;">
                                    <div class="progress-bar bg-success" role="progressbar" style="width: ${job.match_score}%"></div>
                                </div>
                                <small class="text-muted">Match Score: ${job.match_score}%</small>
                            </div>
                        </div>
                    `;
                });
            } else {
                jobContainer.style.display = 'block';
                jobContainer.innerHTML = '<p class="text-muted">No specific job recommendations found.</p>';
            }

            // Populate Gap Analysis + progress bar
            if (data.gap_analysis) {
                document.getElementById('gap-role').innerText = data.gap_analysis.role;
                const pct = data.gap_analysis.match_percentage || 0;
                const wrap = document.getElementById('skill-gap-progress-wrap');
                const bar = document.getElementById('skill-gap-progress-bar');
                if (wrap && bar) {
                    wrap.style.display = 'block';
                    bar.style.width = pct + '%';
                    bar.setAttribute('aria-valuenow', pct);
                    bar.textContent = pct + '%';
                    bar.className = 'progress-bar ' + (pct >= 70 ? 'bg-success' : (pct >= 40 ? 'bg-warning' : 'bg-danger'));
                }

                const missingList = document.getElementById('missing-skills');
                missingList.innerHTML = '';
                data.gap_analysis.missing_skills.forEach(skill => {
                    missingList.innerHTML += `<li class="list-group-item list-group-item-danger py-1">${skill}</li>`;
                });

                const matchingList = document.getElementById('matching-skills');
                matchingList.innerHTML = '';
                data.gap_analysis.matching_skills.forEach(skill => {
                    matchingList.innerHTML += `<li class="list-group-item list-group-item-success py-1">${skill}</li>`;
                });

                // Populate Courses
                const courseContainer = document.getElementById('course-recommendations');
                courseContainer.innerHTML = '';
                if (data.gap_analysis.recommended_courses && data.gap_analysis.recommended_courses.length > 0) {
                    data.gap_analysis.recommended_courses.forEach(course => {
                        courseContainer.innerHTML += `
                            <div class="col-md-6 mb-2">
                                <div class="card h-100">
                                    <div class="card-body py-2">
                                        <h6 class="card-title text-primary" style="font-size: 0.9em;">${course.title}</h6>
                                        <p class="card-text small mb-1">${course.provider}</p>
                                        <a href="${course.link}" target="_blank" class="btn btn-xs btn-outline-primary" style="font-size: 0.8em;">View Course</a>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                } else {
                    courseContainer.innerHTML = '<div class="col-12"><p class="text-muted">No courses found for missing skills.</p></div>';
                }

            }

            // Populate Detailed Job Recommendations
            if (data.detailed_jobs && data.detailed_jobs.length > 0) {
                const detailedContainer = document.getElementById('detailed-job-recommendations');
                if (detailedContainer) {
                    detailedContainer.innerHTML = '';
                    detailedContainer.style.display = 'grid';
                    detailedContainer.style.gridTemplateColumns = 'repeat(3, 1fr)';
                    detailedContainer.style.gap = '15px';

                    data.detailed_jobs.slice(0, 5).forEach(job => {
                        let missingHtml = job.missing_skills && job.missing_skills.length > 0
                            ? job.missing_skills.join(', ')
                            : '<span class="text-success">None!</span>';

                        let readableRole = (job.role ? job.role : job.job).replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

                        detailedContainer.innerHTML += `
                            <div class="card shadow-sm h-100 border-0" style="border-radius:12px; transition: transform 0.3s;" onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
                                <div class="card-body p-3 d-flex flex-column">
                                    <h6 class="card-title fw-bold text-dark mb-2">${readableRole}</h6>
                                    <p class="mb-1 fw-bold text-success"><i class="fas fa-bullseye me-1"></i>Match: ${job.score}%</p>
                                    
                                    <p class="small text-muted mb-1" style="font-size:0.8rem">
                                        <strong class="text-dark">Required:</strong> ${job.required_skills ? job.required_skills.join(', ') : ''}
                                    </p>
                                    <p class="small text-danger mb-2" style="font-size:0.8rem">
                                        <strong class="text-dark">Missing:</strong> ${missingHtml}
                                    </p>
                                    
                                    <p class="small fst-italic mb-3" style="font-size:0.8rem; background:#f8f9fa; padding:5px; border-radius:4px;">
                                        <i class="fas fa-chart-line text-primary me-1"></i> ${job.trend}
                                    </p>
                                    
                                    <a href="${job.apply_link || '#'}" target="_blank" class="btn btn-sm btn-success w-100 mt-auto fw-bold" style="border-radius:6px;">Apply Now</a>
                                </div>
                            </div>
                        `;
                    });
                }
            }

            document.getElementById('analysis-loading').style.display = 'none';
            document.getElementById('analysis-content').style.display = 'block';
        } else {
            alert('Analysis failed: ' + (data.message || 'Unknown error'));
            modal.hide();
        }
    } catch (e) {
        console.error(e);
        alert('Error communicating with server');
        modal.hide();
    }
}

// Rich Text Editor Utils – bold, italic, underline, shadow apply to selected text only
let quills = {};

function initQuill(elementId, section, index, field) {
    // Check if element exists
    if (!document.getElementById(elementId)) return;

    // Check if already initialized
    if (quills[`${section}-${index}`]) return;

    const quill = new Quill(`#${elementId}`, {
        theme: 'snow',
        modules: {
            toolbar: [
                ['bold', 'italic', 'underline', 'strike'],
                [{ 'color': [] }, { 'background': [] }],
                [{ 'size': ['small', false, 'large', 'huge'] }],
                [{ 'align': [] }],
                [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                ['clean']
            ]
        }
    });

    // Set initial content
    if (resumeData[section][index] && resumeData[section][index][field]) {
        quill.root.innerHTML = resumeData[section][index][field];
    }

    // Listener
    quill.on('text-change', function () {
        if (!resumeData[section][index]) resumeData[section][index] = {};
        resumeData[section][index][field] = quill.root.innerHTML;
        renderPreview();
        autoSave();
    });

    quills[`${section}-${index}`] = quill;
}

function initSingleQuill(elementId, section, field, placeholder) {
    if (!document.getElementById(elementId)) return;
    if (quills[elementId]) return;

    const quill = new Quill(`#${elementId}`, {
        theme: 'snow',
        placeholder: placeholder,
        modules: {
            toolbar: [
                ['bold', 'italic', 'underline', 'strike'],
                [{ 'color': [] }, { 'background': [] }],
                [{ 'size': ['small', false, 'large', 'huge'] }],
                [{ 'align': [] }],
                [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                ['clean']
            ]
        }
    });

    if (resumeData[section] && resumeData[section][field]) {
        quill.root.innerHTML = resumeData[section][field];
    }

    quill.on('text-change', function () {
        if (!resumeData[section]) resumeData[section] = {};
        resumeData[section][field] = quill.root.innerHTML;
        renderPreview();
        autoSave();
    });

    quills[elementId] = quill;
}

async function importResume(input) {
    const file = input.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('resume_file', file);

    // Show loading
    const btn = input.nextElementSibling;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Parsing...';
    btn.disabled = true;

    try {
        const res = await fetch('/resume/import', {
            method: 'POST',
            body: formData
        });
        const result = await res.json();

        if (result.status === 'success') {
            const data = result.data;

            // Merge Data
            if (data.personal) {
                resumeData.personal = { ...resumeData.personal, ...data.personal };
                // Update inputs
                if (data.personal.full_name) document.querySelector('input[name="full_name"]').value = data.personal.full_name;
                if (data.personal.email) document.querySelector('input[name="email"]').value = data.personal.email;
                if (data.personal.phone) document.querySelector('input[name="phone"]').value = data.personal.phone;
            }

            if (data.skills) {
                if (data.skills.skills_tech) {
                    resumeData.skills.skills_tech = data.skills.skills_tech;
                    document.querySelector('textarea[name="skills_tech"]').value = data.skills.skills_tech;
                }
                if (data.skills.skills_soft) {
                    resumeData.skills.skills_soft = data.skills.skills_soft;
                    document.querySelector('textarea[name="skills_soft"]').value = data.skills.skills_soft;
                }
            }

            if (data.education && data.education.length > 0) {
                resumeData.education = data.education;
                renderFormList('education');
            }

            if (data.experience && data.experience.length > 0) {
                resumeData.experience = data.experience;
                renderFormList('experience');
            }

            if (data.projects && data.projects.length > 0) {
                resumeData.projects = data.projects;
                renderFormList('projects');
            }

            renderPreview();
            autoSave();
            alert('Resume imported successfully! Please review and edit the extracted data.');
        } else {
            alert('Import failed: ' + result.message);
        }
    } catch (err) {
        console.error(err);
        alert('Error parsing resume');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
        input.value = ''; // Reset input
    }
}

// --- AI Copilot Logic ---
let copilotActiveElement = null;
let copilotActiveQuill = null;

function toggleCopilot() {
    const sidebar = document.querySelector('.editor-sidebar');
    const preview = document.querySelector('.editor-preview');
    const panel = document.getElementById('ai-copilot-panel');

    sidebar.classList.toggle('copilot-open');
    preview.classList.toggle('copilot-open');
    panel.classList.toggle('open');

    if (panel.classList.contains('open')) {
        setupCopilotListeners();
        // Trigger generic focus message if nothing selected
        if (!copilotActiveElement && !copilotActiveQuill) {
            document.getElementById('copilot-placeholder').style.display = 'block';
            document.getElementById('copilot-content').style.display = 'none';
        }
    } else {
        removeCopilotListeners();
    }
}

function setupCopilotListeners() {
    // Standard inputs and textareas
    document.querySelectorAll('.editor-sidebar input[type="text"], .editor-sidebar textarea').forEach(el => {
        el.addEventListener('focus', handleCopilotFocus);
        el.addEventListener('click', handleCopilotFocus);
    });

    // Support for Quill Editors (Experience & Projects)
    document.querySelectorAll('.editor-sidebar .ql-editor').forEach(el => {
        el.addEventListener('focus', handleQuillCopilotFocus);
        el.addEventListener('click', handleQuillCopilotFocus);
    });
}

function removeCopilotListeners() {
    document.querySelectorAll('.editor-sidebar input[type="text"], .editor-sidebar textarea').forEach(el => {
        el.removeEventListener('focus', handleCopilotFocus);
        el.removeEventListener('click', handleCopilotFocus);
    });
    document.querySelectorAll('.editor-sidebar .ql-editor').forEach(el => {
        el.removeEventListener('focus', handleQuillCopilotFocus);
        el.removeEventListener('click', handleQuillCopilotFocus);
    });
} let chatHistory = [];

function getActiveContextText() {
    if (copilotActiveElement) {
        return copilotActiveElement.value;
    } else if (copilotActiveQuill) {
        const tempDiv = document.createElement("div");
        tempDiv.innerHTML = copilotActiveQuill.querySelector('.ql-editor').innerHTML;
        return tempDiv.innerText || tempDiv.textContent || "";
    }
    return "";
}

function handleCopilotFocus(event) {
    copilotActiveElement = event.target;
    copilotActiveQuill = null;
    updateContextUI();
}

function handleQuillCopilotFocus(event) {
    const quillWrapper = event.currentTarget.closest('.quill-editor') || event.currentTarget.closest('.ql-container').parentElement;
    copilotActiveQuill = quillWrapper;
    copilotActiveElement = null;
    updateContextUI();
}

function updateContextUI() {
    const contextIndicator = document.getElementById('copilot-selected-context');
    const contextTextSpan = document.getElementById('copilot-selected-text');
    if (!contextIndicator) return;

    const text = getActiveContextText();
    if (text && text.trim().length > 0) {
        contextIndicator.style.display = 'block';
        contextTextSpan.innerText = text.length > 50 ? text.substring(0, 50) + "..." : text;
    } else {
        contextIndicator.style.display = 'none';
        contextTextSpan.innerText = '';
    }
}

function handleChatKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
    }
}

function sendChatFromChip(chipText) {
    document.getElementById('copilot-chat-input').value = chipText;
    sendChatMessage();
}

async function sendChatMessage() {
    const inputEl = document.getElementById('copilot-chat-input');
    const messageText = inputEl.value.trim();
    if (!messageText) return;

    inputEl.value = '';

    // Add user message to UI
    appendChatMessage('user', messageText);

    // Build context
    const activeContext = getActiveContextText();

    // Add typing indicator
    const typingId = showTypingIndicator();

    chatHistory.push({ role: 'user', content: messageText, context: activeContext });

    try {
        const res = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: chatHistory,
                context: activeContext,
                userSkills: resumeData.skills,
                targetRole: resumeData.target_role
            })
        });

        removeTypingIndicator(typingId);

        if (res.ok) {
            let data = await res.json();
            if (data.status === 'success') {
                const aiMessage = data.suggestion;
                chatHistory.push({ role: 'assistant', content: aiMessage });
                streamChatResponse(aiMessage);
            } else {
                throw new Error(data.message);
            }
        } else {
            console.warn("Backend API not found or failed, using mock fallback.");
            mockChatResponse(messageText, activeContext);
        }
    } catch (e) {
        console.warn("Copilot API failed, using mock output.", e);
        removeTypingIndicator(typingId);
        mockChatResponse(messageText, activeContext);
    }
}

function appendChatMessage(role, text, isHtml = false) {
    const historyContainer = document.getElementById('chat-history');
    if (!historyContainer) return;
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${role}`;

    const contentDiv = document.createElement('div');
    if (isHtml) {
        contentDiv.innerHTML = text;
    } else {
        contentDiv.innerText = text;
    }
    msgDiv.appendChild(contentDiv);

    if (role === 'ai') {
        const applyBtn = document.createElement('button');
        applyBtn.className = 'btn btn-outline-primary apply-btn';
        applyBtn.innerHTML = '<i class="fas fa-check me-1"></i> Apply to Resume';
        applyBtn.onclick = function () { applyChatResult(contentDiv.innerHTML, contentDiv.innerText); };
        msgDiv.appendChild(applyBtn);
    }

    historyContainer.appendChild(msgDiv);
    historyContainer.scrollTop = historyContainer.scrollHeight;
    return contentDiv;
}

function showTypingIndicator() {
    const historyContainer = document.getElementById('chat-history');
    if (!historyContainer) return 'typing';
    const id = 'typing-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.id = id;
    msgDiv.className = `chat-message ai typing-indicator`;
    msgDiv.innerHTML = `<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>`;
    historyContainer.appendChild(msgDiv);
    historyContainer.scrollTop = historyContainer.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function streamChatResponse(fullText) {
    const contentDiv = appendChatMessage('ai', '', true);
    if (!contentDiv) return;

    // Split text into an array of HTML tags and text characters to avoid breaking HTML rendering
    const tokens = [];
    let currentHtmlTag = "";
    let inTag = false;

    for (let c of fullText) {
        if (c === '<') inTag = true;

        if (inTag) {
            currentHtmlTag += c;
            if (c === '>') {
                inTag = false;
                tokens.push(currentHtmlTag);
                currentHtmlTag = "";
            }
        } else {
            tokens.push(c);
        }
    }

    let i = 0;
    const interval = setInterval(() => {
        if (i < tokens.length) {
            // Unveil chunks of 2-3 characters at a time for smooth streaming, skipping over tags
            let chunk = 3;
            while (chunk > 0 && i < tokens.length) {
                if (tokens[i].startsWith('<')) {
                    // Consume tag fully and immediately without counting against chunk
                    i++;
                    continue;
                }
                i++;
                chunk--;
            }
            // Ensure any immediate trailing tags are also consumed so they close properly
            while (i < tokens.length && tokens[i].startsWith('<')) {
                i++;
            }

            contentDiv.innerHTML = tokens.slice(0, i).join('');
            const historyContainer = document.getElementById('chat-history');
            historyContainer.scrollTop = historyContainer.scrollHeight;
        } else {
            contentDiv.innerHTML = fullText;
            clearInterval(interval);
        }
    }, 15);
}

function applyChatResult(htmlContent, textContent) {
    if (copilotActiveElement) {
        copilotActiveElement.value = textContent;
        const event = new Event('input', { bubbles: true });
        copilotActiveElement.dispatchEvent(event);
    } else if (copilotActiveQuill) {
        const quillId = copilotActiveQuill.id;
        if (quillId && quills[quillId]) {
            quills[quillId].clipboard.dangerouslyPasteHTML(htmlContent);
            // Wait a tick for text-change event to process
            setTimeout(() => {
                renderPreview();
                autoSave();
            }, 50);
        } else {
            copilotActiveQuill.querySelector('.ql-editor').innerHTML = htmlContent;
            renderPreview();
            autoSave();
        }
    } else {
        alert("Please highlight or click on a text field on the left before applying.");
    }
}

function mockChatResponse(msg, context) {
    let output = `I'm your AI assistant! Here is a mock response: "${msg}". `;
    if (context) output += `<br><br>Context applied: "${context.substring(0, 30)}..."`;
    chatHistory.push({ role: 'assistant', content: output });
    streamChatResponse(output);
}
