import streamlit as st
import pandas as pd
import numpy as np
from pyvis.network import Network
import random
from datetime import datetime, timedelta
import json

# Set page configuration
st.set_page_config(page_title="Precision Medicine Network", layout="wide")

def generate_synthetic_data(n_patients=100):
    # Helper function to generate random dates within a range
    def random_date(start_date, end_date):
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        return start_date + timedelta(days=random_days)
    
    # 1. Patient Demographics
    demographics = []
    for i in range(n_patients):
        demographics.append({
            'Patient_ID': f'PT{i:03d}',
            'Age': random.randint(25, 85),
            'Sex': random.choice(['Male', 'Female']),
            'Race': random.choice(['White', 'Black', 'Asian', 'Hispanic', 'Other']),
            'Ethnicity': random.choice(['Hispanic/Latino', 'Non-Hispanic/Latino']),
            'Geographic_Location': random.choice(['Northeast', 'Southeast', 'Midwest', 'West', 'Southwest'])
        })
    
    # 2. Genomic Information
    gene_variants = ['BRCA1', 'BRCA2', 'TP53', 'KRAS', 'EGFR', 'ALK', 'ROS1', 'BRAF', 'PIK3CA']
    genomics = []
    for patient in demographics:
        num_variants = random.randint(1, 3)
        for _ in range(num_variants):
            genomics.append({
                'Patient_ID': patient['Patient_ID'],
                'Gene_Variant': random.choice(gene_variants),
                'Allele_Frequency': round(random.uniform(0, 1), 3),
                'Biomarker_Expression': random.choice(['Positive', 'Negative']),
                'Pathogenicity': random.choice(['Benign', 'Likely Benign', 'VUS', 'Likely Pathogenic', 'Pathogenic'])
            })
    
    # 3. Disease Information
    diseases = []
    disease_types = {
        'Cancer': ['Breast Cancer', 'Lung Cancer', 'Colorectal Cancer'],
        'Metabolic': ['Type 2 Diabetes', 'Obesity'],
        'Cardiovascular': ['Hypertension', 'Coronary Artery Disease']
    }
    
    for patient in demographics:
        primary_type = random.choice(list(disease_types.keys()))
        diseases.append({
            'Patient_ID': patient['Patient_ID'],
            'Primary_Diagnosis': random.choice(disease_types[primary_type]),
            'Comorbid_Conditions': random.sample(['Hypertension', 'Hyperlipidemia', 'COPD', 'Asthma'], k=random.randint(0, 2)),
            'Stage': random.choice(['Stage I', 'Stage II', 'Stage III', 'Stage IV']) if primary_type == 'Cancer' else 'N/A',
            'Disease_Subtype': f"Subtype_{random.choice(['A', 'B', 'C'])}"
        })
    
    # 4. Medication History
    medications = []
    med_list = {
        'Breast Cancer': ['Tamoxifen', 'Letrozole', 'Palbociclib'],
        'Lung Cancer': ['Erlotinib', 'Crizotinib', 'Pembrolizumab'],
        'Type 2 Diabetes': ['Metformin', 'Glipizide', 'Sitagliptin']
    }
    
    for disease in diseases:
        num_meds = random.randint(1, 3)
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2023, 12, 31)
        
        for _ in range(num_meds):
            med_start = random_date(start_date, end_date)
            medications.append({
                'Patient_ID': disease['Patient_ID'],
                'Medication_Name': random.choice(med_list.get(disease['Primary_Diagnosis'], ['Aspirin', 'Ibuprofen'])),
                'Dosage': f"{random.choice([100, 200, 500])} mg",
                'Frequency': random.choice(['Once Daily', 'Twice Daily', 'Three Times Daily']),
                'Treatment_Start_Date': med_start.strftime('%Y-%m-%d'),
                'Treatment_End_Date': (med_start + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
                'Adherence_Level': random.choice(['High', 'Moderate', 'Low'])
            })
    
    # 5. Adverse Events
    adverse_events = []
    ae_types = ['Nausea', 'Fatigue', 'Headache', 'Dizziness', 'Rash', 'Joint Pain']
    
    for med in medications:
        if random.random() < 0.3:  # 30% chance of adverse event
            start_date = datetime.strptime(med['Treatment_Start_Date'], '%Y-%m-%d')
            adverse_events.append({
                'Patient_ID': med['Patient_ID'],
                'Adverse_Event': random.choice(ae_types),
                'Severity': random.choice(['Mild', 'Moderate', 'Severe']),
                'Start_Date': (start_date + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
                'Duration': random.randint(1, 30),
                'Outcome': random.choice(['Resolved', 'Ongoing'])
            })
    
    # 6. Biomarkers
    biomarkers = []
    biomarker_types = {
        'Blood Sugar': {'range': (70, 140), 'unit': 'mg/dL'},
        'Cholesterol': {'range': (150, 300), 'unit': 'mg/dL'},
        'White Blood Cell Count': {'range': (4000, 11000), 'unit': 'cells/µL'},
        'Hemoglobin': {'range': (12, 17), 'unit': 'g/dL'}
    }
    
    for patient in demographics:
        for biomarker, info in biomarker_types.items():
            biomarkers.append({
                'Patient_ID': patient['Patient_ID'],
                'Biomarker_Type': biomarker,
                'Value': round(random.uniform(*info['range']), 2),
                'Reference_Range': f"{info['range'][0]}-{info['range'][1]} {info['unit']}",
                'Measurement_Date': random_date(datetime(2023, 1, 1), datetime(2023, 12, 31)).strftime('%Y-%m-%d')
            })
    
    # 7. Outcomes
    outcomes = []
    for disease in diseases:
        outcomes.append({
            'Patient_ID': disease['Patient_ID'],
            'Outcome_Type': 'Treatment Response',
            'Outcome_Date': random_date(datetime(2023, 6, 1), datetime(2023, 12, 31)).strftime('%Y-%m-%d'),
            'Outcome_Status': random.choice(['Complete Response', 'Partial Response', 'Stable Disease', 'Progressive Disease'])
        })
    
    return (pd.DataFrame(demographics),
            pd.DataFrame(genomics),
            pd.DataFrame(diseases),
            pd.DataFrame(medications),
            pd.DataFrame(adverse_events),
            pd.DataFrame(biomarkers),
            pd.DataFrame(outcomes))

def create_network_graph(demo_df, genomics_df, diseases_df, meds_df, ae_df, biomarkers_df, outcomes_df, filters=None):
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    
    # Apply filters
    if filters:
        if filters['demographics']:
            for field, values in filters['demographics'].items():
                if values:
                    demo_df = demo_df[demo_df[field].isin(values)]
        
        filtered_patients = demo_df['Patient_ID'].unique()
        genomics_df = genomics_df[genomics_df['Patient_ID'].isin(filtered_patients)]
        diseases_df = diseases_df[diseases_df['Patient_ID'].isin(filtered_patients)]
        meds_df = meds_df[meds_df['Patient_ID'].isin(filtered_patients)]
        ae_df = ae_df[ae_df['Patient_ID'].isin(filtered_patients)]
        
        if filters.get('gene_variants'):
            genomics_df = genomics_df[genomics_df['Gene_Variant'].isin(filters['gene_variants'])]
        
        if filters.get('medications'):
            meds_df = meds_df[meds_df['Medication_Name'].isin(filters['medications'])]
    
    # Add patient nodes
    for _, patient in demo_df.iterrows():
        patient_genes = genomics_df[genomics_df['Patient_ID'] == patient['Patient_ID']]['Gene_Variant'].tolist()
        patient_meds = meds_df[meds_df['Patient_ID'] == patient['Patient_ID']]['Medication_Name'].tolist()
        patient_aes = ae_df[ae_df['Patient_ID'] == patient['Patient_ID']]['Adverse_Event'].tolist()
        
        tooltip = (f"Patient ID: {patient['Patient_ID']}<br>"
                  f"Demographics:<br>"
                  f"- Age: {patient['Age']}<br>"
                  f"- Sex: {patient['Sex']}<br>"
                  f"- Race: {patient['Race']}<br>"
                  f"Gene Variants: {', '.join(patient_genes)}<br>"
                  f"Medications: {', '.join(patient_meds)}<br>"
                  f"Adverse Events: {', '.join(patient_aes)}")
        
        net.add_node(patient['Patient_ID'], 
                    label=patient['Patient_ID'],
                    title=tooltip,
                    color='#97c2fc',
                    shape='dot')
    
    # Add connections based on shared characteristics
    patient_ids = demo_df['Patient_ID'].unique()
    for i, patient1 in enumerate(patient_ids):
        for patient2 in patient_ids[i+1:]:
            shared_genes = set(genomics_df[genomics_df['Patient_ID'] == patient1]['Gene_Variant']) & \
                         set(genomics_df[genomics_df['Patient_ID'] == patient2]['Gene_Variant'])
            
            shared_meds = set(meds_df[meds_df['Patient_ID'] == patient1]['Medication_Name']) & \
                         set(meds_df[meds_df['Patient_ID'] == patient2]['Medication_Name'])
            
            if shared_genes or shared_meds:
                net.add_edge(patient1, patient2)
    
    # Configure physics
    net.set_options("""
    const options = {
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 200,
                "springConstant": 0.08
            },
            "maxVelocity": 50,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {"iterations": 150}
        }
    }
    """)
    
    return net

def main():
    st.title("Precision Medicine Network Visualization")
    
    # Generate synthetic data
    demo_df, genomics_df, diseases_df, meds_df, ae_df, biomarkers_df, outcomes_df = generate_synthetic_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Demographics filters
    st.sidebar.subheader("Demographics")
    selected_sex = st.sidebar.multiselect("Sex", demo_df['Sex'].unique())
    selected_race = st.sidebar.multiselect("Race", demo_df['Race'].unique())
    selected_location = st.sidebar.multiselect("Location", demo_df['Geographic_Location'].unique())
    
    # Genetic filters
    st.sidebar.subheader("Genetic Information")
    selected_genes = st.sidebar.multiselect("Gene Variants", genomics_df['Gene_Variant'].unique())
    
    # Medication filters
    st.sidebar.subheader("Medications")
    selected_meds = st.sidebar.multiselect("Medications", meds_df['Medication_Name'].unique())
    
    # Reset filters
    if st.sidebar.button("Reset Filters"):
        st.experimental_rerun()
    
    # Collect filters
    filters = {
        'demographics': {
            'Sex': selected_sex,
            'Race': selected_race,
            'Geographic_Location': selected_location
        },
        'gene_variants': selected_genes,
        'medications': selected_meds
    }
    
    # Create and display network
    net = create_network_graph(demo_df, genomics_df, diseases_df, meds_df, ae_df, biomarkers_df, outcomes_df, filters)
    
    try:
        path = "network.html"
        net.save_graph(path)
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        st.components.v1.html(html, height=800)
    except Exception as e:
        st.error(f"Error displaying network: {str(e)}")
    
    # Display summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Patients", len(demo_df))
    with col2:
        st.metric("Unique Gene Variants", len(genomics_df['Gene_Variant'].unique()))
    with col3:
        st.metric("Total Medications", len(meds_df))
    with col4:
        st.metric("Total Adverse Events", len(ae_df))

if __name__ == "__main__":
    main()