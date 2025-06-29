import os
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import streamlit as st

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not found")

engine = create_engine(str(DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PDFDocument(Base):
    """Store uploaded PDF documents and their metadata."""
    __tablename__ = "pdf_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    text_content = Column(Text)
    image_count = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    character_count = Column(Integer, default=0)
    
    # Relationship to analyses
    analyses = relationship("Analysis", back_populates="pdf_document")

class Analysis(Base):
    """Store phenotype analyses and diagnosis results."""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    pdf_document_id = Column(Integer, ForeignKey("pdf_documents.id"))
    phenotype_description = Column(Text, nullable=False)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    report_content = Column(Text)
    
    # Relationships
    pdf_document = relationship("PDFDocument", back_populates="analyses")
    diagnosis_suggestions = relationship("DiagnosisSuggestion", back_populates="analysis")

class DiagnosisSuggestion(Base):
    """Store individual diagnosis suggestions from analyses."""
    __tablename__ = "diagnosis_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    condition_name = Column(String(255), nullable=False)
    confidence_level = Column(String(50))
    confidence_score = Column(Integer)
    matching_features = Column(Text)  # JSON or comma-separated
    evidence = Column(Text)
    additional_info = Column(Text)
    
    # Relationship
    analysis = relationship("Analysis", back_populates="diagnosis_suggestions")

class MedicalTerm(Base):
    """Store extracted medical terms for analysis."""
    __tablename__ = "medical_terms"
    
    id = Column(Integer, primary_key=True, index=True)
    pdf_document_id = Column(Integer, ForeignKey("pdf_documents.id"))
    term = Column(String(255), nullable=False)
    term_type = Column(String(50))  # 'syndrome', 'gene', 'phenotype', etc.
    frequency = Column(Integer, default=1)
    
    # Relationship
    pdf_document = relationship("PDFDocument")

class DatabaseManager:
    """Manage database operations for the medical diagnosis application."""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session."""
        return self.SessionLocal()
    
    def store_pdf_document(self, filename: str, file_size: int, text_content: str, 
                          image_count: int, word_count: int, character_count: int):
        """Store PDF document information in database."""
        session = self.get_session()
        try:
            pdf_doc = PDFDocument(
                filename=filename,
                file_size=file_size,
                text_content=text_content,
                image_count=image_count,
                word_count=word_count,
                character_count=character_count
            )
            session.add(pdf_doc)
            session.commit()
            session.refresh(pdf_doc)
            return pdf_doc.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def store_analysis(self, pdf_document_id: int, phenotype_description: str, 
                      diagnosis_suggestions: list, report_content: str):
        """Store analysis results in database."""
        session = self.get_session()
        try:
            # Create analysis record
            analysis = Analysis(
                pdf_document_id=pdf_document_id,
                phenotype_description=phenotype_description,
                report_content=report_content
            )
            session.add(analysis)
            session.commit()
            session.refresh(analysis)
            
            # Store diagnosis suggestions
            for suggestion in diagnosis_suggestions:
                diag_suggestion = DiagnosisSuggestion(
                    analysis_id=analysis.id,
                    condition_name=suggestion['condition'],
                    confidence_level=suggestion['confidence'],
                    confidence_score=self._parse_confidence_score(suggestion['confidence']),
                    matching_features=', '.join(suggestion['matching_features']),
                    evidence=suggestion['evidence'],
                    additional_info=suggestion['additional_info']
                )
                session.add(diag_suggestion)
            
            session.commit()
            return analysis.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def store_medical_terms(self, pdf_document_id: int, terms: list, term_type: str = 'general'):
        """Store extracted medical terms."""
        session = self.get_session()
        try:
            for term in terms:
                medical_term = MedicalTerm(
                    pdf_document_id=pdf_document_id,
                    term=term,
                    term_type=term_type
                )
                session.add(medical_term)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_pdf_documents(self, limit: int = 10):
        """Get recent PDF documents."""
        session = self.get_session()
        try:
            documents = session.query(PDFDocument).order_by(
                PDFDocument.upload_date.desc()
            ).limit(limit).all()
            return documents
        finally:
            session.close()
    
    def get_analyses_for_pdf(self, pdf_document_id: int):
        """Get all analyses for a specific PDF document."""
        session = self.get_session()
        try:
            analyses = session.query(Analysis).filter(
                Analysis.pdf_document_id == pdf_document_id
            ).order_by(Analysis.analysis_date.desc()).all()
            return analyses
        finally:
            session.close()
    
    def get_analysis_with_suggestions(self, analysis_id: int):
        """Get analysis with its diagnosis suggestions."""
        session = self.get_session()
        try:
            analysis = session.query(Analysis).filter(
                Analysis.id == analysis_id
            ).first()
            if analysis:
                suggestions = session.query(DiagnosisSuggestion).filter(
                    DiagnosisSuggestion.analysis_id == analysis_id
                ).all()
                return analysis, suggestions
            return None, []
        finally:
            session.close()
    
    def get_common_conditions(self, limit: int = 10):
        """Get most commonly suggested conditions."""
        session = self.get_session()
        try:
            conditions = session.query(
                DiagnosisSuggestion.condition_name,
                sa.func.count(DiagnosisSuggestion.id).label('count')
            ).group_by(
                DiagnosisSuggestion.condition_name
            ).order_by(
                sa.desc('count')
            ).limit(limit).all()
            return conditions
        finally:
            session.close()
    
    def search_analyses_by_phenotype(self, search_term: str, limit: int = 10):
        """Search analyses by phenotype description."""
        session = self.get_session()
        try:
            analyses = session.query(Analysis).filter(
                Analysis.phenotype_description.ilike(f'%{search_term}%')
            ).order_by(
                Analysis.analysis_date.desc()
            ).limit(limit).all()
            return analyses
        finally:
            session.close()
    
    def get_statistics(self):
        """Get database statistics."""
        session = self.get_session()
        try:
            pdf_count = session.query(PDFDocument).count()
            analysis_count = session.query(Analysis).count()
            suggestion_count = session.query(DiagnosisSuggestion).count()
            
            return {
                'total_pdfs': pdf_count,
                'total_analyses': analysis_count,
                'total_suggestions': suggestion_count
            }
        finally:
            session.close()
    
    def _parse_confidence_score(self, confidence_text: str) -> int:
        """Convert confidence text to numeric score."""
        confidence_map = {
            'very low confidence': 10,
            'low confidence': 30,
            'moderate confidence': 60,
            'high confidence': 85
        }
        return confidence_map.get(confidence_text.lower(), 50)

# Initialize database
@st.cache_resource
def get_database_manager():
    """Get cached database manager instance."""
    db_manager = DatabaseManager()
    db_manager.create_tables()
    return db_manager