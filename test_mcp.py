import importlib.util
import pkgutil

def check_package(package_name):
    try:
        # Try to import the package
        package = importlib.import_module(package_name)
        print(f"✅ Successfully imported {package_name} (version: {getattr(package, '__version__', 'unknown')})")
        
        # List all modules in the package
        print("Package contents:")
        try:
            for _, name, _ in pkgutil.iter_modules(package.__path__):
                print(f"- {name}")
                try:
                    module = importlib.import_module(f"{package_name}.{name}")
                    print(f"  - Classes: {[cls for cls in dir(module) if not cls.startswith('_')]}")
                except Exception as e:
                    print(f"  - Could not import module: {e}")
        except Exception as e:
            print(f"Could not list package contents: {e}")
            
    except ImportError as e:
        print(f"❌ Could not import {package_name}: {e}")

if __name__ == "__main__":
    print("Checking MCP package...")
    check_package("mcp")
    
    print("Checking langchain_mcp_adapters...")
    check_package("langchain_mcp_adapters")
