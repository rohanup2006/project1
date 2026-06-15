import pandas as pd
import pyodbc
import streamlit as st
import plotly.express as px

# 1. Page Configuration & Theme
st.set_page_config(page_title="HighSchool Analytics Portal", layout="wide", page_icon="🎓")

# Custom CSS to make it look modern and clean
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #4e73df;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏆 HighSchool Performance Analytics Portal")
st.markdown("🔒 **Connected to Live SSMS Database Instance** | Real-time Academic Insights")
st.markdown("---")

# 2. Secure Database Fetching
@st.cache_data(ttl=60) # Caches data for 1 minute to make the app lightning fast
def get_db_data():
    conn_str = (
        r"DRIVER={ODBC Driver 17 for SQL Server};"
        r"SERVER=localhost\SQLEXPRESS;"  
        r"DATABASE=StudentMarksAnalyzerDB;"
        r"Trusted_Connection=yes;"
    )
    conn = pyodbc.connect(conn_str)
    
    # FIXED: Changed [total marks] -> total_marks and [percentage%] -> percentage_pct
    students_df = pd.read_sql("""
        SELECT r.id, r.name, r.class, r.gender, 
               m.maths, m.chemistry, m.physics, m.hindi, m.english,
               m.total_marks AS total_marks, m.percentage_pct AS percentage_pct 
        FROM student_records r 
        JOIN student_marks m ON r.id = m.student_id
    """, conn)
    
    # Fetch subject/teacher definitions
    subjects_df = pd.read_sql("SELECT * FROM subject_info", conn)
    
    conn.close()
    return students_df, subjects_df

