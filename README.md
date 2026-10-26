# Calculator REST API — End-to-End CI/CD Pipeline

**CSE 816 Software Production Engineering — Mini-Project**

A small Spring Boot Calculator REST API with an automated DevOps pipeline:
**GitHub → Jenkins → Maven build & JUnit tests → Docker image → Docker Hub → Docker Compose deployment (Nginx + 2 API replicas)**.

```
 git push ──► GitHub ──webhook──► Jenkins pipeline (Jenkinsfile)
                                   │
   ┌──────────┬──────────┬─────────┴─────┬───────────┬──────────────────────┐
   │ Checkout │  Build   │     Test      │ Docker    │  Push     │  Deploy  │
   │ git      │ mvnw     │ mvnw test +   │ Build     │ Docker    │ docker   │
   │ checkout │ package  │ JUnit report  │ :BUILD_NO │ Hub       │ compose  │
   └──────────┴──────────┴───────────────┴───────────┴───────────┴────┬─────┘
                                                                      │  email on success / failure
                       ┌──────────────────────────────────────────────▼──┐
   client ──:8090──►   │ nginx (proxy) ──► calculator-1 ┐  calculator-net │
                       │                 └► calculator-2 ┘  (healthchecks)│
                       └─────────────────────────────────────────────────┘
```

## Tech stack

| Area | Tool |
|---|---|
| Application | Java 21, Spring Boot 3.5 (Web + Actuator) |
| Build / tests | Maven (wrapper included), JUnit 5, MockMvc |
| VCS | Git / GitHub |
| CI/CD | Jenkins declarative pipeline (`Jenkinsfile`) |
| Containers | Docker multi-stage build, Docker Hub |
| Deployment | Docker Compose (Nginx reverse proxy + 2 API replicas) |

## API

| Operation | Endpoint | Example response |
|---|---|---|
| Add | `GET /api/v1/add?a=2&b=3` | `{"operation":"add","a":2,"b":3,"result":5}` |
| Subtract | `GET /api/v1/subtract?a=10&b=4` | `{"operation":"subtract","a":10,"b":4,"result":6}` |
| Multiply | `GET /api/v1/multiply?a=6&b=7` | `{"operation":"multiply","a":6,"b":7,"result":42}` |
| Divide | `GET /api/v1/divide?a=10&b=4` | `{"operation":"divide","a":10,"b":4,"result":2.5}` |
| Health | `GET /actuator/health` | `{"status":"UP", ...}` |

Errors return **HTTP 400** with a structured body:

```json
{"timestamp":"2026-10-26T19:32:09Z","status":400,"error":"Bad Request",
 "message":"Division by zero is not allowed","path":"/api/v1/divide"}
```

Handled cases: division by zero, missing parameter (`Missing required parameter 'b'`), and non-numeric input
(`Parameter 'a' must be a valid number but was 'abc'`).
Numbers use `BigDecimal`, so `0.1 + 0.2` returns exactly `0.3`.

## Project structure

```
├── src/main/java/com/spe/calculator/
│   ├── CalculatorApplication.java
│   ├── controller/CalculatorController.java     # REST endpoints
│   ├── service/CalculatorService.java           # arithmetic logic
│   ├── model/                                   # response / error records
│   └── exception/GlobalExceptionHandler.java    # 400 error handling
├── src/test/java/com/spe/calculator/
│   ├── service/CalculatorServiceTest.java       # JUnit 5 unit tests
│   └── controller/CalculatorControllerIntegrationTest.java  # MockMvc tests
├── pom.xml, mvnw, mvnw.cmd, .mvn/               # Maven build + wrapper
├── Dockerfile, .dockerignore                    # multi-stage image
├── docker-compose.yml, nginx/nginx.conf         # deployment stack
├── Jenkinsfile                                  # CI/CD pipeline
└── docs/REPORT.md                               # project report
```

## Build, test and run locally

Prerequisites: JDK 21+ and Docker (with Compose v2). Maven itself is **not** required, because the wrapper downloads it.

```bash
./mvnw clean package          # compile + run tests + build target/calculator-api.jar
./mvnw test                   # tests only; JUnit XML in target/surefire-reports/
java -jar target/calculator-api.jar
curl "http://localhost:8080/api/v1/add?a=2&b=3"
```

On Windows use `mvnw.cmd` instead of `./mvnw`.

### Docker (single container)

```bash
docker build -t calculator-api .
docker run -d -p 8080:8080 --name calc calculator-api
curl "http://localhost:8080/api/v1/divide?a=10&b=4"
```

### Docker Compose (full stack)

