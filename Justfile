#!/usr/bin/env just --justfile

run webserver:
    uv run streamlit run app.py