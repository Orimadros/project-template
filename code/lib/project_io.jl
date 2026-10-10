"""Small, explicit input registration and per-output run records.

Usage::

    include("code/lib/project_io.jl")
    using .ProjectIO

    const INPUTS = "data/raw/*.csv"  # paths live in the script, not CLI args
    const OUTPUT = "results/panel.csv"

    run_record(@__FILE__, [OUTPUT]) do run
        input_paths = input_file(run, INPUTS)  # always Vector{String}
        # Read input_paths with ordinary readers, then write OUTPUT.
    end

An input declaration may name one existing file, a directory, or a glob over
filenames in one explicitly named directory. A directory or glob expands to
sorted, immediate regular-file paths; it never walks subdirectories. Patterns
support * and ? in the filename only. Each matched file's filesystem mtime is
captured with stat() before the paths are returned. The helper does not open,
read, or hash input contents.

For every declared output, the context manager writes an adjacent
<output>.run.tsv record in the project-io-run-v1 TSV format shared with Python
and R. Starting a run removes old success markers and writes status=running;
normal return writes success, and an exception writes failed before being
re-thrown. A hard interruption can leave running, which is not a success
marker. Repository paths are recorded relative to the repository root;
external paths remain absolute. Modification times retain their observed
floating-point precision. Records cover only inputs explicitly registered
through this helper.

Declared outputs must be regular files. Before writing status=success, the
helper checks that each file exists and its modification time is no earlier
than the run start; directory outputs are unsupported.

Rows are format, status, script, started_at, completed_at, repeated
input<TAB>path<TAB>mtime rows, output<TAB>path rows, and an optional error
row. Path/error values percent-escape %, tab, LF, and CR as %25, %09, %0A,
and %0D. Shipping may append production_output<TAB>path while preserving the
original run facts.
"""

module ProjectIO

using Dates
using Printf

export RunRecord, input_file, run_record

const FORMAT = "project-io-run-v1"
const REPO_ROOT = normpath(joinpath(@__DIR__, "..", ".."))

struct RegisteredInput
    path::String
    mtime::Float64
end

mutable struct RunRecord
    script::String
    output_paths::Vector{String}
    outputs::Vector{String}
    inputs::Vector{RegisteredInput}
    input_paths::Set{String}
    started_at::String
    started_epoch::Float64
end

absolute_path(path::AbstractString) = normpath(abspath(expanduser(path)))

function record_path(path::AbstractString)
    resolved = absolute_path(path)
    relative = relpath(resolved, REPO_ROOT)
    components = splitpath(relative)
    if !isempty(components) && components[1] == ".."
        return resolved
    end
    return replace(relative, '\\' => '/')
end

function encode_field(value::AbstractString)
    escaped = replace(String(value), "%" => "%25")
    escaped = replace(escaped, "\t" => "%09")
    escaped = replace(escaped, "\n" => "%0A")
    return replace(escaped, "\r" => "%0D")
end

utc_now() = Dates.format(Dates.now(Dates.UTC), dateformat"yyyy-mm-ddTHH:MM:SSZ")

function glob_regex(pattern::AbstractString)
    pieces = String[]
    for character in pattern
        if character == '*'
            push!(pieces, ".*")
        elseif character == '?'
            push!(pieces, ".")
        else
            push!(pieces, escape_string(string(character), ['\\', '.', '^', '$', '|', '(', ')', '[', ']', '{', '}', '+']))
        end
    end
    return Regex("^" * join(pieces) * "\$")
end

function expand_input(declaration::AbstractString)
    declared = absolute_path(declaration)
    if isfile(declared)
        return [declared]
    end

    if isdir(declared)
        matches = filter(isfile, readdir(declared; join=true))
    else
        parent = dirname(declared)
        pattern = basename(declared)
        if !occursin(r"[*?]", pattern)
            throw(ArgumentError("input file does not exist: $declared"))
        end
        if occursin(r"[*?]", parent)
            throw(ArgumentError("glob wildcards are allowed only in the filename; declare its directory explicitly"))
        end
        if !isdir(parent)
            throw(ArgumentError("input directory does not exist: $parent"))
        end
        matcher = glob_regex(pattern)
        matches = filter(path -> isfile(path) && occursin(matcher, basename(path)), readdir(parent; join=true))
    end

    sort!(matches)
    isempty(matches) && throw(ArgumentError("input declaration matched no files: $declared"))
    return matches
end

function record_lines(run::RunRecord, status::AbstractString;
                      completed_at::AbstractString="", error::AbstractString="")
    lines = [
        "format\t" * FORMAT,
        "status\t" * status,
        "script\t" * encode_field(run.script),
        "started_at\t" * run.started_at,
        "completed_at\t" * completed_at,
    ]
    for input in run.inputs
        push!(lines, "input\t" * encode_field(input.path) * "\t" * @sprintf("%.17g", input.mtime))
    end
    for output in run.outputs
        push!(lines, "output\t" * encode_field(output))
    end
    if !isempty(error)
        push!(lines, "error\t" * encode_field(error))
    end
    return lines
end

function write_record(run::RunRecord, status::AbstractString;
                      completed_at::AbstractString="", error::AbstractString="")
    contents = join(record_lines(run, status; completed_at=completed_at, error=error), "\n") * "\n"
    for output in run.output_paths
        sidecar = output * ".run.tsv"
        mkpath(dirname(sidecar))
        temporary = tempname(dirname(sidecar))
        try
            open(temporary, "w") do io
                write(io, contents)
            end
            mv(temporary, sidecar; force=true)
        catch
            isfile(temporary) && rm(temporary; force=true)
            rethrow()
        end
    end
    return nothing
end

function validate_outputs(run::RunRecord)
    for output in run.output_paths
        if !isfile(output) || stat(output).mtime < run.started_epoch
            throw(ArgumentError("declared output was not written or updated during this run: $output"))
        end
    end
    return nothing
end

"""Register one input declaration and return absolute individual file paths."""
function input_file(run::RunRecord, declaration::AbstractString)
    matches = expand_input(declaration)
    for path in matches
        observed_path = record_path(path)
        if !(observed_path in run.input_paths)
            push!(run.inputs, RegisteredInput(observed_path, stat(path).mtime))
            push!(run.input_paths, observed_path)
        end
    end
    write_record(run, "running")
    return matches
end

"""Run `code(run)` and write status records beside each declared output.

Use Julia's do-block form: `run_record(@__FILE__, [OUTPUT]) do run ... end`.
Relative source paths resolve from the current working directory.
"""
function run_record(code::Function, script::AbstractString, outputs)
    output_paths = unique(absolute_path.(String.(collect(outputs))))
    isempty(output_paths) && throw(ArgumentError("run_record requires at least one declared output"))
    run = RunRecord(
        record_path(script),
        output_paths,
        record_path.(output_paths),
        RegisteredInput[],
        Set{String}(),
        utc_now(),
        time(),
    )

    # Clear all old markers before writing any new status record.
    for output in output_paths
        sidecar = output * ".run.tsv"
        mkpath(dirname(sidecar))
        isfile(sidecar) && rm(sidecar; force=true)
    end
    write_record(run, "running")
    try
        result = code(run)
        validate_outputs(run)
        write_record(run, "success"; completed_at=utc_now())
        return result
    catch error
        try
            write_record(run, "failed"; completed_at=utc_now(), error=sprint(showerror, error))
        catch
            # Preserve the script's original error if recording also fails.
        end
        rethrow()
    end
end

end # module ProjectIO
