# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# More stuff

#Reference:
# http://python-cloudant.readthedocs.org/en/latest/getting_started.html
# https://github.com/IBM-Bluemix/bluemix-python-flask-sample
import os.path, time
from flask import Flask, request, render_template, send_file
import datetime
import cloudant
import hashlib

app = Flask(__name__)


client = cloudant.Cloudant('', '', url='https:/')
# or using url
# client = Cloudant(USERNAME, PASSWORD, url='https://acct.cloudant.com')

# Connect to the account
client.connect()

# Open an existing database

my_database = client['my_database']

@app.route('/')
def Welcome():
    #return app.send_static_file('index.html')
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename=file.filename

        if filename != "":
            file_contents = file.stream.read().decode("utf-8")
            #find out the hash code for file contents
            hashvalue = hashlib.md5(file_contents).hexdigest()
            lastmodifieddate = time.strftime("%x")


            print lastmodifieddate

            filenamematched = 0
            hashvaluematched = 0
            #iterate through each document in my_database
            for document in my_database:
                if document['filename'] == filename:
                    filenamematched = 1
                    versionnumber = document['versionnumber']
                    hashvalueofcloudantdoccontents = hashlib.md5(document['filecontents']).hexdigest()
                    if hashvalueofcloudantdoccontents == hashvalue:
                        hashvaluematched = 1
            #if file name not matched
            if filenamematched == 0:
                fileinfo = {
                        'hashvalue': hashvalue,
                        'filename': filename,
                        'versionnumber': 1,
                        'lastmodifieddate': lastmodifieddate,
                        'filecontents': file_contents
                        }
                my_database.create_document(fileinfo)
                result='File created and uploaded to IBM Bluemix successfully.'
                return render_template('result.html',result=result)
            #if file name is matched but contents are different
            if filenamematched == 1:
                if hashvaluematched == 0:
                    fileinfo = {
                            'hashvalue': hashvalue,
                            'filename': filename,
                            'versionnumber': versionnumber+1,
                            'lastmodifieddate': lastmodifieddate,
                            'filecontents': file_contents
                            }
                    my_database.create_document(fileinfo)
                    result='File name already exists, so new file version created and uploaded to IBM Bluemix successfully.'
                    return render_template('result.html',result=result)

            #if filename and filecontents already exits
            result='File already exists on the IBM Bluemix.'
            return render_template('result.html',result=result)
        else:
            return render_template('result.html',result="Please select the file.")

    else:
        return 'Error'

@app.route('/list', methods=['GET', 'POST'])
def list():
    files = []
    for document in my_database:
        fileinfo = {}
        #save the required details into fileinfo json
        fileinfo['filename'] = document['filename']
        fileinfo['versionnumber'] = document['versionnumber']
        fileinfo['lastmodifieddate'] = document['lastmodifieddate']
        files.append(fileinfo)

    return render_template('list.html',files=files)

@app.route('/download', methods=['GET', 'POST'])
def download():
    #filename=request.args.get('filename')
    filename, file_extension = os.path.splitext(request.args.get('filename'))
    versionnumber=request.args.get('versionnumber')

    for document in my_database:
        if document['filename'] == filename+file_extension:
            if int(document['versionnumber']) == int(versionnumber):
                #file get saved into home directory of Ubuntu
                filecontents=document['filecontents']
                result= "File '" + filename+file_extension + "' with version number '" + versionnumber + "' downloaded successfully and saved as '" + filename+versionnumber+file_extension + "'"

    file_download = open(filename+file_extension, 'wb')

    file_download.write(filecontents);
    file_download.close()
    file_download = open('/home/jeet/'+filename+file_extension, 'rb')

    return send_file(file_download.name, as_attachment=True)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    filename_delete=request.args.get('filename')
    versionnumber_delete=request.args.get('versionnumber')
    #iterate through my_database, if filename and version number matches, delete the file.
    for document in my_database:
        if document['filename'] == filename_delete:
            if int(document['versionnumber']) == int(versionnumber_delete):
                document.delete()
                result= "File '" + filename_delete + "' with version number '" + versionnumber_delete + "' deleted successfully."

    return render_template('result.html',result=result)

port = os.getenv('VCAP_APP_PORT', '4500')

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
