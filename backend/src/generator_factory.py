"""
Column generator factory for FOCUS data generation.

This module provides the factory pattern implementation for creating
and managing column generators.
"""

from typing import List

from logging_config import setup_logging
from column_generators import (
    ColumnGenerator,
    ChargeGenerator,
    CostGenerator,
    DateTimeGenerator,
    ServiceGenerator,
    SKUGenerator,
    CommitmentDiscountGenerator,
    CapacityReservationGenerator,
    PricingGenerator,
    ResourceGenerator,
    AccountGenerator,
    CostDetailsGenerator,
    LocationGenerator,
    ServiceDetailsGenerator,
    UsageMetricsGenerator,
    ProviderBusinessGenerator,
    MetadataGenerator,
    GenericGenerator,
)

logger = setup_logging(__name__)


class ColumnGeneratorFactory:
    """Factory for creating and managing column generators."""
    
    def __init__(self):
        """Initialize the factory with all available generators."""
        self._generators: List[ColumnGenerator] = [
            ChargeGenerator(),
            CostGenerator(),
            DateTimeGenerator(),
            ServiceGenerator(),
            SKUGenerator(),
            CommitmentDiscountGenerator(),
            CapacityReservationGenerator(),
            PricingGenerator(),
            ResourceGenerator(),
            AccountGenerator(),
            CostDetailsGenerator(),
            LocationGenerator(),
            ServiceDetailsGenerator(),
            UsageMetricsGenerator(),
            ProviderBusinessGenerator(),
            MetadataGenerator(),
            GenericGenerator(),  # Must be last as fallback
        ]
    
    def get_generator(self, col_name: str) -> ColumnGenerator:
        """
        Get appropriate generator for column.
        
        Args:
            col_name: Name of the column to generate a value for
            
        Returns:
            ColumnGenerator: The generator that can handle this column
        """
        for generator in self._generators:
            if generator.can_handle(col_name):
                return generator
        
        # This should never happen since GenericGenerator handles all columns
        raise RuntimeError(f"No generator found for column: {col_name}")
    
    def get_supported_columns(self) -> List[str]:
        """
        Get list of all columns supported by specialized generators.
        
        Returns:
            List[str]: List of column names with specialized generators
        """
        supported = []
        for generator in self._generators[:-1]:  # Exclude GenericGenerator
            supported.extend(generator.supported_columns())
        return supported
    
    def register_generator(self, generator: ColumnGenerator) -> None:
        """
        Register a new generator with the factory.
        
        Args:
            generator: The generator to register
        """
        # Insert before the GenericGenerator (which should be last)
        self._generators.insert(-1, generator)


# Global factory instance
_generator_factory = ColumnGeneratorFactory()


def get_generator_factory() -> ColumnGeneratorFactory:
    """Get the global generator factory instance."""
    return _generator_factory