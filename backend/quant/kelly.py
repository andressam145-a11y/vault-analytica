class KellyCriterion:
    """
    Motor de Gestión de Riesgo Institucional.
    Determina el tamaño de la posición basándose en la ventaja estadística (Edge).
    'Primero lo primero': No arriesgar lo que no se puede perder.
    """

    @staticmethod
    def calculate_allocation(win_probability: float, risk_reward_ratio: float, fraction_multiplier: float = 0.5) -> float:
        """
        Fórmula de Kelly: f* = (p * b - q) / b
        f* = Fracción óptima del capital
        p = Probabilidad de ganar (decimal 0.0 - 1.0)
        q = Probabilidad de perder (1 - p)
        b = Ratio de Riesgo/Beneficio (ej. si ganas 2 y pierdes 1, b = 2)
        fraction_multiplier = El 'Half-Kelly' (0.5) es el estándar institucional para evitar volatilidad excesiva.
        """
        if risk_reward_ratio <= 0:
            return 0.0
            
        p = win_probability
        q = 1.0 - p
        b = risk_reward_ratio
        
        # Fórmula Core de Kelly
        kelly_f = (p * b - q) / b
        
        # Aplicamos el multiplicador fraccional (Prudencia institucional)
        final_allocation = max(0.0, kelly_f * fraction_multiplier)
        
        # Limitamos a un máximo de 20% por posición para evitar riesgos sistémicos (Regla de Oro)
        return min(20.0, final_allocation * 100)

    @staticmethod
    def get_contextual_win_rate(sigma_deviation: float, rvol: float) -> float:
        """
        Ajusta la probabilidad de éxito basándose en la fuerza del filtro de Vault-Analytica.
        """
        base_rate = 0.50 # Probabilidad base del mercado (azar)
        
        # Si estamos en 2-Sigma, la probabilidad estadística de retorno a la media o continuación fuerte aumenta
        sigma_bonus = 0.10 if abs(sigma_deviation) >= 2.0 else 0.05
        # Si hay volumen relativo fuerte, hay confirmación de 'manos fuertes'
        rvol_bonus = 0.05 if rvol >= 2.0 else 0.0
        
        return base_rate + sigma_bonus + rvol_bonus
