
# Medical Record Analyzer

This project is a Medical Record Analyzer that leverages Azure AI services to extract, analyze, and manage medical records more efficiently.

## Features

- **OCR Module**: Used to extract text from medical records.
- **OpenAI Module**: Summarizes the extracted text for quick review.
- **MySQL Database**: Stores the processed data for better management and retrieval.
- **Streamlit**: The web interface used to interact with the analyzer.

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.x
- Streamlit
- Azure AI services SDKs (OCR, OpenAI)
- MySQL
- Required Python libraries (listed in `requirements.txt`)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/omartarek000/Medical_records_analyzer.git
cd Medical_records_analyzer
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables for Azure credentials and MySQL database:

- `AZURE_OCR_KEY` and `AZURE_OCR_ENDPOINT`
- `OPENAI_KEY`
- `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`

You can store these in a `.env` file.

### Usage

To run the project, use Streamlit:

```bash
streamlit run name_of_the_file.py
```

This will launch the Streamlit web app where you can upload medical records, process them, and view the summarized results.

## Database

The processed medical data is stored in a MySQL database with the following structure:

- **Patient Information**
- **Insurance Information**
- **Medical History**
- **Current Medications**
- **Immunizations**
- **Office Visits**
- **Laboratory Results**
- **Imaging Studies**

## Contributing

Feel free to fork this project, submit issues, and send pull requests.

## License

This project is licensed under the MIT License.
