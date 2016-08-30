import { Injectable } from "@angular/core";
import { URLSearchParams, Response } from "@angular/http";
import { Observable } from "rxjs/Observable";
import { ConfigService } from "../config.service";
import { HttpClient } from "../http-client";

import "rxjs/add/operator/catch";
import "rxjs/add/operator/map";


@Injectable()
export class UsagesReportService {

  private url: string = ConfigService.get("usagesReportAPIUrl");

  constructor(
    private http: HttpClient
  ) { }

  getTypes(): Observable<JSON> {
    let url: string = ConfigService.get("usageTypeAPIUrl");
    return this.http.get(url).map(this.extractSingleData).catch(
      this.handleError
    );
  }

  getCSV(params: URLSearchParams): Observable<Response> {
    return this.http.get(this.url, params).catch(this.handleError);
  }

  private extractSingleData(res: Response) {
    if (res.status < 200 || res.status >= 300) {
        throw new Error("Bad response status: " + res.status);
    }
    let body = res.json();
    return body || {};
  }

  private handleError(response: any) {
    if (response.status === 400 || response.status === 412) {
      return Observable.throw(JSON.parse(response._body));
    }
    let errMsg = response.message || "Server error";
    console.error(errMsg);
    return Observable.throw(errMsg);
  }
}
