import streamlit as st
import json
from pathlib import Path

DATA_FILE = Path("students.json")


def load_data() -> list[dict]:
    """Load student data from JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_data(students: list[dict]) -> None:
    """Save student data to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=2)


def find_student_by_roll(students: list[dict], roll_no: str) -> dict | None:
    """Find a student by roll number."""
    for student in students:
        if student["roll_no"] == roll_no:
            return student
    return None


def add_student(students: list[dict], name: str, roll_no: str, marks: float, department: str) -> tuple[bool, str]:
    """Add a new student to the records."""
    if not name or not roll_no or not department:
        return False, "All fields are required!"
    
    if find_student_by_roll(students, roll_no):
        return False, f"Student with Roll No '{roll_no}' already exists!"
    
    if marks < 0 or marks > 100:
        return False, "Marks must be between 0 and 100!"
    
    students.append({
        "name": name,
        "roll_no": roll_no,
        "marks": marks,
        "department": department
    })
    save_data(students)
    return True, f"Student '{name}' added successfully!"


def update_student(students: list[dict], roll_no: str, name: str, marks: float, department: str) -> tuple[bool, str]:
    """Update an existing student's information."""
    for i, student in enumerate(students):
        if student["roll_no"] == roll_no:
            if marks < 0 or marks > 100:
                return False, "Marks must be between 0 and 100!"
            
            students[i] = {
                "name": name,
                "roll_no": roll_no,
                "marks": marks,
                "department": department
            }
            save_data(students)
            return True, f"Student '{name}' updated successfully!"
    
    return False, f"Student with Roll No '{roll_no}' not found!"


def delete_student(students: list[dict], roll_no: str) -> tuple[bool, str]:
    """Delete a student from the records."""
    for i, student in enumerate(students):
        if student["roll_no"] == roll_no:
            name = student["name"]
            students.pop(i)
            save_data(students)
            return True, f"Student '{name}' deleted successfully!"
    
    return False, f"Student with Roll No '{roll_no}' not found!"


def get_analytics(students: list[dict]) -> dict:
    """Calculate analytics for the student records."""
    if not students:
        return {
            "total": 0,
            "average": 0,
            "topper": None,
            "departments": {}
        }
    
    total = len(students)
    average = sum(s["marks"] for s in students) / total
    topper = max(students, key=lambda x: x["marks"])
    
    departments = {}
    for student in students:
        dept = student["department"]
        if dept not in departments:
            departments[dept] = 0
        departments[dept] += 1
    
    return {
        "total": total,
        "average": round(average, 2),
        "topper": topper,
        "departments": departments
    }


def navigate_to(page_name: str):
    st.session_state.page = page_name


def safe_rerun():
    try:
        st.experimental_rerun()
    except Exception:
        pass


