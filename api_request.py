from flask import Flask
from flask_restx import Api, Resource, fields
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
api = Api(app, version="1.0", title="Task Report API", description="API local para consulta de backlog", doc="/docs")

ns = api.namespace("tasks", description="Operações relacionadas a tarefas")

simple_report_model = api.model("SimpleReport", {
    "services_backlog": fields.Integer,
})


def get_task_report():
    try:
        base_url = os.getenv("API_URL")
        params = {
            "sysparm_query": "assignment_groupLIKESERVICES MONITORING^stateNOT IN-1,5,6,7",
            "sysparm_display_value": "true",
            "sysparm_exclude_reference_link": "true",
            "sysparm_fields": "sys_created_on,number,opened_by,state,assigned_group"
        }

        response = requests.get(
            base_url,
            params=params,
            auth=(os.getenv("PROXY_USERNAME"), os.getenv("PROXY_PASSWORD")),
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        return len(response.json().get('result', [])) if response.status_code == 200 else 0

    except Exception as e:
        print(f"Erro na consulta de tarefas abertas: {str(e)}")
        return 0


def get_work_task_report():
    try:
        base_url = os.getenv("API_URL")
        params = {
            "sysparm_query": (
                "assignment_groupLIKESERVICES MONITORING"
                "^stateIN6,7"
                "^closed_atONToday@javascript:gs.beginningOfToday()@javascript:gs.endOfToday()"
            ),
            "sysparm_display_value": "true",
            "sysparm_exclude_reference_link": "true",
            "sysparm_fields": "sys_created_on,number,opened_by,state,assigned_group"
        }

        response = requests.get(
            base_url,
            params=params,
            auth=(os.getenv("PROXY_USERNAME"), os.getenv("PROXY_PASSWORD")),
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        return len(response.json().get('result', [])) if response.status_code == 200 else 0

    except Exception as e:
        print(f"Erro na consulta de tarefas fechadas hoje: {str(e)}")
        return 0


@ns.route("/report")
class ReportOpenTasks(Resource):
    @ns.marshal_with(simple_report_model)
    def get(self):
        services_backlog = get_task_report()
        return {"services_backlog": services_backlog}


@ns.route("/work")
class ReportClosedTasks(Resource):
    @ns.marshal_with(simple_report_model)
    def get(self):
        services_backlog = get_work_task_report()
        return {"services_backlog": services_backlog}


if __name__ == "__main__":
    app.run(debug=True)
