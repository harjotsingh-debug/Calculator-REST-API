"""Generates docs/SPE_Mini_Project_Report.pdf.

    pip install reportlab
    python docs/build_report.py

Edit STUDENT / ROLL_NO below, and drop extra screenshots (email.png, dockerhub.png) into
docs/screenshots/; any that exist are added to the appendix automatically.
"""
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, KeepTogether, Paragraph, Preformatted, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

STUDENT = "Harjot Singh"
ROLL_NO = "IMT2023064"
GITHUB_URL = "https://github.com/harjotsingh-debug/Calculator-REST-API"
DOCKERHUB_URL = "https://hub.docker.com/r/harjotsingh12312/calculator-api"

DOCS = Path(__file__).resolve().parent
SHOTS = DOCS / "screenshots"
OUT = DOCS / "SPE_Mini_Project_Report.pdf"

INK = colors.HexColor("#1f2937")
ACCENT = colors.HexColor("#1d4ed8")
MUTED = colors.HexColor("#6b7280")
RULE = colors.HexColor("#d1d5db")
FILL = colors.HexColor("#eff6ff")
CODE_BG = colors.HexColor("#f3f4f6")

ss = getSampleStyleSheet()
TITLE = ParagraphStyle("T", parent=ss["Title"], fontSize=17, leading=21, textColor=INK, spaceAfter=2)
SUB = ParagraphStyle("S", parent=ss["Normal"], fontSize=9.5, leading=13, alignment=TA_CENTER, textColor=MUTED)
H1 = ParagraphStyle("H1", parent=ss["Heading2"], fontSize=12.5, leading=15, textColor=ACCENT, spaceBefore=9, spaceAfter=4)
BODY = ParagraphStyle("B", parent=ss["Normal"], fontSize=9.5, leading=13, textColor=INK, spaceAfter=4)
CELL = ParagraphStyle("C", parent=BODY, fontSize=8.8, leading=11.5, spaceAfter=0)
CELL_B = ParagraphStyle("CB", parent=CELL, fontName="Helvetica-Bold")
BULLET = ParagraphStyle("BL", parent=BODY, leftIndent=12, bulletIndent=2, spaceAfter=2)
CAPTION = ParagraphStyle("Cap", parent=BODY, fontSize=8.5, textColor=MUTED, alignment=TA_CENTER, spaceBefore=3)
CODE = ParagraphStyle("Code", fontName="Courier", fontSize=7.4, leading=9.4, textColor=INK, backColor=CODE_BG,
                      borderPadding=6, leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=8)


def p(text, style=BODY):
    return Paragraph(text, style)


def bullets(items):
    return [Paragraph(i, BULLET, bulletText="•") for i in items]


def table(rows, widths, header=True):
    data = [[p(c, CELL_B if (header and r == 0) or c_i == 0 else CELL) for c_i, c in enumerate(row)]
            for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("GRID", (0, 0), (-1, -1), 0.5, RULE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), FILL))
    t.setStyle(TableStyle(style))
    return t


def arrow(d, x1, y1, x2, y2, color=INK):
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1))
    if x1 == x2:  # vertical
        s = -1 if y2 < y1 else 1
        d.add(Polygon([x2, y2, x2 - 3, y2 - 6 * s, x2 + 3, y2 - 6 * s], fillColor=color, strokeColor=color))
    else:
        s = 1 if x2 > x1 else -1
        d.add(Polygon([x2, y2, x2 - 6 * s, y2 - 3, x2 - 6 * s, y2 + 3], fillColor=color, strokeColor=color))


def box(d, x, y, w, h, label, sub=None, fill=FILL, stroke=ACCENT):
    d.add(Rect(x, y, w, h, rx=4, ry=4, fillColor=fill, strokeColor=stroke, strokeWidth=0.9))
    ty = y + h / 2 + (2 if sub else -3)
    d.add(String(x + w / 2, ty, label, fontName="Helvetica-Bold", fontSize=7.6, fillColor=INK, textAnchor="middle"))
    if sub:
        d.add(String(x + w / 2, y + h / 2 - 8, sub, fontName="Helvetica", fontSize=6.4, fillColor=MUTED,
                     textAnchor="middle"))


