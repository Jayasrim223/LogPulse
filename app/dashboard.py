import streamlit as st
import pandas as pd
import re
import ast
import json
import zipfile
import tempfile
import subprocess
import shutil
from pathlib import Path


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="LogPulse",
    page_icon="📊",
    layout="wide"
)

st.title("📊 LogPulse")
st.caption("Server Log Analytics + Multi-Language Error Detection")


# =========================================================
# LANGUAGE DETECTION
# =========================================================

LANGUAGES = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript JSX",
    ".ts": "TypeScript",
    ".tsx": "TypeScript JSX",
    ".java": "Java",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".go": "Go",
    ".php": "PHP",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".sql": "SQL",
    ".json": "JSON",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".sh": "Shell",
    ".bash": "Shell",
    ".md": "Markdown",
    ".txt": "Text"
}


SUPPORTED_CODE_EXTENSIONS = set(LANGUAGES.keys())


# =========================================================
# COMMON ERROR HELPERS
# =========================================================

def make_error(
    file_name,
    language,
    error_type,
    message,
    line_number=None,
    source_line=None
):
    return {
        "file": file_name,
        "language": language,
        "error_type": error_type,
        "message": message,
        "line": line_number,
        "source": source_line
    }


def get_line(source, line_number):
    if not line_number:
        return None

    lines = source.splitlines()

    if 1 <= line_number <= len(lines):
        return lines[line_number - 1]

    return None


# =========================================================
# BRACKET CHECK
# =========================================================

def check_brackets(source, file_name, language):

    errors = []

    pairs = {
        ")": "(",
        "]": "[",
        "}": "{"
    }

    opening = set(pairs.values())

    stack = []

    in_single = False
    in_double = False
    in_backtick = False

    escape = False

    line_number = 1

    for char in source:

        if char == "\n":
            line_number += 1

        if escape:
            escape = False
            continue

        if char == "\\":
            escape = True
            continue

        if char == "'" and not in_double and not in_backtick:
            in_single = not in_single
            continue

        if char == '"' and not in_single and not in_backtick:
            in_double = not in_double
            continue

        if char == "`" and not in_single and not in_double:
            in_backtick = not in_backtick
            continue

        if in_single or in_double or in_backtick:
            continue

        if char in opening:
            stack.append((char, line_number))

        elif char in pairs:

            if not stack:

                errors.append(
                    make_error(
                        file_name,
                        language,
                        "Syntax Error",
                        f"Unexpected closing '{char}'.",
                        line_number
                    )
                )

            elif stack[-1][0] != pairs[char]:

                errors.append(
                    make_error(
                        file_name,
                        language,
                        "Syntax Error",
                        f"Mismatched bracket '{char}'.",
                        line_number
                    )
                )

                stack.pop()

            else:
                stack.pop()

    if in_single or in_double or in_backtick:

        errors.append(
            make_error(
                file_name,
                language,
                "Syntax Error",
                "Unterminated string.",
                line_number
            )
        )

    for bracket, line in reversed(stack):

        errors.append(
            make_error(
                file_name,
                language,
                "Syntax Error",
                f"Unclosed '{bracket}'.",
                line
            )
        )

    return errors


# =========================================================
# PYTHON CHECKER
# =========================================================

def check_python(source, file_name):

    errors = []

    try:

        ast.parse(source)

    except SyntaxError as e:

        errors.append(
            make_error(
                file_name,
                "Python",
                "Syntax Error",
                e.msg,
                e.lineno,
                get_line(source, e.lineno)
            )
        )

    return errors


# =========================================================
# JSON CHECKER
# =========================================================

def check_json(source, file_name):

    errors = []

    try:

        json.loads(source)

    except json.JSONDecodeError as e:

        errors.append(
            make_error(
                file_name,
                "JSON",
                "Syntax Error",
                e.msg,
                e.lineno,
                get_line(source, e.lineno)
            )
        )

    return errors


# =========================================================
# HTML CHECKER
# =========================================================