def page_dashboard():
    """Main dashboard page with quick actions."""
    st.markdown("""
    <div style="color: #e2e8f0; margin-bottom: 18px;">
        <h1 style="margin: 0; color: #ffffff;">Dashboard</h1>
        <p style="margin: 8px 0 0 0; color: #94a3b8;">Manage students, analytics, and actions from a single dark dashboard.</p>
    </div>
    """, unsafe_allow_html=True)

    students = load_data()
    analytics = get_analytics(students)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Students", value=analytics["total"])
    with col2:
        st.metric(label="Average Marks", value=f"{analytics['average']:.2f}")
    with col3:
        st.metric(label="Highest Marks", value=f"{analytics['topper']['marks']:.1f}" if analytics["topper"] else "N/A")

    st.markdown("---")

    st.markdown("### Quick Actions")
    action_cols = st.columns(3)
    with action_cols[0]:
        if st.button("Add Student", key="dashboard_add_student", use_container_width=True):
            navigate_to("Add Student")
    with action_cols[1]:
        if st.button("Update Student", key="dashboard_update_student", use_container_width=True):
            navigate_to("Update Student")
    with action_cols[2]:
        if st.button("Search Student", key="dashboard_search_student", use_container_width=True):
            navigate_to("Search Student")

    st.markdown("---")

    if analytics["departments"]:
        st.subheader("Students by Department")
        st.dataframe(
            [{"Department": dept, "Count": count} for dept, count in analytics["departments"].items()],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No department-level analytics available yet.")


def page_add_student():
    """Page for adding a new student."""
    st.markdown("""
    <div style="text-align: left; margin-bottom: 18px;">
        <h1>Add New Student</h1>
        <p style="font-size: 1.05em; color: #cbd5e1;">Fill in the student information and save it to the records.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    students = load_data()
    
    with st.form("add_student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Student Name", placeholder="Enter full name")
            roll_no = st.text_input("Roll Number", placeholder="Enter roll number")
        
        with col2:
            marks = st.number_input("Marks", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
            department = st.selectbox(
                "Department",
                options=["CSE", "CE", "IT", "Mechanical"]
            )
        
        submitted = st.form_submit_button("Add Student", use_container_width=True)
        
        if submitted:
            success, message = add_student(students, name, roll_no, marks, department)
            if success:
                st.success(message)
            else:
                st.error(message)


def page_view_students():
    """Page for viewing all students."""
    st.markdown("""
    <div style="text-align: left; margin-bottom: 18px;">
        <h1>View All Students</h1>
        <p style="font-size: 1.05em; color: #cbd5e1; margin-top: 8px;">Browse the complete student record list.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    students = load_data()

    if not students:
        st.info("No students found. Add new records from the dashboard.")
        return

    st.dataframe(
        students,
        use_container_width=True,
        column_config={
            "name": st.column_config.TextColumn("Name", width="medium"),
            "roll_no": st.column_config.TextColumn("Roll No", width="small"),
            "marks": st.column_config.ProgressColumn("Marks", min_value=0, max_value=100),
            "department": st.column_config.TextColumn("Department", width="medium")
        },
        hide_index=True
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Records", value=len(students))
    with col2:
        avg = sum(s["marks"] for s in students) / len(students)
        st.metric(label="Average Marks", value=f"{avg:.2f}")
    with col3:
        highest = max(s["marks"] for s in students)
        st.metric(label="Highest Marks", value=f"{highest:.1f}")


def page_search_student():
    """Page for searching a student by roll number."""
    st.markdown("""
    <div style="text-align: left; margin-bottom: 18px;">
        <h1>Search Student</h1>
        <p style="font-size: 1.05em; color: #cbd5e1; margin-top: 8px;">Search for a student by roll number and view their profile.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    students = load_data()

    col1, col2 = st.columns([3, 1])
    with col1:
        roll_no = st.text_input("Enter Roll Number to Search", placeholder="e.g., CS101")

    with col2:
        search_button = st.button("Search", use_container_width=True)

    if search_button:
        if not roll_no:
            st.warning("Please enter a roll number.")
            return

        student = find_student_by_roll(students, roll_no)

        if student:
            st.success("Student found.")
            st.markdown("---")
            st.markdown(f"""
            <div style="background: #0f172a; border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 18px; padding: 26px; box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35);">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <p style="color: #94a3b8; font-weight: 700; font-size: 0.9em; margin-bottom: 6px;">Name</p>
                        <h3 style="margin: 0; color: #e2e8f0;">{student['name']}</h3>
                    </div>
                    <div>
                        <p style="color: #94a3b8; font-weight: 700; font-size: 0.9em; margin-bottom: 6px;">Roll Number</p>
                        <h3 style="margin: 0; color: #e2e8f0;">{student['roll_no']}</h3>
                    </div>
                    <div>
                        <p style="color: #94a3b8; font-weight: 700; font-size: 0.9em; margin-bottom: 6px;">Marks</p>
                        <h3 style="margin: 0; color: #e2e8f0;">{student['marks']}</h3>
                    </div>
                    <div>
                        <p style="color: #94a3b8; font-weight: 700; font-size: 0.9em; margin-bottom: 6px;">Department</p>
                        <h3 style="margin: 0; color: #e2e8f0;">{student['department']}</h3>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"No student found with Roll No '{roll_no}'.")


def page_update_student():
    """Page for updating a student's information."""
    st.markdown("""
    <div style="text-align: left; margin-bottom: 18px;">
        <h1>Update Student</h1>
        <p style="font-size: 1.05em; color: #cbd5e1; margin-top: 8px;">Change any student details and keep the records accurate.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    students = load_data()

    if not students:
        st.info("No students found. Add some students from the dashboard.")
        return

    roll_numbers = [s["roll_no"] for s in students]
    selected_roll = st.selectbox("Select Student by Roll Number", options=roll_numbers)

    student = find_student_by_roll(students, selected_roll)

    if student:
        st.markdown("---")

        with st.form("update_student_form"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Student Name", value=student["name"])
                st.text_input("Roll Number", value=student["roll_no"], disabled=True)

            with col2:
                marks = st.number_input("Marks", min_value=0.0, max_value=100.0, value=float(student["marks"]), step=0.5)
                departments = ["CSE", "CE", "IT", "Mechanical"]
                department = st.selectbox(
                    "Department",
                    options=departments,
                    index=departments.index(student["department"]) if student["department"] in departments else 0
                )

            submitted = st.form_submit_button("Update Student", use_container_width=True)

            if submitted:
                success, message = update_student(students, selected_roll, name, marks, department)
                if success:
                    st.success(message)
                else:
                    st.error(message)


def page_delete_student():
    """Page for deleting a student."""
    st.markdown("""
    <div style="text-align: left; margin-bottom: 18px;">
        <h1>Delete Student</h1>
        <p style="font-size: 1.05em; color: #cbd5e1; margin-top: 8px;">Remove a student record from the system when needed.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    students = load_data()

    if not students:
        st.info("No students found. Add new records from the dashboard.")
        return

    roll_numbers = [s["roll_no"] for s in students]
    selected_roll = st.selectbox("Select Student to Delete", options=roll_numbers)

    student = find_student_by_roll(students, selected_roll)

    if student:
        st.markdown("---")

        st.warning("You are about to delete the following student. This action cannot be undone.")

        st.markdown(f"""
        <div style="background: #0f172a; border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 18px; padding: 26px; box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35); margin-bottom: 20px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <p style="color: #94a3b8; font-weight: 700; font-size: 0.85em; margin-bottom: 6px;">Name</p>
                    <h3 style="margin: 0; color: #e2e8f0;">{student['name']}</h3>
                </div>
                <div>
                    <p style="color: #94a3b8; font-weight: 700; font-size: 0.85em; margin-bottom: 6px;">Roll No</p>
                    <h3 style="margin: 0; color: #e2e8f0;">{student['roll_no']}</h3>
                </div>
                <div>
                    <p style="color: #94a3b8; font-weight: 700; font-size: 0.85em; margin-bottom: 6px;">Marks</p>
                    <h3 style="margin: 0; color: #e2e8f0;">{student['marks']}</h3>
                </div>
                <div>
                    <p style="color: #94a3b8; font-weight: 700; font-size: 0.85em; margin-bottom: 6px;">Department</p>
                    <h3 style="margin: 0; color: #e2e8f0;">{student['department']}</h3>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Delete", use_container_width=True, type="primary"):
                success, message = delete_student(students, selected_roll)
                if success:
                    st.success(message)
                    st.session_state.page = "Dashboard"
                    safe_rerun()
                else:
                    st.error(message)

        with col2:
            if st.button("Cancel", use_container_width=True):
                st.info("Delete action canceled.")


def page_analytics():
    """Page for displaying analytics dashboard."""
    st.markdown("""
    <div style="text-align: left; margin-bottom: 18px;">
        <h1>Analytics Overview</h1>
        <p style="font-size: 1.05em; color: #cbd5e1; margin-top: 8px;">Detailed metrics and insights for the current student record set.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    students = load_data()
    analytics = get_analytics(students)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Students", value=analytics["total"])
    with col2:
        st.metric(label="Average Marks", value=f"{analytics['average']:.2f}")
    with col3:
        st.metric(label="Highest Marks", value=f"{analytics['topper']['marks']:.1f}" if analytics["topper"] else "N/A")

    st.markdown("---")

    if analytics["topper"]:
        topper = analytics["topper"]
        percentage = (topper["marks"] / 100) * 100
        st.markdown(f"""
        <div style="background: #0f172a; border: 1px solid rgba(148, 163, 184, 0.16); border-radius: 18px; padding: 28px; box-shadow: 0 16px 50px rgba(0, 0, 0, 0.35);">
            <h2 style="margin-top: 0; color: #e2e8f0;">Top Performer</h2>
            <div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; margin-bottom: 24px;">
                <div>
                    <p style="margin: 0 0 6px 0; color: #94a3b8; font-size: 0.85em;">Name</p>
                    <strong style="color: #e2e8f0;">{topper['name']}</strong>
                </div>
                <div>
                    <p style="margin: 0 0 6px 0; color: #94a3b8; font-size: 0.85em;">Marks</p>
                    <strong style="color: #e2e8f0;">{topper['marks']}/100</strong>
                </div>
                <div>
                    <p style="margin: 0 0 6px 0; color: #94a3b8; font-size: 0.85em;">Department</p>
                    <strong style="color: #e2e8f0;">{topper['department']}</strong>
                </div>
            </div>
            <div style="background: rgba(148, 163, 184, 0.15); border-radius: 12px; height: 32px; overflow: hidden;">
                <div style="width: {percentage}%; height: 100%; background: #2563eb; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #ffffff; font-weight: 600;">{percentage:.0f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if analytics["departments"]:
        st.subheader("Students by Department")
        dept_data = [{"Department": dept, "Count": count} for dept, count in analytics["departments"].items()]
        st.dataframe(dept_data, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.line_chart(data={dept: count for dept, count in analytics["departments"].items()})
    else:
        st.info("No department-wise analytics available.")


def add_custom_css():
    """Add custom dark theme CSS styling."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        * {
            font-family: 'Inter', sans-serif;
        }

        body {
            background: #080b16;
        }

        .stApp {
            background: #080b16;
            color: #e2e8f0;
        }

        section[data-testid="stSidebar"] {
            background: #0c1226 !important;
            color: #cbd5e1 !important;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label {
            color: #cbd5e1 !important;
        }

        .stSidebar .css-1d391kg {
            background: transparent !important;
        }

        section[data-testid="stSidebar"] .stButton > button {
            width: 100% !important;
            text-align: left !important;
            background: #111827 !important;
            color: #e2e8f0 !important;
            border: 1px solid rgba(148, 163, 184, 0.18) !important;
            border-radius: 12px !important;
            padding: 12px 18px !important;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.25) !important;
            transition: background 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease !important;
            cursor: pointer !important;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(37, 99, 235, 0.15) !important;
            transform: translateX(1px) !important;
            box-shadow: 0 12px 24px rgba(37, 99, 235, 0.22) !important;
        }

        .stMetric,
        .card,
        .stForm,
        .stDataFrame,
        .stBlock {
            background: #0f172a !important;
            border: 1px solid rgba(148, 163, 184, 0.12) !important;
            border-radius: 16px !important;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45) !important;
        }

        .stButton > button {
            background: #2563eb !important;
            color: #ffffff !important;
            border: 1px solid rgba(37, 99, 235, 0.35) !important;
            border-radius: 12px !important;
            padding: 12px 22px !important;
            font-weight: 600 !important;
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.25) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }

        .stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 14px 30px rgba(37, 99, 235, 0.35) !important;
        }

        .stButton > button:active {
            transform: translateY(0) !important;
        }

        .stForm {
            padding: 24px !important;
        }

        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            border: 1px solid rgba(148, 163, 184, 0.18) !important;
            border-radius: 10px !important;
            padding: 12px !important;
            background: #111827 !important;
            color: #e2e8f0 !important;
        }

        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.18) !important;
        }

        .stSuccess,
        .stError,
        .stWarning,
        .stInfo {
            border-radius: 14px !important;
            padding: 18px !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35) !important;
        }

        .stSuccess {
            background: #0f2f1d !important;
            color: #a7f3d0 !important;
            border: 1px solid rgba(34, 197, 94, 0.25) !important;
        }

        .stError {
            background: #3f1d1d !important;
            color: #fecaca !important;
            border: 1px solid rgba(248, 113, 113, 0.25) !important;
        }

        .stWarning {
            background: #352c0b !important;
            color: #facc15 !important;
            border: 1px solid rgba(234, 179, 8, 0.25) !important;
        }

        .stInfo {
            background: #0f172a !important;
            color: #bfdbfe !important;
            border: 1px solid rgba(96, 165, 250, 0.25) !important;
        }

        h1, h2, h3, p, span, label {
            color: #e2e8f0 !important;
        }

        hr {
            border: none !important;
            height: 1px !important;
            background: rgba(148, 163, 184, 0.15) !important;
            margin: 24px 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Student Record Management",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    add_custom_css()

    st.sidebar.title("Student Records")
    st.sidebar.markdown("---")

    menu_options = {
        "Dashboard": page_dashboard,
        "Analytics Overview": page_analytics,
        "Add Student": page_add_student,
        "View Students": page_view_students,
        "Search Student": page_search_student,
        "Update Student": page_update_student,
        "Delete Student": page_delete_student
    }

    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"

    st.sidebar.markdown("### Navigation")
    for option in menu_options:
        if st.sidebar.button(option, key=f"nav_{option}", use_container_width=True):
            st.session_state.page = option

    st.sidebar.markdown(f"**Current page:** {st.session_state.page}")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Stats")
    students = load_data()

    st.sidebar.metric("Total Students", len(students))

    if students:
        avg_marks = sum(s["marks"] for s in students) / len(students)
        st.sidebar.metric("Average Marks", f"{avg_marks:.2f}")

        top_marks = max(s["marks"] for s in students)
        st.sidebar.metric("Highest Marks", f"{top_marks:.1f}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("<div style='text-align:center; color:#94a3b8;'>Managed with Streamlit</div>", unsafe_allow_html=True)

    current_page = st.session_state.page
    if current_page not in menu_options:
        current_page = "Dashboard"
        st.session_state.page = current_page

    menu_options[current_page]()


if __name__ == "__main__":
    main()
