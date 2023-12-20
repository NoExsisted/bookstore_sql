from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.send_receive import Send_Receive

bp_send_receive = Blueprint("send_receive", __name__, url_prefix="/send_receive")


@bp_send_receive.route("/send_books", methods=["POST"])
def send_books():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")

    s = Send_Receive()
    code, message = s.send_books(user_id, order_id)
    return jsonify({"message": message}), code


@bp_send_receive.route("/receive_books", methods=["POST"])
def receive_books():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    s = Send_Receive()
    code, message = s.receive_books(user_id, order_id)
    return jsonify({"message": message}), code
