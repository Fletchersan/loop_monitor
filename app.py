import os
import psycopg2
from flask import Flask, render_template
from flask import jsonify, make_response
from uuid import uuid4
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_
from models import *
from celery import Celery
import pandas as pd
from io import StringIO
from datetime import datetime
import json
from helpers import generate_report_data


app = Flask(__name__)
celery = Celery(app.name, broker='redis://localhost:6379/0')
engine = create_engine('postgresql+psycopg2://postgres:decent_password@localhost:54320/loop_db')
Session = sessionmaker(bind=engine)
session: sessionmaker = Session()


@app.route('/')
def index():
    return "Hello World!"

@app.route('/trigger_report')
def trigger_report():
    report_id, error = trigger_report_generation()
    if error == '':
        # trigger report generation logic
        # return uuid
        response = make_response(
            jsonify(
            {
                "message": "Request triggered successfully",
                "uuid": str(report_id),
                'STATUS': '200'
            }
            )
        )
    return response

@app.route('/get_report/<report_id>')
def get_report(report_id: str):
    is_uuid_valid = validate_report_id(report_id)
    if not is_uuid_valid:
        return "invalid report id, check again"
    is_report_ready = check_report_ready(report_id)
    if is_report_ready:
        report = session.query(Reports).filter(Reports.report_id==report_id).first()
        response = make_response(
            jsonify(
                {
                    'report_id': report_id,
                    'data': report.report,
                }
            )
        )
    else:
        response = f"Report Not Ready {report_id}"
    return response

def validate_report_id(report_id: str):
    reports_with_report_id = session.query(Reports).filter(Reports.report_id==report_id).count()
    return reports_with_report_id == 1

def check_report_ready(report_id: str):
    ready_reports = session.query(Reports).filter(
            and_(Reports.report_id==report_id, Reports.report_status=='Ready')
        ).count()
    print(ready_reports)
    report_obj = session.query(Reports).filter(
            and_(Reports.report_id==report_id, Reports.report_status=='Ready')
        ).first()
    print(report_obj)
    
    return ready_reports==1

@celery.task
def generate_report(report_id):
    report_data = session.query(Reports).filter(Reports.report_id==report_id).first()
    if report_data is not None:
        # report_request_ts = report_data.request_timestamp
        create_report(report_data)

def trigger_report_generation():
    report_id = uuid4()
    new_report = Reports(
        report_id=str(report_id),
        report_status='Not Ready',
        request_timestamp = datetime.utcnow()
    )
    print("adding new report")
    session.add(new_report)
    session.commit()
    print('Report added')
    generate_report.delay(report_id)
    return report_id, ''



def create_report(report: Reports):
    print("IN CREATE REPORT")
    report_data = generate_report_data(session, report)
    report_df: pd.DataFrame = pd.DataFrame(columns = [
        'store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week', 
        'downtime_last_hour', 'downtime_last_day', 'downtime_last_week'
    ])
    for row in report_data:
        report_df.loc[len(report_df.index)] = row
    print(report_df.head())
    report_df = report_df.T
    print('BEGIN JSON CONVERSION')
    json_csv = report_df.to_dict()
    json_csv = json.dumps(json_csv)
    print('JSON CONVERSION FINISHED')
    report.report_status = 'Ready'
    report.report = json_csv
    report.generation_timestamp = datetime.utcnow()
    session.commit()
    print('UPDATE MADE')
    