def architecture():
    """Pipeline + runtime architecture drawn as vector shapes."""
    W, H = 17 * cm, 7.6 * cm
    d = Drawing(W, H)
    top = H - 34
    box(d, 0, top, 62, 26, "Developer", "git push")
    box(d, 82, top, 72, 26, "GitHub", "repo: main")
    arrow(d, 62, top + 13, 82, top + 13)
    # Jenkins frame
    jx, jy, jw, jh = 172, top - 76, W - 172, 104
    d.add(Rect(jx, jy, jw, jh, rx=6, ry=6, fillColor=colors.white, strokeColor=MUTED, strokeDasharray=[3, 2]))
    d.add(String(jx + 8, jy + jh - 12, "Jenkins (Docker, Configuration as Code) - Jenkinsfile",
                 fontName="Helvetica-Bold", fontSize=7.6, fillColor=INK))
    arrow(d, 154, top + 13, jx, top + 13)
    d.add(String(155, top + 17, "trigger", fontName="Helvetica", fontSize=5.8, fillColor=MUTED))
    stages = [("Checkout", "checkout scm"), ("Build", "mvnw package"), ("Test", "19 JUnit tests"),
              ("Docker Build", "tag :BUILD_NO"), ("Push", "Docker Hub"), ("Deploy", "compose --wait")]
    sw, gap = 52, 6
    sx0 = jx + 10
    sy = jy + jh - 52
    for i, (name, sub) in enumerate(stages):
        x = sx0 + i * (sw + gap)
        box(d, x, sy, sw, 30, name, sub)
        if i:
            arrow(d, x - gap, sy + 15, x, sy + 15)
    # email
    ex = sx0 + 2 * (sw + gap)
    box(d, ex, jy + 8, 2 * sw + gap, 22, "Post: email-ext notification", "success / failure + log",
        fill=colors.HexColor("#fef3c7"), stroke=colors.HexColor("#b45309"))
    # Docker Hub
    push_x = sx0 + 4 * (sw + gap) + sw / 2
    box(d, push_x - 40, 2, 80, 26, "Docker Hub", "user/calculator-api", fill=colors.HexColor("#ecfdf5"),
        stroke=colors.HexColor("#047857"))
    arrow(d, push_x, sy, push_x, 28, colors.HexColor("#047857"))
    # Runtime host
    hx, hy, hw, hh = 0, 2, 258, 96
    d.add(Rect(hx, hy, hw, hh, rx=6, ry=6, fillColor=colors.white, strokeColor=MUTED, strokeDasharray=[3, 2]))
    d.add(String(hx + 8, hy + hh - 12, "Docker host - compose project 'calculator' (calculator-net)",
                 fontName="Helvetica-Bold", fontSize=7.2, fillColor=INK))
    box(d, 8, 30, 58, 30, "Client", "curl :8090", fill=colors.white, stroke=MUTED)
    box(d, 84, 30, 64, 30, "Nginx proxy", "healthcheck")
    box(d, 168, 52, 82, 24, "calculator-1", "Spring Boot :8080")
    box(d, 168, 14, 82, 24, "calculator-2", "Spring Boot :8080")
    arrow(d, 66, 45, 84, 45)
    arrow(d, 148, 50, 168, 64)
    arrow(d, 148, 40, 168, 26)
    deploy_x = sx0 + 5 * (sw + gap) + sw / 2
    d.add(Line(deploy_x, sy, deploy_x, jy - 8, strokeColor=INK, strokeWidth=1))
    d.add(Line(deploy_x, jy - 8, 230, jy - 8, strokeColor=INK, strokeWidth=1))
    arrow(d, 230, jy - 8, 230, hy + hh)
    d.add(String(264, jy - 20, "docker compose up -d", fontName="Helvetica", fontSize=6, fillColor=MUTED))
    return d


def screenshot(path, max_w=17 * cm, max_h=15 * cm):
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(str(path)).getSize()
    scale = min(max_w / iw, max_h / ih)
    return Image(str(path), width=iw * scale, height=ih * scale)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1.2 * cm, f"CSE 816 SPE Mini-Project - {STUDENT}")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


