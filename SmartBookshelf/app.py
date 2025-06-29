import streamlit as st
import tempfile
import os
from utils.pdf_processor import PDFProcessor
from utils.medical_analyzer import MedicalAnalyzer
from utils.report_generator import ReportGenerator
from utils.database import get_database_manager
from utils.database_interface import display_database_dashboard, display_search_interface, display_pdf_history

# Configure page
st.set_page_config(
    page_title="Medical Diagnosis Assistant",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'pdf_processed' not in st.session_state:
    st.session_state.pdf_processed = False
if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = ""
if 'pdf_images' not in st.session_state:
    st.session_state.pdf_images = []
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

def main():
    st.title("🧬 Medical Diagnosis Assistant")
    st.markdown("**Upload medical literature PDFs and describe phenotypes for diagnosis suggestions**")
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("📋 Workflow")
        st.markdown("""
        1. **Upload PDF** - Medical literature or case studies
        2. **Enter Phenotype** - Describe clinical observations
        3. **Analyze** - Get diagnosis suggestions
        4. **Download Report** - Export findings
        """)
        
        if st.session_state.pdf_processed:
            st.success("✅ PDF Loaded")
        if st.session_state.analysis_complete:
            st.success("✅ Analysis Complete")
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📄 PDF Upload", "🔍 Analysis", "📊 Results", "🗃️ Database"])
    
    with tab1:
        handle_pdf_upload()
    
    with tab2:
        if st.session_state.pdf_processed:
            handle_phenotype_analysis()
        else:
            st.info("Please upload a PDF document first.")
    
    with tab3:
        if st.session_state.analysis_complete:
            display_results()
        else:
            st.info("Please complete the analysis first.")
    
    with tab4:
        handle_database_tab()

def handle_database_tab():
    """Handle the database tab functionality."""
    st.header("🗃️ Database Management")
    
    # Sub-tabs for different database views
    db_tab1, db_tab2, db_tab3 = st.tabs(["📊 Dashboard", "🔍 Search", "📚 History"])
    
    with db_tab1:
        display_database_dashboard()
    
    with db_tab2:
        display_search_interface()
    
    with db_tab3:
        display_pdf_history()

def handle_pdf_upload():
    st.header("📄 PDF Document Upload")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload medical literature, case studies, or diagnostic references"
    )
    
    if uploaded_file is not None:
        try:
            with st.spinner("Processing PDF..."):
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name
                
                # Process PDF
                processor = PDFProcessor()
                text, images = processor.extract_content(tmp_path)
                
                # Store in database
                db_manager = get_database_manager()
                word_count = len(text.split())
                pdf_document_id = db_manager.store_pdf_document(
                    filename=uploaded_file.name,
                    file_size=uploaded_file.size,
                    text_content=text,
                    image_count=len(images),
                    word_count=word_count,
                    character_count=len(text)
                )
                
                # Store medical terms
                analyzer = MedicalAnalyzer()
                key_terms = analyzer.extract_key_terms(text)
                if key_terms:
                    db_manager.store_medical_terms(pdf_document_id, key_terms)
                
                # Store in session state
                st.session_state.pdf_text = text
                st.session_state.pdf_images = images
                st.session_state.pdf_processed = True
                st.session_state.pdf_document_id = pdf_document_id
                
                # Clean up temp file
                os.unlink(tmp_path)
                
                st.success(f"✅ PDF processed and saved to database!")
                
                # Display preview
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("📝 Text Preview")
                    preview_text = text[:2000] if len(text) > 2000 else text
                    st.text_area("Document content (first 2000 characters):", preview_text, height=200, disabled=True)
                    
                    if len(text) > 2000:
                        st.info(f"Full document contains {len(text)} characters")
                
                with col2:
                    st.subheader("🖼️ Images Found")
                    if images:
                        st.info(f"Found {len(images)} images in the PDF")
                        # Show first image as preview
                        if len(images) > 0:
                            st.image(images[0], caption="Preview of first image", use_container_width=True)
                    else:
                        st.info("No images found in the PDF")
                        
        except Exception as e:
            st.error(f"❌ Error processing PDF: {str(e)}")
            st.session_state.pdf_processed = False

