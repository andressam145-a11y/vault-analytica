import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class QuantitativeEngine:
    """
    Motor Estadístico Estricto de Vault-Analytica
    - Rechaza cualquier análisis basado en opiniones.
    - Exclusivamente opera bajo umbrales probabilísticos (2-Sigma) y RVOL.
    """
    
    def __init__(self, ticker: str, history_days: int = 180):
        self.ticker = ticker.upper()
        self.history_days = history_days
        self.data = pd.DataFrame()
        
    def fetch_market_data(self) -> bool:
        """Descarga el Histórico del Activo para analizar sus Desviaciones."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.history_days)
            
            # Traer datos con yfinance
            asset = yf.Ticker(self.ticker)
            df = asset.history(start=start_date, end=end_date)
            
            if df.empty:
                print(f"[RECHAZADO] Datos insuficientes para el ticker {self.ticker}.")
                return False
                
            self.data = df
            return True
            
        except Exception as e:
            print(f"[ERROR DEL MOTOR] Falla en conexión de datos: {e}")
            return False

    def check_two_sigma_deviation(self, window: int = 20) -> tuple[bool, float, float]:
        """
        Calcula si el precio de cierre actual superó la banda de 2 Desviaciones Estándar
        respecto a la Media Móvil Simple de 20 períodos.
        Retorna: (Aprobado, Precio de Cierre, Desviación Sigma Actual)
        """
        if len(self.data) < window:
            return False, 0.0, 0.0
            
        # Calcular SMA de 20 días
        self.data['SMA_20'] = self.data['Close'].rolling(window=window).mean()
        # Calcular Desviación Estándar de 20 días
        self.data['STD_20'] = self.data['Close'].rolling(window=window).std()
        
        # Bandas Bollinger (2 Sigma)
        self.data['Upper_Band'] = self.data['SMA_20'] + (self.data['STD_20'] * 2)
        self.data['Lower_Band'] = self.data['SMA_20'] - (self.data['STD_20'] * 2)
        
        # Extraer los datos más recientes
        latest = self.data.iloc[-1]
        current_close = latest['Close']
        upper_band = latest['Upper_Band']
        lower_band = latest['Lower_Band']
        
        # Calcular a cuántos sigmas está el precio actual (- o +)
        sigma_deviation = (current_close - latest['SMA_20']) / latest['STD_20']
        
        # La regla dura dice: Debe haber un rompimiento estadístico anormal (> 2 Sigma o < -2 Sigma)
        if current_close > upper_band or current_close < lower_band:
            return True, current_close, sigma_deviation
            
        return False, current_close, sigma_deviation

    def check_relative_volume(self, window: int = 20, threshold: float = 2.0) -> tuple[bool, float]:
        """
        Calcula el RVOL (Relative Volume). Si el interés del mercado no es real (anormal),
        no importa lo que digan las velas.
        Retorna: (Aprobado, RVOL Actual)
        """
        if len(self.data) < window:
            return False, 0.0
            
        # El volumen medio de los últimos [window] días
        self.data['Vol_SMA'] = self.data['Volume'].rolling(window=window).mean()
        
        latest = self.data.iloc[-1]
        current_volume = latest['Volume']
        avg_volume = latest['Vol_SMA']
        
        if avg_volume == 0:
            return False, 0.0
            
        rvol = current_volume / avg_volume
        
        # Regla dura: Sólo si volumen relativo supera el threshold
        return (rvol >= threshold), rvol

    def execute_strict_validation(self) -> dict:
        """
        Ejecuta TODOS los filtros de la Válvula Cuantitativa (Fase 1).
        Si alguna matriz falla, el Trade es abortado sistemáticamente.
        """
        if not self.fetch_market_data():
            return {"status": "FAIL", "reason": "No Data"}
            
        sigma_pass, current_price, sigma_dev = self.check_two_sigma_deviation()
        rvol_pass, rvol = self.check_relative_volume()
        
        # Regla de Hierro: Cero flexibilidad.
        is_approved = sigma_pass and rvol_pass
        
        return {
            "status": "APPROVED" if is_approved else "REJECTED_BY_QUANTS",
            "ticker": self.ticker,
            "closing_price": current_price,
            "sigma_deviation": sigma_dev,
            "relative_volume": rvol,
            "passed_2sigma_test": sigma_pass,
            "passed_rvol_test": rvol_pass,
            "message": "Condición Estadística Cumplida." if is_approved else "Falla en filtro institucional. Posible manipulación de Retail u Oscilación Estándar."
        }

# --- TEST RÁPIDO DEL MOTOR CUANTITATIVO ---
# Si ejecutas este archivo, puedes probar un ticker (ejemplo: 'NVDA' o 'TSLA')
if __name__ == "__main__":
    test_ticker = "SPY" # S&P 500 ETF
    print(f"=== INICIANDO MOTOR VAULT-ANALYTICA PARA: {test_ticker} ===")
    
    engine = QuantitativeEngine(ticker=test_ticker)
    resultados = engine.execute_strict_validation()
    
    print("\n[RESULTADOS DEL FILTRO DURO]")
    for key, value in resultados.items():
        print(f" > {key}: {value}")
