#!/usr/bin/env python3
"""
Download and process the complete VA schools dataset to find all overseas schools
"""

import pandas as pd
import requests
from io import BytesIO
import json
import time

print('[DEBUG] Script is running (top of file)')

def download_complete_va_dataset():
    print('[DEBUG] Entered download_complete_va_dataset')
    """Download the complete VA comparison tool dataset"""
    print("🌐 Downloading complete VA schools dataset...")
    
    # Primary URL for VA Comparison Tool Data
    urls_to_try = [
        "https://www.benefits.va.gov/GIBILL/docs/job_aids/ComparisonToolData.xlsx",
        "https://www.va.gov/education/gi-bill-comparison-tool/",
        "https://inquiry.vba.va.gov/weamspub/buildSearchInstitutionCriteria.do"
    ]
    
    for url in urls_to_try:
        try:
            print(f"Trying URL: {url}")
            
            if url.endswith('.xlsx'):
                # Direct Excel download
                response = requests.get(url, timeout=60)
                response.raise_for_status()
                
                excel_data = BytesIO(response.content)
                excel_file = pd.ExcelFile(excel_data)
                
                print(f"Available sheets: {excel_file.sheet_names}")
                
                # Try each sheet to find the main data
                largest_df = None
                largest_size = 0
                
                for sheet_name in excel_file.sheet_names:
                    try:
                        df = pd.read_excel(excel_data, sheet_name=sheet_name)
                        print(f"Sheet '{sheet_name}': {len(df)} rows, {len(df.columns)} columns")
                        print(df.head(3))  # Print first 3 rows for inspection
                        
                        # Clean column names
                        df.columns = [str(col).strip().upper() for col in df.columns]
                        
                        # Look for key indicators of school data
                        key_cols = ['FACILITY', 'INSTITUTION', 'SCHOOL', 'NAME']
                        location_cols = ['STATE', 'COUNTRY', 'CITY']
                        
                        has_schools = any(any(key in col for col in df.columns) for key in key_cols)
                        has_location = any(any(loc in col for col in df.columns) for loc in location_cols)
                        
                        if has_schools and has_location and len(df) > largest_size:
                            largest_df = df.copy()
                            largest_size = len(df)
                            print(f"   → Found dataset with {len(df)} schools")
                            
                    except Exception as e:
                        print(f"   Error reading sheet '{sheet_name}': {e}")
                        continue
                
                if largest_df is not None:
                    print('[DEBUG] Exiting download_complete_va_dataset')
                    return largest_df
                    
        except Exception as e:
            print(f"   Failed: {e}")
            continue
    
    print("❌ Could not download VA dataset from official sources")
    print('[DEBUG] Exiting download_complete_va_dataset')
    return None

def process_overseas_schools(df):
    print('[DEBUG] Entered process_overseas_schools')
    """Process the dataset to extract all overseas/international schools"""
    if df is None:
        return None
    
    print(f"\n📊 Processing dataset with {len(df)} total schools...")
    
    # Standardize column names
    column_mapping = {}
    for col in df.columns:
        col_upper = str(col).upper()
        if any(x in col_upper for x in ['FACILITY', 'CODE']):
            column_mapping[col] = 'FACILITY_CODE'
        elif any(x in col_upper for x in ['INSTITUTION', 'SCHOOL']) and 'FACILITY' not in col_upper:
            column_mapping[col] = 'INSTITUTION'
        elif 'CITY' in col_upper:
            column_mapping[col] = 'CITY'
        elif 'STATE' in col_upper and 'COUNTRY' not in col_upper:
            column_mapping[col] = 'STATE'
        elif 'COUNTRY' in col_upper:
            column_mapping[col] = 'COUNTRY'
        elif any(x in col_upper for x in ['TYPE', 'CONTROL']):
            column_mapping[col] = 'TYPE'
        elif 'TUITION' in col_upper and 'OUT' in col_upper:
            column_mapping[col] = 'TUITION_OUT_OF_STATE'
        elif 'TUITION' in col_upper and 'IN' in col_upper:
            column_mapping[col] = 'TUITION_IN_STATE'
    
    df = df.rename(columns=column_mapping)
    
    # Remove duplicate columns after renaming
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Remove empty rows
    df = df.dropna(how='all')
    
    print(f"Available columns: {list(df.columns)}")
    
    # Find overseas schools
    if 'COUNTRY' in df.columns:
        # Only use COUNTRY column for overseas detection
        non_us_countries = df['COUNTRY'].astype(str).str.upper()
        overseas_df = df[~non_us_countries.isin(['UNITED STATES', 'USA', 'US', 'NAN', 'NONE', '']) & (non_us_countries != '')].copy()
        print(f"🎯 Found {len(overseas_df)} potential overseas schools (COUNTRY filter only)")
    else:
        print("⚠️  Could not identify overseas schools - no COUNTRY column found")
        return None

    # Show sample of what we found
    if len(overseas_df) > 0:
        print("\nSample overseas schools found:")
        for i, row in overseas_df.head(10).iterrows():
            institution = row.get('INSTITUTION', 'Unknown')
            country = row.get('COUNTRY', 'Unknown')
            city = row.get('CITY', 'Unknown')
            print(f"  • {institution} - {city}, {country}")

    print('[DEBUG] Exiting process_overseas_schools')
    return overseas_df

