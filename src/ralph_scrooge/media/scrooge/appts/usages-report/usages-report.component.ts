import { Component, AfterViewInit, ViewChild } from "@angular/core";
import { FORM_DIRECTIVES } from "@angular/common";
import { URLSearchParams, Response, HTTP_PROVIDERS } from "@angular/http";
import { ConfigService } from "../config.service";
import { HorizontalCalendarComponent } from "../horizontal-calendar/horizontal-calendar.component";
import { FlashService } from "../flash/flash.service";
import { FlashComponent } from "../flash/flash.component";
import { UsagesReportService } from "../usages-report/usages-report.service";
import "rxjs/add/observable/throw";

declare var $: any;


@Component({
  templateUrl: ConfigService.get("usages-report.component.template"),
  providers: [HTTP_PROVIDERS, UsagesReportService],
  directives: [FORM_DIRECTIVES, HorizontalCalendarComponent, FlashComponent],
})
export class UsagesReportComponent implements AfterViewInit {

  private refreshTimeOut: number = 2000;
  public dates: {[key: string]: string} = {startdDate: "", endDate: ""};
  public onlyActive: boolean = false;
  public selectTypes: string[] = [];
  public types: Array<{0: number; 1: string}> = [];
  @ViewChild("startDatePicker") startDatePicker;
  @ViewChild("endDatePicker") endDatePicker;

  constructor(
    private usagesReportService: UsagesReportService,
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
    this.usagesReportService.getTypes().subscribe(
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
    for (var i in event.target.selectedOptions){
      if (event.target.selectedOptions[i].label){
        this.selectTypes.push(event.target.selectedOptions[i].value);
      }
    }
  }

  onClickDownload() {
    // TODO ? only active?
    let params: URLSearchParams = new URLSearchParams();
    params.set("start", $(this.startDatePicker.nativeElement).val());
    params.set("end", $(this.endDatePicker.nativeElement).val());
    params.set("report_format", "csv");
    for (let item of this.selectTypes) {
      params.append("usage_types", String(item));
    }
    this.usagesReportService.getCSV(params).subscribe(
      response => {
        if (response.headers.get("Content-Type") === "application/csv") {
          let url: string = `${ConfigService.get("usagesReportAPIUrl")}/?${params.toString()}`;
            window.location.href = url;
        } else {
          setTimeout(() => this.onClickDownload(), this.refreshTimeOut);
        }
      }
    );
  }
}
