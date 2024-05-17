from flask import Blueprint
from ..controller.document import *


blueprint = Blueprint('document', __name__, url_prefix='/document')

blueprint.route('/insert', methods=['POST'])(insert_document_to_vdb)