from flask import Blueprint
from ..controller.document import *


blueprint = Blueprint('document', __name__, url_prefix='/document')

blueprint.route('/insert', methods=['POST'])(insert_document_to_vdb)
blueprint.route('/delete', methods=['DELETE'])(delete_document_from_vdb)
blueprint.route('/check', methods=['GET'])(check_document_exist_in_vdb)
blueprint.route('/mind_map', methods=['GET'])(create_mind_map)