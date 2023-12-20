from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.search import Search

bp_search = Blueprint("search", __name__, url_prefix="/search")


@bp_search.route("/search_books", methods=["POST"])
def search_books():
    store_id = request.json.get("store_id")
    search_query = request.json.get("search_query")
    search_scopes = request.json.get("search_scopes")
    s = Search()
    code, message = s.search_books(
        store_id=store_id,
        search_query=search_query,
        search_scopes=search_scopes
    )
    return jsonify({"code": code, "message": message}), code
