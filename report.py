import requests
import pandas as pd
import numpy as np
from requests.auth import HTTPBasicAuth
import sys
import os
from itertools import zip_longest


class Api:

    API_PATH_PROJECTS = "components/search_projects"
    API_PATH_MEASURES = "measures/search"
    PAGE_SIZE = 500

    def __init__(self, api_base, user_token):
        self.api_base = api_base
        self.user_token = user_token

    def get_auth(self):
        return HTTPBasicAuth(self.user_token, "")

    def api_call_authenticated(self, url, params):
        params["ps"] = self.PAGE_SIZE
        r = requests.get(url, params=params, auth=self.get_auth())

        if r.status_code == 200:
            return r.json()
        else:
            raise ConnectionError("API request failed")

    def get_projects(self, tags=None):
        params = {"f": "analysisDate"}
        if tags:
            params["filter"] = "tags = {}".format(tags)

        return self.api_call_authenticated(
            self.api_base + self.API_PATH_PROJECTS,
            params
        )

    def get_measures(self, projects, metrics):
        params = {
            'projectKeys': projects,
            'metricKeys': metrics
        }

        return self.api_call_authenticated(
            self.api_base + self.API_PATH_MEASURES,
            params=params
        )


class Report:
    # metrics
    # see https://docs.sonarqube.org/latest/user-guide/metric-definitions/ for detailed description
    #
    # alert_status - passed/failed
    # bugs - number of bugs
    # reliability_rating - based on bugs, A, B, ...
    # vulnerabilities
    # security_rating - based on vulnerabilities, A, B, ...
    # security_hotspots_reviewed - rate of reviewd hotspots
    # security_review_rating - A, B, ... based on rate
    # code_smells
    # sqale_rating
    # coverage
    # duplicated_lines_density
    # ncloc - number of lines of code

    metrics = [
        "alert_status",
        "bugs",
        "reliability_rating",
        "vulnerabilities",
        "security_rating",
        "security_hotspots_reviewed",
        "security_review_rating",
        "code_smells",
        "sqale_rating",
        "coverage",
        "duplicated_lines_density",
        "ncloc"
    ]

    def __init__(self, api):
        self.api = api

    def get_project_report(self, project_tag):
        projects = self.get_projects(project_tag)
        projects.set_index("key", inplace=True)
        project_keys = projects.index.tolist()

        for metric in self.metrics:
            projects[metric] = np.nan

        # api does not accept more than 50 projects at once
        # so query in 50 item chunks
        for subset in Report.grouper(project_keys, 50):
            filtered_subset = list(filter(None, subset))

            measures = self.get_measures(filtered_subset)

            for measure in measures:
                projects.loc[measure["component"], measure["metric"]] = measure["value"]

        return projects

    def get_measures(self, project_list):
        measures = self.api.get_measures(','.join(project_list), ",".join(self.metrics))
        return measures["measures"]

    def get_projects(self, project_tag):
        components = self.api.get_projects(project_tag)["components"]
        projects = pd.DataFrame(components)

        return projects

    @staticmethod
    # borrowed from stackoverflow
    def grouper(iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

def usage():
    print("Usage:\n{} <report filename> [<project tag>]".format(__file__))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        exit(-1)

    report_file = sys.argv[1]
    tag = sys.argv[2] if len(sys.argv) > 2 else None

    api_base = os.getenv("SONARQUBE_API_BASE")
    user_token = os.getenv("SONARQUBE_API_USERTOKEN")

    api = Api(api_base, user_token)
    report = Report(api)

    df = report.get_project_report(tag)

    df.to_csv(report_file)
    print("Report generated at: {}".format(report_file))
