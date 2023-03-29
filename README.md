# Loop Kitchen Monitoring

APIs:
1. Trigger Report: 
    Generates an entry in a reports table, adds a generate report task to the task queue(celery+redis)
2. Get Report
    Retrieves report based on report id

Data too large to effectively compute on local machine, so no video generated, apis have been tested to be functional
utc timestamp defaulted to 25th Jan 2023 because of data freshness for testing