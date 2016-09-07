import { Component, AfterViewInit, ViewChild } from "@angular/core";
import { FORM_DIRECTIVES } from "@angular/common";
import { URLSearchParams, Response, HTTP_PROVIDERS } from "@angular/http";
import { ConfigService } from "../config.service";
import { HorizontalCalendarComponent } from "../horizontal-calendar/horizontal-calendar.component";
import { FlashService } from "../flash/flash.service";
import { FlashComponent } from "../flash/flash.component";
import { ReportService } from "../report.service";
import "rxjs/add/observable/throw";

declare var $: any;


@Component({
  templateUrl: ConfigService.get("usages-report.component.template"),
  providers: [HTTP_PROVIDERS, ReportService],
  directives: [FORM_DIRECTIVES, HorizontalCalendarComponent, FlashComponent],
})
export class UsagesReportComponent implements AfterViewInit {

  @ViewChild("startDatePicker") startDatePicker;
  @ViewChild("endDatePicker") endDatePicker;

  private apiErrorCounter: number = 0;
  private maxApiErrorCounter: number = 10;
  private refreshTimeOut: number = 5000;
  public dates: {[key: string]: string} = {startdDate: "", endDate: ""};
  public selectTypes: string[] = [];
  public types: Array<{0: number; 1: string}> = [];
  public showSpinner: boolean = false;
  public progress: string = "";

  constructor(
    private reportService: ReportService,
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

    this.reportService.getTypes().subscribe(
      json => {
        this.types = [];
        for (let item in json) {
          let type: any = json[item];
          this.types.push([type["id"], type["name"]]);
        }
      }
    );
  }

  onNotify(event: Event) {
    if (String(event) === "dateUpdate") {
      $(this.startDatePicker.nativeElement).datepicker("update", this.dates["startDate"]);
      $(this.endDatePicker.nativeElement).datepicker("update", this.dates["endDate"]);
    }
  }

  setSelectedType(event: any) {
    this.selectTypes = [];
    for (let i in event.target.selectedOptions) {
      if (event.target.selectedOptions[i].label) {
        this.selectTypes.push(event.target.selectedOptions[i].value);
      }
    }
  }

  getCSVFile() {
    let params: URLSearchParams = new URLSearchParams();
    params.set("start", $(this.startDatePicker.nativeElement).val());
    params.set("end", $(this.endDatePicker.nativeElement).val());
    for (let item of this.selectTypes) {
      params.append("usage_types", String(item));
    }
    let url: string = ConfigService.get("usagesReportAPIUrl");
    this.showSpinner = true;
    this.reportService.getCSV(url, params).subscribe(
      (json) => {
        this.progress = `${json["progress"]}%`;
        if (json["finished"]) {
          params.set("report_format", "csv");
          let url: string = `${ConfigService.get("usagesReportAPIUrl")}/?${params.toString()}`;
          this.flashService.addMessage(
            ["success", "File generated."]
          );
          window.location.href = url;
        } else {
          setTimeout(() => this.getCSVFile(), this.refreshTimeOut);
        }
        this.showSpinner = false;
      },
      (error) => {
          this.apiErrorCounter++;
          if (this.apiErrorCounter < this.maxApiErrorCounter) {
            setTimeout(() => this.getCSVFile(), this.refreshTimeOut);
          } else {
            this.flashService.addMessage(
              ["danger", ConfigService.get("serverErrorMessage")]
            );
          }
          this.showSpinner = false;
        }
    );
  }

  onClickDownload() {
    this.flashService.addMessage(
      ["info", "Please wait for report file."]
    );
    this.progress = "0%";
    this.getCSVFile();
  }
}
