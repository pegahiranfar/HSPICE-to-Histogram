import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm
from typing import List, Tuple, Dict
import re


class HSPICEDataAnalyzer:
    """
    A class to analyze HSPICE output data and generate statistical plots
    """
    
    def __init__(self):
        # Dictionary for unit conversion factors to base units
        self.unit_conversions = {
            'f': 1e-15,  # femto
            'p': 1e-12,  # pico
            'n': 1e-9,   # nano
            'u': 1e-6,   # micro
            'm': 1e-3,   # milli
            '': 1.0,     # base unit
            'k': 1e3,    # kilo
            'M': 1e6,    # mega
            'G': 1e9     # giga
        }
    
    def read_hspice_file(self, filename: str) -> str:
        """
        Read HSPICE output file
        
        Args:
            filename (str): Path to the HSPICE output file
            
        Returns:
            str: File content as string
        """
        try:
            with open(filename, 'r') as file:
                data = file.read()
            print(f"Successfully read file: {filename}")
            return data
        except FileNotFoundError:
            print(f"Error: File {filename} not found!")
            return ""
        except Exception as e:
            print(f"Error reading file: {e}")
            return ""
    
    def extract_parameter_values(self, data: str, parameter_name: str) -> List[str]:

        values = []
        lines = data.split('\n')
        
        print(f"Searching for parameter: '{parameter_name}'")
        print(f"Total lines in file: {len(lines)}")
        
        try:
            matches_found = 0
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Look for lines containing the parameter name followed by =
                if f"{parameter_name}=" in line:
                    matches_found += 1
                    
                    # Extract the value after the = sign
                    parts = line.split(f"{parameter_name}=")
                    if len(parts) > 1:
                        value_part = parts[1].strip().split()[0]  
                        
                        # Skip 'failed' values
                        if value_part.lower() != 'failed' and value_part.strip():
                            values.append(value_part)
                            if matches_found <= 5:  
                                print(f"Line {line_num}: Found '{parameter_name}={value_part}'")
            
            print(f"Total valid matches found for '{parameter_name}': {matches_found}")
            print(f"Valid values extracted: {len(values)}")
                
        except Exception as e:
            print(f"Error extracting parameter values: {e}")
        
        if values:
            print(f"Sample extracted values: {values[:10]}")
        else:
            print("No values extracted! Trying alternative search...")
            # Try alternative search method
            values = self._alternative_search(data, parameter_name)
        
        return values
    
    def _alternative_search(self, data: str, parameter_name: str) -> List[str]:
        """
        Alternative search method for parameter extraction
        """
        import re
        values = []
        
        # Pattern to match parameter=value format
        pattern = rf"{re.escape(parameter_name)}\s*=\s*([0-9]*\.?[0-9]+[a-zA-Z]*)"
        matches = re.findall(pattern, data, re.IGNORECASE)
        
        print(f"Alternative search found {len(matches)} matches")
        if matches:
            print(f"Sample matches: {matches[:5]}")
            values = [match for match in matches if match.lower() != 'failed']
        
        return values
    
    def normalize_units(self, values: List[str], target_unit: str = 'p') -> Tuple[np.ndarray, str]:
        """
        Convert all values to the same unit scale
        """
        normalized_values = []
        unit_names = {
            'f': 'femto', 'p': 'p', 'n': 'n', 'u': 'µ',
            'm': 'm', '': '', 'k': 'k', 'M': 'M', 'G': 'G'
        }
        
        print(f"Normalizing {len(values)} values to {target_unit} unit...")
        
        for i, value_str in enumerate(values):
            try:
                value_str = value_str.strip()
                
                # Skip empty or failed values
                if not value_str or value_str.lower() == 'failed':
                    continue
                
                # Extract numeric part and unit using regex
                # This pattern matches: number (with optional decimal and scientific notation) + optional unit
                match = re.match(r'([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*([a-zA-Z]*)', value_str)
                
                if match:
                    numeric_part = float(match.group(1))
                    unit = match.group(2) if match.group(2) else ''
                    
                    if unit:
                        unit = unit[0]

                    # Convert to base unit, then to target unit
                    if unit in self.unit_conversions and target_unit in self.unit_conversions:
                        base_value = numeric_part * self.unit_conversions[unit]
                        target_value = base_value / self.unit_conversions[target_unit]
                        normalized_values.append(target_value)
                        
                        # Show first few conversions for debugging
                        if i < 5:
                            print(f"  {value_str} -> {numeric_part}{unit} -> {target_value:.4f}{target_unit}")
                    else:
                        print(f"Warning: Unknown unit '{unit}' in value '{value_str}'")
                        # Assume it's already in target unit if no unit specified
                        normalized_values.append(numeric_part)
                else:
                    # If regex doesn't match, try to extract just the number
                    try:
                        # Remove any non-numeric characters except decimal point and scientific notation
                        clean_value = re.sub(r'[^0-9.\-+eE]', '', value_str)
                        if clean_value:
                            numeric_value = float(clean_value)
                            normalized_values.append(numeric_value)
                            print(f"  Extracted number from '{value_str}': {numeric_value}")
                    except ValueError:
                        print(f"Warning: Could not extract number from '{value_str}'")
                        continue
                    
            except (ValueError, AttributeError) as e:
                print(f"Warning: Could not convert '{value_str}' to float: {e}")
                continue
        
        print(f"Successfully normalized {len(normalized_values)} values")
        
        unit_description = f"{unit_names.get(target_unit, target_unit)}" if target_unit else " "
        return np.array(normalized_values), unit_description
    
    def calculate_statistics(self, data: np.ndarray) -> Dict[str, float]:

        if len(data) == 0:
            print("Warning: No data to analyze!")
            return {}
        
        # Fit normal distribution and get parameters
        mu, std = norm.fit(data)
        
        stats = {
            'mean': mu,
            'std': std,
            'min': np.min(data),
            'max': np.max(data),
            'median': np.median(data),
            'count': len(data)
        }
        
        return stats
    
    def plot_distribution(self, data: np.ndarray, parameter_name: str, unit: str, 
                         stats: Dict[str, float], save_path: str = None) -> None:
        """
        Create histogram and distribution plot
        """
        if len(data) == 0:
            print("No data to plot!")
            return
        
        # Set up the plot style
        plt.figure(figsize=(10, 6))
        sns.set_style('white', {'font.family': 'serif', 'font.serif': 'Times New Roman'})
        
        # Create histogram with density
        sns.histplot(data, bins=15, color="#2562FC", stat="density", alpha=0.7)
        
        # Add KDE curve
        sns.kdeplot(data=data, color="#C20000", linewidth=2)
        
        # Create legend with statistics
        legend_labels = [
            f'Mean = {stats["mean"]:.4f} {unit}',
            f'Std = {stats["std"]:.4f}',
            f'Count = {stats["count"]}'
        ]
        
        # Labels and title
        plt.xlabel(f"{parameter_name.replace('_', ' ').title()} ({unit})", fontsize=12)
        plt.ylabel("Density", fontsize=12)
        plt.title(f"Distribution of {parameter_name.replace('_', ' ').title()}", fontsize=14)
        plt.legend(legend_labels, loc='upper right')
        
        # Add grid for better readability
        plt.grid(True, alpha=0.3)
        
        # Save plot if path is provided
        if save_path:
            plt.savefig(save_path, format='jpg', dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    def debug_file_content(self, filename: str, lines_to_show: int = 10) -> None:

        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
            
            print(f"\n{'='*60}")
            print("FILE CONTENT ANALYSIS")
            print(f"{'='*60}")
            print(f"Total lines in file: {len(lines)}")
            print(f"Showing first {min(lines_to_show, len(lines))} lines:")
            print("-" * 40)
            
            for i, line in enumerate(lines[:lines_to_show], 1):
                print(f"Line {i:2d}: {line.rstrip()}")
            
            print("-" * 40)
            print("Looking for common HSPICE parameter patterns:")
            
            # Look for common patterns
            patterns = ['static_power', 'av_pow', 'current', 'voltage', 'total_tp', '=']
            for pattern in patterns:
                count = sum(1 for line in lines if pattern.lower() in line.lower())
                if count > 0:
                    print(f"  '{pattern}': found in {count} lines")
            
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"Error reading file for debug: {e}")
    
    def suggest_parameter_names(self, data: str) -> List[str]:

        tokens = data.split()
        potential_params = []
        
        for token in tokens[:1000]:  # Check first 1000 tokens
            if '=' in token:
                param_name = token.split('=')[0].strip()
                if param_name and len(param_name) > 2 and param_name not in potential_params:
                    potential_params.append(param_name)
        
        return potential_params[:10]  # Return top 10 suggestions
        
    def print_statistics(self, stats: Dict[str, float], unit: str) -> None:

        if not stats:
            print("No statistics to display!")
            return
        
        print("\n" + "="*50)
        print("STATISTICAL SUMMARY")
        print("="*50)
        print(f"Count:    {stats['count']}")
        print(f"Mean:     {stats['mean']:.6f} {unit}")
        print(f"Std:  {stats['std']:.6f} {unit}")
        print(f"Minimum:  {stats['min']:.6f} {unit}")
        print(f"Median:   {stats['median']:.6f} {unit}")
        print(f"Maximum:  {stats['max']:.6f} {unit}")
        print("="*50)

