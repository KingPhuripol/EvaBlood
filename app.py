import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64

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
    .calculation-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
        border-left: 4px solid #3498db;
    }
    .formula {
        font-family: monospace;
        background-color: #f8f9fa;
        padding: 4px 8px;
        border-radius: 4px;
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
    stats_dict = {}
    for col in numeric_cols:
        stats_dict[col] = {
            'mean': meandata[col].mean(),
            'std': meandata[col].std(),
            'count': meandata[col].count()
        }
    
    stats_df = pd.DataFrame({
        'Test': numeric_cols,
        'Average': [stats_dict[col]['mean'] for col in numeric_cols],
        'Std Dev': [stats_dict[col]['std'] for col in numeric_cols],
        'Count': [stats_dict[col]['count'] for col in numeric_cols]
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
    
    # Store calculation details in a separate DataFrame
    calc_details = pd.DataFrame(index=meandata.index)
    
    for col in numeric_cols:
        mean_val = stats_dict[col]['mean']
        std_val = stats_dict[col]['std']
        
        meandata[f'{col}_zscore'] = (meandata[col] - mean_val) / std_val
        meandata[f'{col}_zscore'] = meandata[f'{col}_zscore'].round(2)
        
        # Store calculation details
        calc_details[f'{col}_calculation'] = meandata.apply(
            lambda row: f"Z-Score = ({row[col]} - {mean_val:.2f}) / {std_val:.2f} = {row[f'{col}_zscore']}" 
            if not pd.isna(row[col]) else "No data available", 
            axis=1
        )
    
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
        
        # Store grade explanation
        calc_details[f'{col}_grade_explanation'] = meandata.apply(
            lambda row: f"Grade '{row[f'{col}_grade']}' assigned because |{row[f'{col}_zscore']}| " +
                       (f"≤ 0.5" if row[f'{col}_grade'] == "Excellent" else
                        f"is between 0.5 and 1.0" if row[f'{col}_grade'] == "Good" else
                        f"is between 1.0 and 2.0" if row[f'{col}_grade'] == "Satisfactory" else
                        f"is between 2.0 and 3.0" if row[f'{col}_grade'] == "Unsatisfactory" else
                        f"> 3.0" if row[f'{col}_grade'] == "Serious problem" else "")
            if not pd.isna(row[f'{col}_zscore']) else "No data available for grading",
            axis=1
        )
    
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
    
    # NEW: Detailed calculation viewer section
    st.markdown('<div class="subheader-style">Detailed Calculation Viewer</div>', unsafe_allow_html=True)
    
    # Create selection widgets for Lab Code and Test
    row1, row2 = st.columns(2)
    selected_lab = row1.selectbox("Select Lab Code", options=meandata['Lab Code'].unique())
    
    test_options = [col for col in numeric_cols]
    selected_test = row2.selectbox("Select Test", options=test_options)
    
    if selected_lab and selected_test:
        lab_index = meandata[meandata['Lab Code'] == selected_lab].index[0]
        test_value = meandata.loc[lab_index, selected_test]
        z_score = meandata.loc[lab_index, f'{selected_test}_zscore']
        grade = meandata.loc[lab_index, f'{selected_test}_grade']
        
        # Get calculation details
        calculation = calc_details.loc[lab_index, f'{selected_test}_calculation']
        grade_explanation = calc_details.loc[lab_index, f'{selected_test}_grade_explanation']
        
        # Display detailed calculation
        st.markdown(f"""
        <div class="calculation-box">
            <h4>Detailed Calculation for Lab {selected_lab}, Test: {selected_test}</h4>
            
        <p><b>Raw Value:</b> {f"{test_value:.2f}" if not pd.isna(test_value) else "No data"}</p>
        <p><b>Test Statistics:</b> Mean = {stats_dict[selected_test]['mean']:.2f}, Standard Deviation = {stats_dict[selected_test]['std']:.2f}</p>
            
        <p><b>Z-Score Calculation:</b><br>
        <span class="formula">{calculation}</span></p>
            
        <p><b>Grade Determination:</b><br>
        <span class="formula">{grade_explanation}</span></p>
            
        <p><b>Final Grade:</b> {grade}</p>
        </div>
        """, unsafe_allow_html=True)
    
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
    
    # Add calculation details to download
    # Create a combined DataFrame with original data and calculation details
    download_df = meandata.copy()
    
    # Add calculation details to the download DataFrame
    for col in numeric_cols:
        download_df[f'{col}_calculation_details'] = calc_details[f'{col}_calculation']
        download_df[f'{col}_grade_explanation'] = calc_details[f'{col}_grade_explanation']
    
    # Download button
    st.download_button(
        label="📥 Download Full Analysis Report (Including Calculations)",
        data=download_df.to_csv(index=False).encode('utf-8'),
        file_name='smartlab_analysis_report.csv',
        mime='text/csv',
        use_container_width=True
    )
    
    # Generate a detailed PDF report with calculations for selected lab
    st.markdown('<div class="subheader-style">Export Detailed Calculation Report</div>', unsafe_allow_html=True)
    
    export_lab = st.selectbox("Select Lab for Detailed Report", options=meandata['Lab Code'].unique(), key="export_lab")
    
    if st.button("Generate Detailed Report for Selected Lab"):
        st.markdown(f"### Detailed Calculations for Lab: {export_lab}")
        lab_data = meandata[meandata['Lab Code'] == export_lab]
        lab_index = lab_data.index[0]
        
        for col in numeric_cols:
            test_value = lab_data.iloc[0][col]
            z_score = lab_data.iloc[0][f'{col}_zscore']
            grade = lab_data.iloc[0][f'{col}_grade']
            
            calculation = calc_details.loc[lab_index, f'{col}_calculation']
            grade_explanation = calc_details.loc[lab_index, f'{col}_grade_explanation']
            
            st.markdown(f"""
            <div class="calculation-box">
                <h4>Test: {col}</h4>
                <p><b>Raw Value:</b> {f"{test_value:.2f}" if not pd.isna(test_value) else "No data"}</p>
                <p><b>Z-Score Calculation:</b><br>
                <span class="formula">{calculation}</span></p>
                <p><b>Grade Determination:</b><br>
                <span class="formula">{grade_explanation}</span></p>
                <p><b>Final Grade:</b> {grade}</p>
            </div>
            """, unsafe_allow_html=True)

else:
    st.info("ℹ️ Please upload a CSV file to begin analysis. The app will calculate z-scores and grades for all numeric test values.")
