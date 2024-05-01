import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
from tkinter import simpledialog

class FileExplorer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Explorateur de Fichiers")
        self.geometry("800x600")
        self.current_dir = os.path.expanduser("~")
        self.previous_dirs = []

        # Couleurs personnalisées
        self.bg_color = "#f0f0f0"  # Couleur de fond gris clair
        self.accent_color = "#4287f5"  # Couleur d'accent bleu
        self.button_color = "#3367d6"  # Couleur de bouton bleu foncé
        self.button_fg_color = "#ffffff"  # Couleur de texte de bouton blanc

        self.create_widgets()
        self.populate_file_list()

    def create_widgets(self):
        # Style moderne
        style = ttk.Style()
        style.theme_use("clam")

        # Barre de chemin
        self.path_bar = ttk.Label(self, text=self.current_dir, font=("Arial", 12), style="Custom.TLabel")
        self.path_bar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        self.path_bar.bind("<Button-1>", self.browse_directory)

        # Zone d'affichage des fichiers
        self.file_list_frame = ttk.Frame(self)
        self.file_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configurer le style du frame
        style.configure("Custom.TFrame", background=self.bg_color)
        self.file_list_frame.configure(style="Custom.TFrame")

        self.file_list_scrollbar = ttk.Scrollbar(self.file_list_frame)
        self.file_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_list = tk.Listbox(self.file_list_frame, font=("Arial", 12), selectmode=tk.BROWSE, yscrollcommand=self.file_list_scrollbar.set, background=self.bg_color)
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_list_scrollbar.config(command=self.file_list.yview)

        self.file_list.bind("<Double-1>", self.open_directory)
        self.file_list.bind("<Button-3>", self.show_context_menu)

        # Boutons
        button_frame = ttk.Frame(self, style="Custom.TFrame")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Configurer les styles personnalisés
        style.configure("Custom.TLabel", background=self.bg_color)
        style.configure("TButton", background=self.button_color, foreground=self.button_fg_color, font=("Arial", 12))

        create_folder_button = ttk.Button(button_frame, text="Créer un dossier", command=self.create_folder, style="TButton")
        create_folder_button.pack(side=tk.LEFT, padx=5)

        refresh_button = ttk.Button(button_frame, text="Actualiser", command=self.populate_file_list, style="TButton")
        refresh_button.pack(side=tk.LEFT, padx=5)

        favorites_button = ttk.Button(button_frame, text="Favoris", command=self.show_favorites, style="TButton")
        favorites_button.pack(side=tk.LEFT, padx=5)

        filter_button = ttk.Button(button_frame, text="Filtrer", command=self.filter_files, style="TButton")
        filter_button.pack(side=tk.LEFT, padx=5)

        back_button = ttk.Button(button_frame, text="Retour", command=self.go_back, style="TButton")
        back_button.pack(side=tk.LEFT, padx=5)

    def populate_file_list(self):
        self.file_list.delete(0, tk.END)
        for item in os.listdir(self.current_dir):
            item_path = os.path.join(self.current_dir, item)
            is_dir = os.path.isdir(item_path)
            icon = "📁" if is_dir else "📄"
            self.file_list.insert(tk.END, f"{icon} {item}")

        self.path_bar.config(text=self.current_dir)

    def open_directory(self, event):
        selection = self.file_list.curselection()
        if selection:
            item = self.file_list.get(selection[0])
            item_path = os.path.join(self.current_dir, item[2:])
            if os.path.isdir(item_path):
                self.previous_dirs.append(self.current_dir)
                self.current_dir = item_path
                self.populate_file_list()

    def browse_directory(self, event):
        new_dir = filedialog.askdirectory(initialdir=self.current_dir)
        if new_dir:
            self.previous_dirs.append(self.current_dir)
            self.current_dir = new_dir
            self.populate_file_list()

    def create_folder(self):
        folder_name = simpledialog.askstring("Créer un nouveau dossier", "Entrez un nom pour le nouveau dossier", parent=self)
        if folder_name:
            try:
                new_folder_path = os.path.join(self.current_dir, folder_name)
                os.makedirs(new_folder_path)
                self.populate_file_list()
            except OSError as e:
                messagebox.showerror("Erreur", str(e))

    def show_context_menu(self, event):
        selection = self.file_list.curselection()
        if selection:
            item = self.file_list.get(selection[0])
            item_path = os.path.join(self.current_dir, item[2:])
            context_menu = tk.Menu(self, tearoff=0, background=self.bg_color, foreground="black")
            if os.path.isdir(item_path):
                context_menu.add_command(label="Ouvrir", command=lambda: self.open_directory(event))
            else:
                context_menu.add_command(label="Ouvrir", command=lambda: os.startfile(item_path))
            context_menu.add_command(label="Renommer", command=lambda: self.rename_item(item_path))
            context_menu.add_command(label="Supprimer", command=lambda: self.delete_item(item_path))
            context_menu.add_separator(background=self.accent_color)
            context_menu.add_command(label="Marquer comme favori", command=lambda: self.mark_as_favorite(item_path))
            context_menu.tk_popup(event.x_root, event.y_root)

    def rename_item(self, item_path):
        new_name = filedialog.asksaveasfilename(initialdir=self.current_dir, initialfile=os.path.basename(item_path))
        if new_name:
            try:
                os.rename(item_path, new_name)
                self.populate_file_list()
            except OSError as e:
                messagebox.showerror("Erreur", str(e))

    def delete_item(self, item_path):
        confirm = messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer '{os.path.basename(item_path)}' ?")
        if confirm:
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                self.populate_file_list()
            except OSError as e:
                messagebox.showerror("Erreur", str(e))

    def mark_as_favorite(self, item_path):
        favorites = self.load_favorites()
        if item_path not in favorites:
            favorites.append(item_path)
            self.save_favorites(favorites)
            messagebox.showinfo("Favori", f"'{os.path.basename(item_path)}' a été ajouté aux favoris.")
        else:
            messagebox.showwarning("Favori", f"'{os.path.basename(item_path)}' est déjà dans les favoris.")

    def show_favorites(self):
        favorites = self.load_favorites()
        if favorites:
            favorites_window = tk.Toplevel(self)
            favorites_window.title("Favoris")
            favorites_window.configure(background=self.bg_color)
            favorites_list = tk.Listbox(favorites_window, font=("Arial", 12), background=self.bg_color, foreground="black")
            favorites_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            for favorite in favorites:
                favorites_list.insert(tk.END, os.path.basename(favorite))
        else:
            messagebox.showwarning("Favoris", "Aucun favori n'a été défini.")

    def load_favorites(self):
        try:
            with open("favorites.txt", "r") as f:
                favorites = f.read().splitlines()
        except FileNotFoundError:
            favorites = []
        return favorites

    def save_favorites(self, favorites):
        with open("favorites.txt", "w") as f:
            f.write("\n".join(favorites))

    def filter_files(self):
        file_types = filedialog.askopenfilenames(initialdir=self.current_dir)
        if file_types:
            self.file_list.delete(0, tk.END)
            for item in os.listdir(self.current_dir):
                item_path = os.path.join(self.current_dir, item)
                if os.path.isfile(item_path) and any(item_path.endswith(ext) for ext in file_types):
                    self.file_list.insert(tk.END, f"📄 {item}")

    def go_back(self):
        if self.previous_dirs:
            previous_dir = self.previous_dirs.pop()
            self.current_dir = previous_dir
            self.populate_file_list()

if __name__ == "__main__":
    app = FileExplorer()
    app.mainloop()
