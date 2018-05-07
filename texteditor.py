import sys
import os
import time
try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    from Tkinter import *
    from ttk import *
    import ScrolledText as scrolledtext
    import tkMessageBox as messagebox
    from tkFileDialog import askopenfilename, asksaveasfilename
except ImportError:
    from tkinter import *
    from tkinter.ttk import *
    from tkinter import scrolledtext
    from tkinter import messagebox
    from tkinter.filedialog import askopenfilename, asksaveasfilename
import tktextext

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

class App:
    def __init__(self, openfile=None):
        self.running = True
        self.updateEvery = 60
        self.padding = 4
        self.font = "consolas"
        self.fontsize = 12
        self.thisdir = os.path.split(sys.argv[0])[0]
        self.savefile = os.path.join(self.thisdir, "files.dat")
        self.closeicon = resource_path(os.path.join("data", "close.gif"))
        self.newicon = resource_path(os.path.join("data", "new.gif"))
        self.openicon = resource_path(os.path.join("data", "open.gif"))
        self.saveicon = resource_path(os.path.join("data", "save.gif"))
        self.zoominicon = resource_path(os.path.join("data", "zoomin.gif"))
        self.zoomouticon = resource_path(os.path.join("data", "zoomout.gif"))
        self.files = []
        self.pathlabels = []
        self.textboxes = []

        self.root = Tk()
        self.root.title("TextEdit")
        self.root.iconbitmap(resource_path(os.path.join("data", "icon.ico")))
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.root.bind("<Control-n>", lambda e: self.newTab())
        self.root.bind("<Control-o>", lambda e: self.openFile())
        self.root.bind("<Control-s>", lambda e: self.saveFile())
        self.root.bind("<Control-w>", lambda e: self.deleteTab())
        self.root.bind("<Control-equal>", lambda e: self.zoomIn())
        self.root.bind("<Control-minus>", lambda e: self.zoomOut())

        self.mainframe = Frame(self.root)
        self.mainframe.pack(expand=True, fill=BOTH)

        newImage = PhotoImage(file=self.newicon)
        self.newButton = Button(self.mainframe, image=newImage)
        self.newButton.config(command=self.newTab)
        self.newButton.grid(row=0, column=0, padx=self.padding, pady=self.padding, sticky=W)
        self.newButton.image = newImage

        openImage = PhotoImage(file=self.openicon)
        self.openButton = Button(self.mainframe, image=openImage)
        self.openButton.config(command=self.openFile)
        self.openButton.grid(row=0, column=1, padx=self.padding, pady=self.padding, sticky=W)
        self.openButton.image = openImage

        saveImage = PhotoImage(file=self.saveicon)
        self.saveButton = Button(self.mainframe, image=saveImage)
        self.saveButton.config(command=self.saveFile)
        self.saveButton.grid(row=0, column=2, padx=self.padding, pady=self.padding, sticky=W)
        self.saveButton.image = saveImage

        zoominImage = PhotoImage(file=self.zoominicon)
        self.zoominButton = Button(self.mainframe, image=zoominImage)
        self.zoominButton.config(command=self.zoomIn)
        self.zoominButton.grid(row=0, column=3, padx=self.padding, pady=self.padding, sticky=W)
        self.zoominButton.image = zoominImage

        zoomoutImage = PhotoImage(file=self.zoomouticon)
        self.zoomoutButton = Button(self.mainframe, image=zoomoutImage)
        self.zoomoutButton.config(command=self.zoomOut)
        self.zoomoutButton.grid(row=0, column=4, padx=self.padding, pady=self.padding, sticky=W)
        self.zoomoutButton.image = zoomoutImage

        self.notebook = Notebook(self.mainframe)
        self.notebook.enable_traversal()
        self.notebook.grid(row=1, column=0, columnspan=5, padx=self.padding, pady=self.padding, sticky=NSEW)

        self.mainframe.rowconfigure(1, weight=1)
        self.mainframe.columnconfigure(4, weight=1)

        self.loadContent()
        if openfile is not None:
            self.newTab(openfile)
            if self.pathlabels[0]["text"] == "":
                self.notebook.select(0)
                self.deleteTab()
        self.updateZoom()

        self.root.after(int(1000 * (self.updateEvery - (time.time() % self.updateEvery))), self.save)
        self.root.mainloop()

    def save(self):
        if not self.running:
            return
        self.saveContent()
        self.root.after(int(1000 * (self.updateEvery - (time.time() % self.updateEvery))), self.save)

    def close(self):
        for i in range(len(self.textboxes)):
            if self.textboxes[i].edit_modified():
                self.notebook.select(i)
                if messagebox.askyesno("Save on close", "Do you want to save this file before closing?"):
                    self.saveFile()
                else:
                    self.textboxes[i].edit_modified(False)
        i = 0
        while i < len(self.pathlabels):
            if self.pathlabels[i]["text"] == "":
                self.notebook.select(i)
                self.deleteTab(createnew=False)
            else:
                i += 1
        self.saveContent()
        self.root.destroy()
        sys.exit()

    def saveContent(self):
        try:
            selected = self.notebook.index(self.notebook.select())
        except:
            selected = 0
        content = {
            "files": self.files,
            "selected": selected,
            "zoom": self.fontsize
        }
        with open(self.savefile, "wb") as f:
            pickle.dump(content, f)

    def loadContent(self):
        try:
            with open(self.savefile, "rb") as f:
                content = pickle.load(f)
            for path in content["files"]:
                if os.path.isfile(path):
                    self.newTab(path)
                else:
                    content["selected"] = 0
            if len(self.notebook.tabs()) == 0:
                self.newTab()
            self.notebook.select(content["selected"])
            self.fontsize = content["zoom"]
        except:
            self.newTab()
            self.notebook.select(0)

    def newTab(self, path=None):
        page = Frame(self.notebook)
        if path is None:
            pathlabel = Label(page, text="")
        else:
            pathlabel = Label(page, text=path)
        pathlabel.grid(row=0, column=0, padx=self.padding, pady=self.padding, sticky=W)

        closeImage = PhotoImage(file=self.closeicon)
        closeButton = Button(page, image=closeImage)
        closeButton.config(command=lambda p=page: self.deleteTab(p))
        closeButton.grid(row=0, column=1, sticky=NE)
        closeButton.image = closeImage

        textbox = scrolledtext.ScrolledText(page, wrap=NONE, undo=True, font=(self.font, self.fontsize))
        textbox.grid(row=1, column=0, columnspan=2, padx=self.padding, pady=self.padding, sticky=NSEW)
        textbox.bind("<Control-z>", lambda e: self.undo(textbox))
        textbox.bind("<Control-y>", lambda e: self.redo(textbox))

        page.rowconfigure(1, weight=1)
        page.columnconfigure(0, weight=1)
        
        if path is None:
            self.files.append(None)
            self.pathlabels.append(pathlabel)
            self.textboxes.append(textbox)
            self.notebook.add(page, text="Untitled")
        else:
            with open(path, "r") as f:
                text = f.read()
            textbox.insert(END, text)
            textbox.edit_reset()
            textbox.edit_modified(False)
            self.files.append(path)
            self.pathlabels.append(pathlabel)
            self.textboxes.append(textbox)
            self.notebook.add(page, text=os.path.split(path)[1])
        self.notebook.select(len(self.notebook.tabs()) - 1)

    def deleteTab(self, tab=None, createnew=True):
        if tab is None:
            tab = self.notebook.index(self.notebook.select())
        else:
            tab = self.notebook.index(tab)
        if self.textboxes[tab].edit_modified():
            if messagebox.askyesno("Save on close", "Do you want to save this file before closing?"):
                self.saveFile()
        del self.files[tab]
        del self.pathlabels[tab]
        del self.textboxes[tab]
        self.notebook.forget(tab)
        if len(self.notebook.tabs()) == 0 and createnew:
            self.newTab()

    def openFile(self):
        filename = askopenfilename()
        if filename != "":
            self.newTab(filename)

    def saveFile(self, tab=None):
        if tab is None:
            tab = self.notebook.index(self.notebook.select())
        else:
            tab = self.notebook.index(tab)
        if self.files[tab] is None:
            filename = self.promptSaveAs(tab)
        else:
            filename = self.files[tab]
        if filename != "":
            open(filename, "w").close()
            with open(filename, "w") as f:
                f.write(self.textboxes[tab].get(1.0, END)[:-1])
            self.files[tab] = filename
            self.notebook.tab(tab, text=os.path.split(filename)[1])
            self.pathlabels[tab].config(text=filename)
            self.textboxes[tab].edit_modified(False)

    def promptSaveAs(self, tab):
        return asksaveasfilename(filetypes=(("Text Documents", "*.txt"), ("All Files", "*.*")))

    def undo(self, textbox):
        try:
            textbox.edit_undo()
        except:
            pass

    def redo(self, textbox):
        try:
            textbox.edit_redo()
        except:
            pass

    def zoomIn(self):
        if 5 <= self.fontsize < 12:
            self.fontsize += 1
        elif 12 <= self.fontsize < 24:
            self.fontsize += 2
        elif 24 <= self.fontsize < 52:
            self.fontsize += 4
        elif 52 <= self.fontsize <= 92:
            self.fontsize += 8
        self.updateZoom()

    def zoomOut(self):
        if 6 <= self.fontsize <= 12:
            self.fontsize -= 1
        elif 12 < self.fontsize <= 24:
            self.fontsize -= 2
        elif 24 < self.fontsize <= 52:
            self.fontsize -= 4
        elif 52 < self.fontsize <= 100:
            self.fontsize -= 8
        self.updateZoom()

    def updateZoom(self):
        for textbox in self.textboxes:
            textbox.config(font=(self.font, self.fontsize))

if __name__ == "__main__":
    if len(sys.argv) >= 2 and os.path.isfile(sys.argv[1]):
        app = App(sys.argv[1])
    else:
        app = App()
