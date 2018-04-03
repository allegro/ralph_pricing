import { Injectable } from "@angular/core";
import { URLSearchParams, Response } from "@angular/http";
import { Observable } from "rxjs/Observable";
import { ConfigService } from "../config.service";
import { HttpClient } from "../http-client";

import "rxjs/add/operator/catch";
import "rxjs/add/operator/map";


@Injectable()
export class MonthlyCostsService {

  private url: string = ConfigService.get("monhtlyCostsAPIUrl");

  constructor(
    private http: HttpClient
  ) { }

  recalculate(params: Object): Observable<JSON> {
    return this.http.post(this.url, JSON.stringify(params)).map(
      this.extractSingleData
    ).catch(
      this.handleError
    );
  }

  getJobInfo(jobId: string) {
    let url: string = `${this.url}${jobId}`;
    return this.http.get(url).map(this.extractSingleData).catch(
      this.handleError
    );
  }

  acceptCosts(params: Object): Observable<JSON> {
    let url: string = ConfigService.get("acceptMonhtyCostsAPIUrl");
    return this.http.post(url, JSON.stringify(params)).map(
      this.extractSingleData
    ).catch(
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
