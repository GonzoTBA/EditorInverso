import tkinter as tk


class ReverseEditorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Reverse Editor")
        self.root.geometry("800x600")

        # Guarda las lineas ya cerradas con la mas reciente primero.
        self.committed_paragraphs = []

        self.container = tk.Frame(self.root, padx=12, pady=12)
        self.container.pack(fill="both", expand=True)

        self.clear_button = tk.Button(
            self.container,
            text="Limpiar",
            command=self.clear_all,
        )
        self.clear_button.pack(anchor="ne", pady=(0, 8))

        self.text = tk.Text(
            self.container,
            wrap="word",
            undo=False,
            font=("Helvetica", 14),
        )
        self.text.pack(fill="both", expand=True)
        self.text.bind("<Return>", self.on_return_pressed)

        self.reset_editor()

    def reset_editor(self) -> None:
        """Deja el cursor en la primera linea y mantiene el foco activo."""
        self.text.mark_set("insert", "1.0")
        self.text.see("1.0")
        self.text.focus_set()

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
