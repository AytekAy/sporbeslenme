import os
import re
from bs4 import BeautifulSoup

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
            youtube_links.append({
                'file': os.path.basename(file_path),
                'link': src,
                'video_id': video_id
            })
    
    return youtube_links

def main():
    # HTML dosyalarını bul
    html_files = [f for f in os.listdir() if f.endswith('.html')]
    
    all_links = []
    for file in html_files:
        links = extract_youtube_links(file)
        all_links.extend(links)
    
    # Sonuçları göster
    print(f"Toplam {len(all_links)} YouTube linki bulundu.\n")
    
    # Video ID'leri dosyaya ve ekrana yazdır
    with open('youtube_links.txt', 'w', encoding='utf-8') as f:
        for link in all_links:
            line = f"Dosya: {link['file']}, Video ID: {link['video_id']}, Link: {link['link']}"
            print(line)
            f.write(line + '\n')

if __name__ == "__main__":
    main()
