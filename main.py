from app import create_app
from seed import seed_data 
# from dotenv import load_dotenv

# load_dotenv()

app = create_app()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'seed':
        with app.app_context():
            seed_data()
    else:
        app.run(debug=True)