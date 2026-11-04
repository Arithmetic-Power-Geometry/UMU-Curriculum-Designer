import ast
import io
from pathlib import Path
from docx import Document
from print_engine import syllabus, lecture_plan, unit_for, weekly_plan

ast.parse(Path(__file__).with_name("app.py").read_text(encoding="utf-8"))
course={"programme":"MCA","faculty":"Dr. Mohammad Amir Khusru Akhtar","department":"Computing and IT","semester":"I","name":"Operating System","code":"MCA-CC101","credits":3,"lecture":3,"weeks":15,
"cos":["OS concepts","Scheduling","Deadlocks","Memory","Security"],
"units":[{"name":"Unit I. Introduction","topics":"OS overview, OS types","hours":9},{"name":"Unit II. Process","topics":"Process, PCB, Scheduling","hours":9},{"name":"Unit III. Synchronization","topics":"Semaphores, Deadlock","hours":9},{"name":"Unit IV. Memory Management","topics":"Paging, Virtual memory","hours":9},{"name":"Unit V. Security","topics":"Protection, Security","hours":9}],
"suggestions":[{"area":"AI","text":"Unit II: Verify FCFS scheduling","include":True,"source":"Faculty review"},{"area":"SDG","text":"Unit IV: Compare page faults","include":True,"source":"Faculty review"}],"status":"Faculty draft"}
assert unit_for(course["suggestions"][0],course["units"])==course["units"][1]["name"]
assert unit_for(course["suggestions"][1],course["units"])==course["units"][3]["name"]
assert sum(x["contact"] for x in weekly_plan(course))==45
assert len(weekly_plan(course))==15
d=Document(io.BytesIO(syllabus(course)))
paragraphs=[p.text for p in d.paragraphs]
ai=next(i for i,p in enumerate(paragraphs) if "PROPOSED ADDITION (AI)" in p)
sdg=next(i for i,p in enumerate(paragraphs) if "PROPOSED ADDITION (SDG)" in p)
u2=next(i for i,p in enumerate(paragraphs) if p.startswith("Unit II. Process"))
u3=next(i for i,p in enumerate(paragraphs) if p.startswith("Unit III. Synchronization"))
u4=next(i for i,p in enumerate(paragraphs) if p.startswith("Unit IV. Memory"))
u5=next(i for i,p in enumerate(paragraphs) if p.startswith("Unit V. Security"))
assert u2 < ai < u3
assert u4 < sdg < u5
assert any(run.bold for run in d.paragraphs[ai].runs)
l=Document(io.BytesIO(lecture_plan(course)))
assert any("Scheduling" in cell.text for table in l.tables for row in table.rows for cell in row.cells)
assert any("90" in cell.text for table in l.tables for row in table.rows for cell in row.cells)
assert any("45" in cell.text for table in l.tables for row in table.rows for cell in row.cells)
print("PASS: app syntax, unit placement, bold additions, CO/topic plan, notional totals")
