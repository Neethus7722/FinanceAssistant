#!/usr/bin/env python3
"""
Main Data Import Runner
======================

Standard execution script for importing employee data with semantic embeddings.
This script provides a unified entry point for data import operations.

Usage:
    python run_import.py [--clean] [--help]
    
Options:
    --clean    : Clean database before import
    --help     : Show this help message

Requirements:
    - Configure environment variables in config/.env
    - Ensure employee_data.xlsx is in source/ directory
    - PostgreSQL with pgvector extension enabled
"""

import sys
import argparse
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent / "scripts"))

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Employee Data Import with Semantic Embeddings",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--clean', 
        action='store_true',
        help='Clean database before import'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Employee Data Import System")
    print("=" * 60)
    
    # Check required files
    config_file = Path("config/.env")
    source_file = Path("source/employee_data.xlsx")
    
    if not config_file.exists():
        print("❌ Configuration file not found: config/.env")
        print("   Please copy config/.env.template and configure your settings")
        return
        
    if not source_file.exists():
        print("❌ Source data file not found: source/employee_data.xlsx")
        return
    
    print("✅ Configuration file found")
    print("✅ Source data file found")
    print()
    
    # Clean database if requested
    if args.clean:
        print("🧹 Cleaning database...")
        try:
            from database_cleanup import main as cleanup_main
            cleanup_main()
            print("✅ Database cleaned successfully")
        except Exception as e:
            print(f"❌ Database cleanup failed: {e}")
            return
        print()
    
    # Run data import
    print("📊 Starting data import...")
    try:
        from data_importer import main as import_main
        import_main()
        print("\n✅ Data import completed successfully!")
    except Exception as e:
        print(f"\n❌ Data import failed: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Import process completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
