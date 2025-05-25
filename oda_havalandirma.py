import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox


sicaklik = ctrl.Antecedent(np.arange(0, 41, 1), 'Oda Sıcaklığı (°C)')
nem = ctrl.Antecedent(np.arange(0, 101, 1), 'Nem Oranı (%)')
hava_kalitesi = ctrl.Antecedent(np.arange(0, 501, 1), 'Hava Kalitesi')
insan_sayisi = ctrl.Antecedent(np.arange(0, 11, 1), 'İçerdeki İnsan Sayısı')
pencere_acikligi = ctrl.Antecedent(np.arange(0, 101, 1), 'Pencere Açıklık Seviyesi (%)')


fan_hizi = ctrl.Consequent(np.arange(0, 11, 1), 'Fan Hızı')
havalandirma_suresi = ctrl.Consequent(np.arange(0, 31, 1), 'Havalandırma Süresi (dk)')


sicaklik['dusuk'] = fuzz.trimf(sicaklik.universe, [0, 0, 20])
sicaklik['orta'] = fuzz.trimf(sicaklik.universe, [15, 25, 30])
sicaklik['yuksek'] = fuzz.trimf(sicaklik.universe, [25, 40, 40])

nem['dusuk'] = fuzz.trimf(nem.universe, [0, 0, 40])
nem['orta'] = fuzz.trimf(nem.universe, [30, 50, 70])
nem['yuksek'] = fuzz.trimf(nem.universe, [60, 100, 100])

hava_kalitesi['iyi'] = fuzz.trimf(hava_kalitesi.universe, [0, 0, 100])
hava_kalitesi['orta'] = fuzz.trimf(hava_kalitesi.universe, [80, 150, 250])
hava_kalitesi['kotu'] = fuzz.trimf(hava_kalitesi.universe, [200, 500, 500])

insan_sayisi['az'] = fuzz.trimf(insan_sayisi.universe, [0, 0, 3])
insan_sayisi['orta'] = fuzz.trimf(insan_sayisi.universe, [2, 5, 7])
insan_sayisi['cok'] = fuzz.trimf(insan_sayisi.universe, [6, 10, 10])

pencere_acikligi['kapali'] = fuzz.trimf(pencere_acikligi.universe, [0, 0, 10])
pencere_acikligi['kismi'] = fuzz.trimf(pencere_acikligi.universe, [5, 50, 80])
pencere_acikligi['tam_acik'] = fuzz.trimf(pencere_acikligi.universe, [70, 100, 100])

fan_hizi['dusuk'] = fuzz.trimf(fan_hizi.universe, [0, 0, 4])
fan_hizi['orta'] = fuzz.trimf(fan_hizi.universe, [3, 5, 7])
fan_hizi['yuksek'] = fuzz.trimf(fan_hizi.universe, [6, 10, 10])

havalandirma_suresi['kisa'] = fuzz.trimf(havalandirma_suresi.universe, [0, 0, 10])
havalandirma_suresi['orta'] = fuzz.trimf(havalandirma_suresi.universe, [5, 15, 25])
havalandirma_suresi['uzun'] = fuzz.trimf(havalandirma_suresi.universe, [20, 30, 30])

rule1 = ctrl.Rule(sicaklik['yuksek'] | nem['yuksek'] | hava_kalitesi['kotu'] | insan_sayisi['cok'], (fan_hizi['yuksek'], havalandirma_suresi['uzun']))
rule2 = ctrl.Rule(sicaklik['orta'] & nem['orta'] & hava_kalitesi['orta'] & insan_sayisi['orta'], (fan_hizi['orta'], havalandirma_suresi['orta']))
rule3 = ctrl.Rule(sicaklik['dusuk'] & nem['dusuk'] & hava_kalitesi['iyi'] & insan_sayisi['az'], (fan_hizi['dusuk'], havalandirma_suresi['kisa']))
rule4 = ctrl.Rule(pencere_acikligi['tam_acik'], (fan_hizi['dusuk'], havalandirma_suresi['kisa']))
rule5 = ctrl.Rule(pencere_acikligi['kismi'], (fan_hizi['orta'], havalandirma_suresi['orta']))


sistem = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
simulasyon = ctrl.ControlSystemSimulation(sistem)


class HavalandirmaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Oda Havalandırma Sistemi - Bulanık Mantık")
        self.geometry("950x700")

        self.entries = {}
        for i, (isim, aralik) in enumerate([
            ('Oda Sıcaklığı (°C)', (0, 40)),
            ('Nem Oranı (%)', (0, 100)),
            ('Hava Kalitesi', (0, 500)),
            ('İçerdeki İnsan Sayısı', (0, 10)),
            ('Pencere Açıklık Seviyesi (%)', (0, 100))
        ]):
            lbl = tk.Label(self, text=isim)
            lbl.grid(row=i, column=0, padx=10, pady=5, sticky='w')
            ent = tk.Entry(self)
            ent.grid(row=i, column=1, padx=10, pady=5)
            self.entries[isim] = (ent, aralik)

        self.calc_btn = tk.Button(self, text="Hesapla", command=self.hesapla)
        self.calc_btn.grid(row=6, column=0, columnspan=2, pady=15)

        self.result_label = tk.Label(self, text="", font=("Arial", 12, "bold"))
        self.result_label.grid(row=7, column=0, columnspan=2)

        self.fig, self.ax = plt.subplots(figsize=(7, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=10, padx=10, pady=10)


        self.canvas._tkcanvas.pack_forget() 

    def hesapla(self):
        try:
            girilen_degerler = {}
            for isim, (entry, (min_v, max_v)) in self.entries.items():
                val = float(entry.get())
                if val < min_v or val > max_v:
                    raise ValueError(f"{isim} için değer aralığı {min_v}-{max_v} arasında olmalı.")
                girilen_degerler[isim] = val

            simulasyon.input['Oda Sıcaklığı (°C)'] = girilen_degerler['Oda Sıcaklığı (°C)']
            simulasyon.input['Nem Oranı (%)'] = girilen_degerler['Nem Oranı (%)']
            simulasyon.input['Hava Kalitesi'] = girilen_degerler['Hava Kalitesi']
            simulasyon.input['İçerdeki İnsan Sayısı'] = girilen_degerler['İçerdeki İnsan Sayısı']
            simulasyon.input['Pencere Açıklık Seviyesi (%)'] = girilen_degerler['Pencere Açıklık Seviyesi (%)']

            simulasyon.compute()

            fan = simulasyon.output['Fan Hızı']
            sure = simulasyon.output['Havalandırma Süresi (dk)']

            self.result_label.config(
                text=f"Fan Hızı: {fan:.2f} / 10\n"
                     f"Havalandırma Süresi: {sure:.2f} dakika"
            )

            self.grafik_ciz(girilen_degerler)

        except ValueError as e:
            messagebox.showerror("Hata", str(e))
        except Exception as e:
            messagebox.showerror("Hata", "Bir hata oluştu: " + str(e))

    def grafik_ciz(self, girilen_degerler):
        self.ax.clear()

        fan_hizi.view(ax=self.ax)

        self.ax.plot([simulasyon.output['Fan Hızı']], [0], 'ro', markersize=12, label="Çıktı Fan Hızı")
        self.ax.set_title("Fan Hızı Grafiği")
        self.ax.set_ylim(-0.1, 1.1)
        self.ax.legend()
        self.canvas.draw()

if __name__ == "__main__":
    app = HavalandirmaApp()
    app.mainloop()
