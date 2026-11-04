"""Print-ready Word generators for the UMU Curriculum Designer."""
import io
import re
from collections import Counter
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BLUE = RGBColor(7, 94, 127)
ORANGE = RGBColor(207, 104, 34)
def norm(s):
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())
def mentioned_unit(suggestion, units):
    """Recognize a unit explicitly named in the proposed activity text."""
    match = re.search(r"\\bunit\\s*([ivxlcdm]+|\\d+)\\b", str(suggestion.get("text", "")), re.I)
    if not match:
        return ""
    code = match.group(1).lower()
    for unit in units:
        found = re.search(r"\\bunit\\s*([ivxlcdm]+|\\d+)\\b", str(unit["name"]), re.I)
        if found and found.group(1).lower() == code:
            return unit["name"]
    return ""

def unit_for(suggestion, units):
    """Return an unambiguous target; conflicting explicit and textual units are rejected."""
    target = str(suggestion.get("unit", "")).strip()
    explicit = ""
    for unit in units:
        name = str(unit["name"])
        head = re.match(r"^\\s*unit\\s*([ivxlcdm]+|\\d+)\\b", name, re.I)
        selected = re.match(r"^\\s*unit\\s*([ivxlcdm]+|\\d+)\\b", target, re.I)
        if target and (norm(target) == norm(name) or
                       (head and selected and head.group(1).lower() == selected.group(1).lower())):
            explicit = name
            break
    mentioned = mentioned_unit(suggestion, units)
    if explicit and mentioned and explicit != mentioned:
        return ""  # Never put a Unit II activity under Unit I.
    if target and not explicit:
        return ""  # Unknown explicit selection requires faculty correction.
    return explicit or mentioned

