#!/usr/bin/env python3
"""
Run the enhanced VA overseas schools analysis
"""

import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from enhanced_data_processor import EnhancedVASchoolsAnalyzer
    
    def main():
        print("🎯 Starting Enhanced VA Overseas Schools Analysis")
        print("=" * 60)
        
        analyzer = EnhancedVASchoolsAnalyzer()
        
        # Step 1: Load cost of living data
        print("\n📊 Step 1: Loading cost of living data from WorldData.info...")
        try:
            cost_df = analyzer.scrape_worlddata_cost_of_living()
            print(f"✅ Loaded cost of living data for {len(cost_df)} countries")
        except Exception as e:
            print(f"⚠️  Using fallback cost of living data: {e}")
        
        # Step 2: Load VA schools data
        print("\n🏫 Step 2: Loading VA schools data...")
        try:
            va_df = analyzer.load_va_schools_data_comprehensive()
            print(f"✅ Loaded VA schools data: {len(va_df)} records")
        except Exception as e:
            print(f"⚠️  Using sample VA data: {e}")
        
        # Step 3: Analyze all data
        print("\n🔍 Step 3: Performing comprehensive analysis...")
        try:
            analysis = analyzer.analyze_all_va_data()
            
            # Print key findings
            print(f"\n📈 Key Findings:")
            print(f"   • Total VA records: {analysis['data_overview']['total_records']:,}")
            print(f"   • Data columns: {analysis['data_overview']['total_columns']}")
            
            if 'overseas_analysis' in analysis:
                overseas_count = analysis['overseas_analysis'].get('total_overseas', 0)
                countries = len(analysis['overseas_analysis'].get('countries', {}))
                print(f"   • Overseas schools: {overseas_count}")
                print(f"   • Countries represented: {countries}")
            
            if 'domestic_analysis' in analysis:
                domestic_count = analysis['domestic_analysis'].get('total_domestic', 0)
                print(f"   • Domestic schools: {domestic_count}")
                
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return
        
        # Step 4: Merge with cost of living
        print("\n🌍 Step 4: Merging with cost of living data...")
        try:
            merged_df = analyzer.merge_with_cost_living()
            schools_with_cost_data = merged_df['Cost_of_Living_Index'].notna().sum()
            print(f"✅ Merged successfully: {schools_with_cost_data} schools have cost data")
        except Exception as e:
            print(f"⚠️  Merge warning: {e}")
        
        # Step 5: Generate website
        print("\n🌐 Step 5: Generating enhanced website...")
        try:
            analyzer.generate_enhanced_static_site()
            print("✅ Generated: index.html")
        except Exception as e:
            print(f"❌ Website generation failed: {e}")
        
        # Step 6: Export analysis
        print("\n📄 Step 6: Exporting analysis report...")
        try:
            analyzer.export_analysis_report()
            print("✅ Generated: comprehensive_va_analysis.json")
        except Exception as e:
            print(f"❌ Report export failed: {e}")
        
        print("\n🎉 Analysis Complete!")
        print("\nFiles generated:")
        print("• index.html - Enhanced static website")
        print("• comprehensive_va_analysis.json - Detailed analysis report")
        print("\nTo view the website:")
        print("1. Open index.html in your web browser, or")
        print("2. Run: python -m http.server 8000")
        print("3. Then visit: http://localhost:8000")

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