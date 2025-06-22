import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

from backend.curGen import generate_focus_data

logger = logging.getLogger(__name__)

class TrendGenerator:
    """Generates multi-month FOCUS data with various trend patterns."""
    
    def __init__(self):
        self.base_multiplier = 1.0
    
    def generate_trend(
        self,
        provider: str,
        profile: str,
        distribution: str,
        row_count: int,
        month_count: int,
        scenario: str,
        parameters: Dict[str, Any],
        start_date: datetime
    ) -> List[pd.DataFrame]:
        """Generate trend data based on scenario."""
        
        logger.info(f"Generating {scenario} trend for {provider} over {month_count} months")
        
        # Generate cost multipliers for each month based on scenario
        multipliers = self._calculate_multipliers(scenario, month_count, parameters)
        
        dataframes = []
        
        for month_index in range(month_count):
            # Calculate current date
            current_date = start_date + timedelta(days=32 * month_index)
            current_date = current_date.replace(day=1)
            
            # Generate base data for this month
            df = generate_focus_data(
                row_count=row_count,
                profile=profile,
                distribution=distribution,
                cloud_provider=provider,
                billing_period=current_date
            )
            
            # Apply trend multiplier to costs
            cost_multiplier = multipliers[month_index]
            self._apply_cost_multiplier(df, cost_multiplier, month_index + 1)
            
            dataframes.append(df)
            logger.info(f"Generated month {month_index + 1} with {cost_multiplier:.2f}x multiplier")
        
        return dataframes
    
    def _calculate_multipliers(
        self,
        scenario: str,
        month_count: int,
        parameters: Dict[str, Any]
    ) -> List[float]:
        """Calculate cost multipliers for each month based on scenario."""
        
        if scenario == "linear":
            return self._linear_growth_multipliers(month_count, parameters)
        elif scenario == "seasonal":
            return self._seasonal_multipliers(month_count, parameters)
        elif scenario == "stepChange":
            return self._step_change_multipliers(month_count, parameters)
        elif scenario == "anomaly":
            return self._anomaly_multipliers(month_count, parameters)
        else:
            logger.warning(f"Unknown scenario: {scenario}, using linear growth")
            return self._linear_growth_multipliers(month_count, parameters)
    
    def _linear_growth_multipliers(
        self,
        month_count: int,
        parameters: Dict[str, Any]
    ) -> List[float]:
        """Generate linear growth multipliers."""
        
        growth_rate = float(parameters.get('growthRate', 10)) / 100  # Convert percentage
        multipliers = []
        
        for month in range(month_count):
            # Linear growth: 1.0, 1.1, 1.2, etc. (with 10% growth)
            multiplier = 1.0 + (growth_rate * month)
            # Add small random variation (±5%)
            variation = random.uniform(-0.05, 0.05)
            multiplier += variation
            multipliers.append(max(0.1, multiplier))  # Ensure positive
        
        logger.info(f"Linear growth: {growth_rate*100}% per month")
        return multipliers
    
    def _seasonal_multipliers(
        self,
        month_count: int,
        parameters: Dict[str, Any]
    ) -> List[float]:
        """Generate seasonal pattern multipliers."""
        
        baseline_variation = float(parameters.get('baselineVariation', 10)) / 100
        peak_multiplier = float(parameters.get('peakMultiplier', 2.5))
        
        multipliers = []
        
        # Create seasonal pattern (peaks in Nov/Dec - months 11,12 or last 2 months)
        peak_months = set()
        if month_count >= 11:
            peak_months = {10, 11}  # Nov, Dec (0-indexed)
        else:
            # Peak in last 2 months if less than 12 months
            peak_months = {month_count - 2, month_count - 1}
        
        for month in range(month_count):
            if month in peak_months:
                # Peak months
                base_multiplier = peak_multiplier
            else:
                # Normal months with slight growth
                base_multiplier = 1.0 + (month * 0.02)  # 2% monthly growth
            
            # Add baseline variation
            variation = random.uniform(-baseline_variation, baseline_variation)
            multiplier = base_multiplier + variation
            multipliers.append(max(0.1, multiplier))
        
        logger.info(f"Seasonal pattern: {peak_multiplier}x peaks, {baseline_variation*100}% variation")
        return multipliers
    
    def _step_change_multipliers(
        self,
        month_count: int,
        parameters: Dict[str, Any]
    ) -> List[float]:
        """Generate step change multipliers."""
        
        step_month = int(parameters.get('stepMonth', 4)) - 1  # Convert to 0-indexed
        step_multiplier = float(parameters.get('stepMultiplier', 2.0))
        
        multipliers = []
        
        for month in range(month_count):
            if month < step_month:
                # Before step change - normal with small growth
                base_multiplier = 1.0 + (month * 0.02)
            else:
                # After step change - higher baseline
                months_after_step = month - step_month
                base_multiplier = step_multiplier + (months_after_step * 0.02)
            
            # Add small random variation
            variation = random.uniform(-0.05, 0.05)
            multiplier = base_multiplier + variation
            multipliers.append(max(0.1, multiplier))
        
        logger.info(f"Step change: {step_multiplier}x increase at month {step_month + 1}")
        return multipliers
    
    def _anomaly_multipliers(
        self,
        month_count: int,
        parameters: Dict[str, Any]
    ) -> List[float]:
        """Generate anomaly pattern multipliers."""
        
        anomaly_month = int(parameters.get('anomalyMonth', 6)) - 1  # Convert to 0-indexed
        anomaly_multiplier = float(parameters.get('anomalyMultiplier', 10.0))
        
        multipliers = []
        
        for month in range(month_count):
            if month == anomaly_month:
                # Anomaly month - huge spike
                multiplier = anomaly_multiplier
            else:
                # Normal months with slight growth
                base_multiplier = 1.0 + (month * 0.02)
                # Add normal variation
                variation = random.uniform(-0.05, 0.05)
                multiplier = base_multiplier + variation
            
            multipliers.append(max(0.1, multiplier))
        
        logger.info(f"Anomaly pattern: {anomaly_multiplier}x spike at month {anomaly_month + 1}")
        return multipliers
    
    def _apply_cost_multiplier(
        self,
        df: pd.DataFrame,
        multiplier: float,
        month_number: int
    ) -> None:
        """Apply cost multiplier to all cost columns in the DataFrame."""
        
        cost_columns = [
            'BilledCost',
            'EffectiveCost', 
            'UnblendedCost',
            'ListCost'
        ]
        
        for col in cost_columns:
            if col in df.columns:
                df[col] = df[col] * multiplier
        
        # Update billing period to reflect the correct month
        if 'BillingPeriodStart' in df.columns:
            # This would be set by the generate_focus_data function
            pass
        
        logger.debug(f"Applied {multiplier:.2f}x multiplier to costs for month {month_number}")