def weekly_plan(course):
    weeks = max(1, int(course.get("weeks",15)))
    per_week = max(1,int(course.get("lecture",3)))
    slots=[]
    cos=course.get("cos",[])
    for idx,unit in enumerate(course.get("units",[])):
        hours=max(0,int(unit.get("hours",0)))
        topics=[x.strip() for x in re.split(r"[,;\n]+",unit.get("topics","")) if x.strip()]
        if not topics:topics=["Topic allocation pending"]
        for hour in range(hours):
            topic=topics[min(len(topics)-1,hour*len(topics)//max(1,hours))]
            slots.append((unit["name"],topic,"CO"+str(min(idx+1,len(cos))) if cos else "—"))
    rows=[]
    for week in range(weeks):
        chunk=slots[week*per_week:(week+1)*per_week]
        seen=[]
        for unit,topic,co in chunk:
            label=topic
            if label not in seen:seen.append(label)
        cos_for=list(dict.fromkeys(x[2] for x in chunk))
        rows.append({"week":week+1,"topics":"; ".join(seen) or "Revision / assessment (to be confirmed)",
                     "units":", ".join(dict.fromkeys(x[0] for x in chunk)) or "—",
                     "co":", ".join(cos_for) or "—","contact":len(chunk)})
    return rows

def set_shading(cell,fill="E8F1F7"):
    tcPr=cell._tc.get_or_add_tcPr()
    shd=OxmlElement("w:shd");shd.set(qn("w:fill"),fill);tcPr.append(shd)

def table(doc, headers, rows):
    t=doc.add_table(rows=1,cols=len(headers));t.style="Table Grid";t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,h in enumerate(headers):
        cell=t.rows[0].cells[i];cell.text=str(h);set_shading(cell,"D8E7F1")
        for run in cell.paragraphs[0].runs:run.bold=True;run.font.color.rgb=BLUE
    for ri,values in enumerate(rows):
        cells=t.add_row().cells
        for i,value in enumerate(values):
            cells[i].text=str(value)
            if ri%2==1:set_shading(cells[i],"F3F7FA")
    return t

def setup(doc,course,title):
    sec=doc.sections[0];sec.top_margin=Inches(.73);sec.bottom_margin=Inches(.7)
    sec.left_margin=Inches(.76);sec.right_margin=Inches(.76)
    normal=doc.styles["Normal"];normal.font.name="Calibri";normal.font.size=Pt(10)
    normal.paragraph_format.space_after=Pt(5)
    for sty in ["Title","Heading 1","Heading 2","Heading 3"]:
        doc.styles[sty].font.name="Calibri";doc.styles[sty].font.color.rgb=BLUE
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    run=p.add_run("USHA MARTIN UNIVERSITY, RANCHI");run.bold=True;run.font.size=Pt(15);run.font.color.rgb=BLUE
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    run=p.add_run(title.upper());run.bold=True;run.font.size=Pt(13);run.font.color.rgb=ORANGE
    meta=[("Programme",course.get("programme","")),("Faculty name",course.get("faculty","")),
          ("Faculty/Department",course.get("department","")),("Semester",course.get("semester","")),
          ("Course title",course.get("name","")),("Course code",course.get("code","")),
          ("Approved credits",course.get("credits",0)),("Teaching weeks",course.get("weeks",15)),
          ("Weekly lecture hours",course.get("lecture",3))]
    table(doc,["Course information","Details"],meta)
    footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("Usha Martin University | Curriculum review copy")
    return doc

def append_additions(doc,unit,course):
    accepted=[s for s in course.get("suggestions",[]) if s.get("include") and unit_for(s,course["units"])==unit["name"]]
    for s in accepted:
        p=doc.add_paragraph()
        r=p.add_run("PROPOSED ADDITION ("+str(s.get("area","Curriculum"))+"): "+str(s.get("text","")))
        r.bold=True;r.font.color.rgb=BLUE
        shd=OxmlElement("w:shd");shd.set(qn("w:fill"),"FFF0C6");r._r.get_or_add_rPr().append(shd)
        if s.get("source"):doc.add_paragraph("Source / verification: "+str(s["source"]))
    return len(accepted)

def syllabus(course):
    d=setup(Document(),course,"Revised course syllabus — for academic review")
    d.add_heading("Course outcomes",level=1)
    for i,co in enumerate(course.get("cos",[]),1):d.add_paragraph("CO"+str(i)+": "+co)
    d.add_heading("Unit-wise syllabus",level=1)
    for unit in course.get("units",[]):
        d.add_heading(str(unit["name"])+" ("+str(unit["hours"])+" lecture hours)",level=2)
        d.add_paragraph(str(unit.get("topics","")))
        append_additions(d,unit,course)
    unmatched=[s for s in course.get("suggestions",[]) if s.get("include") and not unit_for(s,course["units"])]
    if unmatched:
        d.add_heading("Additions awaiting unit selection — not incorporated",level=2)
        for s in unmatched:d.add_paragraph(str(s.get("area",""))+": "+str(s.get("text","")))
    d.add_paragraph("Original syllabus content is retained. Highlighted additions are proposed and require competent approval.")
    d.add_paragraph("Review status: "+str(course.get("status","Faculty draft")))
    return bytes_of(d)

def short_unit(label):
    """Keep the full unit title in the syllabus but use compact labels in weekly tables."""
    matches = re.findall(r"\\bUnit\\s+(?:[IVXLCDM]+|\\d+)\\b", label, re.I)
    return ", ".join(dict.fromkeys(matches)) if matches else label


def lecture_plan(course):
    d=setup(Document(),course,"Week-wise lecture and learning plan")
    rows=weekly_plan(course)
    weeks=max(1,int(course.get("weeks",15)));weekly=int(course.get("lecture",3))
    contact=weeks*weekly;unit_hours=sum(int(u.get("hours",0)) for u in course.get("units",[]))
    nominal=30*int(course.get("credits",0))
    independent=max(0,nominal-contact)
    d.add_heading("Week-wise teaching plan",level=1)
    plan=[]
    for i,row in enumerate(rows):
        selfhours=independent//weeks+(1 if i<independent%weeks else 0)
        plan.append([row["week"], short_unit(row["units"]), row["topics"], row["co"], row["contact"], selfhours])
    table(d,["Week","Unit","Topics / teaching activities","CO*","Contact h","Independent h**"],plan)
    d.add_paragraph("*CO mapping is a provisional unit-order mapping and must be reviewed against the approved COs.")
    d.add_paragraph("**Independent-learning hours are illustrative, not an adopted University workload requirement.")
    d.add_heading("Unit-wise teaching-hour allocation",level=1)
    table(d,["Unit","Lecture hours"],[[u["name"],u["hours"]] for u in course.get("units",[])])
    d.add_heading("Contact and notional learning-hour report",level=1)
    table(d,["Component","Hours / value"],[
        ["Approved credits",course.get("credits",0)],["Teaching weeks",weeks],
        ["Weekly lecture hours",weekly],["Scheduled contact hours",contact],
        ["Unit-allocated contact hours",unit_hours],["Illustrative independent-learning hours",independent],
        ["Illustrative total notional hours",nominal]])
    if unit_hours!=contact:d.add_paragraph("RECONCILIATION REQUIRED: unit hours differ from scheduled contact hours.")
    if contact>nominal:d.add_paragraph("RECONCILIATION REQUIRED: scheduled contact hours exceed illustrative notional hours.")
    d.add_paragraph("30 notional hours per credit is an illustrative convention, conditional on University authorization.")
    d.add_heading("Reviewed curriculum-enrichment activities",level=1)
    for u in course.get("units",[]):
        for s in course.get("suggestions",[]):
            if s.get("include") and unit_for(s,course["units"])==u["name"]:
                d.add_paragraph(u["name"]+" — "+str(s.get("area",""))+": "+str(s.get("text","")))
    unmatched=[s for s in course.get("suggestions",[]) if s.get("include") and not unit_for(s,course["units"])]
    if unmatched:
        d.add_heading("Additions awaiting corrected unit allocation",level=2)
        for s in unmatched:
            d.add_paragraph(str(s.get("area",""))+": "+str(s.get("text","")))
    d.add_paragraph("Review status: "+str(course.get("status","Faculty draft")))
    return bytes_of(d)

def bytes_of(doc):
    output=io.BytesIO();doc.save(output);return output.getvalue()
