import { Component } from "@angular/core";
import { FlashService } from "./flash.service";


@Component({
  selector: "flash-message",
  template: `
    <div *ngIf="message[0]" class="alert alert-{{ message[0] }}" role="alert">
      <button (click)="removeMessage()" type="button" class="close" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
      {{ message[1] }}
    </div>
  `,
})
export class FlashComponent {

  public message: {0: string, 1: string} = ["", ""];

  constructor(private flashService: FlashService) {
    this.flashService.messages$.subscribe(
      message => {
        this.removeMessage();
        this.message = message;
      }
    );
  }

  removeMessage() {
    this.message = ["", ""];
  }
}
