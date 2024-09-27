import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from openai import AzureOpenAI
import mysql.connector
from mysql.connector import Error
import json

# Load the environment variables
load_dotenv()

# Get the values from the environment variables
pdf_key = os.getenv('PDF_AI_SERVICE_KEY')
pdf_endpoint = os.getenv('PDF_AI_SERVICE_ENDPOINT')
azure_oai_key = os.getenv('NLP_AZURE_OAI_KEY')
azure_oai_endpoint = os.getenv('NLP_AZURE_OAI_ENDPOINT')
azure_oai_deployment_id = os.getenv('NLP_AZURE_OAI_DEPLOYMENT')

# Set page configuration
st.set_page_config(page_title="Medical Record Summarizer", layout="wide")
# Load external CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('style.css')

# Database function
def send_data_to_sql(data):
    host = os.getenv("MYSQL_HOST")
    database = os.getenv("MYSQL_DB")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")

    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=3306
        )
        cursor = connection.cursor()

        if connection.is_connected():

            data = json.loads(data)

            # Insert patient information
            patient_info = data.get('Patient Information', {})
            query = """
                INSERT INTO patient_information (full_name, date_of_birth, address)
                VALUES (%s, %s, %s);
            """
            values = (patient_info.get('Name'), patient_info.get('Date of Birth'), patient_info.get('Address'))
            cursor.execute(query, values)
            patient_id = cursor.lastrowid
            st.success(f"Inserted patient information . ")

            # Insert into other tables (e.g., insurance, medical history, etc.)
            # Example for Insurance Information
            insurance_info = data.get('Insurance Information', {})
            query = """
                INSERT INTO INSURANCE (patient_id, PROVIDER_NAME, POLICY_NAME)
                VALUES (%s, %s, %s)
            """
            values = (patient_id, insurance_info.get('Provider Name'), insurance_info.get('Policy Name'))
            cursor.execute(query, values)

            medical_history = data.get('Medical History', {})
            query = """
                INSERT INTO MEDICAL_HISTORY (patient_id, family_history, past_illness, allergies)
                VALUES (%s, %s, %s, %s)
            """
            values = (patient_id, medical_history.get('Family History'), medical_history.get('Past Illnesses'), medical_history.get('Allergies'))
            print(f"Executing query: {query} with values: {values}")
            cursor.execute(query, values)
            connection.commit()

            # Insert into CurrentMedications table
            current_medications = data.get('Current Medications', {})
            query = """
                INSERT INTO currentmedications (patient_id, medication, dosage, reason)
                VALUES (%s, %s, %s, %s)
            """
            values = (patient_id, current_medications.get('Medication'), current_medications.get('Dosage'), current_medications.get('Reason'))
            print(f"Executing query: {query} with values: {values}")
            cursor.execute(query, values)
            connection.commit()
            # Insert into Immunizations table
            immunizations = data.get('Immunizations', {})
            query = """
                INSERT INTO IMMUNIZATIONS (patient_id, date_time, vaccine, provider)
                VALUES (%s, %s, %s, %s)
            """
            values = (patient_id, immunizations.get('Date'), immunizations.get('Vaccine'), immunizations.get('Provider'))
            print(f"Executing query: {query} with values: {values}")
            cursor.execute(query, values)
            connection.commit()
            # Insert into OfficeVisits table
            office_visits = data.get('Office Visits', {})
            query = """
                INSERT INTO OFFICEVISITS (patient_id, date_time, reason_for_visit, diagnosis, plan)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (patient_id, office_visits.get('Date'), office_visits.get('Reason for Visit'), office_visits.get('Diagnosis'), office_visits.get('Plan'))
            print(f"Executing query: {query} with values: {values}")
            cursor.execute(query, values)

            # Insert into LaboratoryResults table
            laboratory_results = data.get('Laboratory Results', {})
            query = """
                INSERT INTO LABORATORYRESULTS (patient_id, date_time, test, result)
                VALUES (%s, %s, %s, %s)
            """
            values = (patient_id, laboratory_results.get('Date'), laboratory_results.get('Test'), laboratory_results.get('Result'))
            print(f"Executing query: {query} with values: {values}")
            cursor.execute(query, values)

            # Insert into ImagingStudies table
            imaging_studies = data.get('Imaging Studies', {})
            query = """
                INSERT INTO IMAGINGSTUDIES (patient_id, date_time, procedure_, findings)
                VALUES (%s, %s, %s, %s)
            """
            values = (patient_id, imaging_studies.get('Date'), imaging_studies.get('Procedure'), imaging_studies.get('Findings'))
            print(f"Executing query: {query} with values: {values}")
            cursor.execute(query, values)

 

            # Commit all the inserts
            connection.commit()
            st.text('All data inserted successfully and committed to the database')
            st.text(" you can now call your doctor for a follow up")
            st.text("you can contact your insurance provider for more information")
            st.text("")
                    
            st.text("Thank you for using our service") 

    except Error as e:
        print(f"An error occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Current data being processed: {json.dumps(data, indent=2)}")
        if cursor:
            print(f"Last executed query: {cursor.statement}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print('MySQL connection is closed')


# Main title with styling
st.markdown("<h1>📋 Medical Record Summarizer</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("""
    <div class="sidebar">
        <h3>About</h3>
        <p>This app allows you to upload a medical record PDF, analyze it, and store the summarized information in a database.</p>
    </div>
""", unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("<h2>Upload and Analyze</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader('Upload a PDF file', type='pdf')

    if uploaded_file is not None:
        st.success("File uploaded successfully!")

        if st.button("Analyze Document"):
            with st.spinner('Analyzing...'):
                # Analyze document
                document_analysis_client = DocumentAnalysisClient(endpoint=pdf_endpoint, credential=AzureKeyCredential(pdf_key))
                pdf_bytes = uploaded_file.read()
                poller = document_analysis_client.begin_analyze_document("prebuilt-document", pdf_bytes)
                result = poller.result()

                text_data = []
                for page in result.pages:
                    for line in page.lines:
                        text_data.append(line.content)

                client = AzureOpenAI(
                    azure_endpoint=azure_oai_endpoint,
                    api_key=azure_oai_key,
                    api_version="2024-02-15-preview"
                )

                system_message = {"role": "system", "content": "You are a helpful assistant that summarizes and creates a JSON file out of medical records extracted from text."}
                user_message = {"role": "user", "content": f"Summarize the following text and make sure each key begins with a capital letter: {text_data}"}
                messages = [system_message, user_message]

                try:
                    response = client.chat.completions.create(
                        model=azure_oai_deployment_id,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1000
                    )

                    if response.choices and response.choices[0].message:
                        summary = response.choices[0].message.content
                        st.json(summary)
                        data = summary
                        send_data_to_sql(data)
                        st.success("Data stored in database successfully!")


                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

with col2:
    st.markdown("<h2>📄 Instructions</h2>", unsafe_allow_html=True)
    st.info(
        "1. Upload a medical record PDF using the file uploader.\n"
        "2. Click 'Analyze Document' to process the PDF.\n"
        "3. Review the summarized information.\n"
        "4. Click 'Store in Database' to save the data."
    )

# Footer
st.markdown("<footer>© 2024 Medical Record Summarizer. All rights reserved.</footer>", unsafe_allow_html=True)
