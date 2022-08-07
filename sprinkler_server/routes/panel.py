from flask import Blueprint, render_template, redirect, url_for

from sprinkler_server.utils import get_lan_ip_address

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
    return render_template(
        "index.html",
        server_host=get_lan_ip_address(),
    )


@panel_blueprint.route("/schedule")
def schedule_page():
    return render_template(
        "index.html",
        server_host=get_lan_ip_address(),
    )
