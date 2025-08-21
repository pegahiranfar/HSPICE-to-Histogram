import os
from analyzer import HSPICEDataAnalyzer

        
def main():
    """
    Main function to demonstrate the HSPICE data analyzer
    """
    # Initialize the analyzer
    analyzer = HSPICEDataAnalyzer()
    
    print("HSPICE Data Analyzer")
    print("===================")
    print(f"Current working directory: {os.getcwd()}")
    
    # Show available .txt files in current directory
    txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]
    if txt_files:
        print(f"Available .txt files in current directory: {txt_files}")
    else:
        print("No .txt files found in current directory")
    
    # Get file path from user
    while True:
        print("\nOptions:")
        print("1. Enter full path to your file")
        print("2. Enter filename if it's in current directory")
        print("3. List all files in current directory")
        print("4. Change directory")
        
        choice = input("Choose option (1-4): ").strip()
        
        if choice == "1" or choice == "2":
            filename = input("Enter file path/name: ").strip()
            if filename and os.path.exists(filename):
                break
            elif filename:
                print(f"File '{filename}' not found!")
                continue
            else:
                print("Please enter a valid filename")
                continue
                
        elif choice == "3":
            print("All files in current directory:")
            for i, file in enumerate(os.listdir('.'), 1):
                print(f"  {i}. {file}")
            continue
            
        elif choice == "4":
            new_dir = input("Enter new directory path: ").strip()
            if os.path.exists(new_dir) and os.path.isdir(new_dir):
                os.chdir(new_dir)
                print(f"Changed directory to: {os.getcwd()}")
                # Update txt_files list for new directory
                txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]
                if txt_files:
                    print(f"Available .txt files: {txt_files}")
            else:
                print("Invalid directory path!")
            continue
        else:
            print("Invalid choice!")
            continue
    
    parameter_name = input("Enter parameter name to analyze (default: static_power): ").strip()
    if not parameter_name:
        parameter_name = "static_power"
        print(f"Using default parameter: {parameter_name}")
    
    target_unit = input("Enter target unit [f/p/n/u/m/k/M/G] (default: p for pico): ").strip()
    if not target_unit:
        target_unit = "p"
        print(f"Using default unit: {target_unit} (pico)")
    
    save_option = input("Do you want to save the plot? (y/n, default: n): ").strip().lower()
    save_plot_path = None
    if save_option in ['y', 'yes']:
        save_plot_path = f"{parameter_name}_distribution.jpg"
        print(f"Plot will be saved as: {save_plot_path}")
    
    print("HSPICE Data Analyzer")
    print("===================")
    
    # Read the HSPICE file
    file_content = analyzer.read_hspice_file(filename)
    if not file_content:
        return
    
    # Extract parameter values
    raw_values = analyzer.extract_parameter_values(file_content, parameter_name)
    if not raw_values:
        print(f"No values found for parameter '{parameter_name}'")
        return
    
    print(f"Sample raw values: {raw_values[:5]}...")  # Show first 5 values
    
    #  Normalize units
    normalized_data, unit_description = analyzer.normalize_units(raw_values, target_unit)
    
    if len(normalized_data) == 0:
        print("No valid data after normalization!")
        return
    
    # Calculate statistics
    statistics = analyzer.calculate_statistics(normalized_data)
    
    # Print results
    analyzer.print_statistics(statistics, unit_description)
    
    # Visualization
    analyzer.plot_distribution(
        data=normalized_data,
        parameter_name=parameter_name,
        unit=unit_description,
        stats=statistics,
        save_path=save_plot_path
    )

if __name__ == "__main__":
    main()