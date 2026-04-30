// Main entry point for the Angular application.
// This file manually bootstraps the AppComponent. In a full Angular project
// created via the Angular CLI, this file would be auto-generated.
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent).catch((err) => console.error(err));
