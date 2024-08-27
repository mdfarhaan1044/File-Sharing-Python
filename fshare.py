from flask import (
    Flask,
    request,
    send_from_directory)

import os
import socket
import argparse
import signal
import sys
from qr_code import *

app = Flask(__name__)

parser = argparse.ArgumentParser(description="Specify paths to upload")
parser.add_argument(
    "-fp", "--folderpath", type=str, help="Specify upload folder path", default="."
)
args = parser.parse_args()

UPLOAD_FOLDER = args.folderpath

# CTRL+C
def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib/28950776#28950776
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

@app.route('/image')
def send_image():
    return send_from_directory('static', 'my_qr_code.png')

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["files"]
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        
    files = os.listdir(UPLOAD_FOLDER)
    files.sort()
    file_list = "<br>".join(
        [f'<a href="/downloads/{file}">{file}</a>' for file in files]
    )
    
    return f"""
        <!doctype html>
        <title>Easy Share</title>
        <style>
        body{{
        font-family:cursive
        }}

        #drop_area{{
    padding: 100px;
    border: 1px solid black;
    background-color: white;
    color: black;
    font-family: cursive;
    border-radius: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
}}

    h1{{
    text-align:center;
    }}

        button{{
        width: 250px;
        padding: 15px;
        background-color: #8181d5;
        border-radius: 20px;
        border: 1px solid white;
        margin: 12px;
        color: white;
        font-family:cursive;

        }}
        .buttonDiv{{
        display:flex;
        justify-content:center
        }}

        </style>
        <body style= "background-image: linear-gradient(to right, grey, #978080);height: 95vh;color: white;">
        <div>
        <h1>Upload a File</h1>
        <div style="display:flex;width:100%;">
        <div id="drop_area" style="padding:100px; border: 1px solid black; width:70%">
            Drag and drop files here to upload
        </div>
        <div style="width:30%">
<img style= "border-radius:20px;"src="/image" alt="Qr_Code"/>
        </div>
        </div>

        <input style= "display:none" type="file" name="file_input" id="file_input">
        <div class="buttonDiv"><button id="fileButton">Choose File</button>
        <button id="upload_button">Upload</button>
        <button id="cancel_button" style="display: none;">X</button></div>
        <div id="upload_progress"></div>
        <div id="speed"></div>
        </div>
        <script>

        const fileButton = document.getElementById('fileButton');

         fileButton.addEventListener('click', () => {{
      file_input.click();
         }});
        
        ['dragleave', 'drop', 'dragenter', 'dragover'].forEach(function (evt) {{
            document.addEventListener(evt, function (e) {{
                e.preventDefault();
            }}, false);
        }});
        var drop_area = document.getElementById('drop_area');
        var file_input = document.getElementById('file_input');
        var upload_button = document.getElementById('upload_button');
        var cancel_button = document.getElementById('cancel_button');
        var xhr = new XMLHttpRequest();
        drop_area.addEventListener('drop', function (e) {{
            e.preventDefault();
            file_input.files = e.dataTransfer.files;

           const myArray = [...file_input.files]
           myText = ""

            myArray.map((file)=> {{myText += (file.name + " ")}})
           

            document.getElementById('drop_area').innerText = myText;
            
        }}, false);

        file_input.addEventListener('change', function (e) {{
        
         const myArray = [...e.target.files]
           myText = ""

            myArray.map((file)=> {{myText += (file.name + " ")}})
           

            document.getElementById('drop_area').innerText = myText;


        }}, false);
        upload_button.addEventListener('click', function (e) {{
            e.preventDefault();
            var fileList = file_input.files;
            
            if (fileList.length == 0) {{
                return false;
            }}
            xhr.open('post', '/', true);
            var lastTime = Date.now();
            var lastLoad = 0;
            xhr.upload.onprogress = function (event) {{
                if (event.lengthComputable) {{
                    var percent = Math.floor(event.loaded / event.total * 100);
                    document.getElementById('upload_progress').textContent = percent + '%';
                    var curTime = Date.now();
                    var curLoad = event.loaded;
                    var speed = ((curLoad - lastLoad) / (curTime - lastTime) / 1024).toFixed(2);
                    document.getElementById('speed').textContent = speed + 'MB/s'
                    lastTime = curTime;
                    lastLoad = curLoad;
                }}
            }};
            xhr.upload.onloadend = function (event) {{
                document.getElementById('upload_progress').textContent = 'File uploaded successfully';
                document.getElementById('speed').textContent = '0 MB/s';
                cancel_button.style.display = 'none';
                window.location.reload()
            }};
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            var fd = new FormData();
            for (let file of fileList) {{
                fd.append('files', file);
            }}
            lastTime = Date.now();
            xhr.send(fd);
            cancel_button.style.display = 'inline';
            
        }}, false);
        cancel_button.addEventListener('click', function (e) {{
            xhr.abort();
            document.getElementById('upload_progress').textContent = '0%';
            document.getElementById('speed').textContent = '0 MB/s';
            cancel_button.style.display = 'none';
        }}, false);
        </script>
        <h2>Download a File</h2>
        {file_list}
        </body>
        """

@app.route("/downloads/<path:filename>", methods=["GET", "POST"])
def download(filename):
    return send_from_directory(
        directory=UPLOAD_FOLDER,
        path=filename,
        as_attachment=True,
    )

if __name__ == "__main__":
    app.run(host=get_ip(), port=8080)

