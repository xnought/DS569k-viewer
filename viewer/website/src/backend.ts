export * from "./openapi";
export { DefaultService as Backend } from "./openapi";
import { OpenAPI } from "./openapi";

// sets url for all Backend.func() calls
OpenAPI.BASE = "http://localhost:4322";
// OpenAPI.BASE = "https://ocular.cc.gatech.edu/DS569k-backend/"; // for deployment
