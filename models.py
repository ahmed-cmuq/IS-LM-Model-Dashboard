from dataclasses import dataclass
from typing import Dict
import numpy as np

@dataclass
class KCParams:
    """
    A dataclass to hold all the parameters of the Keynesian Cross and IS-LM model.
    This makes passing parameters between functions cleaner and less error-prone.
    """
    a: float          # Autonomous consumption
    c: float          # Marginal propensity to consume
    T: float          # Taxes
    G: float          # Government spending
    i: float          # Current interest rate
    i_max: float      # Max interest rate for charts
    b0: float         # Autonomous investment
    b1: float         # Marginal propensity to invest (from income Y)
    b2: float         # Investment sensitivity to interest rate i

def kc_equilibrium(p: KCParams) -> Dict[str, float]:
    """
    Calculates the equilibrium income (Y*) in the Keynesian Cross model for a given
    set of parameters, including a specific interest rate 'i'.

    The model is defined by:
    Z(Y) = a + c(Y - T) + I + G
    I = b0 + b1*Y - b2*i
    => Z(Y) = (a - cT + b0 - b2*i + G) + (c + b1)Y
    
    Equilibrium Y* solves Y = Z(Y):
    => (1 - c - b1)Y = a - cT + b0 - b2*i + G
    """
    # The denominator of the multiplier. Must be > 0 for a stable economy.
    denom = 1.0 - p.c - p.b1
    if abs(denom) < 1e-9:
        # Avoid division by zero if c + b1 is very close to 1
        denom = 1e-9
    
    # The vertical intercept of the Aggregate Demand (AD) curve
    intercept = p.a - p.c * p.T + p.b0 - p.b2 * p.i + p.G
    
    # Equilibrium income (Y*)
    Y_star = intercept / denom
    
    return {
        "Y_star": Y_star,
        "AD_intercept": intercept,
        "AD_slope": p.c + p.b1
    }

def kc_locus(p: KCParams, i_grid: np.ndarray) -> np.ndarray:
    """
    Calculates the IS curve, which is the locus of equilibrium points Y*(i)
    for a given grid of interest rates. This function shows how equilibrium
    income changes as the interest rate changes, holding all other parameters constant.
    """
    # The denominator of the multiplier
    denom = 1.0 - p.c - p.b1
    if abs(denom) < 1e-9:
        denom = 1e-9
        
    # Part of the AD intercept that does not depend on the interest rate 'i'
    intercept0 = p.a - p.c * p.T + p.b0 + p.G
    
    # Calculate Y*(i) for each interest rate in the provided grid
    return (intercept0 - p.b2 * i_grid) / denom
