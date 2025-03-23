from werkzeug.exceptions import HTTPException
import time
from flask import (
    Flask,
    Response,
    after_this_request,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
)
import uuid
import plotly.express as px
import pandas as pd
import os
import csv
from datetime import datetime as dt
import futures as fut
import mcx
from json import dumps
import RTT_1 as rtt
import AB20 as ab20
import daywiseHL as dhl
import BiweeklyHL as whl

app = Flask(__name__)

app.config["TIMEOUT"] = 900

lines = ["Open", "Close", "High", "Low"]
systems = {1: "RTT", 2: "2 Week High-Lows", 3: "Daily High-Lows"}
criteria = ["2 Days", "3 Days", "4 Days"]


# Custom error handler for all HTTP errors
@app.errorhandler(HTTPException)
def handle_http_error(error):
    return (
        render_template("error.html", error_description=error.description),
        error.code,
    )


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        user = uuid.uuid1()
        system = request.form.get("system")

        if system == "1":
            scripcode = request.form.get("scripcode")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")
            entry_buffer = float(request.form.get("entry_buffer"))
            exit_buffer = float(request.form.get("exit_buffer"))
            # msl = float(request.form.get("msl"))
            tsl1 = float(request.form.get("tsl1"))
            tsl2 = float(request.form.get("tsl2"))

            info = [scripcode.upper(),"Close",entry_buffer,exit_buffer,"5",tsl1,tsl2,start_date,end_date]
            info = tuple(info)
            excel_df = rtt.run(info)
            excel_df.to_csv(f"reports/{user}.csv")
            # fig.update_layout(plot_bgcolor='#27293d')
            # fig.update_layout(paper_bgcolor='#27293d')
            # fig.update_layout(font_color='#ffffff')
            # plot_div = excel_df.to_html()

            with open(f"reports/{user}.csv", "r", newline="") as input_file:
                # Create a csv.reader object
                csv_reader = csv.reader(input_file)

                # Read data from the input CSV file
                data = list(csv_reader)

            with open(f"reports/{user}.csv", "w", newline="") as output_file:
                # Create a csv.writer object
                csv_writer = csv.writer(output_file)

                # Add contents of list as last row in the csv file
                csv_writer.writerow(["","Scripcode","Start Date","End Date","Entry Buffer","Exit Buffer","TSL1","TSL2"])
                csv_writer.writerow(["",scripcode.upper(),start_date,end_date,entry_buffer,exit_buffer,tsl1,tsl2,])
                csv_writer.writerow([""] * len(data[0]))
                csv_writer.writerow([""] * len(data[0]))
                csv_writer.writerows(data)

            return render_template(
                "index.html",
                lines=lines,
                systems=systems,
                downflag=True,
                system="RTT",
                scripcode=scripcode,
                filename=user,
            )

        # elif system == "2":
        #     scripcode = request.form.get("scripcode")
        #     start_date = request.form.get("start_date")
        #     end_date = request.form.get("end_date")
        #     entry_buffer = float(request.form.get("entry_buffer"))
        #     exit_buffer = float(request.form.get("exit_buffer"))
        #     days = int(request.form.get("days"))
        #     msl = float(request.form.get("msl"))
        #     bep = request.form.get("bep")
        #     if not bep:
        #         bep = "no"

        #     info = [
        #         scripcode.upper(),
        #         "Close",
        #         entry_buffer,
        #         exit_buffer,
        #         days,
        #         msl,
        #         bep,
        #         start_date,
        #         end_date,
        #     ]
        #     info = tuple(info)
        #     excel_df = ab20.run(info)

        #     excel_df.to_csv(f"reports/{user}.csv")

        #     with open(f"reports/{user}.csv", "r", newline="") as input_file:
        #         # Create a csv.reader object
        #         csv_reader = csv.reader(input_file)

        #         # Read data from the input CSV file
        #         data = list(csv_reader)

        #     with open(f"reports/{user}.csv", "w", newline="") as output_file:
        #         # Create a csv.writer object
        #         csv_writer = csv.writer(output_file)

        #         # Add contents of list as last row in the csv file
        #         csv_writer.writerow(
        #             [
        #                 "",
        #                 "Scripcode",
        #                 "Start Date",
        #                 "End Date",
        #                 "Entry Buffer",
        #                 "Exit Buffer",
        #                 "Days Average",
        #                 "MSL",
        #                 "BEP",
        #             ]
        #         )
        #         csv_writer.writerow(
        #             [
        #                 "",
        #                 scripcode.upper(),
        #                 start_date,
        #                 end_date,
        #                 entry_buffer,
        #                 exit_buffer,
        #                 days,
        #                 msl,
        #                 bep,
        #             ]
        #         )
        #         csv_writer.writerow([""] * len(data[0]))
        #         csv_writer.writerow([""] * len(data[0]))
        #         csv_writer.writerows(data)

        #     return render_template(
        #         "index.html",
        #         lines=lines,
        #         systems=systems,
        #         downflag=True,
        #         system=f"{days}AB",
        #         scripcode=scripcode,
        #         filename=user,
        #     )

        elif system == "2":
            scripcode = request.form.get("scripcode")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")
            entry_buffer = float(request.form.get("entry_buffer"))
            exit_buffer = float(request.form.get("exit_buffer"))
            msl = float(request.form.get("msl"))
            bep = request.form.get("bep")
            if not bep:
                bep = "no"

            info = [
                scripcode.upper(),
                "Close",
                entry_buffer,
                exit_buffer,
                msl,
                bep,
                start_date,
                end_date,
            ]

            info = tuple(info)
            excel_df = whl.run(info)
            excel_df.to_csv(f"reports/{user}.csv")

            with open(f"reports/{user}.csv", "r", newline="") as input_file:
                # Create a csv.reader object
                csv_reader = csv.reader(input_file)

                # Read data from the input CSV file
                data = list(csv_reader)

            with open(f"reports/{user}.csv", "w", newline="") as output_file:
                # Create a csv.writer object
                csv_writer = csv.writer(output_file)

                # Add contents of list as last row in the csv file
                csv_writer.writerow(
                    [
                        "",
                        "Scripcode",
                        "Start Date",
                        "End Date",
                        "Entry Buffer",
                        "Exit Buffer",
                        "MSL",
                        "BEP",
                    ]
                )
                csv_writer.writerow(
                    [
                        "",
                        scripcode.upper(),
                        start_date,
                        end_date,
                        entry_buffer,
                        exit_buffer,
                        msl,
                        bep,
                    ]
                )
                csv_writer.writerow([""] * len(data[0]))
                csv_writer.writerow([""] * len(data[0]))
                csv_writer.writerows(data)

            return render_template(
                "index.html",
                lines=lines,
                systems=systems,
                downflag=True,
                system="WeeklyHighLow",
                scripcode=scripcode,
                filename=user,
            )

        elif system == "3":
            scripcode = request.form.get("scripcode")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")
            entry_criteria = request.form.get("entry_criteria")
            exit_criteria = request.form.get("exit_criteria")
            entry_buffer = float(request.form.get("entry_buffer"))
            exit_buffer = float(request.form.get("exit_buffer"))
            msl = float(request.form.get("msl"))
            bep = request.form.get("bep")
            if not bep:
                bep = "no"

            info = [
                scripcode.upper(),
                "Close",
                entry_buffer,
                exit_buffer,
                int(entry_criteria.split(" ")[0]),
                msl,
                bep,
                start_date,
                end_date,
            ]

            info = tuple(info)
            excel_df = dhl.run(info)
            excel_df.to_csv(f"reports/{user}.csv")

            with open(f"reports/{user}.csv", "r", newline="") as input_file:
                # Create a csv.reader object
                csv_reader = csv.reader(input_file)

                # Read data from the input CSV file
                data = list(csv_reader)

            with open(f"reports/{user}.csv", "w", newline="") as output_file:
                # Create a csv.writer object
                csv_writer = csv.writer(output_file)

                # Add contents of list as last row in the csv file
                csv_writer.writerow(
                    [
                        "",
                        "Scripcode",
                        "Start Date",
                        "End Date",
                        "Entry Criteria",
                        "Exit Criteria",
                        "Entry Buffer",
                        "Exit Buffer",
                        "MSL",
                        "BEP",
                    ]
                )
                csv_writer.writerow(
                    [
                        "",
                        scripcode.upper(),
                        start_date,
                        end_date,
                        entry_criteria,
                        exit_criteria,
                        entry_buffer,
                        exit_buffer,
                        msl,
                        bep,
                    ]
                )
                csv_writer.writerow([""] * len(data[0]))
                csv_writer.writerow([""] * len(data[0]))
                csv_writer.writerows(data)

            return render_template(
                "index.html",
                lines=lines,
                systems=systems,
                downflag=True,
                system="HighLow",
                scripcode=scripcode,
                criteria=criteria,
                filename=user,
            )
        else:
            return "FAIL"

    return render_template(
        "index.html",
        lines=lines,
        systems=systems,
        downflag=False,
        criteria=criteria,
    )


