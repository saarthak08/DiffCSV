import os

#import magic

import urllib.request

from app import app

from flask import Flask, flash, request, redirect, render_template, session, send_file

from werkzeug.utils import secure_filename

#from csv import comp

 

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'])


def allowed_file(filename):

              return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compare_filenames(filenames):
    return (filenames[0].rsplit('.',1)[1].lower()==filenames[1].rsplit('.',1)[1].lower())
  

         
@app.route('/download', methods=['POST','GET'])
def download_file(): 
    try:
        return send_file(app.config['UPLOAD_FOLDER']+'update.csv',attachment_filename='update.csv',as_attachment=True)
    except:
        flash('update.csv file not found at '+app.config['UPLOAD_FOLDER'])


@app.route('/')
def upload_form():
              
              return render_template('upload.html')

 



@app.route('/', methods=['POST'])
def upload_file():

              if request.method == 'POST':

        # check if the post request has the file part

                             if 'files[]' not in request.files:

                                           flash('No file part')


                                           return redirect(request.url)

                             files = request.files.getlist('files[]')
                             
                             
                             if(files!=None):
                                 
                                 i=0
                                 
                                 filenames=['a','b']
                                                              
                                 for file in files:
                                     
                                     
                                     if file.filename == '':
                                 
                                        flash('No file selected for uploading')
                                     
                                        redirect(request.url)
                                     
                                     if (file and allowed_file(file.filename) ):
                                     
                                        filename = secure_filename(file.filename)
                                        
                                                   
                                        filenames[i]=file.filename
                                        
                                        i+=1
                                        
                                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                                     else:
                                        flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif, csv')
                                      
                                        return redirect(request.url)
                               
                                
                             if(len(filenames)==2 and compare_filenames(filenames)):
                                  flash('Files successfully uploaded')
                                  session['filenames']=filenames
                                  return redirect('/')

                            
                             else:
                                  flash('Both file extensions should be same.')
                                  return redirect('/')
                                    

 

@app.route('/compare', methods=['GET','POST'])
def comp_file():


    os.chdir(app.config['UPLOAD_FOLDER'])

    filenames=session['filenames']
    
    if(filenames!=None and len(filenames)==2):    

        t1 = open(filenames[0], 'r')

        t2 = open(filenames[1], 'r')

        fileone = t1.readlines()

        filetwo = t2.readlines()

        t1.close()

        t2.close()

        outFile = open('update.'+filenames[0].rsplit('.',1)[1].lower(), 'w')
        
        x = 0
        
        for i in fileone:
            
            if i != filetwo[x]:

                outFile.write(filetwo[x])

            x += 1

        outFile.close()
        
        if len(filenames)==2:
            flash('Files Compared Successfully')
            session['filenames']=None
           
    else:
        flash('Please upload the files first')
        session['filenames']=None


        
    return redirect('/')

       

if __name__ == "__main__":

    app.run(port=4000)

   

#os.chdir("C:/Users/eqsvvvx/Desktop/uploads")

#   

#t1 = open('OBF_old.csv', 'r')

#t2 = open('OBF_new.csv', 'r')

#fileone = t1.readlines()

##print(fileone)

#filetwo = t2.readlines()

#t1.close()

#t2.close()

#

#outFile = open('update.csv', 'w')

#x = 0

#for i in fileone:

#    if i != filetwo[x]:

#        outFile.write(filetwo[x])

#    x += 1

#outFile.close()

#   