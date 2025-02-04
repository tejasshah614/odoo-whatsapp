from flask import Flask,request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/send_update", methods=["POST"])
def send_update():
    data = request.json
    socketio.emit("new_message", data)
    return {"status": "success"}

if __name__ == "__main__":
    socketio.run(app, debug=True)
