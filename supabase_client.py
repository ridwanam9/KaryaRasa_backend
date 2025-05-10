# from supabase import create_client, Client
# import os

# SUPABASE_URL = os.getenv("https://qqxwgvcakthdawooayak.supabase.co")
# SUPABASE_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxeHdndmNha3RoZGF3b29heWFrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0Mjk5ODk1MiwiZXhwIjoyMDU4NTc0OTUyfQ.RJa1P6UNntq5NnkSV3c07w-E5OUNXh5wbOeMXnnspRo")
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load isi .env
load_dotenv()

# Ambil dari ENV variabel, bukan langsung nilainya
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Cek kalau nilainya tidak ditemukan
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("SUPABASE_URL or SUPABASE_KEY is not set in environment variables.")

# Buat client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
