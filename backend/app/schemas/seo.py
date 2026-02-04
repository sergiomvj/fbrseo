from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============= DOMAIN =============

class DomainCreate(BaseModel):
    url: str = Field(..., description="URL do domínio (ex: https://example.com)")
    name: str = Field(..., min_length=1, max_length=255)
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL deve começar com http:// ou https://')
        return v.rstrip('/')


class DomainUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class DomainResponse(BaseModel):
    id: int
    url: str
    name: str
    is_active: bool
    created_at: datetime
    last_crawled_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============= KEYWORD =============

class KeywordCreate(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=500)
    search_volume: int = Field(default=0, ge=0)
    keyword_difficulty: float = Field(default=0.0, ge=0.0, le=100.0)
    cpc: float = Field(default=0.0, ge=0.0)
    competition: Optional[str] = None
    trend_data: Optional[Dict[str, Any]] = None


class KeywordBulkCreate(BaseModel):
    keywords: List[KeywordCreate]


class KeywordResponse(BaseModel):
    id: int
    keyword: str
    search_volume: int
    keyword_difficulty: float
    cpc: float
    competition: Optional[str] = None
    trend_data: Optional[Dict[str, Any]] = None
    source: str
    created_at: datetime
    last_updated: datetime
    
    class Config:
        from_attributes = True


class KeywordWithRanking(KeywordResponse):
    current_position: Optional[int] = None
    previous_position: Optional[int] = None
    position_change: Optional[int] = None
    ranking_url: Optional[str] = None


# ============= RANKING =============

class RankingCreate(BaseModel):
    keyword: str
    position: int = Field(..., ge=0)
    url: Optional[str] = None
    search_engine: str = Field(default="google")
    location: str = Field(default="global")
    device: str = Field(default="desktop")


class RankingResponse(BaseModel):
    id: int
    keyword: str
    position: int
    previous_position: int
    url: Optional[str] = None
    estimated_traffic: float
    visibility_score: float
    search_engine: str
    location: str
    device: str
    source: str
    checked_at: datetime
    
    class Config:
        from_attributes = True


class RankingChange(BaseModel):
    keyword: str
    current_position: int
    previous_position: int
    change: int
    change_percent: Optional[float] = None
    alert_type: str  # gain, loss, stable
    url: Optional[str] = None


# ============= BACKLINK =============

class BacklinkCreate(BaseModel):
    source_url: str
    target_url: str
    referring_domain: str
    authority_score: int = Field(default=0, ge=0, le=100)
    anchor_text: Optional[str] = None
    link_type: str = Field(default="dofollow")


class BacklinkResponse(BaseModel):
    id: int
    source_url: str
    target_url: str
    referring_domain: str
    authority_score: int
    anchor_text: Optional[str] = None
    link_type: str
    is_active: bool
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    source: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= PAGE (On-Page Analysis) =============

class PageAnalysisResponse(BaseModel):
    id: int
    url: str
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1: Optional[str] = None
    word_count: int
    status_code: Optional[int] = None
    is_indexable: bool
    canonical_url: Optional[str] = None
    robots_meta: Optional[str] = None
    has_schema_markup: bool
    schema_types: Optional[List[str]] = None
    load_time_ms: Optional[int] = None
    page_size_kb: Optional[int] = None
    mobile_friendly: Optional[bool] = None
    internal_links_count: int
    external_links_count: int
    images_count: int
    images_without_alt: int
    last_crawled_at: datetime
    
    # Issues detectados
    issues: Optional[List[Dict[str, Any]]] = None
    score: Optional[int] = None  # Score de 0-100
    
    class Config:
        from_attributes = True


# ============= IMPORT =============

class ImportResult(BaseModel):
    success: bool
    total_imported: int
    source: str
    import_type: str  # keywords, rankings, backlinks
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


# ============= ENRICHED DATA =============

class EnrichedKeyword(BaseModel):
    keyword: str
    # Data from SemRush
    search_volume: int
    keyword_difficulty: float
    cpc: float
    # Data from GSC (real)
    real_impressions: Optional[int] = None
    real_clicks: Optional[int] = None
    real_ctr: Optional[float] = None
    real_position: Optional[float] = None
    # Combined insights
    volume_vs_impressions_ratio: Optional[float] = None
    data_freshness: str  # semrush, gsc, enriched


# ============= ANALYTICS =============

class DomainAnalytics(BaseModel):
    domain_id: int
    total_keywords: int
    avg_position: float
    total_backlinks: int
    organic_traffic_trend: List[Dict[str, Any]]
    top_keywords: List[KeywordWithRanking]
    recent_ranking_changes: List[RankingChange]
    backlinks_growth: Dict[str, int]
