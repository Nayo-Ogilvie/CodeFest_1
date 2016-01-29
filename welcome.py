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

#Reference:
# http://python-cloudant.readthedocs.org/en/latest/getting_started.html
# https://github.com/IBM-Bluemix/bluemix-python-flask-sample
import os.path, time
from flask import Flask, request, redirect, url_for, flash, render_template
import gnupg
from cloudant.account import Cloudant
import hashlib

app = Flask(__name__)

#Python-gnupg code
gpg = gnupg.GPG(gnupghome='/home/jeet/Cloud/gpghome')
client = Cloudant('3cc6ceb4-cd52-47f8-81c7-f0f3505f6cf8-bluemix', 'e2c3db62406e0c81aa32fda4a99f448434c728ab8ae3b80171c4c693c8c6e15e', url='https://3cc6ceb4-cd52-47f8-81c7-f0f3505f6cf8-bluemix:e2c3db62406e0c81aa32fda4a99f448434c728ab8ae3b80171c4c693c8c6e15e@3cc6ceb4-cd52-47f8-81c7-f0f3505f6cf8-bluemix.cloudant.com')
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
        file_contents = file.stream.read().decode("utf-8")
        print file_contents
        hashvalue = hashlib.md5(file_contents).hexdigest()
        lastmodifieddate = '12/01/2015'
        #lastmodifieddate = time.ctime(os.path.getmtime(filename))
        wd = os.path.dirname(os.path.abspath(filename))
        print wd

        filenamematched = 0
        hashvaluematched = 0

        for document in my_database:
            print document['filename']
            print filename
            if document['filename'] == filename:
                filenamematched = 1
                versionnumber = document['versionnumber']
                hashvalueofcloudantdoccontents = hashlib.md5(document['filecontents']).hexdigest()
                if hashvalueofcloudantdoccontents == hashvalue:
                    hashvaluematched = 1

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

        result='File already exists on the IBM Bluemix.'
        return render_template('result.html',result=result)

    else:
        return 'Error'
    #return redirect(url_for('join'))


@app.route('/join')
def join():
    return 'hihi'

@app.route('/list', methods=['GET', 'POST'])
def list():
    files = []
    for document in my_database:
        fileinfo = {}
        fileinfo['filename'] = document['filename']
        fileinfo['versionnumber'] = document['versionnumber']
        files.append(fileinfo)

    return render_template('list.html',files=files)

@app.route('/download', methods=['GET', 'POST'])
def download():
    filename_download=request.args.get('filename')
    versionnumber_download=request.args.get('versionnumber')

    for document in my_database:
        print document['filename']
        print document['versionnumber']
        print filename_download
        print versionnumber_download
        if document['filename'] == filename_download:
            print 'jeet2'
            if int(document['versionnumber']) == int(versionnumber_download):
                print "jeet"
                with open(filename_download+versionnumber_download, 'w') as my_example:
                    my_example.write(document['filecontents'])
                    result = "File '" +filename_download + "' with version number '" + versionnumber_download+ "' downloaded successfully."

    return render_template('result.html',result=result)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    filename_delete=request.args.get('filename')
    versionnumber_delete=request.args.get('versionnumber')
    for document in my_database:
        if document['filename'] == filename_delete:
            if int(document['versionnumber']) == int(versionnumber_delete):
                document.delete()
                result= "File '" + filename_delete + "' with version number '" + versionnumber_delete + "' deleted successfully."

    return render_template('result.html',result=result)

port = os.getenv('VCAP_APP_PORT', '4500')

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))