try:
    df_students, df_subjects = get_db_data()

    # 3. Sidebar Navigation & Global Filters
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135810.png", width=100)
    st.sidebar.header("Portal Navigation")
    
    # ADDED: "🏆 Top Performers" and "👨‍🏫 Teacher Analytics" to the radio selection array as requested
    view_mode = st.sidebar.radio(
        "Go To View:", 
        [
            "🏫 School Overview", 
            "🔍 Student Search & Report Cards", 
            "🏆 Top Performers", 
            "👨‍🏫 Teacher Analytics"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Global Filters")
    selected_class = st.sidebar.selectbox("Filter by Class/Section:", ["All Classes"] + list(df_students['class'].unique()))
    
    # Apply class filter
    if selected_class != "All Classes":
        df_filtered = df_students[df_students['class'] == selected_class]
    else:
        df_filtered = df_students

    # ==========================================
    # VIEW 1: SCHOOL OVERVIEW
    # ==========================================
    if view_mode == "🏫 School Overview":
        
        # High-End Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Enrolled", len(df_filtered), delta=f"Class {selected_class}" if selected_class != "All Classes" else "All Sections")
        with col2:
            st.metric("Batch Average", f"{df_filtered['percentage_pct'].mean():.1f}%")
        with col3:
            st.metric("Highest Score", f"{df_filtered['percentage_pct'].max():.1f}%")
        with col4:
            # Pass rate assuming 40% is passing threshold
            pass_rate = (len(df_filtered[df_filtered['percentage_pct'] >= 40]) / len(df_filtered)) * 100
            st.metric("Passing Rate", f"{pass_rate:.1f}%")

        st.markdown("<br>", unsafe_allow_html=True)

        # Main Layout Split
        left_col, right_col = st.columns([3, 2])

        with left_col:
            st.subheader("📊 Performance Leaderboard")
            fig = px.bar(
                df_filtered.sort_values(by="percentage_pct", ascending=False),
                x="name", y="percentage_pct",
                color="percentage_pct",
                labels={'name': 'Student Name', 'percentage_pct': 'Final Percentage (%)'},
                color_continuous_scale=px.colors.sequential.Viridis,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)

        with right_col:
            st.subheader("📚 Subject Performance Averages")
            sub_means = df_filtered[['maths', 'chemistry', 'physics', 'hindi', 'english']].mean().reset_index()
            sub_means.columns = ['Subject', 'Average Score']
            
            fig_radar = px.line_polar(sub_means, r='Average Score', theta='Subject', line_close=True, template="plotly_white")
            fig_radar.update_traces(fill='toself')
            st.plotly_chart(fig_radar, use_container_width=True)

        st.subheader("📋 Master Student Registry Directory")
        st.dataframe(df_filtered[['id', 'name', 'class', 'gender', 'total_marks', 'percentage_pct']], use_container_width=True, hide_index=True)

    # ==========================================
    # VIEW 2: STUDENT SEARCH & REPORT CARDS
    # ==========================================
    elif view_mode == "🔍 Student Search & Report Cards":
        st.subheader("🎯 Student Report Card Generator")
        
        student_list = df_students['name'].sort_values().tolist()
        searched_student = st.selectbox("Type or select a student's name:", student_list)
        
        if searched_student:
            student_data = df_students[df_students['name'] == searched_student].iloc[0]
            
            st.markdown(f"""
                <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e3e6f0; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    <h2 style='color: #4e73df; margin-top:0;'>Official Progress Report</h2>
                    <table style='width:100%; border-bottom: 2px solid #eaecf4; padding-bottom: 15px; margin-bottom: 15px;'>
                        <tr>
                            <td><strong>Student Name:</strong> {student_data['name']}</td>
                            <td><strong>Roll Number ID:</strong> {student_data['id']}</td>
                        </tr>
                        <tr>
                            <td><strong>Assigned Class:</strong> Section {student_data['class']}</td>
                            <td><strong>Gender Profile:</strong> {student_data['gender']}</td>
                        </tr>
                    </table>
                </div>
            """, unsafe_allow_html=True)
            
            score_col, chart_col = st.columns([2, 3])
            
            with score_col:
                st.markdown("### 📝 Subject Breakdown")
                scores = pd.DataFrame({
                    "Subject": ["Mathematics", "Chemistry", "Physics", "Hindi", "English"],
                    "Marks Obtained": [student_data['maths'], student_data['chemistry'], student_data['physics'], student_data['hindi'], student_data['english']],
                    "Max Marks": [100, 100, 100, 100, 100]
                })
                st.table(scores)
                
                status = "PASS" if student_data['percentage_pct'] >= 40 else "NEEDS ATTENTION"
                st.metric(label="Final Academic Standing Status", value=f"{student_data['percentage_pct']:.1f}%", delta=status)

            with chart_col:
                st.markdown("### 📈 Visual Progress Distribution")
                fig_student = px.bar(
                    scores, x="Subject", y="Marks Obtained",
                    range_y=[0, 105], text="Marks Obtained",
                    color="Marks Obtained", color_continuous_scale="Blugrn"
                )
                fig_student.update_traces(textposition='outside')
                st.plotly_chart(fig_student, use_container_width=True)

    # ==========================================
    # VIEW 3: TOP PERFORMERS (NEW PAGE)
    # ==========================================
    elif view_mode == "🏆 Top Performers":
        st.subheader("🏆 Elite Academic Top 10 Performers")
        
        # Sort values cleanly based on your class filter dynamic configuration choice
        top10_df = df_filtered.sort_values(by="percentage_pct", ascending=False).head(10)
        
        if top10_df.empty:
            st.warning("No performance data available to sort rosters.")
        else:
            # Highlight leaderboard layout chart matching your aesthetic style blocks
            fig_top = px.bar(
                top10_df,
                x="name", y="percentage_pct",
                color="percentage_pct",
                text="percentage_pct",
                labels={'name': 'Student Name', 'percentage_pct': 'Percentage (%)'},
                color_continuous_scale="Viridis",
                template="plotly_white"
            )
            fig_top.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig_top, use_container_width=True)
            
            st.markdown("### 🥇 Merit Standing Directory")
            st.dataframe(
                top10_df[['id', 'name', 'class', 'gender', 'total_marks', 'percentage_pct']], 
                use_container_width=True, 
                hide_index=True
            )

    # ==========================================
    # VIEW 4: TEACHER ANALYTICS (NEW PAGE)
    # ==========================================
    elif view_mode == "👨‍🏫 Teacher Analytics":
        st.subheader("👨‍🏫 Teacher Assignment & Performance Breakdown")
        
        st.markdown("### 🗺️ Faculty Core Registries")
        st.dataframe(df_subjects, use_container_width=True, hide_index=True)
        st.markdown("---")
        
        if df_filtered.empty:
            st.warning("No records present to formulate performance tracking averages.")
        else:
            st.markdown(f"### 📈 Subject Class Averages Comparison Graph")
            
            # Formulating dynamic tracking blocks directly connected to your active filter scopes
            class_averages = pd.DataFrame({
                "Subject": ["Mathematics", "Chemistry", "Physics", "Hindi", "English"],
                "Average Score": [
                    df_filtered['maths'].mean(),
                    df_filtered['chemistry'].mean(),
                    df_filtered['physics'].mean(),
                    df_filtered['hindi'].mean(),
                    df_filtered['english'].mean()
                ]
            })
            
            fig_teacher = px.bar(
                class_averages,
                x="Subject", y="Average Score",
                color="Average Score",
                text="Average Score",
                color_continuous_scale="Cividis",
                template="plotly_white"
            )
            fig_teacher.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig_teacher, use_container_width=True)

except Exception as e:
    st.error(f"🚨 Critical Failure Connecting to Dashboard Components: {e}")