def check_html(source, file_name):

    errors = []

    stack = []

    pattern = re.compile(
        r"<\s*(/?)\s*([A-Za-z][A-Za-z0-9-]*)[^>]*>"
    )

    self_closing = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr"
    }

    for match in pattern.finditer(source):

        closing = match.group(1)
        tag = match.group(2).lower()

        line_number = source[:match.start()].count("\n") + 1

        if tag in self_closing:
            continue

        if closing:

            if not stack:

                errors.append(
                    make_error(
                        file_name,
                        "HTML",
                        "HTML Error",
                        f"Unexpected closing tag </{tag}>.",
                        line_number
                    )
                )

            elif stack[-1][0] != tag:

                errors.append(
                    make_error(
                        file_name,
                        "HTML",
                        "HTML Error",
                        f"Expected </{stack[-1][0]}> but found </{tag}>.",
                        line_number
                    )
                )

            else:

                stack.pop()

        else:

            stack.append((tag, line_number))

    for tag, line_number in reversed(stack):

        errors.append(
            make_error(
                file_name,
                "HTML",
                "HTML Error",
                f"Unclosed <{tag}> tag.",
                line_number
            )
        )

    return errors


# =========================================================
# XML CHECKER
# =========================================================

def check_xml(source, file_name):

    errors = []

    try:

        import xml.etree.ElementTree as ET

        ET.fromstring(source)

    except Exception as e:

        errors.append(
            make_error(
                file_name,
                "XML",
                "Syntax Error",
                str(e)
            )
        )

    return errors


# =========================================================
# CSS CHECKER
# =========================================================

def check_css(source, file_name):

    errors = []

    errors.extend(
        check_brackets(
            source,
            file_name,
            "CSS"
        )
    )

    return errors


# =========================================================
# JAVASCRIPT / TYPESCRIPT CHECKER
# =========================================================

