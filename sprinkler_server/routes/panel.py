from flask import Blueprint, render_template, redirect, url_for

panel_blueprint = Blueprint(
    "control_panel",
    __name__,
    static_folder="../public/panel/static/",
    template_folder="../public/panel/template/",
    url_prefix="/panel",
)


@panel_blueprint.route("/")
def default_page():
    return redirect(url_for(".control_page"))


@panel_blueprint.route("/control")
def control_page():
    return render_template("index.html")


@panel_blueprint.route("/schedule")
def schedule_page():
    return "Work In Progress", 200
