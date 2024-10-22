import requests
import json
import time
from datetime import datetime, timedelta
from colorama import Fore, Style, init

init(autoreset=True)

def print_welcome_message():
    print(Fore.WHITE + r"""
_  _ _   _ ____ ____ _    ____ _ ____ ___  ____ ____ ___ 
|\ |  \_/  |__| |__/ |    |__| | |__/ |  \ |__/ |  | |__]
| \|   |   |  | |  \ |    |  | | |  \ |__/ |  \ |__| |         
          """)
    print(Fore.GREEN + Style.BRIGHT + "Nyari Airdrop Cat Gold Miner")
    print(Fore.YELLOW + Style.BRIGHT + "Telegram: https://t.me/nyariairdrop")

def load_accounts():
    with open('data.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

def login(authorization):
    url = "https://api-server1.catgoldminer.ai/auth/login"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    payload = {"refBy": ""}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_profile(authorization):
    url = "https://api-server1.catgoldminer.ai/users/getProfile2"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_all_social_quests(authorization):
    url = "https://api-server1.catgoldminer.ai/quest/getAllSocialQuestAndStatus"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_all_daily_quests(authorization):
    url = "https://api-server1.catgoldminer.ai/quest/getAllDailyQuestAndStatus"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def claim_quest(authorization, action_code, quest_type, quest_value):
    url = "https://api-server1.catgoldminer.ai/quest/claimQuest"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    payload = {
        "actionCode": action_code,
        "questType": quest_type,
        "questValue": quest_value
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def do_telegram_quest(authorization, action_code, quest_value):
    url = "https://api-server1.catgoldminer.ai/quest/doTelegramQuest"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    payload = {
        "actionCode": action_code,
        "questValue": quest_value
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_offline_currency(authorization, mine_id, location_id):
    url = "https://api-server1.catgoldminer.ai/users/getOfflineCurrency"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    payload = {
        "mineID": mine_id,
        "locationID": location_id
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def claim_offline_currency(authorization, mine_id, location_id):
    url = "https://api-server1.catgoldminer.ai/users/claimOfflineCurrency2"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    payload = {
        "mineID": mine_id,
        "locationID": location_id,
        "isClaimWithHardCurrency": False,
        "hashSoftCurrencyProfile": None
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def process_quests(authorization):
    # Ambil semua quest harian dan sosial
    daily_quests = get_all_daily_quests(authorization)
    social_quests = get_all_social_quests(authorization)

    if daily_quests['code'] != 0 or social_quests['code'] != 0:
        print(Fore.RED + "Gagal mengambil data quest.")
        return


    # Gabungkan semua quest (harian dan sosial)
    all_quests = daily_quests['data'] + social_quests['data']

    for quest in all_quests:
        # Cek jika quest sudah diklaim
        if quest.get('claimStatus', False):
            print(Fore.YELLOW + f"Quest sudah diklaim: {quest['questDescription']}. Melewati.")
            continue

        # Cek validitas waktu jika diperlukan
        if quest.get('isCheckTimeValidQuest', False) and quest.get('timeValidQuest', 0) > 0:
            # Pastikan 'claimDate' tersedia sebelum mencoba menggunakannya
            if 'claimDate' in quest:
                current_time = time.time()
                quest_time_start = datetime.fromisoformat(quest['claimDate'].replace('Z', ''))  # Ambil waktu mulai
                time_valid = quest.get('timeValidQuest', 0)  # durasi dalam detik

                # Validasi apakah waktu quest masih valid
                if (current_time - quest_time_start.timestamp()) > time_valid:
                    print(Fore.YELLOW + f"Waktu quest habis: {quest['questDescription']}. Melewati.")
                    continue
            else:
                print(Fore.YELLOW + f"Quest tidak memiliki claimDate, melewati validasi waktu: {quest['questDescription']}.")

        # Ambil actionCode, questValue, dan questType dari respons
        action_code = quest['actionCode']
        quest_value = quest['questValue']
        quest_type = quest.get('questType', 0)  # Ambil questType dari respons, default ke 0 jika tidak ada

        # Lakukan quest terlebih dahulu menggunakan do_telegram_quest
        do_quest_result = do_telegram_quest(authorization, action_code, quest_value)
        if do_quest_result['code'] != 0:
            print(Fore.RED + f"Gagal melakukan quest: {quest['questDescription']}.")
            continue
        print(Fore.GREEN + f"Quest berhasil diselesaikan: {quest['questDescription']}.")

        # Setelah quest selesai, klaim quest
        claim_result = claim_quest(authorization, action_code, quest_type, quest_value)  # Menggunakan questType dari data
        if claim_result['code'] == 0:
            print(Fore.GREEN + f"Berhasil klaim quest: {quest['questDescription']}.")
        else:
            print(Fore.RED + f"Gagal klaim quest: {quest['questDescription']}.")

def process_account(authorization, account_number, total_accounts):
    print(Fore.CYAN + f"\nMemproses akun {account_number}/{total_accounts}")
    
    # Login
    login_data = login(authorization)
    if login_data['code'] != 0:
        print(Fore.RED + "Gagal login. Melanjutkan ke akun berikutnya.")
        return

    user_id = login_data['data']['userID']
    user_name = login_data['data']['name']
    assign_location = login_data['data']['assignLocation']
    last_login_date = login_data['data']['lastLoginDate']
    
    print(Fore.GREEN + f"Berhasil login.")
    print(Fore.YELLOW + f"User ID: {user_id}")
    print(Fore.YELLOW + f"Nama: {user_name}")
    print(Fore.YELLOW + f"Lokasi: {assign_location}")
    print(Fore.YELLOW + f"Last Login: {last_login_date}")

    # Ambil profil pengguna
    profile_data = get_profile(authorization)
    if profile_data['code'] != 0:
        print(Fore.RED + "Gagal mendapatkan profil. Melanjutkan ke akun berikutnya.")
        return

    total_currency = profile_data['data']['totalSoftCurrency']
    print(Fore.YELLOW + f"Total Mata Uang: {total_currency}")

    # Proses semua quest
    process_quests(authorization)

    # Ambil dan klaim mata uang offline berdasarkan lokasi yang benar
    offline_currency = get_offline_currency(authorization, 0, assign_location)
    if offline_currency['code'] == 0:
        print(Fore.YELLOW + f"Mata uang offline: {offline_currency['data']}")
        claim_result = claim_offline_currency(authorization, 0, assign_location)
        print(Fore.GREEN + f"Status klaim mata uang offline: {'Berhasil' if claim_result['code'] == 0 else 'Gagal'}.")
    else:
        print(Fore.RED + "Gagal mendapatkan mata uang offline.")


def main():
    print_welcome_message()
    accounts = load_accounts()
    total_accounts = len(accounts)
    print(Fore.CYAN + f"Total akun: {total_accounts}")


    while True:
        for i, authorization in enumerate(accounts, 1):
            process_account(authorization, i, total_accounts)
            if i < total_accounts:
                print(Fore.YELLOW + "Menunggu 5 detik sebelum memproses akun berikutnya...")
                time.sleep(5)


        print(Fore.MAGENTA + "\nSemua akun telah diproses. Menunggu Sekitar 2 jam sebelum memulai ulang...")
        countdown_time = datetime.now() + timedelta(days=0.084)
        
        while datetime.now() < countdown_time:
            remaining_time = countdown_time - datetime.now()
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            print(f"\rWaktu tersisa: {hours:02d}:{minutes:02d}:{seconds:02d}", end="", flush=True)
            time.sleep(1)

        print("\nMemulai ulang proses...")

if __name__ == "__main__":
    main()
