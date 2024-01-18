import pandas as pd
from datetime import datetime, timedelta


class EmployeeAnalyzer:

    #Constructor to set default values
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        self.consecutive_days = []
        self.prev_shift_end = None
        self.processed_names = set()

    #Function to convert time in hours
    def time_to_hours(self, time_str):
        if pd.notnull(time_str):
            parts = time_str.split(":")
            if len(parts) == 2:
                hours = int(parts[0])
                minutes = int(parts[1])
                return hours + minutes / 60
        return None

    #Function to accept csv file, process it and write output to a text file.
    def analyze(self, output_file="output.txt"):
        with open(output_file, "w") as output:
            for index, row in self.df.iterrows():
                if row.isnull().all():  # Skip empty rows
                    continue

                #Parsing parameters the csv file
                employee_name = row["Employee Name"].strip()
                position = row["Position ID"].strip()
                time_in = (
                    datetime.strptime(row["Time"], "%m/%d/%Y %I:%M %p")
                    if pd.notnull(row["Time"])
                    else None
                )
                time_out = (
                    datetime.strptime(row["Time Out"], "%m/%d/%Y %I:%M %p")
                    if pd.notnull(row["Time Out"])
                    else None
                )
                timecard_hours = self.time_to_hours(row["Timecard Hours (as Time)"])

                # Check for 7 consecutive days
                pay_cycle_start_date = row["Pay Cycle Start Date"]
                if pd.notnull(pay_cycle_start_date):
                    current_date = datetime.strptime(
                        pay_cycle_start_date, "%m/%d/%Y"
                    ).date()
                    if (
                        self.consecutive_days
                        and self.consecutive_days[-1] == current_date
                    ):
                        self.consecutive_days.append(current_date)
                    else:
                        self.consecutive_days = [current_date]

                    if (
                        len(self.consecutive_days) == 7
                        and employee_name not in self.processed_names
                    ):
                        output.write(
                            f"{employee_name} ({position}) worked for 7 consecutive days.\n"
                        )
                        self.processed_names.add(employee_name)

                # Check for less than 10 hours between shifts but greater than 1 hour
                if self.prev_shift_end and time_in:
                    hours_between_shifts = (
                        time_in - self.prev_shift_end
                    ).total_seconds() / 3600
                    if (
                        1 < hours_between_shifts < 10
                        and employee_name not in self.processed_names
                    ):
                        output.write(
                            f"{employee_name} ({position}) has less than 10 hours between shifts but greater than 1 hour.\n"
                        )
                        self.processed_names.add(employee_name)

                self.prev_shift_end = time_out

                # Check for more than 14 hours in a single shift
                if (
                    timecard_hours is not None
                    and timecard_hours > 14
                    and employee_name not in self.processed_names
                ):
                    output.write(
                        f"{employee_name} ({position}) worked for more than 14 hours in a single shift.\n"
                    )
                    self.processed_names.add(employee_name)


if __name__ == "__main__":
    analyzer = EmployeeAnalyzer("Assignment_Timecard.xlsx - Sheet1.csv")
    analyzer.analyze(output_file="output.txt")
