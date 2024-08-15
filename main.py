from pyrogram import Client, errors
from pyrogram.raw import functions
from urllib.parse import unquote
import logging
import os
import asyncio
from colorama import init, Fore, Style

# Inisialisasi colorama
init()

# Pengaturan logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mengatur level logging untuk pyrogram menjadi WARNING
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# Ganti dengan path folder sesi
SESSIONS_FOLDER = 'sessions'
QUERY_FILE = "query.txt"

async def generate_query(session_name, api_id, api_hash, bot_username, bot_url):
    """Mengambil query dari bot dan menyimpannya ke query.txt"""
    try:
        async with Client(session_name, api_id=api_id, api_hash=api_hash) as client:
            if not client.is_connected:
                await client.start()
            
            # Menyelesaikan peer untuk bot
            peer = await client.resolve_peer(bot_username)
            
            # Meminta webview
            webview = await client.invoke(functions.messages.RequestWebView(
                peer=peer,
                bot=peer,
                from_bot_menu=False,
                platform='Android',
                url=bot_url
            ))
            
            # Mengekstrak query dari URL
            query = unquote(webview.url.split("&tgWebAppVersion=")[0].split("#tgWebAppData=")[1])
            
            # Menyimpan query ke dalam query.txt
            with open(QUERY_FILE, "a") as file:  # Mode append
                file.write(f"{query}\n")
            
            print(Fore.GREEN + f"Data untuk {session_name} disimpan ke {QUERY_FILE}" + Style.RESET_ALL)
    
    except errors.FloodWait as e:
        logger.error(f"Kesalahan flood wait untuk {session_name}: {str(e)}")
    except Exception as e:
        print(Fore.RED + f"Gagal menyimpan data untuk {session_name} ke {QUERY_FILE}" + Style.RESET_ALL)
        logger.error(f"Kesalahan saat mengambil data query untuk {session_name}: {str(e)}")

async def create_new_session(session_name, api_id, api_hash):
    """Membuat sesi baru dan menyimpannya ke dalam folder sesi"""
    try:
        async with Client(session_name, api_id=api_id, api_hash=api_hash) as client:
            # Tidak perlu memanggil client.start() di sini karena klien sudah terhubung secara otomatis
            logger.info(f"Sesi baru dibuat: {session_name}")
    except Exception as e:
        logger.error(f"Kesalahan saat membuat sesi baru {session_name}: {str(e)}")

async def add_session(api_id, api_hash):
    """Fungsi untuk menambahkan sesi baru"""
    session_name = input("Masukkan nama untuk sesi baru: ")
    await create_new_session(os.path.join(SESSIONS_FOLDER, session_name), api_id, api_hash)

async def generate_queries(api_id, api_hash, bot_username, bot_url):
    """Fungsi untuk menghasilkan query dari sesi yang ada"""
    while True:
        # Mendapatkan semua file sesi di folder sessions
        sessions = [f[:-8] for f in os.listdir(SESSIONS_FOLDER) if f.endswith('.session')]
        
        # Mengosongkan file query.txt sebelum memulai
        if os.path.exists(QUERY_FILE):
            os.remove(QUERY_FILE)
        
        tasks = []
        for session_name in sessions:
            # Menghasilkan query untuk setiap sesi yang ada
            tasks.append(generate_query(os.path.join(SESSIONS_FOLDER, session_name), api_id, api_hash, bot_username, bot_url))
        
        await asyncio.gather(*tasks)
        
        # Menunggu 6 jam sebelum menghasilkan query lagi
        print(Fore.YELLOW + "Menunggu 6 jam sebelum pembuatan query berikutnya..." + Style.RESET_ALL)
        await asyncio.sleep(21600)  # 21600 detik = 6 jam

async def main():
    """Fungsi utama untuk memilih antara menambah sesi atau menghasilkan query"""
    # Placeholder untuk API ID dan API hash jika diperlukan
    api_id = '599686'  # Ganti dengan API ID yang sebenarnya
    api_hash = '12b428f536a2e7cc76296db0805e91e9'  # Ganti dengan API Hash yang sebenarnya

    # Membuat folder sessions jika belum ada
    if not os.path.exists(SESSIONS_FOLDER):
        os.makedirs(SESSIONS_FOLDER)

    print("Pilih opsi:")
    print("1. Tambah Sesi")
    print("2. Generate Query")
    choice = input("Masukkan pilihan (1 atau 2): ")

    if choice == '1':
        await add_session(api_id, api_hash)
    elif choice == '2':
        bot_username = input("Masukkan username bot (contoh: tabizoobot): ")
        bot_url = input("Masukkan URL Header Bot (contoh: https://app.tabibot.com): ")
        await generate_queries(api_id, api_hash, bot_username, bot_url)
    else:
        print("Pilihan tidak valid")

if __name__ == "__main__":
    asyncio.run(main())
