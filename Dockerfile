# syntax=docker/dockerfile:1

# ---------- Stage 1: build the JAR with Maven + full JDK ----------
FROM maven:3.9.11-eclipse-temurin-21 AS build
WORKDIR /workspace

# Copy only the POM first so the dependency layer is cached until pom.xml changes
COPY pom.xml .
RUN mvn -B -q dependency:go-offline

COPY src ./src
# Tests run in the Jenkins "Test" stage, so skip them here to keep image builds fast
RUN mvn -B -q package -DskipTests

# ---------- Stage 2: slim runtime with only the JRE ----------
FROM eclipse-temurin:21-jre-alpine

LABEL org.opencontainers.image.title="calculator-api" \
      org.opencontainers.image.description="Calculator REST API (CSE 816 SPE mini-project)"

# Run as an unprivileged user, never as root
RUN addgroup -S app && adduser -S app -G app
WORKDIR /app

COPY --from=build --chown=app:app /workspace/target/calculator-api.jar app.jar

USER app
EXPOSE 8080

# Lets a plain "docker run" report health too (Compose overrides with the same check)
HEALTHCHECK --interval=15s --timeout=3s --start-period=30s --retries=3 \
    CMD wget -qO- http://localhost:8080/actuator/health | grep -q '"status":"UP"' || exit 1

ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75.0", "-jar", "/app/app.jar"]
