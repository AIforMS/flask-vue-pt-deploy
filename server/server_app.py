from f_app import app, db
from f_app.user_model import Userr


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Userr': Userr}
