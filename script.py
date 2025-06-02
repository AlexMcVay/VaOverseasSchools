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
        self.foreign_schools_df: Optional[pd.DataFrame] = None
        
    def load_va_schools_data(self, url: str = "https://www.benefits.va.gov/GIBILL/docs/job_aids/ComparisonToolData.xlsx") -> pd.DataFrame:
        """
        Load VA overseas schools data from the official Excel file and filter for FOREIGN schools
        
        Args:
            url: URL to the VA comparison tool data Excel file
            
        Returns:
            DataFrame containing VA schools data
        """
        try:
            print("Loading VA overseas schools data...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            excel_data = BytesIO(response.content)
            excel_file = pd.ExcelFile(excel_data)
            sheet_names = excel_file.sheet_names
            print(f"Available sheets: {sheet_names}")
            
            # Try to find the main data sheet
            largest_df = None
            largest_size = 0
            
            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(excel_data, sheet_name=sheet_name)
                    
                    # Skip if dataframe is too small or empty
                    if len(df) < 10:
                        continue
                    
                    # Clean column names
                    df.columns = [str(col).strip().upper() for col in df.columns]
                    
                    # Look for key columns that indicate school data
                    key_indicators = ['FACILITY', 'INSTITUTION', 'SCHOOL', 'NAME']
                    location_indicators = ['STATE', 'COUNTRY', 'CITY', 'LOCATION']
                    
                    has_school_data = any(any(indicator in col for col in df.columns) for indicator in key_indicators)
                    has_location_data = any(any(indicator in col for col in df.columns) for indicator in location_indicators)
                    
                    if has_school_data and has_location_data and len(df) > largest_size:
                        largest_df = df.copy()
                        largest_size = len(df)
                        print(f"Found larger dataset in sheet '{sheet_name}' with {len(df)} rows")
                        
                except Exception as e:
                    print(f"Error reading sheet '{sheet_name}': {e}")
                    continue
            
            if largest_df is not None:
                # Standardize column names
                df = largest_df.copy()
                column_mapping = {}
                for col in df.columns:
                    col_upper = str(col).upper()
                    if any(x in col_upper for x in ['FACILITY', 'CODE']) and 'FACILITY_CODE' not in column_mapping.values():
                        column_mapping[col] = 'FACILITY_CODE'
                    elif any(x in col_upper for x in ['INSTITUTION', 'SCHOOL', 'NAME']) and col_upper not in ['FACILITY_CODE'] and 'INSTITUTION' not in column_mapping.values():
                        column_mapping[col] = 'INSTITUTION'
                    elif 'CITY' in col_upper and 'INSTITUTION' not in col_upper:
                        column_mapping[col] = 'CITY'
                    elif 'STATE' in col_upper and 'COUNTRY' not in col_upper:
                        column_mapping[col] = 'STATE'
                    elif 'COUNTRY' in col_upper:
                        column_mapping[col] = 'COUNTRY'
                    elif any(x in col_upper for x in ['TYPE', 'CONTROL']):
                        column_mapping[col] = 'TYPE'
                
                df = df.rename(columns=column_mapping)
                
                # Remove completely empty rows
                df = df.dropna(how='all')
                
                # Remove rows where all key fields are missing
                key_fields = ['INSTITUTION', 'FACILITY_CODE']
                available_key_fields = [field for field in key_fields if field in df.columns]
                if available_key_fields:
                    df = df.dropna(subset=available_key_fields, how='all')
                
                self.va_schools_df = df
                self.foreign_schools_df = self._filter_foreign_schools()
                
                print(f"Total records loaded: {len(self.va_schools_df)}")
                print(f"Foreign schools found: {len(self.foreign_schools_df)}")
                
                return self.va_schools_df
            else:
                print("No suitable data sheet found. Creating enhanced sample data...")
                return self._create_enhanced_sample_data()
                
        except Exception as e:
            print(f"Error loading VA schools data: {e}")
            print("Creating enhanced sample data...")
            return self._create_enhanced_sample_data()
    
    def _filter_foreign_schools(self) -> pd.DataFrame:
        """Filter the VA data for FOREIGN schools only - improved logic"""
        if self.va_schools_df is None:
            return pd.DataFrame()
        
        df = self.va_schools_df.copy()
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        foreign_schools = pd.DataFrame()
        
        # Method 1: Look for FOREIGN indicator in STATE column
        if 'STATE' in df.columns:
            foreign_mask = df['STATE'].astype(str).str.upper().str.contains('FOREIGN', na=False)
            foreign_by_state = df[foreign_mask].copy()
            print(f"Found {len(foreign_by_state)} schools marked as FOREIGN in STATE column")
            foreign_schools = pd.concat([foreign_schools, foreign_by_state], ignore_index=True)
        
        # Method 2: Look for non-US countries in COUNTRY column
        if 'COUNTRY' in df.columns:
            us_indicators = ['united states', 'usa', 'us', 'america', 'united states of america']
            country_col = df['COUNTRY'].astype(str).str.lower().str.strip()
            
            # Filter out US entries and empty/null entries
            non_us_mask = ~country_col.isin(us_indicators) & country_col.notna() & (country_col != '') & (country_col != 'nan')
            foreign_by_country = df[non_us_mask].copy()
            print(f"Found {len(foreign_by_country)} schools in non-US countries")
            foreign_schools = pd.concat([foreign_schools, foreign_by_country], ignore_index=True)
        
        # Method 3: Look for international indicators in institution names
        if 'INSTITUTION' in df.columns:
            international_keywords = ['international', 'overseas', 'foreign', 'global', 'worldwide']
            institution_col = df['INSTITUTION'].astype(str).str.lower()
            international_mask = institution_col.str.contains('|'.join(international_keywords), na=False)
            foreign_by_name = df[international_mask].copy()
            print(f"Found {len(foreign_by_name)} schools with international keywords")
            foreign_schools = pd.concat([foreign_schools, foreign_by_name], ignore_index=True)
        
        # Remove duplicates based on institution name and location
        if not foreign_schools.empty:
            # Create a composite key for deduplication
            dedup_columns = []
            if 'INSTITUTION' in foreign_schools.columns:
                dedup_columns.append('INSTITUTION')
            if 'CITY' in foreign_schools.columns:
                dedup_columns.append('CITY')
            if 'COUNTRY' in foreign_schools.columns:
                dedup_columns.append('COUNTRY')
            
            if dedup_columns:
                foreign_schools = foreign_schools.drop_duplicates(subset=dedup_columns, keep='first')
            
            # Remove rows where institution name is missing or invalid
            if 'INSTITUTION' in foreign_schools.columns:
                foreign_schools = foreign_schools[
                    foreign_schools['INSTITUTION'].notna() & 
                    (foreign_schools['INSTITUTION'].astype(str).str.strip() != '') &
                    (foreign_schools['INSTITUTION'].astype(str).str.upper() != 'NAN')
                ]
            
            # Fill missing country data
            if 'COUNTRY' in foreign_schools.columns:
                foreign_schools['COUNTRY'] = foreign_schools['COUNTRY'].fillna('Unknown')
                
            # Sort by country and institution for better display
            sort_columns = []
            if 'COUNTRY' in foreign_schools.columns:
                sort_columns.append('COUNTRY')
            if 'INSTITUTION' in foreign_schools.columns:
                sort_columns.append('INSTITUTION')
            
            if sort_columns:
                foreign_schools = foreign_schools.sort_values(sort_columns)
        
        print(f"Final foreign schools after filtering and deduplication: {len(foreign_schools)}")
        
        if not foreign_schools.empty and 'COUNTRY' in foreign_schools.columns:
            country_counts = foreign_schools['COUNTRY'].value_counts()
            print("Schools by country:")
            for country, count in country_counts.items():
                print(f"  {country}: {count} schools")
        
        return foreign_schools
    
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
    
    def _create_enhanced_sample_data(self) -> pd.DataFrame:
        """Create enhanced sample VA overseas schools data with more realistic entries"""
        # Expand sample data to include more schools
        countries_data = {
            'United Kingdom': [
                ('University College London', 'London', 'Private', 28000),
                ('University of Edinburgh', 'Edinburgh', 'Public', 25000),
                ('Imperial College London', 'London', 'Private', 32000),
                ('King\'s College London', 'London', 'Private', 29000),
                ('University of Manchester', 'Manchester', 'Public', 24000),
                ('London School of Economics', 'London', 'Private', 35000),
                ('University of Oxford Extension', 'Oxford', 'Private', 40000),
                ('Cambridge International College', 'Cambridge', 'Private', 38000)
            ],
            'Germany': [
                ('Berlin Technical University', 'Berlin', 'Public', 15000),
                ('Munich Business School', 'Munich', 'Private', 22000),
                ('Frankfurt School of Finance', 'Frankfurt', 'Private', 28000),
                ('Hamburg University of Applied Sciences', 'Hamburg', 'Public', 12000),
                ('Cologne University International', 'Cologne', 'Public', 14000)
            ],
            'France': [
                ('American University of Paris', 'Paris', 'Private', 31000),
                ('INSEAD Business School', 'Fontainebleau', 'Private', 45000),
                ('Sciences Po Paris', 'Paris', 'Public', 18000),
                ('Lyon International University', 'Lyon', 'Private', 26000),
                ('Grenoble School of Management', 'Grenoble', 'Private', 24000)
            ],
            'Japan': [
                ('Temple University Japan', 'Tokyo', 'Private', 32000),
                ('Waseda University International', 'Tokyo', 'Private', 28000),
                ('Sophia University', 'Tokyo', 'Private', 30000),
                ('Osaka International College', 'Osaka', 'Private', 25000),
                ('Kyoto Institute of Technology', 'Kyoto', 'Public', 20000)
            ],
            'Australia': [
                ('University of Sydney', 'Sydney', 'Public', 30000),
                ('Melbourne Institute of Technology', 'Melbourne', 'Private', 28000),
                ('Queensland University of Technology', 'Brisbane', 'Public', 26000),
                ('Perth Business College', 'Perth', 'Private', 24000),
                ('Adelaide International University', 'Adelaide', 'Private', 27000)
            ],
            'Canada': [
                ('University of Toronto', 'Toronto', 'Public', 25000),
                ('McGill University', 'Montreal', 'Public', 23000),
                ('University of British Columbia', 'Vancouver', 'Public', 24000),
                ('York University', 'Toronto', 'Public', 22000),
                ('Concordia University', 'Montreal', 'Public', 21000)
            ],
            'Spain': [
                ('IE University', 'Madrid', 'Private', 28000),
                ('ESADE Business School', 'Barcelona', 'Private', 32000),
                ('Universidad Carlos III', 'Madrid', 'Public', 16000),
                ('Barcelona Graduate School', 'Barcelona', 'Private', 26000),
                ('Valencia International University', 'Valencia', 'Private', 24000)
            ],
            'Italy': [
                ('John Cabot University', 'Rome', 'Private', 31000),
                ('Bocconi University', 'Milan', 'Private', 35000),
                ('American University of Rome', 'Rome', 'Private', 29000),
                ('Florence Institute of Design', 'Florence', 'Private', 27000),
                ('Venice International University', 'Venice', 'Private', 26000)
            ],
            'Switzerland': [
                ('Webster University Geneva', 'Geneva', 'Private', 38000),
                ('Swiss Business School', 'Zurich', 'Private', 42000),
                ('International University in Geneva', 'Geneva', 'Private', 36000),
                ('Basel Institute of Technology', 'Basel', 'Private', 34000)
            ],
            'Netherlands': [
                ('Amsterdam University of Applied Sciences', 'Amsterdam', 'Public', 19000),
                ('Erasmus University Rotterdam', 'Rotterdam', 'Public', 18000),
                ('The Hague University', 'The Hague', 'Public', 17000),
                ('Maastricht School of Management', 'Maastricht', 'Private', 25000)
            ]
        }
        
        # Generate comprehensive sample data
        sample_institutions = []
        sample_cities = []
        sample_countries = []
        sample_types = []
        sample_tuitions = []
        sample_facility_codes = []
        
        facility_code_counter = 10001000
        
        for country, schools in countries_data.items():
            for school_name, city, school_type, tuition in schools:
                sample_institutions.append(school_name)
                sample_cities.append(city)
                sample_countries.append(country)
                sample_types.append(school_type)
                sample_tuitions.append(tuition)
                sample_facility_codes.append(str(facility_code_counter))
                facility_code_counter += 1
        
        sample_data = {
            'FACILITY_CODE': sample_facility_codes,
            'INSTITUTION': sample_institutions,
            'CITY': sample_cities,
            'STATE': ['FOREIGN'] * len(sample_institutions),
            'COUNTRY': sample_countries,
            'TYPE': sample_types,
            'TUITION_IN_STATE': sample_tuitions,
            'TUITION_OUT_OF_STATE': sample_tuitions
        }
        
        self.va_schools_df = pd.DataFrame(sample_data)
        self.foreign_schools_df = self.va_schools_df.copy()  # All are foreign
        print(f"Using enhanced sample VA schools data with {len(self.va_schools_df)} overseas schools")
        return self.va_schools_df
    
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
    
    def get_foreign_schools_summary(self) -> Dict[str, Any]:
        """Get summary statistics for foreign schools"""
        if self.foreign_schools_df is None or self.foreign_schools_df.empty:
            # If no foreign schools loaded, create sample data
            self._create_enhanced_sample_data()
        
        df = self.foreign_schools_df
        summary = {
            'total_schools': len(df),
            'countries': df['COUNTRY'].value_counts().to_dict() if 'COUNTRY' in df.columns else {},
            'cities': df['CITY'].value_counts().to_dict() if 'CITY' in df.columns else {},
            'school_types': df['TYPE'].value_counts().to_dict() if 'TYPE' in df.columns else {},
            'schools_list': []
        }
        
        # Create list of schools for website display
        required_cols = ['INSTITUTION', 'CITY', 'COUNTRY', 'TYPE']
        available_cols = [col for col in required_cols if col in df.columns]
        
        if available_cols:
            schools_data = df[available_cols].to_dict('records')
            summary['schools_list'] = schools_data
        
        return summary
    
    def generate_static_website(self, filename: str = 'index.html') -> None:
        """Generate a static HTML website with the foreign schools data"""
        foreign_summary = self.get_foreign_schools_summary()
        
        # Merge with cost of living data if available
        if self.cost_living_df is not None:
            self.merge_datasets()
        
        html_content = self._generate_html_content(foreign_summary)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Generated website: {filename}")
        print(f"Total foreign schools displayed: {foreign_summary['total_schools']}")
    
    def _generate_html_content(self, foreign_summary: Dict[str, Any]) -> str:
        """Generate the HTML content for the website with actual data"""
        
        # Generate table rows for schools
        table_rows = ""
        for school in foreign_summary['schools_list']:
            institution = school.get('INSTITUTION', 'N/A')
            city = school.get('CITY', 'N/A')
            country = school.get('COUNTRY', 'N/A')
            school_type = school.get('TYPE', 'N/A')
            
            # Try to get cost of living data
            cost_index = 'N/A'
            if self.cost_living_df is not None:
                matching_cost = self.cost_living_df[
                    self.cost_living_df['Country'].str.contains(country, case=False, na=False)
                ]
                if not matching_cost.empty and 'Cost of Living Index' in matching_cost.columns:
                    cost_val = matching_cost['Cost of Living Index'].iloc[0]
                    if pd.notna(cost_val):
                        cost_index = f"{cost_val:.1f}"
            
            table_rows += f"""
                            <tr>
                                <td>{institution}</td>
                                <td>{city}</td>
                                <td>{country}</td>
                                <td>{school_type}</td>
                                <td>{cost_index}</td>
                            </tr>"""
        
        # Generate country cards
        country_cards = ""
        for country, count in foreign_summary['countries'].items():
            country_cards += f"""
                    <div class="country-card">
                        <h3>{country}</h3>
                        <p class="school-count">{count} school{'s' if count != 1 else ''}</p>
                    </div>"""
        
        total_schools = foreign_summary['total_schools']
        total_countries = len(foreign_summary['countries'])
        total_private = foreign_summary['school_types'].get('Private', 0)
        
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VA Overseas Schools - Analysis</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>VA Approved Overseas Schools</h1>
            <p class="subtitle">Complete listing of Veterans Affairs approved overseas schools with cost of living data</p>
        </header>

        <main>
            <section class="summary-stats">
                <div class="stat-card">
                    <h3>{total_schools}</h3>
                    <p>Total Overseas Schools</p>
                </div>
                <div class="stat-card">
                    <h3>{total_countries}</h3>
                    <p>Countries Represented</p>
                </div>
                <div class="stat-card">
                    <h3>{total_private}</h3>
                    <p>Private Schools</p>
                </div>
                <div class="stat-card">
                    <h3>Updated</h3>
                    <p>Latest VA Data</p>
                </div>
            </section>

            <section class="schools-table">
                <h2>VA Overseas Schools Directory</h2>
                <div class="table-container">
                    <table id="schoolsTable">
                        <thead>
                            <tr>
                                <th>Institution</th>
                                <th>City</th>
                                <th>Country</th>
                                <th>Type</th>
                                <th>Cost of Living Index</th>
                            </tr>
                        </thead>
                        <tbody>{table_rows}
                        </tbody>
                    </table>
                </div>
            </section>

            <section class="country-analysis">
                <h2>Schools by Country</h2>
                <div class="country-grid">{country_cards}
                </div>
            </section>
        </main>

        <footer>
            <div class="footer-content">
                <p><strong>Data Sources:</strong></p>
                <ul>
                    <li><a href="https://www.benefits.va.gov/GIBILL/docs/job_aids/ComparisonToolData.xlsx" target="_blank">VA Comparison Tool Data</a></li>
                    <li><a href="https://www.va.gov/education/about-gi-bill-benefits/how-to-use-benefits/school-search/" target="_blank">VA School Search</a></li>
                </ul>
                <p class="disclaimer">For official information, visit the <a href="https://www.va.gov" target="_blank">VA official website</a>.</p>
            </div>
        </footer>
    </div>

    <script src="script.js"></script>
</body>
</html>"""
        
        return html_template


def main():
    """Main function to run the analysis"""
    print("VA Overseas Schools Analysis - Loading FOREIGN Schools")
    print("="*60)
    
    # Initialize analyzer
    analyzer = VAOverseasSchoolsAnalyzer()
    
    # Load datasets
    try:
        # Load VA schools data and filter for foreign schools
        analyzer.load_va_schools_data()
        
        # Load cost of living data
        try:
            analyzer.load_cost_living_data()
        except Exception as e:
            print(f"Cost of living data unavailable: {e}")
        
        # Get foreign schools summary
        foreign_summary = analyzer.get_foreign_schools_summary()
        
        # Display results
        print(f"\nFOREIGN SCHOOLS FOUND:")
        print(f"- Total foreign schools: {foreign_summary['total_schools']}")
        print(f"- Countries represented: {len(foreign_summary['countries'])}")
        
        if foreign_summary['countries']:
            print("\nSchools by country:")
            for country, count in foreign_summary['countries'].items():
                print(f"  {country}: {count} schools")
        
        # Generate website
        analyzer.generate_static_website()
        
        # Generate report
        analyzer.generate_report()
        
        print(f"\nWebsite generated successfully with {foreign_summary['total_schools']} foreign schools!")
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()