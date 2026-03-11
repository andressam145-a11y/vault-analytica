import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.quant.statistics import QuantitativeEngine
from backend.nlp.auditor import ForensicAuditor
from backend.nlp.sec_scraper import SECScraper
from backend.quant.kelly import KellyCriterion

app = FastAPI(
    title="Vault-Analytica API Core",
    description="Endpoint institucional para evaluación de activos bajo rígidos estándares cuánticos y auditoría forense.",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EvaluationRequest(BaseModel) :
    ticker: str
    news_text: str | None = None
    force_sec_update: bool = False

class RiskReport(BaseModel) :
    ticker: str
    status: str
    sigma_deviation: float
    relative_volume: float
    forensic_clear: bool
    kelly_allocation_percentage: float
    message: str

@app.post("/evaluate_asset", response_model=RiskReport)
def evaluate_asset(req: EvaluationRequest):
    ticker = req.ticker.upper()
    
    # 1. Validación Cuantitativa
    engine = QuantitativeEngine(ticker=ticker)
    quant_results = engine.execute_strict_validation()
    
    if quant_results["status"] == "FAIL":
        raise HTTPException(status_code=400, detail=quant_results["reason"])

    # 2. Validación Forense Automática (SEC)
    auditor = ForensicAuditor()
    scraper = SECScraper()
    
    # Si el usuario pide analizar noticia propia o el sistema decide auditar la SEC
    text_to_analyze = req.news_text or ""
    
    if req.force_sec_update:
        scraper.download_latest_filings(ticker, amount=1)
        text_to_analyze += scraper.extract_text_for_analysis(ticker)
    
    is_forensic_clear = True
    if text_to_analyze:
        forensic_report = auditor.analyze_text(text_to_analyze, source="OFFICIAL")
        is_forensic_clear = not auditor.get_integrity_lock(forensic_report)

    # 3. Cálculo de Gestión de Riesgo (Kelly)
    win_rate = KellyCriterion.get_contextual_win_rate(
        quant_results["sigma_deviation"], 
        quant_results["relative_volume"]
    )
    # Asumimos un risk/reward institucional de 2.0 (Ganas 2 por cada 1 arriesgado)
    allocation = KellyCriterion.calculate_allocation(win_rate, risk_reward_ratio=2.0)

    # Estado Final
    final_status = "APPROVED" if (quant_results["status"] == "APPROVED" and is_forensic_clear) else "REJECTED"
    
    return RiskReport(
        ticker=ticker,
        status=final_status,
        sigma_deviation=quant_results["sigma_deviation"],
        relative_volume=quant_results["relative_volume"],
        forensic_clear=is_forensic_clear,
        kelly_allocation_percentage=allocation if final_status == "APPROVED" else 0.0,
        message=quant_results["message"]
    )
