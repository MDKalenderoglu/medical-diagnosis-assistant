import streamlit as st
from utils.database import get_database_manager
import pandas as pd
from datetime import datetime, timedelta

def display_database_dashboard():
    """Display database statistics and recent activity."""
    st.header("📊 Database Dashboard")
    
    db_manager = get_database_manager()
    
    try:
        # Get statistics
        stats = db_manager.get_statistics()
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total PDFs", stats['total_pdfs'])
        
        with col2:
            st.metric("Total Analyses", stats['total_analyses'])
        
        with col3:
            st.metric("Total Suggestions", stats['total_suggestions'])
        
        # Recent PDFs section
        st.subheader("📄 Recent PDF Documents")
        recent_pdfs = db_manager.get_pdf_documents(limit=10)
        
        if recent_pdfs:
            pdf_data = []
            for pdf in recent_pdfs:
                pdf_data.append({
                    'Filename': pdf.filename,
                    'Upload Date': pdf.upload_date.strftime('%Y-%m-%d %H:%M'),
                    'Size (bytes)': pdf.file_size,
                    'Words': pdf.word_count,
                    'Images': pdf.image_count
                })
            
            df_pdfs = pd.DataFrame(pdf_data)
            st.dataframe(df_pdfs, use_container_width=True)
        else:
            st.info("No PDF documents found in database.")
        
        # Common conditions section
        st.subheader("🎯 Most Common Diagnoses")
        common_conditions = db_manager.get_common_conditions(limit=10)
        
        if common_conditions:
            condition_data = []
            for condition, count in common_conditions:
                condition_data.append({
                    'Condition': condition,
                    'Frequency': count
                })
            
            df_conditions = pd.DataFrame(condition_data)
            st.dataframe(df_conditions, use_container_width=True)
            
            # Create bar chart
            st.bar_chart(df_conditions.set_index('Condition')['Frequency'])
        else:
            st.info("No diagnosis suggestions found in database.")
            
    except Exception as e:
        st.error(f"Error accessing database: {str(e)}")

def display_search_interface():
    """Display search interface for historical analyses."""
    st.header("🔍 Search Historical Analyses")
    
    db_manager = get_database_manager()
    
    # Search input
    search_term = st.text_input(
        "Search by phenotype description:",
        placeholder="Enter keywords to search previous analyses"
    )
    
    if search_term:
        try:
            analyses = db_manager.search_analyses_by_phenotype(search_term, limit=20)
            
            if analyses:
                st.success(f"Found {len(analyses)} matching analyses")
                
                for analysis in analyses:
                    with st.expander(f"Analysis from {analysis.analysis_date.strftime('%Y-%m-%d %H:%M')}"):
                        st.write(f"**Phenotype:** {analysis.phenotype_description}")
                        
                        # Get diagnosis suggestions
                        _, suggestions = db_manager.get_analysis_with_suggestions(analysis.id)
                        
                        if suggestions:
                            st.write("**Diagnosis Suggestions:**")
                            for suggestion in suggestions:
                                st.write(f"- {suggestion.condition_name} ({suggestion.confidence_level})")
                        
                        if st.button(f"View Full Report", key=f"report_{analysis.id}"):
                            st.text_area("Report Content:", analysis.report_content, height=300, disabled=True)
            else:
                st.info("No analyses found matching your search term.")
                
        except Exception as e:
            st.error(f"Error searching database: {str(e)}")

def display_pdf_history():
    """Display PDF document history with analysis links."""
    st.header("📚 PDF Document History")
    
    db_manager = get_database_manager()
    
    try:
        pdfs = db_manager.get_pdf_documents(limit=50)
        
        if pdfs:
            for pdf in pdfs:
                with st.expander(f"{pdf.filename} - {pdf.upload_date.strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**File Size:** {pdf.file_size:,} bytes")
                        st.write(f"**Word Count:** {pdf.word_count:,}")
                        st.write(f"**Images:** {pdf.image_count}")
                        st.write(f"**Characters:** {pdf.character_count:,}")
                    
                    with col2:
                        # Get analyses for this PDF
                        analyses = db_manager.get_analyses_for_pdf(pdf.id)
                        st.write(f"**Analyses:** {len(analyses)}")
                        
                        if analyses:
                            st.write("**Recent Analyses:**")
                            for analysis in analyses[:3]:  # Show last 3
                                st.write(f"- {analysis.analysis_date.strftime('%Y-%m-%d %H:%M')}")
                    
                    # Show text preview
                    if pdf.text_content:
                        preview = pdf.text_content[:500] + "..." if len(pdf.text_content) > 500 else pdf.text_content
                        st.text_area("Text Preview:", preview, height=100, disabled=True)
        else:
            st.info("No PDF documents found in database.")
            
    except Exception as e:
        st.error(f"Error accessing PDF history: {str(e)}")