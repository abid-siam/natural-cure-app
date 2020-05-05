from flask import Flask, render_template, make_response, request
import pdfkit
from datetime import datetime
app = Flask(__name__)


records = [
    {
        'timestamp' : "05/01/20",
        'firstName' : 'Abid',
        'lastName' : 'Siam',
        'sex' : 'male',
        'age' : 21,
        'symptoms' : ['Severe Headaches', 'Light Sensitivity', 'Stiff Neck'],
        'diagnoses' : [
            {
                'diagnosis' : 'Migraine',
                'probability' : 0.4532
            },
            {
                'diagnosis' : 'Meningitis',
                'probability' : 0.2942
            },
            {
                'diagnosis' : 'Tension-type headaches',
                'probability' : 0.1787
            }
        ],
        'treatments' : [
            {
                'condition': 'Migraine',
                'treatments': ["Apply peppermint oil", "Massage head", "Attend Yoga class"]
            },
            {
                'condition': 'Meningitis',
                'treatments': ["Haemophilus influenzae type b (Hib) vaccine"]
            },
            {
                'condition': 'Tension-type headaches',
                'treatments': ["Cognitive behavioral therapy", "Cold compress", "Drink water"]
            },
        ]
    },

    {
        'timestamp' : 13,
        'otherdata' : 'blahblah'
    }
]

@app.route("/generateReport", methods=['GET', 'POST'])
def generateReport():
    if request.form:
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %I:%M:%S %p") # current time 
        timestamp = request.form['timestamp'] # time the diagnosis is made 
        # fetch the record from the database 
        recordChosen = None
        for i in range (len(records)):
            if records[i]['timestamp'] == timestamp:
                recordChosen = records[i]
                break 
            if i == (len(records) - 1) and records[i]['timestamp'] != timestamp:
                error = f'Could not find a record for the timestamp {timestamp}'
                return render_template('generateReport.html', error=error)
        print("The current time:", current_time)
        print(recordChosen)
        rendered = render_template('reportTemplate.html', report=recordChosen, current_time=current_time)
        pdf = pdfkit.from_string(rendered, False)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=report.pdf'
        return response 
    return render_template('generateReport.html')


if __name__ == '__main__':
    app.run(debug=True)