# CI/CD Pipeline for a Calculator REST API — Project Report

**Course:** CSE 816 Software Production Engineering (M.Tech CSE, Term I 2026-27)
**Student:** _<Name>_ · _<Roll No.>_
**GitHub:** _<repo URL>_ · **Docker Hub:** _<image URL>_

---

## 1. Overview

The project builds a Spring Boot Calculator REST API and wraps it in a fully automated CI/CD pipeline.
A `git push` to GitHub triggers Jenkins through a webhook. Jenkins compiles and tests the code, builds a Docker image tagged with the build number, pushes it to Docker Hub and deploys it with Docker Compose. It then emails the build result. No manual steps are needed between commit and deployment.

## 2. Architecture

```
Developer ──git push──► GitHub repo ──webhook──► Jenkins
                                                  │
  Checkout ► Build (mvnw package) ► Test (JUnit + report) ► Docker Build (:N)
           ► Push (Docker Hub, credentials store) ► Deploy (docker compose up --wait)
                                                  │
                                    Email notification (success / failure)
                                                  │
              Docker host:  nginx proxy :8090 ──► calculator replica 1
                             (calculator-net)  └─► calculator replica 2
```

_(Replace with a drawn diagram, e.g. from draw.io, for the PDF.)_

## 3. Application

- **Endpoints:** `/api/v1/{add,subtract,multiply,divide}?a=&b=` return JSON like `{"operation":"add","a":2,"b":3,"result":5}`. `/actuator/health` is the health probe.
- **Validation:** a global `@RestControllerAdvice` returns HTTP 400 with `{timestamp,status,error,message,path}` for division by zero, a missing parameter or non-numeric input.
- **Precision:** `BigDecimal` arithmetic, so 0.1 + 0.2 = 0.3 exactly. Division is rounded to 16 significant digits.
- **Tests:** 11 JUnit 5 unit tests for the service, covering every operation, negatives, decimals and divide-by-zero. There are also 8 MockMvc integration tests that boot the full Spring context and hit the real endpoints, including error and health cases.

## 4. Pipeline stages

| Stage | Description |
|---|---|
| **Checkout** | `checkout scm` fetches the exact commit that triggered the webhook. |
| **Build** | `./mvnw -B clean package -DskipTests` compiles the code and produces the executable JAR. The Maven wrapper pins the Maven version, so the build is reproducible on any agent. |
| **Test** | `./mvnw -B test` runs all 19 tests. The `junit` step publishes the Surefire XML reports with trend graphs. Any failure makes Maven exit non-zero, which fails the build and stops it before an image is built. |
| **Docker Build** | Builds the multi-stage image, tagged `<user>/calculator-api:<BUILD_NUMBER>` and `:latest`. |
| **Push** | `withCredentials` injects the Docker Hub token from the Jenkins credentials store. Login uses `--password-stdin`, so the token never appears in the log or in the repo. |
| **Deploy** | `docker compose up -d --no-build --remove-orphans --wait` rolls out the new tag and blocks until every container is healthy. A smoke test then calls `/actuator/health` and `/api/v1/add` through the Nginx proxy. |
| **Post** | `emailext` sends a success or failure email (failure attaches the console log), then dangling images are pruned. |

**Idempotency:** `disableConcurrentBuilds()` prevents parallel deploys, and Compose only recreates containers whose image or config changed. Because of the fixed Compose project name, re-runs update the same stack instead of creating a new one.

## 5. Containerization and deployment

- **Dockerfile:** build stage `maven:3.9-eclipse-temurin-21` and runtime stage `eclipse-temurin:21-jre-alpine`. The POM is copied first with `dependency:go-offline` so dependencies are cached as a layer. The image runs as a non-root user, has an explicit `EXPOSE 8080` and a `HEALTHCHECK`, and uses a `.dockerignore`.
- **Compose:** 2 `calculator` replicas plus an `nginx` reverse proxy on the bridge network `calculator-net`. Both services have health checks, and the proxy waits for the API to be `service_healthy`. Restart policy is `unless-stopped`, and settings come from environment variables. Only the proxy is published on the host, at port 8090.

## 6. Challenges faced

1. **Host port conflict:** port 8081 was already used by another local stack, so the proxy port was made configurable (`PROXY_PORT`, default 8090).
2. **Proxy health check failing:** inside Alpine, `localhost` resolved to IPv6 `::1`, but Nginx listened only on IPv4. Probing `127.0.0.1` fixed it.
3. **Nginx and replicas:** Nginx normally resolves upstream hostnames once at startup, so after a redeploy it kept stale container IPs. Using Docker's DNS resolver (`127.0.0.11`) with a variable in `proxy_pass` makes it re-resolve.
4. **BigDecimal output:** after removing trailing zeros, 10 was serialized as `1E+1`. Enabling Jackson's `write-bigdecimal-as-plain` fixed this.
5. _<Add your own, e.g. Jenkins needing access to the Docker socket, exposing Jenkins to GitHub with ngrok, or a Gmail App Password for SMTP.>_

## 7. Screenshots

_(Insert in the PDF.)_
1. Green Jenkins pipeline run (Stage View)
2. JUnit test result trend in Jenkins
3. Email notification received
4. `docker compose ps` / `docker ps` showing 3 healthy containers
5. Sample API responses (add, divide, divide-by-zero 400)
6. Docker Hub repository showing build-number tags
