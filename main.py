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
pdf_key=os.getenv('PDF_AI_SERVICE_KEY')
pdf_endpoint=os.getenv('PDF_AI_SERVICE_ENDPOINT')   

azure_oai_key=os.getenv('NLP_AZURE_OAI_KEY')
azure_oai_endpoint=os.getenv('NLP_AZURE_OAI_ENDPOINT')
azure_oai_deployment_id=os.getenv('NLP_AZURE_OAI_DEPLOYMENT')


st.title('Medical Record Summarizer')
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('style.css')
# creating a funtion to send the data into a sql database
def send_data_to_sql(data):
    host = os.getenv("MYSQL_HOST")
    database = os.getenv("MYSQL_DB")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")

    # Parse the data if it's a string


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
            print('Connected to MySQL database')
            print(f"Database info: {connection.get_server_info()}")
            # Debug: Print all tables in the database
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("Tables in the database:")
            for table in tables:
                print(table[0])

            data = json.loads(data)

            # Insert patient information
            print(f"Data: {data}")
            patient_info = data.get('Patient Information', {})
            
            print(f"Patient information: {patient_info.get('Name')}")
            print(f"Patient information: {patient_info}")
           
            print(f"Patient date of birth: {patient_info.get('Date of Birth')}")
            print(f"Patient address: {patient_info.get('Address')}")
            query = """
                INSERT INTO patient_information (full_name, date_of_birth, address)
                VALUES (%s, %s, %s);
            """
            print(f" this is the patient name {patient_info.get('name')}")
            values = (patient_info.get('Name'), patient_info.get('Date of Birth'), patient_info.get('Address'))
            print(f"Executing query: {query} with values: {values}")
            cursor.execute(query, values)
            patient_id = cursor.lastrowid
            print(f"Inserted patient information. Patient ID: {patient_id}")
            connection.commit()

            # Similar debug prints for other insertions...
            # Insert into Insurance table
            insurance_info = data.get('Insurance Information', {})
            query = """
                INSERT INTO INSURANCE (patient_id, PROVIDER_NAME, POLICY_NAME)
                VALUES (%s, %s, %s)
            """
            print(f"Insurance information: {insurance_info.get('Provider Name')}")
            print(f"Insurance information: {insurance_info.get('Policy Name')}")
            print(f"Insurance information: {insurance_info}")
            values = (patient_id, insurance_info.get('Provider Name'), insurance_info.get('Policy Name'))
            print(f"Executing query: {query} with values: {values}")
            cursor.execute(query, values)
            connection.commit()
            # Insert into MedicalHistory table
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
            st.text(" you can now call your doctor to get the summary of the medical record and tell you his feedback  his number is : +1234567890")
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

    # Debug: Print final status
    print("Function execution completed. Check above messages for details .")



# Create a client object
document_analysis_client = DocumentAnalysisClient(endpoint=pdf_endpoint,credential=AzureKeyCredential(pdf_key))


# using streamlit to create a file uploader 
uploaded_file =st.file_uploader('upload a pdf file', type='pdf')
if uploaded_file is not None:
    st.text('File uploaded')

    # Read the file
    pdf_bytes = uploaded_file.read()

    # Analyze the document
    with st.spinner('analyzing...'):
        poller = document_analysis_client.begin_analyze_document("prebuilt-document", pdf_bytes)
        result = poller.result()

    # Exctract the data from the result
    text_data = []
    for page in result.pages:
        for line in page.lines:
            text_data.append(line.content)


    st.spinner('Analyzing using Azure OpenAI...')

    client = AzureOpenAI(
        azure_endpoint=azure_oai_endpoint,
        api_key=azure_oai_key,
        api_version="2024-02-15-preview"
    )

    # System message to define the role of the assistant
    system_message = {"role": "system", "content": "You are a helpful assistant that summarizes and make a json file out of  medical records extracted from text ."}

    # User message containing the text to summarize
    user_message = {"role": "user", "content": f"Summarize the following text and make sure a each key is beginning with a capital letter : {text_data}"}

    # Combining the system message and the user message
    messages = [system_message, user_message]
    st.spinner('Summarizing...')
    try:
        # Send the request
        response = client.chat.completions.create(
            model=azure_oai_deployment_id,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        # Check if there's content in the response
        if response.choices and response.choices[0].message:
            summary = response.choices[0].message.content
            st.write(summary)
            data= summary
        else:
            st.error("Error: No content in the response")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


        # Send the data to a SQL database
    send_data_to_sql(data)