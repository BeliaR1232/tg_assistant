#!/usr/bin/env sh
dockerize -wait 'tcp://postgres:5432'
alembic upgrade head
python add_category.py
python main.py
