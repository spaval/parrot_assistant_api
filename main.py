from dotenv import load_dotenv
from app import App

def main():
    load_dotenv(f"config/.env")
    
    app = App()
    app.run()
    
if __name__ == '__main__':
    main()