```bash
docker compose up -d --build        # 2 API replicas + nginx proxy
docker compose ps                   # all three should be (healthy)
curl "http://localhost:8090/api/v1/multiply?a=6&b=7"
docker compose down
```

Set `PROXY_PORT=xxxx` to use a host port other than 8090.

## Dockerfile highlights

- **Multi-stage**: `maven:3.9-eclipse-temurin-21` builds the JAR, and the runtime is `eclipse-temurin:21-jre-alpine` with only the JAR copied in.
- **Layer caching**: `pom.xml` is copied and `dependency:go-offline` runs before `src/` is copied, so dependencies are re-downloaded only when the POM changes.
- **Security**: runs as a non-root `app` user, and `.dockerignore` keeps `.git`, `.env`, IDE files and `target/` out of the build context.
- Explicit `EXPOSE 8080` and a `HEALTHCHECK` on `/actuator/health`.

## Docker Compose highlights

- `calculator` service with **2 replicas**, an **Nginx** reverse proxy in front, load-balanced through Docker DNS.
- Dedicated bridge network `calculator-net`, and only the proxy publishes a host port.
- Health checks on both services, and the proxy starts only after the API is `service_healthy`.
- `restart: unless-stopped`, plus environment variables (`SERVER_PORT`, `SPRING_PROFILES_ACTIVE`, `JAVA_TOOL_OPTIONS`).
- Fixed project name `calculator`, so re-running `docker compose up -d` from any directory updates the same stack.

## Jenkins setup

1. **Jenkins agent requirements**: Git, JDK 21, Docker and Docker Compose v2. The `jenkins` user must be able to run `docker`, e.g. `sudo usermod -aG docker jenkins` followed by a Jenkins restart.
2. **Plugins**: Pipeline, Git, GitHub, JUnit, Email Extension, Credentials Binding, Timestamper. The "suggested plugins" set covers most of these.
3. **Docker Hub credentials**: create an access token on Docker Hub (Account settings → Personal access tokens). In Jenkins, go to *Manage Jenkins → Credentials → Global → Add*, choose *Username with password*, and set:
   - ID: `dockerhub-creds`
   - Username: your Docker Hub username
   - Password: the access token
4. **Global environment variables**: in *Manage Jenkins → System → Global properties → Environment variables*, add:
   - `DOCKERHUB_USER` = your Docker Hub username
   - `NOTIFY_EMAIL` = the address that receives build emails
5. **Email**: in *Manage Jenkins → System → Extended E-mail Notification*, set SMTP server `smtp.gmail.com`, port `465`, SSL on, and credentials = Gmail address + a Google **App Password**.
6. **Job**: *New Item → Pipeline*. Under *Pipeline → Definition* choose *Pipeline script from SCM*, then Git with this repo's URL, branch `*/main`, and script path `Jenkinsfile`. Tick *GitHub hook trigger for GITScm polling*.
7. **Webhook**: in the GitHub repo go to *Settings → Webhooks → Add webhook* and set:
   - Payload URL: `http://<jenkins-host>:8080/github-webhook/`
   - Content type: `application/json`
   - Event: push

   If Jenkins runs on your laptop, expose it with `ngrok http 8080`. If a webhook isn't possible, replace `githubPush()` in the Jenkinsfile with `pollSCM('H/2 * * * *')`.

### Pipeline stages

| Stage | What it does |
|---|---|
| Checkout | `checkout scm` pulls the commit that triggered the build |
| Build | `./mvnw -B clean package -DskipTests` |
| Test | `./mvnw -B test` and publishes `target/surefire-reports/*.xml` with the `junit` step. A failing test fails the build |
| Docker Build | `docker build -t <user>/calculator-api:<BUILD_NUMBER> -t <user>/calculator-api:latest .` |
| Push | `docker login` using `dockerhub-creds` (token piped via `--password-stdin`), then pushes both tags |
| Deploy | `docker compose up -d --no-build --remove-orphans --wait`, then checks health and an API call through the proxy |
| Post | email on success/failure (log attached on failure), then prune dangling images |

**Idempotency**: `disableConcurrentBuilds()` stops two deploys from racing. `docker compose up -d` only recreates containers whose image changed, and `--wait` fails the stage if the new containers don't become healthy.

## Docker Hub

Image: `https://hub.docker.com/r/<your-dockerhub-username>/calculator-api`

## Security notes

- No credentials are stored in this repository. Docker Hub and SMTP secrets live only in the Jenkins credentials store.
- `.gitignore` excludes `target/`, IDE files, `.env` and key/credential files.
