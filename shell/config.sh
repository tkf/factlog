# Ad-hoc wrapper command for `factlog record'.
# Usage:
#    _factlog_record_wrapper COMMAND FILE [OPTIONS]
# Note that this wrapper does not work if the first option is not the
# file to open.  Supporting all possible option will require more
# dedicated handling than this.
_factlog_record_wrapper(){
    local command="$1"
    local file="$2"
    local code
    if [ "$#" = 1 ]
    then
        "$command"
        code="$?"
        return $code
    fi
    shift 2
    if [ -e "$file" ]
    then
        factlog record -a open "$file"
        "$command" "$file" "$@"
        code="$?"
        factlog record -a close "$file"
        return $code
    else
        "$command" "$file" "$@"
    fi
}

# Make wrapper for command using alias
# Usage:
#    _factlog_record_wrap_command COMMAND
# It is roughly equivalent to:
#    _factlog_record_orig_COMMAND=$(which COMMAND)
#    alias COMMAND="_factlog_record_wrapper ${_factlog_record_orig_COMMAND}"
_factlog_record_wrap_command(){
    local command="$1"
    local varname="_factlog_record_orig_${command}"
    if eval "test -z \$$varname"
    then
        eval "${varname}=$(which $command)"
        eval "alias ${command}=\"_factlog_record_wrapper \$${varname}\""
    fi
}

_factlog_record_wrap_command less
_factlog_record_wrap_command vim
