# -*- coding: utf-8 -*-
"""
🔥 FLAME AI OS — Master Orchestration & System Launcher
======================================================
Kusursuz, kilitlenmeyen ve kendi kendini doğrulayan ana başlatıcı:
- Donanım (RTX 3090 24GB VRAM) ve CUDA 12.1 doğrulama
- Ollama yerel model servis kontrolü ve otomatik uyandırma
- Akıllı dinamik port denetleyicisi (8000 meşgulse 8001'e otomatik geçiş)
- FastAPI Kernel API sunucusu ve 3D Dashboard entegrasyonu
- Modlar: --all, --api, --hud, --desktop
"""

import os
import sys

# Windows CP1254 / UnicodeEncodeError 0x81 ve emoji koruması
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import time
import socket
import argparse
import subprocess
import threading
import urllib.request

# Kök dizin ayarı
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
for sub in ["brain", "voice", "memory", "tools", "system"]:
    p = os.path.join(ROOT_DIR, sub)
    if p not in sys.path:
        sys.path.append(p)


def print_banner():
    banner = """
======================================================================
  [FLAME AI OS] - KISISEL YAPAY ZEKA ISLETIM SISTEMI (v1.2)
  [NVIDIA GeForce RTX 3090 24GB VRAM | Python 3.11 | Memory OS]
======================================================================
"""
    print(banner)


def check_hardware():
    """RTX 3090 ve CUDA durumunu kontrol eder."""
    print("[1/4] Donanım ve CUDA doğrulanıyor...")
    try:
        import torch
        if torch.cuda.is_available():
            dev_name = torch.cuda.get_device_name(0)
            vram_gb = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 1)
            print(f"  [✓] GPU Algılandı: {dev_name} | VRAM: {vram_gb} GB")
            return True
        else:
            print("  [!] CUDA algılanamadı, CPU modunda devam edilecek.")
            return False
    except Exception as e:
        print(f"  [!] PyTorch/CUDA uyarısı: {e}")
        return False


def check_and_start_ollama():
    """Ollama servisini kontrol eder, kapalıysa arka planda başlatır."""
    print("[2/4] Ollama yerel model servisi kontrol ediliyor...")
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
        with urllib.request.urlopen(req, timeout=1.5):
            print("  [✓] Ollama servisi zaten aktif (http://127.0.0.1:11434).")
            return True
    except Exception:
        pass

    # Ollama başlatmayı dene
    ollama_exe = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe")
    if os.path.exists(ollama_exe):
        try:
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            subprocess.Popen([ollama_exe, "serve"], creationflags=flags)
            print("  [✓] Ollama servisi arka planda başlatıldı.")
            time.sleep(1.0)
            return True
        except Exception as e:
            print(f"  [!] Ollama başlatılamadı: {e}")
    else:
        print("  [i] Ollama kurulu değil veya bulunamadı (Yerel/Bulut hibrit mod devrede).")
    return False


def find_free_port(start_port: int = 8000, max_port: int = 8020) -> int:
    """Müsait ilk TCP portunu tespit eder."""
    for port in range(start_port, max_port + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", port))
            s.close()
            return port
        except Exception:
            s.close()
            continue
    return start_port


def open_browser_after_delay(url: str, delay_sec: float = 1.2):
    """Belirli bir gecikmeyle varsayılan tarayıcıda dashboard'u açar."""
    def _open():
        time.sleep(delay_sec)
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as e:
            print(f"  [!] Tarayıcı açılamadı: {e}")
    threading.Thread(target=_open, daemon=True).start()


def run_api_server(port: int, open_browser: bool = True):
    """FastAPI sunucusunu belirtilen portta başlatır."""
    import uvicorn
    url = f"http://127.0.0.1:{port}/"
    print(f"[3/4] FLAME Kernel API ve Dashboard hazırlandı.")
    print(f"  [✓] Dashboard URL: {url}")
    print(f"  [✓] API Dokümantasyonu: http://127.0.0.1:{port}/docs")
    print(f"[4/4] Sistem aktif! Kapatmak için CTRL+C tuşlayın.\n")

    if open_browser:
        open_browser_after_delay(url)

    uvicorn.run("core.api_server:app", host="127.0.0.1", port=port, log_level="info")


def run_hud_mode():
    """Native PyWebView HUD penceresini başlatır."""
    hud_runner = os.path.join(ROOT_DIR, "ui", "run_hud.py")
    if os.path.exists(hud_runner):
        print("[HUD] 3D Siber Komuta Merkezi başlatılıyor...")
        subprocess.run([sys.executable, hud_runner])
    else:
        print("[HATA] ui/run_hud.py bulunamadı.")


def run_desktop_orb_mode():
    """Tkinter masaüstü asistanını (Orb + Sohbet) başlatır."""
    main_py = os.path.join(ROOT_DIR, "main.py")
    if os.path.exists(main_py):
        print("[Desktop] FLAME Masaüstü Asistanı başlatılıyor...")
        subprocess.run([sys.executable, main_py])
    else:
        print("[HATA] main.py bulunamadı.")


def main():
    parser = argparse.ArgumentParser(description="[FLAME AI OS] Baslatici")
    parser.add_argument("--mode", choices=["all", "api", "hud", "desktop"], default="all",
                        help="Çalıştırma modu (all, api, hud, desktop)")
    parser.add_argument("--port", type=int, default=None,
                        help="Özel API portu (belirtilmezse otomatik seçilir)")
    parser.add_argument("--no-browser", action="store_true",
                        help="Tarayıcıyı otomatik açma")

    args = parser.parse_args()

    print_banner()
    check_hardware()
    check_and_start_ollama()

    if args.mode == "hud":
        run_hud_mode()
    elif args.mode == "desktop":
        run_desktop_orb_mode()
    else:
        # API veya ALL modu
        selected_port = args.port if args.port else find_free_port(8000, 8020)
        if selected_port != 8000 and not args.port:
            print(f"  [i] 8000 portu meşgul, boş olan {selected_port} portu seçildi.")

        open_browser = not args.no_browser and (args.mode == "all")
        run_api_server(selected_port, open_browser=open_browser)


if __name__ == "__main__":
    main()
