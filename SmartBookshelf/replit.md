# Medical Diagnosis Assistant

## Overview

The Medical Diagnosis Assistant is a Streamlit-based web application designed to help medical professionals and researchers analyze medical literature PDFs and correlate clinical phenotypes with potential diagnoses. The system specializes in craniosynostosis and genetic disorders, providing automated analysis of medical documents and images to generate diagnostic suggestions.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application
- **Interface**: Tab-based navigation with sidebar workflow guidance
- **State Management**: Streamlit session state for maintaining PDF processing status and analysis results
- **User Experience**: Multi-step workflow (Upload → Analyze → Results)

### Backend Architecture
- **Modular Design**: Utility-based architecture with separate modules for different functionalities
- **Processing Pipeline**: PDF → Text/Image Extraction → Medical Analysis → Report Generation
- **File Handling**: Temporary file management for PDF processing

## Key Components

### 1. PDF Processing Module (`utils/pdf_processor.py`)
- **Purpose**: Extract text and images from medical literature PDFs
- **Technology**: PyMuPDF (fitz) for PDF manipulation, PIL for image processing
- **Features**: 
  - Text extraction from all PDF pages
  - Image extraction and format conversion
  - Error handling for corrupted files

### 2. Medical Analyzer (`utils/medical_analyzer.py`)
- **Purpose**: Analyze medical content and phenotypes for diagnosis suggestions
- **Specialization**: Craniosynostosis, genetic disorders, and syndromic conditions
- **Pattern Recognition**: 
  - Medical terminology identification
  - Genetic term detection (FGFR1, FGFR2, TWIST1, etc.)
  - Phenotype classification

### 3. Report Generator (`utils/report_generator.py`)
- **Purpose**: Generate comprehensive medical diagnosis reports
- **Output Format**: Structured text reports with timestamp and disclaimer
- **Sections**: Patient phenotype, diagnosis suggestions, image analysis, document analysis, recommendations

### 4. Main Application (`app.py`)
- **Purpose**: Orchestrate the complete workflow and user interface
- **Session Management**: Track processing states across user interactions
- **Navigation**: Tab-based interface for different workflow stages

## Data Flow

1. **PDF Upload**: User uploads medical literature PDF through Streamlit interface
2. **Content Extraction**: PDFProcessor extracts text and images from the document
3. **Phenotype Input**: User describes clinical observations and symptoms
4. **Medical Analysis**: MedicalAnalyzer processes both PDF content and phenotype description
5. **Report Generation**: ReportGenerator creates comprehensive diagnostic report
6. **Results Display**: Structured output presented through Streamlit interface

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework for medical interface
- **PyMuPDF (fitz)**: PDF processing and content extraction
- **PIL (Pillow)**: Image processing and format conversion
- **Standard Library**: tempfile, os, io, re, datetime, typing

### Deployment Requirements
- Python 3.7+ environment
- PDF processing capabilities
- Image handling libraries
- Web server for Streamlit deployment

## Deployment Strategy

### Local Development
- Streamlit development server for testing and iteration
- Temporary file handling for PDF processing
- Session state management for user workflow

### Production Considerations
- **Security**: File upload validation and temporary file cleanup
- **Performance**: Efficient PDF processing for large medical documents
- **Scalability**: Session state management for concurrent users
- **Compliance**: Medical disclaimer and data handling requirements

## Changelog

- June 29, 2025. Initial setup
- June 29, 2025. Added PostgreSQL database integration with tables for PDFs, analyses, diagnosis suggestions, and medical terms

## User Preferences

Preferred communication style: Simple, everyday language.