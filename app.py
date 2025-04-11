import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import base64
from io import StringIO

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

# Function to split CSV by Model code
def split_csv_by_model_code(df, output_folder="split_by_model_code"):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get unique Model codes
    unique_model_codes = df['Model code'].unique()
    model_dfs = {}
    
    # Split data by Model code
    for model_code in unique_model_codes:
        filtered_df = df[df['Model code'] == model_code]
        model_dfs[model_code] = filtered_df
        
        # Save to CSV with enhanced feedback
        output_filename = f"BloodData_Model_{model_code}.csv"
        output_path = os.path.join(output_folder, output_filename)
        filtered_df.to_csv(output_path, index=False)
        
        # Display a nice confirmation for each saved file with styled message
        st.markdown(f"""
        <div style="margin-bottom:8px; padding:8px 12px; border-radius:6px; background-color:#E8F4FD; 
                    border-left:3px solid #3498db; display:flex; align-items:center;">
            <span style="color:#2874A6; font-size:16px; margin-right:10px;">💾</span>
            <div>
                <span style="font-weight:600; color:#2C3E50;">{output_filename}</span>
                <span style="margin-left:8px; color:#5D6D7E; font-size:13px;">({len(filtered_df)} records saved)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    return model_dfs, unique_model_codes

# File upload section
with st.expander("📁 Upload Your Data", expanded=True):
    uploaded_file = st.file_uploader("Choose a CSV file containing lab test results", type=["csv"])
    st.markdown("""
    <div class="info-box">
        <b>File Requirements:</b><br>
        - CSV format with lab test results<br>
        - Should contain numeric test values<br>
        - Should include 'Lab Code' and 'Model code' columns<br>
        - Zero values will be treated as missing data
    </div>
    """, unsafe_allow_html=True)

if uploaded_file is not None:
    # Read and process data
    meandata = pd.read_csv(uploaded_file)
    meandata = meandata.replace(0, np.nan)
    
    # Split data by Model code
    st.markdown('<div class="subheader-style">Split Data by Model Code</div>', unsafe_allow_html=True)
    
    # Display file info before splitting
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", f"{len(meandata)}", delta=None)
    with col2:
        st.metric("Unique Model Codes", f"{meandata['Model code'].nunique()}", delta=None)
    with col3:
        st.metric("Data Columns", f"{len(meandata.columns)}", delta=None)
    
    # Add progress indicator for splitting operation
    with st.spinner("Splitting data by model code..."):
        model_dfs, unique_model_codes = split_csv_by_model_code(meandata)
    
    # Show success message with enhanced styling
    st.markdown(f"""
    <div style="background-color:#E9F7EF; padding:15px; border-radius:10px; border-left:5px solid #2ECC71; margin:20px 0px;">
        <h4 style="color:#27AE60; margin-top:0;">✅ Data Successfully Split!</h4>
        <p>Your data has been split into <b>{len(unique_model_codes)}</b> separate files based on Model code.</p>
        <p>Each file has been saved and is available for individual analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show model code information in a more visual way
    st.markdown('<div style="margin-top:10px; margin-bottom:15px;"><b>Available Model Codes:</b></div>', unsafe_allow_html=True)
    
    # Create a grid of model code buttons with record counts
    model_buttons = []
    cols = st.columns(4)  # Adjust number of columns as needed
    for i, model_code in enumerate(unique_model_codes):
        with cols[i % 4]:
            record_count = len(model_dfs[model_code])
            st.markdown(f"""
            <div style="background-color:#F8F9F9; padding:10px; border-radius:8px; margin-bottom:10px; 
                        border:1px solid #D5DBDB; text-align:center;">
                <div style="font-weight:bold; font-size:16px; color:#2874A6;">Model {model_code}</div>
                <div style="color:#566573; font-size:14px;">{record_count} records</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Allow user to select a Model code for analysis with enhanced select box
    st.markdown("""
    <div style="background-color:#EBF5FB; padding:15px; border-radius:8px; margin-top:20px; margin-bottom:15px;">
        <p style="margin:0; font-weight:bold;">Select a model code to analyze its data:</p>
    </div>
    """, unsafe_allow_html=True)
    
    selected_model = st.selectbox(
        "Choose Model Code",
        options=unique_model_codes,
        format_func=lambda x: f"Model {x} ({len(model_dfs[x])} records)",
        index=0,
        key="model_selector"
    )
    
    # Add a divider before proceeding with the analysis
    st.markdown("<hr style='margin:30px 0px; border:none; height:1px; background-color:#D5D8DC;'>", unsafe_allow_html=True)
    
    # Use the selected model's data for further analysis
    meandata = model_dfs[selected_model]
    
    # Select numeric columns, excluding non-test columns
    non_test_columns = ['Lab Code', 'Brand code', 'Model code']
    numeric_cols = meandata.select_dtypes(include=np.number).columns
    numeric_cols = [col for col in numeric_cols if col not in non_test_columns]
    
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
    
    # Process data - Include original columns in output
    new_columns = ['Lab Code', 'Brand code', 'Model code']
    
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
    
    # Ensure all original columns are included
    meandata = meandata[['Lab Code', 'Brand code', 'Model code'] + [col for col in meandata.columns if col not in ['Lab Code', 'Brand code', 'Model code']]]
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
    
    # Detailed calculation viewer section
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
        
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(data=grade_counts, x='Test', y='Count', hue='Grade', 
                   palette={'Excellent':'#2ecc71', 'Good':'#3498db', 'Satisfactory':'#f39c12', 
                           'Unsatisfactory':'#e74c3c', 'Serious problem':'#c0392b', 'No data':'#95a5a6'})
        plt.xticks(rotation=45, ha='right')
        plt.title(f'Grade Distribution by Test (Model {selected_model})')
        plt.tight_layout()
        st.pyplot(fig)
    
    with tab2:
        zscore_cols = [col for col in meandata.columns if '_zscore' in col]
        zscore_data = meandata[['Lab Code'] + zscore_cols].melt(id_vars='Lab Code', var_name='Test', value_name='Z-Score')
        
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.boxplot(data=zscore_data, x='Test', y='Z-Score')
        plt.xticks(rotation=45, ha='right')
        plt.title(f'Z-Score Distribution by Test (Model {selected_model})')
        plt.tight_layout()
        st.pyplot(fig)
    
    # Add calculation details to download
    download_df = meandata.copy()
    
    # Add calculation details to the download DataFrame
    for col in numeric_cols:
        download_df[f'{col}_calculation_details'] = calc_details[f'{col}_calculation']
        download_df[f'{col}_grade_explanation'] = calc_details[f'{col}_grade_explanation']
    
    # Download button for processed data
    st.download_button(
        label=f"📥 Download Analysis Report for Model {selected_model}",
        data=download_df.to_csv(index=False).encode('utf-8'),
        file_name=f'smartlab_analysis_model_{selected_model}.csv',
        mime='text/csv',
        use_container_width=True
    )
    
    # Download all split files as a zip
    import zipfile
    from io import BytesIO
    
    st.markdown('<div class="subheader-style">Download All Split Files</div>', unsafe_allow_html=True)
    if st.button("Download All Model Code Files as ZIP"):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for model_code in unique_model_codes:
                output_filename = f"BloodData_Model_{model_code}.csv"
                output_path = os.path.join("split_by_model_code", output_filename)
                zip_file.write(output_path, output_filename)
        
        zip_buffer.seek(0)
        st.download_button(
            label="📦 Download ZIP of All Split Files",
            data=zip_buffer,
            file_name="split_model_code_files.zip",
            mime="application/zip",
            use_container_width=True
        )
    
    # Generate a detailed report for selected lab
    st.markdown('<div class="subheader-style">Export Detailed Calculation Report</div>', unsafe_allow_html=True)
    
    export_lab = st.selectbox("Select Lab for Detailed Report", options=meandata['Lab Code'].unique(), key="export_lab")
    
    if st.button("Generate Detailed Report for Selected Lab"):
        st.markdown(f"### Detailed Calculations for Lab: {export_lab} (Model: {selected_model})")
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
    st.info("ℹ️ Please upload a CSV file to begin analysis. The app will split the data by Model code and calculate z-scores and grades for selected model data.")
