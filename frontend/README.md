# OrbitApp

This project was generated using [Angular CLI](https://github.com/angular/angular-cli) version 21.0.4.

## Development server

To start a local development server, run:

```bash
ng serve
```

Once the server is running, open your browser and navigate to `http://localhost:4200/`. The application will automatically reload whenever you modify any of the source files.

## Code scaffolding

Angular CLI includes powerful code scaffolding tools. To generate a new component, run:

```bash
ng generate component component-name
```

For a complete list of available schematics (such as `components`, `directives`, or `pipes`), run:

```bash
ng generate --help
```

## Building

To build the project run:

```bash
ng build
```

This will compile your project and store the build artifacts in the `dist/` directory. By default, the production build optimizes your application for performance and speed.

## Running unit tests

To execute unit tests with the [Vitest](https://vitest.dev/) test runner, use the following command:

```bash
ng test
```

## Running end-to-end tests

For end-to-end (e2e) testing, run:

```bash
ng e2e
```

Angular CLI does not come with an end-to-end testing framework by default. You can choose one that suits your needs.

## Using proxy.conf.json for API Requests

Angular's development server can proxy API requests to a backend server using a proxy configuration file. This is useful to avoid CORS issues and to simplify API calls during development.

### Location
The proxy configuration file for this project is located at `src/proxy.conf.json`.

### Example Configuration
```json
{
  "/api": {
    "target": "http://localhost:5000",
    "secure": false,
    "pathRewrite": {
      "^/api": "/api/v1"
    },
    "changeOrigin": true,
    "logLevel": "debug"
  }
}
```

### How to Use
To enable the proxy, run the Angular development server with the `--proxy-config` option:

```bash
ng serve --proxy-config src/proxy.conf.json
```

This will forward any requests from your Angular app to `/api/*` to the backend server at `http://localhost:5000/api/v1/*`.

### Why Use a Proxy?
- Avoids CORS issues during development
- Allows you to use relative API paths in your frontend code
- Supports path rewriting and origin changes

For more details, see the [Angular CLI Proxy documentation](https://angular.io/guide/build#proxying-to-a-backend-server).

## Additional Resources

For more information on using the Angular CLI, including detailed command references, visit the [Angular CLI Overview and Command Reference](https://angular.dev/tools/cli) page.
