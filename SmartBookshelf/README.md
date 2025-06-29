# Medical Diagnosis Assistant

A Streamlit-based web application that analyzes medical literature PDFs and correlates clinical phenotypes with potential diagnoses, specializing in craniosynostosis and genetic disorders.

## Features

- **PDF Processing**: Upload and extract text/images from medical literature
- **Phenotype Analysis**: Analyze clinical observations against medical references
- **Diagnosis Suggestions**: Generate evidence-based diagnostic recommendations
- **Database Storage**: PostgreSQL integration for historical data
- **Comprehensive Reports**: Downloadable diagnostic reports with evidence

## Quick Start

### Online Demo
Visit the live application: [Medical Diagnosis Assistant](https://your-streamlit-app.streamlit.app)

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/medical-diagnosis-assistant.git
cd medical-diagnosis-assistant
```

2. Install dependencies:
```bash
pip install -r streamlit_requirements.txt
```

3. Set up PostgreSQL database and environment variables:
```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/dbname"
```

4. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Upload PDF**: Upload medical literature or case studies
2. **Enter Phenotype**: Describe clinical observations and symptoms
3. **Analyze**: Get AI-powered diagnosis suggestions
4. **Review Results**: View evidence-based recommendations
5. **Download Report**: Export comprehensive diagnostic report

## Architecture

- **Frontend**: Streamlit web interface with tab-based navigation
- **Backend**: Python with modular utility classes
- **Database**: PostgreSQL for persistent storage
- **PDF Processing**: PyMuPDF for content extraction
- **Medical Analysis**: Custom pattern matching and scoring algorithms

## Deployment

### Streamlit Community Cloud

1. Push code to GitHub repository
2. Connect repository to [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Add database URL as secret in Streamlit settings
4. Deploy with one click

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string

## Medical Disclaimer

This tool is for educational and research purposes only. It should NOT be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for clinical decisions.

## License

Educational use only. See license file for details.