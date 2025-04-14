import pandas as pd
from typing import Optional, Dict, Any

class FlexoUVCuring:
    def __init__(self, anilox_data_path: str = "SMARTcure-Anilox-information_NL.docx"):
        """
        Initialize the FlexoUVCuring class with improved error handling.
        """
        self.anilox_data = None
        try:
            self.anilox_data = self.load_anilox_data(anilox_data_path)
        except Exception as e:
            print(f"Warning: Could not load anilox data: {str(e)}")

        # Define transfer ranges for different rasterwals types
        self.transfer_ranges = {
            'Hexagonal (20-30% transfer)': (0.20, 0.30),
            'Hachure / Trihelical (35-40% transfer)': (0.35, 0.40),
            'ART / TIF (40-50% transfer)': (0.40, 0.50),
            'GTT UniCoat (25-30% transfer)': (0.25, 0.30)
        }

        # Define volume specifications per rasterwals type
        self.volume_specs = {
            'Hexagonal (20-30% transfer)': [
                {'volume': '7 cm³/m²', 'bcm': 4.5, 'lines': '160 L/cm', 'transfer': '1.8 g/m²'},
                {'volume': '10 cm³/m²', 'bcm': 6.4, 'lines': '120 L/cm', 'transfer': '2.5 g/m²'},
                {'volume': '13 cm³/m²', 'bcm': 8.4, 'lines': '100 L/cm', 'transfer': '3.25 g/m²'},
                {'volume': '16 cm³/m²', 'bcm': 10.3, 'lines': '80 L/cm', 'transfer': '4.0 g/m²'},
                {'volume': '20 cm³/m²', 'bcm': 12.9, 'lines': '60 L/cm', 'transfer': '5.0 g/m²'}
            ],
            'Hachure / Trihelical (35-40% transfer)': [
                {'volume': '7 cm³/m²', 'bcm': 4.5, 'lines': '160 L/cm', 'transfer': '2.3 g/m²'},
                {'volume': '10 cm³/m²', 'bcm': 6.4, 'lines': '120 L/cm', 'transfer': '3.3 g/m²'},
                {'volume': '13 cm³/m²', 'bcm': 8.4, 'lines': '100 L/cm', 'transfer': '4.3 g/m²'},
                {'volume': '16 cm³/m²', 'bcm': 10.3, 'lines': '80 L/cm', 'transfer': '5.3 g/m²'},
                {'volume': '20 cm³/m²', 'bcm': 12.9, 'lines': '60 L/cm', 'transfer': '6.5 g/m²'}
            ],
            'ART / TIF (40-50% transfer)': [
                {'volume': '7 cm³/m²', 'bcm': 4.5, 'lines': '160 L/cm', 'transfer': '2.7 g/m²'},
                {'volume': '10 cm³/m²', 'bcm': 6.4, 'lines': '120 L/cm', 'transfer': '3.7 g/m²'},
                {'volume': '13 cm³/m²', 'bcm': 8.4, 'lines': '100 L/cm', 'transfer': '5.0 g/m²'},
                {'volume': '16 cm³/m²', 'bcm': 10.3, 'lines': '80 L/cm', 'transfer': '6.0 g/m²'},
                {'volume': '20 cm³/m²', 'bcm': 12.9, 'lines': '60 L/cm', 'transfer': '7.5 g/m²'}
            ],
            'GTT UniCoat (25-30% transfer)': [
                {'volume': 'S', 'bcm': 4.5, 'lines': 'GTT', 'transfer': '1.8 g/m²', 'actual_volume': '7 cm³/m²'},
                {'volume': 'M', 'bcm': 6.4, 'lines': 'GTT', 'transfer': '2.5 g/m²', 'actual_volume': '10 cm³/m²'},
                {'volume': 'L', 'bcm': 8.4, 'lines': 'GTT', 'transfer': '3.25 g/m²', 'actual_volume': '13 cm³/m²'},
                {'volume': 'XL', 'bcm': 10.3, 'lines': 'GTT', 'transfer': '4.0 g/m²', 'actual_volume': '16 cm³/m²'},
                {'volume': 'XXL', 'bcm': 12.9, 'lines': 'GTT', 'transfer': '5.0 g/m²', 'actual_volume': '20 cm³/m²'}
            ]
        }

    def get_volume_specs(self, rasterwals_type: str) -> list:
        """Get volume specifications for a specific rasterwals type."""
        return self.volume_specs.get(rasterwals_type, [])

    def get_bcm_from_volume(self, rasterwals_type: str, selected_volume: str) -> float:
        """Get BCM value for selected volume and rasterwals type."""
        specs = self.volume_specs.get(rasterwals_type, [])
        for spec in specs:
            if spec['volume'] == selected_volume:
                return spec['bcm']
        return 0.0

    def get_transfer_from_volume(self, rasterwals_type: str, selected_volume: str) -> str:
        """Get transfer value for selected volume and rasterwals type."""
        specs = self.volume_specs.get(rasterwals_type, [])
        for spec in specs:
            if spec['volume'] == selected_volume:
                return spec['transfer']
        return "0.0 g/m²"

    def calculate_transfer_factor(self, rasterwals_type: str, selected_volume: str) -> float:
        """Calculate transfer factor based on rasterwals type and volume."""
        # Get transfer range for rasterwals type
        transfer_range = self.transfer_ranges.get(rasterwals_type, (0.25, 0.30))
        transfer_avg = sum(transfer_range) / 2

        # Get volume specs
        specs = self.volume_specs.get(rasterwals_type, [])
        selected_spec = next((spec for spec in specs if spec['volume'] == selected_volume), None)

        if selected_spec:
            # Extract numerical value from transfer string (e.g., "2.5 g/m²" -> 2.5)
            transfer_value = float(selected_spec['transfer'].split()[0])
            # Adjust transfer factor based on volume
            return transfer_avg * (transfer_value / 3.0)  # normalize against medium transfer value

        return transfer_avg

    def bereken_uv_vermogen(self, substraat: str, inktsoort: str, bcm: float, rasterwals_type: str, selected_volume: str) -> Dict[str, Any]:
        """
        Calculate required UV power based on substrate, ink type, BCM, rasterwals type and volume.
        Returns both the power and explanation.
        """
        base_power = 40  # Base UV power
        power_factors = {
            'substraat': {
                'Gecoat papier': 1.0,
                'Ongecoat papier': 1.2,
                'Folie': 1.3,
                'Karton': 1.1
            },
            'inktsoort': {
                'UV-inkt': 1.0,
                'Watergedragen inkt': 1.2,
                'LED-UV inkt': 0.9
            }
        }

        # Calculate power with explanations
        substrate_factor = power_factors['substraat'].get(substraat, 1.0)
        ink_factor = power_factors['inktsoort'].get(inktsoort, 1.0)
        transfer_factor = self.calculate_transfer_factor(rasterwals_type, selected_volume)
        bcm_factor = bcm * 0.1  # BCM contribution to power

        # Calculate final power
        uv_vermogen = base_power * substrate_factor * ink_factor * (1 + bcm_factor)
        uv_vermogen = uv_vermogen * (1 + transfer_factor)  # Increase power based on transfer efficiency
        uv_vermogen = max(20, min(uv_vermogen, 100))  # Limit between 20-100%

        # Get actual transfer value for display
        transfer_value = self.get_transfer_from_volume(rasterwals_type, selected_volume)

        explanation = {
            'base_power': base_power,
            'substrate_contribution': (substrate_factor - 1) * 100,
            'ink_contribution': (ink_factor - 1) * 100,
            'bcm_contribution': bcm_factor * 100,
            'transfer_factor': transfer_factor * 100,
            'transfer_value': transfer_value,
            'final_power': round(uv_vermogen, 1)
        }

        return explanation

    def load_anilox_data(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Load anilox information from document with error handling.
        """
        try:
            # Placeholder for actual data loading
            # In real implementation, this would parse the docx file
            return pd.DataFrame({
                'bcm': [1.5, 2.0, 2.5, 3.0],
                'recommended_power': [40, 50, 60, 70]
            })
        except Exception as e:
            print(f"Error loading anilox data: {str(e)}")
            return None

    def get_recommended_settings(self, bcm: float) -> Optional[float]:
        """Get recommended power settings from anilox data."""
        if self.anilox_data is None:
            return None

        # Find closest BCM value and return recommended power
        closest_bcm = self.anilox_data['bcm'].iloc[
            (self.anilox_data['bcm'] - bcm).abs().argsort()[:1]
        ].iloc[0]

        return self.anilox_data.loc[
            self.anilox_data['bcm'] == closest_bcm,
            'recommended_power'
        ].iloc[0]
