# CareerAI Studio — Professional Full-Stack Project

## Run on Windows
```bat
cd CareerAI_Professional
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Features
- Professional responsive SaaS UI/UX
- Resume upload: PDF/DOCX/TXT
- AI career analysis and career scoring
- Skill extraction and skill-gap analysis
- Career-path recommendations
- Personalized learning roadmap
- Job & internship discovery
- PDF career report
- Dark/light theme
- Mobile responsive layout
- Demo profile for instant testing

## Viva / ML
The system uses NLP-style skill extraction and weighted career matching. Resume text is transformed into a structured skill profile; each career has required skills; overlap is used to calculate a career-fit score. This architecture can later be upgraded to TF-IDF/cosine similarity or a trained classifier.
