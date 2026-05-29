import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

class DispensaApp(App):
    def build(self):
        # STRUTTURA PER ANDROID: Definisce il percorso corretto e sicuro per salvare i dati
        cartella_dati = self.user_data_dir
        self.file_dati = os.path.join(cartella_dati, "dispensa_smart.json")
        
        self.dispensa = self.carica_dati()

        self.root = BoxLayout(orientation='vertical', padding=25, spacing=15)

        # --- AREA RICERCA ---
        search_area = BoxLayout(orientation='horizontal', size_hint_y=None, height=120, spacing=12)
        self.search_input = TextInput(
            hint_text="Cerca...", 
            multiline=False, font_size='35sp', size_hint_x=0.65, padding_y=(25, 0)
        )
        btn_cerca = Button(text="CERCA", size_hint_x=0.35, background_color=(0.9, 0.7, 0.1, 1), font_size='22sp', bold=True)
        btn_cerca.bind(on_press=self.ricerca_parziale)
        search_area.add_widget(self.search_input)
        search_area.add_widget(btn_cerca)
        self.root.add_widget(search_area)

        # --- AREA INPUT NUOVO ---
        input_area = BoxLayout(orientation='vertical', size_hint_y=None, height=350, spacing=10)
        self.nome_input = TextInput(hint_text="Nome Prodotto", multiline=False, font_size='30sp', size_hint_y=None, height=100, padding_y=(25, 0))
        self.qty_input = TextInput(hint_text="Quantità", multiline=False, input_filter='int', font_size='30sp', size_hint_y=None, height=100, padding_y=(25, 0))
        btn_aggiungi = Button(text="AGGIUNGI A LISTA", size_hint_y=None, height=110, background_color=(0.1, 0.5, 0.8, 1), font_size='22sp', bold=True)
        btn_aggiungi.bind(on_press=self.nuovo_prodotto)
        input_area.add_widget(self.nome_input); input_area.add_widget(self.qty_input); input_area.add_widget(btn_aggiungi)
        self.root.add_widget(input_area)

        # --- LISTA COMPLETA ---
        self.scroll = ScrollView()
        self.lista_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.lista_layout.bind(minimum_height=self.lista_layout.setter('height'))
        self.aggiorna_lista_grafica()
        self.scroll.add_widget(self.lista_layout)
        self.root.add_widget(self.scroll)

        return self.root

    def ricerca_parziale(self, instance):
        query = self.search_input.text.strip().lower()
        if not query: return
        risultati = {k: v for k, v in self.dispensa.items() if query in k.lower()}
        
        layout_popup = BoxLayout(orientation='vertical', padding=15, spacing=15)
        if risultati:
            scroll_popup = ScrollView()
            grid_risultati = GridLayout(cols=1, spacing=15, size_hint_y=None)
            grid_risultati.bind(minimum_height=grid_risultati.setter('height'))

            for nome, qty in risultati.items():
                riga_pop = BoxLayout(size_hint_y=None, height=100, spacing=10)
                # Testo a sinistra
                lbl_pop = Label(text=f"[b]{nome}[/b]: {qty}", markup=True, font_size='22sp', halign='left', valign='middle')
                lbl_pop.bind(size=lbl_pop.setter('text_size'))
                
                # Tasti a destra
                btn_meno_p = Button(text="-", size_hint_x=None, width=80, font_size='30sp', background_color=(0.8, 0.5, 0.2, 1))
                btn_meno_p.bind(on_release=lambda btn, n=nome: self.azione_rapida_popup(n, -1))
                btn_piu_p = Button(text="+", size_hint_x=None, width=80, font_size='30sp', background_color=(0.2, 0.7, 0.3, 1))
                btn_piu_p.bind(on_release=lambda btn, n=nome: self.azione_rapida_popup(n, 1))
                
                riga_pop.add_widget(lbl_pop); riga_pop.add_widget(btn_meno_p); riga_pop.add_widget(btn_piu_p)
                grid_risultati.add_widget(riga_pop)
            scroll_popup.add_widget(grid_risultati)
            layout_popup.add_widget(scroll_popup)
        else:
            layout_popup.add_widget(Label(text="Nessun match", font_size='22sp'))

        btn_chiudi = Button(text="CHIUDI", size_hint_y=None, height=90, background_color=(0.4, 0.4, 0.4, 1))
        layout_popup.add_widget(btn_chiudi)
        self.current_popup = Popup(title=f"Cerca: {query}", content=layout_popup, size_hint=(0.95, 0.7))
        btn_chiudi.bind(on_press=self.current_popup.dismiss)
        self.current_popup.open()

    def azione_rapida_popup(self, nome, variazione):
        self.modifica_quantita(nome, variazione)
        self.current_popup.dismiss()
        self.ricerca_parziale(None)

    def carica_dati(self):
        try:
            if os.path.exists(self.file_dati):
                with open(self.file_dati, "r") as f: 
                    return json.load(f)
            return {}
        except: 
            return {}

    def salva_dati(self):
        try:
            with open(self.file_dati, "w") as f: 
                json.dump(self.dispensa, f, indent=4)
        except Exception as e:
            print(f"Errore nel salvataggio dati: {e}")

    def nuovo_prodotto(self, instance):
        nome = self.nome_input.text.strip().capitalize()
        qty = self.qty_input.text.strip()
        if nome and qty:
            self.dispensa[nome] = self.dispensa.get(nome, 0) + int(qty)
            self.salva_dati(); self.nome_input.text = ""; self.qty_input.text = ""; self.aggiorna_lista_grafica()

    def modifica_quantita(self, nome, variazione):
        self.dispensa[nome] += variazione
        if self.dispensa[nome] < 0: self.dispensa[nome] = 0
        self.salva_dati(); self.aggiorna_lista_grafica()

    def elimina_prodotto(self, nome):
        if nome in self.dispensa:
            del self.dispensa[nome]
            self.salva_dati(); self.aggiorna_lista_grafica()

    def aggiorna_lista_grafica(self):
        self.lista_layout.clear_widgets()
        for nome, qty in sorted(self.dispensa.items()):
            # Riga Prodotto
            riga = BoxLayout(size_hint_y=None, height=100, spacing=10, padding=(5, 5))
            
            # Etichetta allineata a sinistra
            lbl = Label(text=f"[b]{nome}[/b]: {qty}", markup=True, font_size='26sp', halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            
            # Gruppo tasti a destra
            btn_meno = Button(text="-", size_hint_x=None, width=90, font_size='30sp', background_color=(0.8, 0.5, 0.2, 1))
            btn_meno.bind(on_release=lambda btn, n=nome: self.modifica_quantita(n, -1))
            
            btn_piu = Button(text="+", size_hint_x=None, width=90, font_size='30sp', background_color=(0.2, 0.7, 0.3, 1))
            btn_piu.bind(on_release=lambda btn, n=nome: self.modifica_quantita(n, 1))
            
            btn_del = Button(text="X", size_hint_x=None, width=70, font_size='18sp', background_color=(0.8, 0.1, 0.1, 1))
            btn_del.bind(on_release=lambda btn, n=nome: self.elimina_prodotto(n))
            
            riga.add_widget(lbl)
            riga.add_widget(btn_meno)
            riga.add_widget(btn_piu)
            riga.add_widget(btn_del)
            self.lista_layout.add_widget(riga)

if __name__ == "__main__":
    DispensaApp().run()