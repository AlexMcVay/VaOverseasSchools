#!/usr/bin/env python3
"""
Run the VA overseas schools analysis
"""

import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from data_processor import VASchoolsAnalyzer
    
    def main():
        print("🎯 VA FOREIGN Schools Analysis")
        print("=" * 60)
        
        try:
            from script import VAOverseasSchoolsAnalyzer
            
            analyzer = VAOverseasSchoolsAnalyzer()
            
            # Step 1: Load VA schools data focusing on FOREIGN schools
            print("\n🏫 Step 1: Loading VA schools data...")
            try:
                analyzer.load_va_schools_data()
                foreign_summary = analyzer.get_foreign_schools_summary()
                print(f"✅ Successfully loaded {foreign_summary['total_schools']} FOREIGN schools")
                print(f"✅ Countries represented: {len(foreign_summary['countries'])}")
                
                if foreign_summary['countries']:
                    print("   Countries with schools:")
                    # Show all countries, not just first 10
                    for country, count in foreign_summary['countries'].items():
                        print(f"   • {country}: {count} schools")
                    
                    # Show breakdown by school type
                    if foreign_summary['school_types']:
                        print("\n   School types:")
                        for school_type, count in foreign_summary['school_types'].items():
                            print(f"   • {school_type}: {count} schools")
                        
            except Exception as e:
                print(f"⚠️  Error loading VA data: {e}")
                print("   Using comprehensive sample data instead...")
        
            # Step 2: Load cost of living data (optional)
            print("\n📊 Step 2: Loading cost of living data...")
            try:
                analyzer.load_cost_living_data()
                print("✅ Cost of living data loaded")
            except Exception as e:
                print(f"⚠️  Cost of living data unavailable: {e}")
                print("   Proceeding without cost data...")
        
            # Step 3: Generate website with FOREIGN schools
            print("\n🌐 Step 3: Generating website...")
            try:
                # Validate data before generating website
                pre_gen_summary = analyzer.get_foreign_schools_summary()
                print(f"🔍 Pre-generation validation:")
                print(f"   • Schools available: {pre_gen_summary['total_schools']}")
                print(f"   • Countries: {len(pre_gen_summary['countries'])}")
                
                if pre_gen_summary['total_schools'] == 0:
                    print("⚠️  No schools data available - ensuring sample data is loaded...")
                    # Force load sample data if no schools found
                    if hasattr(analyzer, 'ensure_sample_data'):
                        analyzer.ensure_sample_data()
                    
                analyzer.generate_static_website()
                
                # Verify data was properly written to website
                foreign_summary = analyzer.get_foreign_schools_summary()  # Refresh summary
                print("✅ Generated: index.html")
                print(f"✅ Website populated with {foreign_summary['total_schools']} schools")
                
                # Verify HTML file contains data
                try:
                    with open('index.html', 'r', encoding='utf-8') as f:
                        html_content = f.read()
                        if 'schoolsData' in html_content and len(html_content) > 5000:
                            print("✅ HTML file contains embedded data")
                        else:
                            print("⚠️  HTML file may be missing data - check generation process")
                except Exception as html_e:
                    print(f"⚠️  Could not verify HTML content: {html_e}")
                
                # Show some sample schools
                if foreign_summary['schools_list']:
                    print("\n   Sample schools included:")
                    for school in foreign_summary['schools_list'][:5]:
                        inst = school.get('INSTITUTION', 'Unknown')
                        country = school.get('COUNTRY', 'Unknown')
                        print(f"   • {inst} ({country})")
                        
            except Exception as e:
                print(f"❌ Website generation failed: {e}")
                return
            
            # Step 4: Generate analysis report
            print("\n📄 Step 4: Generating analysis report...")
            try:
                analyzer.generate_report()
                print("✅ Generated: va_overseas_schools_report.txt")
            except Exception as e:
                print(f"⚠️  Report generation warning: {e}")
            
            # Step 5: Generate updated JSON analysis
            print("\n📊 Step 5: Updating analysis JSON...")
            try:
                import json
                with open('comprehensive_va_analysis.json', 'w') as f:
                    json.dump({
                        "data_overview": {
                            "total_records": foreign_summary['total_schools'],
                            "countries_represented": len(foreign_summary['countries']),
                            "data_source": "VA Comparison Tool or Sample Data"
                        },
                        "overseas_analysis": foreign_summary
                    }, f, indent=2)
                print("✅ Updated: comprehensive_va_analysis.json")
            except Exception as e:
                print(f"⚠️  JSON update warning: {e}")
            
            print("\n🎉 Analysis Complete!")
            print(f"\n📊 Final Results:")
            print(f"   • Total schools displayed: {foreign_summary['total_schools']}")
            print(f"   • Countries represented: {len(foreign_summary['countries'])}")
            print(f"   • Private schools: {foreign_summary['school_types'].get('Private', 0)}")
            print(f"   • Public schools: {foreign_summary['school_types'].get('Public', 0)}")
            
            print(f"\n📁 Files generated:")
            print(f"   • index.html (main website)")
            print(f"   • styles.css (styling)")
            print(f"   • script.js (interactivity)")
            print(f"   • va_overseas_schools_report.txt (detailed report)")
            
            print("\n🌐 To view the website:")
            print("   1. Open terminal in this folder")
            print("   2. Run: python -m http.server 8000")
            print("   3. Visit: http://localhost:8000")
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("\nPlease install required packages:")
            print("pip install pandas numpy requests openpyxl")
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nPlease install required packages:")
    print("pip install pandas numpy requests beautifulsoup4 lxml")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()