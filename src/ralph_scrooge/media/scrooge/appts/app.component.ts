import { Component, OnInit, ViewChild } from "@angular/core";
import { Location } from "@angular/common";
import { ROUTER_DIRECTIVES, Route, Router, RouteConfig } from "@angular/router-deprecated";
import { ConfigService } from "./config.service";
import { HttpClient } from "./http-client";
import { MonthlyCostsComponent } from "./monthly-costs/monthly-costs.component";


@Component({
  selector: "scrooge-app",
  templateUrl: ConfigService.get("app.component.template"),
  directives: [ROUTER_DIRECTIVES]
})
 @RouteConfig([
  { path: "/monthly-costs", name: "MonhtlyCosts", component: MonthlyCostsComponent },
])
export class AppComponent implements OnInit {

  public changelogUrl: string;
  public bugtrackerUrl: string;
  public username: string;
  public logoutUrl: string;
  public subMenus: Array<{0: string, 1: string}> = [];

  constructor(
    private router: Router,
    private location: Location,
    private http: HttpClient
  ) { }

  ngOnInit() {
    this.changelogUrl = ConfigService.get("changelogUrl");
    this.bugtrackerUrl = ConfigService.get("bugtrackerUrl");
    this.username = ConfigService.get("username");
    this.logoutUrl = ConfigService.get("logoutUrl");

    if (this.location.path().length === 0) {
      this.router.navigate(["MonhtlyCosts"]);
    }
    this.http.get(ConfigService.get("subMenuUrl")).subscribe(
      (response) => {
        let menus = response.json();
        for (let item in menus) {
          if (menus[item].hasOwnProperty("href")) {
            this.subMenus.push([menus[item]["href"], menus[item]["name"]]);
          }
        }
      }
    );
  }
}
