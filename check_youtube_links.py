import os
import re
import requests
from bs4 import BeautifulSoup
import concurrent.futures

def extract_youtube_links(file_path):
    """HTML dosyasından YouTube embed linklerini çıkarır"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    iframes = soup.find_all('iframe')
    
    youtube_links = []
    for iframe in iframes:
        src = iframe.get('src', '')
        if 'youtube.com/embed/' in src:
            youtube_links.append({
                'file': os.path.basename(file_path),
                'link': src,
                'video_id': src.split('/')[-1].split('?')[0]
            })
    
    return youtube_links

def check_youtube_link(link_info):
    """YouTube linkinin erişilebilir olup olmadığını kontrol eder"""
    try:
        response = requests.head(link_info['link'], timeout=5)
        if response.status_code == 200:
            status = "Çalışıyor"
        else:
            status = f"Hata: HTTP {response.status_code}"
    except Exception as e:
        status = f"Hata: {str(e)}"
    
    link_info['status'] = status
    return link_info

def main():
    # HTML dosyalarını bul
    html_files = [f for f in os.listdir() if f.endswith('.html')]
    
    all_links = []
    for file in html_files:
        links = extract_youtube_links(file)
        all_links.extend(links)
    
    print(f"Toplam {len(all_links)} YouTube linki bulundu.")
    
    # Linkleri paralel olarak kontrol et
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(check_youtube_link, all_links))
    
    # Sonuçları göster
    working_links = [r for r in results if r['status'] == "Çalışıyor"]
    broken_links = [r for r in results if r['status'] != "Çalışıyor"]
    
    print(f"\nÇalışan linkler: {len(working_links)}/{len(all_links)}")
    
    if broken_links:
        print("\nÇalışmayan linkler:")
        for link in broken_links:
            print(f"Dosya: {link['file']}, Link: {link['link']}, Durum: {link['status']}")
    else:
        print("\nTüm linkler çalışıyor!")

if __name__ == "__main__":
    main()
