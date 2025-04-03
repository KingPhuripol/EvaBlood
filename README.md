# 🧪 SmartLab Data Analysis

## Overview
SmartLab Data Analysis is a powerful tool designed to analyze laboratory test results. It processes CSV files, calculates Z-scores, assigns grades, and provides visual insights into the data.

## 📁 Upload Your Data
To start the analysis, upload a CSV file containing lab test results.

### **File Requirements:**
- Format: CSV
- Should contain numeric test values
- Must include a 'Lab Code' column for identification
- Zero values will be treated as missing data

## 🔬 Calculation Methodology
### **Z-Score Calculation:**
Z-scores measure how many standard deviations a value is from the mean.

#### **Formula:**
```math
z = \frac{x - \mu}{\sigma}
```
Where:
- `x` = individual test value
- `μ` = mean of all values for that test
- `σ` = standard deviation of all values for that test

### **Grading System:**
| Z-Score Range   | Grade            |
|----------------|----------------|
| |z| ≤ 0.5      | **Excellent**    |
| 0.5 < |z| ≤ 1  | **Good**         |
| 1 < |z| ≤ 2    | **Satisfactory** |
| 2 < |z| ≤ 3    | **Unsatisfactory** |
| |z| > 3        | **Serious problem** |

## 📊 Test Statistics
Before processing, the dataset is analyzed to calculate:
- **Mean (μ)**
- **Standard Deviation (σ)**
- **Number of Samples (N)**

## ✅ Processed Results
The dataset is transformed by:
1. **Replacing zero values** with `NaN`
2. **Computing Z-scores** for each test
3. **Assigning grades** based on Z-score values
4. **Rearranging columns** for clarity

## 🎨 Data Styling
- **Excellent**: 🟩 Green
- **Good**: 🔵 Blue
- **Satisfactory**: 🟠 Orange
- **Unsatisfactory**: 🔴 Red
- **Serious Problem**: 🟥 Dark Red
- **No Data**: ⚪ Grey

## 📊 Visual Analysis
### **1️⃣ Grade Distribution**
A bar chart shows how test results are distributed across different grades.

### **2️⃣ Z-Score Distribution**
A boxplot visualizes the spread and variability of Z-scores for different tests.

## 📥 Download Your Report
Once the analysis is complete, you can download the full processed report in CSV format.

