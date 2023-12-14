from flask import Flask, render_template, request
import numpy as np
import pandas as pd
import csv
import pickle
from io import StringIO
import mysql.connector

app = Flask(__name__)
# #konfigurasi db
# conn = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     database ="eclatdatabase",
#     password="",
# )
# if conn.is_connected():
#     print("terhubung")

# Membaca file CSV dari URL

def hitung_eclat(data):
    data = pd.read_csv(StringIO(file.read().decode('utf-8')))
    grouped_data = data.groupby('Transaction')['Item'].apply(list).reset_index()
    all_items = grouped_data['Item'].explode()
    unique_items = all_items.unique()

    # Menghitung nilai support untuk setiap item
    vertical = list()
    new_vertical2 = list()
    sup1 = list()

    # Menghitung jumlah sum dari kolom Kuantitas
    total_kuantitas_all_items = data['Kuantitas'].sum()

    for item in all_items.unique():
        id = 1
        for d in grouped_data['Item']:
            if item in d:
                vertical.append(id)
            id += 1
        new_vertical2.append(list(vertical))
        s = len(vertical) / total_kuantitas_all_items  # Menggunakan total_kuantitas_all_items
        sup1.append(s)
        vertical = []

    data_vertical = {
        "Nama Barang": all_items.unique(),
        "Kode Transaksi": new_vertical2,
        "Support": sup1
    }

    df_vertical = pd.DataFrame(data_vertical)

    #Mengurutkan DataFrame berdasarkan nilai Support dari terbesar ke terkecil
    sorted_df = df_vertical.sort_values(by='Support', ascending=False)

    sorted_df['Jumlah Kode Transaksi'] = sorted_df['Kode Transaksi'].apply(lambda x: len(str(x).split(', ')))
    sorted_df = sorted_df[sorted_df['Jumlah Kode Transaksi'] > 1]

    # Inisialisasi list pasangan2
    pasangan2 = []
    # Inisialisasi list untuk menyimpan nilai
    values_pasangan2 = []
    intersect2 = []
    # Looping untuk membuat pasangan item
    for i in range(0, len(sorted_df)):
        for j in range(i + 1, len(sorted_df)):
            pasangan2.append([sorted_df['Nama Barang'].iloc[i], sorted_df['Nama Barang'].iloc[j]])
    # Looping untuk menemukan irisan dari pasangan item
    for a in range(0, len(sorted_df)):
        for b in range(a + 1, len(sorted_df)):
            nama_barang_a = sorted_df['Nama Barang'].iloc[a]
            nama_barang_b = sorted_df['Nama Barang'].iloc[b]

            kode_transaksi_a = set(sorted_df[sorted_df['Nama Barang'] == nama_barang_a]['Kode Transaksi'].iloc[0])
            kode_transaksi_b = set(sorted_df[sorted_df['Nama Barang'] == nama_barang_b]['Kode Transaksi'].iloc[0])

            intersect = list(kode_transaksi_a.intersection(kode_transaksi_b))
            values_pasangan2.append([sorted_df['Kode Transaksi'].iloc[a], sorted_df['Kode Transaksi'].iloc[b]])
            intersect2.append(intersect)

    # Membuat DataFrame dari hasil penyilangan item
    data_penyilangan2 = {
        "Pasangan Barang": pasangan2,
        "Kode Transaksi": values_pasangan2,
        "Hasil Penyilangan": intersect2
    }

    df_penyilangan2 = pd.DataFrame(data_penyilangan2)
    df_penyilangan2
    min_sup = 5
    new_values_pasangan2 = []
    new_pasangan2 = []
    new_intersect2 = []
    for i in range(0,len(values_pasangan2)):
        if len(intersect2[i]) >= min_sup:
            #hasil_pasangan2.append([pasangan2[i],intersect2[i],support2[i]])
            new_pasangan2.append(pasangan2[i])
            new_values_pasangan2.append(values_pasangan2[i])
            new_intersect2.append(intersect2[i])
    data_penyilangan2 = {"Nama Barang":new_pasangan2,"Kode Transaksi":new_values_pasangan2, "Hasil Penyilangan":new_intersect2}
    df_penyilangan2 = pd.DataFrame(data_penyilangan2)
    df_penyilangan2
    rules2=[]
    values_rules2=[]
    confidents2 = []
    final_support2 = []
    final_irisan2 =[]
    # menentukan aturan asosiasi untuk itemset berisi 2 item
    for i in range(len(new_pasangan2)):
        support = len(new_intersect2[i])/len(data_penyilangan2)
        rules2.append([new_pasangan2[i][0],new_pasangan2[i][1]])
        rules2.append([new_pasangan2[i][1],new_pasangan2[i][0]])

        values_rules2.append([new_values_pasangan2[i][0],new_values_pasangan2[i][1]])
        final_irisan2.append(new_intersect2[i])
        final_support2.append(support)
        con2 = len(new_intersect2[i])/len(new_values_pasangan2[i][0])
        confidents2.append(con2)


        #eclat_p2.append([[new_pasangan2[i][0],new_pasangan2[i][1]],new_support2[i],con2])

        values_rules2.append([new_values_pasangan2[i][1],new_values_pasangan2[i][0]])
        final_irisan2.append(new_intersect2[i])
        final_support2.append(support)
        con2 = len(new_intersect2[i])/len(new_values_pasangan2[i][1])
        confidents2.append(con2)
    final_rules2 =[]
    for value in rules2:
        string = f"Jika beli {value[0]}, maka beli {value[1]}"
        final_rules2.append(string)
    data_penyilangan2 = {"Nama Barang":final_rules2,"Support":final_support2, "Confidence":confidents2}
    df_penyilangan2 = pd.DataFrame(data_penyilangan2)
    sorted_df = df_penyilangan2.sort_values(by=['Support', 'Confidence'], ascending=False)
    with open('model_eclat.pkl', 'wb') as model_file:
        pickle.dump(data_penyilangan2, model_file)

#routing
@app.route('/') #menampilkan data
def halo():
    return render_template('index.html')

@app.route('/tambah', methods = ['GET', 'POST'])
def tambah():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        file = request.files['file']
        if file:
            data = pd.read_csv(StringIO(file.read().decode('utf-8')))
            if model_file:
                result_table = hitung_eclat(data)
            else:
                # Jika model belum ada, hitung kembali
                result_table = hitung_eclat(data)

            return render_template('hasil_analisis.html', tables=[result_table.to_html(classes='data')],titles=result_table.columns.values)
        else:
            return render_template('upload_data.html', error="Gagal mengunggah file CSV.")

if __name__ == '__main__':
    app.run(debug=True)