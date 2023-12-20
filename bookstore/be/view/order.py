from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.order import Order

bp_order = Blueprint("order", __name__, url_prefix="/order")


@bp_order.route("/new_order_cancel_manually", methods=["POST"])
def new_order_cancel_manually():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    o = Order()
    code, message = o.new_order_cancel_manually(user_id, order_id)
    return jsonify({"message": message}), code


@bp_order.route("/new_order_cancel_auto", methods=["POST"])
def new_order_cancel_auto():
    order_id: str = request.json.get("order_id")
    o = Order()
    code, message = o.new_order_cancel_auto(order_id)
    return jsonify({"message": message}), code


@bp_order.route("/query_order_history", methods=["POST"])
def query_order_history():
    user_id: str = request.json.get("user_id")
    o = Order()
    code, message = o.query_order_history(user_id)
    return jsonify({"message": message}), code