@app.route("/getPlotCSV/<filename>")
def getPlotCSV(filename):
    try:
        # Read the CSV file content as a string
        with open(f"reports/{filename}.csv", "r") as fp:
            csv_content = fp.read()
            try:
                csv_system = csv_content.split("\n")[5].split(",")[1]
            except:
                csv_system = "System"
            csv_scrip = csv_content.split("\n")[1].split(",")[1]
            csv_sdate = csv_content.split("\n")[1].split(",")[2]
            csv_edate = csv_content.split("\n")[1].split(",")[3]

        return send_file(
            f"reports/{filename}.csv",
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"{csv_system}-{csv_scrip} {csv_sdate}_{csv_edate}.csv",
        )

    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for("index"))


@app.route("/getSuggestions")
def get_suggestions():
    # Get the user input from the query parameters
    user_input = request.args.get("input")
    options = fut.get_all_symbols_list()

    # Filter suggestions from the 'options' list based on user input
    suggestions = [option for option in options if user_input.lower() in option.lower()]

    try:
        commodities = mcx.get_comm_list()
        suggestions = suggestions + [
            commodity for commodity in commodities if user_input.lower() in commodity.lower()
        ]
    except:
        pass

    # Return the suggestions as a JSON response
    return dumps(suggestions)


@app.route("/deleteFile/<filename>")
def delete_file(filename):
    try:
        # Specify the path to the reports folder
        reports_folder = "reports"

        # Construct the full path to the file
        file_path = os.path.join(reports_folder, f"{filename}.csv")

        # Check if the file exists before attempting to delete
        if os.path.exists(file_path):
            os.remove(file_path)
            return f"File '{filename}.csv' deleted successfully."
        else:
            return f"File '{filename}.csv' not found."

    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
    # app.run(host="127.0.0.1", port=5000, threaded=True)
    app.run(debug=True)
