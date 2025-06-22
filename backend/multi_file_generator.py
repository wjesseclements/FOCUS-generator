import os
import uuid
import zipfile
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd

from backend.curGen import generate_focus_data
from backend.validate_cur import validate_focus_df

logger = logging.getLogger(__name__)

class MultiFileGenerator:
    """Generates multiple FOCUS files for multi-cloud and multi-month scenarios."""
    
    def __init__(self):
        from backend.trend_generator import TrendGenerator
        self.trend_generator = TrendGenerator()
    
    def generate_multi_cloud_files(
        self,
        providers: List[str],
        profile: str,
        distribution: str,
        row_count: int,
        base_date: datetime = None
    ) -> Dict[str, pd.DataFrame]:
        """Generate separate FOCUS files for each cloud provider."""
        
        if base_date is None:
            base_date = datetime.now().replace(day=1)  # First day of current month
        
        files = {}
        
        for provider in providers:
            logger.info(f"Generating FOCUS data for {provider}")
            
            # Generate provider-specific data
            df = generate_focus_data(
                row_count=row_count,
                profile=profile,
                distribution=distribution,
                cloud_provider=provider.upper(),
                billing_period=base_date
            )
            
            # Validate the data
            validate_focus_df(df)
            
            # Create filename
            month_str = base_date.strftime("%Y-%m")
            filename = f"{provider}-focus-{month_str}.csv"
            
            files[filename] = df
            logger.info(f"Generated {len(df)} rows for {provider}")
        
        return files
    
    def generate_trend_files(
        self,
        providers: List[str],
        profile: str,
        distribution: str,
        row_count: int,
        trend_options: Dict[str, Any],
        base_date: datetime = None
    ) -> Dict[str, pd.DataFrame]:
        """Generate multi-month trend files for selected providers."""
        
        if base_date is None:
            base_date = datetime.now().replace(day=1)
        
        files = {}
        month_count = trend_options.get('monthCount', 6)
        scenario = trend_options.get('scenario', 'linear')
        parameters = trend_options.get('parameters', {})
        
        logger.info(f"Generating {month_count} months of {scenario} trend data for {len(providers)} providers")
        
        for provider in providers:
            # Generate trend data for this provider
            monthly_dataframes = self.trend_generator.generate_trend(
                provider=provider.upper(),
                profile=profile,
                distribution=distribution,
                row_count=row_count,
                month_count=month_count,
                scenario=scenario,
                parameters=parameters,
                start_date=base_date
            )
            
            # Add each month's data to files
            for month_index, df in enumerate(monthly_dataframes):
                current_date = base_date + timedelta(days=32 * month_index)
                current_date = current_date.replace(day=1)  # First day of month
                month_str = current_date.strftime("%Y-%m")
                filename = f"{provider}-focus-{month_str}.csv"
                
                files[filename] = df
                logger.info(f"Generated {len(df)} rows for {provider} {month_str}")
        
        return files
    
    def create_zip_package(
        self,
        files: Dict[str, pd.DataFrame],
        trend_options: Dict[str, Any] = None,
        temp_dir: str = None
    ) -> str:
        """Create a ZIP file containing all generated CSV files."""
        
        if temp_dir is None:
            temp_dir = os.path.join(os.path.dirname(__file__), "files")
        
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create unique ZIP filename
        zip_filename = f"focus-data-{uuid.uuid4().hex[:8]}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add CSV files
            for filename, df in files.items():
                csv_data = df.to_csv(index=False)
                zipf.writestr(filename, csv_data)
                logger.info(f"Added {filename} to ZIP package")
            
            # Add manifest file for trend data
            if trend_options:
                manifest = {
                    "generated_at": datetime.now().isoformat(),
                    "file_count": len(files),
                    "trend_scenario": trend_options.get('scenario'),
                    "month_count": trend_options.get('monthCount'),
                    "parameters": trend_options.get('parameters', {}),
                    "files": list(files.keys()),
                    "description": f"Multi-month FOCUS data with {trend_options.get('scenario')} trend pattern"
                }
                zipf.writestr("manifest.json", json.dumps(manifest, indent=2))
                logger.info("Added manifest.json to ZIP package")
        
        logger.info(f"Created ZIP package: {zip_filename} with {len(files)} files")
        return zip_filename
    
    def get_file_summary(self, files: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Get summary statistics for generated files."""
        
        total_rows = sum(len(df) for df in files.values())
        providers = set()
        months = set()
        
        for filename in files.keys():
            # Parse filename: provider-focus-YYYY-MM.csv
            parts = filename.replace('.csv', '').split('-')
            if len(parts) >= 3:
                providers.add(parts[0])
                months.add(f"{parts[2]}-{parts[3]}")
        
        return {
            "file_count": len(files),
            "total_rows": total_rows,
            "providers": sorted(list(providers)),
            "months": sorted(list(months)),
            "avg_rows_per_file": round(total_rows / len(files)) if files else 0
        }