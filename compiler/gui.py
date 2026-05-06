from __future__ import annotations

import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from .errors import CompilerError
from .pipeline import (
    compile_source,
    format_instructions,
    format_object,
    format_outputs,
    format_token_stream,
)

# ── Catppuccin Mocha palette ──────────────────────────────────────────────────
_C = {
    "crust":     "#11111b",
    "mantle":    "#181825",
    "base":      "#1e1e2e",
    "surface0":  "#313244",
    "surface1":  "#45475a",
    "surface2":  "#585b70",
    "overlay0":  "#6c7086",
    "overlay1":  "#7f849c",
    "text":      "#cdd6f4",
    "subtext0":  "#a6adc8",
    "subtext1":  "#bac2de",
    "lavender":  "#b4befe",
    "blue":      "#89b4fa",
    "sapphire":  "#74c7ec",
    "teal":      "#94e2d5",
    "green":     "#a6e3a1",
    "yellow":    "#f9e2af",
    "peach":     "#fab387",
    "red":       "#f38ba8",
    "mauve":     "#cba6f7",
    "pink":      "#f5c2e7",
    "flamingo":  "#f2cdcd",
    "rosewater": "#f5e0dc",
}


class VintageCalcGUI:
    """VS-Code inspired Debug Studio for VintageCalc with multi-file support."""

    # ── construction ──────────────────────────────────────────────────────
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("VintageCalc Debug Studio")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 640)
        self.root.configure(bg=_C["crust"])

        self.sample_programs = self._build_sample_programs()
        self.sample_index = 0
        
        self.editors = {}  # tab_id -> dict with text, canvas, path, name, frame

        self._configure_style()
        self._build_layout()

    # ── ttk styling ───────────────────────────────────────────────────────
    def _configure_style(self) -> None:
        s = ttk.Style(self.root)
        s.theme_use("clam")

        s.configure(".", background=_C["base"], foreground=_C["text"])
        s.configure("TFrame", background=_C["base"])

        s.configure("EditorNotebook.TNotebook", background=_C["mantle"], borderwidth=0)
        s.configure(
            "EditorNotebook.TNotebook.Tab",
            background=_C["mantle"],
            foreground=_C["overlay1"],
            padding=(16, 7),
            font=("Segoe UI", 10),
        )
        s.map(
            "EditorNotebook.TNotebook.Tab",
            background=[("selected", _C["base"])],
            foreground=[("selected", _C["text"])],
        )

        s.configure("OutputNotebook.TNotebook", background=_C["mantle"], borderwidth=0)
        s.configure(
            "OutputNotebook.TNotebook.Tab",
            background=_C["mantle"],
            foreground=_C["overlay1"],
            padding=(16, 7),
            font=("Segoe UI", 10),
        )
        s.map(
            "OutputNotebook.TNotebook.Tab",
            background=[("selected", _C["base"])],
            foreground=[("selected", _C["text"])],
        )

        # Buttons
        s.configure(
            "Accent.TButton",
            background=_C["blue"],
            foreground=_C["crust"],
            font=("Segoe UI", 10, "bold"),
            padding=(14, 7),
            borderwidth=0,
        )
        s.map(
            "Accent.TButton",
            background=[("active", _C["sapphire"]), ("pressed", _C["lavender"])],
        )
        s.configure(
            "Ghost.TButton",
            background=_C["surface0"],
            foreground=_C["subtext1"],
            font=("Segoe UI", 10),
            padding=(12, 7),
            borderwidth=0,
        )
        s.map(
            "Ghost.TButton",
            background=[("active", _C["surface1"]), ("pressed", _C["surface2"])],
            foreground=[("active", _C["text"])],
        )

    # ── layout ────────────────────────────────────────────────────────────
    def _build_layout(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self._build_activity_bar()
        self._build_main_area()

    # ── activity bar ────────────────────────────────
    def _build_activity_bar(self) -> None:
        bar = tk.Frame(self.root, bg=_C["crust"], width=48)
        bar.grid(row=0, column=0, sticky="ns")
        bar.grid_propagate(False)

        logo = tk.Label(
            bar, text="VC", font=("Consolas", 14, "bold"),
            fg=_C["blue"], bg=_C["crust"], cursor="hand2",
        )
        logo.pack(pady=(14, 20))

        icons = [
            ("📝", "New File", self.new_file),
            ("📂", "Open Files", self.open_file),
            ("▶", "Run Debug", self.run_debug),
            ("🔄", "Load Sample", self.load_sample),
        ]
        for symbol, tip, cmd in icons:
            btn = tk.Label(
                bar, text=symbol, font=("Segoe UI Emoji", 16),
                fg=_C["overlay1"], bg=_C["crust"],
                cursor="hand2", width=3,
            )
            btn.pack(pady=4)
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            btn.bind("<Enter>", lambda e, b=btn: b.configure(fg=_C["text"]))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(fg=_C["overlay1"]))
            self._add_tooltip(btn, tip)

    # ── main area ─────────────────────────────────────────────────────────
    def _build_main_area(self) -> None:
        main = ttk.Frame(self.root)
        main.grid(row=0, column=1, sticky="nsew")
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)

        body = ttk.Frame(main)
        body.grid(row=0, column=0, sticky="nsew")
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1, uniform="half")
        body.columnconfigure(1, weight=1, uniform="half")

        self._build_editor_pane(body)
        self._build_output_pane(body)
        self._build_status_bar(main)

    # ── editor pane ───────────────────────────────────────────────────────
    def _build_editor_pane(self, parent: ttk.Frame) -> None:
        pane = ttk.Frame(parent)
        pane.grid(row=0, column=0, sticky="nsew")
        pane.rowconfigure(1, weight=1)
        pane.columnconfigure(0, weight=1)

        # ── toolbar ──────────────────────────
        toolbar = tk.Frame(pane, bg=_C["mantle"], height=46)
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.grid_propagate(False)

        btn_frame = tk.Frame(toolbar, bg=_C["mantle"])
        btn_frame.pack(side="right", padx=6, pady=4)

        for label, style, cmd in [
            ("▶  Run", "Accent.TButton", self.run_debug),
            ("📂  Open", "Ghost.TButton", self.open_file),
            ("❌  Close", "Ghost.TButton", self.close_current_tab),
        ]:
            ttk.Button(btn_frame, text=label, style=style, command=cmd).pack(
                side="left", padx=(0, 6)
            )

        # ── editor notebook ─────────
        self.editor_notebook = ttk.Notebook(pane, style="EditorNotebook.TNotebook")
        self.editor_notebook.grid(row=1, column=0, sticky="nsew")
        self.editor_notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        sep = tk.Frame(pane, bg=_C["surface0"], width=2)
        sep.grid(row=0, column=1, rowspan=2, sticky="ns", padx=0)

        # Create initial tab
        self._create_editor_tab("untitled.vc", self.sample_programs[self.sample_index], None)

    def _create_editor_tab(self, title: str, content: str, path: str | None) -> None:
        frame = tk.Frame(self.editor_notebook, bg=_C["base"])
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        line_canvas = tk.Canvas(
            frame, width=46, bg=_C["mantle"],
            bd=0, highlightthickness=0,
        )
        line_canvas.grid(row=0, column=0, sticky="ns")

        source_text = scrolledtext.ScrolledText(
            frame,
            wrap="none",
            font=("Cascadia Code", 12),
            background=_C["base"],
            foreground=_C["text"],
            insertbackground=_C["rosewater"],
            selectbackground=_C["surface1"],
            selectforeground=_C["text"],
            relief="flat",
            borderwidth=0,
            padx=8,
            pady=8,
            undo=True,
        )
        source_text.grid(row=0, column=1, sticky="nsew")
        source_text.insert("1.0", content)

        # Configure syntax tags
        source_text.tag_configure("keyword", foreground=_C["mauve"], font=("Cascadia Code", 12, "bold"))
        source_text.tag_configure("builtin", foreground=_C["blue"])
        source_text.tag_configure("number", foreground=_C["peach"])
        source_text.tag_configure("operator", foreground=_C["sapphire"])
        source_text.tag_configure("semicolon", foreground=_C["overlay0"])
        source_text.tag_configure("percent", foreground=_C["green"])
        source_text.tag_configure("comment", foreground=_C["overlay0"], font=("Cascadia Code", 12, "italic"))

        source_text.bind("<KeyRelease>", self._on_source_change)
        source_text.bind("<MouseWheel>", self._on_scroll)
        source_text.bind("<<Change>>", self._on_source_change)
        source_text.bind("<Configure>", self._on_source_change)

        self.editor_notebook.add(frame, text=f"  ● {title}  ")
        tab_id = self.editor_notebook.tabs()[-1]
        
        self.editors[tab_id] = {
            "text": source_text,
            "canvas": line_canvas,
            "path": path,
            "name": title,
            "frame": frame
        }
        
        self.editor_notebook.select(tab_id)
        self._apply_syntax_highlighting()
        self.root.after(50, self._update_line_numbers)

    def _get_active_editor(self) -> dict | None:
        try:
            selected = self.editor_notebook.select()
            return self.editors.get(selected)
        except tk.TclError:
            return None

    # ── output pane ───────────────────────────────────────────────────────
    def _build_output_pane(self, parent: ttk.Frame) -> None:
        pane = ttk.Frame(parent)
        pane.grid(row=0, column=1, sticky="nsew")
        pane.rowconfigure(0, weight=1)
        pane.columnconfigure(0, weight=1)

        self.output_notebook = ttk.Notebook(pane, style="OutputNotebook.TNotebook")
        self.output_notebook.grid(row=0, column=0, sticky="nsew")

        tab_info = [
            ("⟨T⟩  Tokens",       "sapphire"),
            ("🌲  AST",           "green"),
            ("⚙  IR",             "peach"),
            ("✦  Optimized IR",   "mauve"),
            ("►  Output",         "teal"),
            ("ℹ  Status",         "blue"),
        ]
        self.token_view = self._create_output_tab(tab_info[0][0])
        self.ast_view = self._create_output_tab(tab_info[1][0])
        self.ir_view = self._create_output_tab(tab_info[2][0])
        self.optimized_view = self._create_output_tab(tab_info[3][0])
        self.output_view = self._create_output_tab(tab_info[4][0])
        self.status_view = self._create_output_tab(tab_info[5][0])

    # ── status bar ────────────────────────────────────────────────────────
    def _build_status_bar(self, parent: ttk.Frame) -> None:
        bar = tk.Frame(parent, bg=_C["blue"], height=26)
        bar.grid(row=1, column=0, sticky="ew")
        bar.grid_propagate(False)

        self._status_left = tk.Label(
            bar, text="  ● Ready", font=("Segoe UI", 9),
            fg=_C["crust"], bg=_C["blue"], anchor="w",
        )
        self._status_left.pack(side="left", padx=6)

        self._status_right = tk.Label(
            bar, text="VintageCalc Debug Studio  ",
            font=("Segoe UI", 9), fg=_C["crust"], bg=_C["blue"], anchor="e",
        )
        self._status_right.pack(side="right", padx=6)

    # ── helpers ───────────────────────────────────────────────────────────
    def _create_output_tab(self, title: str) -> scrolledtext.ScrolledText:
        frame = ttk.Frame(self.output_notebook)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        view = scrolledtext.ScrolledText(
            frame,
            wrap="none",
            font=("Cascadia Code", 11),
            background=_C["base"],
            foreground=_C["text"],
            insertbackground=_C["text"],
            selectbackground=_C["surface1"],
            selectforeground=_C["text"],
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10,
        )
        view.grid(row=0, column=0, sticky="nsew")
        view.configure(state="disabled")
        self.output_notebook.add(frame, text=title)
        return view

    def _set_view(self, widget: scrolledtext.ScrolledText, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def _set_status(self, text: str, error: bool = False) -> None:
        color = _C["red"] if error else _C["blue"]
        icon = "✗" if error else "●"
        self._status_left.configure(text=f"  {icon} {text}", bg=color)
        self._status_right.configure(bg=color)
        bar = self._status_left.master
        bar.configure(bg=color)

    # ── event handlers ────────────────────────────────────────────────────
    def _on_tab_changed(self, event: tk.Event) -> None:
        editor = self._get_active_editor()
        if editor:
            self._set_status(f"Active file: {editor['name']}")
            self._on_source_change()

    def _update_line_numbers(self) -> None:
        editor = self._get_active_editor()
        if not editor:
            return
        canvas = editor["canvas"]
        source_text = editor["text"]
        
        canvas.delete("all")
        idx = source_text.index("@0,0")
        while True:
            dline = source_text.dlineinfo(idx)
            if dline is None:
                break
            y = dline[1]
            line_num = int(str(idx).split(".")[0])
            canvas.create_text(
                38, y + 2, anchor="ne", text=str(line_num),
                font=("Cascadia Code", 11), fill=_C["overlay0"],
            )
            idx = source_text.index(f"{idx}+1line")
            if source_text.compare(idx, ">=", "end"):
                break

    def _on_source_change(self, _event: tk.Event | None = None) -> None:
        self._update_line_numbers()
        self._apply_syntax_highlighting()
        editor = self._get_active_editor()
        if editor:
            pos = editor["text"].index("insert")
            parts = pos.split(".")
            self._status_right.configure(
                text=f"Ln {parts[0]}, Col {int(parts[1]) + 1}  ·  VintageCalc Debug Studio  "
            )

    def _on_scroll(self, _event: tk.Event | None = None) -> None:
        self.root.after(1, self._update_line_numbers)

    # ── syntax highlighting ───────────────────────────────────────────────
    def _apply_syntax_highlighting(self) -> None:
        editor = self._get_active_editor()
        if not editor:
            return
        source_text = editor["text"]
        src = source_text.get("1.0", "end")
        
        for tag in ("keyword", "builtin", "number", "operator", "semicolon", "percent", "comment"):
            source_text.tag_remove(tag, "1.0", "end")

        patterns = [
            ("keyword", r"\b(print|if|else|while|return|let|var|const)\b"),
            ("builtin", r"\b(sqrt)\b"),
            ("number",  r"\b\d+(\.\d+)?\b"),
            ("percent", r"\d+%"),
            ("operator", r"[+\-*/^=<>!&|]+"),
            ("semicolon", r";"),
        ]
        for tag, pattern in patterns:
            for m in re.finditer(pattern, src):
                start = f"1.0+{m.start()}c"
                end = f"1.0+{m.end()}c"
                source_text.tag_add(tag, start, end)

    # ── tooltip helper ────────────────────────────────────────────────────
    @staticmethod
    def _add_tooltip(widget: tk.Widget, text: str) -> None:
        tip_window: list[tk.Toplevel | None] = [None]

        def show(event: tk.Event) -> None:
            tw = tk.Toplevel(widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{event.x_root + 18}+{event.y_root + 4}")
            lbl = tk.Label(
                tw, text=f"  {text}  ", font=("Segoe UI", 9),
                bg=_C["surface0"], fg=_C["text"], relief="solid", borderwidth=1,
            )
            lbl.pack()
            tip_window[0] = tw

        def hide(_: tk.Event) -> None:
            if tip_window[0]:
                tip_window[0].destroy()
                tip_window[0] = None

        widget.bind("<Enter>", show, add="+")
        widget.bind("<Leave>", hide, add="+")

    # ── sample programs ───────────────────────────────────────────────────
    def _build_sample_programs(self) -> list[str]:
        return [
            (
                "a = 16;\n"
                "b = sqrt(a);\n"
                "rate = 10%;\n"
                "total = 200 * (1 + rate);\n"
                "result = (b + total / 10) ^ 2;\n"
                "print result;\n"
            ),
            (
                "x = 50 + 25;\n"
                "print x;\n"
            ),
            (
                "principal = 500;\n"
                "tax = 8%;\n"
                "final = principal + principal * tax;\n"
                "print final;\n"
            ),
            (
                "base = 9;\n"
                "root = sqrt(base);\n"
                "power = (root + 1) ^ 3;\n"
                "print power;\n"
            ),
            (
                "n = 12;\n"
                "discount = 15%;\n"
                "price = 300;\n"
                "reduced = price * (1 - discount);\n"
                "result = reduced / n;\n"
                "print result;\n"
            ),
            (
                "x = 7;\n"
                "y = 3;\n"
                "expr = ((x ^ 2) + (y ^ 2)) / 2;\n"
                "print expr;\n"
            ),
        ]

    # ── commands ──────────────────────────────────────────────────────────
    def new_file(self) -> None:
        self._create_editor_tab("untitled.vc", "", None)
        self._set_status("Created new file")

    def load_sample(self) -> None:
        self.sample_index = (self.sample_index + 1) % len(self.sample_programs)
        content = self.sample_programs[self.sample_index]
        name = f"sample_{self.sample_index + 1}.vc"
        self._create_editor_tab(name, content, None)
        self._set_status(f"Sample {self.sample_index + 1}/{len(self.sample_programs)} loaded")

    def open_file(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Open VintageCalc Source Files",
            filetypes=[("VintageCalc files", "*.vc"), ("All files", "*.*")],
        )
        if not paths:
            return
        for path in paths:
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    content = handle.read()
                name = os.path.basename(path)
                self._create_editor_tab(name, content, path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open {path}:\n{e}")
        if len(paths) > 0:
            self._set_status(f"Opened {len(paths)} file(s)")

    def close_current_tab(self) -> None:
        try:
            selected = self.editor_notebook.select()
            if not selected:
                return
            self.editor_notebook.forget(selected)
            if selected in self.editors:
                del self.editors[selected]
            if len(self.editor_notebook.tabs()) == 0:
                self.new_file()  # keep at least one tab open
            else:
                self._on_tab_changed(None)
        except tk.TclError:
            pass

    def run_debug(self) -> None:
        editor = self._get_active_editor()
        if not editor:
            messagebox.showinfo("VintageCalc", "No file opened.")
            return

        source = editor["text"].get("1.0", "end").strip()
        if not source:
            messagebox.showinfo("VintageCalc", "Enter source code first.")
            return

        try:
            result = compile_source(source + "\n")
            self._set_view(self.token_view, format_token_stream(result.tokens))
            self._set_view(self.ast_view, format_object(result.ast))
            self._set_view(self.ir_view, format_instructions(result.ir_program.instructions))
            self._set_view(self.optimized_view, format_instructions(result.optimized_ir_program.instructions))
            self._set_view(self.output_view, format_outputs(result.outputs))
            self._set_view(self.status_view, "Compilation successful. No errors reported.")
            self._set_status(f"Build succeeded for {editor['name']} ✓")
            self.output_notebook.select(4)
        except CompilerError as exc:
            self._set_view(self.status_view, str(exc))
            self._set_view(self.output_view, "<no output>")
            self._set_view(self.token_view, "<unavailable>")
            self._set_view(self.ast_view, "<unavailable>")
            self._set_view(self.ir_view, "<unavailable>")
            self._set_view(self.optimized_view, "<unavailable>")
            self._set_status(f"Error in {editor['name']}: {exc}", error=True)
            self.output_notebook.select(5)
            messagebox.showerror("VintageCalc error", str(exc))

    def run(self) -> None:
        self.root.mainloop()


def launch_gui() -> None:
    VintageCalcGUI().run()
