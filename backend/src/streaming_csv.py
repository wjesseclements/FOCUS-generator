"""
Streaming CSV generation for large datasets to improve memory efficiency.
"""

import csv
import io
import gzip
import tempfile
import os
from typing import Generator, List, Dict, Any, Optional
from contextlib import contextmanager
from dataclasses import dataclass
from fastapi.responses import StreamingResponse
import pandas as pd

from logging_config import setup_logging
from config import get_settings

logger = setup_logging(__name__)
settings = get_settings()


@dataclass
class StreamingConfig:
    """Configuration for streaming CSV generation."""
    chunk_size: int = 10000
    use_compression: bool = True
    buffer_size: int = 8192
    temp_dir: Optional[str] = None


class StreamingCSVWriter:
    """Efficient streaming CSV writer for large datasets."""
    
    def __init__(self, config: StreamingConfig = None):
        self.config = config or StreamingConfig()
        self.temp_file = None
        self.writer = None
        self.file_handle = None
        self.row_count = 0
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close()
        
    def create_temp_file(self) -> str:
        """Create a temporary file for streaming."""
        temp_dir = self.config.temp_dir or tempfile.gettempdir()
        
        # Create temporary file
        fd, temp_path = tempfile.mkstemp(
            suffix='.csv.gz' if self.config.use_compression else '.csv',
            dir=temp_dir
        )
        
        # Close the file descriptor and reopen with appropriate mode
        os.close(fd)
        
        if self.config.use_compression:
            self.file_handle = gzip.open(temp_path, 'wt', newline='', encoding='utf-8')
        else:
            self.file_handle = open(temp_path, 'w', newline='', encoding='utf-8')
        
        self.temp_file = temp_path
        return temp_path
        
    def write_headers(self, headers: List[str]):
        """Write CSV headers."""
        if not self.file_handle:
            raise RuntimeError("No file handle available. Call create_temp_file() first.")
            
        self.writer = csv.writer(self.file_handle)
        self.writer.writerow(headers)
        
    def write_row(self, row: List[Any]):
        """Write a single row."""
        if not self.writer:
            raise RuntimeError("Writer not initialized. Call write_headers() first.")
            
        self.writer.writerow(row)
        self.row_count += 1
        
        # Flush buffer periodically
        if self.row_count % self.config.chunk_size == 0:
            self.file_handle.flush()
            logger.debug(f"Flushed buffer at row {self.row_count}")
            
    def write_rows(self, rows: List[List[Any]]):
        """Write multiple rows efficiently."""
        if not self.writer:
            raise RuntimeError("Writer not initialized. Call write_headers() first.")
            
        for row in rows:
            self.write_row(row)
            
    def close(self):
        """Close the writer and file handle."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
            
        if self.writer:
            self.writer = None
            
    def get_file_size(self) -> int:
        """Get the current file size in bytes."""
        if not self.temp_file or not os.path.exists(self.temp_file):
            return 0
        return os.path.getsize(self.temp_file)
        
    def get_temp_file_path(self) -> str:
        """Get the temporary file path."""
        return self.temp_file


class StreamingDataGenerator:
    """Generator for streaming large datasets efficiently."""
    
    def __init__(self, config: StreamingConfig = None):
        self.config = config or StreamingConfig()
        
    def generate_streaming_csv(self, 
                             data_generator: Generator[List[Any], None, None],
                             headers: List[str],
                             total_rows: int = None) -> StreamingCSVWriter:
        """
        Generate streaming CSV from a data generator.
        
        Args:
            data_generator: Generator that yields rows of data
            headers: CSV headers
            total_rows: Expected total rows (for progress tracking)
            
        Returns:
            StreamingCSVWriter instance
        """
        writer = StreamingCSVWriter(self.config)
        
        try:
            # Create temporary file
            temp_file = writer.create_temp_file()
            logger.info(f"Created temporary file: {temp_file}")
            
            # Write headers
            writer.write_headers(headers)
            
            # Write data in chunks
            rows_processed = 0
            chunk_buffer = []
            
            for row in data_generator:
                chunk_buffer.append(row)
                rows_processed += 1
                
                # Write chunk when buffer is full
                if len(chunk_buffer) >= self.config.chunk_size:
                    writer.write_rows(chunk_buffer)
                    chunk_buffer = []
                    
                    # Log progress
                    if total_rows:
                        progress = (rows_processed / total_rows) * 100
                        logger.info(f"Progress: {progress:.1f}% ({rows_processed}/{total_rows} rows)")
                    
                    # Check file size limit
                    file_size_mb = writer.get_file_size() / (1024 * 1024)
                    if file_size_mb > settings.max_file_size_mb:
                        raise RuntimeError(f"File size exceeded limit: {file_size_mb:.1f}MB > {settings.max_file_size_mb}MB")
            
            # Write remaining buffer
            if chunk_buffer:
                writer.write_rows(chunk_buffer)
                
            writer.close()
            
            logger.info(f"Generated CSV with {rows_processed} rows, file size: {writer.get_file_size() / (1024 * 1024):.1f}MB")
            return writer
            
        except Exception as e:
            writer.close()
            # Clean up temporary file on error
            if writer.temp_file and os.path.exists(writer.temp_file):
                os.unlink(writer.temp_file)
            raise e


@contextmanager
def streaming_csv_response(temp_file_path: str, 
                          filename: str = "data.csv",
                          cleanup: bool = True):
    """
    Context manager for streaming CSV response.
    
    Args:
        temp_file_path: Path to temporary CSV file
        filename: Download filename
        cleanup: Whether to clean up temp file after streaming
        
    Yields:
        StreamingResponse
    """
    try:
        def file_generator():
            with open(temp_file_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk
        
        # Determine content type
        content_type = "application/gzip" if temp_file_path.endswith('.gz') else "text/csv"
        
        response = StreamingResponse(
            file_generator(),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Encoding": "gzip" if temp_file_path.endswith('.gz') else "identity"
            }
        )
        
        yield response
        
    finally:
        # Clean up temporary file
        if cleanup and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.error(f"Failed to clean up temporary file {temp_file_path}: {e}")


def create_data_generator(df: pd.DataFrame, chunk_size: int = 10000) -> Generator[List[Any], None, None]:
    """
    Create a generator from pandas DataFrame for streaming.
    
    Args:
        df: DataFrame to stream
        chunk_size: Size of chunks to process
        
    Yields:
        List of values for each row
    """
    for start_idx in range(0, len(df), chunk_size):
        end_idx = min(start_idx + chunk_size, len(df))
        chunk = df.iloc[start_idx:end_idx]
        
        for _, row in chunk.iterrows():
            yield row.tolist()


def estimate_csv_size(num_rows: int, num_columns: int, avg_cell_size: int = 20) -> int:
    """
    Estimate CSV file size in bytes.
    
    Args:
        num_rows: Number of rows
        num_columns: Number of columns
        avg_cell_size: Average size per cell in bytes
        
    Returns:
        Estimated file size in bytes
    """
    # Estimate: (avg_cell_size * num_columns + delimiters + newline) * num_rows
    row_size = (avg_cell_size * num_columns) + num_columns + 1  # +1 for newline
    return row_size * num_rows