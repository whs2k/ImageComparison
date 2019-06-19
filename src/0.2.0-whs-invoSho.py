import os
#import magic
import urllib.request
#from app import app
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import sys

import pandas as pd
from tqdm import tqdm
sys.path.append(os.getcwd())
import helper
from Config import UPLOAD_FOLDER, FN_DF_TRANSFORMED 

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

trained_densenet_model = helper.load_model()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            fn_to_save = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(fn_to_save)
            #flash('Processing File')
            df = helper.get_image_sims(fn_to_save, trained_densenet_model, FN_DF_TRANSFORMED) \
                                            .sort_values('ref_cosim',ascending=False)
            helper.createResultsHTML(df_html=df[['fn','ref_cosim']],
                                upload_image=fn_to_save, 
                                list_of_topX_links=df.fn.tolist()[0:3], 
                                list_of_perfect_links=df[df['ref_cosim'] > 0.8].fn.tolist()[0:3], 
                                fn_to_save=os.path.join(os.getcwd(),'templates','export_'+fn_to_save+'.html'))
            #print(df.head())
            #flash("Saved HTML REsults")
            return render_template('export.html')


        #process file
        #save output in an templates/___.html
        #render_template(___.html)




            return redirect('/')
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect(request.url)

if __name__ == "__main__":
    
    #app.run()
    app.run(host='0.0.0.0', port=5001, debug=True)