def handle_phenotype_analysis():
    st.header("🔍 Phenotype Analysis")
    
    # Display PDF summary
    with st.expander("📄 Loaded PDF Summary", expanded=False):
        st.write(f"**Document length:** {len(st.session_state.pdf_text)} characters")
        st.write(f"**Images found:** {len(st.session_state.pdf_images)}")
        
        # Show key terms found
        analyzer = MedicalAnalyzer()
        key_terms = analyzer.extract_key_terms(st.session_state.pdf_text)
        if key_terms:
            st.write("**Key medical terms found:**")
            st.write(", ".join(key_terms[:20]))  # Show first 20 terms
    
    # Phenotype input
    st.subheader("👤 Patient Phenotype Description")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        phenotype_description = st.text_area(
            "Describe the clinical observations:",
            placeholder="Example: unilateral coronal craniosynostosis, developmental delay, hearing loss, brachycephaly",
            height=150,
            help="Enter detailed phenotypic features, symptoms, and clinical observations"
        )
    
    with col2:
        st.markdown("**Common phenotype categories:**")
        st.markdown("""
        - Craniofacial features
        - Skeletal abnormalities
        - Neurological symptoms
        - Developmental delays
        - Cardiac anomalies
        - Growth parameters
        """)
    
    # Analysis button
    if st.button("🔬 Start Analysis", type="primary", use_container_width=True):
        if phenotype_description.strip():
            with st.spinner("Analyzing phenotype against medical literature..."):
                analyzer = MedicalAnalyzer()
                
                # Perform analysis
                diagnosis_suggestions = analyzer.analyze_phenotype(
                    phenotype_description, 
                    st.session_state.pdf_text
                )
                
                image_analysis = analyzer.analyze_images(st.session_state.pdf_images)
                
                # Generate report
                report_generator = ReportGenerator()
                report = report_generator.generate_comprehensive_report(
                    phenotype_description,
                    diagnosis_suggestions,
                    image_analysis,
                    st.session_state.pdf_text
                )
                
                # Store results in database
                if hasattr(st.session_state, 'pdf_document_id'):
                    db_manager = get_database_manager()
                    analysis_id = db_manager.store_analysis(
                        pdf_document_id=st.session_state.pdf_document_id,
                        phenotype_description=phenotype_description,
                        diagnosis_suggestions=diagnosis_suggestions,
                        report_content=report
                    )
                    st.session_state.analysis_id = analysis_id
                
                # Store results in session
                st.session_state.diagnosis_suggestions = diagnosis_suggestions
                st.session_state.image_analysis = image_analysis
                st.session_state.report = report
                st.session_state.phenotype_description = phenotype_description
                st.session_state.analysis_complete = True
                
                st.success("✅ Analysis completed and saved to database!")
                st.rerun()
        else:
            st.warning("⚠️ Please enter a phenotype description before starting analysis.")

def display_results():
    st.header("📊 Analysis Results")
    
    # Display diagnosis suggestions
    st.subheader("🎯 Diagnosis Suggestions")
    
    if st.session_state.diagnosis_suggestions:
        for i, suggestion in enumerate(st.session_state.diagnosis_suggestions, 1):
            with st.expander(f"Suggestion {i}: {suggestion['condition']}", expanded=i==1):
                st.write(f"**Confidence:** {suggestion['confidence']}")
                st.write(f"**Matching features:** {', '.join(suggestion['matching_features'])}")
                st.write(f"**Evidence:** {suggestion['evidence']}")
                if suggestion['additional_info']:
                    st.write(f"**Additional information:** {suggestion['additional_info']}")
    else:
        st.info("No specific diagnosis suggestions found based on the provided phenotype.")
    
    # Display image analysis
    if st.session_state.pdf_images:
        st.subheader("🖼️ Image Analysis")
        
        for i, analysis in enumerate(st.session_state.image_analysis):
            with st.expander(f"Image {i+1} Analysis"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(st.session_state.pdf_images[i], use_column_width=True)
                with col2:
                    st.write(analysis)
    
    # Download report
    st.subheader("📄 Download Report")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.download_button(
            label="📋 Download Full Report (TXT)",
            data=st.session_state.report,
            file_name=f"medical_diagnosis_report_{st.session_state.phenotype_description[:20].replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 New Analysis", use_container_width=True):
            # Reset analysis state
            st.session_state.analysis_complete = False
            st.session_state.diagnosis_suggestions = []
            st.session_state.image_analysis = []
            st.session_state.report = ""
            st.rerun()
    
    with col3:
        if st.button("📄 New PDF", use_container_width=True):
            # Reset all state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Display full report preview
    with st.expander("📋 Report Preview", expanded=False):
        st.text_area("Generated Report:", st.session_state.report, height=400, disabled=True)

if __name__ == "__main__":
    main()
