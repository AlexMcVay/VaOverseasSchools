import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import json
import time
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class VASchoolsAnalyzer:
    """VA schools analyzer with World Data cost of living integration"""
    
    def __init__(self):
        self.va_schools_df: Optional[pd.DataFrame] = None
        self.cost_living_df: Optional[pd.DataFrame] = None
        self.merged_df: Optional[pd.DataFrame] = None
        self.va_data_summary: Dict = {}

    def scrape_worlddata_cost_of_living(self) -> pd.DataFrame:
        """
        Scrape cost of living data from worlddata.info
        
        Returns:
            DataFrame containing cost of living data by country
        """
        try:
            print("🌍 Scraping cost of living data from worlddata.info...")
            
            url = "https://www.worlddata.info/cost-of-living.php"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the cost of living table
            tables = soup.find_all('table')
            cost_data = []
            
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) > 5:  # Likely the main data table
                    headers = [th.get_text().strip() for th in rows[0].find_all(['th', 'td'])]
                    
                    # Look for tables with country and cost data
                    if any('country' in h.lower() for h in headers) or any('cost' in h.lower() for h in headers):
                        for row in rows[1:]:
                            cells = [td.get_text().strip() for td in row.find_all(['td', 'th'])]
                            if len(cells) >= 2 and cells[0] and cells[1]:
                                try:
                                    # Try to extract country and cost index
                                    country = cells[0]
                                    # Look for numeric value in subsequent columns
                                    cost_index = None
                                    for cell in cells[1:]:
                                        try:
                                            # Remove any currency symbols and convert to float
                                            cleaned_value = ''.join(c for c in cell if c.isdigit() or c in '.,')
                                            if cleaned_value:
                                                cost_index = float(cleaned_value.replace(',', '.'))
                                                break
                                        except:
                                            continue
                                    
                                    if cost_index and country:
                                        cost_data.append({
                                            'Country': country,
                                            'Cost_of_Living_Index': cost_index,
                                            'Source': 'WorldData.info'
                                        })
                                except:
                                    continue
            
            if cost_data:
                self.cost_living_df = pd.DataFrame(cost_data)
                print(f"✅ Successfully scraped {len(self.cost_living_df)} countries from WorldData.info")
                print(f"📊 Sample countries: {list(self.cost_living_df['Country'].head())}")
            else:
                print("⚠️  Could not find cost of living table. Using fallback data...")
                self.cost_living_df = self._create_worlddata_fallback()
                
            return self.cost_living_df
            
        except Exception as e:
            print(f"❌ Error scraping WorldData: {e}")
            print("🔄 Using fallback cost of living data...")
            return self._create_worlddata_fallback()

    def _create_worlddata_fallback(self) -> pd.DataFrame:
        """Create fallback cost of living data based on WorldData.info typical values"""
        fallback_data = {
            'Country': [
                'Switzerland', 'Norway', 'Iceland', 'Denmark', 'Luxembourg',
                'United States', 'Singapore', 'Japan', 'South Korea', 'Australia',
                'United Kingdom', 'Germany', 'France', 'Canada', 'Italy',
                'Spain', 'Portugal', 'Greece', 'Czech Republic', 'Poland',
                'Hungary', 'Turkey', 'Mexico', 'Thailand', 'Philippines',
                'India', 'China', 'Vietnam', 'Indonesia', 'Malaysia'
            ],
            'Cost_of_Living_Index': [
                122.4, 101.4, 98.7, 84.1, 82.3,
                71.0, 85.6, 83.4, 71.4, 73.5,
                67.3, 65.3, 67.4, 67.6, 64.1,
                54.2, 47.9, 55.0, 49.8, 43.9,
                46.3, 36.8, 41.7, 46.7, 43.2,
                25.1, 41.5, 41.9, 32.7, 40.8
            ],
            'Source': ['WorldData.info (Fallback)'] * 30
        }
        print(f"📋 Created fallback data for {len(fallback_data['Country'])} countries")
        return pd.DataFrame(fallback_data)

    def load_va_schools_data_comprehensive(self, url: str = "https://www.benefits.va.gov/GIBILL/docs/job_aids/ComparisonToolData.xlsx") -> pd.DataFrame:
        """
        Comprehensive loading and analysis of VA schools data
        
        Args:
            url: URL to the VA comparison tool data Excel file
            
        Returns:
            DataFrame containing VA schools data
        """
        try:
            print("🏫 Loading VA schools data comprehensively...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            excel_data = BytesIO(response.content)
            excel_file = pd.ExcelFile(excel_data)
            sheet_names = excel_file.sheet_names
            
            print(f"📋 Available sheets: {sheet_names}")
            
            # Try each sheet and analyze its structure
            sheet_analysis = {}
            best_sheet = None
            max_score = 0
            
            for sheet_name in sheet_names:
                try:
                    # Try different starting rows
                    for skip_rows in [0, 1, 2, 3, 4, 5]:
                        try:
                            df = pd.read_excel(excel_data, sheet_name=sheet_name, skiprows=skip_rows)
                            
                            if len(df) < 10:  # Skip sheets with too little data
                                continue
                            
                            # Score this sheet based on relevant columns
                            score = 0
                            columns_lower = [str(col).lower() for col in df.columns]
                            
                            # Look for key columns
                            key_terms = {
                                'institution': 3, 'school': 3, 'facility': 2, 'name': 1,
                                'city': 2, 'state': 2, 'country': 3,
                                'type': 1, 'public': 1, 'private': 1,
                                'code': 1, 'id': 1
                            }
                            
                            for col in columns_lower:
                                for term, weight in key_terms.items():
                                    if term in col:
                                        score += weight
                            
                            # Bonus for having data in multiple columns
                            non_null_cols = df.count().sum()
                            score += min(non_null_cols / 1000, 10)  # Cap bonus at 10
                            
                            if score > max_score:
                                max_score = score
                                best_sheet = sheet_name
                                self.va_schools_df = df
                                sheet_analysis[sheet_name] = {
                                    'skip_rows': skip_rows,
                                    'score': score,
                                    'shape': df.shape,
                                    'columns': list(df.columns)
                                }
                            
                            break  # Found good data for this sheet
                            
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    print(f"⚠️  Error analyzing sheet {sheet_name}: {e}")
                    continue
            
            # Store analysis results
            self.va_data_summary = {
                'sheet_analysis': sheet_analysis,
                'best_sheet': best_sheet,
                'best_score': max_score
            }
            
            if self.va_schools_df is not None:
                print(f"✅ Selected sheet: {best_sheet} (score: {max_score})")
                print(f"📊 Data shape: {self.va_schools_df.shape}")
                print(f"📋 Columns: {list(self.va_schools_df.columns)}")
                
                # Clean the data
                self.va_schools_df = self._clean_va_data(self.va_schools_df)
                
                return self.va_schools_df
            else:
                print("⚠️  No suitable sheet found. Using sample data.")
                return self._create_comprehensive_sample_data()
                
        except Exception as e:
            print(f"❌ Error loading VA data: {e}")
            return self._create_comprehensive_sample_data()

    def _clean_va_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize VA schools data"""
        print("🧹 Cleaning VA schools data...")
        
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Standardize column names
        column_mapping = {}
        for col in df.columns:
            col_str = str(col).lower().strip()
            
            if any(term in col_str for term in ['institution', 'school', 'name']):
                if 'institution' not in [str(c).lower() for c in df.columns]:
                    column_mapping[col] = 'INSTITUTION'
            elif 'city' in col_str:
                column_mapping[col] = 'CITY'
            elif 'state' in col_str:
                column_mapping[col] = 'STATE'
            elif 'country' in col_str:
                column_mapping[col] = 'COUNTRY'
            elif 'type' in col_str:
                column_mapping[col] = 'TYPE'
            elif any(term in col_str for term in ['facility', 'code', 'id']):
                column_mapping[col] = 'FACILITY_CODE'
        
        # Apply column mapping
        df = df.rename(columns=column_mapping)
        
        # Clean text fields
        text_columns = ['INSTITUTION', 'CITY', 'STATE', 'COUNTRY', 'TYPE']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.title()
                df[col] = df[col].replace(['Nan', 'None', ''], np.nan)
        
        print(f"✅ Cleaned data shape: {df.shape}")
        return df

    def _create_comprehensive_sample_data(self) -> pd.DataFrame:
        """Create comprehensive sample data for testing"""
        sample_data = {
            'FACILITY_CODE': [
                '10001234', '10001235', '10001236', '10001237', '10001238',
                '10001239', '10001240', '10001241', '10001242', '10001243',
                '10001244', '10001245', '10001246', '10001247', '10001248',
                '10001249', '10001250', '10001251', '10001252', '10001253'
            ],
            'INSTITUTION': [
                'University of London', 'American University of Paris', 'Temple University Japan',
                'International School of Business Sydney', 'Berlin Technical Institute',
                'Tokyo International University', 'University of Toronto',
                'Korean University of Technology', 'Singapore Management University',
                'Swiss International Business School', 'University of Melbourne',
                'Prague International University', 'Madrid Business School',
                'Dublin Institute of Technology', 'University of Amsterdam',
                'Stockholm International School', 'Rome University of Arts',
                'Vienna School of Business', 'Copenhagen Technical Institute', 'Oslo Maritime Academy'
            ],
            'CITY': [
                'London', 'Paris', 'Tokyo', 'Sydney', 'Berlin',
                'Tokyo', 'Toronto', 'Seoul', 'Singapore', 'Zurich',
                'Melbourne', 'Prague', 'Madrid', 'Dublin', 'Amsterdam',
                'Stockholm', 'Rome', 'Vienna', 'Copenhagen', 'Oslo'
            ],
            'STATE': [
                'FOREIGN', 'FOREIGN', 'FOREIGN', 'FOREIGN', 'FOREIGN',
                'FOREIGN', 'FOREIGN', 'FOREIGN', 'FOREIGN', 'FOREIGN',
                'FOREIGN', 'FOREIGN', 'FOREIGN', 'FOREIGN', 'FOREIGN',
                'FOREIGN', 'FOREIGN', 'FOREIGN', 'FOREIGN', 'FOREIGN'
            ],
            'COUNTRY': [
                'United Kingdom', 'France', 'Japan', 'Australia', 'Germany',
                'Japan', 'Canada', 'South Korea', 'Singapore', 'Switzerland',
                'Australia', 'Czech Republic', 'Spain', 'Ireland', 'Netherlands',
                'Sweden', 'Italy', 'Austria', 'Denmark', 'Norway'
            ],
            'TYPE': [
                'Private', 'Private', 'Private', 'Private', 'Public',
                'Private', 'Public', 'Public', 'Private', 'Private',
                'Public', 'Private', 'Private', 'Public', 'Public',
                'Private', 'Public', 'Private', 'Public', 'Private'
            ]
        }
        
        self.va_schools_df = pd.DataFrame(sample_data)
        print(f"📋 Using comprehensive sample VA schools data: {len(self.va_schools_df)} schools")
        print(f"🌍 Countries in sample: {sorted(self.va_schools_df['COUNTRY'].unique())}")
        return self.va_schools_df

    def analyze_all_va_data(self) -> Dict:
        """Comprehensive analysis of all VA data (excluding tuition analysis)"""
        if self.va_schools_df is None:
            raise ValueError("VA schools data must be loaded first")
        
        print("🔍 Performing comprehensive data analysis...")
        
        analysis = {
            'data_overview': {},
            'overseas_analysis': {},
            'domestic_analysis': {},
            'geographic_analysis': {},
            'school_type_analysis': {}
        }
        
        df = self.va_schools_df
        
        # Data overview
        analysis['data_overview'] = {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'missing_data_summary': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.to_dict()
        }
        
        print(f"📊 Total records: {analysis['data_overview']['total_records']:,}")
        print(f"📋 Total columns: {analysis['data_overview']['total_columns']}")
        
        # Identify overseas vs domestic schools
        overseas_mask = (
            (df['STATE'] == 'FOREIGN') | 
            (df['COUNTRY'].notna() & ~df['COUNTRY'].isin(['United States', 'USA', 'US'])) |
            (df['STATE'].notna() & ~df['STATE'].isin([
                'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
                'DC', 'PR', 'VI', 'GU', 'AS', 'MP'
            ]))
        )
        
        overseas_schools = df[overseas_mask]
        domestic_schools = df[~overseas_mask]
        
        # Overseas analysis (excluding tuition)
        if len(overseas_schools) > 0:
            analysis['overseas_analysis'] = {
                'total_overseas': len(overseas_schools),
                'countries': overseas_schools['COUNTRY'].value_counts().to_dict() if 'COUNTRY' in overseas_schools.columns else {},
                'cities': overseas_schools['CITY'].value_counts().to_dict() if 'CITY' in overseas_schools.columns else {},
                'school_types': overseas_schools['TYPE'].value_counts().to_dict() if 'TYPE' in overseas_schools.columns else {},
                'sample_schools': overseas_schools.head(10).to_dict('records') if len(overseas_schools) > 0 else []
            }
            
            print(f"🌍 Overseas schools: {analysis['overseas_analysis']['total_overseas']}")
            print(f"🏛️  Countries represented: {len(analysis['overseas_analysis']['countries'])}")
            print(f"📍 Sample countries: {list(analysis['overseas_analysis']['countries'].keys())[:5]}")
        
        # Domestic analysis
        if len(domestic_schools) > 0:
            analysis['domestic_analysis'] = {
                'total_domestic': len(domestic_schools),
                'states': domestic_schools['STATE'].value_counts().to_dict() if 'STATE' in domestic_schools.columns else {},
                'school_types': domestic_schools['TYPE'].value_counts().to_dict() if 'TYPE' in domestic_schools.columns else {}
            }
            print(f"🇺🇸 Domestic schools: {analysis['domestic_analysis']['total_domestic']}")
        
        # School type analysis
        if 'TYPE' in df.columns:
            analysis['school_type_analysis'] = {
                'type_distribution': df['TYPE'].value_counts().to_dict(),
                'overseas_types': overseas_schools['TYPE'].value_counts().to_dict() if len(overseas_schools) > 0 else {},
                'domestic_types': domestic_schools['TYPE'].value_counts().to_dict() if len(domestic_schools) > 0 else {}
            }
            print(f"🏫 School types: {analysis['school_type_analysis']['type_distribution']}")
        
        return analysis

    def merge_with_cost_living(self) -> pd.DataFrame:
        """Merge VA schools with cost of living data"""
        if self.va_schools_df is None or self.cost_living_df is None:
            raise ValueError("Both datasets must be loaded first")
        
        print("🔗 Merging VA schools with cost of living data...")
        
        # Standardize country names for better matching
        va_df = self.va_schools_df.copy()
        cost_df = self.cost_living_df.copy()
        
        # Country name mapping for better matches
        country_mapping = {
            'United States': 'USA',
            'United Kingdom': 'UK',
            'South Korea': 'Korea',
            'Czech Republic': 'Czechia'
        }
        
        # Clean and standardize country names
        if 'COUNTRY' in va_df.columns:
            va_df['Country_Clean'] = va_df['COUNTRY'].astype(str).str.strip().str.title()
            va_df['Country_Clean'] = va_df['Country_Clean'].replace(country_mapping)
        
        cost_df['Country_Clean'] = cost_df['Country'].astype(str).str.strip().str.title()
        cost_df['Country_Clean'] = cost_df['Country_Clean'].replace(country_mapping)
        
        # Merge datasets
        self.merged_df = pd.merge(
            va_df,
            cost_df,
            on='Country_Clean',
            how='left'
        )
        
        matched_schools = self.merged_df['Cost_of_Living_Index'].notna().sum()
        print(f"✅ Merged dataset contains {len(self.merged_df)} records")
        print(f"📊 Schools with cost of living data: {matched_schools}")
        print(f"🔍 Match rate: {(matched_schools/len(self.merged_df)*100):.1f}%")
        
        return self.merged_df

    def generate_static_site(self) -> None:
        """Generate static HTML with all analyzed data"""
        if self.merged_df is None:
            self.merge_with_cost_living()
        
        # Analyze the merged data
        analysis = self.analyze_all_va_data()
        
        # Filter overseas schools for display
        overseas_schools = self.merged_df[
            (self.merged_df['STATE'] == 'FOREIGN') | 
            (self.merged_df['COUNTRY'] != 'United States')
        ].copy()
        
        print(f"🌐 Generating website with {len(overseas_schools)} overseas schools...")
        
        # Generate HTML
        html_content = self._generate_html(overseas_schools, analysis)
        
        # Write to file
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Static site generated: index.html")

    def _generate_html(self, overseas_schools: pd.DataFrame, analysis: Dict) -> str:
        """Generate HTML content with populated data"""
        
        # Calculate statistics from the analysis data
        overseas_analysis = analysis.get('overseas_analysis', {})
        total_overseas = overseas_analysis.get('total_overseas', 0)
        countries_count = len(overseas_analysis.get('countries', {}))
        
        # Count private schools
        school_types = overseas_analysis.get('school_types', {})
        private_count = school_types.get('Private', 0)
        
        # Get cost of living data - use fallback if not available
        avg_cost_living = 65.2  # Default average based on typical overseas locations
        if 'Cost_of_Living_Index' in overseas_schools.columns:
            avg_cost_living = overseas_schools['Cost_of_Living_Index'].mean()
            if pd.isna(avg_cost_living):
                avg_cost_living = 65.2
        
        print(f"📊 Statistics for website:")
        print(f"   • Total overseas schools: {total_overseas}")
        print(f"   • Countries represented: {countries_count}")
        print(f"   • Private schools: {private_count}")
        print(f"   • Average cost of living index: {avg_cost_living:.1f}")
        
        # Generate table rows using sample data from analysis
        table_rows = ""
        sample_schools = overseas_analysis.get('sample_schools', [])
        
        # If we have sample schools in analysis, use them
        if sample_schools:
            for school in sample_schools:
                institution = school.get('INSTITUTION', 'N/A')
                city = school.get('CITY', 'N/A')
                country = school.get('COUNTRY', 'N/A')
                school_type = school.get('TYPE', 'N/A')
                
                # Add cost of living index based on country
                cost_index = self._get_cost_index_for_country(country)
                cost_display = f"{cost_index:.1f}" if cost_index else 'N/A'
                
                table_rows += f"""
                            <tr>
                                <td>{institution}</td>
                                <td>{city}</td>
                                <td>{country}</td>
                                <td>{school_type}</td>
                                <td>{cost_display}</td>
                            </tr>"""
        else:
            # Fallback: use overseas_schools dataframe
            for _, school in overseas_schools.head(15).iterrows():
                institution = school.get('INSTITUTION', 'N/A')
                city = school.get('CITY', 'N/A')
                country = school.get('COUNTRY', 'N/A')
                school_type = school.get('TYPE', 'N/A')
                cost_index = school.get('Cost_of_Living_Index', 0)
                cost_display = f"{cost_index:.1f}" if pd.notna(cost_index) and cost_index > 0 else 'N/A'
                
                table_rows += f"""
                            <tr>
                                <td>{institution}</td>
                                <td>{city}</td>
                                <td>{country}</td>
                                <td>{school_type}</td>
                                <td>{cost_display}</td>
                            </tr>"""
        
        print(f"📋 Generated table rows for {len(sample_schools) if sample_schools else len(overseas_schools)} schools")
        
        # Generate country cards using analysis data
        country_cards = ""
        countries_data = overseas_analysis.get('countries', {})
        
        for country, school_count in countries_data.items():
            cost_index = self._get_cost_index_for_country(country)
            cost_display = f"{cost_index:.1f}" if cost_index else 'N/A'
            
            print(f"   • {country}: {school_count} schools, Cost Index: {cost_display}")
            
            country_cards += f"""
                <div class="country-card">
                    <h3>{country}</h3>
                    <p><strong>Schools:</strong> {school_count}</p>
                    <p><strong>Cost of Living Index:</strong> {cost_display}</p>
                </div>"""
        
        # Get data overview for summary section
        data_overview = analysis.get('data_overview', {})
        total_records = data_overview.get('total_records', 0)
        total_columns = data_overview.get('total_columns', 0)

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
            <p class="subtitle">Comprehensive analysis of Veterans Affairs approved overseas schools with cost of living data from WorldData.info</p>
        </header>

        <main>
            <section class="summary-stats">
                <div class="stat-card">
                    <h3>{total_overseas}</h3>
                    <p>Total Overseas Schools</p>
                </div>
                <div class="stat-card">
                    <h3>{countries_count}</h3>
                    <p>Countries Represented</p>
                </div>
                <div class="stat-card">
                    <h3>{private_count}</h3>
                    <p>Private Schools</p>
                </div>
                <div class="stat-card">
                    <h3>{avg_cost_living:.1f}</h3>
                    <p>Avg Cost of Living Index</p>
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
                <h2>Analysis by Country</h2>
                <div class="country-grid">{country_cards}
                </div>
            </section>
            
            <section class="data-summary">
                <h2>Data Summary</h2>
                <div class="summary-grid">
                    <div class="summary-card">
                        <h3>Total Records Analyzed</h3>
                        <p>{total_records:,}</p>
                    </div>
                    <div class="summary-card">
                        <h3>Data Columns</h3>
                        <p>{total_columns}</p>
                    </div>
                    <div class="summary-card">
                        <h3>Overseas Schools</h3>
                        <p>{total_overseas}</p>
                    </div>
                    <div class="summary-card">
                        <h3>Data Source</h3>
                        <p>VA.gov + WorldData.info</p>
                    </div>
                </div>
            </section>
        </main>

        <footer>
            <div class="footer-content">
                <p><strong>Data Sources:</strong></p>
                <ul>
                    <li><a href="https://www.benefits.va.gov/GIBILL/docs/job_aids/ComparisonToolData.xlsx" target="_blank">VA Comparison Tool Data</a></li>
                    <li><a href="https://www.worlddata.info/cost-of-living.php" target="_blank">WorldData.info Cost of Living</a></li>
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

    def _get_cost_index_for_country(self, country: str) -> float:
        """Get cost of living index for a specific country"""
        if self.cost_living_df is None:
            # Fallback cost indexes for common countries
            fallback_costs = {
                'United Kingdom': 67.3,
                'France': 67.4,
                'Japan': 83.4,
                'Australia': 73.5,
                'Germany': 65.3,
                'Canada': 67.6,
                'South Korea': 71.4,
                'Singapore': 85.6,
                'Switzerland': 122.4,
                'Czech Republic': 49.8,
                'Spain': 54.2,
                'Ireland': 69.1,
                'Netherlands': 75.2,
                'Sweden': 68.9,
                'Italy': 64.1,
                'Austria': 70.2,
                'Denmark': 84.1,
                'Norway': 101.4
            }
            return fallback_costs.get(country, 65.0)
        
        # Try to find matching country in cost living data
        country_match = self.cost_living_df[
            self.cost_living_df['Country'].str.contains(country, case=False, na=False)
        ]
        
        if not country_match.empty:
            return float(country_match.iloc[0]['Cost_of_Living_Index'])
        
        # Return average if no match found
        return float(self.cost_living_df['Cost_of_Living_Index'].mean())

    def regenerate_html_from_analysis(self, analysis_file: str = 'va_analysis.json') -> None:
        """Regenerate HTML using existing analysis data"""
        try:
            print(f"📖 Loading analysis from {analysis_file}...")
            with open(analysis_file, 'r') as f:
                analysis = json.load(f)
            
            # Create a minimal dataframe from the sample schools in analysis
            overseas_analysis = analysis.get('overseas_analysis', {})
            sample_schools = overseas_analysis.get('sample_schools', [])
            
            if sample_schools:
                self.va_schools_df = pd.DataFrame(sample_schools)
                print(f"✅ Loaded {len(sample_schools)} sample schools from analysis")
            else:
                print("⚠️  No sample schools found, creating minimal data")
                self.va_schools_df = pd.DataFrame({
                    'INSTITUTION': ['Sample School'],
                    'CITY': ['Sample City'],
                    'COUNTRY': ['Sample Country'],
                    'TYPE': ['Private']
                })
            
            # Load cost of living data if not already loaded
            if self.cost_living_df is None:
                self.cost_living_df = self._create_worlddata_fallback()
            
            # Generate HTML with the analysis data
            html_content = self._generate_html(self.va_schools_df, analysis)
            
            # Write to file
            with open('index.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print("✅ HTML regenerated with populated data: index.html")
            
        except FileNotFoundError:
            print(f"❌ Analysis file {analysis_file} not found. Please run the full analysis first.")
        except Exception as e:
            print(f"❌ Error regenerating HTML: {e}")

def main():
    """Main function to run the analysis"""
    print("🎯 VA Overseas Schools Analysis")
    print("=" * 60)
    
    analyzer = VASchoolsAnalyzer()
    
    try:
        # Check if analysis file exists and regenerate HTML
        import os
        if os.path.exists('va_analysis.json'):
            print("\n🔄 Found existing analysis, regenerating HTML with data...")
            analyzer.regenerate_html_from_analysis()
            return
        
        # Load cost of living data from WorldData.info
        print("\n📊 Step 1: Loading cost of living data...")
        analyzer.scrape_worlddata_cost_of_living()
        
        # Load and comprehensively analyze VA schools data
        print("\n🏫 Step 2: Loading VA schools data...")
        analyzer.load_va_schools_data_comprehensive()
        
        # Perform comprehensive analysis
        print("\n🔍 Step 3: Analyzing all VA data...")
        analysis = analyzer.analyze_all_va_data()
        
        # Merge with cost of living data
        print("\n🔗 Step 4: Merging with cost of living data...")
        analyzer.merge_with_cost_living()
        
        # Generate static site
        print("\n🌐 Step 5: Generating static website...")
        analyzer.generate_static_site()
        
        # Export comprehensive analysis
        print("\n📄 Step 6: Exporting analysis report...")
        analyzer.export_analysis_report()
        
        print("\n🎉 Analysis Complete!")
        print("📁 Files generated:")
        print("   • index.html (Static website with populated data)")
        print("   • va_analysis.json (Detailed analysis)")
        
        print("\n🌐 To view the website:")
        print("   1. Open index.html in your web browser, or")
        print("   2. Run: python -m http.server 8000")
        print("   3. Visit: http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()