def check_javascript(source, file_name, extension):

    errors = []

    language = LANGUAGES.get(extension, "JavaScript")

    # First perform general bracket checking.
    errors.extend(
        check_brackets(
            source,
            file_name,
            language
        )
    )

    # JSX / TSX cannot reliably be checked by Node --check.
    if extension in [".jsx", ".tsx", ".ts"]:
        return errors

    # Try Node.js if installed.
    node_path = shutil.which("node")

    if node_path:

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=extension,
            delete=False,
            encoding="utf-8"
        ) as temp:

            temp.write(source)
            temp_path = temp.name

        try:

            result = subprocess.run(
                [
                    node_path,
                    "--check",
                    temp_path
                ],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:

                message = (
                    result.stderr.strip()
                    or result.stdout.strip()
                    or "JavaScript syntax error."
                )

                line_number = None

                match = re.search(
                    r":(\d+)",
                    message
                )

                if match:
                    line_number = int(match.group(1))

                errors.append(
                    make_error(
                        file_name,
                        language,
                        "Syntax Error",
                        message,
                        line_number,
                        get_line(source, line_number)
                    )
                )

        finally:

            Path(temp_path).unlink(
                missing_ok=True
            )

    return errors


# =========================================================
# JAVA CHECKER
# =========================================================

def check_java(source, file_name):

    errors = []

    errors.extend(
        check_brackets(
            source,
            file_name,
            "Java"
        )
    )

    javac = shutil.which("javac")

    if not javac:
        return errors

    temp_dir = tempfile.mkdtemp()

    try:

        java_file = Path(temp_dir) / Path(file_name).name

        java_file.write_text(
            source,
            encoding="utf-8"
        )

        result = subprocess.run(
            [
                javac,
                str(java_file)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            message = (
                result.stderr.strip()
                or result.stdout.strip()
            )

            match = re.search(
                r":(\d+):",
                message
            )

            line_number = (
                int(match.group(1))
                if match
                else None
            )

            errors.append(
                make_error(
                    file_name,
                    "Java",
                    "Compile Error",
                    message,
                    line_number,
                    get_line(source, line_number)
                )
            )

    finally:

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )

    return errors


# =========================================================
# PHP CHECKER
# =========================================================

def check_php(source, file_name):

    errors = []

    php = shutil.which("php")

    if php:

        temp_dir = tempfile.mkdtemp()

        try:

            php_file = Path(temp_dir) / Path(file_name).name

            php_file.write_text(
                source,
                encoding="utf-8"
            )

            result = subprocess.run(
                [
                    php,
                    "-l",
                    str(php_file)
                ],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:

                message = (
                    result.stdout.strip()
                    or result.stderr.strip()
                )

                match = re.search(
                    r"on line (\d+)",
                    message
                )

                line_number = (
                    int(match.group(1))
                    if match
                    else None
                )

                errors.append(
                    make_error(
                        file_name,
                        "PHP",
                        "Syntax Error",
                        message,
                        line_number,
                        get_line(source, line_number)
                    )
                )

        finally:

            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )

    else:

        errors.extend(
            check_brackets(
                source,
                file_name,
                "PHP"
            )
        )

    return errors


# =========================================================
# GO CHECKER
# =========================================================

def check_go(source, file_name):

    errors = []

    errors.extend(
        check_brackets(
            source,
            file_name,
            "Go"
        )
    )

    gofmt = shutil.which("gofmt")

    if gofmt:

        temp_dir = tempfile.mkdtemp()

        try:

            go_file = Path(temp_dir) / Path(file_name).name

            go_file.write_text(
                source,
                encoding="utf-8"
            )

            result = subprocess.run(
                [
                    gofmt,
                    "-e",
                    str(go_file)
                ],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:

                errors.append(
                    make_error(
                        file_name,
                        "Go",
                        "Syntax Error",
                        result.stderr.strip()
                        or result.stdout.strip()
                    )
                )

        finally:

            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )

    return errors


# =========================================================
# GENERIC CODE CHECKER
# =========================================================

def check_code_file(source, file_name):

    extension = Path(file_name).suffix.lower()

    language = LANGUAGES.get(
        extension,
        "Unknown"
    )

    if extension == ".py":
        return check_python(
            source,
            file_name
        )

    if extension == ".json":
        return check_json(
            source,
            file_name
        )

    if extension in [".html", ".htm"]:
        return check_html(
            source,
            file_name
        )

    if extension == ".xml":
        return check_xml(
            source,
            file_name
        )

    if extension == ".css":
        return check_css(
            source,
            file_name
        )

    if extension in [
        ".js",
        ".jsx",
        ".ts",
        ".tsx"
    ]:
        return check_javascript(
            source,
            file_name,
            extension
        )

    if extension == ".java":
        return check_java(
            source,
            file_name
        )

    if extension == ".php":
        return check_php(
            source,
            file_name
        )

    if extension == ".go":
        return check_go(
            source,
            file_name
        )

    if extension in [
        ".c",
        ".h",
        ".cpp",
        ".cc",
        ".cxx",
        ".hpp",
        ".cs",
        ".sql",
        ".sh",
        ".bash",
        ".yaml",
        ".yml"
    ]:

        return check_brackets(
            source,
            file_name,
            language
        )

    return []


# =========================================================
# DISPLAY ERRORS
# =========================================================

def display_errors(errors):

    if not errors:

        st.success(
            "✅ No syntax/structural errors detected."
        )

        return

    st.error(
        f"❌ {len(errors)} error(s) detected."
    )

    for index, error in enumerate(errors, 1):

        line_text = ""

        if error["line"]:
            line_text = f"Line {error['line']}"

        with st.expander(
            f"❌ {index}. {error['file']} — {error['error_type']} {line_text}"
        ):

            st.write(
                f"**Language:** {error['language']}"
            )

            st.write(
                f"**Message:** {error['message']}"
            )

            if error["line"]:
                st.write(
                    f"**Line:** {error['line']}"
                )

            if error["source"]:
                st.code(
                    error["source"],
                    language="text"
                )


# =========================================================
# 1. SERVER LOG ANALYTICS
# =========================================================

st.header("1️⃣ Server Log Analytics")

server_log_file = st.file_uploader(
    "Upload your server log file (.log or .txt)",
    type=["log", "txt"],
    key="server_log_upload"
)

if server_log_file is not None:

    log_text = server_log_file.getvalue().decode(
        "utf-8",
        errors="ignore"
    )

    st.success(
        f"Uploaded: {server_log_file.name}"
    )

else:

    default_log = Path("demo_server.log")

    if default_log.exists():

        log_text = default_log.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        st.info(
            "Demo Mode: using demo_server.log"
        )

    else:

        log_text = ""


LOG_PATTERN = re.compile(
    r"\[(.*?)\]\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)"
)


if log_text:

    records = []

    for line in log_text.splitlines():

        match = LOG_PATTERN.search(line)

        if match:

            timestamp, ip, method, endpoint, status = match.groups()

            records.append(
                {
                    "timestamp": timestamp,
                    "ip": ip,
                    "method": method,
                    "endpoint": endpoint,
                    "status": int(status)
                }
            )

    if records:

        df = pd.DataFrame(records)

        total = len(df)

        successful = len(
            df[df["status"] == 200]
        )

        failed = total - successful

        success_rate = (
            successful / total * 100
        )

        error_rate = (
            failed / total * 100
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Requests",
            total
        )

        col2.metric(
            "Successful",
            successful
        )

        col3.metric(
            "Failed",
            failed
        )

        col4.metric(
            "Success Rate",
            f"{success_rate:.2f}%"
        )

        st.subheader("📊 Endpoint Usage")

        endpoint_counts = (
            df["endpoint"]
            .value_counts()
        )

        st.bar_chart(
            endpoint_counts
        )

        st.subheader("📌 Status Codes")

        status_counts = (
            df["status"]
            .value_counts()
            .sort_index()
        )

        st.bar_chart(
            status_counts
        )

        st.subheader("📋 Log Data")

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.warning(
            "No valid server-log entries were found."
        )


# =========================================================
# 2. PROJECT ERROR DETECTION
# =========================================================

st.divider()

st.header("2️⃣ Project Error Detection")

st.write(
    "Upload a ZIP project or select an entire project folder."
)

project_files = st.file_uploader(
    "Upload project ZIP OR project folder",
    type=None,
    accept_multiple_files="directory",
    key="project_upload"
)

project_zip = None

# Separate ZIP uploader because directory mode does not handle ZIP
project_zip = st.file_uploader(
    "Or upload Project ZIP",
    type=["zip"],
    key="project_zip_upload"
)


def scan_project_folder(project_path):

    all_errors = []
    scanned_files = []

    for file_path in project_path.rglob("*"):

        if not file_path.is_file():
            continue

        extension = file_path.suffix.lower()

        if extension not in SUPPORTED_CODE_EXTENSIONS:
            continue

        try:

            source = file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            relative_name = str(
                file_path.relative_to(project_path)
            )

            scanned_files.append(
                relative_name
            )

            errors = check_code_file(
                source,
                relative_name
            )

            all_errors.extend(
                errors
            )

        except Exception as e:

            all_errors.append(
                make_error(
                    str(file_path),
                    "Unknown",
                    "File Error",
                    str(e)
                )
            )

    return scanned_files, all_errors


if project_zip is not None:

    temp_dir = tempfile.mkdtemp()

    try:

        with zipfile.ZipFile(
            project_zip,
            "r"
        ) as zip_ref:

            zip_ref.extractall(
                temp_dir
            )

        project_path = Path(temp_dir)

        st.success(
            f"Project ZIP extracted: {project_zip.name}"
        )

        scanned_files, project_errors = scan_project_folder(
            project_path
        )

        st.subheader(
            f"📁 Scanned Files: {len(scanned_files)}"
        )

        if scanned_files:

            st.write(
                "\n".join(
                    f"• {file}"
                    for file in scanned_files
                )
            )

        st.subheader("🔍 Error Detection")

        display_errors(
            project_errors
        )

    finally:

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )


elif project_files:

    temp_dir = tempfile.mkdtemp()

    try:

        project_path = Path(temp_dir)

        for uploaded in project_files:

            relative_path = Path(
                uploaded.name
            )

            destination = (
                project_path /
                relative_path
            )

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            destination.write_bytes(
                uploaded.getvalue()
            )

        st.success(
            f"Project folder received: {len(project_files)} files"
        )

        scanned_files, project_errors = scan_project_folder(
            project_path
        )

        st.subheader(
            f"📁 Scanned Files: {len(scanned_files)}"
        )

        if scanned_files:

            st.write(
                "\n".join(
                    f"• {file}"
                    for file in scanned_files
                )
            )

        st.subheader("🔍 Error Detection")

        display_errors(
            project_errors
        )

    finally:

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )


