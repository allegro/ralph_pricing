import { Injectable } from "@angular/core";
import {
  Http,
  Headers,
  URLSearchParams,
  Response,
  RequestOptionsArgs
} from "@angular/http";
import { Observable } from "rxjs/Observable";
import { CookieService } from "./cookie.service";


@Injectable()
export class HttpClient {

  constructor(
    private http: Http,
    private cookieService: CookieService
  ) { }

  getHeaders(): Headers {
    let headers: Headers = new Headers();
    headers.append("Content-Type", "application/json");
    headers.append("X-CSRFToken", this.cookieService.getCookie("csrftoken"));
    return headers;
  }

  get(url: string, params?: URLSearchParams): Observable<Response>  {
    return this.http.get(url, {
      search: params,
      headers: this.getHeaders()
    });
  }

  delete(url: string): Observable<Response>  {
    return this.http.delete(url, {
      headers: this.getHeaders()
    });
  }

  options(url: string): Observable<Response>  {
    let requestOptions: RequestOptionsArgs = {
      method: "OPTIONS",
      url: url,
      headers: this.getHeaders()
    };
    return this.http.request(url, requestOptions);
  }

  post(url: string, data: string): Observable<Response> {
    return this.http.post(url, data, {
      headers: this.getHeaders()
    });
  }

  patch(url: string, data: string): Observable<Response> {
    return this.http.patch(url, data, {
      headers: this.getHeaders()
    });
  }
}
