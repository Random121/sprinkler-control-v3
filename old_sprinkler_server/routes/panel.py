import test_constants as constants

from flask import Flask, Blueprint, render_template

panel_blueprint = Blueprint(
    "panel",
    __name__,
    template_folder="public/template",
    static_folder="public/static",
)


@panel_blueprint.route("/")
def panel_page():
    return render_template(
        "index.html",
        api_control_address=constants.API_CONTROL_PATH,
        api_schedule_address=constants.API_SCHEDULE_PATH,
        socketio_address=constants.SOCKETIO_UPDATE_PATH,
    )


def panel_register(flask_app: Flask):
    flask_app.register_blueprint(panel_blueprint)