def create_comprehensive_json(overseas_df):
    print('[DEBUG] Entered create_comprehensive_json')
    """Create a comprehensive JSON file with all overseas schools"""
    if overseas_df is None or len(overseas_df) == 0:
        print("❌ No overseas schools data to process")
        return
    
    # Convert to records for JSON
    schools_list = []
    for _, row in overseas_df.iterrows():
        school = {
            'FACILITY_CODE': str(row.get('FACILITY_CODE', '')),
            'INSTITUTION': str(row.get('INSTITUTION', '')),
            'CITY': str(row.get('CITY', '')),
            'STATE': str(row.get('STATE', '')),
            'COUNTRY': str(row.get('COUNTRY', '')),
            'TYPE': str(row.get('TYPE', '')),
            'TUITION_IN_STATE': row.get('TUITION_IN_STATE', 0),
            'TUITION_OUT_OF_STATE': row.get('TUITION_OUT_OF_STATE', 0)
        }
        schools_list.append(school)
    
    # Create summary statistics
    countries = overseas_df['COUNTRY'].value_counts().to_dict() if 'COUNTRY' in overseas_df.columns else {}
    cities = overseas_df['CITY'].value_counts().to_dict() if 'CITY' in overseas_df.columns else {}
    school_types = overseas_df['TYPE'].value_counts().to_dict() if 'TYPE' in overseas_df.columns else {}
    
    # Create comprehensive data structure
    comprehensive_data = {
        "data_overview": {
            "total_records": len(overseas_df),
            "countries_represented": len(countries),
            "data_source": "VA Comparison Tool - Complete Dataset",
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "overseas_analysis": {
            "total_schools": len(overseas_df),
            "countries": countries,
            "cities": cities,
            "school_types": school_types,
            "schools_list": schools_list
        }
    }
    
    # Save to JSON file
    with open('comprehensive_va_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created comprehensive_va_analysis.json with {len(schools_list)} schools")
    print(f"📊 Countries: {len(countries)}")
    print(f"🏙️  Cities: {len(cities)}")
    print(f"🏫 School types: {school_types}")
    
    print('[DEBUG] Exiting create_comprehensive_json')
    return comprehensive_data

def main():
    print("🌍 VA COMPREHENSIVE OVERSEAS SCHOOLS DATASET PROCESSOR")
    print("=" * 60)
    
    # Step 1: Download complete dataset
    df = download_complete_va_dataset()
    if df is not None:
        print(f"[DEBUG] Downloaded DataFrame shape: {df.shape}")
        print(f"[DEBUG] Columns: {list(df.columns)}")
    else:
        print("❌ Could not download VA dataset. Using existing data...")
        return
    
    # Step 2: Process for overseas schools
    overseas_df = process_overseas_schools(df)
    if overseas_df is not None:
        print(f"[DEBUG] Overseas DataFrame shape: {overseas_df.shape}")
    else:
        print("❌ No overseas schools found.")
        return
    
    # Step 3: Create comprehensive JSON
    comprehensive_data = create_comprehensive_json(overseas_df)
    
    if comprehensive_data:
        print(f"\n🎉 SUCCESS! Found {comprehensive_data['overseas_analysis']['total_schools']} overseas schools")
        print("📄 Data saved to: comprehensive_va_analysis.json")
    else:
        print("❌ Failed to create comprehensive dataset")

print("[DEBUG] Script started.")

if __name__ == "__main__":
    try:
        print('[DEBUG] __main__ block starting')
        main()
        print('[DEBUG] __main__ block finished')
    except Exception as e:
        import traceback
        print("[ERROR] Exception in script:")
        traceback.print_exc()
