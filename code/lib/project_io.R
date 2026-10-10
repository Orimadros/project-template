# Small, explicit input registration and per-output run records.
#
# Usage:
#   source("code/lib/project_io.R")
#   INPUTS <- "data/raw/*.csv"  # paths live in the script, not CLI arguments
#   OUTPUT <- "results/panel.csv"
#   with_run_record(script = "code/02_analyze/01_make_panel.R",
#                   outputs = OUTPUT, code = function(run) {
#     input_paths <- run$input_file(INPUTS)  # always character vector
#     # Read input_paths with ordinary readers, then write OUTPUT.
#   })
#
# An input declaration may name one file, a directory, or a filename glob in
# one explicitly named directory. Directories and globs expand to sorted,
# immediate regular files only. The helper does not walk subdirectories,
# read file contents, or hash them. Patterns support * and ? in the filename;
# wildcards in directory components are rejected. File modification times are
# read with file.info() before paths are returned.
#
# Each declared output receives an adjacent <output>.run.tsv sidecar in the
# common project-io-run-v1 format used by Python and Julia. A run first removes
# old success records and writes status=running, then records success on normal
# return or failed before rethrowing an error. Paths inside this repository are
# stored relative to its root; external paths remain absolute. Input times are
# Unix seconds with full observed floating-point precision. These records cover
# only inputs explicitly registered through this helper.
#
# TSV rows are format, status, script, started_at, completed_at, repeated
# input<TAB>path<TAB>mtime rows, output<TAB>path rows, and an optional error
# row. Path/error values percent-escape %, tab, LF, and CR as %25, %09, %0A,
# and %0D. Shipping may append production_output<TAB>path without changing
# the original run facts.
#
# Declared outputs must be regular files. Before writing status=success, the
# helper checks that each file exists and its modification time is no earlier
# than the run start; directory outputs are unsupported.

.project_io_source <- tryCatch(sys.frame(1)$ofile, error = function(e) NULL)
if (is.null(.project_io_source) || !nzchar(.project_io_source)) {
  .project_io_source <- file.path(getwd(), "code", "lib", "project_io.R")
}
.project_io_module <- normalizePath(.project_io_source, winslash = "/", mustWork = FALSE)
.project_io_root <- normalizePath(file.path(dirname(.project_io_module), "..", ".."),
                                  winslash = "/", mustWork = FALSE)

.project_io_absolute <- function(path) {
  path <- path.expand(as.character(path)[[1]])
  if (!grepl("^(/|[A-Za-z]:[/\\\\])", path)) {
    path <- file.path(getwd(), path)
  }
  path
}

.project_io_record_path <- function(path) {
  resolved <- .project_io_absolute(path)
  prefix <- paste0(sub("/$", "", .project_io_root), "/")
  if (identical(resolved, .project_io_root)) return(".")
  if (startsWith(resolved, prefix)) return(substring(resolved, nchar(prefix) + 1L))
  resolved
}

.project_io_encode <- function(value) {
  value <- gsub("%", "%25", as.character(value), fixed = TRUE)
  value <- gsub("\t", "%09", value, fixed = TRUE)
  value <- gsub("\n", "%0A", value, fixed = TRUE)
  gsub("\r", "%0D", value, fixed = TRUE)
}

.project_io_glob_regex <- function(pattern) {
  characters <- strsplit(pattern, "", fixed = TRUE)[[1]]
  escaped <- vapply(characters, function(character) {
    if (character == "*") return(".*")
    if (character == "?") return(".")
    if (character %in% c("\\", ".", "+", "(", ")", "[", "]", "{", "}",
                         "^", "$", "|")) return(paste0("\\", character))
    character
  }, character(1))
  paste0("^", paste0(escaped, collapse = ""), "$")
}

.project_io_expand_input <- function(declaration) {
  declaration <- .project_io_absolute(declaration)
  if (file_test("-f", declaration)) {
    return(declaration)
  }

  if (dir.exists(declaration)) {
    entries <- list.files(declaration, full.names = TRUE, all.files = TRUE,
                          no.. = TRUE, recursive = FALSE)
    matches <- entries[file_test("-f", entries)]
  } else {
    parent <- dirname(declaration)
    pattern <- basename(declaration)
    if (!grepl("[*?]", pattern)) {
      stop(sprintf("input file does not exist: %s", declaration), call. = FALSE)
    }
    if (grepl("[*?]", parent)) {
      stop("glob wildcards are allowed only in the filename; declare its directory explicitly",
           call. = FALSE)
    }
    if (!dir.exists(parent)) {
      stop(sprintf("input directory does not exist: %s", parent), call. = FALSE)
    }
    entries <- list.files(parent, full.names = TRUE, all.files = TRUE,
                          no.. = TRUE, recursive = FALSE)
    matches <- entries[grepl(.project_io_glob_regex(pattern), basename(entries), perl = TRUE)]
    matches <- matches[file_test("-f", matches)]
  }

  matches <- sort(matches)
  if (!length(matches)) {
    stop(sprintf("input declaration matched no files: %s", declaration), call. = FALSE)
  }
  matches
}

