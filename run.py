#!/usr/bin/env python3
"""
Easy launcher script for Social Media Review Analyzer
Provides choice between web interface and command line
"""

import os
import sys
import subprocess

def print_header():
    """Print application header"""
    print("=" * 60)
    print("🚀 Social Media Review Analyzer")
    print("=" * 60)
    print()

def check_prerequisites():
    """Check if setup is complete"""
    issues = []
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        issues.append("❌ .env file not found")
        issues.append("   Run: cp .env.template .env")
        issues.append("   Then edit .env with your OpenAI API key")
    
    # Check if virtual environment exists
    venv_paths = ['venv/Scripts/python.exe', 'venv/bin/python']
    venv_exists = any(os.path.exists(path) for path in venv_paths)
    
    if not venv_exists:
        issues.append("❌ Virtual environment not found")
        issues.append("   Run: python -m venv venv")
        issues.append("   Then: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Mac/Linux)")
        issues.append("   Then: pip install -r requirements.txt")
    
    # Check if requirements are installed
    try:
        import streamlit
        import openai
        import pandas
    except ImportError as e:
        issues.append(f"❌ Missing dependency: {e}")
        issues.append("   Run: pip install -r requirements.txt")
    
    return issues

def get_user_choice():
    """Get user's choice for interface"""
    print("Choose your interface:")
    print()
    print("1. 🌐 Web Interface (Recommended)")
    print("   - Beautiful graphical interface")
    print("   - Real-time progress tracking")
    print("   - Interactive charts and visualizations")
    print("   - Easy URL input and configuration")
    print()
    print("2. 💻 Command Line Interface")
    print("   - Text-based interface")
    print("   - Suitable for automation")
    print("   - Runs in terminal")
    print()
    print("3. ❓ Help & Setup")
    print("   - Setup instructions")
    print("   - Troubleshooting guide")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1, 2, or 3): ").strip()
            if choice in ['1', '2', '3']:
                return int(choice)
            else:
                print("Please enter 1, 2, or 3")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(0)

def launch_web_interface():
    """Launch Streamlit web interface"""
    print("\n🌐 Launching Web Interface...")
    print("📝 Note: Your browser should open automatically")
    print("🔗 If not, go to: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Web interface stopped.")
    except FileNotFoundError:
        print("❌ Streamlit not found. Please run: pip install streamlit")
    except Exception as e:
        print(f"❌ Error launching web interface: {e}")

def launch_command_line():
    """Launch command line interface"""
    print("\n💻 Launching Command Line Interface...")
    print()
    
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Command line interface stopped.")
    except Exception as e:
        print(f"❌ Error launching command line interface: {e}")

def show_help():
    """Show help and setup information"""
    print("\n📚 Help & Setup Guide")
    print("=" * 30)
    print()
    
    print("🔧 Quick Setup:")
    print("1. Create virtual environment: python -m venv venv")
    print("2. Activate it:")
    print("   Windows: venv\\Scripts\\activate")
    print("   Mac/Linux: source venv/bin/activate")
    print("3. Install dependencies: pip install -r requirements.txt")
    print("4. Setup environment: cp .env.template .env")
    print("5. Edit .env with your OpenAI API key")
    print("6. Run: python run.py")
    print()
    
    print("🌐 Web Interface Features:")
    print("- Drag & drop URL input")
    print("- Real-time progress tracking")
    print("- Interactive charts and graphs")
    print("- Download Excel reports")
    print("- AI-powered insights display")
    print()
    
    print("💻 Command Line Features:")
    print("- Text-based input/output")
    print("- Suitable for scripting")
    print("- Detailed logging")
    print("- Batch processing capable")
    print()
    
    print("🆘 Troubleshooting:")
    print("- Module not found: pip install -r requirements.txt")
    print("- OpenAI errors: Check API key in .env file")
    print("- No reviews found: Verify URLs are correct")
    print("- Slow processing: Normal for large datasets")
    print()
    
    print("📖 Full documentation: See README.md")
    print()
    
    input("Press Enter to return to main menu...")

def main():
    """Main launcher function"""
    print_header()
    
    # Check prerequisites
    issues = check_prerequisites()
    if issues:
        print("⚠️  Setup Issues Found:")
        for issue in issues:
            print(f"   {issue}")
        print()
        print("Please fix these issues before continuing.")
        print("Choose option 3 for detailed setup help.")
        print()
    
    while True:
        choice = get_user_choice()
        
        if choice == 1:
            if not issues:
                launch_web_interface()
            else:
                print("❌ Please fix setup issues first (choose option 3 for help)")
            break
            
        elif choice == 2:
            if not issues:
                launch_command_line()
            else:
                print("❌ Please fix setup issues first (choose option 3 for help)")
            break
            
        elif choice == 3:
            show_help()
            # Return to menu after help
            continue

if __name__ == "__main__":
    main()