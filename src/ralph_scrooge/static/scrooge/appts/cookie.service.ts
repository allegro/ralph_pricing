import { Injectable } from "@angular/core";


@Injectable()
export class CookieService {

    public getCookie(name: string) {
        let allCookie: Array<string> = document.cookie.split(";");
        let allCookieLength: number = allCookie.length;
        let cookieName = name + "=";
        let c: string;

        for (let i: number = 0; i < allCookieLength; i += 1) {
            c = allCookie[i].replace(/^\s\+/g, "");
            c = c.trim();
            if (c.indexOf(cookieName) === 0) {
                return c.substring(cookieName.length, c.length);
            }
        }
        return "";
    }

    public deleteCookie(name) {
        this.setCookie(name, "", -1);
    }

    public setCookie(
      name: string, value: string, expireDays: number, path: string = ""
    ) {
        let currentdate: Date = new Date();
        currentdate.setTime(currentdate.getTime() + expireDays * 24 * 60 * 60 * 1000);
        let expires: string = "expires=" + currentdate.toUTCString();
        document.cookie = name + "=" + value + "; " + expires + (path.length > 0 ? "; path=" + path : "");
    }
}
