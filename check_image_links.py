import os
import re
import requests
from bs4 import BeautifulSoup
import time

def extract_image_links(file_path):
    """HTML dosyasından resim linklerini çıkarır"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    images = soup.find_all('img')
    
    image_links = []
    for img in images:
        src = img.get('src', '')
        if src and not src.startswith('data:'):
            image_links.append({
                'file': os.path.basename(file_path),
                'link': src,
                'alt': img.get('alt', 'Açıklama yok')
            })
    
    return image_links

def check_image_link(link_info):
    """Resim linkinin erişilebilir olup olmadığını kontrol eder"""
    try:
        # Eğer link göreli bir yol ise, kontrol etmeye gerek yok
        if not link_info['link'].startswith(('http://', 'https://')):
            return True, "Yerel dosya"
        
        response = requests.head(link_info['link'], timeout=5)
        if response.status_code == 200:
            return True, "Erişilebilir"
        else:
            return False, f"HTTP Hata: {response.status_code}"
    except Exception as e:
        return False, f"Hata: {str(e)}"

def main():
    # HTML dosyalarını bul
    html_files = [f for f in os.listdir() if f.endswith('.html')]
    
    all_links = []
    for file in html_files:
        links = extract_image_links(file)
        all_links.extend(links)
    
    print(f"Toplam {len(all_links)} resim linki bulundu.\n")
    
    # Her bir resmi kontrol et
    working_links = []
    broken_links = []
    
    for link in all_links:
        print(f"Kontrol ediliyor: {link['link']}...", end="")
        is_valid, message = check_image_link(link)
        
        if is_valid:
            working_links.append(link)
            print(f" {message} ✓")
        else:
            broken_links.append(link)
            print(f" ÇALIŞMIYOR ✗ - {message}")
        
        # API sınırlamalarını aşmamak için kısa bir bekleme
        time.sleep(0.2)
    
    # Sonuçları göster
    print(f"\nÇalışan resimler: {len(working_links)}/{len(all_links)}")
    
    if broken_links:
        print("\nÇALIŞMAYAN RESİMLER:")
        for link in broken_links:
            print(f"Dosya: {link['file']}, Alt: {link['alt']}, Link: {link['link']}")
    else:
        print("\nTüm resimler çalışıyor!")

if __name__ == "__main__":
    main()
