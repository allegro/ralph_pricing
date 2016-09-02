import { Injectable } from "@angular/core";
import { URLSearchParams, Response } from "@angular/http";
import { Observable } from "rxjs/Observable";
import { HttpClient } from "./http-client";
import { ConfigService } from "./config.service";

import "rxjs/add/operator/catch";
import "rxjs/add/operator/map";

@Injectable()
export class ReportService{

  constructor(
    private http: HttpClient
  ) { }

  getCSV(url: string, params: URLSearchParams): Observable<JSON> {
    return this.http.get(url, params).map(
      this.extractSingleData
    ).catch(this.handleError);
  }

  getTypes(): Observable<JSON> {
    let url: string = ConfigService.get("usageTypeAPIUrl");
    return this.http.get(url).map(this.extractSingleData).catch(
      this.handleError
    );
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
