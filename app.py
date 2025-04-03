import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Page configuration
st.set_page_config(
    page_title="SmartLab Data Analysis",
    page_icon=":microscope:",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .header-style {
        font-size: 24px;
        font-weight: bold;
        color: #2e86c1;
        margin-bottom: 20px;
    }
    .subheader-style {
        font-size: 20px;
        font-weight: bold;
        color: #3498db;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .info-box {
        background-color: #eaf2f8;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
    }
    .stDataFrame {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title(':microscope: SmartLab Data Analysis')
st.markdown('<div class="header-style">Comprehensive Laboratory Test Analysis with Z-Scores and Grading</div>', unsafe_allow_html=True)

# File upload section
with st.expander("📁 Upload Your Data", expanded=True):
    uploaded_file = st.file_uploader("Choose a CSV file containing lab test results", type=["csv"])
    st.markdown("""
    <div class="info-box">
        <b>File Requirements:</b><br>
        - CSV format with lab test results<br>
        - Should contain numeric test values<br>
        - Should include 'Lab Code' column for identification<br>
        - Zero values will be treated as missing data
    </div>
    """, unsafe_allow_html=True)

if uploaded_file is not None:
    # Read and process data
    meandata = pd.read_csv(uploaded_file)
    meandata = meandata.replace(0, np.nan)
    
    # Select numeric columns
    numeric_cols = meandata.select_dtypes(include=np.number).columns
    if 'Lab Code' in numeric_cols:
        numeric_cols = numeric_cols.drop(['Lab Code'])
    
    # Calculation explanations
    st.markdown('<div class="subheader-style">Calculation Methodology</div>', unsafe_allow_html=True)
    
    with st.expander("ℹ️ How the Analysis Works"):
        st.markdown("""
        <div class="info-box">
            <h4>Z-Score Calculation:</h4>
            <p>Z-scores measure how many standard deviations a value is from the mean.</p>
            <p><b>Formula:</b> <code>z = (x - μ) / σ</code></p>
            <p>Where:<br>
            - <code>x</code> = individual test value<br>
            - <code>μ</code> = mean of all values for that test<br>
            - <code>σ</code> = standard deviation of all values for that test</p>
            
        <h4>Grading System:</h4>
        <p>Grades are assigned based on the absolute z-score:</p>
        <ul>
            <li><b>Excellent:</b> |z| ≤ 0.5 (very close to mean)</li>
            <li><b>Good:</b> 0.5 < |z| ≤ 1 (moderately close to mean)</li>
            <li><b>Satisfactory:</b> 1 < |z| ≤ 2 (somewhat far from mean)</li>
            <li><b>Unsatisfactory:</b> 2 < |z| ≤ 3 (far from mean)</li>
            <li><b>Serious problem:</b> |z| > 3 (very far from mean)</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Calculate statistics before processing
    stats_df = pd.DataFrame({
        'Test': numeric_cols,
        'Average': [meandata[col].mean() for col in numeric_cols],
        'Std Dev': [meandata[col].std() for col in numeric_cols],
        'Count': [meandata[col].count() for col in numeric_cols]
    }).round(2)
    
    # Show statistics
    st.markdown('<div class="subheader-style">Test Statistics</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, row in stats_df.iterrows():
        with cols[i % 4]:
            st.markdown(f"""
            <div class="metric-box">
                <b>{row['Test']}</b><br>
                Avg: {row['Average']}<br>
                SD: {row['Std Dev']}<br>
                N: {row['Count']}
            </div>
            """, unsafe_allow_html=True)
    
    # Process data - Modified column order here
    new_columns = ['Lab Code', 'รายงานผล']  # Moved these to the front
    
    for col in numeric_cols:
        new_columns.extend([col, f'{col}_zscore', f'{col}_grade'])
    
    for col in numeric_cols:
        meandata[f'{col}_zscore'] = (meandata[col] - meandata[col].mean()) / meandata[col].std()
        meandata[f'{col}_zscore'] = meandata[f'{col}_zscore'].round(2)
    
    def assign_grade(zscore):
        if pd.isna(zscore):
            return "No data"
        zscore = abs(zscore)
        if zscore <= 0.5:
            return "Excellent"
        elif zscore <= 1:
            return "Good"
        elif zscore <= 2:
            return "Satisfactory"
        elif zscore <= 3:
            return "Unsatisfactory"
        else:
            return "Serious problem"
    
    for col in numeric_cols:
        meandata[f'{col}_grade'] = meandata[f'{col}_zscore'].apply(assign_grade)
    
    meandata = meandata[new_columns]
    
    # Display results
    st.markdown('<div class="subheader-style">Processed Results</div>', unsafe_allow_html=True)
    
    # Apply styling
    def color_grade(val):
        color_map = {
            'Excellent': 'background-color: #2ecc71; color: white;',
            'Good': 'background-color: #3498db; color: white;',
            'Satisfactory': 'background-color: #f39c12; color: white;',
            'Unsatisfactory': 'background-color: #e74c3c; color: white;',
            'Serious problem': 'background-color: #c0392b; color: white;',
            'No data': 'background-color: #95a5a6; color: white;'
        }
        return color_map.get(val, '')
    
    # Apply styling to grade columns
    grade_columns = [col for col in meandata.columns if '_grade' in col]
    styled_df = meandata.style.applymap(color_grade, subset=grade_columns)
    
    # Format numeric columns
    numeric_format = {col: "{:.2f}" for col in numeric_cols}
    zscore_format = {col: "{:.2f}" for col in meandata.columns if '_zscore' in col}
    styled_df = styled_df.format({**numeric_format, **zscore_format})
    
    st.dataframe(styled_df, height=400, use_container_width=True)
    
    # Visualization
    st.markdown('<div class="subheader-style">Visual Analysis</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Grade Distribution", "Z-Score Distribution"])
    
    with tab1:
        grade_cols = [col for col in meandata.columns if '_grade' in col]
        grade_data = meandata[['Lab Code'] + grade_cols].melt(id_vars='Lab Code', var_name='Test', value_name='Grade')
        grade_counts = grade_data.groupby(['Test', 'Grade']).size().reset_index(name='Count')
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=grade_counts, x='Test', y='Count', hue='Grade', 
                   palette={'Excellent':'#2ecc71', 'Good':'#3498db', 'Satisfactory':'#f39c12', 
                           'Unsatisfactory':'#e74c3c', 'Serious problem':'#c0392b', 'No data':'#95a5a6'})
        plt.xticks(rotation=45)
        plt.title('Grade Distribution by Test')
        st.pyplot(fig)
    
    with tab2:
        zscore_cols = [col for col in meandata.columns if '_zscore' in col]
        zscore_data = meandata[['Lab Code'] + zscore_cols].melt(id_vars='Lab Code', var_name='Test', value_name='Z-Score')
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=zscore_data, x='Test', y='Z-Score')
        plt.xticks(rotation=45)
        plt.title('Z-Score Distribution by Test')
        st.pyplot(fig)
    
    # Download button
    st.download_button(
        label="📥 Download Full Analysis Report",
        data=meandata.to_csv(index=False).encode('utf-8'),
        file_name='smartlab_analysis_report.csv',
        mime='text/csv',
        use_container_width=True
    )

else:
    st.info("ℹ️ Please upload a CSV file to begin analysis. The app will calculate z-scores and grades for all numeric test values.")
