#!/bin/bash

. venv/bin/activate
gunicorn run_gun:app --log-file=-