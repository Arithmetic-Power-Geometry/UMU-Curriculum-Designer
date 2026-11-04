"""Regression tests for unit matching and exported Word documents."""
from io import BytesIO
from docx import Document
from print_engine import unit_for, mentioned_unit, short_unit, syllabus, lecture_plan

UNITS=[
    {"name":"Unit I. Introduction","topics":"OS overview","hours":9},
    {"name":"Unit II. Processes","topics":"FCFS and SJF","hours":9},
    {"name":"Unit III. Memory","topics":"Memory","hours":9},
]
def course(suggestions):
    return dict(programme="MCA",faculty="Test",department="Computing",semester="I",
                name="Operating System",code="MCA-CC101",credits=3,weeks=9,lecture=3,
                cos=["OS overview","Processes","Memory"],units=UNITS,suggestions=suggestions,
                status="Faculty draft")
def test_explicit_conflict():
    s={"unit":"Unit I. Introduction","text":"Unit II: Verify FCFS and SJF","area":"AI","include":True}
    assert mentioned_unit(s,UNITS)=="Unit II. Processes"
    assert unit_for(s,UNITS)==""  # Must never be inserted into Unit I.
    doc=Document(BytesIO(syllabus(course([s]))))
    text="\n".join(p.text for p in doc.paragraphs)
    assert "Additions awaiting unit selection" in text
def test_legacy_target():
    s={"text":"Unit II: Verify FCFS and SJF","area":"AI","include":True}
    assert unit_for(s,UNITS)=="Unit II. Processes"
    doc=Document(BytesIO(syllabus(course([s]))))
    text="\n".join(p.text for p in doc.paragraphs)
    assert text.index("Unit II. Processes (") < text.index("PROPOSED ADDITION (AI)")
def test_compact_table():
    assert short_unit("Unit II. Processes")=="Unit II"
    doc=Document(BytesIO(lecture_plan(course([]))))
    assert doc.tables
    assert any(cell.text=="Unit II" for table in doc.tables for row in table.rows for cell in row.cells)
if __name__=="__main__":
    test_explicit_conflict()
    test_legacy_target()
    test_compact_table()
    print("All curriculum regression tests passed.")
