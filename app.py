import json
import streamlit as st
from print_engine import syllabus, lecture_plan, weekly_plan, unit_for

st.set_page_config(page_title="UMU Curriculum Designer", layout="wide")
st.title("USHA MARTIN UNIVERSITY, RANCHI")
st.subheader("Curriculum Design & Revision")
st.caption("Faculty workspace • Review proposed additions before using revised documents.")
def empty():
    return {"programme":"","faculty":"Dr. Mohammad Amir Khusru Akhtar","department":"Computing and IT","semester":"","name":"","code":"","credits":3,"lecture":3,"weeks":15,"cos":[""],"units":[{"name":"Unit I","topics":"","hours":9}],"suggestions":[],"status":"Faculty draft"}
if "course" not in st.session_state: st.session_state.course=empty()
if "page" not in st.session_state: st.session_state.page=0
c=st.session_state.course
with st.sidebar:
    st.write("**How to use:** Enter course information, COs and original units. Review additions and select their unit. Check the lecture plan, then download Word files. Use Next and Previous to navigate.")
    uploaded=st.file_uploader("Upload saved course JSON",type=["json"])
    if st.button("Load JSON",disabled=uploaded is None):
        try:
            incoming=json.load(uploaded)
            if not isinstance(incoming.get("units"),list): raise ValueError("Units missing")
            st.session_state.course={**empty(),**incoming}
            st.session_state.page=0
            st.rerun()
        except (ValueError,TypeError) as exc: st.error(str(exc))
    if st.button("New course"):
        st.session_state.course=empty()
        st.session_state.page=0
        st.rerun()
names=["Course information","Course outcomes and units","AI, IKS and SDG additions","Lecture plan","Review and downloads"]
step=st.session_state.page
st.progress((step+1)/5,text=f"Step {step+1} of 5: {names[step]}")
if step==0:
    for key,label in [("programme","Programme"),("faculty","Faculty name"),("department","Faculty/Department"),("semester","Semester"),("name","Course title"),("code","Course code")]:
        c[key]=st.text_input(label,value=str(c.get(key,"")),help="Enter the approved programme or course information.")
    for key,label in [("credits","Credits"),("lecture","Lecture hours per week"),("weeks","Teaching weeks")]:
        c[key]=st.number_input(label,min_value=1,max_value=40,value=int(c[key]))
elif step==1:
    st.write("Enter each original course outcome and each unit without changing the approved wording.")
    for i in range(len(c["cos"])):
        c["cos"][i]=st.text_area(f"CO{i+1}",value=c["cos"][i])
    if st.button("Add CO"): c["cos"].append("");st.rerun()
    for i,u in enumerate(c["units"]):
        with st.expander(f"Unit {i+1}",expanded=True):
            u["name"]=st.text_input("Unit heading",value=u["name"],key=f"unitname{i}")
            u["topics"]=st.text_area("Original syllabus topics",value=u["topics"],key=f"topics{i}")
            u["hours"]=st.number_input("Lecture hours",min_value=1,max_value=200,value=int(u["hours"]),key=f"hours{i}")
    if st.button("Add unit"): c["units"].append({"name":f"Unit {len(c['units'])+1}","topics":"","hours":9});st.rerun()
elif step==2:
    st.write("Suggestions are optional. Include only verified additions relevant to a selected unit.")
    if st.button("Create editable example suggestions"):
        c["suggestions"]=[{"area":x,"text":"","source":"","include":False,"unit":c["units"][0]["name"]} for x in ("AI","IKS","SDG")]
        st.rerun()
    for i,s in enumerate(c["suggestions"]):
        st.markdown("**"+s.get("area","Addition")+"**")
        s["text"]=st.text_area("Proposed addition",value=s.get("text",""),key=f"add{i}")
        s["source"]=st.text_input("Verified reference",value=s.get("source",""),key=f"source{i}")
        options=[u["name"] for u in c["units"]]
        initial=s.get("unit") or unit_for(s,c["units"]) or options[0]
        s["unit"]=st.selectbox("Place under unit",options,index=options.index(initial) if initial in options else 0,key=f"select{i}")
        s["include"]=st.checkbox("Include after review",value=bool(s.get("include")),key=f"include{i}")
elif step==3:
    st.dataframe(weekly_plan(c),use_container_width=True,hide_index=True)
    total=sum(int(u["hours"]) for u in c["units"])
    scheduled=int(c["weeks"])*int(c["lecture"])
    st.write(f"Unit hours: {total}; scheduled contact hours: {scheduled}; illustrative notional hours: {30*int(c['credits'])}.")
    if total!=scheduled:st.warning("Unit hours and scheduled contact hours do not match.")
    st.caption("CO mappings and the 30-hours-per-credit illustration require faculty verification and University authorization.")
else:
    st.write("Review the original syllabus and accepted additions before downloading.")
    c["status"]=st.selectbox("Review status",["Faculty draft","Submitted for review","Reviewed"],index=["Faculty draft","Submitted for review","Reviewed"].index(c["status"]) if c.get("status") in ["Faculty draft","Submitted for review","Reviewed"] else 0)
    st.download_button("Download revised syllabus (Word)",syllabus(c),file_name="revised_syllabus.docx")
    st.download_button("Download lecture plan (Word)",lecture_plan(c),file_name="lecture_plan.docx")
    st.download_button("Save course JSON",json.dumps(c,indent=2),file_name="course.json")
a,b=st.columns(2)
if a.button("Previous",disabled=step==0):st.session_state.page-=1;st.rerun()
if b.button("Next",disabled=step==4):st.session_state.page+=1;st.rerun()