# =========================================================
# 3. SINGLE FILE ERROR DETECTION
# =========================================================

st.divider()

st.header("3️⃣ Single File Error Detection")

st.write(
    "Upload one code/text file. Log files are handled by the Server Log section above."
)

single_file = st.file_uploader(
    "Upload a single code file",
    type=[
        "py",
        "js",
        "jsx",
        "ts",
        "tsx",
        "java",
        "c",
        "h",
        "cpp",
        "cc",
        "cxx",
        "hpp",
        "cs",
        "go",
        "php",
        "html",
        "htm",
        "css",
        "sql",
        "json",
        "xml",
        "yaml",
        "yml",
        "sh",
        "bash",
        "md",
        "txt"
    ],
    key="single_file_upload"
)


if single_file is not None:

    file_name = single_file.name

    extension = Path(
        file_name
    ).suffix.lower()

    language = LANGUAGES.get(
        extension,
        "Unknown"
    )

    source = single_file.getvalue().decode(
        "utf-8",
        errors="ignore"
    )

    st.success(
        f"File uploaded: {file_name}"
    )

    st.write(
        f"**Detected language:** {language}"
    )

    with st.expander("👀 View File"):

        st.code(
            source,
            language="text"
        )

    st.subheader(
        "🔍 Error Detection Result"
    )

    errors = check_code_file(
        source,
        file_name
    )

    display_errors(
        errors
    )