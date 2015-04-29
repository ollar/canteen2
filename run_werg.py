from main.main import app
from main.main import login_manager

# --------------------------------------------------------------------
# -------------------------------------------------- Application Start
# --------------------------------------------------------------------

if __name__ == '__main__':
    login_manager.init_app(app)
    app.run(host='0.0.0.0')
