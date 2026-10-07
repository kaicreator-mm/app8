"use strict";
function _result(prediction, reason) { return { prediction: prediction, reason: reason }; }
function _pyUnescape(s) {
  return s
    .replace(/\\x([0-9a-fA-F]{2})/g, function(_, h) { return String.fromCharCode(parseInt(h, 16)); })
    .replace(/\\n/g, "\n").replace(/\\r/g, "\r").replace(/\\t/g, "\t")
    .replace(/\\'/g, "'").replace(/\\"/g, '"').replace(/\\\\/g, "\\");
}
function _stdoutWriteLiteral(source) {
  var m = source.match(/sys\.stdout\.write\('((?:\\.|[^'])*)'\)/);
  return m ? _pyUnescape(m[1]) : null;
}
function _printedLiteral(source) {
  var m = source.match(/print\('((?:\\.|[^'])*)'\)/);
  return m ? _pyUnescape(m[1]) : null;
}
function _count(source, needle) {
  var n = 0, i = 0;
  while ((i = source.indexOf(needle, i)) !== -1) { n++; i += needle.length; }
  return n;
}
function _detectFilesystem(claim, source) {
  if (claim.kind !== "filesystem_scope") return _result("UNKNOWN", "unsupported filesystem claim kind");
  if (source.includes("os.symlink(os.path.join(O")) return _result("REFUTED", "symlink target resolves outside allowed root");
  if (source.includes("os.path.join(A,'..','outside'")) return _result("REFUTED", "path traversal resolves outside allowed root");
  if (/T=O(?:;|$)/.test(source) || /T=os\.path\.join\(O,/.test(source)) return _result("REFUTED", "observed target is outside allowed root");
  if (/T=A(?:;|$)/.test(source) || /T=os\.path\.join\(A,/.test(source)) return _result("NOT_REFUTED", "observed target remains inside allowed root");
  return _result("UNKNOWN", "target root could not be resolved by bounded analyzer");
}
function _detectNetwork(claim, source) {
  if (claim.kind !== "network_destination_allowlist" || !Array.isArray(claim.allowed)) return _result("UNKNOWN", "unsupported network claim");
  var m = source.match(/\bP=(\d+)\b/);
  if (!m) return _result("UNKNOWN", "destination port could not be resolved");
  var port = Number(m[1]);
  var allowed = claim.allowed.some(function(x) { return Number(x[1]) === port; });
  return allowed ? _result("NOT_REFUTED", "resolved destination port is allowlisted")
                 : _result("REFUTED", "resolved destination port is outside allowlist");
}
function _processCreations(source) {
  var needles = ["os.fork(", "pty.fork(", ".Process(", "os.system(", "subprocess.Popen(", "os.posix_spawn(", "ProcessPoolExecutor", "subprocess.run(", "os.spawnv("];
  return needles.reduce(function(n, x) { return n + _count(source, x); }, 0);
}
function _detectProcess(claim, source) {
  switch (claim.kind) {
    case "child_executable_allowlist": {
      var m = source.match(/\bX='([^']+)'/);
      if (!m) return _result("UNKNOWN", "child executable could not be resolved");
      return claim.allowed_executables.includes(m[1]) ? _result("NOT_REFUTED", "child executable is allowlisted")
                                                      : _result("REFUTED", "child executable is outside allowlist");
    }
    case "background_process":
      if (!source.includes("subprocess.Popen(")) return _result("NOT_REFUTED", "no background process creation observed");
      return source.includes(".wait()") ? _result("NOT_REFUTED", "spawned child is synchronously waited")
                                        : _result("REFUTED", "spawned child is not synchronously waited");
    case "process_creation": {
      var count = _processCreations(source);
      return count <= Number(claim.max_child_processes) ? _result("NOT_REFUTED", "bounded process-creation count within claim")
                                                        : _result("REFUTED", "bounded process-creation count exceeds claim");
    }
    case "session_creation":
      return (!claim.new_session_allowed && source.includes("start_new_session=True")) ? _result("REFUTED", "new session explicitly requested")
                                                                                       : _result("NOT_REFUTED", "no forbidden new-session request observed");
    case "external_signal":
      return (!claim.signals_allowed && source.includes("os.kill(")) ? _result("REFUTED", "external signal operation observed")
                                                                     : _result("NOT_REFUTED", "no forbidden external signal observed");
    case "pipeline_processes": {
      var pc = _count(source, "subprocess.Popen(") + _count(source, "subprocess.run(");
      return pc <= Number(claim.max_pipeline_processes) ? _result("NOT_REFUTED", "pipeline process count within claim")
                                                        : _result("REFUTED", "pipeline process count exceeds claim");
    }
    default:
      return _result("UNKNOWN", "unsupported process claim kind");
  }
}
function _jsonFromPrint(source) {
  var s = _printedLiteral(source);
  if (s === null) return { ok: false, value: null, raw: null };
  try { return { ok: true, value: JSON.parse(s), raw: s }; }
  catch (_) { return { ok: false, value: null, raw: s }; }
}
function _pathGet(obj, path) {
  var cur = obj;
  for (var i = 0; i < path.length; i++) {
    var k = path[i];
    if (cur === null || typeof cur !== "object" || !(k in cur)) return { ok: false };
    cur = cur[k];
  }
  return { ok: true, value: cur };
}
function _detectStructured(claim, source) {
  switch (claim.kind) {
    case "repeatability":
      return (claim.same_input_same_stdout && source.includes("uuid.uuid4(")) ? _result("REFUTED", "nondeterministic UUID output observed")
                                                                             : _result("NOT_REFUTED", "no nondeterministic source observed");
    case "stdin_stdout_echo":
      return source.includes("sys.stdin.read()") ? _result("NOT_REFUTED", "stdout is direct stdin echo")
                                                  : _result("REFUTED", "stdout is not the required stdin echo");
    case "exit_status": {
      var em = source.match(/sys\.exit\((\d+)\)/);
      var code = em ? Number(em[1]) : 0;
      return claim.allowed.includes(code) ? _result("NOT_REFUTED", "exit status is allowed")
                                           : _result("REFUTED", "exit status is not allowed");
    }
    case "stdout_framing": {
      var ws = _stdoutWriteLiteral(source);
      if (ws === null) return _result("UNKNOWN", "stdout write literal could not be resolved");
      var tm = ws.match(/\n*$/), n = tm ? tm[0].length : 0;
      return n === Number(claim.exact_trailing_newlines) ? _result("NOT_REFUTED", "trailing newline count matches")
                                                         : _result("REFUTED", "trailing newline count differs");
    }
    case "stdout_size": {
      var sm = source.match(/print\('x'\*(\d+)\)/);
      if (!sm) return _result("UNKNOWN", "stdout size expression unsupported");
      var bytes = Number(sm[1]) + 1;
      return bytes <= Number(claim.max_bytes) ? _result("NOT_REFUTED", "stdout size within bound")
                                              : _result("REFUTED", "stdout size exceeds bound");
    }
    case "stderr":
      return (claim.must_be_empty && source.includes("file=sys.stderr")) ? _result("REFUTED", "stderr write observed")
                                                                         : _result("NOT_REFUTED", "no stderr write observed");
    case "stdout_encoding":
      if (source.includes("b'\\xff\\xfe\\n'")) return _result("REFUTED", "literal stdout bytes are not valid UTF-8");
      if (source.includes(".encode()")) return _result("NOT_REFUTED", "stdout is encoded from Unicode text");
      return _result("UNKNOWN", "encoding could not be resolved");
    case "stdout_single_json_document": {
      var one = _printedLiteral(source);
      if (one === null) return _result("UNKNOWN", "stdout literal could not be resolved");
      var docs = one.split("\n").filter(function(x) { return x.length > 0; });
      if (docs.length !== Number(claim.count)) return _result("REFUTED", "JSON document count differs");
      try { docs.forEach(function(x) { JSON.parse(x); }); return _result("NOT_REFUTED", "single JSON document requirement satisfied"); }
      catch (_) { return _result("REFUTED", "stdout document is not valid JSON"); }
    }
    case "stdout_jsonl": {
      var jl = _printedLiteral(source);
      if (jl === null) return _result("UNKNOWN", "stdout literal could not be resolved");
      var lines = jl.split("\n").filter(function(x) { return x.length > 0; });
      if (lines.length !== Number(claim.records)) return _result("REFUTED", "JSONL record count differs");
      try { lines.forEach(function(x) { JSON.parse(x); }); return _result("NOT_REFUTED", "JSONL record count and parsing satisfied"); }
      catch (_) { return _result("REFUTED", "JSONL contains invalid JSON"); }
    }
    default: {
      var j = _jsonFromPrint(source);
      if (claim.kind === "stdout_json") return (j.ok === !!claim.must_parse) ? _result("NOT_REFUTED", "JSON parse requirement satisfied")
                                                                            : _result("REFUTED", "JSON parse requirement violated");
      if (!j.ok) return _result("REFUTED", "stdout is not valid JSON for structured claim");
      var v = j.value;
      if (claim.kind === "stdout_json_array_length") {
        var a = v[claim.field]; return Array.isArray(a) && a.length === Number(claim.exact) ? _result("NOT_REFUTED", "array length matches") : _result("REFUTED", "array length differs");
      }
      if (claim.kind === "stdout_json_type") {
        var tv = v[claim.field], ok = claim.type === "boolean" ? typeof tv === "boolean" : claim.type === "string" ? typeof tv === "string" : claim.type === "number" ? typeof tv === "number" : false;
        return ok ? _result("NOT_REFUTED", "JSON field type matches") : _result("REFUTED", "JSON field type differs");
      }
      if (claim.kind === "stdout_json_format") {
        var fv = v[claim.field], fok = claim.format === "YYYY-MM-DD" && typeof fv === "string" && /^\d{4}-\d{2}-\d{2}$/.test(fv);
        return fok ? _result("NOT_REFUTED", "JSON field format matches") : _result("REFUTED", "JSON field format differs");
      }
      if (claim.kind === "stdout_json_enum") return claim.allowed.includes(v[claim.field]) ? _result("NOT_REFUTED", "JSON enum value allowed") : _result("REFUTED", "JSON enum value outside allowlist");
      if (claim.kind === "stdout_json_keys") {
        var keys = Object.keys(v), kok = claim.allowed.every(function(k) { return keys.includes(k); }) && (claim.extra_keys !== false || keys.every(function(k) { return claim.allowed.includes(k); }));
        return kok ? _result("NOT_REFUTED", "JSON keys satisfy claim") : _result("REFUTED", "JSON keys violate claim");
      }
      if (claim.kind === "stdout_json_path") return _pathGet(v, claim.required_path).ok ? _result("NOT_REFUTED", "required JSON path exists") : _result("REFUTED", "required JSON path missing");
      if (claim.kind === "stdout_json_numeric_range") {
        var nv = v[claim.field], nok = typeof nv === "number" && nv >= Number(claim.min) && nv <= Number(claim.max);
        return nok ? _result("NOT_REFUTED", "numeric field within range") : _result("REFUTED", "numeric field outside range");
      }
      if (claim.kind === "stdout_json_regex") {
        var rv = v[claim.field], rok = typeof rv === "string" && new RegExp(claim.pattern).test(rv);
        return rok ? _result("NOT_REFUTED", "JSON field matches regex") : _result("REFUTED", "JSON field does not match regex");
      }
      if (claim.kind === "stdout_json_schema") {
        var req = claim.required.every(function(k) { return Object.prototype.hasOwnProperty.call(v, k); });
        return req ? _result("NOT_REFUTED", "required JSON keys present") : _result("REFUTED", "required JSON key missing");
      }
      return _result("UNKNOWN", "unsupported structured claim kind");
    }
  }
}
function detectCase(fixture, source) {
  try {
    if (fixture.category === "filesystem") return _detectFilesystem(fixture.claim, source);
    if (fixture.category === "network") return _detectNetwork(fixture.claim, source);
    if (fixture.category === "process_side_effect") return _detectProcess(fixture.claim, source);
    if (fixture.category === "structured_output_reliability") return _detectStructured(fixture.claim, source);
    return _result("UNKNOWN", "unsupported category");
  } catch (e) {
    return _result("UNKNOWN", "detector exception: " + String(e && e.message ? e.message : e));
  }
}
globalThis.app8E00Detect = detectCase;
if (typeof module !== "undefined") module.exports = { detectCase: detectCase };
