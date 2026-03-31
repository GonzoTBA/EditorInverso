import tkinter as tk
from pathlib import Path
from tkinter import filedialog


class ReverseEditorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.geometry("800x600")

        self.current_file = None
        # Guarda las lineas ya cerradas con la mas reciente primero.
        self.committed_paragraphs = []

        self.container = tk.Frame(self.root, padx=12, pady=12)
        self.container.pack(fill="both", expand=True)

        self.toolbar = tk.Frame(self.container)
        self.toolbar.pack(fill="x", pady=(0, 8))

        self.open_button = tk.Button(
            self.toolbar,
            text="Abrir",
            command=self.open_file,
        )
        self.open_button.pack(side="left")

        self.save_button = tk.Button(
            self.toolbar,
            text="Guardar",
            command=self.save_file,
        )
        self.save_button.pack(side="left", padx=(8, 0))

        self.clear_button = tk.Button(
            self.toolbar,
            text="Limpiar",
            command=self.clear_all,
        )
        self.clear_button.pack(side="right")

        self.text = tk.Text(
            self.container,
            wrap="word",
            undo=False,
            font=("Helvetica", 14),
        )
        self.text.pack(fill="both", expand=True)
        self.text.bind("<Return>", self.on_return_pressed)

        self.update_title()
        self.reset_editor()

    def reset_editor(self) -> None:
        """Deja el cursor en la primera linea y mantiene el foco activo."""
        self.text.mark_set("insert", "1.0")
        self.text.see("1.0")
        self.text.focus_set()

    def update_title(self) -> None:
        """Actualiza el titulo con el nombre del archivo actual, si existe."""
        if self.current_file is None:
            self.root.title("Reverse Editor")
            return

        self.root.title(f"Reverse Editor - {Path(self.current_file).name}")

    def get_current_draft(self) -> str:
        """Devuelve la linea editable donde siempre vive el cursor."""
        return self.text.get("1.0", "2.0").rstrip("\n")

    def get_document_text(self) -> str:
        """Construye el texto completo visible para guardar en disco."""
        pieces = [self.get_current_draft()]
        pieces.extend(self.committed_paragraphs)

        while pieces and pieces[-1] == "":
            pieces.pop()

        return "\n".join(pieces)

    def load_document(self, content: str) -> None:
        """
        Carga el archivo tal y como se ve en pantalla:
        primera linea editable y resto como historial.
        """
        normalized = content.replace("\r\n", "\n").replace("\r", "\n")
        lines = normalized.split("\n")

        if lines and lines[-1] == "":
            lines.pop()

        draft = lines[0] if lines else ""
        self.committed_paragraphs = lines[1:] if len(lines) > 1 else []
        self.render_document(draft=draft)

    def render_document(self, draft: str = "") -> None:
        """
        Reconstruye el contenido completo del widget.

        La primera linea siempre es el borrador actual. Debajo se insertan las
        lineas ya cerradas con el orden invertido: lo mas nuevo arriba.
        """
        pieces = [draft.rstrip("\n")]
        pieces.extend(self.committed_paragraphs)
        document = "\n".join(pieces)

        self.text.delete("1.0", "end")
        if document:
            self.text.insert("1.0", document)

        self.reset_editor()

    def open_file(self) -> None:
        """Abre un archivo de texto y reconstruye el editor desde su contenido."""
        path = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            self.reset_editor()
            return

        content = Path(path).read_text(encoding="utf-8")
        self.current_file = path
        self.update_title()
        self.load_document(content)

    def save_file(self) -> None:
        """Guarda el contenido visible actual en un archivo de texto."""
        path = self.current_file
        if path is None:
            path = filedialog.asksaveasfilename(
                title="Guardar archivo",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            )
            if not path:
                self.reset_editor()
                return

        Path(path).write_text(self.get_document_text(), encoding="utf-8")
        self.current_file = path
        self.update_title()
        self.reset_editor()

    def on_return_pressed(self, event: tk.Event) -> str:
        """
        Cierra el parrafo que se estaba escribiendo arriba y lo mueve al bloque
        de contenido inferior. Devuelve 'break' para cancelar el Enter normal.
        """
        current_line = self.text.get("1.0", "2.0")
        paragraph = current_line.rstrip("\n")

        if paragraph.strip():
            # La nueva linea confirmada se coloca al principio del historial
            # para empujar hacia abajo las anteriores.
            self.committed_paragraphs.insert(0, paragraph)

        self.render_document(draft="")
        return "break"

    def clear_all(self) -> None:
        """Borra el borrador y todos los parrafos cerrados."""
        self.committed_paragraphs.clear()
        self.render_document(draft="")


def main() -> None:
    root = tk.Tk()
    ReverseEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
