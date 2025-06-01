# VA Overseas Schools Analysis

import pandas as pd
import numpy as np
import requests
from io import BytesIO
import kagglehub
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

class VAOverseasSchoolsAnalyzer:
    """Analyzer for VA overseas schools and cost of living data"""
    
    def __init__(self):
        self.va_schools_df: Optional[pd.DataFrame] = None
        self.cost_living_df: Optional[pd.DataFrame] = None
        self.merged_df: Optional[pd.DataFrame] = None
        
    def load_va_schools_data(self, url: str = "https://www.benefits.va.gov/GIBILL/docs/job_aids/ComparisonToolData.xlsx") -> pd.DataFrame:
        """
        Load VA overseas schools data from the official Excel file
        
        Args:
            url: URL to the VA comparison tool data Excel file
            
        Returns:
            DataFrame containing VA schools data
        """
        try:
            print("Loading VA overseas schools data...")
            response = requests.get(url)
            response.raise_for_status()
            
            # Read Excel file from bytes
            excel_data = BytesIO(response.content)
            
            # Read the Excel file and examine its structure
            excel_file = pd.ExcelFile(excel_data)
            sheet_names = excel_file.sheet_names
            print(f"Available sheets: {sheet_names}")
            
            # Try to find the correct sheet with actual data
            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(excel_data, sheet_name=sheet_name, skiprows=0)
                    print(f"Sheet '{sheet_name}' columns: {list(df.columns)}")
                    print(f"Shape: {df.shape}")
                    
                    # Look for a sheet that has institution/school data
                    if any(col for col in df.columns if any(keyword in str(col).lower() for keyword in ['institution', 'school', 'facility', 'name'])):
                        self.va_schools_df = df
                        print(f"Using sheet: {sheet_name}")
                        break
                except Exception as e:
                    print(f"Error reading sheet {sheet_name}: {e}")
                    continue
            
            # If we still don't have data, try different approaches
            if self.va_schools_df is None or len(self.va_schools_df) == 0:
                print("Could not find proper data in Excel file. Using sample data.")
                return self._create_sample_va_data()
            
            # Clean up the dataframe
            self.va_schools_df = self.va_schools_df.dropna(how='all')  # Remove empty rows
            
            # If the dataframe has generic column names, try to skip header rows
            if all('Unnamed' in str(col) for col in self.va_schools_df.columns):
                print("Found generic column names, trying to find header row...")
                # Try reading with different skip rows
                for skip in range(1, 10):
                    try:
                        df_test = pd.read_excel(excel_data, sheet_name=sheet_names[0], skiprows=skip)
                        if not all('Unnamed' in str(col) for col in df_test.columns):
                            self.va_schools_df = df_test.dropna(how='all')
                            print(f"Found proper headers at row {skip}")
                            print(f"New columns: {list(self.va_schools_df.columns)}")
                            break
                    except:
                        continue
                
                # If still no luck, create sample data
                if all('Unnamed' in str(col) for col in self.va_schools_df.columns):
                    return self._create_sample_va_data()
            
            print(f"Loaded {len(self.va_schools_df)} records from VA schools data")
            print(f"Final columns: {list(self.va_schools_df.columns)}")
            
            return self.va_schools_df
            
        except Exception as e:
            print(f"Error loading VA schools data: {e}")
            return self._create_sample_va_data()
    
    def load_cost_living_data(self) -> pd.DataFrame:
        """
        Load cost of living data using kagglehub
        
        Returns:
            DataFrame containing cost of living data by country
        """
        try:
            print("Loading cost of living data from Kaggle...")
            
            # Download the dataset using kagglehub
            path = kagglehub.dataset_download("myrios/cost-of-living-index-by-country-by-number-2024")
            print(f"Dataset downloaded to: {path}")
            
            # Find CSV files in the downloaded path
            import os
            csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
            print(f"Found CSV files: {csv_files}")
            
            if csv_files:
                # Load the first CSV file
                csv_path = os.path.join(path, csv_files[0])
                self.cost_living_df = pd.read_csv(csv_path)
                print(f"Loaded cost of living data for {len(self.cost_living_df)} countries")
                print("Columns:", list(self.cost_living_df.columns))
                print("First 5 records:")
                print(self.cost_living_df.head())
            else:
                raise Exception("No CSV files found in downloaded dataset")
            
            return self.cost_living_df
            
        except Exception as e:
            print(f"Error loading cost of living data: {e}")
            return self._create_sample_cost_data()
    
    def _create_sample_va_data(self) -> pd.DataFrame:
        """Create sample VA overseas schools data for testing"""
        sample_data = {
            'FACILITY_CODE': ['12345678', '23456789', '34567890', '45678901', '56789012'],
            'INSTITUTION': ['University of London', 'American University of Paris', 
                           'International School of Business', 'Berlin Technical Institute',
                           'Tokyo International University'],
            'CITY': ['London', 'Paris', 'Sydney', 'Berlin', 'Tokyo'],
            'STATE': ['FOREIGN', 'FOREIGN', 'FOREIGN', 'FOREIGN', 'FOREIGN'],
            'COUNTRY': ['United Kingdom', 'France', 'Australia', 'Germany', 'Japan'],
            'TYPE': ['Private', 'Private', 'Private', 'Public', 'Private'],
            'TUITION_IN_STATE': [25000, 30000, 28000, 22000, 35000],
            'TUITION_OUT_OF_STATE': [25000, 30000, 28000, 22000, 35000]
        }
        self.va_schools_df = pd.DataFrame(sample_data)
        print("Using sample VA schools data")
        return self.va_schools_df
    
    def _create_sample_cost_data(self) -> pd.DataFrame:
        """Create sample cost of living data for testing"""
        sample_data = {
            'Country': ['United Kingdom', 'France', 'Australia', 'Germany', 'Japan', 'Canada', 'Spain'],
            'Cost of Living Index': [67.28, 67.41, 71.32, 65.26, 83.35, 67.62, 54.27],
            'Rent Index': [36.32, 32.84, 47.04, 29.90, 24.31, 35.48, 25.95],
            'Cost of Living Plus Rent Index': [53.29, 51.78, 60.50, 48.73, 56.34, 53.05, 41.23],
            'Groceries Index': [58.79, 63.54, 68.61, 53.31, 88.35, 69.74, 47.89],
            'Restaurant Price Index': [66.87, 67.15, 75.88, 58.29, 48.12, 65.31, 52.43],
            'Local Purchasing Power Index': [107.74, 99.29, 104.61, 115.48, 91.85, 105.32, 87.65]
        }
        self.cost_living_df = pd.DataFrame(sample_data)
        print("Using sample cost of living data")
        return self.cost_living_df
    
    def merge_datasets(self) -> pd.DataFrame:
        """
        Merge VA schools data with cost of living data by country
        
        Returns:
            Merged DataFrame
        """
        if self.va_schools_df is None or self.cost_living_df is None:
            raise ValueError("Both datasets must be loaded before merging")
        
        # Check if COUNTRY column exists, if not, create it or use alternative
        if 'COUNTRY' not in self.va_schools_df.columns:
            print("COUNTRY column not found in VA data. Available columns:")
            print(list(self.va_schools_df.columns))
            
            # Try to find a column that might contain country information
            country_col = None
            for col in self.va_schools_df.columns:
                if any(keyword in str(col).lower() for keyword in ['country', 'nation', 'location']):
                    country_col = col
                    break
            
            if country_col:
                self.va_schools_df['COUNTRY'] = self.va_schools_df[country_col]
                print(f"Using column '{country_col}' as COUNTRY")
            else:
                print("No country column found. Using sample data instead.")
                self.va_schools_df = self._create_sample_va_data()
        
        # Standardize country names for matching
        va_countries = self.va_schools_df['COUNTRY'].astype(str).str.strip().str.title()
        cost_countries = self.cost_living_df['Country'].astype(str).str.strip().str.title()
        
        # Create mapping for common country name variations
        country_mapping = {
            'United States': 'USA',
            'United Kingdom': 'UK',
            'South Korea': 'Korea'
        }
        
        # Apply mapping if needed
        va_countries = va_countries.replace(country_mapping)
        
        # Merge datasets
        va_with_country = self.va_schools_df.copy()
        va_with_country['Country_Clean'] = va_countries
        
        cost_with_country = self.cost_living_df.copy()
        cost_with_country['Country_Clean'] = cost_countries
        
        self.merged_df = pd.merge(
            va_with_country, 
            cost_with_country, 
            left_on='Country_Clean', 
            right_on='Country_Clean', 
            how='left'
        )
        
        print(f"Merged dataset contains {len(self.merged_df)} records")
        return self.merged_df
    
    def analyze_schools_by_cost_of_living(self) -> Dict[str, Any]:
        """
        Analyze VA overseas schools by cost of living metrics
        
        Returns:
            Dictionary containing analysis results
        """
        if self.merged_df is None:
            raise ValueError("Datasets must be merged before analysis")
        
        analysis = {}
        
        # Filter for overseas schools only (exclude US schools)
        overseas_schools = self.merged_df[
            (self.merged_df['STATE'] == 'FOREIGN') | 
            (self.merged_df['COUNTRY'] != 'United States')
        ].copy()
        
        # Basic statistics
        analysis['total_schools'] = len(overseas_schools)
        analysis['countries_with_schools'] = overseas_schools['COUNTRY'].nunique()
        
        # Handle tuition columns that might not exist
        tuition_col = None
        for col in ['TUITION_OUT_OF_STATE', 'TUITION', 'Tuition']:
            if col in overseas_schools.columns:
                tuition_col = col
                break
        
        if tuition_col:
            analysis['avg_tuition'] = overseas_schools[tuition_col].mean()
        else:
            analysis['avg_tuition'] = 0
            print("No tuition data found")
        
        if 'Cost of Living Index' in overseas_schools.columns:
            analysis['avg_cost_of_living'] = overseas_schools['Cost of Living Index'].mean()
        else:
            analysis['avg_cost_of_living'] = 0
        
        # Create detailed school listing with cost of living
        school_columns = ['INSTITUTION', 'CITY', 'COUNTRY', 'TYPE']
        cost_columns = ['Cost of Living Index', 'Rent Index', 'Local Purchasing Power Index']
        
        if tuition_col:
            school_columns.append(tuition_col)
        
        # Select relevant columns that exist
        available_columns = [col for col in school_columns + cost_columns if col in overseas_schools.columns]
        
        schools_table = overseas_schools[available_columns].copy()
        
        # Round numeric columns for better display
        numeric_cols = schools_table.select_dtypes(include=[np.number]).columns
        schools_table[numeric_cols] = schools_table[numeric_cols].round(2)
        
        # Sort by country and institution name
        if 'INSTITUTION' in schools_table.columns:
            schools_table = schools_table.sort_values(['COUNTRY', 'INSTITUTION'])
        
        analysis['schools_table'] = schools_table
        
        # Summary by country (keep existing aggregation for summary stats)
        if 'INSTITUTION' in overseas_schools.columns:
            agg_dict = {'INSTITUTION': 'count'}
        else:
            agg_dict = {'COUNTRY': 'count'}
        
        if tuition_col:
            agg_dict[tuition_col] = 'mean'
        if 'Cost of Living Index' in overseas_schools.columns:
            agg_dict['Cost of Living Index'] = 'first'
        if 'Rent Index' in overseas_schools.columns:
            agg_dict['Rent Index'] = 'first'
        if 'Local Purchasing Power Index' in overseas_schools.columns:
            agg_dict['Local Purchasing Power Index'] = 'first'
        
        country_summary = overseas_schools.groupby('COUNTRY').agg(agg_dict).round(2)
        analysis['country_summary'] = country_summary
        
        return analysis
    
    def create_visualizations(self) -> None:
        """Create visualizations of the analysis"""
        if self.merged_df is None:
            raise ValueError("Datasets must be merged before creating visualizations")
        
        plt.style.use('default')  # Use default style as seaborn-v0_8 might not be available
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Schools by Country
        country_counts = self.merged_df['COUNTRY'].value_counts().head(10)
        axes[0, 0].bar(range(len(country_counts)), country_counts.values)
        axes[0, 0].set_xticks(range(len(country_counts)))
        axes[0, 0].set_xticklabels(country_counts.index, rotation=45, ha='right')
        axes[0, 0].set_title('Number of VA Schools by Country')
        axes[0, 0].set_ylabel('Number of Schools')
        
        # 2. Cost of Living Distribution
        if 'Cost of Living Index' in self.merged_df.columns:
            cost_living_data = self.merged_df['Cost of Living Index'].dropna()
            if len(cost_living_data) > 0:
                axes[0, 1].hist(cost_living_data, bins=10, alpha=0.7, edgecolor='black')
                axes[0, 1].set_xlabel('Cost of Living Index')
                axes[0, 1].set_ylabel('Frequency')
                axes[0, 1].set_title('Distribution of Cost of Living Index')
        
        # 3. Simple country analysis
        axes[1, 0].text(0.1, 0.5, f"Total Schools: {len(self.merged_df)}\nCountries: {self.merged_df['COUNTRY'].nunique()}", 
                       transform=axes[1, 0].transAxes, fontsize=12)
        axes[1, 0].set_title('Summary Statistics')
        axes[1, 0].axis('off')
        
        # 4. Available data info
        available_cols = list(self.merged_df.columns)
        axes[1, 1].text(0.1, 0.9, "Available Data Columns:", transform=axes[1, 1].transAxes, fontsize=10, weight='bold')
        col_text = "\n".join([f"• {col}" for col in available_cols[:10]])  # Show first 10 columns
        axes[1, 1].text(0.1, 0.1, col_text, transform=axes[1, 1].transAxes, fontsize=8)
        axes[1, 1].set_title('Data Structure')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.show()
    
    def generate_report(self, filename: str = 'va_overseas_schools_report.txt') -> None:
        """Generate a comprehensive report"""
        analysis = self.analyze_schools_by_cost_of_living()
        
        report_content = f"""
VA OVERSEAS SCHOOLS ANALYSIS REPORT
{'='*50}

SUMMARY STATISTICS:
- Total overseas schools: {analysis['total_schools']}
- Countries with VA schools: {analysis['countries_with_schools']}
- Average tuition: ${analysis['avg_tuition']:,.2f}
- Average cost of living index: {analysis['avg_cost_of_living']:.2f}

SCHOOLS BY COUNTRY:
{analysis['country_summary'].to_string()}

DATA STRUCTURE:
Available columns in merged dataset:
{list(self.merged_df.columns)}

SAMPLE DATA:
{self.merged_df.head().to_string()}
"""
        
        with open(filename, 'w') as f:
            f.write(report_content)
        
        print(f"Report saved to {filename}")
        return report_content


def main():
    """Main function to run the analysis"""
    print("VA Overseas Schools Analysis")
    print("="*40)
    
    # Initialize analyzer
    analyzer = VAOverseasSchoolsAnalyzer()
    
    # Load datasets
    try:
        analyzer.load_va_schools_data()
        analyzer.load_cost_living_data()
        
        # Merge datasets
        analyzer.merge_datasets()
        
        # Perform analysis
        analysis_results = analyzer.analyze_schools_by_cost_of_living()
        
        # Display key results
        print("\nKEY FINDINGS:")
        print(f"- Total overseas schools: {analysis_results['total_schools']}")
        print(f"- Countries represented: {analysis_results['countries_with_schools']}")
        print(f"- Average tuition: ${analysis_results['avg_tuition']:,.2f}")
        
        print("\nCountry summary:")
        print(analysis_results['country_summary'])
        
        # Generate visualizations
        try:
            analyzer.create_visualizations()
        except Exception as e:
            print(f"Note: Visualization creation failed: {e}")
        
        # Generate report
        analyzer.generate_report()
        
        print("\nAnalysis complete!")
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()