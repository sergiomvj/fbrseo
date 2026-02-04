from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Domain(Base):
    """
    Domínios/sites sendo monitorados
    """
    __tablename__ = "domains"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    
    # Informações do domínio
    url = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_crawled_at = Column(DateTime)
    
    # Relacionamentos
    client = relationship("Client", back_populates="domains")
    keywords = relationship("Keyword", back_populates="domain", cascade="all, delete-orphan")
    rankings = relationship("Ranking", back_populates="domain", cascade="all, delete-orphan")
    backlinks = relationship("Backlink", back_populates="domain", cascade="all, delete-orphan")
    pages = relationship("Page", back_populates="domain", cascade="all, delete-orphan")


class Keyword(Base):
    """
    Keywords sendo monitoradas
    """
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)
    
    # Keyword info
    keyword = Column(String(500), nullable=False, index=True)
    search_volume = Column(Integer, default=0)
    keyword_difficulty = Column(Float, default=0.0)
    cpc = Column(Float, default=0.0)
    competition = Column(String(50))
    trend_data = Column(JSON)  # Dados de tendência mensal
    
    # Source
    source = Column(String(50), default="manual")  # semrush, gsc, manual, etc
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    domain = relationship("Domain", back_populates="keywords")
    rankings = relationship("Ranking", back_populates="keyword_obj", cascade="all, delete-orphan")


class Ranking(Base):
    """
    Posições das keywords nos motores de busca
    """
    __tablename__ = "rankings"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)
    keyword_id = Column(Integer, ForeignKey("keywords.id", ondelete="CASCADE"), nullable=True)
    
    # Ranking info
    keyword = Column(String(500), nullable=False, index=True)
    position = Column(Integer, default=0)
    previous_position = Column(Integer, default=0)
    url = Column(Text)
    
    # Métricas
    estimated_traffic = Column(Float, default=0.0)
    visibility_score = Column(Float, default=0.0)
    
    # Search engine
    search_engine = Column(String(50), default="google")  # google, bing, etc
    location = Column(String(100), default="global")
    device = Column(String(20), default="desktop")  # desktop, mobile
    
    # Source
    source = Column(String(50), default="gsc")  # semrush, gsc, serpapi, etc
    
    # Timestamps
    checked_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relacionamentos
    domain = relationship("Domain", back_populates="rankings")
    keyword_obj = relationship("Keyword", back_populates="rankings")


class Backlink(Base):
    """
    Backlinks apontando para o domínio
    """
    __tablename__ = "backlinks"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)
    
    # Link info
    source_url = Column(Text, nullable=False)
    target_url = Column(Text, nullable=False)
    referring_domain = Column(String(255), index=True)
    
    # Métricas
    authority_score = Column(Integer, default=0)
    anchor_text = Column(Text)
    link_type = Column(String(20), default="dofollow")  # dofollow, nofollow
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Datas
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    
    # Source
    source = Column(String(50), default="gsc")  # semrush, ahrefs, gsc, etc
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    domain = relationship("Domain", back_populates="backlinks")


class Page(Base):
    """
    Páginas do site (para análise on-page)
    """
    __tablename__ = "pages"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)
    
    # Page info
    url = Column(Text, nullable=False, unique=True)
    title = Column(String(500))
    meta_description = Column(Text)
    h1 = Column(Text)
    
    # Content
    word_count = Column(Integer, default=0)
    content_hash = Column(String(64))  # Para detectar mudanças
    
    # Technical SEO
    canonical_url = Column(Text)
    robots_meta = Column(String(100))
    has_schema_markup = Column(Boolean, default=False)
    schema_types = Column(JSON)
    
    # Performance
    load_time_ms = Column(Integer)
    page_size_kb = Column(Integer)
    mobile_friendly = Column(Boolean)
    
    # Status codes
    status_code = Column(Integer)
    is_indexable = Column(Boolean, default=True)
    
    # Links
    internal_links_count = Column(Integer, default=0)
    external_links_count = Column(Integer, default=0)
    
    # Images
    images_count = Column(Integer, default=0)
    images_without_alt = Column(Integer, default=0)
    
    # Timestamps
    first_crawled_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_crawled_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    domain = relationship("Domain", back_populates="pages")
