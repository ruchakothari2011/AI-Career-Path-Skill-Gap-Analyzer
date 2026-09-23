from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import re, io, csv
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER

app=Flask(__name__)
BASE=Path(__file__).resolve().parent
DATA=BASE/"data"

SKILLS=["python","java","c++","javascript","react","node.js","html","css","sql","mysql","mongodb","excel","power bi","tableau","machine learning","deep learning","nlp","data analysis","data science","tensorflow","pytorch","scikit-learn","git","github","aws","azure","docker","kubernetes","flask","fastapi","communication","leadership","problem solving","teamwork","project management","figma","ui/ux","cybersecurity","linux","cloud computing","statistics","pandas","numpy","opencv"]

CAREERS=[
 {"title":"Data Scientist","desc":"Analyze data, build predictive models, communicate insights.","skills":["python","sql","machine learning","data analysis","statistics","pandas","numpy"],"color":"purple"},
 {"title":"Machine Learning Engineer","desc":"Build, deploy and maintain machine learning systems.","skills":["python","machine learning","deep learning","tensorflow","pytorch","scikit-learn","docker"],"color":"blue"},
 {"title":"Data Analyst","desc":"Turn business data into dashboards, reports and decisions.","skills":["sql","excel","power bi","tableau","python","data analysis","statistics"],"color":"green"},
 {"title":"Full Stack Developer","desc":"Create modern web applications across frontend and backend.","skills":["javascript","react","node.js","html","css","mongodb","git"],"color":"orange"},
 {"title":"AI/NLP Engineer","desc":"Develop intelligent language and AI applications.","skills":["python","nlp","machine learning","deep learning","pytorch","tensorflow"],"color":"pink"},
 {"title":"Cloud & DevOps Engineer","desc":"Automate deployment and manage scalable cloud systems.","skills":["aws","azure","docker","kubernetes","linux","git"],"color":"cyan"},
 {"title":"UI/UX Designer","desc":"Design user-centered interfaces and digital experiences.","skills":["figma","ui/ux","communication","problem solving"],"color":"yellow"}
]

def extract_skills(text):
    t=text.lower()
    return sorted({s for s in SKILLS if re.search(r'(?<!\w)'+re.escape(s.lower())+r'(?!\w)',t)}, key=str.lower)

def sections(text):
    t=text.lower()
    checks={
      "Contact":"email" in t or re.search(r'\b\d{10}\b',t) is not None,
      "Summary":"summary" in t or "objective" in t or "profile" in t,
      "Education":"education" in t or "b.tech" in t or "bachelor" in t,
      "Experience":"experience" in t or "intern" in t or "work history" in t,
      "Skills":"skills" in t or len(extract_skills(text))>=3,
      "Projects":"projects" in t,
      "Certifications":"certification" in t or "certificate" in t
    }
    return checks

def score_resume(text):
    words=re.findall(r'\b[\w+#.-]+\b',text)
    n=len(words)
    sec=sections(text); complete=sum(sec.values())/len(sec)
    length=min(n/500,1) if n<800 else max(0.75,1-(n-800)/1600)
    skills=extract_skills(text)
    keyword=min(len(skills)/15,1)
    ats=round(100*(.42*complete+.25*length+.33*keyword))
    quality=round(100*(.40*complete+.25*length+.35*keyword))
    preds=[]
    for c in CAREERS:
        overlap=len(set(skills)&set(c["skills"]))/max(1,len(c["skills"]))
        preds.append({**c,"score":round(overlap*100)})
    preds.sort(key=lambda x:x["score"],reverse=True)
    tips=[]
    missing=[k for k,v in sec.items() if not v]
    if missing: tips.append("Add missing sections: "+", ".join(missing[:4])+".")
    if n<250: tips.append("Expand your impact with projects, experience and measurable achievements.")
    if len(skills)<8: tips.append("Add relevant technical and soft skills that you can genuinely demonstrate.")
    tips += ["Use action verbs and quantify outcomes where possible.","Tailor keywords to the role you are applying for."]
    return {"ats_score":ats,"quality_score":quality,"word_count":n,"skills":skills,"sections":sec,"predictions":preds[:5],"tips":tips[:5]}

