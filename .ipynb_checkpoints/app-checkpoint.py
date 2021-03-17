import streamlit as st
import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle

def desc_calc():
    bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    os.remove('molecule.smi')

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings to bytes
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

def build_model(input_data):
    load_model = pickle.load(open('Homo_Sapiens_Cytochrome_P450_19A1_model.pkl', 'rb'))
    prediction = load_model.predict(input_data)
    st.header('**Prediction output**')
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(load_data[1], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.markdown(filedownload(df), unsafe_allow_html=True)

st.markdown("""
# Cytochrome P450 19A1 Inhibitors Prediction on Homo-Sapiens
### by Ariandy/1kb
App ini digunakan untuk memprediksi bioactivity terhadap penghambatan enzim dari superfamily Cytochrome P450 19A1 yang ada pada Homo Sapiens. Enzim ini merupakan enzim yang menyebabkan kanker payudara.

**Notes & Credits**
- Dataset PubChem Fingerprint yang digunakan merupakan dataset yang telah di-preprocess. Sedangkan raw dataset (yang tidak disertakan pada repository ini) adalah hasil scrap dari [ChemBL Database API](https://www.ebi.ac.uk/chembl/)
- Molecule Descriptor dihitung menggunakan [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/). Berikut [ini](https://doi.org/10.1002/jcc.21707) adalah paper tentang PaDEL.
- Permodelan dibuat berdasarkan workflow [QSAR](https://en.wikipedia.org/wiki/Quantitative_structure%E2%80%93activity_relationship)
- Adapun proses di luar permodelan (akuisisi data, pembersihan, dan Chemical Space Analysis) tidak disertakan dibagian ini dan akan disertakan pada repository terpisah.
- Proses di luar permodelan masih dalam tahap optimasi. Mengingat score R$^{2}$ score pada prediktor ini bernilai 0.63, sehingga memerlukan riset lebih lanjut.
---
""")

with st.sidebar.header('Upload CSV/TXT'):
    uploaded_file = st.sidebar.file_uploader("Upload input file", type=['txt'])
    st.sidebar.markdown("""
[Input file example](https://raw.githubusercontent.com/ariandy/)
""")

if st.sidebar.button('Prediction'):
    load_data = pd.read_table(uploaded_file, sep=' ', header=None)
    load_data.to_csv('molecule.smi', sep = '\t', header = False, index = False)

    st.header('**Original input data**')
    st.write(load_data)

    with st.spinner("Calculate molecule descriptors..."):
        desc_calc()

    # Read in calculated descriptors and display the dataframe
    st.header('**Calculated molecular descriptors**')
    desc = pd.read_csv('descriptors_output.csv')
    st.write(desc)
    st.write(desc.shape)

    # Read descriptor list used in previously built model
    st.header('**Subset of descriptors from previously built models**')
    Xlist = list(pd.read_csv('descriptor_list.csv').columns)
    desc_subset = desc[Xlist]
    st.write(desc_subset)
    st.write(desc_subset.shape)

    # Apply trained model to make prediction on query compounds
    build_model(desc_subset)
else:
    st.info('Untuk memulai, unggah input data pada sidebar!')
