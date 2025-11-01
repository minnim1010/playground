#!/usr/bin/env just --justfile

run webserver:
    uv run streamlit run src/app.py --server.address localhost