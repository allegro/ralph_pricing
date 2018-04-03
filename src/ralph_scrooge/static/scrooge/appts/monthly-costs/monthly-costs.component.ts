import { Component, AfterViewInit, ViewChild } from "@angular/core";
import { FORM_DIRECTIVES } from "@angular/common";
import { URLSearchParams, Response, HTTP_PROVIDERS } from "@angular/http";
import { ConfigService } from "../config.service";
import { HorizontalCalendarComponent } from "../horizontal-calendar/horizontal-calendar.component";
import { MonthlyCostsService } from "./monthly-costs.service";
import { FlashService } from "../flash/flash.service";
import { FlashComponent } from "../flash/flash.component";
import { daysInMonth } from "../utils";
import "rxjs/add/observable/throw";

declare var $: any;


@Component({
  templateUrl: ConfigService.get("monthly-cost.component.template"),
  providers: [HTTP_PROVIDERS, MonthlyCostsService],
  directives: [FORM_DIRECTIVES, HorizontalCalendarComponent, FlashComponent],
  styles: [".red { color:red;.green { color: green; }"]
})
export class MonthlyCostsComponent implements AfterViewInit {

  @ViewChild("startDatePicker") startDatePicker;
  @ViewChild("endDatePicker") endDatePicker;

  private apiErrorCounter: number = 0;
  private maxApiErrorCounter: number = 10;
  private refreshTimeOut: number = 5000;
  public dates: {[key: string]: string} = {startdDate: "", endDate: ""};
  public forecast: boolean;
  public results: Array<{0: string; 1: string}> = [];
  public showSpinner: boolean = false;
  public progress: string = "";
  public activeErrorItem: string = "";

  constructor(
    private monthlyCostsService: MonthlyCostsService,
    private flashService: FlashService
  ) {}

  ngAfterViewInit() {
    let dateParams: Object = {
      format: "yyyy-mm-dd",
      orientation: "top center",
      autoclose: true
    };
    $(this.startDatePicker.nativeElement).datepicker(dateParams);
    $(this.endDatePicker.nativeElement).datepicker(dateParams);
  }

  onNotify(event: Event) {
    if (String(event) === "dateUpdate") {
      $(this.startDatePicker.nativeElement).datepicker("update", this.dates["startDate"]);
      $(this.endDatePicker.nativeElement).datepicker("update", this.dates["endDate"]);
    }
  }

  checkJob(jobId: string) {
    if (jobId) {
      this.showSpinner = true;
      this.monthlyCostsService.getJobInfo(jobId).subscribe(
        (json) => {
          this.progress = `${json["progress"]}%`;
          if (json["status"] === "finished" && json["data"]) {
            this.results = json["data"];
            this.flashService.addMessage(
              ["success", "Costs recalculated."]
            );
          } else if (json["status"] === "failed") {
            this.flashService.addMessage(
              ["danger", "Recalculate failed."]
            );
          } else {
            this.results = json["data"];
            setTimeout(() => this.checkJob(jobId), this.refreshTimeOut);
          }
          this.showSpinner = false;
        },
        (error) => {
          this.apiErrorCounter++;
          if (this.apiErrorCounter < this.maxApiErrorCounter) {
            setTimeout(() => this.checkJob(jobId), this.refreshTimeOut);
          } else {
            this.flashService.addMessage(
              ["danger", ConfigService.get("serverErrorMessage")]
            );
          }
          this.showSpinner = false;
        }
      );
    }
  }

  getParams(): Object {
    return {
      start: $(this.startDatePicker.nativeElement).val(),
      end: $(this.endDatePicker.nativeElement).val(),
      forecast: this.forecast ? 1 : 0
    };
  }

  onClickRecalculate() {
    let params: Object = this.getParams();
    this.progress = "0%";
    this.monthlyCostsService.recalculate(params).subscribe(
      json => {
        this.results = [];
        this.flashService.addMessage(["info", json["message"]]);
        setTimeout(() => this.checkJob(json["job_id"]), this.refreshTimeOut);
      },
      error => {
        if (error.hasOwnProperty("message")) {
          this.flashService.addMessage(
            ["danger", error["message"]]
          );
        }
      }
    );
  }

  onClickAcceptCosts() {
    if (confirm("Are you sure you want accept costs?")) {
      let params: Object = this.getParams();
      this.monthlyCostsService.acceptCosts(params).subscribe(
        (json) => {
          this.flashService.addMessage(["info", json["message"]]);
        }
      );
    }
  }

  icon(value?: boolean): string {
    if (value === true) {
      return "fa-check-circle green";
    } else if (value === false) {
      return "fa-times-circle red";
    }
    return "fa-question-circle";
  }

  showDataErrors(date: string) {
    if (date === this.activeErrorItem) {
      this.activeErrorItem = "";
    } else {
      this.activeErrorItem = date;
    }
  }
}
