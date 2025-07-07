import speech_recognition as sr
import datetime
import time
import os
import threading
import queue
import tkinter as tk
from tkinter import messagebox, ttk
import pystray
from PIL import Image, ImageDraw

# Nome do arquivo será gerado dinamicamente no formato transcription-yyyy-mm-dd.txt
def get_output_filename():
    return f"transcription-{datetime.datetime.now().strftime('%Y-%m-%d')}.txt"

class TranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controlador de Transcrição")
        self.root.geometry("500x350")
        self.root.resizable(True, True)
        
        # Variáveis de controle
        self.is_running = False
        self.transcription_thread = None
        self.processing_thread = None
        self.audio_queue = queue.Queue()
        
        # Configurações de reconhecimento
        self.energy_threshold = 200
        self.pause_threshold = 0.5
        self.dynamic_energy_adjustment = True
        
        # Configuração da bandeja do sistema
        self.icon = None
        self.setup_system_tray()
        
        # Criação da interface
        self.setup_ui()
        
        # Oculta a janela ao iniciar
        self.root.withdraw()
        
        # Verifica o status periodicamente
        self.check_status()
        
        # Intercepta o evento de fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Inicia a transcrição automaticamente
        self.start_transcription()
        
    def on_closing(self):
        """Oculta a janela quando o usuário clica no botão 'X'."""
        self.hide_window()
    
    def create_circle_icon(self, color):
        """Cria um ícone circular com a cor especificada."""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))  # Fundo transparente
        draw = ImageDraw.Draw(image)
        draw.ellipse((0, 0, size-1, size-1), fill=color)
        return image
    
    def setup_system_tray(self):
        """Configura o ícone na bandeja do sistema."""
        # Ícone inicial (vermelho, transcrição parada)
        initial_icon = self.create_circle_icon('green')
        menu = (
            pystray.MenuItem("Mostrar Interface", self.show_window),
            pystray.MenuItem("Iniciar Transcrição", self.start_transcription),
            pystray.MenuItem("Parar Transcrição", self.stop_transcription),
            pystray.MenuItem("Sair", self.quit_application)
        )
        self.icon = pystray.Icon("transcription_app", initial_icon, "Transcrição de Áudio", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()
    
    def update_tray_icon(self, is_running):
        """Atualiza o ícone da bandeja com base no estado da transcrição."""
        if self.icon:
            color = 'green' if is_running else 'red'
            self.icon.icon = self.create_circle_icon(color)
    
    def show_window(self):
        """Mostra a janela principal."""
        self.root.deiconify()
    
    def hide_window(self):
        """Oculta a janela principal."""
        self.root.withdraw()
    
    def quit_application(self):
        """Encerra a aplicação."""
        self.stop_transcription()
        if self.icon:
            self.icon.stop()
        self.root.quit()
        self.root.destroy()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Sistema de Transcrição de Áudio", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=5)
        
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(status_frame, text="Status:", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(status_frame, text="Parado", font=("Helvetica", 12))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.status_indicator = ttk.Label(status_frame, text="●", font=("Helvetica", 16))
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        self.update_status_indicator(False)
        
        config_frame = ttk.LabelFrame(main_frame, text="Configurações")
        config_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(config_frame, text="Sensibilidade:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.energy_scale = ttk.Scale(config_frame, from_=100, to=1000, length=200, 
                                      orient=tk.HORIZONTAL, value=self.energy_threshold,
                                      command=self.update_energy)
        self.energy_scale.grid(row=0, column=1, padx=5, pady=2)
        self.energy_value = ttk.Label(config_frame, text=str(self.energy_threshold))
        self.energy_value.grid(row=0, column=2, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Tempo de pausa:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.pause_scale = ttk.Scale(config_frame, from_=0.3, to=2.0, length=200, 
                                     orient=tk.HORIZONTAL, value=self.pause_threshold,
                                     command=self.update_pause)
        self.pause_scale.grid(row=1, column=1, padx=5, pady=2)
        self.pause_value = ttk.Label(config_frame, text=str(self.pause_threshold))
        self.pause_value.grid(row=1, column=2, padx=5, pady=2)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Iniciar Transcrição", command=self.start_transcription, width=20)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = ttk.Button(button_frame, text="Parar Transcrição", command=self.stop_transcription, width=20, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(button_frame, text="Ocultar", command=self.hide_window, width=20).pack(side=tk.LEFT, padx=10)
        
        log_frame = ttk.LabelFrame(main_frame, text="Log de Atividades")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        log_scroll_frame = ttk.Frame(log_frame)
        log_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(log_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_scroll_frame, height=8, width=50, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        self.status_bar = ttk.Label(self.root, text="Pronto", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_energy(self, value):
        self.energy_threshold = int(float(value))
        self.energy_value.config(text=str(self.energy_threshold))
    
    def update_pause(self, value):
        self.pause_threshold = float(value)
        self.pause_value.config(text=f"{self.pause_threshold:.1f}")
    
    def update_status_indicator(self, is_running):
        if is_running:
            self.status_indicator.config(text="●", foreground="green")
            self.status_label.config(text="Em execução")
        else:
            self.status_indicator.config(text="●", foreground="red")
            self.status_label.config(text="Parado")
    
    def add_log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.status_bar.config(text=message)
    
    def start_transcription(self):
        if not self.is_running:
            # Verifica e cria o arquivo do dia se não existir
            output_file = get_output_filename()
            if not os.path.exists(output_file):
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("Transcrições:\n")
            
            self.is_running = True
            self.update_status_indicator(True)
            self.update_tray_icon(True)  # Atualiza para ícone verde
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break
            
            self.transcription_thread = threading.Thread(target=self.listen_audio)
            self.transcription_thread.daemon = True
            self.transcription_thread.start()
            
            self.processing_thread = threading.Thread(target=self.process_audio_queue)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            self.add_log("Transcrição iniciada")
    
    def stop_transcription(self):
        if self.is_running:
            self.is_running = False
            self.update_status_indicator(False)
            self.update_tray_icon(False)  # Atualiza para ícone vermelho
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.add_log("Transcrição interrompida")
    
    def check_status(self):
        thread_alive = (self.transcription_thread and self.transcription_thread.is_alive())
        process_alive = (self.processing_thread and self.processing_thread.is_alive())
        
        if not thread_alive and self.is_running:
            self.is_running = False
            self.update_status_indicator(False)
            self.update_tray_icon(False)  # Atualiza para ícone vermelho
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.add_log("A thread de áudio parou inesperadamente")
        
        if not process_alive and self.is_running:
            self.is_running = False
            self.update_status_indicator(False)
            self.update_tray_icon(False)  # Atualiza para ícone vermelho
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.add_log("A thread de processamento parou inesperadamente")
        
        self.root.after(1000, self.check_status)
    
    def write_to_file(self, text):
        output_file = get_output_filename()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {text}\n")
        
        display_text = text if len(text) <= 50 else f"{text[:47]}..."
        self.root.after(0, lambda: self.add_log(f"Transcrito: {display_text}"))
    
    def listen_audio(self):
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = self.energy_threshold
        recognizer.pause_threshold = self.pause_threshold
        recognizer.dynamic_energy_threshold = self.dynamic_energy_adjustment
        
        try:
            with sr.Microphone() as source:
                self.root.after(0, lambda: self.add_log("Ajustando ao ruído ambiente..."))
                recognizer.adjust_for_ambient_noise(source, duration=1)
                self.root.after(0, lambda: self.add_log("Escutando..."))

                while self.is_running:
                    try:
                        audio = recognizer.listen(source, timeout=0.8, phrase_time_limit=30)
                        self.audio_queue.put(audio)
                        time.sleep(0.05)
                    except sr.WaitTimeoutError:
                        pass
                    except Exception as e:
                        self.root.after(0, lambda: self.add_log(f"Erro na captura: {e}"))
                        time.sleep(0.5)
        except Exception as e:
            self.root.after(0, lambda: self.add_log(f"Erro ao iniciar microfone: {e}"))
            self.root.after(0, self.stop_transcription)
    
    def process_audio_queue(self):
        recognizer = sr.Recognizer()
        
        while self.is_running:
            try:
                try:
                    audio = self.audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                self.root.after(0, lambda: self.status_bar.config(text="Processando áudio..."))
                
                text = recognizer.recognize_google(audio, language="pt-BR")
                
                if text:
                    self.write_to_file(text)
                
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                self.root.after(0, lambda: self.add_log(f"Erro API Google: {e}"))
                time.sleep(2)
            except Exception as e:
                self.root.after(0, lambda: self.add_log(f"Erro: {e}"))
                time.sleep(0.5)
                
            if not self.audio_queue.empty():
                self.audio_queue.task_done()

if __name__ == "__main__":
    root = tk.Tk()
    app = TranscriptionApp(root)
    try:
        import psutil
        p = psutil.Process(os.getpid())
        p.nice(psutil.HIGH_PRIORITY_CLASS)
    except:
        pass
    root.mainloop()