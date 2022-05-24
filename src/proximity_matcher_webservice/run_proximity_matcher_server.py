#!/usr/bin/env python3
#
# Copyright 2022 - TNG Technology Consulting GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0


import subprocess


def run_proximity_server():
    subprocess.Popen("export FLASK_APP=proximity_matcher_webservice.proximity_server.py; flask run", shell=True)


def run_proximity_server_opt():
    subprocess.Popen("export FLASK_APP=proximity_matcher_webservice.proximity_server_opt.py; flask run", shell=True)


def run_proximity_server_gunicorn():
    subprocess.Popen("gunicorn -w 4 -b 127.0.0.1:5000 --preload proximity_matcher_webservice.proximity_server:app", shell=True)


def run_proximity_server_gunicorn_opt():
    subprocess.Popen("gunicorn -w 4 -b 127.0.0.1:5000 -t 60 --preload "
                     "proximity_matcher_webservice.proximity_server_opt:app", shell=True)