DOCKER_PS = """$ docker ps
NAMES                    IMAGE                               STATUS                  PORTS
calculator-proxy-1       calculator-proxy:latest             Up (healthy)            0.0.0.0:8090->80/tcp
calculator-calculator-2  harjotsingh12312/calculator-api:7   Up (healthy)            8080/tcp
calculator-calculator-1  harjotsingh12312/calculator-api:7   Up (healthy)            8080/tcp
jenkins-jenkins-1        calculator-jenkins:latest           Up                      0.0.0.0:8085->8080/tcp"""

API_CALLS = """$ curl "localhost:8090/api/v1/add?a=2&b=3"
{"operation":"add","a":2,"b":3,"result":5}                                        [HTTP 200]
$ curl "localhost:8090/api/v1/subtract?a=10&b=4"
{"operation":"subtract","a":10,"b":4,"result":6}                                  [HTTP 200]
$ curl "localhost:8090/api/v1/multiply?a=6&b=7"
{"operation":"multiply","a":6,"b":7,"result":42}                                  [HTTP 200]
$ curl "localhost:8090/api/v1/divide?a=10&b=4"
{"operation":"divide","a":10,"b":4,"result":2.5}                                  [HTTP 200]
$ curl "localhost:8090/api/v1/divide?a=1&b=0"
{"timestamp":"2026-10-26T20:10:24.60Z","status":400,"error":"Bad Request",
 "message":"Division by zero is not allowed","path":"/api/v1/divide"}            [HTTP 400]
$ curl "localhost:8090/api/v1/add?a=abc&b=1"
{"timestamp":"2026-10-26T20:10:24.67Z","status":400,"error":"Bad Request",
 "message":"Parameter 'a' must be a valid number but was 'abc'","path":"/api/v1/add"}  [HTTP 400]
$ curl "localhost:8090/actuator/health"
{"status":"UP","groups":["liveness","readiness"]}                                 [HTTP 200]"""

BUILD_7_LOG = """Started by an SCM change
Checking out Revision e80d181 (refs/remotes/origin/main)
[Test]   Tests run: 19, Failures: 0, Errors: 0, Skipped: 0 - BUILD SUCCESS
[Push]   7: digest: sha256:fb29ba45b9fa...  latest: digest: sha256:fb29ba45b9fa...
[Deploy] calculator-calculator-1, calculator-calculator-2, calculator-proxy-1: Healthy
[Deploy] {"status":"UP"}   {"operation":"add","a":2,"b":3,"result":5}
[Post]   Sending email to: jogamerzne658@gmail.com
Finished: SUCCESS"""