.project_io_now <- function() {
  format(Sys.time(), tz = "UTC", format = "%Y-%m-%dT%H:%M:%SZ", usetz = FALSE)
}

.project_io_record_lines <- function(run, status, completed_at = "", error = "") {
  rows <- c(
    paste("format", "project-io-run-v1", sep = "\t"),
    paste("status", status, sep = "\t"),
    paste("script", .project_io_encode(run$script), sep = "\t"),
    paste("started_at", run$started_at, sep = "\t"),
    paste("completed_at", completed_at, sep = "\t")
  )
  if (length(run$inputs)) {
    rows <- c(rows, vapply(run$inputs, function(input) {
      paste("input", .project_io_encode(input$path), input$mtime, sep = "\t")
    }, character(1)))
  }
  if (length(run$outputs)) {
    rows <- c(rows, paste("output", .project_io_encode(run$outputs), sep = "\t"))
  }
  if (nzchar(error)) rows <- c(rows, paste("error", .project_io_encode(error), sep = "\t"))
  rows
}

.project_io_write <- function(run, status, completed_at = "", error = "") {
  contents <- .project_io_record_lines(run, status, completed_at, error)
  for (output in run$output_paths) {
    sidecar <- paste0(output, ".run.tsv")
    directory <- dirname(sidecar)
    dir.create(directory, recursive = TRUE, showWarnings = FALSE)
    temporary <- tempfile(pattern = paste0(basename(sidecar), "."), tmpdir = directory)
    writeLines(contents, temporary, useBytes = TRUE)
    if (file.exists(sidecar)) unlink(sidecar)
    if (!file.rename(temporary, sidecar)) {
      unlink(temporary)
      stop(sprintf("could not write run record: %s", sidecar), call. = FALSE)
    }
  }
  invisible(NULL)
}

.project_io_validate_outputs <- function(run) {
  for (output in run$output_paths) {
    if (!file_test("-f", output)) {
      stop(sprintf("declared output was not written or updated during this run: %s", output),
           call. = FALSE)
    }
    modified_at <- as.numeric(file.info(output)$mtime)
    if (is.na(modified_at) || modified_at < run$started_epoch) {
      stop(sprintf("declared output was not written or updated during this run: %s", output),
           call. = FALSE)
    }
  }
  invisible(NULL)
}

#' Register direct input paths and write output run records.
#'
#' `with_run_record()` invokes `code` with a `run` object. Call
#' `run$input_file(declaration)` before the ordinary reader; it returns a
#' character vector of absolute individual file paths. `outputs` and `script`
#' are source-declared paths. The sidecar next to each output is named
#' `<output>.run.tsv`.
with_run_record <- function(script, outputs, code) {
  output_paths <- unique(vapply(as.character(outputs), .project_io_absolute, character(1)))
  if (!length(output_paths)) stop("with_run_record() requires at least one output", call. = FALSE)
  run <- new.env(parent = emptyenv())
  run$script <- .project_io_record_path(script)
  run$output_paths <- output_paths
  run$outputs <- vapply(output_paths, .project_io_record_path, character(1))
  run$inputs <- list()
  run$input_paths <- character()
  run$started_at <- .project_io_now()
  run$started_epoch <- as.numeric(Sys.time())
  run$input_file <- function(declaration) {
    matches <- .project_io_expand_input(declaration)
    info <- file.info(matches)
    paths <- vapply(matches, .project_io_record_path, character(1))
    for (index in seq_along(matches)) {
      if (!(paths[[index]] %in% run$input_paths)) {
        run$inputs[[length(run$inputs) + 1L]] <- list(
          path = paths[[index]],
          mtime = sprintf("%.17g", as.numeric(info$mtime[[index]]))
        )
        run$input_paths <- c(run$input_paths, paths[[index]])
      }
    }
    .project_io_write(run, "running")
    matches
  }

  for (output in output_paths) {
    sidecar <- paste0(output, ".run.tsv")
    dir.create(dirname(sidecar), recursive = TRUE, showWarnings = FALSE)
    if (file.exists(sidecar)) unlink(sidecar)
  }
  .project_io_write(run, "running")
  result <- tryCatch({
    value <- code(run)
    .project_io_validate_outputs(run)
    value
  },
    error = function(error) {
      try(.project_io_write(run, "failed", .project_io_now(), conditionMessage(error)), silent = TRUE)
      stop(error)
    }
  )
  .project_io_write(run, "success", .project_io_now())
  result
}
