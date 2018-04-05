import { enableProdMode, ExceptionHandler, provide } from "@angular/core";
import { bootstrap } from "@angular/platform-browser-dynamic";
import { HTTP_PROVIDERS } from "@angular/http";
import { ROUTER_PROVIDERS } from "@angular/router-deprecated";
import { Location, LocationStrategy, HashLocationStrategy } from "@angular/common";

import { AppComponent } from "./app.component";
import { ConfigService } from "./config.service";
import { CustomExceptionHandler } from "./exception-handler";
import { HttpClient } from "./http-client";
import { CookieService } from "./cookie.service";
import { FlashService } from "./flash/flash.service";


if (!ConfigService.get("debug")) {
  enableProdMode();
}


bootstrap(AppComponent, [
  ROUTER_PROVIDERS,
  HTTP_PROVIDERS,
  provide(ExceptionHandler, {useClass: CustomExceptionHandler}),
  provide(LocationStrategy, { useClass: HashLocationStrategy }),
  provide(HttpClient, { useClass: HttpClient  }),
  provide(CookieService, { useClass: CookieService }),
  provide(FlashService, { useClass: FlashService }),
  provide(ConfigService, { useClass: ConfigService })
]);