def build():
    s = []
    s.append(p("End-to-End CI/CD Pipeline for a Calculator REST API", TITLE))
    s.append(p("CSE 816 Software Production Engineering - Mini-Project Report<br/>"
               "M.Tech (CSE), Term I 2026-27 &nbsp;|&nbsp; Faculty: Prof. B. Thangaraju", SUB))
    s.append(Spacer(1, 8))
    s.append(table([
        ["Student", f"{STUDENT} &nbsp;&nbsp;&nbsp; <b>Roll No.:</b> {ROLL_NO}"],
        ["GitHub repository", f'<link href="{GITHUB_URL}" color="#1d4ed8">{GITHUB_URL}</link>'],
        ["Docker Hub image", f'<link href="{DOCKERHUB_URL}" color="#1d4ed8">{DOCKERHUB_URL}</link>'],
        ["Stack", "Java 21, Spring Boot 3.5, Maven, JUnit 5 / MockMvc, Git/GitHub, Jenkins, Docker, Docker Compose, Nginx"],
    ], [3.6 * cm, 13.4 * cm], header=False))

    s.append(p("1. Overview", H1))
    s.append(p("A Spring Boot Calculator REST API is wrapped in a fully automated pipeline. A push to the <b>main</b> "
               "branch on GitHub triggers Jenkins, which compiles the code, runs the JUnit suite, builds a Docker image "
               "tagged with the build number, pushes it to Docker Hub, redeploys the Docker Compose stack and emails the "
               "result. No manual step is needed between <i>git push</i> and a healthy deployment. This was "
               "demonstrated by build #7, which Jenkins started on its own about 25 seconds after a merge was pushed "
               "and which ended with the new version live behind the proxy."))

    s.append(p("2. Architecture", H1))
    s.append(architecture())
    s.append(p("Figure 1 - Pipeline stages (top) and the deployed runtime (bottom left).", CAPTION))

    s.append(p("3. Application and Tests", H1))
    s.append(table([
        ["Endpoint", "Behaviour"],
        ["GET /api/v1/add | subtract | multiply | divide ?a=&amp;b=",
         'JSON result, e.g. {"operation":"add","a":2,"b":3,"result":5}'],
        ["Errors (HTTP 400)", "Division by zero, missing parameter, non-numeric input. Body: "
                              "{timestamp, status, error, message, path} from a @RestControllerAdvice"],
        ["GET /actuator/health, /actuator/info", "Spring Actuator probe used by Docker / Compose health checks; app version info"],
    ], [6.2 * cm, 10.8 * cm]))
    s.append(Spacer(1, 4))
    s.extend(bullets([
        "Arithmetic uses <b>BigDecimal</b>, so 0.1 + 0.2 returns exactly 0.3. Division is rounded to 16 significant digits.",
        "<b>11 JUnit 5 unit tests</b> (CalculatorServiceTest) cover every operation, negatives, decimals and "
        "divide-by-zero (including 0.0).",
        "<b>8 MockMvc integration tests</b> boot the full Spring context and hit the real endpoints, covering success, "
        "the three 400 cases and the health probe. All 19 run with <i>mvn test</i> and produce Surefire JUnit XML.",
    ]))

    s.append(p("4. Pipeline Stages (Jenkinsfile)", H1))
    s.append(table([
        ["Stage", "What it does"],
        ["Trigger", "githubPush() for a webhook, plus pollSCM('H/2 * * * *') because Jenkins runs on a laptop that "
                    "GitHub cannot reach. disableConcurrentBuilds() prevents racing deploys."],
        ["Checkout", "checkout scm fetches the exact commit that triggered the build."],
        ["Build", "./mvnw -B clean package -DskipTests. The Maven wrapper pins the Maven version, so any agent builds identically."],
        ["Test", "./mvnw -B test. The junit step publishes target/surefire-reports/*.xml (Test Result Trend). "
                 "A failing test exits non-zero and fails the build before an image is produced."],
        ["Docker Build", "docker build -t &lt;user&gt;/calculator-api:$BUILD_NUMBER -t ...:latest, plus "
                         "docker compose build proxy for the Nginx image."],
        ["Push", "withCredentials(usernamePassword 'dockerhub-creds'). The token comes from the Jenkins credentials "
                 "store and is passed with --password-stdin, so it never appears in the log or the repo. Pushes both tags."],
        ["Deploy", "docker compose up -d --no-build --remove-orphans --wait. This is idempotent: only changed containers "
                   "are recreated, and --wait fails the stage unless every service is healthy. A smoke test then calls "
                   "/actuator/health and /api/v1/add through the proxy."],
        ["Post", "emailext sends a success or failure mail (failure attaches the console log) via Gmail SMTP with an "
                 "App Password stored as a credential, then prunes dangling images."],
    ], [2.6 * cm, 14.4 * cm]))

    s.append(p("5. Containerisation and Deployment", H1))
    s.extend(bullets([
        "<b>Multi-stage Dockerfile:</b> maven:3.9.11-eclipse-temurin-21 builds the JAR, and the runtime is "
        "eclipse-temurin:21-jre-alpine with only the JAR copied in. pom.xml is copied and dependency:go-offline runs "
        "before src/, so the dependency layer stays cached. The image runs as a non-root <i>app</i> user with an "
        "explicit EXPOSE 8080 and a HEALTHCHECK, and a .dockerignore keeps .git, target/ and secrets out of the "
        "build context. A single <i>docker run -p 8080:8080</i> serves the API.",
        "<b>docker-compose.yml:</b> two <i>calculator</i> replicas behind an <i>Nginx</i> reverse proxy on the "
        "bridge network calculator-net. Both services have health checks (/actuator/health), and the proxy "
        "starts only after the API is service_healthy. Restart policy is unless-stopped, and environment variables "
        "set SERVER_PORT, SPRING_PROFILES_ACTIVE, JAVA_TOOL_OPTIONS and the image tag. Only the proxy publishes a "
        "host port (8090). Nginx resolves the replicas through Docker DNS (127.0.0.11) at request time, so "
        "redeployed containers are picked up.",
        "<b>Jenkins as code:</b> jenkins/ holds a Jenkins image with the Docker CLI and Compose, the plugins, and a "
        "Configuration-as-Code file. That file creates the admin user, credentials, global variables, SMTP settings "
        "and the pipeline job, with secrets read from a git-ignored .env file.",
    ]))

    s.append(p("6. Version Control Practices", H1))
    s.append(p("The history has 17 commits, built up incrementally from scaffold to service, API, Docker, Compose, "
               "Jenkins and docs. Four feature branches (feature/docker, feature/jenkins-pipeline, "
               "feature/jenkins-docker, feature/actuator-info) were merged into main with --no-ff merge commits. "
               "The .gitignore covers target/, IDE files, .env and key/credential files. No credentials exist in "
               "the repository, and all secrets live in the Jenkins credentials store."))

    s.append(p("7. Challenges Faced", H1))
    s.extend(bullets([
        "<b>Deploying from a containerised Jenkins:</b> Compose resolves bind-mount paths on the Docker host, not "
        "inside the Jenkins container, so mounting nginx.conf from the workspace failed. The config is now "
        "baked into a small proxy image built by the pipeline.",
        "<b>Docker socket permissions:</b> the jenkins user could not use /var/run/docker.sock (root:root, 660). "
        "This was solved with group_add: 0 in Jenkins' compose file.",
        "<b>Proxy health check unhealthy:</b> inside Alpine, <i>localhost</i> resolved to IPv6 ::1 while Nginx "
        "listened on IPv4 only. Probing 127.0.0.1 fixed it.",
        "<b>Failure e-mail crashed:</b> email-ext's attachLog needs the matrix-project plugin, which was missing. "
        "A test run that failed on purpose exposed this, and the plugin was added to plugins.txt.",
        "<b>Early red builds (#3-#5 in the Stage View):</b> Jenkins was first validated against a local checkout "
        "with placeholder Docker Hub credentials, so Push failed with <i>unauthorized</i> and Deploy was skipped, "
        "as intended. Builds #1-#2 failed at checkout because of git's safe.directory ownership check on the "
        "mounted repo. After the real token was configured, #6 and #7 passed end to end.",
        "<b>Host port conflicts:</b> 8080 and 8081 were already used by other local services, so Jenkins uses "
        "8085 and the proxy port is configurable (PROXY_PORT, default 8090).",
        "<b>Number formatting:</b> after removing trailing zeros, BigDecimal 10 serialised as 1E+1. Jackson's "
        "write-bigdecimal-as-plain fixed this.",
    ]))

    # ---------- Appendix: evidence ----------
    s.append(p("Appendix - Screenshots and Evidence", H1))
    s.append(KeepTogether([p("A1 - Console highlights of build #7 (auto-triggered by a push)", CELL_B),
                           Preformatted(BUILD_7_LOG, CODE)]))
    s.append(KeepTogether([p("A2 - Running containers after deployment", CELL_B), Preformatted(DOCKER_PS, CODE)]))
    s.append(KeepTogether([p("A3 - Sample API responses through the Nginx proxy", CELL_B),
                           Preformatted(API_CALLS, CODE)]))
    stage = SHOTS / "jenkins-stage-view.png"
    if stage.exists():
        s.append(KeepTogether([screenshot(stage, max_h=14.5 * cm),
                               p("A4 - Jenkins job: Test Result Trend (19 passing) and Stage View. Builds #6 and #7 "
                                 "are green across all stages, and #7 was triggered automatically by a push "
                                 "(\"1 commit\").", CAPTION)]))
    extra = [("email.png", "A5 - Build notification e-mail"),
             ("dockerhub.png", "A6 - Docker Hub repository with build-number tags"),
             ("docker-ps.png", "A7 - docker ps"),
             ("api-responses.png", "A8 - API responses")]
    for name, caption in extra:
        f = SHOTS / name
        if f.exists():
            s.append(KeepTogether([screenshot(f, max_h=11 * cm), p(caption, CAPTION)]))

    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.6 * cm,
                            bottomMargin=1.8 * cm, title="CI/CD Pipeline for a Calculator REST API",
                            author=STUDENT, subject="CSE 816 SPE Mini-Project Report")
    doc.build(s, onFirstPage=footer, onLaterPages=footer)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    build()
