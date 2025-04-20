import os
import re
import requests
from bs4 import BeautifulSoup
import json
import time

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
            video_id = src.split('/')[-1].split('?')[0]
            
            # İframe'in içinde bulunduğu bölümü bulmaya çalış
            parent_div = iframe.find_parent('div', class_='card-body')
            if parent_div:
                header_div = parent_div.find_previous_sibling('div', class_='card-header')
                title = header_div.text.strip() if header_div else "Bilinmeyen Bölüm"
            else:
                title = "Bilinmeyen Bölüm"
            
            youtube_links.append({
                'file': os.path.basename(file_path),
                'link': src,
                'video_id': video_id,
                'title': title
            })
    
    return youtube_links

def check_youtube_video(video_id):
    """YouTube video ID'sinin geçerli olup olmadığını kontrol eder"""
    url = f"https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={video_id}&format=json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True, "Video erişilebilir"
        else:
            return False, f"HTTP Hata: {response.status_code}"
    except Exception as e:
        return False, f"Hata: {str(e)}"

def main():
    # HTML dosyalarını bul
    html_files = [f for f in os.listdir() if f.endswith('.html')]
    
    all_links = []
    for file in html_files:
        links = extract_youtube_links(file)
        all_links.extend(links)
    
    print(f"Toplam {len(all_links)} YouTube linki bulundu.\n")
    
    # Benzersiz video ID'lerini al
    unique_videos = {}
    for link in all_links:
        if link['video_id'] not in unique_videos:
            unique_videos[link['video_id']] = []
        unique_videos[link['video_id']].append(link)
    
    print(f"Benzersiz video sayısı: {len(unique_videos)}\n")
    
    # Her bir videoyu kontrol et
    working_videos = []
    broken_videos = []
    
    for video_id, links in unique_videos.items():
        print(f"Kontrol ediliyor: {video_id}...", end="")
        is_valid, message = check_youtube_video(video_id)
        
        if is_valid:
            working_videos.extend(links)
            print(" Çalışıyor ✓")
        else:
            broken_videos.extend(links)
            print(f" ÇALIŞMIYOR ✗ - {message}")
        
        # YouTube API sınırlamalarını aşmamak için kısa bir bekleme
        time.sleep(0.5)
    
    # Sonuçları göster
    print(f"\nÇalışan videolar: {len(working_videos)}/{len(all_links)}")
    
    if broken_videos:
        print("\nÇALIŞMAYAN VİDEOLAR:")
        for link in broken_videos:
            print(f"Dosya: {link['file']}, Bölüm: {link['title']}, Video ID: {link['video_id']}, Link: {link['link']}")
    else:
        print("\nTüm videolar çalışıyor!")

if __name__ == "__main__":
    main()
