export * from "./openapi";
export { DefaultService as Backend } from "./openapi";
import { OpenAPI } from "./openapi";

OpenAPI.BASE = "http://localhost:4322"; // sets url for all Backend.func() calls
