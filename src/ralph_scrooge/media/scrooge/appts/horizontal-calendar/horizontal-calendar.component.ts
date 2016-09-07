import { Component, OnInit, Input, Output, EventEmitter } from "@angular/core";
import { FORM_DIRECTIVES } from "@angular/common";
import { HTTP_PROVIDERS } from "@angular/http";
import { ConfigService } from "../config.service";
import { daysInMonth } from "../utils";


@Component({
  selector: "horizontal-calendar",
  templateUrl: ConfigService.get("horizontal-calendar.component.template"),
  providers: [HTTP_PROVIDERS],
  directives: [FORM_DIRECTIVES],
  styles: [".padding { padding-bottom:5px; }"]
})
export class HorizontalCalendarComponent implements OnInit {

  @Input("dates") dates: {[key: string]: string};
  @Output() notify: EventEmitter<string> = new EventEmitter<string>();

  public startYear: number = 2011;
  public years: Array<number> = [];
  public months: Array<{0: number, 1: string}> = [];
  private monthNames: Array<String> = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
  ];
  public activeYear: number = this.startYear;
  public activeMonth: number = 1;

  ngOnInit() {
    this.years = [];
    let currentDate: Date = new Date();
    for (let i: number = this.startYear; i <= currentDate.getFullYear(); i++) {
      this.years.push(i);
    }

    this.months = [];
    for (let i: number = 0; i < 12; i++) {
      this.months.push([i + 1, String(this.monthNames[i])]);
    }

    let monthDays: Array<number> = daysInMonth(currentDate.getFullYear());
    this.dates["startDate"] = `${currentDate.getFullYear()}-${currentDate.getMonth() + 1}-${1}`;
    this.dates["endDate"] =  `${currentDate.getFullYear()}-${currentDate.getMonth() + 1}-${monthDays[currentDate.getMonth()]}`;
    this.activeMonth = currentDate.getMonth()  + 1;
    this.activeYear = currentDate.getFullYear();
  }

  onClickYear(year: number) {
    this.activeYear = year;
    this.setDates();
  }

  onClickMonth(month: number) {
    this.activeMonth = month;
    this.setDates();
  }

  private setDates() {
    let monthDays: Array<number> = daysInMonth(this.activeYear);
    this.dates["startDate"] = `${this.activeYear}-${this.activeMonth}-${1}`;
    this.dates["endDate"] =  `${this.activeYear}-${this.activeMonth}-${monthDays[this.activeMonth - 1]}`;
    this.notify.emit("dateUpdate");
  }
}
