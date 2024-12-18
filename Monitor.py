import os
import shutil
import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def check_root_permissions():
    """Verifica se o script está sendo executado como root e tenta elevar as permissões usando 'su' caso necessário."""
    if os.name != "nt" and os.geteuid() != 0:
        print("Este script precisa ser executado com permissões de root. Tentando executar com 'su'...")
        try:
            # Tenta relançar o script com permissões elevadas
            subprocess.run(["su", "-c", " ".join([sys.executable] + sys.argv)], check=True)
        except Exception as e:
            print(f"Erro ao tentar elevar permissões: {e}")
            sys.exit(1)
        sys.exit(0)

def install_watchdog():
    """Instala o pacote watchdog automaticamente se necessário."""
    try:
        import watchdog  # Testa se o watchdog já está instalado
        print("Watchdog já está instalado.")
    except ImportError:
        print("Watchdog não encontrado. Instalando automaticamente...")
        subprocess.run([sys.executable, "-m", "pip", "install", "watchdog"], check=True)
        print("Watchdog instalado com sucesso.")

def delete_active_folder_if_exists(parent_folder):
    """Verifica se a pasta 'active' existe e a deleta, se necessário."""
    target_folder = os.path.join(parent_folder, "active")
    
    if os.path.exists(target_folder):
        print(f"Pasta 'active' encontrada. Deletando: {target_folder}")
        try:
            shutil.rmtree(target_folder)
            print("Pasta 'active' deletada com sucesso!")
        except OSError as e:
            print(f"Erro ao deletar a pasta: {e}")

class FolderDeletionHandler(FileSystemEventHandler):
    def __init__(self, parent_folder):
        self.parent_folder = parent_folder
        self.target_folder = os.path.join(self.parent_folder, "active")

    def on_created(self, event):
        """Previne a criação da pasta 'active'."""
        if event.src_path == self.target_folder:
            print(f"Tentativa de criar a pasta 'active' detectada: {event.src_path}. Ela será deletada.")
            try:
                shutil.rmtree(self.target_folder)
                print("Pasta 'active' deletada com sucesso!")
            except OSError as e:
                print(f"Erro ao deletar a pasta: {e}")

def monitor_folder(parent_folder):
    """Inicia o monitoramento da pasta principal para criação ou mudanças na pasta 'active'."""
    if not os.path.exists(parent_folder):
        print("A pasta principal não existe. Criando para monitoramento...")
        os.makedirs(parent_folder)

    # Deleta a pasta 'active' se já existir antes de começar o monitoramento
    delete_active_folder_if_exists(parent_folder)

    event_handler = FolderDeletionHandler(parent_folder)
    observer = Observer()
    observer.schedule(event_handler, parent_folder, recursive=False)  # Monitoramento não-recursivo
    observer.start()

    print(f"Monitorando a pasta principal: {parent_folder}")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Verifica permissões de root
    check_root_permissions()

    # Instala o Watchdog se necessário
    install_watchdog()

    # Define o caminho fixo para a pasta principal que contém a pasta 'active' a ser monitorada
    parent_folder = "/data/apex"
    print(f"Pasta principal configurada para monitoramento: {parent_folder}")
    monitor_folder(parent_folder)