def match(resume,jd):
    rs=set(extract_skills(resume)); js=set(extract_skills(jd))
    overlap=round(100*len(rs&js)/max(1,len(js)))
    # lightweight semantic proxy based on keyword + shared important terms
    rwords=set(re.findall(r'\b[a-zA-Z]{4,}\b',resume.lower()))
    jwords=set(re.findall(r'\b[a-zA-Z]{4,}\b',jd.lower()))
    semantic=round(100*len(rwords&jwords)/max(1,len(jwords)))
    fit=round(.72*semantic+.28*overlap)
    return {"fit_score":fit,"semantic":semantic,"overlap":overlap,"matched":sorted(rs&js),"missing":sorted(js-rs)}

@app.route("/")
def home(): return render_template("index.html")

@app.route("/api/analytics")
def analytics():
    rows=[]
    p=DATA/"career_profiles.csv"
    if p.exists():
        with open(p,encoding="utf-8") as f: rows=list(csv.DictReader(f))
    return jsonify({"profiles":len(rows),"categories":len(CAREERS),"careers":[{"title":c["title"],"score":0} for c in CAREERS]})

@app.route("/api/analyze",methods=["POST"])
def analyze():
    text=request.form.get("text","")
    f=request.files.get("file")
    if f:
        name=f.filename.lower()
        raw=f.read()
        if name.endswith(".txt"): text=raw.decode("utf-8","ignore")
        elif name.endswith(".pdf"):
            try:
                from PyPDF2 import PdfReader
                text="\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(raw)).pages)
            except Exception as e: return jsonify({"error":"Could not read PDF: "+str(e)}),400
        elif name.endswith(".docx"):
            try:
                from docx import Document
                doc=Document(io.BytesIO(raw)); text="\n".join(p.text for p in doc.paragraphs)
            except Exception as e: return jsonify({"error":"Could not read DOCX: "+str(e)}),400
    if not text.strip(): return jsonify({"error":"Please upload a resume or paste resume text."}),400
    return jsonify(score_resume(text))

@app.route("/api/match",methods=["POST"])
def api_match():
    d=request.get_json(force=True); return jsonify(match(d.get("resume",""),d.get("job","")))

@app.route("/api/careers")
def careers():
    return jsonify(CAREERS)

@app.route("/api/jobs")
def jobs():
    p=DATA/"jobs.csv"; rows=[]
    if p.exists():
        with open(p,encoding="utf-8") as f: rows=list(csv.DictReader(f))
    return jsonify(rows)

@app.route("/api/report",methods=["POST"])
def report():
    d=request.get_json(force=True); out=BASE/"reports"/"career_report.pdf"
    styles=getSampleStyleSheet(); story=[]
    story += [Paragraph("CareerAI — Career Intelligence Report",styles["Title"]),Spacer(1,12)]
    story += [Paragraph("Personalized AI-powered career analysis",styles["Normal"]),Spacer(1,18)]
    story += [Paragraph(f"Career Match Score: {d.get('score','—')}%",styles["Heading2"])]
    story += [Paragraph(f"Primary Career: {d.get('career','—')}",styles["Heading3"])]
    story += [Spacer(1,10),Paragraph("Current Skills",styles["Heading3"]),Paragraph(", ".join(d.get("skills",[])) or "—",styles["Normal"])]
    story += [Spacer(1,10),Paragraph("Recommended Skills to Build",styles["Heading3"]),Paragraph(", ".join(d.get("missing",[])) or "No major gaps detected.",styles["Normal"])]
    story += [Spacer(1,15),Paragraph("Generated by CareerAI Studio",styles["Normal"])]
    SimpleDocTemplate(str(out),pagesize=A4,rightMargin=45,leftMargin=45,topMargin=45,bottomMargin=45).build(story)
    return send_file(out,as_attachment=True,download_name="CareerAI_Report.pdf")

@app.route("/api/status")
def status(): return jsonify({"status":"ready","app":"CareerAI Studio","version":"3.0"})
if __name__=="__main__":
    app.run(debug=True,port=5000)
